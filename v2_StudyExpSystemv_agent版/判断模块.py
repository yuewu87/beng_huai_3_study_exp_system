from agent import Agent

class ExeJudger:
    def __init__(self, exp_system, whitelist=None):
        # 累时长不算, 只有看学习视频时才会计时长, 待改版
        self.whitelist = whitelist or {
            'code', 'pycharm64', 'idea', 'windowsterminal', 'python',
            'chrome', 'firefox', 'msedge',
            'wps', 'obsidian', 'notepad', 'explorer',
            '哔哩哔哩'
        }
        self.exp_system = exp_system
        self.agent = Agent()
        
    def _check_productive(self, app_info):
        if app_info.get('app_name'):
            print("检测到应用名称:", app_info['app_name'])
            # 处理带.exe后缀的应用名称（如chrome.exe -> chrome）
            app_name = app_info['app_name'].lower().replace('.exe', '')
            if app_name not in self.whitelist:
                return False
            window_title = app_info.get('window_title', '').lower()
            print(f"应用名称: {app_name}, 窗口标题: {window_title}")
            print("-" * 50)
            is_valid = self.agent.check_title(window_title)
            return is_valid
        return False

    def is_productive(self, app_info):
        """修改后添加经验值逻辑"""
        is_valid = self._check_productive(app_info)
        print("是否有效: ", is_valid)
        if is_valid:
            self.exp_system.add_xp(
                self.exp_system.config["base_xp"]["app_active"]
            )
        return is_valid