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
import math
from .mapper import Mapper
TEMPLATE_PATH = Path(__file__).parent / "resources" / "luogu_card_full.html"
cards_save_path = luogu_save_path / "cards"
users_save_path = luogu_save_path / "users.json"

DEFAULT_WIDTH = 1170
DEFAULT_HEIGHT = 950

class Luogu:
    headers = {
            "user-agent": "",
            "X-Lentille-Request": "content-only",    
            "x-requested-with": "XMLHttpRequest",
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
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP状态错误: {e.response.status_code}")
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
        url = cls.base_url + f"/user/{user_id}"
        user_info = await cls.request(url)
        if user_info:
            try:
                passed_detail_url = cls.base_url + f"/user/{user_id}/practice"
                headers = {**cls.headers, "referer": f"{cls.base_url}/user/{user_id}"}
                passed_detail = await cls.request(passed_detail_url, headers=headers)
                if passed_detail:
                    user_info['data']['passed'] = passed_detail['data']['passed']
            except Exception as e:
                logger.error("获取通过详情失败")
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
        badge = user_info.get("badge")
        color_key = user_info.get("color", "Gray")
        color = Mapper.luogu_name_color.get(color_key) or "#bbbbbb"
        avatar = user_info.get("avatar", "")
        background = user_info.get("background","")
        uid = user_info.get("uid", "-")
        slogan = user_info.get("slogan", "")
        following = user_info.get("followingCount", "-")
        followers = user_info.get("followerCount", "-")
        
        passed_problem_count = user_info.get("passedProblemCount","")
        submitted_problem_count = user_info.get("submittedProblemCount","")
        #当前等级分
        if (elo_list := all_info.get('elo')) and len(elo_list) > 0:
            elo = elo_list[0].get('rating', "--")
        else:
            elo="--"    
        # 徽章文本（若存在则渲染到名字后）
        name_badge = ""
        if badge is not None:
            badge_safe = html.escape(badge)
            name_badge = f"<span class='name-badge' style='background:{color};color:#fff'>{badge_safe}</span>"
        
        # 获奖情况部分
        prizes = all_info.get("prizes", [])
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


        # 每日做题详情（用于热力图）
        daily_counts = all_info.get("dailyCounts", {}) or {}
        heatmap_rows, weekday_labels, month_labels = cls._build_heatmap(daily_counts)

        # 计算 quality
        def solve_weights(diff, cnt):
            return (math.pow(2, diff-1) + math.log2(math.pow(cnt, diff/ 6) + 1)) * cnt
            
        quality = 0.00
        # 做题情况部分
        passed_problems_info=all_info.get("passed",{})
        passed_difficulty_counter = Counter(p.get("difficulty") for p in passed_problems_info)
        levels = [1, 2, 3, 4, 5, 6, 7, 0]
        # 颜色映射：1-7 依次 红、橙、黄、绿、蓝、紫、黑； 灰色为未评级
        level_to_color = Mapper.luogu_problem_level_color
        counts = [int(passed_difficulty_counter.get(l, 0)) for l in levels]
        max_count = max(counts) if any(counts) else 1
        bars = []
        names_map = Mapper.luogu_difficulty_names or {}
        for idx, l in enumerate(levels):
            cnt = counts[idx]
            width = 0 if cnt == 0 else int(12 + (cnt / max_count) * 68)
            bars.append({
                "label": names_map.get(l),
                "value": cnt,
                "width": width,
                "color": level_to_color[idx],
            })
            if cnt > 0 and l > 0:
                quality += solve_weights(l, cnt)
        quality/=(passed_problem_count-counts[7]) # 未评级不计入质量

        return {
            "name": name,
            "uid": uid,
            "slogan": slogan,
            "avatar": avatar,
            "background":background,
            "name_color": color,
            "name_badge": name_badge,
            "passed": passed_problem_count,
            "following": following,
            "followers": followers,
            "prizes": prize_list,
            "prize_rows": prize_rows,
            "elo": elo,
            "diff_bars": bars,
            "current_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "heatmap_rows": heatmap_rows,
            "weekday_labels": weekday_labels,
            "month_labels": month_labels,
            "quality": round(quality*10,2)
        }

    
    @staticmethod
    def _build_heatmap(daily_counts: Dict[str, list]) -> tuple[list[list[int]], list[str], list[str]]:
        """将 daily_counts 构造成 7 行（周日到周六）、N 列的强度矩阵，强度等级 0-6。

        daily_counts 示例：{"2025-07-16": [2,4]}，其中 [0] 为做题数，[1] 为热度。
        返回：(热力图数据, 星期标签, 月份标签)
        """
        from datetime import date, timedelta

        if not daily_counts:
            return [[0] * 7 for _ in range(7)], ["日", "一", "二", "三", "四", "五", "六"], []

        # 解析日期与热度
        parsed: dict[date, int] = {}
        max_heat = 0
        for ds, arr in daily_counts.items():
            try:
                d = date.fromisoformat(ds)
                heat = int(arr[1]) if isinstance(arr, (list, tuple)) and len(arr) > 1 else 0
                parsed[d] = heat
                if heat > max_heat:
                    max_heat = heat
            except Exception:
                continue

        if not parsed:
            return [[0] * 7 for _ in range(7)], ["日", "一", "二", "三", "四", "五", "六"], []

        min_d = min(parsed.keys())
        max_d = max(parsed.keys())

        # 对齐到周列：从 min_d 所在周的周日到 max_d 所在周的周六
        # Python: Monday=0..Sunday=6
        def to_sunday(d: date) -> date:
            return d - timedelta(days=(d.weekday() + 1) % 7)

        def to_saturday(d: date) -> date:
            return d + timedelta(days=(5 - d.weekday()) % 7 + 1)

        start = to_sunday(min_d)
        end = to_saturday(max_d)

        total_days = (end - start).days + 1

        # 构建列：按天遍历，填充等级
        # 行顺序：周日(6)、周一(0)、...、周六(5)
        row_order = [6, 0, 1, 2, 3, 4, 5]
        weekday_labels = ["日", "一", "二", "三", "四", "五", "六"]

        # 初始化 7 行
        rows: list[list[int]] = [[] for _ in range(7)]
        
        # 生成月份标签
        month_labels = []
        current_month = None
        for i in range(total_days):
            cur = start + timedelta(days=i)
            month = cur.month
            if month != current_month:
                # 新月份开始，添加月份标签
                month_labels.append(f"{month}月")
                current_month = month
            else:
                # 同一月份，添加空标签
                month_labels.append("")
            
            heat = parsed.get(cur, 0)
            if max_heat <= 0 or heat <= 0:
                level = 0
            else:
                ratio = heat / max_heat
                level = max(1, min(6, int(round(ratio * 6))))

            py_wd = cur.weekday()  # Monday=0..Sunday=6
            # 映射到我们定义的行索引（周日行在最上）
            row_index = row_order.index(py_wd)
            rows[row_index].append(level)

        return rows, weekday_labels, month_labels
