# MiMo API 重构设计

**日期:** 2026-05-27
**范围:** v2_StudyExpSystemv_agent版/

## 目标

将 v2 `agent.py` 中的本地 Ollama (qwen2.5:7b) 替换为 MiMo 云端 API (`mimo-v2-flash`)，实现更快的窗口标题分类。

## 改动内容

### 1. agent.py — 重写

用 OpenAI 兼容的 MiMo API 替换 Ollama SDK。

- **SDK:** `openai.OpenAI`，`base_url="https://api.xiaomimimo.com/v1"`
- **模型:** `mimo-v2-flash`
- **API Key 来源:** `data/api_config.json`（格式：`{"api_key": "sk-xxx"}`）
- **超时:** 5 秒
- **缓存:** 保留现有 `true_titles` / `false_titles` 集合缓存
- **Prompt:** 与现有一致 — 判断窗口标题是否属于学习内容（返回 True/False）
- **错误处理:** 失败时返回 `False`，打印错误日志

### 2. 判断模块.py — 扩展白名单

从 2 个应用扩展到 v1 级别的白名单：

```
code, pycharm64, idea, windowsterminal, python,
chrome, firefox, msedge, wps, obsidian, notepad,
explorer, 哔哩哔哩
```

仅白名单内的应用会送 Agent 进行标题分类。

### 3. data/api_config.json — 新增配置文件

```json
{
  "api_key": "<用户自行填写>"
}
```

### 不改动的部分

- 监测系统模块.py
- 经验值系统模块.py
- GUI系统模块.py
- main.py
- v1 目录

## 架构

```
main.py
  ├── 监测系统模块.py   →  每 1 秒获取当前活动窗口
  ├── 判断模块.py       →  白名单检查 → Agent.check_title()
  │   └── agent.py      →  缓存查找 → MiMo API 调用 (mimo-v2-flash)
  ├── 经验值系统模块.py   →  带夜间倍率的 add_xp()
  └── GUI系统模块.py     →  PyQt5 悬浮窗
```
