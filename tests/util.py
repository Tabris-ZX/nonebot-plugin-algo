import asyncio
from datetime import datetime, timezone, timedelta
import httpx

from nonebot.log import logger
from typing import List, Dict, Union
from .config import algo_config

    
class Util:
    
    @staticmethod
    def _normalize_params(params: dict) -> dict:
        normalized: dict = {}
        for key, value in params.items():
            if isinstance(value, datetime):
                if value.tzinfo is None:
                    value = value.replace(tzinfo=timezone.utc)
                normalized[key] = value.isoformat(timespec="seconds")
            else:
                normalized[key] = value
        return normalized

    @classmethod
    def build_contest_params(cls,
        days=None, 
        resource_id=None, 
        id=None, 
        event=None,
        ) -> dict:
        #当前时间
        if days is None:
            base_params = {
                "id": id,
                "event": event,
                **algo_config.default_params,
            }
        else:
            now_start = datetime.now(timezone.utc)
            last_start = (now_start + timedelta(days=days)).replace(hour=0, minute=0, second=0)
            base_params = {
                "start__gte": now_start.strftime("%Y-%m-%dT%H:%M:%S"),
                "start__lte": last_start.strftime("%Y-%m-%dT%H:%M:%S"),
                **algo_config.default_params,
                **{"resource_id": resource_id},
            }
        base_params = {k: v for k, v in base_params.items() if v is not None}
        return cls._normalize_params(base_params)

    @classmethod
    def build_problem_params(cls,
        contest_ids=None, 
        url=None
        ) -> dict:
        base_params = {
            **algo_config.default_params,
            "contest_ids": str(contest_ids),
            "order_by": "rating",
            "limit": algo_config.limit,
            "url": url,
        }
        base_params = {k: v for k, v in base_params.items() if v is not None}
        return cls._normalize_params(base_params)

    @classmethod
    async def get_contest_info(cls,
        id=None, #比赛id
        event=None #比赛名称
        ) -> Union[List[Dict], int]:
        params = cls.build_contest_params(id=id, event=event)
        timeout = httpx.Timeout(10.0)
        for attempt in range(3):
            try:
                async with httpx.AsyncClient(timeout=timeout) as client:
                    response = await client.get("https://clist.by/api/v4/contest/", params=params)
                    response.raise_for_status()
                    return response.json().get("objects", [])
            except httpx.ReadTimeout:
                wait_time = min(2 ** attempt, 5)
                logger.warning(f"[Attempt {attempt + 1}/3] Timeout, retrying in {wait_time}s...")
                await asyncio.sleep(wait_time)

            except httpx.HTTPStatusError as e:
                if attempt == 2:
                    logger.error(f"比赛获取失败,状态码{e.response.status_code}: {e}")
                    return e.response.status_code
                await asyncio.sleep(2 ** attempt)

            except Exception as e:
                logger.exception(f"比赛获取失败,发生异常: {e}")
                return 0
        return 0

    @classmethod
    async def get_upcoming_contests(cls,
        resource_id=None, #平台id
        id=None, #比赛id
        days:int= algo_config.days #查询天数
        ) -> Union[List[Dict], int]:
        params = cls.build_contest_params(
            resource_id=resource_id,
            id=id,
            days=days
            )
        timeout = httpx.Timeout(10.0)

        for attempt in range(3):
            try:
                async with httpx.AsyncClient(timeout=timeout) as client:
                    response = await client.get(
                        "https://clist.by/api/v4/contest/",
                        params=params,
                    )
                    response.raise_for_status()
                    return response.json().get("objects", [])

            except httpx.ReadTimeout:
                wait_time = min(2 ** attempt, 5)
                logger.warning(f"[Attempt {attempt + 1}/3] Timeout, retrying in {wait_time}s...")
                await asyncio.sleep(wait_time)

            except httpx.HTTPStatusError as e:
                if attempt == 2:
                    logger.error(f"比赛获取失败,状态码{e.response.status_code}: {e}")
                    return e.response.status_code
                await asyncio.sleep(2 ** attempt)

            except Exception as e:
                logger.exception(f"比赛获取失败,发生异常: {e}")
                return 0
        return 0

    @classmethod
    async def get_problems_by_contest(cls,
        contest_ids: int #比赛id
        ) -> Union[List[Dict], int]: #比赛id
        params = cls.build_problem_params(contest_ids)
        timeout = httpx.Timeout(10.0)
        for attempt in range(3):
            try:
                async with httpx.AsyncClient(timeout=timeout) as client:
                    response = await client.get(
                        "https://clist.by/api/v4/problem/",
                        params=params,
                    )
                    response.raise_for_status()
                    return response.json().get("objects", [])

            except httpx.ReadTimeout:
                wait_time = min(2 ** attempt, 5)
                logger.warning(f"[Attempt {attempt + 1}/3] Timeout, retrying in {wait_time}s...")
                await asyncio.sleep(wait_time)

            except httpx.HTTPStatusError as e:
                if attempt == 2:
                    logger.error(f"题目获取失败,状态码{e.response.status_code}:{e}")
                    return e.response.status_code
                await asyncio.sleep(2 ** attempt)

            except Exception as e:
                logger.exception(f"题目获取失败,发生异常:{e}")
                return 0

        return 0

    @classmethod
    async def get_problems_info(cls,
        contest_ids=None,
        url=None
        ) -> Union[List[Dict], int]:
        """条件查询题目信息
        
        Args:
            contest_ids: 比赛id
            url: 题目链接
        Returns:
            str: 题目信息
        """
        parmas = cls.build_problem_params(contest_ids, url)
        timeout = httpx.Timeout(10.0)
        for attempt in range(3):
            try:
                async with httpx.AsyncClient(timeout=timeout) as client:
                    response = await client.get(
                        "https://clist.by/api/v4/problem/",
                        params=parmas,
                    )
                    response.raise_for_status()
                    return response.json().get("objects", [])

            except httpx.ReadTimeout:
                wait_time = min(2 ** attempt, 5)
                logger.warning(f"[Attempt {attempt + 1}/3] Timeout, retrying in {wait_time}s...")
                await asyncio.sleep(wait_time)

            except httpx.HTTPStatusError as e:  
                if attempt == 2:
                    logger.error(f"题目获取失败,状态码{e.response.status_code}:{e}")
                    return e.response.status_code
                await asyncio.sleep(2 ** attempt)

            except Exception as e:
                logger.exception(f"题目获取失败,发生异常:{e}")
                return 0
        return 0