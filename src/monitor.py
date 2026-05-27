"""前台窗口监测 — 检测活动窗口变化并回调通知"""
import win32gui
import win32process
import psutil
import time
import threading


class ExeChecker:
    def __init__(self):
        self.current_app = None
        self.current_title = None
        self._is_running = False
        self._monitor_thread = None
        self._callback = None

    @staticmethod
    def get_active_window():
        hwnd = win32gui.GetForegroundWindow()
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        try:
            process = psutil.Process(pid)
            exe_name = process.name().lower()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            exe_name = "unknown"
        title = win32gui.GetWindowText(hwnd)
        return exe_name, title

    def start_monitoring(self, on_change=None):
        self._is_running = True
        self._callback = on_change

        def monitoring_loop():
            prev_app = None
            prev_title = None
            while self._is_running:
                try:
                    exe_name, title = self.get_active_window()
                    if exe_name != prev_app or title != prev_title:
                        self.current_app = exe_name
                        self.current_title = title
                        prev_app = exe_name
                        prev_title = title
                        if self._callback:
                            self._callback(self.get_current_info())
                    time.sleep(0.5)
                except KeyboardInterrupt:
                    break

        self._monitor_thread = threading.Thread(target=monitoring_loop, daemon=True)
        self._monitor_thread.start()

    def get_current_info(self):
        return {
            "app_name": self.current_app,
            "window_title": self.current_title
        }

    def stop(self):
        self._is_running = False
