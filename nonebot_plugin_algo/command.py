import sched
from nonebot import require, get_driver
require("nonebot_plugin_alconna")
require("nonebot_plugin_localstore")
require("nonebot_plugin_apscheduler")
from nonebot_plugin_alconna import Alconna, Args, Option, on_alconna, UniMessage
from nonebot_plugin_uninfo import Uninfo
from nonebot.adapters.onebot.v11 import GroupMessageEvent, PrivateMessageEvent, MessageSegment,Event
from nonebot.log import logger
from .config import algo_config
from .query import Query
from .subscribe import Subscribe
from .luogu import Luogu
from .scheduler import cleanup_luogu_cards

# 查询全部比赛
# recent_contest = on_alconna(
#     Alconna("近期比赛"),
#     priority=5,
#     block=True,
# )

# 查询今日比赛
query_today_contest = on_alconna(
    Alconna("今日比赛"),
    priority=5,
    block=True,
)

# 按条件检索比赛
query_conditions_contest = on_alconna(
    Alconna(
        "近期比赛",
        Args["resource_id?", int],
        Args["days?", int],
    ),
    priority=5,
    block=True,
)

query_conditions_problem = on_alconna(
    Alconna(
        "比赛题目",
        Args["contest_ids", int],
    ),
    priority=5,
    block=True,
)

# 订阅比赛
subscribe_contests = on_alconna(
    Alconna(
        "订阅",
        Option("-i", Args["id?", int]),
        Option("-e", Args["event__regex?", str]),
    ),
    aliases={"订阅比赛"},
    priority=5,
    block=True,
)

# 取消订阅
unsubscribe_contests = on_alconna(
    Alconna(
        "取消订阅",
        Args["contest_id", int],
    ),
    priority=5,
    block=True,
)

# 查看订阅列表
list_subscribes = on_alconna(
    Alconna("订阅列表"),
    aliases={"我的订阅"},
    priority=5,
    block=True,
)

# 清空订阅
clear_subscribes = on_alconna(
    Alconna("清空订阅"),
    priority=5,
    block=True,
)

luogu_info = on_alconna(
    Alconna("洛谷信息",
        Args["user", str | int],
    ),
    priority=5,
    block=True,
)

bind_luogu = on_alconna(
    Alconna("绑定洛谷",
        Args["user", str | int],
    ),
    aliases={"洛谷绑定"},
    priority=5,
    block=True,
)

my_luogu = on_alconna(
    Alconna("我的洛谷"),
    priority=5,
    block=True,
)

clear_luogu_cards = on_alconna(
    Alconna("清空洛谷卡片"),
    aliases={"清空洛谷"},
    priority=5,
    block=True,
)

@bind_luogu.handle()
async def handle_bind_luogu(session:Uninfo,user: str| int):
    """绑定洛谷用户"""
    user_qq = session.user.id
    if await Luogu.bind_luogu_user(user_qq,user):
        await bind_luogu.finish("绑定成功!",reply_to=True)
    else:
        await bind_luogu.finish("绑定失败!",reply_to=True)

@my_luogu.handle()
async def handle_my_luogu(event:Event,session:Uninfo):
    """查询自己的洛谷信息"""
    user_qq = session.user.id;
    msg = await Luogu.build_bind_user_info(user_qq)
    if msg is None:
        await UniMessage("你还未绑定洛谷账号捏~").finish(reply_to=True)
    await UniMessage.image(path=msg).finish(reply_to=True)

@clear_luogu_cards.handle()
async def handle_clear_luogu_cards():
    """清空洛谷卡片缓存"""
    await cleanup_luogu_cards()
    await clear_luogu_cards.finish(f"已清空洛谷卡片缓存！")


@luogu_info.handle()
async def handle_luogu_info(user: str| int):
    """查询指定用户洛谷信息"""
    msg = await Luogu.build_user_info(user)
    if msg is None:
        await luogu_info.finish("该用户不存在或未通过实名认证捏~")
    await UniMessage.image(path=msg).finish(reply_to=True)

# @recent_contest.handle()
# async def handle_all_matcher():
#     """查询近期比赛"""
#     msg = await Query.ans_recent_contests()
#     await recent_contest.finish(msg)

@query_today_contest.handle()
async def handle_today_match():
    """查询今日比赛"""
    msg = await Query.ans_today_contests()
    await query_today_contest.finish(msg)

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
        days=days,
    )
    await query_conditions_contest.finish(msg)

@query_conditions_problem.handle()
async def handle_problem_matcher(
    contest_ids: int,
):
    """按条件检索题目"""
    msg = await Query.ans_conditions_problem(contest_ids)
    await query_conditions_problem.finish(msg)

@subscribe_contests.handle()
async def handle_subscribe_matcher(
    event: Event,
    id=None,  # 比赛id
    event__regex=None,  # 比赛名称
):
    """处理订阅命令：将当前用户订阅到指定比赛，并在比赛开始前提醒"""
    try:
        group_id, user_id = parse_event_info(event)
        success, msg = await Subscribe.subscribe_contest(
            group_id=group_id,
            id=str(id) if id else None,
            event__regex=event__regex,
            user_id=user_id,
        )
        await subscribe_contests.finish(msg)
    except ValueError as e:
        await subscribe_contests.finish(str(e))

@unsubscribe_contests.handle()
async def handle_unsubscribe_matcher(event: Event, contest_id: int):
    """取消订阅比赛"""
    try:
        group_id, user_id = parse_event_info(event)
        success, msg = await Subscribe.unsubscribe_contest(
            group_id=group_id,
            contest_id=str(contest_id),
            user_id=user_id,
        )
        await unsubscribe_contests.finish(msg)
    except ValueError as e:
        await unsubscribe_contests.finish(str(e))

@list_subscribes.handle()
async def handle_list_subscribes(event: Event):
    """查看当前订阅列表"""
    try:
        group_id, user_id = parse_event_info(event)
        msg = await Subscribe.list_subscribes(group_id, user_id)
        await list_subscribes.finish(msg)
    except ValueError as e:
        await list_subscribes.finish(str(e))

@clear_subscribes.handle()
async def handle_clear_subscribes(event: Event):
    """清空当前的所有订阅"""
    try:
        group_id, user_id = parse_event_info(event)
        success, msg = await Subscribe.clear_subscribes(group_id, user_id)
        await clear_subscribes.finish(msg)
    except ValueError as e:
        await clear_subscribes.finish(str(e))

# Bot 启动时恢复定时任务
@get_driver().on_startup
async def restore_scheduled_jobs():
    """Bot启动时恢复所有定时任务"""
    try:
        restored_count = await Subscribe.restore_scheduled_jobs()
        logger.info(f"算法比赛助手启动完成，恢复了 {restored_count} 个定时任务")
    except Exception as e:
        logger.error(f"恢复定时任务失败: {e}")


def parse_event_info(event: Event) -> tuple[str, str]:
    """解析事件信息，返回group_id和user_id"""
    if isinstance(event, GroupMessageEvent):
        return str(event.group_id), str(event.user_id)
    elif isinstance(event, PrivateMessageEvent):
        return "null", str(event.user_id)
    else:
        raise ValueError("不支持的聊天类型")

