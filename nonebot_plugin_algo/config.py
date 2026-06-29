
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
cf_save_path: Path = plugin_data_dir / "codeforces"


class Mapper:
    """颜色/名称映射常量"""

    # 洛谷难度等级名称映射
    luogu_difficulty_names: dict = {
        0: "暂无评定",
        1: "入门",
        2: "普及-",
        3: "普及",
        4: "普及+/提高-",
        5: "提高",
        6: "提高+/省选-",
        7: "省选/NOI-",
        8: "NOI/NOI+/CTS",
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

    # 洛谷题目难度颜色
    luogu_problem_level_color: list[str] = [
        "#bfbfbf",  # 0 暂无评定
        "#fe4c61",  # 1 入门
        "#f39c11",  # 2 普及-
        "#ffc116",  # 3 普及
        "#52c41a",  # 4 普及+/提高-
        "#19b7c6",  # 5 提高
        "#3498db",  # 6 提高+/省选-
        "#9d3dcf",  # 7 省选/NOI-
        "#0e1d69",  # 8 NOI/NOI+/CTS
    ]

    # 洛谷奖项颜色
    luogu_prize_color: dict = {
        "first": "#ffd700",
        "second": "#ffffff",
        "third": "#cd7f32",
        "other": "#888888",
    }

    # Codeforces rank 颜色
    cf_rank_color: dict = {
        "newbie": "#808080",
        "pupil": "#008000",
        "specialist": "#03a89e",
        "expert": "#0000ff",
        "candidate master": "#aa00aa",
        "master": "#ff8c00",
        "international master": "#ff8c00",
        "grandmaster": "#ff0000",
        "international grandmaster": "#ff0000",
        "legendary grandmaster": "#ff0000",
    }

    # CF rank 名称
    cf_rank_names: dict = {
        "newbie": "Newbie",
        "pupil": "Pupil",
        "specialist": "Specialist",
        "expert": "Expert",
        "candidate master": "Candidate Master",
        "master": "Master",
        "international master": "International Master",
        "grandmaster": "Grandmaster",
        "international grandmaster": "International Grandmaster",
        "legendary grandmaster": "Legendary Grandmaster",
    }
