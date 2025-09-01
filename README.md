<div align="center">
  <a href="https://v2.nonebot.dev/store"><img src="https://github.com/A-kirami/nonebot-plugin-template/blob/resources/nbp_logo.png" width="180" height="180" alt="NoneBotPluginLogo"></a>
  <br>
  <p><img src="https://github.com/A-kirami/nonebot-plugin-template/blob/resources/NoneBotPlugin.svg" width="240" alt="NoneBotPluginText"></p>
</div>

<div align="center">

<h1 style="font-size: 4em; margin: 20px 0;">算法比赛助手</h1>
<!-- _✨ 算法比赛与题目信息查询助手 ✨_ -->

<a href="./LICENSE">
    <img src="https://img.shields.io/github/license/Tabris-ZX/nonebot-plugin-algo.svg" alt="license">
</a>
<a href="https://pypi.python.org/pypi/nonebot-plugin-algo">
    <img src="https://img.shields.io/pypi/v/nonebot-plugin-algo.svg" alt="pypi">
</a>
<img src="https://img.shields.io/badge/python-3.10+-blue.svg" alt="python">

</div>

## 📖 简介

基于 NoneBot2 与 clist.by API 的算法比赛助手插件，支持查询今日/近期比赛、按条件检索比赛/题目列表，以及订阅比赛提醒等功能。

## ✨ 功能特性

### 🔍 基础查询功能
- **查询近期比赛**：`近期比赛`（别名：`近期`）
- **查询今日比赛**：`今日比赛`（别名：`今日`）
- **条件检索比赛**：`比赛 [平台id] [天数]`
  - `平台id` 为站点 ID（来自 clist.by）
  - `天数` 为查询天数，默认来自配置 `algo_days`
- **查询比赛题目**：`题目 [比赛id]`
- **clist 官网链接**：`clt`（别名：`/官网`）

### 🔔 订阅提醒功能 ⭐
- **订阅比赛提醒**：`订阅 -i [比赛id]` 或 `订阅 -e [比赛名称]`
  - 支持通过比赛ID或比赛名称订阅
  - 订阅后将在比赛开始前自动提醒
  - 提醒时间可通过配置项 `algo_remind_pre` 设置
  - **支持私聊和群聊**：可在私聊中订阅个人提醒，或在群聊中订阅群组提醒

## 📋 TODO

### 🚀 todo
- [x] **取消订阅功能**：`取消订阅 [比赛id]` - 允许用户取消特定比赛的订阅
- [x] **订阅持久化存储**：将订阅信息保存到数据库或文件，重启后不丢失
- [x] **便捷检索**: 支持通过中文检索指定比赛
- [ ] **批量订阅管理**：支持查看和管理所有订阅的比赛
- [ ] **自定义提醒时间**：允许用户为不同比赛设置不同的提醒时间

### 📊 功能增强
- [ ] **比赛统计功能**：提供比赛参与度、难度等统计信息
- [ ] **个性化推荐**：基于用户历史订阅推荐相关比赛
- [ ] **多语言支持**：支持英文等多语言界面
- [ ] **Web管理界面**：提供Web界面管理订阅和配置

## 🚀 安装

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

## ⚙️ 配置

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
algo_save_path=./data/algo_subscribes.json  # 订阅数据保存路径
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
| `algo_save_path` | str | "./data/algo_subscribes.json" | 订阅数据保存路径 |

> **注意**：若未配置 clist.by 凭据，请前往 [clist.by](https://clist.by/) 申请 API Key。

## 📖 使用说明

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
订阅 -i 123456     # 通过比赛ID订阅比赛
订阅 -e "Codeforces Round"  # 通过比赛名称订阅比赛
订阅列表           # 查看当前订阅列表
取消订阅 123456    # 取消订阅比赛ID为123456的比赛
清空订阅           # 清空所有订阅
```

### 订阅功能特性

- **智能匹配**：支持通过比赛ID或比赛名称模糊匹配订阅
- **自动提醒**：订阅成功后，系统将在比赛开始前自动发送提醒消息
- **链接保存**：订阅时会自动保存比赛链接，提醒时一并显示
- **持久化存储**：订阅信息保存到本地文件，重启后不丢失
- **多场景支持**：
  - **群聊订阅**：提醒消息将发送到群聊
  - **私聊订阅**：提醒消息将发送到个人私聊

### 提醒消息格式

```
🔔比赛提醒

🏆比赛名称: [比赛名称]
⏰开始时间: [本地时间]
🔗比赛链接: [比赛链接]
```

## 🏗️ 项目结构

```
nonebot-plugin-algo/
├── nonebot_plugin_algo/
│   ├── __init__.py          # 插件主入口，命令处理
│   ├── config.py            # 配置管理
│   ├── query.py             # 查询功能实现
│   ├── subscribe.py         # 订阅功能实现
│   └── util.py              # 工具函数和API处理
├── tests/                   # 测试文件
├── pyproject.toml           # 项目配置
└── README.md               # 项目说明
```

## 🔧 开发与依赖

### 系统要求
- Python >= 3.10
- NoneBot2 >= 2.4.3

### 核心依赖
- `nonebot2[console]` >= 2.4.3
- `nonebot-plugin-alconna` >= 0.49.0
- `nonebot-plugin-apscheduler` >= 0.5.0
- `httpx` >= 0.24
- `pydantic` >= 2.4, < 3.0
- `tzlocal` - 时区处理

### 开发依赖
- `black` >= 24.4.2
- `isort` >= 5.13.2
- `ruff` >= 0.4.6

## 🛠️ 技术特性

- **异步处理**：基于 asyncio 的异步 HTTP 请求
- **智能重试**：网络请求失败时自动重试机制（最多3次）
- **时区处理**：自动处理 UTC 时间转换本地时间
- **持久化存储**：订阅信息保存到 JSON 文件，重启后自动恢复
- **定时提醒**：基于 APScheduler 的精确定时提醒
- **参数优化**：所有多参数函数采用垂直格式，提高代码可读性

## 📝 更新日志

### v0.1.3
- ✅ 添加订阅时保存比赛链接功能
- ✅ 优化函数参数格式，提高代码可读性
- ✅ 完善订阅列表显示，包含比赛链接
- ✅ 改进错误处理和日志记录

### v0.1.2
- ✅ 支持私聊和群聊订阅
- ✅ 添加订阅持久化存储
- ✅ 实现定时提醒功能

### v0.1.1
- ✅ 基础查询功能
- ✅ 支持多种比赛平台

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

### 开发指南

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📄 许可

本项目采用 MIT License - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- [NoneBot2](https://github.com/nonebot/nonebot2) - 优秀的机器人框架
- [clist.by](https://clist.by/) - 提供算法比赛数据API
- [Alconna](https://github.com/ArcletProject/Alconna) - 强大的命令解析器

---

<div align="center">

**如果这个项目对你有帮助，请给它一个 ⭐️**

</div>
