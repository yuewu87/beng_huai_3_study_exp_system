from monitor import ExeChecker
from judger import ExeJudger
from exp_system import ExpSystem
from gui import ExperienceWindow
from PyQt5.QtWidgets import QApplication
import sys
import signal


def main():
    app = QApplication(sys.argv)

    exp_sys = ExpSystem()
    judger = ExeJudger(exp_sys)
    monitor = ExeChecker()

    window = ExperienceWindow(exp_sys)
    window.show()

    def graceful_exit(sig, frame):
        monitor.stop()
        window.close()
        app.quit()
    signal.signal(signal.SIGINT, graceful_exit)

    def check_app(app_info):
        judger.is_productive(app_info)

    monitor.start_monitoring(on_change=check_app)
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
