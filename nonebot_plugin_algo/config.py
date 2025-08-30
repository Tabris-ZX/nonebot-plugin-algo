import os
from pydantic import BaseModel

class AlgoConfig(BaseModel):
    #clist用户名,api_key
    clist_username: str = os.getenv("algo_clist_username", "")
    clist_api_key: str = os.getenv("algo_clist_api_key", "")
    #近期的天数
    days: int = int(os.getenv("algo_days", 7))
    #比赛数目限制
    limit: int = int(os.getenv("algo_limit", 20))   
    #提醒提前时间（分钟）
    remind_pre: int = int(os.getenv("algo_remind_pre", 30))
    #查询排序字段
    order_by: str = os.getenv("algo_order_by", "start")

    @property
    def default_params(self) -> dict:
        return {
            "username": self.clist_username,
            "api_key": self.clist_api_key,
            "order_by": self.order_by,
            "limit": self.limit,
        }
