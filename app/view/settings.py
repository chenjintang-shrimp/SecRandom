from qfluentwidgets import *
from qfluentwidgets import FluentIcon as fIcon
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import os
from loguru import logger

# 导入子页面
from app.view.more_setting import more_setting
from app.view.global_setting import global_setting
from app.view.extract_single_setting import single_setting
from app.view.extract_multi_setting import multi_setting
from app.view.extract_group_setting import group_setting
from app.view.Changeable_history import changeable_history
from app.view.quicksetup import quicksetup

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

        self.global_settingInterface = global_setting(self)
        self.global_settingInterface.setObjectName("global_settingInterface")

        self.single_settingInterface = single_setting(self)
        self.single_settingInterface.setObjectName("single_settingInterface")

        self.multi_settingInterface = multi_setting(self)
        self.multi_settingInterface.setObjectName("multi_settingInterface")

        self.group_settingInterface = group_setting(self)
        self.group_settingInterface.setObjectName("group_settingInterface")

        self.historyInterface = changeable_history(self)
        self.historyInterface.setObjectName("historyInterface")

        self.quicksetupInterface = quicksetup(self)
        self.quicksetupInterface.setObjectName("quicksetupInterface")

        self.initNavigation()

    def initNavigation(self):
        # 使用 MSFluentWindow 的 addSubInterface 方法
        self.addSubInterface(self.global_settingInterface, fIcon.APPLICATION, '全局设置', position=NavigationItemPosition.TOP)
        self.addSubInterface(self.single_settingInterface, fIcon.ROBOT, '抽单人设置', position=NavigationItemPosition.TOP)
        self.addSubInterface(self.multi_settingInterface, fIcon.PEOPLE, '抽多人设置', position=NavigationItemPosition.TOP)
        self.addSubInterface(self.group_settingInterface, fIcon.TILES, '抽小组设置', position=NavigationItemPosition.TOP)

        self.addSubInterface(self.historyInterface, fIcon.HISTORY, '历史记录', position=NavigationItemPosition.BOTTOM)
        self.addSubInterface(self.quicksetupInterface, fIcon.QUICK_NOTE, '名单设置', position=NavigationItemPosition.BOTTOM)
        self.addSubInterface(self.more_settingInterface, fIcon.SETTING, '更多设置', position=NavigationItemPosition.BOTTOM)

    def closeEvent(self, event):
        """窗口关闭时隐藏主界面"""
        self.hide()
        event.ignore()