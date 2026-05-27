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
