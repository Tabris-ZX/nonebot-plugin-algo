from nonebot.plugin import PluginMetadata
from .config import AlgoConfig

__plugin_meta__ = PluginMetadata(
    name="algo helper",
    description="支持 oj算法比赛日程查询/订阅,洛谷/Codeforces信息绑定/查询~",
    usage="""
    **比赛查询:**
    今日比赛: 查询今日未开始的比赛
    近期比赛 ?[平台id] ?[天数=7] : 按条件查询比赛
    比赛题目 [比赛id] : 查询比赛题目

    **洛谷服务:**
    bindlg [用户名/id]: 绑定洛谷用户
    mylg:查询自己洛谷信息
    lg [用户名/id]: 查询指定用户洛谷简略信息
    lg -f [用户名/id]: 查询指定用户洛谷详细信息

    **cf服务:**
    bindcf [uid]: 绑定 CF 用户
    mycf : 查询自己 CF 信息
    cf [uid]: 查询指定用户cf简略信息
    cf -f [uid] 查询指定用户cf详细信息

    **订阅功能:**
    比赛订阅(订阅比赛) [比赛id] : 订阅比赛提醒
    取消订阅 [比赛id] : 取消指定id订阅
    清空订阅: 清空所有订阅
    订阅列表: 查看当前订阅

    **示例:**
    近期比赛 162 10 : 查询洛谷平台10天内的比赛
    lg 123456 : 查询洛谷用户信息
    cf -f tourist : 查询 tourist 的 CF 完整信息

    **常用ID对应:**
    CodeForces -> 1
    AtCoder -> 93
    洛谷 -> 162
    牛客 -> 166

    """.strip(),
    homepage="https://github.com/Tabris-ZX/nonebot-plugin-algo.git",
    type="application",
    config=AlgoConfig,
    supported_adapters={"~onebot.v11"},
)

from . import command 
from . import scheduler

