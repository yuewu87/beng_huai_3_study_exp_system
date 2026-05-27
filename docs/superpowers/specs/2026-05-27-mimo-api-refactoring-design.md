# Mimo API Refactoring Design

**Date:** 2026-05-27
**Scope:** v2_StudyExpSystemv_agent版/

## Goal

Replace local Ollama (qwen2.5:7b) in v2's `agent.py` with MiMo cloud API (`mimo-v2-flash`) for faster window title classification.

## Changes

### 1. agent.py — Rewrite

Replace Ollama SDK with OpenAI-compatible MiMo API.

- **SDK:** `openai.OpenAI` with `base_url="https://api.xiaomimimo.com/v1"`
- **Model:** `mimo-v2-flash`
- **API Key source:** `data/api_config.json` (`{"api_key": "sk-xxx"}`)
- **Timeout:** 5s
- **Cache:** Keep existing `true_titles` / `false_titles` set-based cache
- **Prompt:** Same as current — classify window title as learning content (True/False)
- **Error handling:** Return `False` on failure, log the error

### 2. 判断模块.py — Expand Whitelist

Expand from 2 apps to v1-level whitelist:

```
code, pycharm64, idea, windowsterminal, python,
chrome, firefox, msedge, wps, obsidian, notepad,
explorer, 哔哩哔哩
```

Only apps in whitelist get sent to Agent for title classification.

### 3. data/api_config.json — New Config File

```json
{
  "api_key": "<user fills in>"
}
```

### Not Changed

- 监测系统模块.py
- 经验值系统模块.py
- GUI系统模块.py
- main.py
- v1 directory

## Architecture

```
main.py
  ├── 监测系统模块.py   →  get_active_window() every 1s
  ├── 判断模块.py       →  whitelist check → Agent.check_title()
  │   └── agent.py      →  cache lookup → MiMo API call (mimo-v2-flash)
  ├── 经验值系统模块.py   →  add_xp() with night multiplier
  └── GUI系统模块.py     →  PyQt5 overlay
```
