"""PyQt5 桌面悬浮窗 — 等级/段位/经验进度实时显示"""
from PyQt5.QtWidgets import (QHBoxLayout, QMainWindow, QProgressBar,
                             QLabel, QVBoxLayout, QWidget)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QPainter, QColor, QLinearGradient, QBrush


class ExperienceWindow(QMainWindow):
    def __init__(self, exp_system):
        super().__init__()
        self.exp_system = exp_system
        self.last_level = exp_system.user["current_level"]
        self.last_segment = self.get_segment(exp_system.user["current_level"])

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.drag_pos = None
        self.init_ui()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_data)
        self.timer.start(1000)

    def mousePressEvent(self, event):
        self.drag_pos = event.globalPos()

    def mouseMoveEvent(self, event):
        if self.drag_pos:
            delta = event.globalPos() - self.drag_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.drag_pos = event.globalPos()

    def mouseReleaseEvent(self, event):
        self.drag_pos = None

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0, QColor(0x2b, 0x2b, 0x2b, 200))
        gradient.setColorAt(1, QColor(0x1f, 0x1f, 0x1f, 150))

        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(self.rect(), 15, 15)

    def init_ui(self):
        title_font = QFont("秋日私语", 14, QFont.Bold)
        digital_font = QFont("秋日私语", 14, QFont.Bold)

        self.level_label = QLabel("等级: 1")
        self.segment_label = QLabel("段位: F")
        self.level_label.setObjectName("LevelLabel")
        self.segment_label.setObjectName("SegmentLabel")

        self.setStyleSheet("""
            QProgressBar {
                color: #ffffff;
                background: #404040;
                border: 2px solid #555555;
                border-radius: 5px;
                height: 25px;
                text-align: center;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x1:1, y1:0,
                    stop:0 #00ff88,
                    stop:1 #00ccff);
                border-radius: 3px;
            }
            QLabel#LevelLabel {
                color: #00ffaa;
                font-size: 18px;
                padding: 5px;
            }
            QLabel#SegmentLabel {
                color: #00ffaa;
                font-size: 18px;
                padding: 5px;
            }
            QLabel {
                color: #00ff99;
                font-family: 微软雅黑;
                font-size: 14px;
                padding: 5px;
            }
        """)

        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)

        main_widget = QWidget()
        main_widget.setAttribute(Qt.WA_TranslucentBackground)
        main_widget.setStyleSheet("background: transparent;")
        self.setCentralWidget(main_widget)

        header_layout = QHBoxLayout()
        header_layout.addWidget(self.level_label)
        header_layout.addWidget(self.segment_label)

        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setFormat("经验进度: %p%")

        self.level_label.setFont(title_font)
        self.segment_label.setFont(title_font)
        self.progress.setFont(digital_font)

        main_layout = QVBoxLayout()
        main_layout.addLayout(header_layout)
        main_layout.addWidget(self.progress)

        main_widget.setLayout(main_layout)

        self.setWindowTitle("学习经验系统")
        self.setGeometry(100, 100, 300, 100)

    def get_segment(self, level):
        segments = ['F', 'E', 'D', 'C', 'B', 'A', 'S', 'SS', 'SSS']
        if level <= 80:
            return segments[(level-1)//10]
        return 'EX'

    def update_data(self):
        self.exp_system._update_level()
        current_level = self.exp_system.user["current_level"]
        total_xp = self.exp_system.user["total_xp"]
        current_segment = self.get_segment(current_level)

        if current_level < 88:
            next_level_xp = self.exp_system.exp_thresholds[current_level-1]
            current_level_xp = self.exp_system.exp_thresholds[current_level-2] if current_level > 1 else 0
            current_exp = int(total_xp - current_level_xp)
            required_exp = next_level_xp - current_level_xp

            self.progress.setMaximum(required_exp)
            self.progress.setValue(current_exp)
            self.progress.setFormat(f"经验进度: {current_exp}/{required_exp}")
        else:
            self.progress.setMaximum(100)
            self.progress.setValue(100)
            self.progress.setFormat("经验进度: MAX")

        self.level_label.setText(f"等级: {current_level} 级")
        self.segment_label.setText(f"段位: {self.get_segment(current_level)} 级女武神")

        if current_level > self.last_level:
            self.last_level = current_level

        if current_segment != self.last_segment:
            self.last_segment = current_segment
