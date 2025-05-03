from qfluentwidgets import *
from qfluentwidgets import FluentIcon as fIcon
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

import json
import os
import sys
from loguru import logger

if './app/Settings' != None and not os.path.exists('./app/Settings'):
    os.makedirs('./app/Settings')

if './app/resource/group' != None and not os.path.exists('./app/resource/group'):
    os.makedirs('./app/resource/group')

from app.view.settings import settings_Window
from app.view.single import single
from app.view.multiplayer import multiplayer
from app.view.group import groupplayer
from app.view.history import history
from app.view.levitation import LevitationWindow

class Window(MSFluentWindow):
    def __init__(self):
        super().__init__()
        try:
            with open('app/Settings/Settings.json', 'r', encoding='utf-8') as f:
                settings = json.load(f)
                foundation_settings = settings.get('foundation', {})
                main_window_size = foundation_settings.get('main_window_size', 0)
                if main_window_size == 0:
                    self.resize(800, 600)
                elif main_window_size == 1:
                    self.resize(1200, 800)
                else:
                    self.resize(800, 600)
        except FileNotFoundError as e:
            logger.error(f"加载设置时出错: {e}, 使用默认大小:800x600")
            self.resize(800, 600)
        except KeyError:
            logger.error(f"设置文件中缺少foundation键, 使用默认大小:800x600")
            self.resize(800, 600)
        self.setMinimumSize(600, 400)
        self.setWindowTitle('SecRandom')
        self.setWindowIcon(QIcon('./app/resource/icon/SecRandom.png'))
        self.start_cleanup()
        self.levitation_window = LevitationWindow()
        try:
            with open('app/Settings/Settings.json', 'r', encoding='utf-8') as f:
                settings = json.load(f)
                foundation_settings = settings.get('foundation', {})
                pumping_floating_enabled = foundation_settings.get('pumping_floating_enabled', True)
                if pumping_floating_enabled:
                    self.levitation_window.show()
        except FileNotFoundError as e:
            logger.error(f"加载设置时出错: {e}, 使用默认显示浮窗功能")
            self.levitation_window.show()
        except KeyError:
            logger.error(f"设置文件中缺少foundation键, 使用默认显示浮窗功能")
            self.levitation_window.show()

        # 系统托盘
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon('./app/resource/icon/SecRandom.png'))
        self.tray_icon.setToolTip('SecRandom')
        self.tray_menu = RoundMenu(parent=self)
        self.tray_menu.addAction(Action(fIcon.POWER_BUTTON, '暂时显示/隐藏主界面', triggered=self.toggle_window))
        self.tray_menu.addAction(Action(QIcon("app\\resource\\icon\\SecRandom_floating_100%.png"), '暂时显示/隐藏浮窗', triggered=self.toggle_levitation_window))
        self.tray_menu.addAction(Action(fIcon.SETTING, '打开设置界面', triggered=self.show_setting_interface))
        self.tray_menu.addAction(Action(fIcon.SYNC, '重启', triggered=self.restart_app))
        self.tray_menu.addAction(Action(fIcon.CLOSE, '退出', triggered=self.close_window_secrandom))

        self.tray_icon.show()
        self.tray_icon.activated.connect(self.contextMenuEvent)

        screen = QApplication.primaryScreen()
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
        logger.info("应用程序已退出")
        logger.remove()
        QApplication.quit()

    def start_cleanup(self):
        """软件启动时清理临时抽取记录文件"""
        try:
            with open('app/Settings/Settings.json', 'r', encoding='utf-8') as f:
                settings = json.load(f)
                global_draw_mode = settings['global']['draw_mode']

        except Exception as e:
            global_draw_mode = 1
            logger.error(f"加载抽选模式设置时出错: {e}, 使用默认:不重复抽取(直到软件重启)模式来清理临时抽取记录文件")

        import glob
        temp_dir = "app/resource/Temp"

        if global_draw_mode == 1:  # 不重复抽取(直到软件重启)
            if os.path.exists(temp_dir):
                for file in glob.glob(f"{temp_dir}/until_the_reboot_draw_*.json"):
                    try:
                        os.remove(file)
                        logger.info(f"已清理临时抽取记录文件: {file}")
                    except Exception as e:
                        logger.error(f"清理临时抽取记录文件失败: {e}")
            if os.path.exists(temp_dir):
                for file in glob.glob(f"{temp_dir}/until_the_reboot_scope_*.json"):
                    try:
                        os.remove(file)
                        logger.info(f"已清理临时抽取记录文件: {file}")
                    except Exception as e:
                        logger.error(f"清理临时抽取记录文件失败: {e}")

    def contextMenuEvent(self):
        pos = self.calculate_menu_position(self.tray_menu)
        self.tray_menu.exec_(pos)

    def toggle_window(self):
        """切换窗口显示/隐藏状态"""  
        if self.isVisible():
            self.hide()
            if self.isMinimized():
                self.showNormal()
        else:
            if self.isMinimized():
                self.showNormal()
            else:
                self.show()
                self.activateWindow()
                self.raise_()

    def calculate_menu_position(self, menu):
        """计算菜单显示位置"""
        screen = QApplication.primaryScreen().availableGeometry()
        menu_size = menu.sizeHint()

        cursor_pos = QCursor.pos()

        x = cursor_pos.x() + 20
        y = cursor_pos.y() - menu_size.height()

        if x + menu_size.width() > screen.right():
            x = screen.right() - menu_size.width()
        if y < screen.top():
            y = screen.top()

        return QPoint(x, y)

    def restart_app(self):
        self.hide()
        logger.info("重启程序")
        logger.remove()
        self.tray_icon.hide()
        os.execl(sys.executable, sys.executable, *sys.argv)

    def show_setting_interface(self):
        """显示设置界面"""
        try:
            with open('app/SecRandom/enc_set.json', 'r', encoding='utf-8') as f:
                settings = json.load(f)
                if settings.get('hashed_set', {}).get('start_password_enabled', False):
                    from app.common.password_dialog import PasswordDialog
                    dialog = PasswordDialog(self)
                    if dialog.exec_() != QDialog.Accepted:
                        return
        except Exception as e:
            logger.error(f"密码验证失败: {e}")

        try:
            with open('app/SecRandom/enc_set.json', 'r', encoding='utf-8') as f:
                settings = json.load(f)
            settings['hashed_set']['verification_start'] = True
            with open('app/SecRandom/enc_set.json', 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=4)
        except Exception as e:
            logger.error(f"写入verification_start失败: {e}")

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