from nonebot.plugin import PluginMetadata, get_plugin_config
from .config import AlgoConfig
from .query import Query
from nonebot_plugin_apscheduler import scheduler
from nonebot_plugin_alconna import (
    Alconna,
    Args,
    on_alconna,
)

__plugin_meta__ = PluginMetadata(
    name="算法比赛助手",
    description="<your_plugin_description>",
    usage="""
    今日比赛:
    近期比赛: 查询近期即将进行的比赛
    比赛 ?[平台id] ?[天数=7] : 按条件查询比赛
    题目 [比赛id] : 查询比赛题目
    clt官网: 查询clt官网
    订阅 [比赛id] : 提醒比赛开始

    示例: 比赛 163 10 : 查询洛谷平台3天内的比赛
    """,
    homepage="https://github.com/Tabris_ZX/nonebot-plugin-algo",
    type="application",
    config=AlgoConfig,
    supported_adapters=set(), 
)

# 查询全部比赛
recent_contest = on_alconna(
    Alconna("近期比赛"),
    aliases={"/近期"},
    priority=5,
    block=True,
)

@recent_contest.handle()
async def handle_all_matcher():
    msg = await Query.ans_recent_contests()
    await recent_contest.finish(msg)


# 查询今日比赛
query_today_contest = on_alconna(
    Alconna("今日比赛"),
    aliases={"/今日"},
    priority=5,
    block=True,
)

@query_today_contest.handle()
async def handle_today_match():
    msg = await Query.ans_today_contests()
    await query_today_contest.finish(msg)


# 按条件检索比赛
query_conditions_contest = on_alconna(
    Alconna("比赛",
     Args["resource_id?", int],
     Args["days?", int]),
    priority=5,
    block=True,
)


@query_conditions_contest.handle()
async def handle_match_id_matcher(
    resource_id=None,
    days: int = AlgoConfig.days,
):
    """
    查询条件比赛
    
    参数：
    resource_id: 比赛平台id
    days: 查询天数

    """

    msg = await Query.ans_conditions_contest(
        resource_id=resource_id,
        days=days
    )
    await query_conditions_contest.finish(msg)


query_conditions_problem = on_alconna(
    Alconna(
        "题目",
        Args["contest_ids", int],
    ),
    priority=5,
    block=True,
)

@query_conditions_problem.handle()
async def handle_problem_matcher(
    contest_ids: int,
):
    msg = await Query.ans_conditions_problem(contest_ids)
    await query_conditions_problem.finish(msg)


clist = on_alconna(
    Alconna("clt"),
    aliases={"/官网"},
    priority=5,
    block=True,
)

@clist.handle()
async def handle_clist_matcher():
    msg = "https://clist.by/"
    await clist.finish(msg)


subscribe_contests = on_alconna(
    Alconna(
        "订阅",
        Args["id?", int],
    ),
    priority=5,
    block=True,
)



@subscribe_contests.handle()
async def handle_subscribe_matcher(contest_id: int):
    """处理订阅命令：将当前用户订阅到指定比赛，并在比赛开始前提醒"""




# # 每日定时任务
# async def check(bot: Bot, group_id: str) -> bool:
#     return not await CommonUtils.task_is_block(bot, "today_match", group_id)


# @scheduler.scheduled_job(
#     "cron",
#     hour=6,  # 改为凌晨0点
#     minute=1,  # 第1分钟
# )
# async def send_daily_matches():
#     try:
#         msg = await DataSource.ans_today()
#         await broadcast_group(
#             msg,
#             log_cmd="今日比赛提醒",  # 修改日志标识
#             check_func=check,  # 保留检查函数
#         )
#         logger.info("每日比赛提醒发送成功")
#     except Exception as e:
#         logger.error(f"发送每日比赛提醒失败: {e}")
