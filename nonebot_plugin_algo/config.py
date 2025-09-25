
from pydantic import BaseModel
from nonebot import get_plugin_config

# 配置模型
class AlgoConfig(BaseModel):
    # 使用 .env 中的环境变量或者默认值
    algo_clist_username: str =""
    algo_clist_api_key: str =""
    # 查询天数
    algo_days: int = 7
    # 查询结果数量限制
    algo_limit: int =20
    # 提醒提前时间
    algo_remind_pre: int = 30
    # 排序字段
    algo_order_by: str = "start"

    @property
    def default_params(self) -> dict:
        return {
            "username": self.algo_clist_username,
            "api_key": self.algo_clist_api_key,
            "order_by": self.algo_order_by,
            "limit": self.algo_limit,
        }

# 获取插件配置

algo_config:AlgoConfig = get_plugin_config(AlgoConfig)
