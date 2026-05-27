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

    def _check_productive(self, app_info):
        if not app_info.get('app_name'):
            return False

        print("检测到应用名称:", app_info['app_name'])
        app_name = app_info['app_name'].lower().replace('.exe', '')

        # 1. 内置白名单或已学习白名单 → 直接放行
        if app_name in self.direct_pass or app_name in self.agent.learned_direct:
            print(f"应用名称: {app_name} → 直接放行")
            print("-" * 50)
            return True

        # 2. 内置灰名单或已学习灰名单 → LLM 判定标题
        if app_name in self.llm_check or app_name in self.agent.learned_llm:
            window_title = app_info.get('window_title', '').lower()
            print(f"应用名称: {app_name}, 窗口标题: {window_title}")
            print("-" * 50)
            return self.agent.check_title(window_title)

        # 3. 未知应用 → LLM 先分类应用类型
        label = self.agent.classify_app(app_name)
        print(f"应用分类结果: {app_name} → {label}")
        print("-" * 50)

        if label == "direct":
            return True
        if label == "llm":
            window_title = app_info.get('window_title', '').lower()
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
