import json
import os
from datetime import timedelta, datetime
from typing import Dict, List, Optional, Union
from nonebot.log import logger
from nonebot import require
require("nonebot_plugin_apscheduler")
from nonebot_plugin_apscheduler import scheduler
from .config import algo_config,subscribe_save_path
from .util import Util

class Subscribe:
    # 订阅数据文件路径
    save_path = subscribe_save_path

    def __init__(self):
        self._ensure_data_dir()
        self.subscribes = self._load_subscribes()
    
    @staticmethod
    def _get_key(group_id: str, user_id: Optional[str] = None) -> str:
        """获取存储键：私聊场景使用用户ID，群聊使用群ID"""
        return user_id if group_id == "null" and user_id else group_id
    
    def _ensure_data_dir(self):
        """确保数据目录存在"""
        os.makedirs(os.path.dirname(self.save_path), exist_ok=True)
    
    @staticmethod
    def _parse_datetime(dt_str: Union[str, datetime]) -> Optional[datetime]:
        """统一解析日期时间"""
        if isinstance(dt_str, datetime):
            return dt_str
        if not dt_str:
            return None
        try:
            return datetime.fromisoformat(dt_str)
        except ValueError:
            try:
                return datetime.strptime(dt_str, '%Y-%m-%d %H:%M')
            except ValueError:
                return None

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
            logger.info(f"订阅数据已保存: {self.save_path}")
        except Exception as e:
            logger.error(f"保存订阅数据失败: {e} (path={self.save_path})")
    
    def add_subscribe(
        self, 
        group_id: str, 
        contest_id: str, 
        event: str, 
        start_time: datetime, 
        user_id: Optional[str] = None, 
        href: Optional[str] = None
    ):
        """添加订阅"""
        key = self._get_key(group_id, user_id)
        if key not in self.subscribes:
            self.subscribes[key] = [] #type: ignore
        
        # 检查是否已订阅
        for sub in self.subscribes[key]: #type: ignore
            if sub.get('contest_id') == contest_id:
                return False, "该比赛已订阅"
        
        subscribe_info = {
            'contest_id': contest_id,
            'event': event,
            'start_time': start_time.isoformat(),
            'subscribe_time': datetime.now().isoformat(),
            'user_id': user_id,
            'group_id': group_id,
            'remind_time': (start_time - timedelta(minutes=algo_config.algo_remind_pre)).isoformat(),
            'href': href
        }
        
        self.subscribes[key].append(subscribe_info) #type: ignore
        self._save_subscribes()
        return True, "订阅成功"
    
    def remove_subscribe(
        self, 
        group_id: str, 
        contest_id: str, 
        user_id: Optional[str] = None
    ) -> bool:
        """取消订阅"""
        key = self._get_key(group_id, user_id)
        if key not in self.subscribes:
            return False
        
        for i, sub in enumerate(self.subscribes[key]):
            if sub.get('contest_id') == contest_id:
                del self.subscribes[key][i]
                self._save_subscribes()
                return True
        return False
    
    def get_group_subscribes(
        self, 
        group_id: str, 
        user_id: Optional[str] = None
    ) -> List[Dict]:
        """获取订阅列表"""
        key = self._get_key(group_id, user_id)
        return self.subscribes.get(key, []) #type: ignore
    
    def clear_group_subscribes(
        self, 
        group_id: str, 
        user_id: Optional[str] = None
    ) -> bool:
        """清空所有订阅"""
        key = self._get_key(group_id, user_id)
        if key in self.subscribes:
            del self.subscribes[key]
            self._save_subscribes()
            return True
        return False

    @classmethod
    async def send_contest_reminder(cls, contest_info: dict):
        """发送比赛提醒"""
        logger.info(f"比赛提醒: {contest_info['event']}")
        
        # 获取本地时间
        dt = cls._parse_datetime(contest_info['start_time'])
        local_time = dt.strftime('%Y-%m-%d %H:%M') if dt else str(contest_info['start_time'])
        
        # 构建提醒消息
        message = f"🔔比赛提醒\n\n"
        message += f"🏆比赛名称: {contest_info['event']}\n"
        message += f"⏰开始时间: {local_time}\n"
        message += f"🔗比赛链接: {contest_info.get('href', '无链接')}"
        
        try:
            # 使用 Bot 发送消息
            from nonebot import get_bot
            bot = get_bot()
            
            # 根据是否有群组ID决定发送方式
            if contest_info.get("group_id") and contest_info.get("group_id") != "null":
                await bot.send_group_msg(
                    group_id=contest_info["group_id"],
                    message=message
                )
            elif contest_info.get("user_id"):
                await bot.send_private_msg(
                    user_id=contest_info["user_id"],
                    message=message
                )
            
            # 发送成功后，移除该场比赛的订阅记录
            try:
                subscribe_manager = Subscribe()
                group_id = contest_info.get("group_id", "null")
                user_id = contest_info.get("user_id")
                contest_id = str(contest_info.get("contest_id", ""))
                if contest_id:
                    removed = subscribe_manager.remove_subscribe(group_id, contest_id, user_id)
                    if removed:
                        logger.info(f"已移除订阅: {contest_info.get('event')} (contest_id={contest_id})")
                    else:
                        logger.info(f"未找到订阅以移除: {contest_info.get('event')} (contest_id={contest_id})")
            except Exception as e:
                logger.error(f"发送后移除订阅失败: {e}")

            # 发送成功后，清理已过期的订阅
            await cls.cleanup_expired_subscriptions()
            
        except Exception as e:
            logger.error(f"发送比赛提醒失败: {e}")

    @classmethod
    async def subscribe_contest(
        cls,
        group_id: str,
        id: str,  # 比赛id
        user_id: Optional[str] = None  # 用户id
    ) -> tuple[bool, str]:
        """订阅比赛"""
        try:
            contest_info = await Util.get_contest_info(id=id)
            logger.info(f"比赛信息: {contest_info}")
            if isinstance(contest_info, int) or contest_info is None or not contest_info:
                return False, "未找到相关比赛"
            
            # 遍历所有匹配的比赛，找到第一个未来的比赛
            contest = None
            for c in contest_info:
                local_start_time = Util.utc_to_local(c['start'])
                if local_start_time.tzinfo is None:
                    current_time = datetime.now()
                else:
                    current_time = datetime.now(local_start_time.tzinfo)
                if local_start_time > current_time:
                    contest = c
                    break
            
            if contest is None:
                return False, f"未找到{algo_config.algo_remind_pre}分钟后的比赛，无法订阅"
            
            # 创建订阅实例
            subscribe_manager = Subscribe()
            
            # 添加订阅
            success, msg = subscribe_manager.add_subscribe(
                group_id=group_id,
                contest_id=str(contest['id']),
                event=contest['event'],
                start_time=Util.utc_to_local(contest['start']),
                user_id=user_id,
                href=contest.get('href')
            )
            
            if not success:
                return False, msg
            
            # 设置定时提醒
            remind_time = local_start_time - timedelta(minutes=algo_config.algo_remind_pre) #type: ignore
            
            # 检查提醒时间是否已经过了
            if remind_time.tzinfo is None: #type: ignore
                # 如果remind_time没有时区信息，使用本地时区
                current_time = datetime.now()
            else:
                current_time = datetime.now(remind_time.tzinfo) #type: ignore
            
            if remind_time <= current_time: #type: ignore
                return False, "比赛即将开始，无法订阅"
            
            # 添加定时任务
            key = cls._get_key(group_id, user_id)
            job_id = f"contest_reminder_{key}_{contest['id']}"
            scheduler.add_job(
                func=cls.send_contest_reminder,
                args=({
                    'group_id': group_id,
                    'user_id': user_id,
                    'contest_id': str(contest['id']),
                    'event': contest['event'],
                    'start_time': Util.utc_to_local(contest['start']),
                    'href': contest.get('href', '')
                },),
                trigger="date",
                run_date=remind_time,
                id=job_id,
                replace_existing=True
            )
            
            return True, f"订阅成功！比赛：{contest['event']}，将在 {remind_time.strftime('%Y-%m-%d %H:%M')} 提醒" #type: ignore
            
        except Exception as e:
            logger.exception(f"订阅比赛失败: {e}")
            return False, f"订阅失败：{str(e)}"
    
    @classmethod
    async def unsubscribe_contest(
        cls, 
        group_id: str, 
        contest_id: str, 
        user_id: Optional[str] = None
    ) -> tuple[bool, str]:
        """取消订阅比赛"""
        try:
            subscribe_manager = Subscribe()
            
            # 取消订阅
            if subscribe_manager.remove_subscribe(group_id, contest_id, user_id):
                # 删除定时任务
                key = Subscribe._get_key(group_id, user_id)
                job_id = f"contest_reminder_{key}_{contest_id}"
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
    async def list_subscribes(
        cls, 
        group_id: str, 
        user_id: Optional[str] = None
    ) -> str:
        """列出订阅"""
        try:
            subscribe_manager = Subscribe()
            subscribes = subscribe_manager.get_group_subscribes(group_id, user_id)
            
            if not subscribes:
                return "当前暂无订阅"
            
            msg_list = []
            for sub in subscribes:
                # 解析开始时间并转换为本地时间
                dt_start = cls._parse_datetime(sub['start_time'])
                start_time = dt_start.strftime('%Y-%m-%d %H:%M') if dt_start else sub['start_time']
                # 解析订阅时间
                dt_sub = cls._parse_datetime(sub['subscribe_time'])
                subscribe_time = dt_sub.strftime('%Y-%m-%d %H:%M') if dt_sub else sub['subscribe_time']
            
                msg_list.append(
                    f"🏆比赛名称: {sub['event']}\n"
                    f"⏰比赛时间: {start_time}\n"  
                    f"📌比赛ID: {sub['contest_id']}\n"
                    f"📅订阅时间: {subscribe_time}\n"
                    f"🔗比赛链接: {sub.get('href', '无链接')}"
                )
            
            logger.info(f"返回 {len(msg_list)} 个订阅信息")
            return f"当前有{len(msg_list)}个订阅：\n\n" + "\n\n".join(msg_list)
            
        except Exception as e:
            logger.exception(f"获取订阅列表失败: {e}")
            return f"获取订阅列表失败：{str(e)}"
    
    @classmethod
    async def clear_subscribes(
        cls, 
        group_id: str, 
        user_id: Optional[str] = None
    ) -> tuple[bool, str]:
        """清空所有订阅"""
        try:
            subscribe_manager = Subscribe()
            
            # 获取当前订阅
            subscribes = subscribe_manager.get_group_subscribes(group_id, user_id)
            
            # 删除所有定时任务
            key = Subscribe._get_key(group_id, user_id)
            for sub in subscribes:
                job_id = f"contest_reminder_{key}_{sub['contest_id']}"
                try:
                    scheduler.remove_job(job_id)
                except:
                    pass
            
            # 清空订阅
            if subscribe_manager.clear_group_subscribes(group_id, user_id):
                return True, f"已清空 {len(subscribes)} 个订阅"
            else:
                return False, "当前暂无订阅"
                
        except Exception as e:
            logger.exception(f"清空订阅失败: {e}")
            return False, f"清空订阅失败：{str(e)}"

    @classmethod
    async def restore_scheduled_jobs(cls):
        """恢复所有定时任务"""
        try:
            subscribe_manager = Subscribe()
            restored_count = 0
            
            # 遍历所有订阅
            for key, subscribes in subscribe_manager.subscribes.items():
                for sub in subscribes:
                    try:
                        # 解析提醒时间
                        remind_time = cls._parse_datetime(sub['remind_time'])
                        if not remind_time:
                            continue
                            
                        # 检查是否已经过了提醒时间
                        if remind_time.tzinfo is None:
                            now = datetime.now()
                        else:
                            now = datetime.now(remind_time.tzinfo)
                        if remind_time <= now:
                            logger.info(f"跳过已过期的定时任务: {sub['event']}")
                            continue
                        
                        # 重新创建定时任务
                        job_id = f"contest_reminder_{key}_{sub['contest_id']}"
                        scheduler.add_job(
                            func=cls.send_contest_reminder,
                            args=({
                                'group_id': sub.get('group_id'),
                                'user_id': sub.get('user_id'),
                                'contest_id': sub.get('contest_id'),
                                'event': sub['event'],
                                'start_time': datetime.fromisoformat(sub['start_time']).strftime('%Y-%m-%d %H:%M'),
                                'href': sub.get('href', '')
                            },),
                            trigger="date",
                            run_date=remind_time,
                            id=job_id,
                            replace_existing=True
                        )
                        restored_count += 1
                        logger.info(f"恢复定时任务: {sub['event']} -> {remind_time}")
                        
                    except Exception as e:
                        logger.error(f"恢复定时任务失败 {sub.get('event', 'unknown')}: {e}")
                        continue
            
            logger.info(f"成功恢复 {restored_count} 个定时任务")
            return restored_count
            
        except Exception as e:
            logger.exception(f"恢复定时任务失败: {e}")
            return 0

    @classmethod
    async def cleanup_expired_subscriptions(cls):
        """清理已过期的订阅"""
        try:
            subscribe_manager = Subscribe()
            cleaned_count = 0
            
            # 遍历所有订阅
            for key, subscribes in list(subscribe_manager.subscribes.items()):
                # 使用列表副本进行迭代，以便在迭代过程中删除元素
                for sub in list(subscribes):
                    try:
                        # 解析比赛开始时间
                        start_time = cls._parse_datetime(sub['start_time'])
                        if not start_time:
                            continue
                        
                        # 检查比赛是否已经结束（假设比赛持续2小时）
                        end_time = start_time + timedelta(hours=2)
                        if start_time.tzinfo is None:
                            now = datetime.now()
                        else:
                            now = datetime.now(start_time.tzinfo)
                        
                        if end_time < now:
                            # 比赛已结束，删除订阅
                            subscribes.remove(sub)
                            cleaned_count += 1
                            logger.info(f"清理过期订阅: {sub['event']}")
                            
                    except Exception as e:
                        logger.error(f"清理订阅时出错 {sub.get('event', 'unknown')}: {e}")
                        continue
                
                # 如果该键下没有订阅了，删除整个键
                if not subscribes:
                    del subscribe_manager.subscribes[key]
            
            # 保存更改
            if cleaned_count > 0:
                subscribe_manager._save_subscribes()
                logger.info(f"清理了 {cleaned_count} 个过期订阅")
            
            return cleaned_count
            
        except Exception as e:
            logger.exception(f"清理过期订阅失败: {e}")
            return 0
