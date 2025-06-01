from qfluentwidgets import *
from qfluentwidgets import FluentIcon as fIcon
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import os
from loguru import logger

# 导入子页面
from app.view.settings_page.more_setting import more_setting
from app.view.settings_page.Changeable_history_handoff_setting import changeable_history_handoff_setting
from app.view.settings_page.password_setting import password_set
from app.view.settings_page.about_setting import about
from app.view.settings_page.pumping_handoff_setting import pumping_handoff_setting

class settings_Window(MSFluentWindow):
    def __init__(self, parent=None):
        super().__init__()
        try:
            with open('app/Settings/Settings.json', 'r', encoding='utf-8') as f:
                settings = json.load(f)
                foundation_settings = settings.get('foundation', {})
                settings_window_size = foundation_settings.get('settings_window_size', 0)
                if settings_window_size == 0:
                    self.resize(800, 600)
                elif settings_window_size == 1:
                    self.resize(1200, 800)
                else:
                    self.resize(800, 600)
        except FileNotFoundError as e:
            logger.error(f"加载设置时出错: {e}, 使用默认大小:800x600")
            self.resize(800, 600)
        except KeyError:
            logger.error(f"设置文件中缺少'foundation'键, 使用默认大小:800x600")
            self.resize(800, 600)
        self.setMinimumSize(600, 400)
        self.setWindowTitle('SecRandom - 设置')
        self.setWindowIcon(QIcon('./app/resource/icon/SecRandom.png'))

        # 获取主屏幕
        screen = QApplication.primaryScreen()
        # 获取屏幕的可用几何信息
        desktop = screen.availableGeometry()
        w, h = desktop.width(), desktop.height()
        try:
            with open('app/Settings/Settings.json', 'r', encoding='utf-8') as f:
                settings = json.load(f)
                foundation_settings = settings.get('foundation', {})
                settings_window_mode = foundation_settings.get('settings_window_mode', 0)
                if settings_window_mode == 0:
                    self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)
                elif settings_window_mode == 1:
                    self.move(w // 2 - self.width() // 2, h * 3 // 5 - self.height() // 2)
        except FileNotFoundError as e:
            logger.error(f"加载设置时出错: {e}, 使用默认窗口居中显示设置界面")
            self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)

        self.createSubInterface()

    def createSubInterface(self):
        loop = QEventLoop(self)
        QTimer.singleShot(1, loop.quit)
        loop.exec()

        self.more_settingInterface = more_setting(self)
        self.more_settingInterface.setObjectName("more_settingInterface")

        self.pumping_handoff_settingInterface = pumping_handoff_setting(self)
        self.pumping_handoff_settingInterface.setObjectName("pumping_handoff_settingInterface")

        self.changeable_history_handoff_settingInterface = changeable_history_handoff_setting(self)
        self.changeable_history_handoff_settingInterface.setObjectName("changeable_history_handoff_settingInterface")

        self.about_settingInterface = about(self)
        self.about_settingInterface.setObjectName("about_settingInterface")

        self.password_setInterface = password_set(self)
        self.password_setInterface.setObjectName("password_setInterface")

        self.initNavigation()

    def initNavigation(self):
        # 使用 MSFluentWindow 的 addSubInterface 方法
        self.addSubInterface(self.pumping_handoff_settingInterface, QIcon("app/resource/assets/ic_fluent_people_community_20_filled.svg"), '抽取设置', position=NavigationItemPosition.TOP)

        self.addSubInterface(self.password_setInterface, QIcon("app/resource/assets/ic_fluent_shield_keyhole_20_filled.svg"), '安全设置', position=NavigationItemPosition.BOTTOM)
        self.addSubInterface(self.changeable_history_handoff_settingInterface, QIcon("app/resource/assets/ic_fluent_chat_history_20_filled.svg"), '历史记录', position=NavigationItemPosition.BOTTOM)
        self.addSubInterface(self.about_settingInterface, QIcon("app/resource/assets/ic_fluent_info_20_filled.svg"), '关于', position=NavigationItemPosition.BOTTOM)
        self.addSubInterface(self.more_settingInterface, QIcon("app/resource/assets/ic_fluent_more_horizontal_20_filled.svg"), '更多设置', position=NavigationItemPosition.BOTTOM)

    def closeEvent(self, event):
        """窗口关闭时隐藏主界面"""
        self.hide()
        event.ignore()
