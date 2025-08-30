import os
from dotenv import load_dotenv
from pydantic import BaseModel

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))
class AlgoConfig(BaseModel):
    days: int = int(os.getenv("algo_days", 3))
    limit: int = int(os.getenv("algo_limit", 20))
    remind_pre: int = int(os.getenv("algo_remind_pre", 30))

    clist_username: str = os.getenv("algo_clist_username", "")
    clist_api_key: str = os.getenv("algo_clist_api_key", "")
    order_by: str = os.getenv("algo_order_by", "start")

    @property
    def default_params(self) -> dict:
        return {
            "username": self.clist_username,
            "api_key": self.clist_api_key,
            "order_by": self.order_by,
            "limit": self.limit,
        }

