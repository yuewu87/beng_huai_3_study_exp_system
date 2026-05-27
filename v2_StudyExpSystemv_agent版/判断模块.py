from agent import Agent


class ExeJudger:
    def __init__(self, exp_system):
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

        # 1. 白名单 → 直接放行
        if app_name in self.agent.direct_pass:
            if app_changed:
                print(f"应用: {app_name} → 直接放行")
                print("-" * 50)
            self._prev_app = app_name
            return True

        # 2. 灰名单 → LLM 判定标题
        if app_name in self.agent.llm_check:
            result = self.agent.check_title(window_title)
            if app_changed or title_changed:
                print(f"应用: {app_name}, 标题: {window_title} → {'有效' if result else '无效'}")
                print("-" * 50)
            self._prev_app = app_name
            self._prev_title = window_title
            return result

        # 3. 未知应用 → LLM 先分类应用类型
        label = self.agent.classify_app(app_name)
        self._prev_app = app_name
        if app_changed:
            if label == "direct":
                print(f"应用分类: {app_name} → 开发工具，已加入白名单")
            elif label == "llm":
                print(f"应用分类: {app_name} → 内容应用，已加入灰名单")
            else:
                print(f"应用分类: {app_name} → 非学习应用")
            print("-" * 50)

        if label == "direct":
            return True
        if label == "llm":
            result = self.agent.check_title(window_title)
            if app_changed:
                print(f"标题判定: {window_title} → {'有效' if result else '无效'}")
                print("-" * 50)
            self._prev_title = window_title
            return result
        return False

    def is_productive(self, app_info):
        is_valid = self._check_productive(app_info)
        if is_valid:
            self.exp_system.add_xp(
                self.exp_system.config["base_xp"]["app_active"]
            )
        return is_valid
