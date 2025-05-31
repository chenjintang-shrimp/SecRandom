from qfluentwidgets import *
from qfluentwidgets import FluentIcon as fIcon
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtNetwork import *

import json
import os
import sys
import webbrowser
import subprocess
from loguru import logger

from app.common.config import YEAR, MONTH, AUTHOR, VERSION, APPLY_NAME, GITHUB_WEB, BILIBILI_WEB

if './app/Settings' != None and not os.path.exists('./app/Settings'):
    os.makedirs('./app/Settings')

from app.view.settings import settings_Window
from app.view.main_page.pumping_people import pumping_people
# from app.view.main_page.lottery import lottery
from app.view.main_page.history import history
from app.view.levitation import LevitationWindow

class Window(MSFluentWindow):
    def __init__(self):
        super().__init__()
        self.server = QLocalServer(self)
        self.server.newConnection.connect(self.handle_new_connection)
        self.server.listen("SecRandomIPC")

        self.focus_timer = QTimer(self)
        self.focus_timer.timeout.connect(self.check_focus_timeout)
        self.last_focus_time = QDateTime.currentDateTime()

        try:
            with open('app/Settings/Settings.json', 'r', encoding='utf-8') as f:
                settings = json.load(f)
                foundation_settings = settings.get('foundation', {})
                self.focus_mode = foundation_settings.get('main_window_focus_mode', 0)
        except Exception as e:
            logger.error(f"加载焦点模式设置时出错: {e}")
            self.focus_mode = 0

        try:
            with open('app/Settings/Settings.json', 'r', encoding='utf-8') as f:
                settings = json.load(f)
                foundation_settings = settings.get('foundation', {})
                self.focus_time = foundation_settings.get('main_window_focus_time', 0)
        except Exception as e:
            logger.error(f"加载检测焦点时间设置时出错: {e}")
            self.focus_time = 1

        self.focus_timeout_map = [
            0, 0, 3000, 5000, 10000, 15000, 30000, 60000, 120000, 180000, 300000, 600000, 1800000,
            2700000, 3600000, 7200000, 10800000, 21600000, 43200000
        ]

        self.focus_timeout_time = [
            0, 1000, 2000, 3000, 5000, 10000, 15000, 30000, 60000, 300000, 600000, 900000, 1800000,
            3600000, 7200000, 10800000, 21600000, 43200000
        ]

        if self.focus_time >= len(self.focus_timeout_time):
            self.focus_time = 1

        if self.focus_time == 0:
            self.focus_timer.start(0)
        else:
            self.focus_timer.start(self.focus_timeout_time[self.focus_time])

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
        # 添加关于SecRandom,点击后直接打开到到Github
        self.tray_menu.addAction(Action(QIcon("app/resource/assets/ic_fluent_info_20_filled.svg"), '关于SecRandom', triggered=self.open_github))
        self.tray_menu.addSeparator()
        self.tray_menu.addAction(Action(QIcon("app/resource/assets/ic_fluent_power_20_filled.svg"), '暂时显示/隐藏主界面', triggered=self.toggle_window))
        self.tray_menu.addAction(Action(QIcon("app/resource/assets/ic_fluent_window_ad_20_filled"), '暂时显示/隐藏浮窗', triggered=self.toggle_levitation_window))
        self.tray_menu.addAction(Action(QIcon("app/resource/assets/ic_fluent_settings_20_filled.svg"), '打开设置界面', triggered=self.show_setting_interface))
        self.tray_menu.addSeparator()
        self.tray_menu.addAction(Action(QIcon("app/resource/assets/ic_fluent_arrow_sync_20_filled.svg"), '重启', triggered=self.restart_app))
        self.tray_menu.addAction(Action(QIcon("app/resource/assets/ic_fluent_arrow_exit_20_filled.svg"), '退出', triggered=self.close_window_secrandom))

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

        self.pumping_peopleInterface = pumping_people(self)
        self.pumping_peopleInterface.setObjectName("pumping_peopleInterface")

        # self.lotteryInterface = lottery(self)
        # self.lotteryInterface.setObjectName("lotteryInterface")

        self.initNavigation()

    def initNavigation(self):
        self.addSubInterface(self.pumping_peopleInterface, QIcon("app/resource/assets/ic_fluent_people_community_20_filled.svg"), '抽人', position=NavigationItemPosition.TOP)
        # self.addSubInterface(self.lotteryInterface, QIcon("app/resource/assets/ic_fluent_reward_20_filled.svg"), '抽奖', position=NavigationItemPosition.TOP)

        self.addSubInterface(self.historyInterface, QIcon("app/resource/assets/ic_fluent_chat_history_20_filled.svg"), '历史记录', position=NavigationItemPosition.BOTTOM)

    def closeEvent(self, event):
        """窗口关闭时隐藏主界面"""
        self.hide()
        event.ignore()

    def close_window_secrandom(self):
        """关闭应用程序"""
        try:
            with open('app/SecRandom/enc_set.json', 'r', encoding='utf-8') as f:
                settings = json.load(f)
                if settings.get('hashed_set', {}).get('start_password_enabled', False) == True:
                    if settings.get('hashed_set', {}).get('exit_verification_enabled', False) == True:
                        from app.common.password_dialog import PasswordDialog
                        dialog = PasswordDialog(self)
                        if dialog.exec_() != QDialog.Accepted:
                            logger.warning("用户取消退出程序操作")
                            return
        except Exception as e:
            logger.error(f"密码验证失败: {e}")
            return

        self.hide()
        self.levitation_window.hide()
        self.stop_focus_timer()
        if hasattr(self, 'server'):
            self.server.close()
        logger.remove()
        QApplication.quit()

    def update_focus_mode(self, mode):
        """更新焦点模式"""
        self.focus_mode = mode
        self.last_focus_time = QDateTime.currentDateTime()

        if mode < len(self.focus_timeout_map):
            self.focus_timeout = self.focus_timeout_map[mode]

    def update_focus_time(self, time):
        """更新检测焦点时间"""
        self.focus_time = time
        self.last_focus_time = QDateTime.currentDateTime()
        if time < len(self.focus_timeout_time):
            self.focus_timeout = self.focus_timeout_time[time]
            self.focus_timer.start(self.focus_timeout)
        else:
            self.focus_timer.start(0)

    def check_focus_timeout(self):
        """检查窗口是否失去焦点超过设定时间"""
        if self.focus_mode == 0:  # 不关闭
            return

        if not self.isActiveWindow() and not self.isMinimized():
            elapsed = self.last_focus_time.msecsTo(QDateTime.currentDateTime())
            timeout = self.focus_timeout_map[self.focus_mode]

            if self.focus_mode == 1:  # 直接关闭
                self.hide()
            elif elapsed >= timeout:
                self.hide()
        else:
            self.last_focus_time = QDateTime.currentDateTime()

    def stop_focus_timer(self):
        """停止焦点检测计时器"""
        self.focus_timer.stop()

    def showEvent(self, event):
        """窗口显示时重置焦点时间"""
        super().showEvent(event)
        self.last_focus_time = QDateTime.currentDateTime()

    def focusInEvent(self, event):
        """窗口获得焦点时重置焦点时间"""
        super().focusInEvent(event)
        self.last_focus_time = QDateTime.currentDateTime()

    def open_github(self):
        # dialog = Dialog(
        #     '打开Github-SecRandom',
        #     '是否打开Github-SecRandom🤗',
        # )
        # dialog.yesButton.setText("打开")
        # dialog.cancelButton.setText("取消")
        # dialog.yesButton.clicked.connect(lambda: webbrowser.open(GITHUB_WEB))
        # dialog.setFixedWidth(500)
        # dialog.exec()
        webbrowser.open(GITHUB_WEB)

    def start_cleanup(self):
        """软件启动时清理临时抽取记录文件"""
        try:
            with open('app/Settings/Settings.json', 'r', encoding='utf-8') as f:
                settings = json.load(f)
                pumping_people_draw_mode = settings['pumping_people']['draw_mode']

        except Exception as e:
            pumping_people_draw_mode = 1
            logger.error(f"加载抽选模式设置时出错: {e}, 使用默认:不重复抽取(直到软件重启)模式来清理临时抽取记录文件")

        import glob
        temp_dir = "app/resource/Temp"

        if pumping_people_draw_mode == 1:  # 不重复抽取(直到软件重启)
            if os.path.exists(temp_dir):
                for file in glob.glob(f"{temp_dir}/until_the_reboot_*.json"):
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
        try:
            with open('app/SecRandom/enc_set.json', 'r', encoding='utf-8') as f:
                settings = json.load(f)
                if settings.get('hashed_set', {}).get('start_password_enabled', False) == True:
                    if settings.get('hashed_set', {}).get('restart_verification_enabled', False) == True:
                        from app.common.password_dialog import PasswordDialog
                        dialog = PasswordDialog(self)
                        if dialog.exec_() != QDialog.Accepted:
                            logger.warning("用户取消重启操作")
                            return
        except Exception as e:
            logger.error(f"密码验证失败: {e}")
            return

        self.hide()
        self.levitation_window.hide()
        self.stop_focus_timer()
        if hasattr(self, 'server'):
            self.server.close()
        logger.remove()
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
                        logger.warning("用户取消打开设置界面操作")
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
            if self.settingInterface.isMinimized():
                self.settingInterface.showNormal()
            else:
                self.settingInterface.show()
                self.settingInterface.activateWindow()
                self.settingInterface.raise_()

    def toggle_levitation_window(self):
        """切换浮窗显示/隐藏状态"""
        try:
            with open('app/SecRandom/enc_set.json', 'r', encoding='utf-8') as f:
                settings = json.load(f)
                if settings.get('hashed_set', {}).get('start_password_enabled', False) == True:
                    if settings.get('hashed_set', {}).get('show_hide_verification_enabled', False) == True:
                        from app.common.password_dialog import PasswordDialog
                        dialog = PasswordDialog(self)
                        if dialog.exec_() != QDialog.Accepted:
                            logger.warning("用户取消暂时切换浮窗显示/隐藏状态操作")
                            return
        except Exception as e:
            logger.error(f"密码验证失败: {e}")
            return

        if not hasattr(self, 'levitation_window') or not self.levitation_window:
            self.levitation_window.show()
        elif self.levitation_window.isVisible():
            self.levitation_window.hide()
        else:
            self.levitation_window.show()
            self.levitation_window.activateWindow()
            self.levitation_window.raise_()

    def handle_new_connection(self):
        """处理新连接请求"""
        socket = self.server.nextPendingConnection()
        if socket:
            socket.readyRead.connect(lambda: self.show_window_from_ipc(socket))

    def show_window_from_ipc(self, socket):
        """从IPC接收显示窗口请求"""
        socket.readAll()
        self.show()
        self.activateWindow()
        self.raise_()
        socket.disconnectFromServer()
        self.levitation_window.raise_()