import os
from pydantic import BaseModel
from nonebot import get_plugin_config
from dotenv import load_dotenv  # 用于加载 .env 文件
# 加载 .env 文件
load_dotenv()


# 配置模型
class AlgoConfig(BaseModel):
    # 使用 .env 中的环境变量或者默认值
    clist_username: str = os.getenv("algo_clist_username", "")
    clist_api_key: str = os.getenv("algo_clist_api_key", "")
    # 查询天数
    days: int = int(os.getenv("algo_days", 7))
    # 查询结果数量限制
    limit: int = int(os.getenv("algo_limit", 20))
    # 提醒提前时间
    remind_pre: int = int(os.getenv("algo_remind_pre", 30))
    # 排序字段
    order_by: str = os.getenv("algo_order_by", "start")
    # 保存路径
    save_path: str = os.getenv("algo_save_path", "data/algo/subscribes.json")

    @property
    def default_params(self) -> dict:
        return {
            "username": self.clist_username,
            "api_key": self.clist_api_key,
            "order_by": self.order_by,
            "limit": self.limit,
        }

# 获取插件配置
algo_config:AlgoConfig = get_plugin_config(AlgoConfig)

