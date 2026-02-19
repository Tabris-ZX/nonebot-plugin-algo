from nonebot.plugin import PluginMetadata
from .config import AlgoConfig

__plugin_meta__ = PluginMetadata(
    name="算法比赛助手",
    description="支持 oj算法比赛日程查询/订阅,洛谷信息绑定/查询,后面还会增添更多功能~",
    usage="""
    比赛查询:
    今日比赛: 查询今日未开始的比赛
    近期比赛 ?[平台id] ?[天数=7] : 按条件查询比赛
    比赛题目 [比赛id] : 查询比赛题目

    洛谷服务:
    绑定洛谷 [用户名/id]: 绑定洛谷用户
    我的洛谷 :查询自己洛谷信息
    洛谷信息 [用户名/id]: 查询指定洛谷用户信息

    订阅功能:
    订阅 ?-i [比赛id] ?-e [比赛名称] : 订阅比赛提醒(名称订阅暂时不支持含空格)
    取消/清空订阅 [比赛id] : 取消/清空订阅
    订阅列表: 查看当前订阅

    示例: 
    比赛 163 10 : 查询洛谷平台10天内的比赛
    洛谷信息 123456 : 查询洛谷用户信息

    常用ID对应: 
    CodeForces -> 1
    CodeChef -> 2
    AtCoder -> 93
    洛谷 -> 162
    牛客 -> 166
    
    """,
    homepage="https://github.com/Tabris-ZX/nonebot-plugin-algo.git",
    type="application",
    config=AlgoConfig,
    supported_adapters={"~onebot.v11"},
)

from . import command 
from . import scheduler

