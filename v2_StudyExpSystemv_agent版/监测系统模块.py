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
        
    @staticmethod
    def get_active_window():
        """获取当前活动窗口信息"""
        hwnd = win32gui.GetForegroundWindow()
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        try:
            process = psutil.Process(pid)
            exe_name = process.name().lower()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            exe_name = "unknown"
        title = win32gui.GetWindowText(hwnd)
        return exe_name, title

    def start_monitoring(self):
        """启动监测线程"""
        self._is_running = True
        def monitoring_loop():
            while self._is_running:
                # 添加退出检查点
                try:
                    exe_name, title = self.get_active_window()
                    self.current_app = exe_name
                    self.current_title = title
                    time.sleep(3)  # 每2.5秒检测一次
                except KeyboardInterrupt:
                    break
                
        self._monitor_thread = threading.Thread(target=monitoring_loop, daemon=True)
        self._monitor_thread.start()

    def get_current_info(self):
        """获取当前应用信息"""
        return {
            "app_name": self.current_app,
            "window_title": self.current_title
        }

    def stop(self):
        """停止监测"""
        self._is_running = False
