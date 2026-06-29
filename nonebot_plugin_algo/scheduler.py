import shutil
from pathlib import Path
from nonebot import require, get_bot
from nonebot.log import logger
from .config import luogu_save_path, cf_save_path
require("nonebot_plugin_apscheduler")
from nonebot_plugin_apscheduler import scheduler

luogu_cards_path = luogu_save_path / "cards"
cf_cards_path = cf_save_path / "cards"


async def cleanup_luogu_cards():
    """清理洛谷卡片文件"""
    try:
        if luogu_cards_path.exists():
            shutil.rmtree(luogu_cards_path)
            luogu_cards_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"已清理洛谷卡片目录: {luogu_cards_path}")
        else:
            logger.info("洛谷卡片目录不存在，无需清理")
    except Exception as e:
        logger.error(f"清理洛谷卡片时发生错误: {e}")


async def cleanup_cf_cards():
    """清理 CF 卡片文件"""
    try:
        if cf_cards_path.exists():
            shutil.rmtree(cf_cards_path)
            cf_cards_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"已清理 CF 卡片目录: {cf_cards_path}")
        else:
            logger.info("CF 卡片目录不存在，无需清理")
    except Exception as e:
        logger.error(f"清理 CF 卡片时发生错误: {e}")


def init_scheduler():
    """初始化定时任务"""
    # 每天3次执行洛谷清理任务
    scheduler.add_job(
        cleanup_luogu_cards,
        "cron",
        hour=2,
        minute=0,
        id="cleanup_luogu_cards_2",
        name="清理洛谷卡片(2点)",
        replace_existing=True,
    )
    scheduler.add_job(
        cleanup_luogu_cards,
        "cron",
        hour=10,
        minute=0,
        id="cleanup_luogu_cards_10",
        name="清理洛谷卡片(10点)",
        replace_existing=True,
    )
    scheduler.add_job(
        cleanup_luogu_cards,
        "cron",
        hour=18,
        minute=0,
        id="cleanup_luogu_cards_18",
        name="清理洛谷卡片(18点)",
        replace_existing=True,
    )

    # 每天3次执行 CF 清理任务
    scheduler.add_job(
        cleanup_cf_cards,
        "cron",
        hour=3,
        minute=0,
        id="cleanup_cf_cards_3",
        name="清理CF卡片(3点)",
        replace_existing=True,
    )
    scheduler.add_job(
        cleanup_cf_cards,
        "cron",
        hour=11,
        minute=0,
        id="cleanup_cf_cards_11",
        name="清理CF卡片(11点)",
        replace_existing=True,
    )
    scheduler.add_job(
        cleanup_cf_cards,
        "cron",
        hour=19,
        minute=0,
        id="cleanup_cf_cards_19",
        name="清理CF卡片(19点)",
        replace_existing=True,
    )

    logger.info("洛谷卡片清理定时任务已启动，每天2点、10点、18点执行")
    logger.info("CF卡片清理定时任务已启动，每天3点、11点、19点执行")


# 在模块导入时自动初始化定时任务
init_scheduler()
