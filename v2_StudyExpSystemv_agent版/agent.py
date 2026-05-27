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

        self.title_prompt = (
            '请判断以下窗口标题是否属于学习内容（编程/数学/科学/技术文档/论文/课程）：\n\n'
            '"{title}"\n\n'
            '只回答 True 或 False，不要附带任何解释。'
        )

        self.app_prompt = (
            '请判断以下应用程序是否属于编程开发或技术学习类工具：\n\n'
            '应用名称: "{app_name}"\n\n'
            '分类规则：\n'
            '- 回答 "direct"：IDE、编辑器、终端、版本管理、调试器、设计工具、数据库工具等直接用于编程开发的工具\n'
            '- 回答 "llm"：浏览器、办公软件、视频平台、文档阅读器、文件管理器等需要看具体内容才能判断的工具\n'
            '- 回答 "none"：游戏、娱乐、购物等与学习无关的应用\n\n'
            '只回答 direct、llm 或 none，不要附带任何解释。'
        )

        self.learned_direct = set()
        self.learned_llm = set()
        self._load_learned_apps()

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

    def _load_learned_apps(self):
        path = Path("./data/learned_apps.json")
        if path.exists():
            try:
                with open(path) as f:
                    data = json.load(f)
                    self.learned_direct = set(data.get("direct", []))
                    self.learned_llm = set(data.get("llm", []))
            except Exception:
                pass

    def _save_learned_apps(self):
        path = Path("./data/learned_apps.json")
        with open(path, "w") as f:
            json.dump({
                "direct": sorted(self.learned_direct),
                "llm": sorted(self.learned_llm)
            }, f, indent=2, ensure_ascii=False)

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
                    "content": self.title_prompt.format(title=title)
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

    def classify_app(self, app_name: str) -> str:
        """返回 'direct'、'llm' 或 'none'"""
        name = app_name.strip().lower()

        if name in self.learned_direct:
            return "direct"
        if name in self.learned_llm:
            return "llm"

        try:
            response = self.client.chat.completions.create(
                model="mimo-v2-flash",
                messages=[{
                    "role": "user",
                    "content": self.app_prompt.format(app_name=app_name)
                }],
                timeout=5
            )
            label = response.choices[0].message.content.strip().lower()

            if label == "direct":
                self.learned_direct.add(name)
            elif label == "llm":
                self.learned_llm.add(name)
            else:
                label = "none"

            self._save_learned_apps()
            return label
        except Exception as e:
            print(f"MiMo API 应用分类失败: {e}")
            return "none"


if __name__ == "__main__":
    agent = Agent()
    print(agent.check_title("VS Code - main.py"))
