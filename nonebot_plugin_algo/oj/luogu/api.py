import json
from pathlib import Path
from typing import Dict

import httpx
from nonebot.log import logger

from ...config import luogu_save_path

users_save_path = luogu_save_path / "users.json"


class LuoguAPI:
    headers = {
        "user-agent": "",
        "X-Lentille-Request": "content-only",
        "x-requested-with": "XMLHttpRequest",
    }
    base_url = "https://www.luogu.com.cn"

    @staticmethod
    async def request(url: str, headers: dict = headers) -> Dict | None:
        try:
            timeout = httpx.Timeout(10.0)
            async with httpx.AsyncClient(timeout=timeout, follow_redirects=True, headers=headers) as client:
                response = await client.get(url)
            response.raise_for_status()
            return response.json()
        except (httpx.HTTPError, ValueError) as e:
            logger.error(f"洛谷请求失败: {url} ({type(e).__name__}: {e})")
            return None

    @classmethod
    async def search_user_id(cls, keyword: str) -> int | None:
        data = await cls.request(cls.base_url + f"/api/user/search?keyword={keyword}")
        if not data:
            return None
        try:
            return int(data["users"][0]["uid"])
        except (KeyError, IndexError, TypeError, ValueError):
            return None

    @classmethod
    async def get_user_info(cls, user: str | int) -> Dict | None:
        if isinstance(user, int):
            user_id = user
        else:
            user_id = await cls.search_user_id(user)
        if user_id is None:
            return None

        user_info = await cls.request(cls.base_url + f"/user/{user_id}")
        if user_info:
            passed_detail_url = cls.base_url + f"/user/{user_id}/practice"
            headers = {**cls.headers, "referer": f"{cls.base_url}/user/{user_id}"}
            passed_detail = await cls.request(passed_detail_url, headers=headers)
            if passed_detail:
                user_info["data"]["passed"] = passed_detail["data"]["passed"]
        return user_info

    @classmethod
    async def bind_luogu_user(cls, user_qq: str, user: str | int) -> bool:
        if isinstance(user, int):
            user_id = user
        else:
            user_id = await cls.search_user_id(user)
        if user_id is None:
            return False

        users = cls._load_bound_users()
        users[user_qq] = user_id
        cls._save_bound_users(users)
        return True

    @classmethod
    def get_bound_user(cls, user_qq: str) -> int | str | None:
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
