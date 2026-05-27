from agent import Agent


class ExeJudger:
    def __init__(self, exp_system, whitelist=None):
        # 直接放行：开发/笔记工具，无需 LLM 判定
        self.direct_pass = whitelist or {
            'code', 'pycharm64', 'idea', 'windowsterminal', 'python',
            'obsidian', 'notepad'
        }
        # 需 LLM 判定标题：浏览器/办公/文件管理器
        self.llm_check = {
            'chrome', 'firefox', 'msedge',
            'wps', 'explorer', '哔哩哔哩'
        }
        self.exp_system = exp_system
        self.agent = Agent()
        self._prev_app = None
        self._prev_title = None

    def _check_productive(self, app_info):
        if not app_info.get('app_name'):
            return False

        app_name = app_info['app_name'].lower().replace('.exe', '')
        window_title = app_info.get('window_title', '').lower()
        app_changed = app_name != self._prev_app
        title_changed = window_title != self._prev_title

        # 1. 内置白名单或已学习白名单 → 直接放行
        if app_name in self.direct_pass or app_name in self.agent.learned_direct:
            if app_changed:
                print(f"应用: {app_name} → 直接放行")
                print("-" * 50)
            self._prev_app = app_name
            return True

        # 2. 内置灰名单或已学习灰名单 → LLM 判定标题
        if app_name in self.llm_check or app_name in self.agent.learned_llm:
            if app_changed or title_changed:
                print(f"应用: {app_name}, 标题: {window_title} → 检测")
                print("-" * 50)
            self._prev_app = app_name
            self._prev_title = window_title
            return self.agent.check_title(window_title)

        # 3. 未知应用 → LLM 先分类应用类型
        label = self.agent.classify_app(app_name)
        if app_changed:
            print(f"应用分类: {app_name} → {label}")
            print("-" * 50)

        self._prev_app = app_name
        if label == "direct":
            return True
        if label == "llm":
            return self.agent.check_title(window_title)
        return False

    def is_productive(self, app_info):
        is_valid = self._check_productive(app_info)
        print("是否有效: ", is_valid)
        if is_valid:
            self.exp_system.add_xp(
                self.exp_system.config["base_xp"]["app_active"]
            )
        return is_valid
