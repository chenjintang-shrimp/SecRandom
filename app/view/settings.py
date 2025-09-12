from qfluentwidgets import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import os
import json
from loguru import logger

from app.common.config import get_theme_icon, load_custom_font
from app.common.path_utils import path_manager
from app.common.path_utils import open_file, ensure_dir

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
        self.app_dir = path_manager._app_root
        self.resize_timer = QTimer(self)
        self.resize_timer.setSingleShot(True)
        self.resize_timer.timeout.connect(self.save_settings_window_size)

        settings_path = path_manager.get_settings_path()
        try:
            with open_file(settings_path, 'r', encoding='utf-8') as f:
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
        self.setWindowIcon(QIcon(str(path_manager.get_resource_path('icon', 'SecRandom.png'))))

        # 获取主屏幕
        screen = QApplication.primaryScreen()
        # 获取屏幕的可用几何信息
        desktop = screen.availableGeometry()
        w, h = desktop.width(), desktop.height()
        try:
            with open_file(settings_path, 'r', encoding='utf-8') as f:
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

        try:
            self.more_settingInterface = more_setting(self)
            self.more_settingInterface.setObjectName("more_settingInterface")
            logger.debug("设置界面: 更多设置界面创建成功")
        except Exception as e:
            logger.error(f"设置界面: 创建更多设置界面失败: {e}")
            self.more_settingInterface = None

        try:
            self.plugin_settingsInterface = PluginSettingsWindow(self)
            self.plugin_settingsInterface.setObjectName("plugin_settingsInterface")
            logger.debug("设置界面: 插件设置界面创建成功")
        except Exception as e:
            logger.error(f"设置界面: 创建插件设置界面失败: {e}")
            self.plugin_settingsInterface = None

        try:
            self.pumping_handoff_settingInterface = pumping_handoff_setting(self)
            self.pumping_handoff_settingInterface.setObjectName("pumping_handoff_settingInterface")
            logger.debug("设置界面: 抽取设置界面创建成功")
        except Exception as e:
            logger.error(f"设置界面: 创建抽取设置界面失败: {e}")
            self.pumping_handoff_settingInterface = None

        try:
            self.changeable_history_handoff_settingInterface = changeable_history_handoff_setting(self)
            self.changeable_history_handoff_settingInterface.setObjectName("changeable_history_handoff_settingInterface")
            logger.debug("设置界面: 历史记录设置界面创建成功")
        except Exception as e:
            logger.error(f"设置界面: 创建历史记录设置界面失败: {e}")
            self.changeable_history_handoff_settingInterface = None

        try:
            self.about_settingInterface = about(self)
            self.about_settingInterface.setObjectName("about_settingInterface")
            logger.debug("设置界面: 关于界面创建成功")
        except Exception as e:
            logger.error(f"设置界面: 创建关于界面失败: {e}")
            self.about_settingInterface = None

        try:
            self.password_setInterface = password_set(self)
            self.password_setInterface.setObjectName("password_setInterface")
            logger.debug("设置界面: 安全设置界面创建成功")
        except Exception as e:
            logger.error(f"设置界面: 创建安全设置界面失败: {e}")
            self.password_setInterface = None

        try:
            self.voice_engine_settingsInterface = voice_engine_settings(self)
            self.voice_engine_settingsInterface.setObjectName("voice_engine_settingsInterface")
            logger.debug("设置界面: 语音设置界面创建成功")
        except Exception as e:
            logger.error(f"设置界面: 创建语音设置界面失败: {e}")
            self.voice_engine_settingsInterface = None

        self.initNavigation()

    def initNavigation(self):
        # 使用 MSFluentWindow 的 addSubInterface 方法
        if self.pumping_handoff_settingInterface is not None:
            self.addSubInterface(self.pumping_handoff_settingInterface, get_theme_icon("ic_fluent_people_community_20_filled"), '抽取设置', position=NavigationItemPosition.TOP)
        else:
            logger.error("设置界面导航: 抽取设置界面不存在，无法添加到导航栏")

        if self.plugin_settingsInterface is not None:
            self.addSubInterface(self.plugin_settingsInterface, get_theme_icon("ic_fluent_extensions_20_filled"), '插件', position=NavigationItemPosition.BOTTOM)
        else:
            logger.error("设置界面导航: 插件设置界面不存在，无法添加到导航栏")

        if self.voice_engine_settingsInterface is not None:
            self.addSubInterface(self.voice_engine_settingsInterface, get_theme_icon("ic_fluent_person_voice_20_filled"), '语音设置', position=NavigationItemPosition.BOTTOM)
        else:
            logger.error("设置界面导航: 语音设置界面不存在，无法添加到导航栏")

        if self.password_setInterface is not None:
            self.addSubInterface(self.password_setInterface, get_theme_icon("ic_fluent_shield_keyhole_20_filled"), '安全设置', position=NavigationItemPosition.BOTTOM)
        else:
            logger.error("设置界面导航: 安全设置界面不存在，无法添加到导航栏")

        if self.changeable_history_handoff_settingInterface is not None:
            history_item = self.addSubInterface(self.changeable_history_handoff_settingInterface, get_theme_icon("ic_fluent_chat_history_20_filled"), '历史记录', position=NavigationItemPosition.BOTTOM)
            history_item.clicked.connect(lambda: self.changeable_history_handoff_settingInterface.pumping_people_card.load_data())
        else:
            logger.error("设置界面导航: 历史记录设置界面不存在，无法添加到导航栏")

        if self.about_settingInterface is not None:
            self.addSubInterface(self.about_settingInterface, get_theme_icon("ic_fluent_info_20_filled"), '关于', position=NavigationItemPosition.BOTTOM)
        else:
            logger.error("设置界面导航: 关于界面不存在，无法添加到导航栏")

        if self.more_settingInterface is not None:
            self.addSubInterface(self.more_settingInterface, get_theme_icon("ic_fluent_more_horizontal_20_filled"), '更多设置', position=NavigationItemPosition.BOTTOM)
        else:
            logger.error("设置界面导航: 更多设置界面不存在，无法添加到导航栏")

    def closeEvent(self, event):
        """窗口关闭时隐藏主界面"""
        # 停止resize_timer以优化CPU占用
        if hasattr(self, 'resize_timer') and self.resize_timer.isActive():
            self.resize_timer.stop()
            logger.info("设置窗口resize_timer已停止")
        
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
                settings_path = path_manager.get_settings_path()
                # 读取现有设置
                try:
                    with open_file(settings_path, 'r', encoding='utf-8') as f:
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
                ensure_dir(settings_path.parent)
                with open_file(settings_path, 'w', encoding='utf-8') as f:
                    json.dump(settings, f, ensure_ascii=False, indent=4)
            except Exception as e:
                logger.error(f"保存窗口大小设置失败: {e}")
    
    def show_plugin_settings_interface(self):
        """(^・ω・^ ) 白露的插件设置界面召唤魔法！
        通过URL协议打开插件设置界面，让用户可以管理插件相关设置～
        会自动切换到插件设置界面，方便用户进行插件管理！🔌✨
        """
        logger.info(f"白露URL: 正在打开插件设置界面～")
        
        try:
            # 确保设置窗口可见
            if not self.isVisible():
                self.show()
                self.activateWindow()
                self.raise_()
            
            # 如果窗口最小化，则恢复
            if self.isMinimized():
                self.showNormal()
            
            # 检查插件设置界面是否存在
            if self.plugin_settingsInterface is not None:
                # 切换到插件设置界面
                self.stackedWidget.setCurrentWidget(self.plugin_settingsInterface)
                logger.info(f"白露URL: 插件设置界面已成功打开～")
            else:
                logger.error(f"白露URL: 插件设置界面不存在，无法打开～")
                # 尝试重新创建插件设置界面
                try:
                    self.plugin_settingsInterface = PluginSettingsWindow(self)
                    self.plugin_settingsInterface.setObjectName("plugin_settingsInterface")
                    logger.debug("设置界面: 插件设置界面重新创建成功")
                    # 重新初始化导航
                    self.initNavigation()
                    # 切换到插件设置界面
                    self.stackedWidget.setCurrentWidget(self.plugin_settingsInterface)
                    logger.info(f"白露URL: 插件设置界面重新创建并成功打开～")
                except Exception as e:
                    logger.error(f"白露URL: 重新创建插件设置界面失败: {e}")
        except Exception as e:
            logger.error(f"白露URL: 打开插件设置界面时发生异常: {e}")
