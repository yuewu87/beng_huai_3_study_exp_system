# 崩坏3 学习经验系统

游戏化学习激励系统 —— 通过追踪电脑活动（应用使用、键盘输入、文件保存）自动发放经验值，并提供等级/段位系统和桌面悬浮窗 GUI。

## 版本

| 版本 | 路径 | 判定方式 |
|------|------|----------|
| v1 | `v1_StudyExpSystemv_v1/` | 白名单匹配 |
| v2 | `v2_StudyExpSystemv_agent版/` | LLM Agent 智能判定 (MiMo API) |

## 核心机制

- **活动监测** — 检测当前活动窗口，识别正在使用的应用
- **智能判定** — v1 使用白名单，v2 使用 LLM 判断窗口内容是否为学习相关
- **经验值系统** — 1-80 普通等级 + 81-88 EX 等级，夜间 (22:00-6:00) 1.5 倍加成
- **桌面悬浮窗** — PyQt5 无边框窗口，实时显示等级/段位/进度条

## 经验值获取

| 行为 | 经验值 |
|------|--------|
| 活跃于有效应用 | 10 XP/次 |
| 键盘输入 | 1 XP/次 |
| 文件保存 (.py/.java/.cpp) | 20 XP/次 |

## 运行

```bash
pip install pyqt5 psutil pywin32 pynput watchdog openai
cd v2_StudyExpSystemv_agent版
python main.py
```

## 配置

- `data/exp_config.json` — 经验值参数
- `data/user_data.json` — 用户存档
- API Key 存放于配置文件
