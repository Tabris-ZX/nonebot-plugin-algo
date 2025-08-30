<div align="center">

## nonebot-plugin-algo

_✨ 算法比赛与题目信息查询助手 ✨_

<a href="./LICENSE">
    <img src="https://img.shields.io/github/license/Tabris_ZX/nonebot-plugin-algo.svg" alt="license">
  </a>
  <a href="https://pypi.python.org/pypi/nonebot-plugin-algo">
    <img src="https://img.shields.io/pypi/v/nonebot-plugin-algo.svg" alt="pypi">
  </a>
  <img src="https://img.shields.io/badge/python-3.9+-blue.svg" alt="python">

</div>

## 简介

基于 NoneBot2 与 clist.by API 的算法比赛助手插件，支持查询今日/近期比赛、按条件检索比赛/题目列表等功能。

## 功能

- 查询近期比赛：`近期比赛`（别名：`近期`）
- 查询今日比赛：`今日比赛`（别名：`今日`）
- 条件检索比赛：`比赛 <resource_id> [days]`
  - `resource_id` 为站点 ID（来自 clist.by）
  - `days` 为查询天数，默认来自配置 `days`
- 查询比赛题目：`题目 <contest_ids>`
- clist 官网链接：`clt`（别名：`官网`）

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

插件支持通过环境变量或 NoneBot 配置覆盖参数：

- 环境变量
  - `CLIST_USERNAME`: clist.by 用户名
  - `CLIST_API_KEY`: clist.by API Key

- NoneBot 配置（.env / 配置文件）
  - `algo_config.clist_username`
  - `algo_config.clist_api_key`
  - `algo_config.days`（默认 7）：查询近期天数
  - `algo_config.limit`（默认 20）：返回数量上限
  - `algo_config.order_by`（默认 `start`）：排序字段

若未配置凭据，请前往 clist.by 申请 API。

## 使用说明

示例：

```text
近期比赛
今日比赛
比赛 2 10
题目 123456
clt
```

时间显示将按本地时区格式化。

## 开发与依赖

- Python >= 3.9
- NoneBot2 >= 2.3.1
- nonebot-plugin-alconna >= 0.49.0
- httpx >= 0.24
- pydantic >= 2.4

## 许可

MIT License
