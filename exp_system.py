import json
import time
from datetime import datetime
from pathlib import Path


class ExpSystem:
    def __init__(self):
        self.config_file = Path("./data/exp_config.json")
        self.user_file = Path("./data/user_data.json")
        self._load_config()
        self._load_user_data()
        self._precompute_thresholds()

        self._init_keyboard_listener()
        self.last_key_time = 0

    def _load_config(self):
        default_config = {
            "base_xp": {
                "app_active": 10,
                "key_press": 1
            },
            "night_multiplier": {
                "start": 22,
                "end": 6,
                "rate": 1.5
            },
            "level_formula": "200*(n**1.7) + 50*n"
        }

        self.config_file.parent.mkdir(parents=True, exist_ok=True)

        if not self.config_file.exists():
            with open(self.config_file, 'w') as f:
                json.dump(default_config, f, indent=2)
            self.config = default_config
        else:
            with open(self.config_file) as f:
                self.config = json.load(f)

    def _load_user_data(self):
        default_user = {
            "total_xp": 0,
            "current_level": 1,
            "last_update": time.time()
        }

        self.user_file.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(self.user_file) as f:
                self.user = json.load(f)
                self.user["total_xp"] = max(self.user.get("total_xp", 0), 0)
        except:
            self.user = default_user
            self._save_user_data()

    def _save_user_data(self):
        with open(self.user_file, 'w') as f:
            json.dump(self.user, f, indent=2)

    def _precompute_thresholds(self):
        self.exp_thresholds = []
        total = 0
        for lv in range(1, 81):
            lv_exp = int(200*(lv**1.7) + 50*lv)
            total += lv_exp
            self.exp_thresholds.append(total)

        ex_base = self.exp_thresholds[-1]
        for lv in range(81, 89):
            ex_exp = ex_base * (2**(lv-80))
            total += ex_exp
            self.exp_thresholds.append(total)

    def _get_multiplier(self):
        now = datetime.now().hour
        cfg = self.config["night_multiplier"]
        if cfg["start"] <= now or now < cfg["end"]:
            return cfg["rate"]
        return 1.0

    def add_xp(self, amount):
        multiplier = self._get_multiplier()
        actual_xp = amount * multiplier

        self.user["total_xp"] += actual_xp
        self.user["last_update"] = time.time()
        self._update_level()
        self._save_user_data()

    def _update_level(self):
        if not hasattr(self, 'exp_thresholds'):
            self._precompute_thresholds()

        current_xp = self.user["total_xp"]
        new_level = 1

        left, right = 0, len(self.exp_thresholds)-1
        while left <= right:
            mid = (left + right) // 2
            if current_xp >= self.exp_thresholds[mid]:
                new_level = mid + 2
                left = mid + 1
            else:
                right = mid - 1

        self.user["current_level"] = min(new_level, 88)

    def _init_keyboard_listener(self):
        from pynput import keyboard
        def on_press(key):
            if (time.time() - self.last_key_time) > 0.05:
                self.add_xp(self.config["base_xp"]["key_press"])
                self.last_key_time = time.time()

        listener = keyboard.Listener(on_press=on_press)
        listener.daemon = True
        listener.start()
