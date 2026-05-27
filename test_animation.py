"""升级/升段动画演示"""
import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer
from src.exp_system import ExpSystem
from src.gui import ExperienceWindow, LEVEL_COLOR, RANK_COLOR


def main():
    app = QApplication(sys.argv)

    exp_sys = ExpSystem()
    window = ExperienceWindow(exp_sys)
    window.show()

    demos = [
        ("LEVEL UP! (Lv.30)", LEVEL_COLOR),
        ("RANK UP! (B)", RANK_COLOR),
        ("LEVEL UP! (Lv.31)", LEVEL_COLOR),
    ]

    def run_demo(i=0):
        if i >= len(demos):
            return
        text, color = demos[i]
        window._trigger_animation(text, color)
        QTimer.singleShot(3000, lambda: run_demo(i + 1))

    QTimer.singleShot(500, lambda: run_demo(0))

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
