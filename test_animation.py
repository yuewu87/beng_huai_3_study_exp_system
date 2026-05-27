"""升级/升段动画演示 — 每隔几秒依次触发"""
import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer
from src.exp_system import ExpSystem
from src.gui import ExperienceWindow


def main():
    app = QApplication(sys.argv)

    exp_sys = ExpSystem()
    window = ExperienceWindow(exp_sys)
    window.show()

    demos = [
        (window._show_popup, ("LEVEL UP! (Lv.30)", "#FFD700")),
        (window._flash_progress, ("#FFD700",)),
        (window._show_popup, ("RANK UP! (B)", "#AA44FF")),
        (window._flash_progress, ("#AA44FF",)),
        (window._show_popup, ("LEVEL UP! (Lv.31)", "#FFD700")),
        (window._flash_progress, ("#FFD700",)),
    ]

    def run_demo(i=0):
        if i >= len(demos):
            return
        func, args = demos[i]
        func(*args)
        QTimer.singleShot(2000, lambda: run_demo(i + 1))

    QTimer.singleShot(500, lambda: run_demo(0))

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
