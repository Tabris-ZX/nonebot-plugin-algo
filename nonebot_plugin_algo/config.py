
from pydantic import BaseModel
from nonebot import get_plugin_config,require
from pathlib import Path
require("nonebot_plugin_localstore")
import nonebot_plugin_localstore as store

# 配置模型
class AlgoConfig(BaseModel):
    clist_username: str =""
    clist_api_key: str =""
    # 查询天数
    algo_days: int = 7
    # 查询结果数量限制
    algo_limit: int =20
    # 提醒提前时间
    algo_remind_pre: int = 30
    # 排序字段
    algo_order_by: str = "start"
    # 洛谷cookie(选填,填写后可获取用户关注/动态信息)
    # luogu_cookie: str =""
    # luogu_x_csrf_token: str =""
    # luogu_x_requested_with: str =""
    
    # 洛谷难度等级名称映射
    luogu_difficulty_names: dict = {
        -1: "暂未评级",
        1: "入门",
        2: "普及-",
        3: "普及/提高-",
        4: "普及+/提高",
        5: "提高+/省选",
        6: "省选/NOI-",
        7: "NOI/NOI+/CTSC",
    }

    # 洛谷用户名颜色
    luogu_name_color: dict = {
        "Gray": "#bbbbbb",
        "Blue": "#0e90d2",
        "Green": "#5eb95e",
        "Orange": "#e67e22",
        "Red": "#e74c3c",
        "Purple": "#9d3dcf",
        "Cheater": "#ad8b00",
    }

    @property
    def default_params(self) -> dict:
        return {
            "username": self.clist_username,
            "api_key": self.clist_api_key,
            "order_by": self.algo_order_by,
            "limit": self.algo_limit,
        }

# 获取插件存储
plugin_data_dir: Path = store.get_plugin_data_dir()

algo_config:AlgoConfig = get_plugin_config(AlgoConfig)

subscribe_save_path: Path = plugin_data_dir / "subscribes.json"
luogu_save_path: Path = plugin_data_dir / "luogu"
