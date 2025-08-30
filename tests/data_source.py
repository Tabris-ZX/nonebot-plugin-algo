import asyncio
from datetime import datetime, timezone, timedelta
import httpx
from typing import List, Dict, Union
from .config import AlgoConfig

# from nonebot.log import logger
# from nonebot.plugin import get_plugin_config
import logging
logger = logging.getLogger(__name__)

algo_config = AlgoConfig()

class DataSource:
    
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
        days:int= algo_config.days,
        resource_id=None,
        ) -> dict:
        #当前时间
        now_start = datetime.now(timezone.utc)
        #构建比赛开始的最晚时间
        last_start = (now_start + timedelta(days=days)).replace(hour=0, minute=0, second=0)
        #构建参数
        base_params = {
            "start__gte": now_start.strftime("%Y-%m-%dT%H:%M:%S"),
            "start__lte": last_start.strftime("%Y-%m-%dT%H:%M:%S"),
            **algo_config.default_params,
            **{"resource_id": resource_id},
        }
        base_params = {k: v for k, v in base_params.items() if v is not None}
        return cls._normalize_params(base_params)

    @classmethod
    def build_problem_params(cls, contest_ids: int) -> dict:
        base_params = {
            **algo_config.default_params,
            "contest_ids": str(contest_ids),
            "order_by": "rating",
            "limit": algo_config.limit,
        }
        base_params = {k: v for k, v in base_params.items() if v is not None}
        return cls._normalize_params(base_params)

    @classmethod
    async def get_contest(cls,
        resource_id=None,
        days:int= algo_config.days
        ) -> Union[List[Dict], int]:
        params = cls.build_contest_params(
            resource_id=resource_id,
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
    async def get_problems(cls, contest_ids: int) -> Union[List[Dict], int]:
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
    async def ans_today(cls) -> str:
        """生成今日比赛信息"""
        today_contest = await cls.get_contest(days=1)
        if isinstance(today_contest, int):
            return f"比赛获取失败,状态码{today_contest}"
        if not today_contest:   
            return "今天没有比赛安排哦~"
        msg_list = []
        for contest in today_contest:
            start_time = datetime.fromisoformat(contest["start"])
            local_time = start_time.astimezone().strftime("%Y-%m-%d %H:%M")

            msg_list.append(
                f"🏆比赛名称: {contest['event']}\n"
                f"⏰比赛时间: {local_time}\n"
                f"📌比赛ID: {contest['id']}\n"
                f"🔗比赛链接: {contest.get('href', '无链接')}"
            )

        logger.info(f"返回今日 {len(msg_list)} 场比赛信息")
        return f"今日有{len(msg_list)}场比赛安排：\n\n" + "\n\n".join(msg_list)

    @classmethod
    async def ans_recent(cls) -> str:
        """生成近期比赛信息"""
        recent_contest = await cls.get_contest()
        if isinstance(recent_contest, int):
            return f"比赛获取失败,状态码{recent_contest}"
        msg_list = []
        for contest in recent_contest:
            start_time = datetime.fromisoformat(contest["start"])
            local_time = start_time.astimezone().strftime("%Y-%m-%d %H:%M")
            msg_list.append(
                f"🏆比赛名称: {contest['event']}\n"
                f"⏰比赛时间: {local_time}\n"
                f"📌比赛ID: {contest['id']}\n"
                f"🔗比赛链接: {contest.get('href', '无链接')}"
            )

        logger.info(f"返回近期 {len(msg_list)} 场比赛信息")
        return f"近期有{len(msg_list)}场比赛安排：\n\n" + "\n\n".join(msg_list)

    @classmethod
    async def ans_conditions_contest(cls,
        resource_id=None,
        days:int= algo_config.days
        ) -> str:
        """条件查询比赛信息"""
        conditions_contest = await cls.get_contest(
            resource_id=resource_id,
            days=days
            )
        if isinstance(conditions_contest, int):
            return f"比赛获取失败,状态码{conditions_contest}"
        msg_list = []
        for contest in conditions_contest:
            start_time = datetime.fromisoformat(contest["start"])
            local_time = start_time.astimezone().strftime("%Y-%m-%d %H:%M")
            msg_list.append(
                f"🏆比赛名称: {contest['event']}\n"
                f"⏰比赛时间: {local_time}\n"
                f"📌比赛ID: {contest['id']}\n"
                f"🔗比赛链接: {contest.get('href', '无链接')}"
            )

        logger.info(f"返回近期 {len(msg_list)} 场比赛信息")
        return f"近期有{len(msg_list)}场比赛安排：\n\n" + "\n\n".join(msg_list)

    @classmethod
    async def ans_conditions_problem(cls, contest_ids:int) -> str:
        """条件查询题目信息"""
        conditions_problem = await cls.get_problems(contest_ids)
        if isinstance(conditions_problem, int):
            return f"题目获取失败,状态码{conditions_problem}"
        msg_list = []
        for problem in conditions_problem:
            msg_list.append(
                f"🏆题目名称: {problem['name']}\n"
                f"⏰题目难度: {problem['rating']}\n"
                f"📌题目ID: {problem['id']}\n"
                f"🔗题目链接: {problem.get('url', '无链接')}"
            )

        logger.info(f"返回本场比赛{len(msg_list)}条题目信息")
        return f"本场比赛有{len(msg_list)}条题目信息：\n\n" + "\n\n".join(msg_list)