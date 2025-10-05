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

# 🏆 算法比赛助手

_✨ 基于 NoneBot2 的算法比赛查询与订阅助手，支持洛谷用户信息查询 ✨_

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

## 📖 简介

基于 **NoneBot2** 与 **clist.by API** 开发的智能算法比赛助手插件，同时支持洛谷用户信息查询与绑定功能。

> ⚠️ **使用前提**：需要申请 [clist.by API](https://clist.by/api/v4/doc/) 凭据才能正常使用比赛查询功能

🎯 **核心功能**：

- 🔍 **智能查询**：今日/近期比赛、平台筛选、题目检索
- 🔔 **订阅提醒**：个性化比赛提醒，支持群聊/私聊
- 💾 **持久化存储**：订阅数据本地保存，重启不丢失
- 🌐 **多平台支持**：涵盖 Codeforces、AtCoder、洛谷等主流平台
- 🏆 **洛谷服务**：用户信息查询、绑定管理、精美卡片展示

## ✨ 功能特性

### 🔍 比赛查询功能

| 命令                     | 功能              | 示例            |
| ------------------------ | ----------------- | --------------- |
| `近期比赛` / `近期`  | 查询近期比赛      | `近期比赛`    |
| `今日比赛` / `今日`  | 查询今日比赛      | `今日比赛`    |
| `比赛 [平台id] [天数]` | 条件检索比赛      | `比赛 163 10` |
| `题目 [比赛id]`        | 查询比赛题目      | `题目 123456` |

> 💡 **平台ID说明**：163-洛谷，1-Codeforces，2-AtCoder 等，详见 [clist.by](https://clist.by/resources/)

### 🏆 洛谷服务功能

| 命令                        | 功能             | 示例                          |
| --------------------------- | ---------------- | ----------------------------- |
| `绑定洛谷 [用户名/id]`     | 绑定洛谷用户     | `绑定洛谷 123456`            |
| `我的洛谷`                  | 查询自己洛谷信息 | `我的洛谷`                   |
| `洛谷信息 [用户名/id]`     | 查询指定用户信息 | `洛谷信息 123456`           |

### 🔔 订阅提醒功能 ⭐

| 命令                        | 功能             | 示例                          |
| --------------------------- | ---------------- | ----------------------------- |
| `订阅 -i [比赛id]`         | 通过ID订阅比赛   | `订阅 -i 123456`             |
| `订阅 -e [比赛名称]`       | 通过名称订阅比赛 | `订阅 -e "Codeforces"` |
| `取消订阅 [比赛id]`       | 取消指定订阅     | `取消订阅 123456`           |
| `订阅列表` / `我的订阅` | 查看订阅列表     | `订阅列表`                  |
| `清空订阅`                | 清空所有订阅     | `清空订阅`                  |


## 🚀 快速开始

> 🚨 **开始前必读**：本插件依赖 clist.by API，请先完成 API 凭据申请，否则无法正常使用！

### 📦 安装插件

<details>
<summary>🎯 方式一：使用 nb-cli（推荐）</summary>

```bash
nb plugin install nonebot-plugin-algo
```

</details>

<details>
<summary>📚 方式二：使用包管理器</summary>

```bash
# 使用 poetry（推荐）
poetry add nonebot-plugin-algo

# 使用 pip
pip install nonebot-plugin-algo
```

然后在 NoneBot 项目的 `pyproject.toml` 中启用插件：

```toml
[tool.nonebot]
plugins = ["nonebot_plugin_algo"]
```

</details>

### ⚙️ 配置设置

> ⚠️ **重要提示**：本插件需要 clist.by API 凭据才能正常工作，请务必先申请！

<details>
<summary>🔧 必需配置</summary>

**第一步：申请 API 凭据**
1. 访问 [clist.by](https://clist.by/api/v4/doc/) 注册账号
2. 在个人设置中生成 API Key
3. 将凭据添加到 `.env` 文件中

**第二步：配置文件**
在 `.env` 文件中添加配置：

```env
# clist.by API 凭据（必需）
clist_username=your_username    # 你的 clist.by 用户名
clist_api_key=your_api_key      # 你的 clist.by API Key

# 查询配置（可选）
algo_days=7                    # 查询近期天数，默认 7
algo_limit=20                  # 返回数量上限，默认 20
algo_remind_pre=30             # 提醒提前时间（分钟），默认 30
algo_order_by=start            # 排序字段，默认 start
```
> ⚠️ **重要**：没有 API 凭据将无法使用任何功能！请务必前往 [clist.by API 文档](https://clist.by/api/v4/doc/) 申请。
</details>

## 📖 使用示例

### 🔍 比赛查询功能演示

```bash
# 基础查询
近期比赛          # 查询近期比赛
今日比赛          # 查询今日比赛
比赛 163 10       # 查询洛谷平台10天内的比赛
题目 123456       # 查询比赛ID为123456的题目
```

### 🏆 洛谷服务功能演示

```bash
# 洛谷用户操作
绑定洛谷 123456              # 绑定洛谷用户ID
绑定洛谷 "用户名"            # 绑定洛谷用户名
我的洛谷                    # 查询自己的洛谷信息
洛谷信息 123456             # 查询指定用户信息
洛谷信息 "用户名"            # 查询指定用户名信息
```

### 🔔 订阅功能演示

```bash
# 订阅操作
订阅 -i 123456                   # 通过比赛ID订阅
订阅 -e Codeforces               # 通过名称订阅
订阅列表                         # 查看订阅列表
取消订阅 123456                  # 取消指定订阅
清空订阅                         # 清空所有订阅
```
## 🎯 功能路线图

### todo list

- [X] **比赛查询系统** - 支持今日/近期比赛查询
- [X] **条件检索** - 按平台、时间筛选比赛
- [X] **题目查询** - 根据比赛ID查询题目信息
- [X] **订阅提醒系统** - 智能比赛订阅与定时提醒
- [X] **洛谷用户绑定** - 支持用户名和ID绑定
- [X] **洛谷信息查询** - 用户详细信息查询

### 🚧 计划中功能

- [ ] **批量订阅管理** - 一键管理多个订阅
- [ ] **自定义提醒时间** - 个性化提醒时间设置
- [ ] **多语言支持** - 国际化界面
- [ ] **Web管理面板** - 可视化订阅管理
- [ ] **更多OJ平台** - 支持更多在线判题平台

## 📄 开源协议
本项目基于 [MIT License](LICENSE) 开源协议。

<div align="center">

### 🌟 如果这个项目对你有帮助，请给个 Star！
**有任何问题欢迎来提issue!**
#### 让我们一起让算法竞赛变得更简单！

</div>
