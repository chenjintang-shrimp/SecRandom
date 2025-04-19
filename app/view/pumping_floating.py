from qfluentwidgets import *
from qfluentwidgets import FluentIcon as fIcon
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import os
from loguru import logger

# 导入子页面
from app.view.multiplayer import multiplayer

class pumping_floating_window(MSFluentWindow):
    def __init__(self):
        super().__init__()
        try:
            with open('app/Settings/Settings.json', 'r', encoding='utf-8') as f:
                settings = json.load(f)
                foundation_settings = settings.get('foundation', {})
                convenient_window_size = foundation_settings.get('convenient_window_size', 0)
                if convenient_window_size == 0:
                    self.resize(800, 600)
                elif convenient_window_size == 1:
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
        self.setWindowTitle('SecRandom - 浮窗便捷抽取')
        self.setWindowIcon(QIcon('./app/resource/icon/SecRandom.png'))

        # 获取主屏幕
        screen = QApplication.primaryScreen()
        # 获取屏幕的可用几何信息
        desktop = screen.availableGeometry()
        w, h = desktop.width(), desktop.height()
        try:
            with open('app/Settings/Settings.json', 'r', encoding='utf-8') as f:
                settings = json.load(f)
                convenient_window_mode = settings['foundation']['convenient_window_mode']
                if convenient_window_mode == 0:
                    self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)
                elif convenient_window_mode == 1:
                    self.move(w // 2 - self.width() // 2, h * 3 // 5 - self.height() // 2)
        except FileNotFoundError:
            logger.error(f"加载设置时出错: {e}, 使用默认窗口居中显示便捷抽人窗口")
            self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)

        self.createSubInterface()

    def createSubInterface(self):
        self.pumping_floating_Interface = multiplayer(self)
        self.pumping_floating_Interface.setObjectName("pumping_floating_Interface")

        self.initNavigation()

    def initNavigation(self):
        # 使用 MSFluentWindow 的 addSubInterface 方法
        self.addSubInterface(self.pumping_floating_Interface, fIcon.PEOPLE, '抽人', position=NavigationItemPosition.TOP)

    def closeEvent(self, event):
        """窗口关闭时隐藏主界面"""
        self.hide()
        event.ignore()