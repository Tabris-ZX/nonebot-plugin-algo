from datetime import datetime,timezone

from nonebot.log import logger
from .util import Util
from .config import algo_config

class Query:

    @classmethod
    async def ans_today_contests(cls) -> str:
        """生成今日比赛信息"""
        today_contest = await Util.get_upcoming_contests(days=1)
        if isinstance(today_contest, int):
            return f"比赛获取失败,状态码{today_contest}"
        if not today_contest:   
            return "今天没有比赛安排哦~"
        msg_list = []
        for contest in today_contest:
            start_time = datetime.fromisoformat(contest["start"]).replace(tzinfo=timezone.utc)
            local_time = start_time.astimezone().strftime("%Y-%m-%d %H:%M")

            msg_list.append(
                f"🏆比赛名称: {contest['event']}\n"
                f"⏰比赛时间: {local_time}\n"
                f"📌比赛ID: {contest['id']}\n"
                f"🔗比赛链接: {contest.get('href', '无链接')}"
            )

        logger.info(f"返回今日 {len(msg_list)} 场比赛信息")
        return f"今日有{len(msg_list)}场比赛安排(test)：\n\n" + "\n\n".join(msg_list)

    @classmethod
    async def ans_recent_contests(cls) -> str:
        """生成近期比赛信息"""
        recent_contest = await Util.get_upcoming_contests()
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

        logger.info(f"返回近期 {len(msg_list)} 场比赛信息(test)")
        return f"近期有{len(msg_list)}场比赛安排：\n\n" + "\n\n".join(msg_list)

    @classmethod
    async def ans_conditions_contest(cls,
        resource_id=None,
        days:int= algo_config.days
        ) -> str:
        """条件查询比赛信息"""
        conditions_contest = await Util.get_upcoming_contests(
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
        conditions_problem = await Util.get_problems_by_contest(contest_ids)
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