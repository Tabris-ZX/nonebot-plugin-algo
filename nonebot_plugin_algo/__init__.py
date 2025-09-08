from nonebot import require,get_driver
require("nonebot_plugin_alconna")
from nonebot_plugin_alconna import Alconna, Args, Option, on_alconna
from nonebot.adapters import Event
from nonebot.adapters.onebot.v11 import GroupMessageEvent, PrivateMessageEvent
from nonebot.plugin import PluginMetadata
from nonebot.log import logger

from .config import algo_config, AlgoConfig
from .query import Query
from .subscribe import Subscribe


__plugin_meta__ = PluginMetadata(
    name="算法比赛助手",
    description="算法比赛查询和订阅助手",
    usage="""
    今日比赛: 查询今日比赛
    近期比赛: 查询近期即将进行的比赛
    比赛 ?[平台id] ?[天数=7] : 按条件查询比赛
    题目 [比赛id] : 查询比赛题目
    clt官网: 查询clt官网
    
    订阅功能:
    订阅 ?i [比赛id] ?e [比赛名称] : 订阅比赛提醒
    取消订阅 [比赛id] : 取消订阅
    订阅列表: 查看当前订阅
    清空订阅: 清空所有订阅

    示例: 比赛 163 10 : 查询洛谷平台10天内的比赛
    """,
    homepage="https://github.com/Tabris-ZX/nonebot-plugin-algo.git",
    type="application",
    config=AlgoConfig,
    supported_adapters={"~onebot.v11"}
)

# 查询全部比赛
recent_contest = on_alconna(
    Alconna("近期比赛"),
    aliases={"近期"},
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
    aliases={"今日"},
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
    days: int = algo_config.algo_days,
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


# 订阅比赛
subscribe_contests = on_alconna(
    Alconna(
        "订阅",
        Option("i", Args["id?", int]),
        Option("e", Args["event__regex?", str]),
    ),
    priority=5,
    block=True,
)

@subscribe_contests.handle()
async def handle_subscribe_matcher(
    event: Event,
    id=None, #比赛id
    event__regex=None, #比赛名称
    ):
    """处理订阅命令：将当前用户订阅到指定比赛，并在比赛开始前提醒"""

    
    # 获取事件对象
    event_obj = event
    group_id = None
    user_id = None
    
    if isinstance(event_obj, GroupMessageEvent):
        group_id = str(event_obj.group_id)
        user_id = str(event_obj.user_id)
    elif isinstance(event_obj, PrivateMessageEvent):
        group_id = "null" 
        user_id = str(event_obj.user_id)
    else:
        await subscribe_contests.finish("不支持的聊天类型")
    
    success, msg = await Subscribe.subscribe_contest(
        group_id=group_id,  # type: ignore
        id=str(id) if id else None,
        event__regex=event__regex, 
        user_id=user_id
    )
    
    await subscribe_contests.finish(msg)

# 取消订阅
unsubscribe_contests = on_alconna(
    Alconna(
        "取消订阅",
        Args["contest_id", int],
    ),
    priority=5,
    block=True,
)

@unsubscribe_contests.handle()
async def handle_unsubscribe_matcher(event: Event, contest_id: int):
    """取消订阅比赛"""
    from nonebot.adapters.onebot.v11 import GroupMessageEvent, PrivateMessageEvent
    from nonebot.adapters import Event
        
    event_obj = event
    group_id = None
    user_id = None
    
    if isinstance(event_obj, GroupMessageEvent):
        group_id = str(event_obj.group_id)
        user_id = str(event_obj.user_id)
    elif isinstance(event_obj, PrivateMessageEvent):
        group_id = "null"  # 私聊时群组ID为null字符串
        user_id = str(event_obj.user_id)
    else:
        await unsubscribe_contests.finish("不支持的聊天类型")
    
    success, msg = await Subscribe.unsubscribe_contest(
        group_id=group_id,  # type: ignore
        contest_id=str(contest_id),
        user_id=user_id
    )
    
    await unsubscribe_contests.finish(msg)

# 查看订阅列表
list_subscribes = on_alconna(
    Alconna("订阅列表"),
    aliases={"我的订阅"},
    priority=5,
    block=True,
)

@list_subscribes.handle()
async def handle_list_subscribes(event: Event):
    """查看当前订阅列表"""
    from nonebot.adapters.onebot.v11 import GroupMessageEvent, PrivateMessageEvent
    from nonebot.adapters import Event
    
    event_obj = event
    group_id = None
    user_id = None
    
    if isinstance(event_obj, GroupMessageEvent):
        group_id = str(event_obj.group_id)
        user_id = str(event_obj.user_id)
    elif isinstance(event_obj, PrivateMessageEvent):
        group_id = "null"  # 私聊时群组ID为null字符串
        user_id = str(event_obj.user_id)
    else:
        await list_subscribes.finish("不支持的聊天类型")
    
    msg = await Subscribe.list_subscribes(group_id, user_id) # type: ignore
    await list_subscribes.finish(msg)

# 清空订阅
clear_subscribes = on_alconna(
    Alconna("清空订阅"),
    aliases={"取消订阅"},
    priority=5,
    block=True,
)

@clear_subscribes.handle()
async def handle_clear_subscribes(event: Event):
    """清空当前的所有订阅"""
    from nonebot.adapters.onebot.v11 import GroupMessageEvent, PrivateMessageEvent
    from nonebot.adapters import Event
    
    event_obj = event
    group_id = None
    user_id = None
    
    if isinstance(event_obj, GroupMessageEvent):
        group_id = str(event_obj.group_id)
        user_id = str(event_obj.user_id)
    elif isinstance(event_obj, PrivateMessageEvent):
        group_id = "null"  # 私聊时群组ID为null字符串
        user_id = str(event_obj.user_id)
    else:
        await clear_subscribes.finish("不支持的聊天类型")
    
    success, msg = await Subscribe.clear_subscribes(group_id, user_id) # type: ignore
    await clear_subscribes.finish(msg)



#Bot启动时恢复定时任务
@get_driver().on_startup
async def restore_scheduled_jobs():
    """Bot启动时恢复所有定时任务"""
    try:
        restored_count = await Subscribe.restore_scheduled_jobs()
        logger.info(f"算法比赛助手启动完成，恢复了 {restored_count} 个定时任务")
    except Exception as e:
        logger.error(f"恢复定时任务失败: {e}")


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
