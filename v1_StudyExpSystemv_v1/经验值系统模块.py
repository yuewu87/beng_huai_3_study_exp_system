import json
import time
from datetime import datetime
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pynput import keyboard

class ExpSystem:
    def __init__(self):
        self.config_file = Path("./data/exp_config.json")
        self.user_file = Path("./data/user_data.json")
        self._load_config()
        self._load_user_data()
        self._precompute_thresholds()
        
        # 初始化键盘监听
        self._init_keyboard_listener()
        self.last_key_time = 0  # 防连击保护

        # 新增文件保存监听
        self._init_file_save_listener()

    def _load_config(self):
        """加载经验配置"""
        default_config = {
            "base_xp": {
                "app_active": 10,    # 有效应用检测奖励
                "key_press": 1,      # 每次按键奖励
                "file_save": 20      # 新增文件保存奖励
            },
            "night_multiplier": {    # 夜间奖励时段
                "start": 22,         # 开始时间（22点）
                "end": 6,            # 结束时间（次日6点） 
                "rate": 1.5          # 经验倍率
            },
            "level_formula": "200*(n**1.7) + 50*n"  # 等级计算公式
        }
        
        self.config_file.parent.mkdir(parents=True, exist_ok=True)

        if not self.config_file.exists():
            with open(self.config_file, 'w') as f:
                json.dump(default_config, f, indent=2)
            self.config = default_config
        else:
            with open(self.config_file) as f:
                self.config = json.load(f)
        # 确保 file_save 存在
        self.config["base_xp"].setdefault("file_save", 20)

    def _load_user_data(self):
        """加载用户数据"""
        default_user = {
            "total_xp": 0,               # 总经验值
            "current_level": 1,          # 当前等级
            "last_update": time.time()   # 最后更新时间
        }
        
        self.user_file.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(self.user_file) as f:
                self.user = json.load(f)
                # 数据校验
                self.user["total_xp"] = max(self.user.get("total_xp", 0), 0)
        except:
            self.user = default_user
            self._save_user_data()

    def _save_user_data(self):
        """保存用户数据"""
        with open(self.user_file, 'w') as f:
            json.dump(self.user, f, indent=2)

    def _precompute_thresholds(self):
        """预计算各等级经验阈值"""
        self.exp_thresholds = []
        total = 0
        # 常规等级 1-80
        for lv in range(1, 81):
            lv_exp = int(200*(lv**1.7) + 50*lv)
            total += lv_exp
            self.exp_thresholds.append(total)
        
        # EX等级 81-88
        ex_base = self.exp_thresholds[-1]  # 80级总经验
        for lv in range(81, 89):
            ex_exp = ex_base * (2**(lv-80))
            total += ex_exp
            self.exp_thresholds.append(total)

    def _get_multiplier(self):
        """获取当前时段倍率"""
        now = datetime.now().hour
        cfg = self.config["night_multiplier"]
        if cfg["start"] <= now or now < cfg["end"]:
            return cfg["rate"]
        return 1.0

    def add_xp(self, amount):
        """添加经验值核心方法"""
        multiplier = self._get_multiplier()     # 获取当前时段的经验倍率(如夜间加成)
        actual_xp = amount * multiplier         # 计算实际获得经验值 = 基础值 × 倍率

        # 添加调试信息
        # print(f"[XP+] 获得经验值 {amount} × {multiplier}倍 = {actual_xp} (总经验: {self.user['total_xp']} → {self.user['total_xp'] + actual_xp})")

        self.user["total_xp"] += actual_xp      # 更新总经验值
        self.user["last_update"] = time.time()  # 更新最后更新时间
        self._update_level()                    # 检查并更新等级
        self._save_user_data()                  # 保存数据

    def _update_level(self):
        """更新等级逻辑"""
        # 初始化时预计算阈值
        if not hasattr(self, 'exp_thresholds'):
            self._precompute_thresholds()
        
        current_xp = self.user["total_xp"]
        new_level = 1
        
        # 二分查找优化性能
        left, right = 0, len(self.exp_thresholds)-1
        while left <= right:
            mid = (left + right) // 2
            if current_xp >= self.exp_thresholds[mid]:
                new_level = mid + 2  # 等级=索引+1（因数组从0开始）
                left = mid + 1
            else:
                right = mid -1
        
        # 限制最大等级为88
        self.user["current_level"] = min(new_level, 88)

    def _init_keyboard_listener(self):
        """初始化键盘监听线程"""
        def on_press(key):
            if (time.time() - self.last_key_time) > 0.01:
                print("[键盘输入奖励] 检测到键盘输入")
                self.add_xp(self.config["base_xp"]["key_press"])
                self.last_key_time = time.time()
        
        listener = keyboard.Listener(on_press=on_press)
        listener.daemon = True
        listener.start()
    
    def _init_file_save_listener(self):
        """初始化文件保存监听"""
        self.observer = Observer()
        event_handler = FileSaveHandler(self, self.config["base_xp"]["file_save"])
        
        # 监听当前工作目录下的所有保存操作（可根据需要调整路径）
        self.observer.schedule(event_handler, '.', recursive=True)
        self.observer.start()
        

class FileSaveHandler(FileSystemEventHandler):
    def __init__(self, exp_system, file_save_xp):
        super().__init__()
        self.exp_system = exp_system
        self.file_save_xp = file_save_xp  # 存储文件保存奖励经验值
        self.last_save = 0  # 防重复保存检测
        
    def on_modified(self, event):
        # 仅处理文件修改事件
        if not event.is_directory:
            # 防连击检测（1秒内不重复触发）
            if time.time() - self.last_save > 1:
                # 仅对代码文件生效（可扩展其他类型）
                if event.src_path.endswith(('.py', '.java', '.cpp')):
                    self.exp_system.add_xp(self.file_save_xp)  # 使用配置的经验值
                    print(f"[文件保存奖励] 检测到 {Path(event.src_path).name} 的保存操作")
                    self.last_save = time.time()