# MiMo API 重构实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将 v2 的 `agent.py` 从本地 Ollama 替换为 MiMo 云端 API (`mimo-v2-flash`)，同时扩展白名单。

**Architecture:** 用 `openai` SDK 以 OpenAI 兼容模式调用 `https://api.xiaomimimo.com/v1`，保留缓存机制（`true_titles` / `false_titles` set），白名单从 2 个扩展到 13 个应用。

**Tech Stack:** Python 3.x, openai SDK, MiMo API (`mimo-v2-flash`), PyQt5

---

### Task 1: 新增 API 配置文件

**Files:**
- Create: `data/api_config.json`

- [ ] **Step 1: 创建配置文件**

```json
{
  "api_key": ""
}
```

写入 `data/api_config.json`。

- [ ] **Step 2: 创建 example 文件**

```json
{
  "api_key": "sk-your-api-key-here"
}
```

写入 `data/api_config.example.json`，方便其他开发者知道格式。

- [ ] **Step 3: 更新 .gitignore 忽略真实 API Key**

确保 `.gitignore` 包含：

```
api_config.json
```

保持 `api_config.example.json` 可提交，真实的 `api_config.json` 不可提交。

- [ ] **Step 4: 提交**

```bash
git add data/api_config.example.json .gitignore
git commit -m "feat: add api_config example and gitignore api key"
```

---

### Task 2: 重写 agent.py

**Files:**
- Rewrite: `v2_StudyExpSystemv_agent版/agent.py`

- [ ] **Step 1: 重写 agent.py — 用 MiMo API 替换 Ollama**

```python
import json
from pathlib import Path
from openai import OpenAI


class Agent:
    def __init__(self):
        api_key = self._load_api_key()
        self.client = OpenAI(
            base_url="https://api.xiaomimimo.com/v1",
            api_key=api_key
        )
        self.true_titles = set()
        self.false_titles = set()
        self.prompt_template = (
            '请判断以下窗口标题是否属于学习内容（编程/数学/科学/技术文档/论文/课程）：\n\n'
            '"{title}"\n\n'
            '只回答 True 或 False，不要附带任何解释。'
        )

    def _load_api_key(self):
        config_path = Path("./data/api_config.json")
        if not config_path.exists():
            raise FileNotFoundError(
                f"API 配置文件不存在: {config_path}\n"
                "请参考 data/api_config.example.json 创建 data/api_config.json 并填入 API Key"
            )
        with open(config_path) as f:
            config = json.load(f)
        api_key = config.get("api_key", "")
        if not api_key:
            raise ValueError(
                "api_key 为空，请在 data/api_config.json 中填入有效的 API Key"
            )
        return api_key

    def check_title(self, title: str) -> bool:
        normalized_title = title.strip().lower()

        if normalized_title in self.true_titles:
            return True
        if normalized_title in self.false_titles:
            return False

        try:
            response = self.client.chat.completions.create(
                model="mimo-v2-flash",
                messages=[{
                    "role": "user",
                    "content": self.prompt_template.format(title=title)
                }],
                timeout=5
            )
            result = response.choices[0].message.content.strip().lower() == "true"

            if result:
                self.true_titles.add(normalized_title)
            else:
                self.false_titles.add(normalized_title)

            return result
        except Exception as e:
            print(f"MiMo API 调用失败: {e}")
            return False


if __name__ == "__main__":
    agent = Agent()
    print(agent.check_title("VS Code - main.py"))
```

- [ ] **Step 2: 安装 openai SDK**

```bash
pip install openai
```

- [ ] **Step 3: 提交**

```bash
git add v2_StudyExpSystemv_agent版/agent.py
git commit -m "refactor: replace Ollama with MiMo API (mimo-v2-flash)"
```

---

### Task 3: 扩展判断模块白名单

**Files:**
- Modify: `v2_StudyExpSystemv_agent版/判断模块.py`

- [ ] **Step 1: 替换白名单**

将 `判断模块.py` 第 6-8 行的白名单：

```python
        self.whitelist = whitelist or {
            '哔哩哔哩', 'msedge'
        }
```

替换为：

```python
        self.whitelist = whitelist or {
            'code', 'pycharm64', 'idea', 'windowsterminal', 'python',
            'chrome', 'firefox', 'msedge',
            'wps', 'obsidian', 'notepad', 'explorer',
            '哔哩哔哩'
        }
```

- [ ] **Step 2: 提交**

```bash
git add v2_StudyExpSystemv_agent版/判断模块.py
git commit -m "feat: expand whitelist to 13 apps with LLM-based classification"
```

---

### 验证清单

- [ ] `data/api_config.json` 存在且包含有效的 API Key
- [ ] `python -c "from agent import Agent; a = Agent(); print(a.check_title('VS Code - main.py'))"` 能正常返回 True/False
- [ ] 同标题第二次调用命中缓存，不产生额外 API 调用
- [ ] `python main.py` 正常启动 GUI 界面
