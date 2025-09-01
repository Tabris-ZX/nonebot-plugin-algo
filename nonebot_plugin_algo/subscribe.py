from nonebot_plugin_apscheduler import scheduler
from nonebot.log import logger
# from nonebot.adapters import MessageSegment, Bot
from datetime import timedelta, datetime,timezone
import tzlocal
import json
import os
from typing import Dict, List, Optional

from .util import Util
from .config import algo_config

class Subscribe:
    # 订阅数据文件路径
    save_path = algo_config.save_path
    def __init__(self):
        self._ensure_data_dir()
        self.subscribes = self._load_subscribes()
    
    def _ensure_data_dir(self):
        """确保数据目录存在"""
        os.makedirs(os.path.dirname(self.save_path), exist_ok=True)
    
    def _load_subscribes(self) -> Dict[str, List[Dict]]:
        """加载订阅数据"""
        try:
            if os.path.exists(self.save_path):
                with open(self.save_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"加载订阅数据失败: {e}")
        return {}
    
    def _save_subscribes(self):
        """保存订阅数据"""
        try:
            with open(self.save_path, 'w', encoding='utf-8') as f:
                json.dump(self.subscribes, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存订阅数据失败: {e}")
    
    def add_subscribe(self, group_id: str, contest_id: str, event: str, start_time: str):
        """添加订阅"""
        if group_id not in self.subscribes:
            self.subscribes[group_id] = []
        
        # 检查是否已订阅
        for sub in self.subscribes[group_id]:
            if sub.get('contest_id') == contest_id:
                return False, "该比赛已订阅"
        
        subscribe_info = {
            'contest_id': contest_id,
            'event': event,
            'start_time': start_time,
            'subscribe_time': datetime.now().isoformat()
        }
        
        self.subscribes[group_id].append(subscribe_info)
        self._save_subscribes()
        return True, "订阅成功"
    
    def remove_subscribe(self, group_id: str, contest_id: str) -> bool:
        """取消订阅"""
        if group_id not in self.subscribes:
            return False
        
        for i, sub in enumerate(self.subscribes[group_id]):
            if sub.get('contest_id') == contest_id:
                del self.subscribes[group_id][i]
                self._save_subscribes()
                return True
        return False
    
    def get_group_subscribes(self, group_id: str) -> List[Dict]:
        """获取群组订阅列表"""
        return self.subscribes.get(group_id, [])
    
    def clear_group_subscribes(self, group_id: str) -> bool:
        """清空群组所有订阅"""
        if group_id in self.subscribes:
            del self.subscribes[group_id]
            self._save_subscribes()
            return True
        return False

    @classmethod
    async def send_contest_reminder(cls, contest_info: dict):
        """发送比赛提醒"""
        logger.info(f"比赛提醒: {contest_info['event']}")
        
        # 解析时间并转换为本地时间
        try:
            start_time = datetime.fromisoformat(contest_info['start_time'].replace('Z', '+00:00'))
            local_time = start_time.astimezone().strftime("%Y-%m-%d %H:%M")
        except:
            local_time = contest_info['start_time']
        
        # 构建提醒消息
        message = f"🔔比赛提醒\n\n"
        message += f"🏆比赛名称: {contest_info['event']}\n"
        message += f"⏰开始时间: {local_time}\n"
        message += f"🔗比赛链接: {contest_info.get('href', '无链接')}"
        
        try:
            # 使用 Bot 发送消息
            from nonebot import get_bot
            bot = get_bot()
            await bot.send_group_msg(
                group_id=contest_info["group_id"],
                message=message
            )
        except Exception as e:
            logger.error(f"发送比赛提醒失败: {e}")

    @classmethod
    async def subscribe_contest(cls,
     group_id: str,
     id: Optional[str] = None,  # 比赛id
     event: Optional[str] = None  # 比赛名称
     ) -> tuple[bool, str]:
        """订阅比赛"""
        if id is None and event is None:
            return False, "请提供比赛ID或比赛名称"
        
        try:
            contest_info = await Util.get_contest_info(id=id, event=event)
            if isinstance(contest_info, int) or contest_info is None or not contest_info:
                return False, "未找到相关比赛"
            
            contest = contest_info[0]  # 取第一个匹配的比赛
            
            # 创建订阅实例
            subscribe_manager = Subscribe()
            
            # 添加订阅
            success, msg = subscribe_manager.add_subscribe(
                group_id=group_id,
                contest_id=str(contest['id']),
                event=contest['event'],
                start_time=contest['start']
            )
            
            if not success:
                return False, msg
            
            # 设置定时提醒
            local_tz = tzlocal.get_localzone()  # 获取本地时区

            start_time = datetime.fromisoformat(contest['start']).replace(tzinfo=timezone.utc).astimezone(local_tz)
            remind_time = start_time - timedelta(minutes=algo_config.remind_pre)
            
            # 检查是否已经过了提醒时间
            if remind_time <= datetime.now(start_time.tzinfo):
                return False, "比赛开始时间已过或即将开始，无法订阅"
            
            # 添加定时任务
            job_id = f"contest_reminder_{group_id}_{contest['id']}"
            scheduler.add_job(
                func=cls.send_contest_reminder,
                args=({
                    'group_id': group_id,
                    'event': contest['event'],
                    'start_time': contest['start'],
                    'href': contest.get('href', '')
                },),
                trigger="date",
                run_date=remind_time,
                id=job_id,
                replace_existing=True
            )
            
            return True, f"订阅成功！比赛：{contest['event']}，将在 {remind_time.strftime('%Y-%m-%d %H:%M')} 提醒"
            
        except Exception as e:
            logger.exception(f"订阅比赛失败: {e}")
            return False, f"订阅失败：{str(e)}"
    
    @classmethod
    async def unsubscribe_contest(cls, group_id: str, contest_id: str) -> tuple[bool, str]:
        """取消订阅比赛"""
        try:
            subscribe_manager = Subscribe()
            
            # 取消订阅
            if subscribe_manager.remove_subscribe(group_id, contest_id):
                # 删除定时任务
                job_id = f"contest_reminder_{group_id}_{contest_id}"
                try:
                    scheduler.remove_job(job_id)
                except:
                    pass
                return True, "取消订阅成功"
            else:
                return False, "未找到该订阅"
                
        except Exception as e:
            logger.exception(f"取消订阅失败: {e}")
            return False, f"取消订阅失败：{str(e)}"
    
    @classmethod
    async def list_subscribes(cls, group_id: str) -> str:
        """列出群组订阅"""
        try:
            subscribe_manager = Subscribe()
            subscribes = subscribe_manager.get_group_subscribes(group_id)
            
            if not subscribes:
                return "当前群组暂无订阅"
            
            msg_list = []
            for sub in subscribes:
                # 解析开始时间并转换为本地时间
                try:
                    start_time = datetime.fromisoformat(sub['start_time'].replace('Z', '+00:00'))
                    local_time = start_time.astimezone().strftime("%Y-%m-%d %H:%M")
                except:
                    local_time = sub['start_time']
                
                # 解析订阅时间
                try:
                    subscribe_time = datetime.fromisoformat(sub['subscribe_time'].replace('Z', '+00:00'))
                    subscribe_local_time = subscribe_time.astimezone().strftime("%Y-%m-%d %H:%M")
                except:
                    subscribe_local_time = sub['subscribe_time']
                
                msg_list.append(
                    f"🏆比赛名称: {sub['event']}\n"
                    f"⏰比赛时间: {local_time}\n"
                    f"📌比赛ID: {sub['contest_id']}\n"
                    f"📅订阅时间: {subscribe_local_time}"
                )
            
            logger.info(f"返回群组 {len(msg_list)} 个订阅信息")
            return f"当前群组有{len(msg_list)}个订阅：\n\n" + "\n\n".join(msg_list)
            
        except Exception as e:
            logger.exception(f"获取订阅列表失败: {e}")
            return f"获取订阅列表失败：{str(e)}"
    
    @classmethod
    async def clear_subscribes(cls, group_id: str) -> tuple[bool, str]:
        """清空群组所有订阅"""
        try:
            subscribe_manager = Subscribe()
            
            # 获取当前订阅
            subscribes = subscribe_manager.get_group_subscribes(group_id)
            
            # 删除所有定时任务
            for sub in subscribes:
                job_id = f"contest_reminder_{group_id}_{sub['contest_id']}"
                try:
                    scheduler.remove_job(job_id)
                except:
                    pass
            
            # 清空订阅
            if subscribe_manager.clear_group_subscribes(group_id):
                return True, f"已清空 {len(subscribes)} 个订阅"
            else:
                return False, "当前群组暂无订阅"
                
        except Exception as e:
            logger.exception(f"清空订阅失败: {e}")
            return False, f"清空订阅失败：{str(e)}"

