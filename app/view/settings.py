from qfluentwidgets import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import os
from loguru import logger

from app.common.config import get_theme_icon, load_custom_font

# 导入子页面
from app.view.settings_page.more_setting import more_setting
from app.view.settings_page.Changeable_history_handoff_setting import changeable_history_handoff_setting
from app.view.settings_page.password_setting import password_set
from app.view.settings_page.about_setting import about
from app.view.settings_page.pumping_handoff_setting import pumping_handoff_setting
from app.view.settings_page.voice_engine_setting import voice_engine_settings
from app.view.plugins.plugin_settings import PluginSettingsWindow


class settings_Window(MSFluentWindow):
    def __init__(self, parent=None):
        super().__init__()
        self.resize_timer = QTimer(self)
        self.resize_timer.setSingleShot(True)
        self.resize_timer.timeout.connect(self.save_settings_window_size)

        try:
            with open('app/Settings/Settings.json', 'r', encoding='utf-8') as f:
                settings = json.load(f)
                foundation_settings = settings.get('foundation', {})
                # 读取保存的窗口大小，默认为800x600
                window_width = foundation_settings.get('settings_window_width', 800)
                window_height = foundation_settings.get('settings_window_height', 600)
                self.resize(window_width, window_height)
        except FileNotFoundError as e:
            logger.error(f"加载设置时出错: {e}, 使用默认大小:800x600")
            self.resize(800, 600)
        except Exception as e:
            logger.error(f"加载窗口大小设置失败: {e}, 使用默认大小:800x600")
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

        self.plugin_settingsInterface = PluginSettingsWindow(self)
        self.plugin_settingsInterface.setObjectName("plugin_settingsInterface")

        self.pumping_handoff_settingInterface = pumping_handoff_setting(self)
        self.pumping_handoff_settingInterface.setObjectName("pumping_handoff_settingInterface")

        self.changeable_history_handoff_settingInterface = changeable_history_handoff_setting(self)
        self.changeable_history_handoff_settingInterface.setObjectName("changeable_history_handoff_settingInterface")

        self.about_settingInterface = about(self)
        self.about_settingInterface.setObjectName("about_settingInterface")

        self.password_setInterface = password_set(self)
        self.password_setInterface.setObjectName("password_setInterface")

        self.voice_engine_settingsInterface = voice_engine_settings(self)
        self.voice_engine_settingsInterface.setObjectName("voice_engine_settingsInterface")

        self.initNavigation()

    def initNavigation(self):
        # 使用 MSFluentWindow 的 addSubInterface 方法
        self.addSubInterface(self.pumping_handoff_settingInterface, get_theme_icon("ic_fluent_people_community_20_filled"), '抽取设置', position=NavigationItemPosition.TOP)

        self.addSubInterface(self.plugin_settingsInterface, get_theme_icon("ic_fluent_extensions_20_filled"), '插件广场', position=NavigationItemPosition.BOTTOM)
        self.addSubInterface(self.voice_engine_settingsInterface, get_theme_icon("ic_fluent_person_voice_20_filled"), '语音设置', position=NavigationItemPosition.BOTTOM)
        self.addSubInterface(self.password_setInterface, get_theme_icon("ic_fluent_shield_keyhole_20_filled"), '安全设置', position=NavigationItemPosition.BOTTOM)
        history_item = self.addSubInterface(self.changeable_history_handoff_settingInterface, get_theme_icon("ic_fluent_chat_history_20_filled"), '历史记录', position=NavigationItemPosition.BOTTOM)
        history_item.clicked.connect(lambda: self.changeable_history_handoff_settingInterface.pumping_people_card.load_data())

        self.addSubInterface(self.about_settingInterface, get_theme_icon("ic_fluent_info_20_filled"), '关于', position=NavigationItemPosition.BOTTOM)
        self.addSubInterface(self.more_settingInterface, get_theme_icon("ic_fluent_more_horizontal_20_filled"), '更多设置', position=NavigationItemPosition.BOTTOM)

    def closeEvent(self, event):
        """窗口关闭时隐藏主界面"""
        self.hide()
        event.ignore()
        self.save_settings_window_size()

    def resizeEvent(self, event):
        # 调整大小时重启计时器，仅在停止调整后保存
        self.resize_timer.start(500)  # 500毫秒延迟
        super().resizeEvent(event)

    def save_settings_window_size(self):
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
                settings['foundation']['settings_window_width'] = self.width()
                settings['foundation']['settings_window_height'] = self.height()
                
                # 保存设置
                with open('app/Settings/Settings.json', 'w', encoding='utf-8') as f:
                    json.dump(settings, f, ensure_ascii=False, indent=4)
            except Exception as e:
                logger.error(f"保存窗口大小设置失败: {e}")