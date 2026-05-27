# 崩坏3 学习经验系统 v1.0

游戏化学习激励系统 —— 追踪电脑活动自动发放经验值，搭配 LLM 智能判定和桌面悬浮窗，从 F 级女武神向 SSS 级进阶。

## 项目结构

```
Exp_system/
├── main.py
├── start_llm.bat          # LLM 模式一键启动
├── start_simple.bat       # 白名单模式一键启动
├── src/
│   ├── agent.py           # MiMo LLM Agent
│   ├── judger.py          # 判定引擎
│   ├── exp_system.py      # 经验值系统
│   ├── gui.py             # PyQt5 悬浮窗
│   └── monitor.py         # 前台窗口监测
├── requirements.txt
└── data/
    ├── api_config.json
    ├── api_config.example.json
    ├── app_config.json
    ├── exp_config.json
    └── user_data.json
```

## 运行模式

### LLM 模式 `--llm`

```
app_name
  ├── 黑名单 → False（零 API）
  ├── 白名单 → True（零 API）
  ├── 灰名单 → LLM 判定窗口标题
  └── 未知    → LLM 分类后自动加入对应名单
```

### 白名单模式 `--no-llm`

- 白名单 + 灰名单合并视为白名单
- 零 API 调用
- 不加 `--llm` / `--no-llm` 时默认读取 `app_config.json` 的 `use_llm` 字段

## 快速开始

```bash
pip install -r requirements.txt
```

### LLM 模式

双击 `start_llm.bat`，或：
```bash
python main.py --llm
```

需先配置 API Key：
```bash
cp data/api_config.example.json data/api_config.json
# 编辑填入 MiMo API Key
```

### 白名单模式

双击 `start_simple.bat`，或：
```bash
python main.py --no-llm
```

无需 API Key，纯白名单判定。

## 等级系统

- 1-80 级：`200*(n^1.7) + 50*n`
- 81-88 EX 级：指数增长
- 段位：F → E → D → C → B → A → S → SS → SSS → EX
- 夜间加成：22:00-6:00 ×1.5

## 经验值获取

| 行为 | 经验值 | 说明 |
|------|--------|------|
| 有效应用活动 | 10 XP | 窗口变化时触发 |
| 键盘输入 | 1 XP | 50ms 防连击 |

## 配置

| 文件 | 用途 |
|------|------|
| `data/api_config.json` | MiMo API Key |
| `data/app_config.json` | `use_llm` 开关 + 名单 |
| `data/exp_config.json` | 经验值参数 |
| `data/user_data.json` | 存档 |
