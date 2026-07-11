import random
import base64
import httpx
from typing import Dict
from nonebot.log import logger
from jinja2 import Template
from ...config import cf_save_path, Mapper
from .api import CodeforcesAPI, CodeforcesRateLimitError, RATE_LIMIT_MESSAGE
from pathlib import Path
import html
from datetime import datetime, date, timedelta
from uuid import uuid4

ASSETS_PATH = Path(__file__).resolve().parents[2] / "assets"
TEMPLATE_PATH = ASSETS_PATH / "template" / "cf_card.html"
SAMPLE_TEMPLATE_PATH = ASSETS_PATH / "template" / "sample_card.html"
FULL_STYLE_PATH = ASSETS_PATH / "template" / "full-style.css"
SAMPLE_STYLE_PATH = ASSETS_PATH / "template" / "sample-style.css"
LOGO_PATH = ASSETS_PATH / "cf.webp"
BACKGROUND_DIR = ASSETS_PATH / "background"
FONT_DIR = ASSETS_PATH / "fonts"
cards_save_path = cf_save_path / "cards"

DEFAULT_WIDTH = 1440
DEFAULT_HEIGHT = 900


class Codeforces(CodeforcesAPI):
    @classmethod
    async def build_bind_user_info(cls, user_qq: str, full: bool = False) -> Path | str | None:
        """根据绑定的 QQ 号构建用户卡片"""
        handle = cls.get_bound_handle(user_qq)
        if handle is None:
            return None
        return await cls.build_user_info(handle, full=full)

    @classmethod
    async def build_user_info(cls, handle: str, full: bool = False) -> Path | str | None:
        """构建 CF 用户信息卡片"""
        try:
            info = await cls.get_user_info(handle, include_submissions=True)
        except CodeforcesRateLimitError:
            return RATE_LIMIT_MESSAGE
        if not info:
            return None
        img_output: Path = cards_save_path / f"{handle}.png"
        sample_output: Path = cards_save_path / f"{handle}_sample.png"
        img_output.parent.mkdir(parents=True, exist_ok=True)

        context = cls._build_user_card_context(info)
        try:
            if full:
                with open(TEMPLATE_PATH, encoding="utf-8") as f:
                    template = Template(f.read())
            else:
                with open(SAMPLE_TEMPLATE_PATH, encoding="utf-8") as f:
                    template = Template(f.read())
            background = cls._random_background_uri()
            handle_safe = html.escape(context["handle"])
            if context["rank"] == "legendary grandmaster" and handle_safe:
                name_styled = (
                    f"<span style='color:#111827'>{handle_safe[0]}</span>"
                    f"<span style='color:{context['rank_color']}'>{handle_safe[1:]}</span>"
                )
            else:
                name_styled = f"<span style='color:{context['rank_color']}'>{handle_safe}</span>"
            context = {
                **context,
                "name_styled": name_styled,
                "logo_src": cls._image_data_uri(LOGO_PATH),
                "background": background,
                "avatar": await cls._remote_image_data_uri(context["avatar"]),
                "font_faces": cls._font_faces(),
                **cls._theme_vars(context["rank_color"]),
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
            logger.error(f"读取模板失败: {e}")
            return None

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
            logger.warning(f"读取远程头像失败: {url} ({e})")
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
        """将 HTML 渲染为 PNG 图片"""
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
                context = await browser.new_context(
                    viewport={"width": int(width), "height": int(height or 1)},
                    device_scale_factor=2,
                )
                page = await context.new_page()
                await page.goto(html_path.as_uri(), wait_until="domcontentloaded")
                try:
                    await page.wait_for_load_state("load", timeout=3000)
                except PlaywrightTimeoutError:
                    pass
                await page.evaluate("document.fonts ? document.fonts.ready : Promise.resolve()")
                await page.wait_for_timeout(120)
                if height is None:
                    await page.screenshot(path=str(out_path), full_page=True, type="png")
                else:
                    await page.screenshot(
                        path=str(out_path),
                        clip={"x": 0, "y": 0, "width": width, "height": height},
                        type="png",
                    )
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
        """从 CF API 数据构建模板上下文"""
        handle = data["handle"]
        rating = data["rating"] if "rating" in data else 0
        max_rating = data["maxRating"] if "maxRating" in data else 0
        rank = (data["rank"] if "rank" in data else "unknown").lower()
        max_rank = (data["maxRank"] if "maxRank" in data else "unknown").lower()
        friend_of_count = data["friendOfCount"]
        avatar = data["titlePhoto"] if "titlePhoto" in data else data["avatar"]
        first_name = data["firstName"] if "firstName" in data else ""
        last_name = data["lastName"] if "lastName" in data else ""
        country = data["country"] if "country" in data else ""
        city = data["city"] if "city" in data else ""
        organization = data["organization"] if "organization" in data else ""
        last_online = data["lastOnlineTimeSeconds"] if "lastOnlineTimeSeconds" in data else 0
        registration = data["registrationTimeSeconds"] if "registrationTimeSeconds" in data else 0

        # 颜色
        rank_color = Mapper.cf_rank_color.get(rank, "#808080")
        max_rank_color = Mapper.cf_rank_color.get(max_rank, rank_color)
        rank_display = Mapper.cf_rank_names.get(rank, rank.capitalize())
        max_rank_display = Mapper.cf_rank_names.get(max_rank, max_rank.capitalize())

        # 格式化时间
        last_online_str = ""
        if last_online:
            dt = datetime.fromtimestamp(last_online)
            last_online_str = dt.strftime("%Y-%m-%d %H:%M")
        registration_str = ""
        if registration:
            dt = datetime.fromtimestamp(registration)
            registration_str = dt.strftime("%Y-%m-%d")

        # 昵称（如果有姓名则组合显示）
        display_name = handle
        if first_name or last_name:
            display_name = f"{first_name} {last_name}".strip()

        # Rating 历史 - 取最近若干场比赛
        rating_history = data["ratingHistory"]
        recent_contests: list[dict] = []
        for rh in rating_history[-5:]:
            recent_contests.append({
                "contest_name": rh["contestName"],
                "rank": rh["rank"],
                "old_rating": rh["oldRating"],
                "new_rating": rh["newRating"],
                "delta": rh["newRating"] - rh["oldRating"],
                "time": datetime.fromtimestamp(rh["ratingUpdateTimeSeconds"]).strftime("%Y-%m-%d"),
            })
        recent_contests = recent_contests[::-1]

        # Rating 曲线数据（用于 SVG chart）
        CHART_W = 760
        CHART_H = 260
        PAD_L = 58
        PAD_R = 18
        PAD_T = 18
        PAD_B = 36
        PLOT_W = CHART_W - PAD_L - PAD_R
        PLOT_H = CHART_H - PAD_T - PAD_B
        chart_points: list[dict] = []
        rating_bands: list[dict] = []
        chart_y_ticks: list[dict] = []
        chart_x_ticks: list[dict] = []
        if rating_history:
            min_time = rating_history[0]["ratingUpdateTimeSeconds"]
            max_time = rating_history[-1]["ratingUpdateTimeSeconds"]
            time_range = max(max_time - min_time, 1)
            min_rating = min(rh["newRating"] for rh in rating_history)
            max_history_rating = max(rh["newRating"] for rh in rating_history)
            chart_y_min = max(0, (min_rating // 200) * 200 - 200)
            chart_y_max = ((max_history_rating + 199) // 200) * 200 + 200
            chart_y_max = max(chart_y_max, 1600)
            rating_range = max(chart_y_max - chart_y_min, 1)

            band_defs = [
                (0, 1200, "#cfcfcf"),
                (1200, 1400, "#77ff77"),
                (1400, 1600, "#77ddbb"),
                (1600, 1900, "#aaaaff"),
                (1900, 2100, "#ff77ff"),
                (2100, 2300, "#ffcc88"),
                (2300, 2400, "#ffbb55"),
                (2400, 2600, "#ff7777"),
                (2600, 3000, "#ff3333"),
                (3000, max(chart_y_max, 4000), "#aa0000"),
            ]
            for low, high, color in band_defs:
                visible_low = max(low, chart_y_min)
                visible_high = min(high, chart_y_max)
                if visible_high <= visible_low:
                    continue
                y = PAD_T + (chart_y_max - visible_high) / rating_range * PLOT_H
                h = (visible_high - visible_low) / rating_range * PLOT_H
                rating_bands.append({
                    "x": PAD_L,
                    "y": round(y, 2),
                    "width": PLOT_W,
                    "height": round(h, 2),
                    "color": color,
                })

            # 采样以控制点数（最多 80 个点）
            sampled = rating_history
            if len(rating_history) > 80:
                step = len(rating_history) / 80
                sampled = [rating_history[int(i * step)] for i in range(80)]

            for rh in sampled:
                t = rh["ratingUpdateTimeSeconds"]
                r = rh["newRating"]
                x = PAD_L + (t - min_time) / time_range * PLOT_W
                y = PAD_T + (chart_y_max - r) / rating_range * PLOT_H
                chart_points.append({"x": round(x, 2), "y": round(y, 2), "rating": r})

            last_tick_y: float | None = None
            for tick in (1200, 1400, 1600, 1900, 2100, 2300, 2400, 2600, 3000, 4000):
                if chart_y_min < tick <= chart_y_max:
                    y = PAD_T + (chart_y_max - tick) / rating_range * PLOT_H
                    if last_tick_y is not None and abs(y - last_tick_y) < 18:
                        continue
                    chart_y_ticks.append({"value": tick, "y": round(y, 2)})
                    last_tick_y = y

            use_year_label = time_range >= 86400 * 365 * 2
            for i in range(6):
                ratio = i / 5
                ts = min_time + time_range * ratio
                x = PAD_L + PLOT_W * ratio
                chart_x_ticks.append({
                    "x": round(x, 2),
                    "label": datetime.fromtimestamp(ts).strftime("%Y" if use_year_label else "%m-%d"),
                })
        else:
            chart_y_min = 0
            chart_y_max = 0

        # 生成 rating 变化折线的 SVG polyline points
        polyline_points = " ".join(f"{p['x']},{p['y']}" for p in chart_points)

        # 首次参赛日期
        first_contest_time = ""
        if rating_history:
            first_ct = datetime.fromtimestamp(rating_history[0]["ratingUpdateTimeSeconds"])
            first_contest_time = first_ct.strftime("%Y-%m-%d")

        # 参赛场次
        contest_count = len(rating_history)
        heatmap_rows, heatmap_months = cls._build_heatmap(data["submissions"])
        submissions = data["submissions"]
        solved_count = cls._count_solved(submissions) if submissions else "--"

        return {
            "handle": handle,
            "display_name": display_name,
            "rating": rating,
            "max_rating": max_rating,
            "rank": rank,
            "max_rank": max_rank,
            "rank_color": rank_color,
            "max_rank_color": max_rank_color,
            "rank_display": rank_display,
            "max_rank_display": max_rank_display,
            "friend_of_count": friend_of_count,
            "avatar": avatar,
            "country": country,
            "city": city,
            "organization": organization,
            "last_online_str": last_online_str,
            "registration_str": registration_str,
            "first_contest_time": first_contest_time,
            "contest_count": contest_count,
            "solved_count": solved_count,
            "recent_contests": recent_contests,
            "chart_points": chart_points,
            "polyline_points": polyline_points,
            "rating_bands": rating_bands,
            "chart_y_ticks": chart_y_ticks,
            "chart_x_ticks": chart_x_ticks,
            "chart_y_min": chart_y_min,
            "chart_y_max": chart_y_max,
            "heatmap_rows": heatmap_rows,
            "heatmap_months": heatmap_months,
            "current_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

    @classmethod
    def _build_sample_context(cls, context: Dict) -> Dict:
        accent = context["rank_color"]
        return {
            "short_name": "CF",
            "logo_src": cls._image_data_uri(LOGO_PATH),
            "accent": accent,
            "accent_dark": cls._adjust_color(accent, -0.14),
            "accent_soft": cls._adjust_color(accent, 0.38),
            "avatar": context["avatar"],
            "name": context["handle"],
            "rating": context["rating"] or "--",
            "chip_left": f"MaxRating {context['max_rating'] or '--'}",
            "chip_right": f"{context['friend_of_count']} friends",
            "side_rows": [
                {"key": "solved", "value": context["solved_count"]},
                {"key": "contests", "value": context["contest_count"]},
                {"key": "registered", "value": context["registration_str"] or "--"},
            ],
        }

    @staticmethod
    def _adjust_color(color: str, amount: float) -> str:
        value = (color or "#ef4444").strip().lstrip("#")
        if len(value) == 3:
            value = "".join(ch * 2 for ch in value)
        try:
            rgb = [int(value[i:i + 2], 16) for i in (0, 2, 4)]
        except Exception:
            rgb = [239, 68, 68]
        target = 255 if amount >= 0 else 0
        ratio = abs(amount)
        mixed = [round(c * (1 - ratio) + target * ratio) for c in rgb]
        return "#" + "".join(f"{c:02x}" for c in mixed)

    @staticmethod
    def _count_solved(submissions: list[dict]) -> int:
        solved: set[str] = set()
        for sub in submissions:
            if sub.get("verdict") != "OK":
                continue
            problem = sub.get("problem") or {}
            contest_id = problem.get("contestId", "")
            index = problem.get("index", "")
            name = problem.get("name", "")
            key = f"{contest_id}:{index}:{name}" if contest_id or index else name
            if key:
                solved.add(key)
        return len(solved)

    @staticmethod
    def _build_heatmap(submissions: list[dict]) -> tuple[list[list[int]], list[dict]]:
        """构建最近 26 周公开提交热力图。"""
        today = date.today()
        end = today + timedelta(days=(5 - today.weekday()) % 7 + 1)
        start = end - timedelta(days=7 * 26 - 1)
        start = start - timedelta(days=(start.weekday() + 1) % 7)
        end = start + timedelta(days=7 * 26 - 1)

        daily_counts: dict[date, int] = {}
        for sub in submissions:
            ts = sub.get("creationTimeSeconds")
            if not ts:
                continue
            d = datetime.fromtimestamp(ts).date()
            if start <= d <= end:
                daily_counts[d] = daily_counts.get(d, 0) + 1

        max_count = max(daily_counts.values()) if daily_counts else 0
        row_order = [6, 0, 1, 2, 3, 4, 5]
        rows: list[list[int]] = [[] for _ in range(7)]
        month_labels: list[dict] = []
        current_month: int | None = None

        for day_offset in range((end - start).days + 1):
            cur = start + timedelta(days=day_offset)
            col = day_offset // 7
            if cur.day <= 7 and cur.month != current_month:
                month_labels.append({
                    "label": cur.strftime("%b"),
                    "left": f"{col / 26 * 100:.2f}%",
                })
                current_month = cur.month

            count = daily_counts.get(cur, 0)
            if max_count <= 0 or count <= 0:
                level = 0
            else:
                ratio = count / max_count
                level = max(1, min(5, int(round(ratio * 5))))

            row_index = row_order.index(cur.weekday())
            rows[row_index].append(level)

        return rows, month_labels
