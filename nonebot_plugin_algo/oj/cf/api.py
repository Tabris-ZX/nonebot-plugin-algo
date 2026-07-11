import json
import asyncio
from pathlib import Path
from typing import Dict

import httpx
from nonebot.log import logger

from ...config import cf_save_path

users_save_path = cf_save_path / "users.json"
RATE_LIMIT_MESSAGE = "请求频繁,请稍候"


class CodeforcesRateLimitError(Exception):
    pass


class CodeforcesAPI:
    headers = {
        "user-agent": "nonebot-plugin-algo/0.2.7",
    }
    base_url = "https://codeforces.com/api"
    _request_lock = asyncio.Lock()

    @classmethod
    async def request(cls, url: str, params: dict = None) -> Dict | None:
        last_error = ""
        for attempt in range(1, 4):
            try:
                async with cls._request_lock:
                    timeout = httpx.Timeout(15.0)
                    async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
                        response = await client.get(url, params=params)

                response.raise_for_status()
                data = response.json()
                if data.get("status") == "OK":
                    return data.get("result")

                comment = data.get("comment", "Unknown error")
                if not cls._is_rate_limited(comment=comment):
                    logger.error(f"CF API 返回错误: {comment}")
                    return None
                last_error = comment
            except httpx.HTTPStatusError as e:
                if e.response.status_code != 429:
                    logger.error(f"CF API 请求失败: {url} ({e.response.status_code})")
                    return None
                last_error = f"HTTP {e.response.status_code}"
            except (httpx.HTTPError, ValueError) as e:
                last_error = f"{type(e).__name__}: {e}"

            if attempt < 3:
                logger.warning(f"CF API 请求频率受限，2 秒后重试({attempt}/3): {url}")
                await asyncio.sleep(2)

        logger.error(f"CF API 请求频繁，重试后仍失败: {url} ({last_error})")
        raise CodeforcesRateLimitError(RATE_LIMIT_MESSAGE)

    @staticmethod
    def _is_rate_limited(comment: str = "") -> bool:
        text = (comment or "").lower()
        return "limit" in text or "too many" in text or "frequent" in text

    @classmethod
    async def get_user_info(cls, handle: str, include_submissions: bool = True) -> Dict | None:
        url = cls.base_url + "/user.info"
        result = await cls.request(url, {"handles": handle})
        if not result or not isinstance(result, list) or len(result) == 0:
            return None
        user_data = result[0]

        rating_result = await cls.request(cls.base_url + "/user.rating", {"handle": handle})
        user_data["ratingHistory"] = rating_result if isinstance(rating_result, list) else []

        if include_submissions:
            status_result = await cls.request(
                cls.base_url + "/user.status",
                {"handle": handle, "from": 1, "count": 10000},
            )
            user_data["submissions"] = status_result if isinstance(status_result, list) else []
        else:
            user_data["submissions"] = []
        return user_data

    @classmethod
    async def bind_cf_user(cls, user_qq: str, handle: str) -> bool | str:
        try:
            user_info = await cls.get_user_info(handle)
        except CodeforcesRateLimitError:
            return RATE_LIMIT_MESSAGE
        if user_info is None:
            return False

        users = cls._load_bound_users()
        users[user_qq] = handle
        cls._save_bound_users(users)
        return True

    @classmethod
    def get_bound_handle(cls, user_qq: str) -> str | None:
        return cls._load_bound_users().get(user_qq)

    @staticmethod
    def _load_bound_users() -> dict:
        if not users_save_path.exists():
            return {}
        with open(users_save_path, "r", encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def _save_bound_users(users: dict) -> None:
        users_save_path.parent.mkdir(parents=True, exist_ok=True)
        with open(users_save_path, "w", encoding="utf-8") as f:
            json.dump(users, f, ensure_ascii=False, indent=4)
