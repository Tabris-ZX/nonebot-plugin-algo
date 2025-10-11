import asyncio
import shutil
from pathlib import Path
from nonebot import require, get_bot
from nonebot.log import logger
from .config import luogu_save_path
require("nonebot_plugin_apscheduler")
from nonebot_plugin_apscheduler import scheduler

cards_save_path = luogu_save_path / "cards"

async def cleanup_luogu_cards():
    """清理洛谷卡片文件"""
    try:
        if cards_save_path.exists():
            # 删除cards目录下的所有文件
            shutil.rmtree(cards_save_path)
            # 重新创建目录
            cards_save_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"已清理洛谷卡片目录: {cards_save_path}")
        else:
            logger.info("洛谷卡片目录不存在，无需清理")
    except Exception as e:
        logger.error(f"清理洛谷卡片时发生错误: {e}")

def init_scheduler():
    """初始化定时任务"""
    # 每天3次执行清理任务
    scheduler.add_job(
        cleanup_luogu_cards,
        "cron",
        hour=2,
        minute=0,
        id="cleanup_cards_2",
        name="清理洛谷卡片(2点)",
        replace_existing=True
    )
    scheduler.add_job(
        cleanup_luogu_cards,
        "cron",
        hour=10,
        minute=0,
        id="cleanup_cards_10",
        name="清理洛谷卡片(10点)",
        replace_existing=True
    )
    scheduler.add_job(
        cleanup_luogu_cards,
        "cron",
        hour=18,
        minute=0,
        id="cleanup_cards_18",
        name="清理洛谷卡片(18点)",
        replace_existing=True
    )
    
    logger.info("洛谷卡片清理定时任务已启动，每天2点、10点、18点执行")

# 在模块导入时自动初始化定时任务
init_scheduler()
