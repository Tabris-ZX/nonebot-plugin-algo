
from nonebot.log import logger

from .config import algo_config
from .util import Util

class Query:
    
    @staticmethod
    def _format_contest_info(contest: dict) -> str:
        """格式化比赛信息"""
        return (
            f"🏆比赛名称: {contest['event']}\n"
            f"⏰比赛时间: {Util.utc_to_local(contest['start']).strftime('%Y-%m-%d %H:%M')}\n"
            f"📌比赛ID: {contest['id']}\n"
            f"🔗比赛链接: {contest.get('href', '无链接')}"
        )
    
    @staticmethod
    def _format_problem_info(problem: dict) -> str:
        """格式化题目信息"""
        return (
            f"🏆题目名称: {problem['name']}\n"
            f"⏰题目难度: {problem['rating']}\n"
            f"📌题目ID: {problem['id']}\n"
            f"🔗题目链接: {problem.get('url', '无链接')}"
        )

    @classmethod
    async def ans_today_contests(cls) -> str:
        """生成今日比赛信息"""
        contests = await Util.get_upcoming_contests(days=1)
        if isinstance(contests, int):
            return f"比赛获取失败,状态码{contests}"
        if not contests:   
            return "今天没有比赛安排哦~"
        
        msg_list = [cls._format_contest_info(contest) for contest in contests]
        logger.info(f"返回今日 {len(msg_list)} 场比赛信息")
        return f"今日有{len(msg_list)}场比赛安排(algo)：\n\n" + "\n\n".join(msg_list)

    @classmethod
    async def ans_recent_contests(cls) -> str:
        """生成近期比赛信息"""
        contests = await Util.get_upcoming_contests()
        if isinstance(contests, int):
            return f"比赛获取失败,状态码{contests}"
        
        msg_list = [cls._format_contest_info(contest) for contest in contests]
        logger.info(f"返回近期 {len(msg_list)} 场比赛信息")
        return f"近期有{len(msg_list)}场比赛安排：\n\n" + "\n\n".join(msg_list)

    @classmethod
    async def ans_conditions_contest(
        cls,
        resource_id=None,
        days:int= algo_config.algo_days
    ) -> str:
        """条件查询比赛信息"""
        contests = await Util.get_upcoming_contests(resource_id=resource_id, days=days)
        if isinstance(contests, int):
            return f"比赛获取失败,状态码{contests}"
        
        msg_list = [cls._format_contest_info(contest) for contest in contests]
        logger.info(f"返回近期 {len(msg_list)} 场比赛信息")
        return f"近期有{len(msg_list)}场比赛安排：\n\n" + "\n\n".join(msg_list)

    @classmethod
    async def ans_conditions_problem(cls, contest_ids:int) -> str:
        """条件查询题目信息"""
        problems = await Util.get_problems_by_contest(contest_ids)
        if isinstance(problems, int):
            return f"题目获取失败,状态码{problems}"
        
        msg_list = [cls._format_problem_info(problem) for problem in problems]
        logger.info(f"返回本场比赛{len(msg_list)}条题目信息")
        return f"本场比赛有{len(msg_list)}条题目信息：\n\n" + "\n\n".join(msg_list)