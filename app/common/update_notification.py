from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from qfluentwidgets import *
import webbrowser

from app.common.config import get_theme_icon, load_custom_font, check_for_updates, VERSION, themeColor
from app.common.path_utils import path_manager, open_file

def show_update_notification(latest_version, auto_close=False):
    """显示更新通知窗口"""
    if hasattr(QApplication.instance(), 'update_notification_window'):
        # 如果窗口已存在则激活它
        notification_window = QApplication.instance().update_notification_window
        if notification_window.isHidden():
            notification_window.show()
        notification_window.raise_()
        notification_window.activateWindow()
        return

    # 创建新的通知窗口
    notification_window = UpdateNotification(latest_version, auto_close=auto_close)
    QApplication.instance().update_notification_window = notification_window
    notification_window.show()

class UpdateNotification(QDialog):
    """自定义更新通知窗口"""
    def __init__(self, latest_version, auto_close=False):
        super().__init__(parent=None, flags=Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.latest_version = latest_version
        self.auto_close = auto_close
        self.duration = 30000  # 默认显示30秒（如果启用自动关闭）
        self.init_ui()
        self.init_animation()
        if self.auto_close:
            self.start_auto_close_timer()

    def init_ui(self):
        """初始化UI界面"""
        cursor_pos = QCursor.pos()
        for screen in QGuiApplication.screens():
            if screen.geometry().contains(cursor_pos):
                target_screen = screen
                break
        else:
            target_screen = QGuiApplication.primaryScreen()
        screen_geometry = target_screen.availableGeometry()
        max_width = min(int(screen_geometry.width() * 0.3), 500)  # 最大宽度为屏幕30%或500px取较小值
        self.setMaximumWidth(max_width)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setStyleSheet("""
            QDialog {
                background-color: rgba(235, 238, 242, 0.5);
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 5px;
                opacity: 0;
            }
        """)

        # 创建主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(20)

        # 标题栏（包含图标和标题）
        title_layout = QHBoxLayout()
        title_layout.setSpacing(10)

        # 更新图标
        icon_label = QLabel()
        icon_path = path_manager.get_resource_path('icon', 'secrandom-icon-paper.png')
        icon_label.setPixmap(QIcon(str(icon_path)).pixmap(55, 55))
        icon_label.setStyleSheet("background: transparent; border: none;")

        # 标题文本
        title_label = BodyLabel("SecRandom 有新版本可用")
        title_label.setFont(QFont(load_custom_font(), 14, QFont.Bold))
        title_label.setStyleSheet("color: #1a1a1a; border: none; background: transparent;")

        # 版本信息
        version_label = BodyLabel(f"📌 当前版本: {VERSION}\n🎉 发现新版本 {self.latest_version}\n✨ 包含多项功能优化和体验改进")
        version_label.setFont(QFont(load_custom_font(), 12))
        version_label.setStyleSheet("color: #2d3436; border: none; background: transparent;")
        version_label.setAlignment(Qt.AlignCenter)

        # 关闭按钮
        close_btn = PushButton("")
        close_icon_path = get_theme_icon("ic_fluent_arrow_exit_20_filled")
        close_btn.setIcon(QIcon(str(close_icon_path)))
        close_btn.setStyleSheet("background: transparent; border: none;")
        close_btn.clicked.connect(self.close_with_animation)

        # 添加到标题布局
        title_layout.addWidget(icon_label)
        title_layout.addWidget(title_label)
        title_layout.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))
        title_layout.addWidget(close_btn)

        # 按钮布局
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        try:
            theme_color = themeColor()
            # 如果themeColor()返回的是QColor对象，需要转换为十六进制字符串
            if hasattr(theme_color, 'name'):
                theme_color = theme_color.name()
        except:
            theme_color = "#3AF2FF"
            
        font_color = "black"

        # 官网
        manual_update_btn = PushButton("     官网 下载更新")
        manual_update_btn.setIcon(QIcon(str(icon_path)))
        manual_update_btn.setStyleSheet(f""
            f"QPushButton {{background-color: {theme_color}; color: {font_color}; border-radius: 8px; padding: 8px 16px; font-weight: 500; border: none;}}"
            f"QPushButton:hover {{background-color: {theme_color};}}"

        )
        manual_update_btn.setFont(QFont(load_custom_font(), 12))
        manual_update_btn.clicked.connect(self.on_manual_update_clicked)

        # 添加到按钮布局
        btn_layout.addWidget(manual_update_btn)

        # 添加所有组件到主布局
        main_layout.addLayout(title_layout)
        main_layout.addWidget(version_label)
        main_layout.addLayout(btn_layout)

        self.move_to_bottom_right()

    def init_animation(self):
        """初始化动画效果"""
        # 获取屏幕几何信息
        screen_geometry = QApplication.desktop().availableGeometry()
        # 设置初始位置在屏幕右侧外
        self.move(screen_geometry.width(), self.y())
        
        # 创建位置动画
        self.pos_animation = QPropertyAnimation(self, b"pos")
        self.pos_animation.setDuration(600)
        self.pos_animation.setEasingCurve(QEasingCurve.OutCubic)
        self.pos_animation.setStartValue(QPoint(screen_geometry.width(), self.y()))
        self.pos_animation.setEndValue(QPoint(screen_geometry.width() - self.width() - 20, self.y()))
        
        # 创建透明度动画
        self.opacity_animation = QPropertyAnimation(self, b"windowOpacity")
        self.opacity_animation.setDuration(400)
        self.opacity_animation.setEasingCurve(QEasingCurve.InOutQuad)
        self.opacity_animation.setStartValue(0.0)
        self.opacity_animation.setEndValue(1.0)
        
        # 并行运行所有动画
        self.group_animation = QParallelAnimationGroup(self)
        self.group_animation.addAnimation(self.pos_animation)
        self.group_animation.addAnimation(self.opacity_animation)
        self.group_animation.start()

    def start_auto_close_timer(self):
        """启动自动关闭定时器"""
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.close_with_animation)
        self.timer.start(self.duration)

    def showEvent(self, event):
        super().showEvent(event)
        # 确保窗口尺寸已确定后再计算位置
        QTimer.singleShot(100, self.move_to_bottom_right)

    def move_to_bottom_right(self):
        """将窗口移动到屏幕右下角"""
        screen_geometry = QGuiApplication.primaryScreen().availableGeometry()
        # 重新获取窗口尺寸确保准确性
        self.adjustSize()
        x = max(0, screen_geometry.width() - self.width() - 20)
        y = max(0, screen_geometry.height() - self.height() - 20)
        self.move(x, y)

    def on_manual_update_clicked(self):
        """官网手动更新按钮点击事件"""
        webbrowser.open("https://secrandom.netlify.app/download")
        self.close_with_animation()

    def show_auto_update_dialog(self):
        """显示自动更新对话框"""
        dialog = AutoUpdateDialog(self.latest_version)
        dialog.exec_()

    def close_with_animation(self):
        """带动画效果关闭窗口"""
        # 获取屏幕几何信息
        screen_geometry = QApplication.desktop().availableGeometry()
        
        # 创建位置动画到屏幕右侧外
        self.pos_animation = QPropertyAnimation(self, b"pos")
        self.pos_animation.setEasingCurve(QEasingCurve.InCubic)
        self.pos_animation.setDuration(600)
        self.pos_animation.setStartValue(self.pos())
        self.pos_animation.setEndValue(QPoint(screen_geometry.width(), self.y()))
        
        # 创建透明度动画
        self.opacity_animation = QPropertyAnimation(self, b"windowOpacity")
        self.opacity_animation.setEasingCurve(QEasingCurve.InOutQuad)
        self.opacity_animation.setDuration(400)
        self.opacity_animation.setStartValue(1.0)
        self.opacity_animation.setEndValue(0.0)
        
        # 并行运行所有动画
        self.group_animation = QParallelAnimationGroup(self)
        self.group_animation.addAnimation(self.pos_animation)
        self.group_animation.addAnimation(self.opacity_animation)
        self.group_animation.finished.connect(self.close)
        self.group_animation.start()

    def mousePressEvent(self, event):
        """鼠标按下事件 - 重置自动关闭定时器（仅在启用自动关闭时）"""
        if event.button() == Qt.LeftButton and self.auto_close and hasattr(self, 'timer'):
            self.timer.start(self.duration)
        super().mousePressEvent(event)

    def showEvent(self, event):
        """显示事件 - 确保窗口在最前面"""
        self.raise_()
        super().showEvent(event)

    def closeEvent(self, event):
        if hasattr(QApplication.instance(), 'update_notification_window'):
            del QApplication.instance().update_notification_window
        super().closeEvent(event)
