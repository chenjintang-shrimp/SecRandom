from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from qfluentwidgets import *
import webbrowser
import os
import json
from datetime import datetime
from loguru import logger

from app.common.config import get_theme_icon, load_custom_font, check_for_updates, VERSION, themeColor, is_dark_theme
from app.common.path_utils import path_manager, open_file

def show_update_notification(latest_version, auto_close=True):
    """显示更新通知窗口"""
    if hasattr(QApplication.instance(), 'update_notification_window'):
        # 如果窗口已存在则激活它
        notification_window = QApplication.instance().update_notification_window
        if notification_window.isHidden():
            notification_window.show()
        notification_window.raise_()
        notification_window.activateWindow()
        return

    # 创建新的通知窗口（UpdateNotification类已通过qconfig.themeChanged.connect处理主题变化）
    notification_window = UpdateNotification(latest_version, auto_close=auto_close)
    QApplication.instance().update_notification_window = notification_window
    notification_window.show()

class UpdateNotification(QDialog):
    """自定义更新通知窗口"""
    def __init__(self, latest_version, auto_close=False):
        super().__init__(parent=None, flags=Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.latest_version = latest_version
        self.auto_close = auto_close
        self.duration = 15000  # 默认显示15秒（如果启用自动关闭）
        self.init_ui()
        self.update_theme_style()  # 应用主题样式
        self.init_animation()
        if self.auto_close:
            self.start_auto_close_timer()
        
        # 连接主题变化信号
        qconfig.themeChanged.connect(self.update_theme_style)

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
        self.title_label = BodyLabel("SecRandom 有新版本可用")
        self.title_label.setFont(QFont(load_custom_font(), 14, QFont.Bold))
        self.title_label.setStyleSheet("border: none; background: transparent;")

        # 版本信息
        self.version_label = BodyLabel(f"📌 当前版本: {VERSION}\n🚀 发现新版本 {self.latest_version}\n✨ 修复已知问题，优化体验\n💡 建议立即更新以获得最佳体验")
        self.version_label.setFont(QFont(load_custom_font(), 12))
        self.version_label.setStyleSheet("border: none; background: transparent;")
        self.version_label.setAlignment(Qt.AlignCenter)

        # 关闭按钮
        close_btn = PrimaryPushButton("x")
        close_icon_path = get_theme_icon("ic_fluent_arrow_exit_20_filled")
        close_btn.setIcon(QIcon(str(close_icon_path)))
        close_btn.setStyleSheet("background: transparent; border: none;")
        close_btn.clicked.connect(self.close_with_animation)
        close_btn.setFont(QFont(load_custom_font(), 12))

        # 添加到标题布局
        title_layout.addWidget(icon_label)
        title_layout.addWidget(self.title_label)
        title_layout.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))
        title_layout.addWidget(close_btn)

        # 按钮布局
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        # 稍后提醒按钮
        later_btn = PushButton("今日不提醒")
        later_btn.setObjectName("later_btn")
        later_btn.setFont(QFont(load_custom_font(), 12))
        later_btn.clicked.connect(self.remind_later)

        # 官网
        manual_update_btn = PrimaryPushButton("官网 下载更新")
        manual_update_btn.setIcon(QIcon(str(icon_path)))
        manual_update_btn.setObjectName("manual_update_btn")
        manual_update_btn.setFont(QFont(load_custom_font(), 12))
        manual_update_btn.clicked.connect(self.on_manual_update_clicked)

        # 添加到按钮布局
        btn_layout.addWidget(later_btn)
        btn_layout.addWidget(manual_update_btn)

        # 添加所有组件到主布局
        main_layout.addLayout(title_layout)
        main_layout.addWidget(self.version_label)
        main_layout.addLayout(btn_layout)

        self.move_to_bottom_right()

    def init_animation(self):
        """初始化动画效果"""
        # 设置初始透明度为0
        self.setWindowOpacity(0.0)
        
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

    def update_theme_style(self):
        """更新主题样式"""
        # 判断当前主题
        is_dark = is_dark_theme(qconfig)
        
        # 获取主题色
        try:
            theme_color = themeColor()
            # 如果themeColor()返回的是QColor对象，需要转换为十六进制字符串
            if hasattr(theme_color, 'name'):
                theme_color = theme_color.name()
        except:
            theme_color = "#66CCFF"
        
        # 根据主题设置颜色
        if is_dark:
            bg_color = "#111116"  # 深色背景
            text_color = "#F5F5F5"  # 浅色文本
            border_color = "#323233"  # 深色边框
            title_bg = "#202020"  # 深色标题背景
            hover_color = "#323233"  # 深色悬停颜色
        else:
            bg_color = "#F5F5F5"  # 浅色背景
            text_color = "#111116"  # 深色文本
            border_color = "#E0E0E0"  # 浅色边框
            title_bg = "#FFFFFF"  # 浅色标题背景
            hover_color = "#E0E0E0"  # 浅色悬停颜色
        
        # 获取当前透明度，避免覆盖动画设置的透明度
        current_opacity = self.windowOpacity()
        
        # 应用样式表
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {bg_color};
                border: 1px solid {border_color};
                border-radius: 8px;
            }}
            QLabel {{
                color: {text_color};
                background: transparent;
                border: none;
            }}
            QPushButton {{
                background-color: {title_bg};
                color: {text_color};
                border: 1px solid {border_color};
                border-radius: 4px;
                padding: 5px 10px;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
            }}
            QPushButton#manual_update_btn {{
                background-color: {theme_color};
                color: white;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: 500;
                border: none;
            }}
            QPushButton#manual_update_btn:hover {{
                background-color: {theme_color};
            }}
            QPushButton#later_btn {{
                background-color: transparent;
                border: 1px solid {border_color};
            }}
            QPushButton#later_btn:hover {{
                background-color: {hover_color};
            }}
        """)
        
        # 恢复透明度设置
        self.setWindowOpacity(current_opacity)
        
        # 更新标签颜色
        if hasattr(self, 'title_label'):
            self.title_label.setStyleSheet(f"color: {text_color}; border: none; background: transparent;")
        if hasattr(self, 'version_label'):
            self.version_label.setStyleSheet(f"color: {text_color}; border: none; background: transparent;")
        
        # 更新窗口标题栏颜色（仅Windows系统）
        if os.name == 'nt':  # Windows系统
            try:
                import ctypes
                from ctypes import wintypes
                
                # 定义Windows API函数和结构
                hwnd = int(self.winId())
                color = int(text_color.replace('#', '0x'), 16)
                
                # 设置窗口标题栏颜色
                ctypes.windll.dwmapi.DwmSetWindowAttribute(
                    hwnd,
                    35,  # DWMWA_TEXT_COLOR
                    ctypes.byref(ctypes.c_int(color)),
                    ctypes.sizeof(ctypes.c_int)
                )
                
                # 设置窗口背景颜色
                bg_color_int = int(bg_color.replace('#', '0x'), 16)
                ctypes.windll.dwmapi.DwmSetWindowAttribute(
                    hwnd,
                    36,  # DWMWA_CAPTION_COLOR
                    ctypes.byref(ctypes.c_int(bg_color_int)),
                    ctypes.sizeof(ctypes.c_int)
                )
            except Exception:
                pass  # 如果设置失败，忽略错误

    def start_auto_close_timer(self):
        """启动自动关闭定时器"""
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.close_with_animation)
        self.timer.start(self.duration)

    def showEvent(self, event):
        """显示事件 - 确保窗口在最前面并正确定位"""
        self.raise_()
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

    def remind_later(self):
        """今日不提醒按钮点击事件"""
        # 获取配置文件路径
        config_file = path_manager.get_settings_path("update_reminder.json")
        
        # 获取当前日期
        today = datetime.now().strftime("%Y-%m-%d")
        
        # 保存今日已提醒的标记
        reminder_data = {
            "last_reminder_date": today,
            "latest_version": self.latest_version
        }
        
        try:
            with open(config_file, "w") as f:
                json.dump(reminder_data, f)
        except Exception as e:
            logger.error(f"保存提醒设置失败: {e}")
        
        self.close_with_animation()
    
    def should_show_notification(self):
        """检查是否应该显示更新通知"""
        # 获取配置文件路径
        config_file = path_manager.get_settings_path("update_reminder.json")
        
        # 如果配置文件不存在，则显示通知
        if not os.path.exists(config_file):
            return True
        
        try:
            # 读取配置文件
            with open(config_file, "r") as f:
                reminder_data = json.load(f)
            
            # 获取上次提醒日期
            last_reminder_date = reminder_data.get("last_reminder_date", "")
            last_version = reminder_data.get("latest_version", "")
            
            # 如果上次提醒日期不是今天，或者版本已更新，则显示通知
            today = datetime.now().strftime("%Y-%m-%d")
            if last_reminder_date != today or last_version != self.latest_version:
                return True
            
            return False
        except Exception as e:
            logger.error(f"读取提醒设置失败: {e}")
            return True

    def closeEvent(self, event):
        if hasattr(QApplication.instance(), 'update_notification_window'):
            del QApplication.instance().update_notification_window
        super().closeEvent(event)
