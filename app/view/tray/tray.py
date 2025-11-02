# ==================================================
# 导入库
# ==================================================
import json
import os
import sys
import subprocess

from loguru import logger
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtNetwork import *
from qfluentwidgets import *

from app.tools.variable import *
from app.tools.path_utils import *
from app.tools.personalised import *
from app.tools.settings_default import *
from app.tools.settings_access import *
from app.Language.obtain_language import *

from app.tools.extract import _is_non_class_time

# ==================================================
# 平台检测
# ==================================================
def is_wayland():
    """检测是否在Wayland环境下运行"""
    if sys.platform.startswith('linux'):
        # 检查环境变量
        wayland_display = os.environ.get('WAYLAND_DISPLAY')
        xdg_session_type = os.environ.get('XDG_SESSION_TYPE')
        
        # 仅依赖环境变量检测，避免调用Qt函数可能导致的问题
        return (wayland_display is not None or xdg_session_type == 'wayland')
    return False

# ==================================================
# 托盘图标管理器类
# ==================================================
class Tray(QSystemTrayIcon):
    """系统托盘图标管理器
    
    负责管理托盘图标和菜单，提供右键菜单功能。
    继承自QSystemTrayIcon以简化实现。
    """
    showSettingsRequested = pyqtSignal()
    showSettingsRequestedAbout = pyqtSignal()
    
    def __init__(self, parent=None):
        """初始化系统托盘图标
        
        Args:
            parent: 父窗口对象，通常为主窗口
        """
        super().__init__(parent)
        self.main_window = parent
        self.is_wayland = is_wayland()
        if self.is_wayland:
            logger.info("检测到Wayland环境，启用Wayland兼容模式")
        self.setIcon(QIcon(str(get_resources_path('assets/icon', 'secrandom-icon-paper.png'))))
        self.setToolTip('SecRandom')
        self._create_menu()
        self.activated.connect(self._on_tray_activated)
        
        # 初始化菜单自动关闭定时器
        self._init_menu_timer()
    
    def _init_menu_timer(self):
        """初始化菜单自动关闭定时器"""
        self.menu_timer = QTimer(self)
        self.menu_timer.setSingleShot(True)
        self.menu_timer.timeout.connect(self._on_menu_timeout)
    
    def _create_menu(self):
        """创建托盘右键菜单"""
        # Wayland需要菜单为独立窗口，否则会出现点击和定位问题
        if self.is_wayland:
            self.tray_menu = RoundMenu(parent=None)
            # 设置Wayland特定的窗口标志
            self.tray_menu.setWindowFlags(
                Qt.WindowType.Popup | 
                Qt.WindowType.FramelessWindowHint |
                Qt.WindowType.NoDropShadowWindowHint
            )
        else:
            self.tray_menu = RoundMenu(parent=self.main_window)
        
        # 关于SecRandom
        self.tray_menu.addAction(Action('SecRandom', triggered=self.showSettingsRequestedAbout.emit))
        self.tray_menu.addSeparator()
        # 主界面控制
        self.tray_menu.addAction(Action('暂时显示/隐藏主界面', triggered=self.main_window.toggle_window))
        # 设置界面
        self.tray_menu.addAction(Action('打开设置界面', triggered=self.showSettingsRequested.emit))
        self.tray_menu.addSeparator()
        # 系统操作
        self.tray_menu.addAction(Action('重启', triggered=self.main_window.restart_app))
        self.tray_menu.addAction(Action('退出', triggered=self.main_window.close_window_secrandom))
        
        self.tray_menu.installEventFilter(self)
    
    def _on_tray_activated(self, reason):
        """处理托盘图标点击事件
        当用户点击托盘图标时，显示菜单"""
        if reason in (QSystemTrayIcon.ActivationReason.Trigger, 
                     QSystemTrayIcon.ActivationReason.Context):
            if self.is_wayland:
                # Wayland环境：使用exec_()在光标位置显示菜单
                # 这样可以避免菜单出现在屏幕中央的问题
                pos = QCursor.pos()
                # 使用QMenu的exec_静态方法，这在Wayland下工作得更好
                self.tray_menu.exec(pos)
                # Wayland下不需要手动管理菜单关闭，系统会处理
            else:
                # X11环境：使用原有的popup方式
                pos = QCursor.pos()
                screen = QApplication.primaryScreen().availableGeometry()
                menu_size = self.tray_menu.sizeHint()
                if pos.x() + menu_size.width() > screen.right():
                    adjusted_x = pos.x() - menu_size.width()
                else:
                    adjusted_x = pos.x()
                if pos.y() + menu_size.height() > screen.bottom():
                    adjusted_y = pos.y() - menu_size.height()
                else:
                    adjusted_y = pos.y()
                adjusted_x = max(screen.left(), min(adjusted_x, screen.right() - menu_size.width()))
                adjusted_y = max(screen.top(), min(adjusted_y, screen.bottom() - menu_size.height()))
                adjusted_pos = QPoint(adjusted_x, adjusted_y - 35)
                self.tray_menu.popup(adjusted_pos)
                self.menu_timer.start(MENU_AUTO_CLOSE_TIMEOUT)
    
    def _on_menu_timeout(self):
        """菜单超时自动关闭
        当用户5秒内没有操作菜单时，自动关闭菜单"""
        if self.tray_menu.isVisible():
            self.tray_menu.close()
    
    def eventFilter(self, obj, event):
        """事件过滤器
        
        监听菜单相关事件，当用户点击菜单外部时自动关闭菜单。
        
        Args:
            obj: 事件对象
            event: 事件类型
            
        Returns:
            bool: 是否拦截事件
        """
        if obj == self.tray_menu:
            if event.type() in (QEvent.Type.MouseButtonPress, QEvent.Type.Hide):
                self.menu_timer.stop()
        if (event.type() == QEvent.Type.MouseButtonPress and 
            self.tray_menu.isVisible()):
            click_pos = event.globalPosition().toPoint()
            menu_rect = self.tray_menu.geometry()
            if not menu_rect.contains(click_pos):
                self.tray_menu.close()
                self.menu_timer.stop()
                return True
        return super().eventFilter(obj, event)
    
    def show_tray_icon(self):
        """显示托盘图标"""
        if not self.isVisible():
            self.show()