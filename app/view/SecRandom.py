from qfluentwidgets import *
from qfluentwidgets import FluentIcon as fIcon
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtNetwork import *

import json
import os
import sys
import subprocess
from urllib.parse import urlparse, parse_qs
from loguru import logger

from app.common.config import YEAR, MONTH, AUTHOR, VERSION, APPLY_NAME, GITHUB_WEB, BILIBILI_WEB
from app.common.config import get_theme_icon, load_custom_font, check_for_updates, get_update_channel
import warnings
from urllib3.exceptions import InsecureRequestWarning
warnings.filterwarnings('ignore', category=InsecureRequestWarning)

if './app/Settings' != None and not os.path.exists('./app/Settings'):
    os.makedirs('./app/Settings')

from app.view.settings import settings_Window
from app.view.main_page.pumping_people import pumping_people
from app.view.main_page.pumping_reward import pumping_reward
from app.view.main_page.history_handoff_setting import history_handoff_setting
from app.view.levitation import LevitationWindow
from app.view.settings_page.about_setting import about

def show_update_notification(latest_version):
    """显示自定义更新通知窗口"""
    try:
        from app.common.update_notification import UpdateNotification
        import sys

        # 确保有应用实例
        if QApplication.instance() is None:
            app = QApplication(sys.argv)
        else:
            app = QApplication.instance()

        # 创建并显示通知窗口
        notification = UpdateNotification(latest_version)
        notification.show()
        # 防止通知窗口关闭时程序退出
        original_quit_setting = app.quitOnLastWindowClosed()
        app.setQuitOnLastWindowClosed(False)
        notification.destroyed.connect(lambda: app.setQuitOnLastWindowClosed(original_quit_setting))
        logger.info(f"自定义更新通知已显示，版本: {latest_version}")

    except ImportError as e:
        logger.error(f"导入自定义通知失败: {str(e)}")
    except Exception as e:
        logger.error(f"显示更新通知失败: {str(e)}", exc_info=True)

class Window(MSFluentWindow):
    def __init__(self):
        super().__init__()
        self.server = QLocalServer(self)
        self.server.newConnection.connect(self.handle_new_connection)
        self.server.listen("SecRandomIPC")

        self.focus_timer = QTimer(self)
        self.focus_timer.timeout.connect(self.check_focus_timeout)
        self.last_focus_time = QDateTime.currentDateTime()

        self.resize_timer = QTimer(self)
        self.resize_timer.setSingleShot(True)
        self.resize_timer.timeout.connect(self.save_window_size)

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
            self.focus_time = 0

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
                # 读取保存的窗口大小，默认为800x600
                window_width = foundation_settings.get('window_width', 800)
                window_height = foundation_settings.get('window_height', 600)
                self.resize(window_width, window_height)
        except FileNotFoundError as e:
            logger.error(f"加载设置时出错: {e}, 使用默认大小:800x600")
            self.resize(800, 600)
        except Exception as e:
            logger.error(f"加载窗口大小设置失败: {e}, 使用默认大小:800x600")
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
        # 添加关于SecRandom,点击后打开主界面的关于选项卡
        self.tray_menu.addAction(Action(get_theme_icon("ic_fluent_info_20_filled"), '关于SecRandom', triggered=self.show_about_tab))
        self.tray_menu.addSeparator()
        self.tray_menu.addAction(Action(get_theme_icon("ic_fluent_power_20_filled"), '暂时显示/隐藏主界面', triggered=self.toggle_window))
        self.tray_menu.addAction(Action(get_theme_icon("ic_fluent_window_ad_20_filled"), '暂时显示/隐藏浮窗', triggered=self.toggle_levitation_window))
        self.tray_menu.addAction(Action(get_theme_icon("ic_fluent_settings_20_filled"), '打开设置界面', triggered=self.show_setting_interface))
        self.tray_menu.addSeparator()
        self.tray_menu.addAction(Action(get_theme_icon("ic_fluent_arrow_sync_20_filled"), '重启', triggered=self.restart_app))
        self.tray_menu.addAction(Action(get_theme_icon("ic_fluent_arrow_exit_20_filled"), '退出', triggered=self.close_window_secrandom))

        self.tray_icon.show()
        self.tray_icon.activated.connect(self.trayIconActivated)

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
                check_startup = settings.get('foundation', {}).get('check_on_startup', True)
            if settings.get('toggle_window') == 'show':
                self.show()
        except Exception as e:
            logger.error(f"无法加载设置文件: {e}")
            check_startup = True

        self.createSubInterface()
        self.splashScreen.finish()

        if check_startup:
            QTimer.singleShot(1000, self.check_updates_async)

    class UpdateCheckWorker(QThread):
        result_ready = pyqtSignal(bool, str)
        
        def run(self):
            channel = get_update_channel()
            update_available, latest_version = check_for_updates(channel)
            self.result_ready.emit(update_available, latest_version)
    
    def check_updates_async(self):
        self.update_worker = self.UpdateCheckWorker()
        self.update_worker.result_ready.connect(self.on_update_check_finished)
        self.update_worker.start()
    
    def on_update_check_finished(self, update_available, latest_version):
        if update_available and latest_version:
            show_update_notification(latest_version)
        self.update_worker.deleteLater()

    def createSubInterface(self):
        loop = QEventLoop(self)
        QTimer.singleShot(1, loop.quit)
        loop.exec()

        self.settingInterface = settings_Window(self)
        self.settingInterface.setObjectName("settingInterface")

        self.history_handoff_settingInterface = history_handoff_setting(self)
        self.history_handoff_settingInterface.setObjectName("history_handoff_settingInterface")

        self.pumping_peopleInterface = pumping_people(self)
        self.pumping_peopleInterface.setObjectName("pumping_peopleInterface")

        self.about_settingInterface = about(self)
        self.about_settingInterface.setObjectName("about_settingInterface")

        self.pumping_rewardInterface = pumping_reward(self)
        self.pumping_rewardInterface.setObjectName("pumping_rewardInterface")

        self.initNavigation()

    def initNavigation(self):
        try:
            with open('app/Settings/Settings.json', 'r', encoding='utf-8') as f:
                settings = json.load(f)
                foundation_settings = settings.get('foundation', {})
                if foundation_settings.get('pumping_floating_side', 0) == 1:
                    self.addSubInterface(self.pumping_peopleInterface, get_theme_icon("ic_fluent_people_community_20_filled"), '抽人', position=NavigationItemPosition.BOTTOM)
                else:
                    self.addSubInterface(self.pumping_peopleInterface, get_theme_icon("ic_fluent_people_community_20_filled"), '抽人', position=NavigationItemPosition.TOP)
                if foundation_settings.get('pumping_reward_side', 0) == 1:
                    self.addSubInterface(self.pumping_rewardInterface, get_theme_icon("ic_fluent_reward_20_filled"), '抽奖', position=NavigationItemPosition.BOTTOM)
                else:
                    self.addSubInterface(self.pumping_rewardInterface, get_theme_icon("ic_fluent_reward_20_filled"), '抽奖', position=NavigationItemPosition.TOP)
        except FileNotFoundError as e:
            logger.error(f"加载设置时出错: {e}, 使用默认顶部显示抽人功能")
            self.addSubInterface(self.pumping_peopleInterface, get_theme_icon("ic_fluent_people_community_20_filled"), '抽人', position=NavigationItemPosition.TOP)
            self.addSubInterface(self.pumping_rewardInterface, get_theme_icon("ic_fluent_reward_20_filled"), '抽奖', position=NavigationItemPosition.TOP)

        self.addSubInterface(self.history_handoff_settingInterface, get_theme_icon("ic_fluent_chat_history_20_filled"), '历史记录', position=NavigationItemPosition.BOTTOM)
        self.addSubInterface(self.about_settingInterface, get_theme_icon("ic_fluent_info_20_filled"), '关于', position=NavigationItemPosition.BOTTOM)

    def closeEvent(self, event):
        """窗口关闭时隐藏主界面"""
        self.hide()
        event.ignore()
        self.save_window_size()

    def resizeEvent(self, event):
        # 调整大小时重启计时器，仅在停止调整后保存
        self.resize_timer.start(500)  # 500毫秒延迟
        super().resizeEvent(event)

    def save_window_size(self):
        if not self.isMaximized():
            try:
                # 读取现有设置
                try:
                    with open('app/Settings/Settings.json', 'r', encoding='utf-8') as f:
                        settings = json.load(f)
                except FileNotFoundError:
                    settings = {}
                
                # 确保foundation键存在
                if 'foundation' not in settings:
                    settings['foundation'] = {}
                
                # 更新窗口大小设置
                settings['foundation']['window_width'] = self.width()
                settings['foundation']['window_height'] = self.height()
                
                # 保存设置
                with open('app/Settings/Settings.json', 'w', encoding='utf-8') as f:
                    json.dump(settings, f, ensure_ascii=False, indent=4)
            except Exception as e:
                logger.error(f"保存窗口大小设置失败: {e}")

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
        if hasattr(self, 'levitation_window'):
            self.levitation_window.hide()
        if hasattr(self, 'focus_timer'):
            self.stop_focus_timer()
        if hasattr(self, 'server'):
            self.server.close()
        # 关闭共享内存
        if hasattr(self, 'shared_memory'):
            self.shared_memory.detach()
            logger.info("共享内存已关闭")
        logger.remove()
        # 确保完全退出应用程序
        QApplication.quit()
        sys.exit(0)

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

    def show_about_tab(self):
        """显示主界面的关于选项卡"""
        if self.isMinimized():
            self.showNormal()
        else:
            self.show()
            self.activateWindow()
            self.raise_()
        self.switchTo(self.about_settingInterface)

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

    def trayIconActivated(self, reason):
        if reason in (QSystemTrayIcon.Trigger, QSystemTrayIcon.Context):
            pos = QCursor.pos()
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
        self.switchTo(self.pumping_peopleInterface)

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
            logger.error(f"密码验证过程出错: {e}")
        try:
            self.hide()
            if hasattr(self, 'levitation_window'):
                self.levitation_window.hide()
            # 清理定时器资源
            if hasattr(self, 'focus_timer'):
                self.stop_focus_timer()
                self.focus_timer.deleteLater()
            if hasattr(self, 'server'):
                self.server.close()
        except Exception as e:
            logger.error(f"重启前清理资源失败: {e}")
        # 关闭共享内存
        if hasattr(self, 'shared_memory'):
            self.shared_memory.detach()
            logger.info("共享内存已关闭")
        logger.remove()
        # 使用新进程组启动，避免被当前进程退出影响
        subprocess.Popen([sys.executable] + sys.argv, creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
        # 退出当前进程
        sys.exit(0)

    def show_setting_interface(self, target_page=None):
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
                
        # 如果指定了目标页面，则切换到对应设置子页面
        if target_page:
            # 根据页面参数切换到不同设置子界面
            if target_page == 'pumping':
                self.settingInterface.stackedWidget.setCurrentWidget(self.settingInterface.pumping_handoff_settingInterface)
            elif target_page == 'security':
                self.settingInterface.stackedWidget.setCurrentWidget(self.settingInterface.password_setInterface)
            elif target_page == 'history':
                self.settingInterface.stackedWidget.setCurrentWidget(self.settingInterface.changeable_history_handoff_settingInterface)
            elif target_page == 'about':
                self.settingInterface.stackedWidget.setCurrentWidget(self.settingInterface.about_settingInterface)
            elif target_page == 'more':
                self.settingInterface.stackedWidget.setCurrentWidget(self.settingInterface.more_settingInterface)

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
            socket.disconnected.connect(socket.deleteLater)

    def show_window_from_ipc(self, socket):
        """从IPC接收显示窗口请求并激活窗口"""
        data = socket.readAll().data().decode().strip()
        logger.info(f"接收到IPC窗口显示请求: {data}")
        
        # 确保主窗口资源正确加载并显示
        self.show()
        self.activateWindow()
        self.raise_()
        
        # 处理悬浮窗口
        self._handle_levitation_window()
        
        socket.disconnectFromServer()

    def _handle_levitation_window(self):
        """处理悬浮窗口激活"""
        if hasattr(self, 'levitation_window') and self.levitation_window:
            self.levitation_window.raise_()
            self.levitation_window.activateWindow()
    
    def _handle_pump_path(self, query_params):
        """处理抽人路径逻辑并返回目标界面"""
        pump_type = query_params.get('type', [None])[0]
        if pump_type == 'reward':
            logger.debug(f"切换到奖励抽选界面: {pump_type}")
            return self.pumping_rewardInterface
        return self.pumping_peopleInterface
    
    def switch_history_tab(self, pump_type):
        """根据页面类型切换历史记录界面"""
        if pump_type == 'setting_history':
            self.show_setting_interface('history')
        elif pump_type == 'main_history':
            self.history_handoff_settingInterface()
        
    def _handle_settings_path(self, query_params):
        """处理设置路径逻辑并返回设置界面"""
        settings_page = query_params.get('page', [None])[0]
        self.show_setting_interface(settings_page)
        logger.debug(f"打开设置界面: {settings_page or '默认页面'}")
        return self.show_setting_interface('pumping')