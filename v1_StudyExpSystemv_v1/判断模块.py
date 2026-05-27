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
        
    def _check_productive(self, app_info):
        try:
            app_name = app_info['app_name'].lower().replace('.exe', '')
            window_title = app_info.get('window_title', '').lower()
            print("-" * 100)
            print(f"应用名称: {app_name}, 窗口标题: {window_title}")
            if app_name in self.whitelist:
                is_valid = True
                return is_valid
            else:
                return False
        except Exception as e:
            print(f"Error checking productivity: {e}")
            return False

    def is_productive(self, app_info):
        """修改后添加经验值逻辑"""
        is_valid = self._check_productive(app_info)
        print("是否有效: ", is_valid)
        print("-" * 100)
        if is_valid:
            self.exp_system.add_xp(
                self.exp_system.config["base_xp"]["app_active"]
            )
        return is_valid