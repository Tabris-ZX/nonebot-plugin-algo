<div align="center">

## nonebot-plugin-algo

_✨ 算法比赛与题目信息查询助手 ✨_

<a href="./LICENSE">
    <img src="https://img.shields.io/github/license/Tabris-ZX/nonebot-plugin-algo.svg" alt="license">
  </a>
  <a href="https://pypi.python.org/pypi/nonebot-plugin-algo">
    <img src="https://img.shields.io/pypi/v/nonebot-plugin-algo.svg" alt="pypi">
  </a>
  <img src="https://img.shields.io/badge/python-3.9+-blue.svg" alt="python">

</div>

## 简介

基于 NoneBot2 与 clist.by API 的算法比赛助手插件，支持查询今日/近期比赛、按条件检索比赛/题目列表，以及订阅比赛提醒等功能。

## 功能特性

### 基础查询功能
- **查询近期比赛**：`近期比赛`（别名：`/近期`）
- **查询今日比赛**：`今日比赛`（别名：`/今日`）
- **条件检索比赛**：`比赛 [平台id] [天数]`
  - `平台id` 为站点 ID（来自 clist.by）
  - `天数` 为查询天数，默认来自配置 `algo_days`
- **查询比赛题目**：`题目 [比赛id]`
- **clist 官网链接**：`clt`（别名：`/官网`）

### 订阅提醒功能 ⭐
- **订阅比赛提醒**：`订阅 [比赛id]`
  - 订阅后将在比赛开始前自动提醒
  - 提醒时间可通过配置项 `algo_remind_pre` 设置
  - 支持查看当前订阅列表

## 安装

### 使用 nb-cli

```bash
nb plugin install nonebot-plugin-algo
```

### 使用包管理器

```bash
# poetry（推荐）
poetry add nonebot-plugin-algo

# pip
pip install nonebot-plugin-algo
```

然后在 NoneBot 项目的 `pyproject.toml` 中启用插件：

```toml
[tool.nonebot]
plugins = ["nonebot_plugin_algo"]
```

## 配置

### 环境变量配置

在 `.env` 文件中配置：

```env
# clist.by API 凭据
algo_clist_username=your_username
algo_clist_api_key=your_api_key

# 查询配置
algo_days=7                    # 查询近期天数，默认 7
algo_limit=20                  # 返回数量上限，默认 20
algo_remind_pre=30             # 提醒提前时间（分钟），默认 30
algo_order_by=start            # 排序字段，默认 start
```

### 配置项说明

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `algo_days` | int | 7 | 查询近期比赛的天数 |
| `algo_limit` | int | 20 | 返回结果数量上限 |
| `algo_remind_pre` | int | 30 | 订阅提醒提前时间（分钟） |
| `algo_clist_username` | str | "" | clist.by 用户名 |
| `algo_clist_api_key` | str | "" | clist.by API Key |
| `algo_order_by` | str | "start" | 查询结果排序字段 |

> **注意**：若未配置 clist.by 凭据，请前往 [clist.by](https://clist.by/) 申请 API Key。

## 使用说明

### 基础查询示例

```text
近期比赛          # 查询近期比赛
今日比赛          # 查询今日比赛
比赛 163 10       # 查询洛谷平台10天内的比赛
题目 123456       # 查询比赛ID为123456的题目
clt               # 获取clist.by官网链接
```

### 订阅功能示例

```text
订阅 123456       # 订阅比赛ID为123456的比赛
订阅              # 查看当前订阅列表
```

订阅成功后，系统将在比赛开始前 30 分钟（可配置）自动发送提醒消息。

## 开发与依赖

### 系统要求
- Python >= 3.9
- NoneBot2 >= 2.4.3

### 核心依赖
- `nonebot2[console]` >= 2.4.3
- `nonebot-plugin-alconna` >= 0.49.0
- `nonebot-plugin-apscheduler` >= 0.5.0
- `httpx` >= 0.24
- `pydantic` >= 2.4, < 3.0

### 开发依赖
- `black` >= 24.4.2
- `isort` >= 5.13.2
- `ruff` >= 0.4.6

## 技术特性

- **异步处理**：基于 asyncio 的异步 HTTP 请求
- **智能重试**：网络请求失败时自动重试机制
- **时区处理**：自动处理 UTC 时间转换本地时间
- **内存存储**：订阅信息内存存储，重启后清空
- **定时提醒**：基于 APScheduler 的精确定时提醒

## 项目结构

```
nonebot-plugin-algo/
├── nonebot_plugin_algo/
│   ├── __init__.py          # 插件主入口，命令处理
│   ├── config.py            # 配置管理
│   └── data_source.py       # 数据源和API处理
├── tests/                   # 测试文件
├── pyproject.toml           # 项目配置
└── README.md               # 项目说明
```

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可

MIT License
