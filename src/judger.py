from .agent import Agent


class ExeJudger:
    def __init__(self, exp_system, use_llm=None):
        self.exp_system = exp_system
        self.agent = Agent(use_llm=use_llm)
        self._prev_app = None
        self._prev_title = None

    def _check_title(self, app_name, window_title, app_changed, title_changed):
        if not self.agent.use_llm:
            return True
        result = self.agent.check_title(window_title)
        if app_changed or title_changed:
            print(f"应用: {app_name}, 标题: {window_title} → {'有效' if result else '无效'}")
            print("-" * 50)
        self._prev_app = app_name
        self._prev_title = window_title
        return result

    def _check_productive(self, app_info):
        if not app_info.get('app_name'):
            return False

        app_name = app_info['app_name'].lower().replace('.exe', '')
        window_title = app_info.get('window_title', '').lower()
        app_changed = app_name != self._prev_app
        title_changed = window_title != self._prev_title

        # 1. 黑名单 → 直接跳过
        if app_name in self.agent.blacklist:
            self._prev_app = app_name
            return False

        # 2. 白名单 → 直接放行
        if app_name in self.agent.direct_pass:
            if app_changed:
                print(f"应用: {app_name} → 直接放行")
                print("-" * 50)
            self._prev_app = app_name
            return True

        # 3. 灰名单 → LLM 判定（LLM 不可用时视为白名单）
        if app_name in self.agent.llm_check:
            if not self.agent.use_llm:
                if app_changed:
                    print(f"应用: {app_name} → 白名单放行")
                    print("-" * 50)
                self._prev_app = app_name
                return True
            return self._check_title(app_name, window_title, app_changed, title_changed)

        # 4. 未知应用
        if not self.agent.use_llm:
            self._prev_app = app_name
            return False

        label = self.agent.classify_app(app_name)
        if app_changed:
            mapping = {"direct": "开发工具，已加入白名单", "llm": "内容应用，已加入灰名单"}
            print(f"应用分类: {app_name} → {mapping.get(label, '非学习应用，已加入黑名单')}")
            print("-" * 50)

        if label == "direct":
            self._prev_app = app_name
            return True
        if label == "llm":
            return self._check_title(app_name, window_title, True, True)
        self._prev_app = app_name
        return False

    def is_productive(self, app_info):
        is_valid = self._check_productive(app_info)
        if is_valid:
            self.exp_system.add_xp(
                self.exp_system.config["base_xp"]["app_active"]
            )
        return is_valid
