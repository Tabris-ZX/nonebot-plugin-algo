<div align="center">
  <a href="https://v2.nonebot.dev/store">
    <img src="https://github.com/A-kirami/nonebot-plugin-template/blob/resources/nbp_logo.png" width="180" height="180" alt="NoneBotPluginLogo">
  </a>
  <br>
  <p>
    <img src="https://github.com/A-kirami/nonebot-plugin-template/blob/resources/NoneBotPlugin.svg" width="240" alt="NoneBotPluginText">
  </p>
</div>

<div align="center">

# 算法比赛助手

_基于 NoneBot2 的算法比赛查询、订阅提醒与 OJ 用户信息卡片插件_

<a href="./LICENSE">
  <img src="https://img.shields.io/github/license/Tabris-ZX/nonebot-plugin-algo.svg" alt="license">
</a>
<a href="https://pypi.python.org/pypi/nonebot-plugin-algo">
  <img src="https://img.shields.io/pypi/v/nonebot-plugin-algo.svg" alt="pypi">
</a>
<img src="https://img.shields.io/badge/python-3.10+-blue.svg" alt="python">
<a href="https://github.com/nonebot/nonebot2">
  <img src="https://img.shields.io/badge/nonebot-2.4.3+-red.svg" alt="nonebot2">
</a>

</div>

## 简介

`nonebot-plugin-algo` 是一个面向算法竞赛群和个人机器人的 NoneBot2 插件，支持通过 clist.by 查询比赛与题目，订阅比赛开始提醒，并生成洛谷、Codeforces 用户信息卡片。

比赛查询功能依赖 [clist.by API](https://clist.by/api/v4/doc/)，使用前需要准备 `clist_username` 和 `clist_api_key`。用户卡片截图依赖 Playwright 浏览器运行环境。

## 功能

- 查询今日、近期比赛，支持按 OJ 平台 ID 和天数筛选
- 查询指定比赛的题目信息
- 订阅比赛提醒，支持群聊和私聊场景
- 查询、绑定洛谷用户，支持简略卡片和详细卡片
- 查询、绑定 Codeforces 用户，展示 rating、提交热力图、近期比赛等信息
- 使用本地存储保存订阅数据、用户绑定数据和卡片缓存

## 安装

### 使用 nb-cli

```bash
nb plugin install nonebot-plugin-algo
```

### 使用 uv

```bash
uv add nonebot-plugin-algo
```

### 使用 pip

```bash
pip install nonebot-plugin-algo
```

然后在 NoneBot 项目的 `pyproject.toml` 中启用插件：

```toml
[tool.nonebot]
plugins = ["nonebot_plugin_algo"]
```

如果需要生成洛谷或 Codeforces 信息卡片，还需要安装 Playwright Chromium：

```bash
uv run playwright install chromium
```

非 `uv` 环境可以使用：

```bash
python -m playwright install chromium
```

## 配置

在 NoneBot 项目的 `.env` 或 `.env.*` 中添加配置：

```env
# clist.by API 凭据，使用比赛查询和题目查询时必需
clist_username=your_username
clist_api_key=your_api_key

# 可选配置
algo_days=7
algo_limit=20
algo_remind_pre=30
algo_order_by=start
oj_include=[1,93,163,166,102]
```

配置项说明：

| 配置项 | 默认值 | 说明 |
| --- | --- | --- |
| `clist_username` | 空 | clist.by 用户名 |
| `clist_api_key` | 空 | clist.by API Key |
| `oj_include` | `[1,93,163,166,102]` | 默认查询的平台 ID 列表 |
| `algo_days` | `7` | 近期比赛默认查询天数 |
| `algo_limit` | `20` | clist.by API 返回数量上限 |
| `algo_remind_pre` | `30` | 比赛开始前多少分钟提醒 |
| `algo_order_by` | `start` | clist.by 排序字段 |

常用 clist.by 平台 ID：

| 平台 | ID |
| --- | --- |
| Codeforces | `1` |
| AtCoder | `93` |
| 洛谷 | `162` |
| 牛客 | `166` |

## 命令

### 比赛查询

| 命令 | 功能 | 示例 |
| --- | --- | --- |
| `今日比赛` | 查询今天未开始的比赛 | `今日比赛` |
| `近期比赛 [平台ID] [天数]` | 查询近期比赛，可选平台和天数 | `近期比赛 162 10` |
| `比赛题目 [比赛ID]` | 查询指定比赛题目 | `比赛题目 123456` |

### 订阅提醒

| 命令 | 功能 | 示例 |
| --- | --- | --- |
| `订阅 [比赛ID]` / `订阅比赛 [比赛ID]` | 订阅比赛提醒 | `订阅 123456` |
| `取消订阅 [比赛ID]` | 取消指定比赛订阅 | `取消订阅 123456` |
| `订阅列表` / `我的订阅` | 查看当前会话的订阅列表 | `订阅列表` |
| `清空订阅` | 清空当前会话的订阅 | `清空订阅` |

### 洛谷

| 命令 | 功能 | 示例 |
| --- | --- | --- |
| `绑定洛谷 [用户名或ID]` | 绑定洛谷账号 | `绑定洛谷 123456` |
| `我的洛谷` | 查询已绑定洛谷账号的简略卡片 | `我的洛谷` |
| `我的洛谷 -f` | 查询已绑定洛谷账号的详细卡片 | `我的洛谷 -f` |
| `/洛谷 [用户名或ID]` / `/lg [用户名或ID]` | 查询指定洛谷用户简略卡片 | `/lg 123456` |
| `/洛谷 -f [用户名或ID]` / `/lg -f [用户名或ID]` | 查询指定洛谷用户详细卡片 | `/lg -f 123456` |

别名：`洛谷绑定`、`绑定lg`、`lg绑定` 等同于 `绑定洛谷`。

### Codeforces

| 命令 | 功能 | 示例 |
| --- | --- | --- |
| `绑定cf [handle]` | 绑定 Codeforces 账号 | `绑定cf tourist` |
| `我的cf` | 查询已绑定 CF 账号的简略卡片 | `我的cf` |
| `我的cf -f` | 查询已绑定 CF 账号的详细卡片 | `我的cf -f` |
| `/cf [handle]` | 查询指定 CF 用户简略卡片 | `/cf tourist` |
| `/cf -f [handle]` | 查询指定 CF 用户详细卡片 | `/cf -f tourist` |

别名：`cf绑定` 等同于 `绑定cf`。

### 缓存

| 命令 | 功能 |
| --- | --- |
| `清空卡片` / `清理卡片` | 清空洛谷和 Codeforces 卡片缓存 |

卡片缓存会在每天 `02:00`、`10:00`、`18:00` 自动清理。

## 开发

本项目使用 `uv` 管理依赖和锁文件。

```bash
# 安装项目依赖和开发依赖
uv sync --all-groups

# 安装 Playwright Chromium
uv run playwright install chromium

# 运行代码检查
uv run ruff check .

# 格式化
uv run black .
uv run isort .

# 构建发行包
uv build
```

如果只想安装运行依赖：

```bash
uv sync
```

## 项目结构

```text
nonebot_plugin_algo/
  command.py          # NoneBot 命令入口
  config.py           # 插件配置和本地存储路径
  query.py            # 比赛与题目查询响应
  subscribe.py        # 比赛订阅、提醒和恢复任务
  scheduler.py        # 卡片缓存清理任务
  util.py             # clist.by API 请求工具
  oj/
    luogu/            # 洛谷 API 与卡片生成
    cf/               # Codeforces API 与卡片生成
  assets/             # 卡片模板、样式和图片资源
```

## 路线图

- [x] 比赛查询系统
- [x] 条件检索比赛
- [x] 比赛题目查询
- [x] 订阅提醒系统
- [x] 洛谷用户绑定与信息卡片
- [x] Codeforces 用户绑定与信息卡片
- [ ] AtCoder 用户信息查询
- [ ] 个性题单
- [ ] 题目链接解析

## 开源协议

本项目基于 [AGPL-3.0 License](LICENSE) 开源。
