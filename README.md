# 崩坏3 学习经验系统 v1.0

游戏化学习激励系统 —— 追踪电脑活动自动发放经验值，搭配 LLM 智能判定和桌面悬浮窗，从 F 级女武神向 SSS 级进阶。

## 架构

```
main.py
  ├── 监测系统模块.py   →  0.5s 检测前台窗口，变化时触发回调
  ├── 判断模块.py       →  三级判定链：黑名单 → 白名单 → 灰名单 → LLM 分类
  │   └── agent.py      →  MiMo API (mimo-v2-flash)，含缓存 + 自动学习
  ├── 经验值系统模块.py   →  等级/段位计算 + 夜间倍率 + 键盘监听
  └── GUI系统模块.py     →  PyQt5 无边框悬浮窗
```

## 判定逻辑

```
app_name
  ├── 黑名单 (blacklist)       → False，零 API
  ├── 白名单 (direct_pass)     → True，零 API
  ├── 灰名单 (llm_check)       → LLM 判定窗口标题
  └── 未知应用                  → LLM 分类 + 自动加入对应名单
```

- 名单持久化在 `data/app_config.json`，手动编辑即时生效
- 黑名单优先级最高，重复项启动时自动去重
- 控制台仅在切换应用或标题变化时输出，不刷屏
- 窗口切换触发判定，静止时零 API 调用

## 等级系统

- 1-80 级：公式 `200*(n^1.7) + 50*n`
- 81-88 EX 级：指数增长
- 段位：F → E → D → C → B → A → S → SS → SSS → EX
- 夜间加成：22:00-6:00 经验值 ×1.5

## 经验值获取

| 行为 | 经验值 | 说明 |
|------|--------|------|
| 有效应用活动 | 10 XP/次 | 窗口变化时触发 |
| 键盘输入 | 1 XP/次 | 50ms 防连击 |
| 文件保存 | 20 XP/次 | .py / .java / .cpp |

## 快速开始

### 1. 安装依赖

```bash
pip install pyqt5 psutil pywin32 pynput watchdog openai
```

### 2. 配置 API Key

```bash
cp data/api_config.example.json data/api_config.json
# 编辑 data/api_config.json，填入 MiMo API Key
```

在 [platform.xiaomimimo.com](https://platform.xiaomimimo.com) 注册获取。

### 3. 运行

```bash
cd v2_StudyExpSystemv_agent版
python main.py
```

## 配置文件

| 文件 | 用途 |
|------|------|
| `data/api_config.json` | MiMo API Key（不入库） |
| `data/app_config.json` | 黑白灰名单（自动生成+可手动编辑） |
| `data/exp_config.json` | 经验值参数 |
| `data/user_data.json` | 用户存档 |

## 目录

| 目录 | 说明 |
|------|------|
| `v2_StudyExpSystemv_agent版/` | 当前版本（LLM 智能判定） |
| `v1_StudyExpSystemv_v1/` | 旧版（纯白名单） |
