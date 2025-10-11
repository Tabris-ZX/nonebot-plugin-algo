import json
from typing import Dict
from nonebot.log import logger
import httpx
from jinja2 import Template
from .config import algo_config,luogu_save_path
from pathlib import Path
from collections import Counter
import html
from datetime import datetime
from .mapper import Mapper
TEMPLATE_PATH = Path(__file__).parent / "resources" / "lougu_card.html"
cards_save_path = luogu_save_path / "cards"
users_save_path = luogu_save_path / "users.json"

DEFAULT_WIDTH = 610
DEFAULT_HEIGHT = 950

class Luogu:
    headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0",
            "X-Lentille-Request": "content-only",    
            "x-requested-with": "XMLHttpRequest",
            "cookie":algo_config.luogu_cookie,
            "x-csrf-token": algo_config.luogu_x_csrf_token,
        }
    base_url = "https://www.luogu.com.cn"

    @staticmethod
    async def request(url: str, headers: dict = headers)-> Dict | None:
        """异步HTTP请求方法"""
        try:
            timeout = httpx.Timeout(10.0)
            # 跟随重定向以避免 302 中断，同时设置默认 headers
            async with httpx.AsyncClient(timeout=timeout, follow_redirects=True, headers=headers) as client:
                response = await client.get(url)
                response.raise_for_status()
                if response.status_code == 200:
                    data = response.json()
                    return data
                else:
                    logger.error(f"网络请求错误，状态码: {response.status_code}")
                    return None
        except httpx.TimeoutException:
            logger.error("网络请求超时")
            return None
        except httpx.RequestError as e:
            logger.error(f"网络请求错误: {e}")
            return None
        except Exception as e:
            logger.error(f"请求发生未知异常: {e}")
            return None

    @classmethod
    async def search_user_id(cls, keyword: str) -> int | None:
        """根据关键字搜索用户id（解析 users.result[0].uid）"""
        url = cls.base_url + f"/api/user/search?keyword={keyword}"
        data = await cls.request(url)
        if not data:
            return None
        try:
            user_id = int(data["users"][0]["uid"])
            return user_id
        except Exception:
            return None

    @classmethod
    async def bind_luogu_user(cls, user_qq: str, user: str| int)-> bool:
        if isinstance(user, int):
            user_id = user
        else:
            user_id = await cls.search_user_id(user)
        if user_id is None:
            return False
        save_path = users_save_path
        save_path.parent.mkdir(parents=True, exist_ok=True)
        if not save_path.exists():
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump({}, f)
                
        with open(save_path, "r", encoding="utf-8") as f:
            users = json.load(f)
        users[user_qq] = user_id
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(users, f, ensure_ascii=False, indent=4)
        return True

    @classmethod
    async def build_bind_user_info(cls, user_qq: str)-> Path | None:
        save_path = users_save_path
        with open(save_path, "r", encoding="utf-8") as f:
            users = json.load(f)
        user_id = users.get(user_qq,None)
        if user_id is None:
            return None
        return await cls.build_user_info(user_id)

    @classmethod
    def check_card_exists(cls, user: str) -> Path | None:
        """检查洛谷卡片是否存在"""
        img_path = cards_save_path / f"{user}.png"
        if img_path.exists():
            return img_path
        return None

    @classmethod
    async def get_user_info(cls, user: str| int)-> Dict | None:
        """获取用户信息"""
        if isinstance(user, int):
            user_id = user
        else:
            user_id = await cls.search_user_id(user)
        if user_id is None:
            return None
        url = cls.base_url + f"/user/{user_id}/practice"
        user_info = await cls.request(url)
        if user_info:
            try:
                prize_url = cls.base_url + f"/offlinePrize/getList/{user_id}"
                headers = {**cls.headers, "referer": f"{cls.base_url}/user/{user_id}"}
                prizes = await cls.request(prize_url, headers=headers)
                if prizes:
                    user_info['data']['user']['prizes'] = prizes['prizes']
            except Exception as e:
                logger.warning(f"获取奖项信息失败: {e}")
                return None
        return user_info



    @classmethod
    async def build_user_info(cls, user: str|int)-> Path | None:
        info = await cls.get_user_info(user)
        if not info:
            return None
        username = info['data']['user']['name']    
        if username is None:
            return None
        img_output: Path = cards_save_path / f"{username}.png"
        img_output.parent.mkdir(parents=True, exist_ok=True)

        if cls.check_card_exists(username):
            return img_output
        # 渲染模板
        context = cls._build_user_card_context(info)
        try:
            with open(TEMPLATE_PATH, encoding="utf-8") as f:
                template = Template(f.read())
            # 预构建彩色名称
            context = {
                **context,
                "name_styled": f"<span style='color:{context.get('name_color', '#fff')}'>{context.get('name','')}</span>",
            }
            html_rendered = template.render(**context)
        except Exception as e:
            logger.error(f"读取模板失败: {e}，改用内置模板渲染")
            return None
        
        # 仅使用 Playwright 渲染
        # 初次按动态高度渲染（让页面自适应内容），再截图整个页面
        ok = await cls.html_to_pic(html_rendered, img_output, DEFAULT_WIDTH, None)
        if ok:
            return img_output
        logger.error("Playwright 截图失败，未生成卡片")
        return None

    @staticmethod
    async def html_to_pic(html: str, out_path: Path, width: int, height: int | None) -> bool:
        try:
            from playwright.async_api import async_playwright
        except Exception as e:
            logger.warning(f"未安装 Playwright：{e}")
            return False
        try:
            async with async_playwright() as pw:
                browser = await pw.chromium.launch()
                context = await browser.new_context(viewport={"width": int(width), "height": int(height or 1)}, device_scale_factor=2)
                page = await context.new_page()
                await page.set_content(html, wait_until="networkidle")
                # 若未指定高度，则截图整页
                if height is None:
                    await page.screenshot(path=str(out_path), full_page=True, type="png")
                else:
                    await page.screenshot(path=str(out_path), clip={"x": 40, "y": 10, "width": width, "height": height}, type="png")
                await context.close()
                await browser.close()
                return True
        except Exception as e:
            logger.error(f"Playwright 截图失败: {e}")
            return False


    @classmethod
    def _build_user_card_context(cls, data: Dict) -> Dict:
        """提取用户信息"""
        all_info=data.get("data",{})

        #用户部分
        user_info=all_info.get("user",{})
        name = user_info.get("name", "Unknown")
        badge = user_info.get("badge", "")
        color_key = user_info.get("color", "Gray")
        color = Mapper.luogu_name_color.get(color_key) or "#bbbbbb"
        avatar = user_info.get("avatar", "")
        uid = user_info.get("uid", "-")
        slogan = user_info.get("slogan", "")
        ranking = user_info.get("ranking","--")
        # passed = user_info.get("passedProblemCount", "--")
        # submitted = user_info.get("submittedProblemCount", "--")
        following = user_info.get("followingCount", "-")
        followers = user_info.get("followerCount", "-")
        intro = user_info.get("introduction") if user_info.get("introduction") is not None else "--"
        email = user_info.get("email") if user_info.get("email") is not None else "--"
        #当前等级分
        if (elo_list := all_info.get('elo')) and len(elo_list) > 0:
            elo = elo_list[0].get('rating', "--")
        else:
            elo = "--"
        # 徽章文本（若存在则渲染到名字后）
        badge = user_info.get("badge")
        name_badge = ""
        if badge is not None:
            badge_safe = html.escape(badge)
            name_badge = f"<span class='name-badge' style='background:{color};color:#fff'>{badge_safe}</span>"
        
        # 获奖情况部分
        prizes = user_info.get("prizes", [])
        prize_list: list[str] = []
        prize_rows: list[dict] = []
        try:
            for item in prizes:
                p = item['prize']
                year = p['year']
                contest = p['contest']
                level = p['prize']
                if year or contest or level:
                    prize_list.append(f"{year or ''} {contest or ''} {level or ''}".strip())
                    # 使用Mapper中的奖项颜色配置
                    level_text = str(level or "")
                    if "一" in level_text or "金" in level_text:
                        prize_color = Mapper.luogu_prize_color["first"]
                    elif "二" in level_text or "银" in level_text:
                        prize_color = Mapper.luogu_prize_color["second"]
                    elif "三" in level_text or "铜" in level_text:
                        prize_color = Mapper.luogu_prize_color["third"]
                    else:
                        prize_color = Mapper.luogu_prize_color["other"]
                    prize_rows.append({
                        "left": f"[{year}] {contest}",
                        "right_html": f"<span style='color:{prize_color}'>{level}</span>",
                    })
        except Exception:
            prize_list = []
            prize_rows = []

        # 做题情况部分
        # submitted_problems_info=all_info.get("submitted",{})
        # submitted = len(submitted_problems_info)
        passed_problems_info=all_info.get("passed",{})
        passed = len(passed_problems_info)
        passed_problems_counter = Counter(p.get("difficulty") for p in passed_problems_info)
        # 难度顺序：1-7 后跟 -1（未评级放最后）
        levels = [1, 2, 3, 4, 5, 6, 7, -1]
        # 颜色映射：1-7 依次 红、橙、黄、绿、蓝、紫、黑；-1 灰
        level_to_color = Mapper.luogu_problem_level_color
        counts = [int(passed_problems_counter.get(l, 0)) for l in levels]
        max_count = max(counts) if any(counts) else 1
        bars = []
        names_map = Mapper.luogu_difficulty_names or {}
        for idx, l in enumerate(levels):
            c = counts[idx]
            width = 0 if c == 0 else int(12 + (c / max_count) * 68)
            bars.append({
                "label": names_map.get(l),
                "value": c,
                "width": width,
                "color": level_to_color[idx],
            })
    

        return {
            "name": name,
            "uid": uid,
            "slogan": slogan,
            # "ranking": ranking,
            "avatar": avatar,
            "name_color": color,
            "name_badge": name_badge,
            "passed": passed,
            # "submitted": submitted,
            "following": following,
            "followers": followers,
            "intro": intro,
            "prizes": prize_list,
            "prize_rows": prize_rows,
            "email": email,
            "elo": elo,
            "diff_bars": bars,
            "current_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

    @classmethod
    async def get_user_followings(cls, user_id: str):
        url = cls.base_url + f"/api/user/followings?user={user_id}"
        pass
    @classmethod
    async def get_user_activitys(cls, user_id: str):
        url = cls.base_url + f"/api/user/activitys?user={user_id}"
        pass
