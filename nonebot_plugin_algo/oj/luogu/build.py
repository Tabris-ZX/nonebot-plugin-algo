import random
import base64
import httpx
from typing import Dict
from nonebot.log import logger
from jinja2 import Template
from ...config import luogu_save_path, Mapper
from .api import LuoguAPI
from pathlib import Path
from collections import Counter
import html
from datetime import datetime
from uuid import uuid4
ASSETS_PATH = Path(__file__).resolve().parents[2] / "assets"
TEMPLATE_PATH = ASSETS_PATH / "template" / "lougu_card.html"
SAMPLE_TEMPLATE_PATH = ASSETS_PATH / "template" / "sample_card.html"
FULL_STYLE_PATH = ASSETS_PATH / "template" / "full-style.css"
SAMPLE_STYLE_PATH = ASSETS_PATH / "template" / "sample-style.css"
LOGO_PATH = ASSETS_PATH / "luogu.webp"
BACKGROUND_DIR = ASSETS_PATH / "background"
FONT_DIR = ASSETS_PATH / "fonts"
cards_save_path = luogu_save_path / "cards"

DEFAULT_WIDTH = 1440
DEFAULT_HEIGHT = 900

class Luogu(LuoguAPI):
    @classmethod
    async def build_bind_user_info(cls, user_qq: str, full: bool = False)-> Path | None:
        user_id = cls.get_bound_user(user_qq)
        if user_id is None:
            return None
        return await cls.build_user_info(user_id, full=full)

    @classmethod
    async def build_user_info(cls, user: str|int, full: bool = False)-> Path | None:
        info = await cls.get_user_info(user)
        if not info:
            return None
        username = info['data']['user']['name']    
        if username is None:
            return None
        img_output: Path = cards_save_path / f"{username}.png"
        sample_output: Path = cards_save_path / f"{username}_sample.png"
        img_output.parent.mkdir(parents=True, exist_ok=True)

        # 渲染模板
        context = cls._build_user_card_context(info)
        try:
            if full:
                with open(TEMPLATE_PATH, encoding="utf-8") as f:
                    template = Template(f.read())
            else:
                with open(SAMPLE_TEMPLATE_PATH, encoding="utf-8") as f:
                    template = Template(f.read())
            background = context["background"] or cls._random_background_uri()
            # 预构建彩色名称
            avatar = await cls._remote_image_data_uri(context["avatar"])
            context = {
                **context,
                "background": background,
                "logo_src": cls._image_data_uri(LOGO_PATH),
                "avatar": avatar,
                "font_faces": cls._font_faces(),
                "name_styled": f"<span style='color:{context['name_color']}'>{context['name']}</span>",
                **cls._theme_vars(context["name_color"]),
            }
            if full:
                render_context = {
                    **context,
                    "full_style": cls._render_style(FULL_STYLE_PATH, context),
                }
                html_rendered = template.render(**render_context)
                output, width, height = img_output, DEFAULT_WIDTH, DEFAULT_HEIGHT
            else:
                render_context = {
                    **cls._build_sample_context(context),
                    "font_faces": context["font_faces"],
                }
                render_context = {
                    **render_context,
                    "sample_style": cls._render_style(SAMPLE_STYLE_PATH, render_context),
                }
                html_rendered = template.render(**render_context)
                output, width, height = sample_output, 600, 800
        except Exception as e:
            logger.error(f"读取模板失败: {e}，改用内置模板渲染")
            return None
        
        # 仅使用 Playwright 渲染
        # 初次按动态高度渲染（让页面自适应内容），再截图整个页面
        ok = await cls.html_to_pic(html_rendered, output, width, height)
        if ok:
            return output
        logger.error("Playwright 截图失败，未生成卡片")
        return None

    @staticmethod
    def _image_data_uri(path: Path) -> str:
        try:
            return "data:image/webp;base64," + base64.b64encode(path.read_bytes()).decode("ascii")
        except Exception as e:
            logger.warning(f"读取本地图片失败: {path} ({e})")
            return ""

    @staticmethod
    def _font_url(path: Path) -> str:
        return path.resolve().as_uri()

    @staticmethod
    def _font_data_uri(path: Path) -> str:
        return "data:font/ttf;base64," + base64.b64encode(path.read_bytes()).decode(
            "ascii"
        )

    @classmethod
    def _font_faces(cls) -> str:
        return (
            "@font-face{font-family:'Baloo 2';src:url('"
            f"{cls._font_data_uri(FONT_DIR / 'Baloo2-Regular.ttf')}"
            "') format('truetype');font-weight:400 800;font-style:normal;font-display:block;}"
            "@font-face{font-family:'Noto Sans CJK SC';src:url('"
            f"{cls._font_url(FONT_DIR / 'NotoSansSC-Regular.ttf')}"
            "') format('truetype');font-weight:400;font-style:normal;font-display:block;}"
            "@font-face{font-family:'Noto Sans CJK SC';src:url('"
            f"{cls._font_url(FONT_DIR / 'NotoSansSC-Bold.ttf')}"
            "') format('truetype');font-weight:700;font-style:normal;font-display:block;}"
        )

    @staticmethod
    async def _remote_image_data_uri(url: str) -> str:
        if not url:
            return ""
        timeout = httpx.Timeout(10.0)
        try:
            async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
                response = await client.get(url)
            response.raise_for_status()
        except httpx.HTTPError as e:
            logger.warning(f"读取远程头像失败: {url} ({type(e).__name__}: {e!r})")
            return url
        content_type = response.headers.get("content-type", "image/png").split(";")[0]
        return f"data:{content_type};base64," + base64.b64encode(response.content).decode("ascii")

    @staticmethod
    def _render_style(path: Path, context: Dict) -> str:
        with open(path, encoding="utf-8") as f:
            return Template(f.read()).render(**context)

    @classmethod
    def _random_background_uri(cls) -> str:
        backgrounds = sorted(BACKGROUND_DIR.glob("*.webp"))
        if not backgrounds:
            return ""
        return cls._image_data_uri(random.choice(backgrounds))

    @staticmethod
    def _theme_vars(color: str) -> dict[str, str]:
        def parse_hex(value: str) -> tuple[int, int, int]:
            value = (value or "").strip().lstrip("#")
            if len(value) == 3:
                value = "".join(ch * 2 for ch in value)
            try:
                return int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16)
            except Exception:
                return 43, 138, 238

        def mix_white(rgb: tuple[int, int, int], amount: float) -> tuple[int, int, int]:
            return (
                int(rgb[0] * (1 - amount) + 255 * amount),
                int(rgb[1] * (1 - amount) + 255 * amount),
                int(rgb[2] * (1 - amount) + 255 * amount),
            )

        def rgba(rgb: tuple[int, int, int], alpha: float) -> str:
            return f"rgba({rgb[0]}, {rgb[1]}, {rgb[2]}, {alpha:.2f})"

        rgb = parse_hex(color)
        return {
            "surface_glass": rgba(mix_white(rgb, 0.12), 0.90),
            "surface_card": rgba(mix_white(rgb, 0.22), 0.96),
            "identity_bg": rgba(mix_white(rgb, 0.88), 0.96),
            "border_light": rgba(mix_white(rgb, 0.76), 0.48),
            "border_subtle": rgba(mix_white(rgb, 0.70), 0.26),
            "overlay_start": rgba(mix_white(rgb, 0.48), 0.30),
            "overlay_end": rgba(mix_white(rgb, 0.20), 0.42),
        }

    @staticmethod
    async def html_to_pic(html: str, out_path: Path, width: int, height: int | None) -> bool:
        try:
            from playwright.async_api import TimeoutError as PlaywrightTimeoutError, async_playwright
        except Exception as e:
            logger.warning(f"未安装 Playwright：{e}")
            return False
        html_path = out_path.with_name(f".{out_path.stem}-{uuid4().hex}.html")
        try:
            # set_content() 的页面地址是 about:blank，会被 Chromium 拒绝加载
            # file:// 字体。通过同目录临时 HTML 文件导航，字体与页面保持同源。
            html_path.write_text(html, encoding="utf-8")
            async with async_playwright() as pw:
                browser = await pw.chromium.launch()
                context = await browser.new_context(viewport={"width": int(width), "height": int(height or 1)}, device_scale_factor=2)
                page = await context.new_page()
                await page.goto(html_path.as_uri(), wait_until="domcontentloaded")
                try:
                    await page.wait_for_load_state("load", timeout=3000)
                except PlaywrightTimeoutError:
                    pass
                await page.evaluate("document.fonts ? document.fonts.ready : Promise.resolve()")
                await page.wait_for_timeout(120)
                # 若未指定高度，则截图整页
                if height is None:
                    await page.screenshot(path=str(out_path), full_page=True, type="png")
                else:
                    await page.screenshot(path=str(out_path), clip={"x": 0, "y": 0, "width": width, "height": height}, type="png")
                await context.close()
                await browser.close()
                return True
        except Exception as e:
            logger.error(f"Playwright 截图失败: {e}")
            return False
        finally:
            html_path.unlink(missing_ok=True)


    @classmethod
    def _build_user_card_context(cls, data: Dict) -> Dict:
        """提取用户信息"""
        all_info = data["data"]

        #用户部分
        user_info = all_info["user"]
        gu_info = all_info["gu"]
        gu_scores = gu_info["scores"]
        elo_list = all_info["elo"]
        name = user_info["name"]
        badge = user_info["badge"]
        color_key = user_info["color"]
        color = Mapper.luogu_name_color.get(color_key) or "#bbbbbb"
        avatar = user_info["avatar"]
        background = user_info["background"]
        uid = user_info["uid"]
        slogan = user_info["slogan"]
        following = user_info["followingCount"]
        followers = user_info["followerCount"]
        registration = user_info["registerTime"]
        contest_count = len(elo_list) if elo_list else gu_scores["contest"]
        
        passed_problem_count = user_info["passedProblemCount"]
        #当前等级分
        if elo_list and len(elo_list) > 0:
            elo = elo_list[0]["rating"]
        else:
            elo = gu_info["rating"]
        # 徽章文本（若存在则渲染到名字后）
        name_badge = ""
        if badge is not None:
            badge_safe = html.escape(badge)
            name_badge = f"<span class='name-badge' style='background:{color};color:#fff'>{badge_safe}</span>"
        
        # 获奖情况部分
        prizes = all_info["prizes"]
        prize_list: list[str] = []
        prize_rows: list[dict] = []
        for item in prizes:
            p = item['prize']
            year = p['year']
            contest = p['contest']
            level = p['prize']
            if year or contest or level:
                prize_list.append(f"{year or ''} {contest or ''} {level or ''}".strip())
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


        # 每日做题详情（用于热力图）
        daily_counts = all_info["dailyCounts"]
        heatmap_rows, weekday_labels, month_labels = cls._build_heatmap(daily_counts)

        # 做题情况部分
        passed_problems_info = all_info["passed"]
        passed_difficulty_counter = Counter(p["difficulty"] for p in passed_problems_info)
        levels = [0, 1, 2, 3, 4, 5, 6, 7, 8]
        # 颜色映射与洛谷新难度顺序一致：暂无评定 -> NOI/NOI+/CTS
        level_to_color = Mapper.luogu_problem_level_color
        counts = [int(passed_difficulty_counter.get(l, 0)) for l in levels]
        max_count = max(counts) if any(counts) else 1
        bars = []
        names_map = Mapper.luogu_difficulty_names or {}
        for idx, l in enumerate(levels):
            cnt = counts[idx]
            width = 0 if cnt == 0 else int(12 + (cnt / max_count) * 68)
            bars.append({
                "label": names_map.get(l, "暂无评定"),
                "value": cnt,
                "width": width,
                "color": level_to_color[idx],
            })

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
            "registration_str": cls._format_date_value(registration),
            "contest_count": contest_count,
            "prizes": prize_list,
            "prize_rows": prize_rows,
            "prize_total": len(prize_rows),
            "elo": elo,
            "diff_bars": bars,
            "current_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "heatmap_rows": heatmap_rows,
            "heatmap_cols": len(heatmap_rows[0]) if heatmap_rows else 7,
            "weekday_labels": weekday_labels,
            "month_labels": month_labels,
        }

    @classmethod
    def _build_sample_context(cls, context: Dict) -> Dict:
        accent = context["name_color"]

        def display(value, default="--"):
            return value if value is not None and value != "" else default

        return {
            "short_name": "LG",
            "logo_src": cls._image_data_uri(LOGO_PATH),
            "accent": accent,
            "accent_dark": cls._adjust_color(accent, -0.14),
            "accent_soft": cls._adjust_color(accent, 0.38),
            "avatar": context["avatar"],
            "name": context["name"],
            "rating": display(context["elo"]),
            "chip_left": f"Rating {display(context['elo'])}",
            "chip_right": f"{display(context['followers'])} followers",
            "side_rows": [
                {"key": "solved", "value": display(context["passed"])},
                {"key": "contests", "value": display(context["contest_count"])},
                {"key": "registered", "value": display(context["registration_str"])},
            ],
        }

    @staticmethod
    def _adjust_color(color: str, amount: float) -> str:
        value = (color or "#e67e22").strip().lstrip("#")
        if len(value) == 3:
            value = "".join(ch * 2 for ch in value)
        try:
            rgb = [int(value[i:i + 2], 16) for i in (0, 2, 4)]
        except Exception:
            rgb = [230, 126, 34]
        target = 255 if amount >= 0 else 0
        ratio = abs(amount)
        mixed = [round(c * (1 - ratio) + target * ratio) for c in rgb]
        return "#" + "".join(f"{c:02x}" for c in mixed)

    @staticmethod
    def _format_date_value(value) -> str:
        if not value:
            return "--"
        if isinstance(value, (int, float)):
            try:
                return datetime.fromtimestamp(value).strftime("%Y-%m-%d")
            except Exception:
                return "--"
        text = str(value)
        if len(text) >= 10:
            return text[:10]
        return text or "--"

    
    @staticmethod
    def _build_heatmap(daily_counts: Dict[str, list]) -> tuple[list[list[int]], list[str], list[str]]:
        """将 daily_counts 构造成 7 行（周日到周六）、N 列的强度矩阵，强度等级 0-6。

        daily_counts 示例：{"2025-07-16": [2,4]}，其中 [0] 为做题数，[1] 为热度。
        返回：(热力图数据, 星期标签, 月份标签)
        """
        from datetime import date, timedelta

        today = date.today()
        end = today + timedelta(days=(5 - today.weekday()) % 7 + 1)
        start = end - timedelta(days=7 * 26 - 1)
        start = start - timedelta(days=(start.weekday() + 1) % 7)
        end = start + timedelta(days=7 * 26 - 1)
        row_order = [6, 0, 1, 2, 3, 4, 5]
        weekday_labels = ["日", "一", "二", "三", "四", "五", "六"]
        rows: list[list[int]] = [[] for _ in range(7)]

        # 解析日期与热度
        parsed: dict[date, int] = {}
        max_heat = 0
        for ds, arr in daily_counts.items():
            try:
                d = date.fromisoformat(ds)
                if not start <= d <= end:
                    continue
                heat = int(arr[1]) if isinstance(arr, (list, tuple)) and len(arr) > 1 else 0
                parsed[d] = heat
                if heat > max_heat:
                    max_heat = heat
            except Exception:
                continue

        # 生成月份标签
        month_labels = []
        current_month = None
        for i in range((end - start).days + 1):
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
