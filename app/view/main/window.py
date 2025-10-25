# ==================================================
# 导入库
# ==================================================
import json
import os
import sys
import subprocess

import loguru
from loguru import logger
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtNetwork import *
from qfluentwidgets import *

from app.tools.variable import *
from app.tools.path_utils import *
from app.tools.personalised import *
from app.Language.obtain_language import *

from app.tools.extract import _is_non_class_time

from app.page_building.main_window_page import about_page
from app.view.settings.settings import SettingsWindow

# ==================================================
# 主窗口类
# ==================================================
class MainWindow(MSFluentWindow):
    """主窗口类
    程序的核心控制中心"""
    
    # 定义信号，用于请求显示设置窗口
    showSettingsRequested = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        # 设置窗口对象名称，方便其他组件查找
        self.setObjectName("MainWindow")

        # resize_timer的初始化
        self.resize_timer = QTimer(self)
        self.resize_timer.setSingleShot(True)
        self.resize_timer.timeout.connect(lambda: self.save_window_size(self.width(), self.height()))

        # 设置窗口属性
        window_width = 800
        window_height = 600
        self.resize(window_width, window_height)
        self.setMinimumSize(MINIMUM_WINDOW_SIZE[0], MINIMUM_WINDOW_SIZE[1])
        self.setWindowTitle('SecRandom')
        self.setWindowIcon(QIcon(str(get_resources_path('assets/icon', 'secrandom-icon-paper.png'))))

        self._position_window()
        
        QTimer.singleShot(APP_INIT_DELAY, lambda: (
            self.createSubInterface()
        ))

    def _position_window(self):
        """窗口定位
        根据屏幕尺寸和用户设置自动计算最佳位置"""
        screen = QApplication.primaryScreen()
        desktop = screen.availableGeometry()
        w, h = desktop.width(), desktop.height()

        target_x = w // 2 - self.width() // 2
        target_y = h // 2 - self.height() // 2
        
        self.move(target_x, target_y)

    def _apply_window_visibility_settings(self):
        """应用窗口显示设置
        根据用户保存的设置决定窗口是否显示"""
        try:
            self.show()
        except Exception as e:
            logger.error(f"加载窗口显示设置失败: {e}")

    def createSubInterface(self):
        """创建子界面
        搭建子界面导航系统"""
        self.settingsInterface = QWidget(self)
        self.settingsInterface.setObjectName("settingsInterface")

        self.aboutInterface = about_page(self)
        self.aboutInterface.setObjectName("aboutInterface")

        # self.pumping_peopleInterface = pumping_people(self)
        # self.pumping_peopleInterface.setObjectName("pumping_peopleInterface")

        # self.pumping_rewardInterface = pumping_reward(self)
        # self.pumping_rewardInterface.setObjectName("pumping_rewardInterface")

        # self.history_handoff_settingInterface = history_handoff_setting(self)
        # self.history_handoff_settingInterface.setObjectName('history_handoff_settingInterface')

        self.initNavigation()

    def initNavigation(self):
        """初始化导航系统
        根据用户设置构建个性化菜单导航"""
        # self.addSubInterface(self.pumping_peopleInterface, get_theme_icon("ic_fluent_people_community_20_filled"), '点名', position=NavigationItemPosition.TOP)

        # self.addSubInterface(self.pumping_rewardInterface, get_theme_icon("ic_fluent_reward_20_filled"), '抽奖', position=NavigationItemPosition.TOP)

        # self.addSubInterface(self.history_handoff_settingInterface, get_theme_icon("ic_fluent_chat_history_20_filled"), '历史记录', position=NavigationItemPosition.BOTTOM)
        
        self.addSubInterface(self.aboutInterface, get_theme_icon("ic_fluent_info_20_filled"), '关于', position=NavigationItemPosition.BOTTOM)

        settings_item = self.addSubInterface(self.settingsInterface, get_theme_icon("ic_fluent_settings_20_filled"), '设置', position=NavigationItemPosition.BOTTOM)
        settings_item.clicked.connect(self.showSettingsRequested.emit)

    def closeEvent(self, event):
        """窗口关闭事件处理
        拦截窗口关闭事件，隐藏窗口并保存窗口大小"""
        self.hide()
        event.ignore()
        self.save_window_size(self.width(), self.height())

    def resizeEvent(self, event):
        """窗口大小变化事件处理
        检测窗口大小变化，但不启动尺寸记录倒计时，减少IO操作"""
        self.resize_timer.start(500)
        super().resizeEvent(event)

    def save_window_size(self, width, height):
        """保存窗口大小
        记录当前窗口尺寸，下次启动时自动恢复"""
        self.window_size = (width, height)
        self.save()

    def toggle_window(self):
        """切换窗口显示状态
        在显示和隐藏状态之间切换窗口，切换时自动激活点名界面"""
        if self.isVisible():
            self.hide()
            if self.isMinimized():
                self.showNormal()
                self.activateWindow()
                self.raise_()
        else:
            if self.isMinimized():
                self.showNormal()
                self.activateWindow()
                self.raise_()
            else:
                self.show()
                self.activateWindow()
                self.raise_()

    def close_window_secrandom(self):
        """关闭窗口
        执行安全验证后关闭程序，释放所有资源"""
        try:
            loguru.logger.remove()
        except Exception as e:
            logger.error(f"日志系统关闭出错: {e}")

        QApplication.quit()
        sys.exit(0)

    def restart_app(self):
        """重启应用程序
        执行安全验证后重启程序，清理所有资源"""
        try:
            working_dir = str(get_app_root())
            
            filtered_args = [arg for arg in sys.argv if not arg.startswith('--')]
            
            startup_info = subprocess.STARTUPINFO()
            startup_info.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            
            subprocess.Popen(
                [sys.executable] + filtered_args,
                cwd=working_dir,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS,
                startupinfo=startup_info
            )
        except Exception as e:
            logger.error(f"启动新进程失败: {e}")
            return

        try:
            loguru.logger.remove()
        except Exception as e:
            logger.error(f"日志系统关闭出错: {e}")
        
        # 完全退出当前应用程序
        QApplication.quit()
        sys.exit(0)
