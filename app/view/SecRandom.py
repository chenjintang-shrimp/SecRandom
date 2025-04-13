from qfluentwidgets import *
from qfluentwidgets import FluentIcon as fIcon
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

import json
import os
import sys
from loguru import logger

# 确认是否存在目录
if ('./app/Settings') != None and not os.path.exists('./app/Settings'):
    os.makedirs('./app/Settings')

if ('./app/resource/group') != None and not os.path.exists('./app/resource/group'):
    os.makedirs('./app/resource/group')

# 配置日志记录
log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

logger.add(
    os.path.join(log_dir, "SecRandom_{time:YYYY-MM-DD}.log"),
    rotation="1 MB",
    encoding="utf-8",
    retention="30 days",
    format="{time:YYYY-MM-DD HH:mm:ss:SSS} | {level} | {name}:{function}:{line} - {message}"
)

# 导入子页面
from app.view.settings import settings_Window
from app.view.single import single
from app.view.multiplayer import multiplayer
from app.view.group import groupplayer
from app.view.history import history
from app.view.levitation import LevitationWindow

class Window(MSFluentWindow):
    def __init__(self):
        super().__init__()
        self.resize(1200, 810)
        self.setMinimumSize(1000, 810)
        self.setWindowTitle('SecRandom')
        self.setWindowIcon(QIcon('./app/resource/icon/SecRandom.png'))
        self.start_cleanup()
        self.levitation_window = LevitationWindow()
        try:
            with open('app/Settings/Settings.json', 'r', encoding='utf-8') as f:
                settings = json.load(f)
                foundation_settings = settings.get('foundation', {})
                pumping_floating_enabled = foundation_settings.get('pumping_floating_enabled', True)
                if pumping_floating_enabled == True:
                    self.levitation_window.show()
        except FileNotFoundError as e:
            logger.error(f"加载设置时出错: {e}, 使用默认显示浮窗功能")
            self.levitation_window.show()
        except KeyError:
            logger.error(f"设置文件中缺少'foundation'键, 使用默认显示浮窗功能")
            self.levitation_window.show()
      
        # 初始化系统托盘
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon('./app/resource/icon/SecRandom.png'))
        self.tray_icon.setToolTip('SecRandom')
        
        # 创建托盘菜单
        self.tray_menu = RoundMenu(parent=self)
        self.tray_menu.addAction(Action(fIcon.POWER_BUTTON, '暂时显示/隐藏主界面', triggered=self.toggle_window))
        self.tray_menu.addAction(Action(QIcon("app\\resource\\icon\\SecRandom_floating.png"), '暂时显示/隐藏浮窗', triggered=self.toggle_levitation_window))
        self.tray_menu.addAction(Action(fIcon.SETTING, '打开设置界面', triggered=self.show_setting_interface))
        # self.tray_menu.addAction(Action(fIcon.SYNC, '重启', triggered=self.restart_app))
        self.tray_menu.addAction(Action(fIcon.CLOSE, '退出', triggered=self.close_window_secrandom))
        
        self.tray_icon.show()
        self.tray_icon.activated.connect(self.contextMenuEvent)

        # 获取主屏幕
        screen = QApplication.primaryScreen()
        # 获取屏幕的可用几何信息
        desktop = screen.availableGeometry()
        w, h = desktop.width(), desktop.height()
        try:
            with open('app/Settings/Settings.json', 'r', encoding='utf-8') as f:
                settings = json.load(f)
                foundation_settings = settings.get('foundation', {})
                main_window_mode = foundation_settings.get('main_window_mode', 0)
                if main_window_mode == 0:
                    self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)
                elif main_window_mode == 1:
                    self.move(w // 2 - self.width() // 2, h * 3 // 5 - self.height() // 2)
        except FileNotFoundError as e:
            logger.error(f"加载设置时出错: {e}, 使用默认窗口居中显示主窗口")
            self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)

        self.splashScreen = SplashScreen(self.windowIcon(), self)
        self.splashScreen.setIconSize(QSize(256, 256))
        try:
            with open('./app/Settings/Settings.json', 'r', encoding='utf-8') as f:
                settings = json.load(f)
            if settings.get('toggle_window') == 'show':
                self.show()
        except Exception as e:
            logger.error(f"无法加载设置文件: {e}")
        self.createSubInterface()
        self.splashScreen.finish()

    def createSubInterface(self):
        loop = QEventLoop(self)
        QTimer.singleShot(1, loop.quit)
        loop.exec()

        self.settingInterface = settings_Window(self)
        self.settingInterface.setObjectName("settingInterface")

        self.historyInterface = history(self)
        self.historyInterface.setObjectName("historyInterface")

        self.singleInterface = single(self)
        self.singleInterface.setObjectName("singleInterface")

        self.multiInterface = multiplayer(self)
        self.multiInterface.setObjectName("multiInterface")

        self.groupInterface = groupplayer(self)
        self.groupInterface.setObjectName("groupInterface")

        self.initNavigation()

    def initNavigation(self):
        # 使用 MSFluentWindow 的 addSubInterface 方法
        self.addSubInterface(self.singleInterface, fIcon.ROBOT, '抽单人', position=NavigationItemPosition.TOP)
        self.addSubInterface(self.multiInterface, fIcon.PEOPLE, '抽多人', position=NavigationItemPosition.TOP)
        self.addSubInterface(self.groupInterface, fIcon.TILES, '抽小组', position=NavigationItemPosition.TOP)

        self.addSubInterface(self.historyInterface, fIcon.HISTORY, '历史记录', position=NavigationItemPosition.BOTTOM)

    def closeEvent(self, event):
        """窗口关闭时隐藏主界面"""
        self.hide()
        event.ignore()

    def close_window_secrandom(self):
        """关闭应用程序"""
        self.start_cleanup()
        self.tray_icon.hide()
        QApplication.quit()
        logger.info("应用程序已退出")

    def start_cleanup(self):
        """软件启动时清理临时抽取记录文件"""
        # 获取抽选模式设置
        try:
            with open('app/Settings/Settings.json', 'r', encoding='utf-8') as f:
                settings = json.load(f)
                global_draw_mode = settings['global']['draw_mode']

        except Exception as e:
            global_draw_mode = 1
            logger.error(f"加载抽选模式设置时出错: {e}, 使用默认:不重复抽取(直到软件重启)模式来清理临时抽取记录文件")

        import glob
        temp_dir = "app/resource/Temp"
        # 根据抽选模式执行不同逻辑
        # 跟随全局设置
        if global_draw_mode == 1:  # 不重复抽取(直到软件重启)
            # 清理临时抽取记录文件
            if os.path.exists(temp_dir):
                for file in glob.glob(f"{temp_dir}/until_the_reboot_draw_*.json"):
                    try:
                        os.remove(file)
                        logger.info(f"已清理临时抽取记录文件: {file}")
                    except Exception as e:
                        logger.error(f"清理临时抽取记录文件失败: {e}")
            # 清理临时抽取范围记录文件            
            if os.path.exists(temp_dir):
                for file in glob.glob(f"{temp_dir}/until_the_reboot_scope_*.json"):
                    try:
                        os.remove(file)
                        logger.info(f"已清理临时抽取记录文件: {file}")
                    except Exception as e:
                        logger.error(f"清理临时抽取记录文件失败: {e}")

    # 确保菜单显示位置正确
    def contextMenuEvent(self):
        pos = self.calculate_menu_position(self.tray_menu)
        self.tray_menu.exec_(pos)

    def toggle_window(self):
        """切换窗口显示/隐藏状态"""
        if self.isVisible():
            self.hide()
        else:
            self.show()
            self.activateWindow()
            self.raise_()
            
    def calculate_menu_position(self, menu):
        """计算菜单显示位置，确保显示在鼠标右上方且不超出屏幕边界"""
        screen = QApplication.primaryScreen().availableGeometry()
        menu_size = menu.sizeHint()
        
        # 获取鼠标当前位置
        cursor_pos = QCursor.pos()
        
        # 计算菜单显示位置
        x = cursor_pos.x() + 20
        y = cursor_pos.y() - menu_size.height()
        
        # 检查是否超出屏幕边界
        if x + menu_size.width() > screen.right():
            x = screen.right() - menu_size.width()
        if y < screen.top():
            y = screen.top()
        
        return QPoint(x, y)
            
    def restart_app(self):
        """重启应用程序"""
        self.close_window_secrandom()
        os.execl(sys.executable, sys.executable, *sys.argv)

    def show_setting_interface(self):
        if not hasattr(self, 'settingInterface') or not self.settingInterface:
            self.settingInterface = settings_Window(self)
        if not self.settingInterface.isVisible():
            self.settingInterface.show()
            self.settingInterface.activateWindow()
            self.settingInterface.raise_()
            
    def toggle_levitation_window(self):
        """切换浮窗显示/隐藏状态"""
        if not hasattr(self, 'levitation_window') or not self.levitation_window:
            self.levitation_window.show()
        elif self.levitation_window.isVisible():
            self.levitation_window.hide()
        else:
            self.levitation_window.show()
            self.levitation_window.activateWindow()
            self.levitation_window.raise_()