"""崩坏3 学习经验系统 — 入口，支持 --llm / --no-llm 参数"""
import argparse
import sys
import signal
from PyQt5.QtWidgets import QApplication
from src.monitor import ExeChecker
from src.judger import ExeJudger
from src.exp_system import ExpSystem
from src.gui import ExperienceWindow


def main():
    parser = argparse.ArgumentParser(description="崩坏3 学习经验系统")
    parser.add_argument("--llm", action="store_true", default=None, dest="use_llm",
                        help="启用 LLM 判定模式")
    parser.add_argument("--no-llm", action="store_false", default=None, dest="use_llm",
                        help="使用纯白名单模式")
    args = parser.parse_args()

    app = QApplication(sys.argv)

    exp_sys = ExpSystem()
    judger = ExeJudger(exp_sys, use_llm=args.use_llm)
    monitor = ExeChecker()

    window = ExperienceWindow(exp_sys)
    window.show()

    mode = "LLM" if judger.agent.use_llm else "白名单"
    print(f"启动模式: {mode}")

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
