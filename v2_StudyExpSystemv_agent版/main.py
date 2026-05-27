from 监测系统模块 import ExeChecker
from 判断模块 import ExeJudger
from 经验值系统模块 import ExpSystem
from GUI系统模块 import ExperienceWindow
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication
import sys
import signal

def main():
    # 创建Qt应用
    app = QApplication(sys.argv)
    
    # 初始化系统
    exp_sys = ExpSystem()
    monitor = ExeChecker()
    judger = ExeJudger(exp_sys)
    
    # 创建并显示GUI
    window = ExperienceWindow(exp_sys)
    window.show()

    # 设置信号处理
    def graceful_exit(sig, frame):
        monitor.stop()
        window.close()
        app.quit()
    signal.signal(signal.SIGINT, graceful_exit)
    
    # 启动监测
    monitor.start_monitoring()
    
    # 定时检测应用
    def check_app():
        app_info = monitor.get_current_info()
        judger.is_productive(app_info)
    
    timer = QTimer()
    timer.timeout.connect(check_app)
    timer.start(3000)  # 3秒检测一次
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()