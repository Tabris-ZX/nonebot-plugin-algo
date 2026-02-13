
from pydantic import BaseModel
from nonebot import get_plugin_config,require
from pathlib import Path
require("nonebot_plugin_localstore")
import nonebot_plugin_localstore as store

# 配置模型
class AlgoConfig(BaseModel):
    clist_username: str =""
    clist_api_key: str =""
    oj_include:list[int] = [1,93,163,166,102]
    # 查询天数
    algo_days: int = 7
    # 查询结果数量限制
    algo_limit: int =20
    # 提醒提前时间
    algo_remind_pre: int = 30
    # 排序字段
    algo_order_by: str = "start"
    # 洛谷cookie(选填,填写后可获取用户关注/动态信息,隐私设置用户)
    # luogu_cookie: str =""
    # luogu_x_csrf_token: str =""
    

    @property
    def default_params(self) -> dict:
        return {
            "username": self.clist_username,
            "api_key": self.clist_api_key,
            "resource_id__in": self.oj_include,
            "order_by": self.algo_order_by,
            "limit": self.algo_limit,
        }

# 获取插件存储
plugin_data_dir: Path = store.get_plugin_data_dir()

algo_config:AlgoConfig = get_plugin_config(AlgoConfig)

subscribe_save_path: Path = plugin_data_dir / "subscribes.json"
luogu_save_path: Path = plugin_data_dir / "luogu"
