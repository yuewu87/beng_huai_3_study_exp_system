from PyQt5.QtWidgets import (QHBoxLayout, QMainWindow, QProgressBar, 
                            QLabel, QVBoxLayout, QWidget, QMessageBox)
from PyQt5.QtCore import (Qt, QTimer)
from PyQt5.QtGui import QFont, QPainter, QColor, QLinearGradient, QBrush

class ExperienceWindow(QMainWindow):
    def __init__(self, exp_system):
        super().__init__()
        self.exp_system = exp_system
        self.last_level = exp_system.user["current_level"]

        # 修改窗口标志
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        # 添加拖动支持
        self.drag_pos = None
        
        # 窗口置顶设置
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        
        # 初始化UI
        self.init_ui()
        
        # 启动定时刷新
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_data)
        self.timer.start(1000)  # 1秒刷新一次
    
    # 设置窗口拖动
    def mousePressEvent(self, event):
        self.drag_pos = event.globalPos()
        
    def mouseMoveEvent(self, event):
        if self.drag_pos:
            delta = event.globalPos() - self.drag_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.drag_pos = event.globalPos()
            
    def mouseReleaseEvent(self, event):
        self.drag_pos = None

        # 在类中添加绘制方法
    def paintEvent(self, event):
        """
        这种方法相比纯 CSS 实现的优势：

        能更好地处理半透明效果
        可以实现更复杂的渐变效果
        与窗口的透明属性（WA_TranslucentBackground）配合更好
        避免了一些平台相关的渲染问题
        """
        # 创建QPainter绘制圆角背景
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 绘制渐变背景（最后两位是Alpha值）
        """
        这种方法相比setWindowOpacity的优势：

        只影响背景透明度，文字和控件保持清晰
        可以与渐变效果完美结合
        不会产生窗口阴影等副作用
        数值范围：0（完全透明）~255（完全不透明）
        """
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0, QColor(0x2b, 0x2b, 0x2b, 200))  # #2b2b2b # 80%不透明
        gradient.setColorAt(1, QColor(0x1f, 0x1f, 0x1f, 150))  # #1f1f1f # 60%不透明
        
        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(self.rect(), 15, 15)  # 15px圆角

    def init_ui(self):
        # 创建字体对象
        title_font = QFont("秋日私语", 14, QFont.Bold)  
        digital_font = QFont("秋日私语", 14, QFont.Bold)

        self.level_label = QLabel("等级: 1")
        self.segment_label = QLabel("段位: F")
        # 设置对象名称用于样式表选择
        self.level_label.setObjectName("LevelLabel")
        self.segment_label.setObjectName("SegmentLabel")


        # 添加样式表
        self.setStyleSheet("""
            QProgressBar {
                color: #ffffff;  /* 新增文字颜色设置 */
                background: #404040;  /* 中灰色 - 进度条背景 */
                border: 2px solid #555555;  /* 灰蓝色 - 进度条边框 */
                border-radius: 5px;
                height: 25px;
                text-align: center;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x1:1, y1:0,
                    stop:0 #00ff88,  /* 青绿色 - 进度条渐变起始色 */
                    stop:1 #00ccff); /* 亮蓝色 - 进度条渐变结束色 */
                border-radius: 3px;
            }
            QLabel#LevelLabel {
                color: #00ffaa;  /* 等级数字颜色 - 青绿色 */
                font-size: 18px;
                padding: 5px;
            }
            QLabel#SegmentLabel {
                color: #00ffaa;  /* 段位字母颜色 - 金色 */
                font-size: 18px;
                padding: 5px;
            }
            QLabel {
                color: #00ff99;  /* 青绿色 - 所有标签文字颜色 */
                font-family: 微软雅黑;  /*保底设置*/
                font-size: 14px;
                padding: 5px;
            }
        """)

        # 新增窗口属性设置
        self.setAttribute(Qt.WA_TranslucentBackground)  # 启用透明背景
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)
        
        # 添加透明度
        # self.setWindowOpacity(0.80)

        # 主控件
        main_widget = QWidget()
        main_widget.setAttribute(Qt.WA_TranslucentBackground)  # 子控件透明
        main_widget.setStyleSheet("background: transparent;")  # 新增
        self.setCentralWidget(main_widget)
        
        # 创建水平布局容器
        header_layout = QHBoxLayout()
        header_layout.addWidget(self.level_label)
        header_layout.addWidget(self.segment_label)
        
        # 进度条
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setFormat("经验进度: %p%")
        
        # 应用字体
        self.level_label.setFont(title_font)
        self.segment_label.setFont(title_font)
        self.progress.setFont(digital_font)

        # 垂直布局
        main_layout = QVBoxLayout()
        main_layout.addLayout(header_layout)
        main_layout.addWidget(self.progress)
        
        main_widget.setLayout(main_layout)
        
        # 窗口设置
        self.setWindowTitle("学习经验系统")
        self.setGeometry(100, 100, 300, 100)

    def get_segment(self, level):
        """根据等级返回段位"""
        segments = ['F', 'E', 'D', 'C', 'B', 'A', 'S', 'SS', 'SSS']
        if level <= 80:
            return segments[(level-1)//10]
        return 'EX'

    def update_data(self):
        # 获取最新数据
        current_level = self.exp_system.user["current_level"]
        total_xp = self.exp_system.user["total_xp"]
        
        # 更新进度条
        if current_level < 88:
            next_level_xp = self.exp_system.exp_thresholds[current_level-1]
            current_level_xp = self.exp_system.exp_thresholds[current_level-2] if current_level>1 else 0
            current_exp = int(total_xp - current_level_xp)
            required_exp = next_level_xp - current_level_xp
            
            self.progress.setMaximum(required_exp)
            self.progress.setValue(current_exp)
            self.progress.setFormat(f"经验进度: {current_exp}/{required_exp}")
        else:
            self.progress.setMaximum(100)
            self.progress.setValue(100)
            self.progress.setFormat("经验进度: MAX")
        
        # 更新标签
        self.level_label.setText(f"等级: {current_level}")
        self.segment_label.setText(f"段位: {self.get_segment(current_level)}")
        
        # 检测升级
        if current_level > self.last_level:
            print(f"触发升级动画：{self.last_level} → {current_level}")    # 调试输出
            self.show_levelup_message(current_level)                      # 调用升级动画
            self.last_level = current_level                               # 更新等级

    def show_levelup_message(self, new_level):
        print("=" * 10, "升级了!", "=" * 10)
        # # 创建消息弹窗
        # msg_box = QMessageBox()
        # msg_box.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        # msg_box.setStyleSheet("""
        #     QMessageBox {
        #         background: rgba(0, 0, 0, 180);
        #         border-radius: 15px;
        #         padding: 15px;
        #     }
        #     QLabel {
        #         color: #FFD700;
        #         font-size: 18px;
        #         font-weight: bold;
        #         padding: 8px 15px;
        #     }
        # """)
        # msg_box.setText(f"✨ 升级到 {new_level} 级！✨")
        
        # # 设置弹窗位置（屏幕右下角）
        # screen_geo = self.screen().availableGeometry()
        # msg_box.move(
        #     screen_geo.right() - msg_box.width() - 20,
        #     screen_geo.bottom() - msg_box.height() - 20
        # )
        
        # # 自动关闭设置
        # QTimer.singleShot(2500, msg_box.close)  # 2.5秒后自动关闭
        # msg_box.exec_()
