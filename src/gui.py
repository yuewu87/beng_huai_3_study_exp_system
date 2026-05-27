"""PyQt5 桌面悬浮窗 — 等级/段位/经验进度实时显示 + 升级升段动画"""
from PyQt5.QtWidgets import (QHBoxLayout, QMainWindow, QProgressBar,
                             QLabel, QVBoxLayout, QWidget)
from PyQt5.QtCore import (Qt, QTimer, QPropertyAnimation, QEasingCurve,
                          QParallelAnimationGroup, pyqtProperty)
from PyQt5.QtGui import (QFont, QPainter, QColor, QLinearGradient, QBrush,
                         QPen)


LEVEL_COLOR = "#FFD700"
RANK_COLOR = "#AA44FF"
GLOW_WIDTH = 6


class ExperienceWindow(QMainWindow):
    def __init__(self, exp_system):
        super().__init__()
        self.exp_system = exp_system
        self.last_level = exp_system.user["current_level"]
        self.last_segment = self.get_segment(exp_system.user["current_level"])
        self._glow_color = None
        self._glow_anim = None
        self._flash_timer = None
        self._glow_opacity_val = 0.0

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.drag_pos = None
        self.init_ui()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_data)
        self.timer.start(1000)

    def _get_glow_opacity(self):
        return self._glow_opacity_val

    def _set_glow_opacity(self, val):
        self._glow_opacity_val = val
        self.update()

    _glow_opacity = pyqtProperty(float, _get_glow_opacity, _set_glow_opacity)

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

        # 泛光环
        if self._glow_color and self._glow_opacity_val > 0:
            base = QColor(self._glow_color)
            for i in range(3):
                alpha = int(self._glow_opacity_val * (100 - i * 30))
                if alpha <= 0:
                    continue
                glow = QColor(base.red(), base.green(), base.blue(), alpha)
                pen = QPen(glow, GLOW_WIDTH + i * 4)
                pen.setJoinStyle(Qt.RoundJoin)
                painter.setPen(pen)
                painter.setBrush(Qt.NoBrush)
                m = int((GLOW_WIDTH + i * 4) / 2)
                painter.drawRoundedRect(self.rect().adjusted(m, m, -m, -m), 15, 15)

        # 主体
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
        self.setGeometry(100, 100, 380, 100)

    def get_segment(self, level):
        segments = ['F', 'E', 'D', 'C', 'B', 'A', 'S', 'SS', 'SSS']
        if level <= 80:
            return segments[(level-1)//10]
        return 'EX'

    def _show_popup(self, text, color):
        popup = QLabel(text, self)
        popup.setStyleSheet(f"""
            color: {color};
            font-family: 微软雅黑;
            font-size: 22px;
            font-weight: bold;
            background: transparent;
            padding: 0px;
        """)
        popup.adjustSize()
        popup.show()

        x = (self.width() - popup.width()) // 2
        y = -popup.height()
        popup.move(x, y)
        popup.raise_()

        anim_group = QParallelAnimationGroup()

        pos_anim = QPropertyAnimation(popup, b"pos")
        pos_anim.setDuration(1200)
        pos_anim.setStartValue(popup.pos())
        pos_anim.setEndValue(popup.pos() + type(popup.pos())(0, -60))
        pos_anim.setEasingCurve(QEasingCurve.OutCubic)

        fade_anim = QPropertyAnimation(popup, b"windowOpacity")
        fade_anim.setDuration(1200)
        fade_anim.setStartValue(1.0)
        fade_anim.setEndValue(0.0)

        anim_group.addAnimation(pos_anim)
        anim_group.addAnimation(fade_anim)
        anim_group.finished.connect(popup.deleteLater)
        anim_group.start()

    def _start_glow(self, color):
        self._glow_color = color
        self._glow_opacity = 255
        self.update()

        if self._glow_anim:
            self._glow_anim.stop()
        self._glow_anim = QPropertyAnimation(self, b"_glow_opacity")
        self._glow_anim.setDuration(360)
        self._glow_anim.setStartValue(255)
        self._glow_anim.setEndValue(0)
        self._glow_anim.setEasingCurve(QEasingCurve.OutQuad)
        self._glow_anim.finished.connect(
            lambda: setattr(self, '_glow_color', None) or self.update()
        )
        self._glow_anim.start()

    def _flash_progress(self, color):
        self.progress.setStyleSheet(f"""
            QProgressBar::chunk {{
                background: qlineargradient(x1:0, y1:0, x1:1, y1:0,
                    stop:0 {color},
                    stop:1 {color});
                border-radius: 3px;
            }}
        """)
        if self._flash_timer:
            self._flash_timer.stop()
        self._flash_timer = QTimer()
        self._flash_timer.setSingleShot(True)
        self._flash_timer.timeout.connect(self._restore_progress_style)
        self._flash_timer.start(1200)

    def _restore_progress_style(self):
        self.progress.setStyleSheet("")

    def _trigger_animation(self, popup_text, color):
        self._show_popup(popup_text, color)
        self._start_glow(color)
        self._flash_progress(color)

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
        self.segment_label.setText(f"段位: {current_segment} 级女武神")

        if current_level > self.last_level:
            self._trigger_animation(f"LEVEL UP! (Lv.{current_level})", LEVEL_COLOR)
            self.last_level = current_level

        if current_segment != self.last_segment:
            self._trigger_animation(f"RANK UP! ({current_segment})", RANK_COLOR)
            self.last_segment = current_segment
