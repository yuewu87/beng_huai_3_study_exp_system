import json
from pathlib import Path
from openai import OpenAI


DEFAULT_DIRECT = {'code', 'pycharm64', 'idea', 'windowsterminal', 'python', 'obsidian', 'notepad', 'explorer'}
DEFAULT_LLM = {'chrome', 'firefox', 'msedge', 'wps', '哔哩哔哩'}
DEFAULT_BLACKLIST = set()


class Agent:
    def __init__(self, use_llm=None):
        self._use_llm_override = use_llm
        self.use_llm = True
        self.client = None
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
            '- 回答 "llm"：浏览器、办公软件、视频平台等需要看具体内容才能判断的工具\n'
            '- 回答 "none"：游戏、娱乐、购物、社交软件等与学习无关的应用\n\n'
            '只回答 direct、llm 或 none，不要附带任何解释。'
        )

        self.direct_pass = set()
        self.llm_check = set()
        self.blacklist = set()
        self._load_app_config()

        if self._use_llm_override is not None:
            self.use_llm = self._use_llm_override

        if self.use_llm:
            self._init_client()

    def _init_client(self):
        try:
            api_key = self._load_api_key()
            self.client = OpenAI(
                base_url="https://api.xiaomimimo.com/v1",
                api_key=api_key
            )
        except Exception as e:
            print(f"LLM 初始化失败，降级为白名单模式: {e}")
            self.use_llm = False

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

    def _load_app_config(self):
        path = Path("./data/app_config.json")
        if path.exists():
            try:
                with open(path) as f:
                    data = json.load(f)
                    self.use_llm = data.get("use_llm", True)
                    self.direct_pass = set(data.get("direct_pass", []))
                    self.llm_check = set(data.get("llm_check", []))
                    self.blacklist = set(data.get("blacklist", []))
                    self._deduplicate_lists()
                    return
            except Exception:
                pass

        # 迁移旧 learned_apps.json
        old_path = Path("./data/learned_apps.json")
        if old_path.exists():
            try:
                with open(old_path) as f:
                    data = json.load(f)
                    self.direct_pass = DEFAULT_DIRECT | set(data.get("direct", []))
                    self.llm_check = DEFAULT_LLM | set(data.get("llm", []))
                    self.blacklist = DEFAULT_BLACKLIST.copy()
                    self._save_app_config()
                    old_path.unlink()
                    return
            except Exception:
                pass

        # 首次运行
        self.direct_pass = DEFAULT_DIRECT.copy()
        self.llm_check = DEFAULT_LLM.copy()
        self.blacklist = DEFAULT_BLACKLIST.copy()
        self._save_app_config()

    def _save_app_config(self):
        path = Path("./data/app_config.json")
        with open(path, "w") as f:
            json.dump({
                "use_llm": self.use_llm,
                "direct_pass": sorted(self.direct_pass),
                "llm_check": sorted(self.llm_check),
                "blacklist": sorted(self.blacklist)
            }, f, indent=2, ensure_ascii=False)

    def _deduplicate_lists(self):
        before = (self.direct_pass.copy(), self.llm_check.copy(), self.blacklist.copy())
        self.direct_pass -= self.blacklist
        self.llm_check -= self.blacklist
        self.llm_check -= self.direct_pass
        after = (self.direct_pass, self.llm_check, self.blacklist)
        if before != after:
            self._save_app_config()

    def check_title(self, title: str) -> bool:
        if not self.use_llm or self.client is None:
            return True

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
        if not self.use_llm or self.client is None:
            return "none"

        name = app_name.strip().lower()

        if name in self.blacklist:
            return "none"
        if name in self.direct_pass:
            return "direct"
        if name in self.llm_check:
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
                self.direct_pass.add(name)
            elif label == "llm":
                self.llm_check.add(name)
            else:
                self.blacklist.add(name)
                label = "none"

            self._save_app_config()
            return label
        except Exception as e:
            print(f"MiMo API 应用分类失败: {e}")
            return "none"
