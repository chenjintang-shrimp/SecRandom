# ==================================================
# 导入库
# ==================================================
import json
import os
import sys
import subprocess

from loguru import logger
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtNetwork import *
from qfluentwidgets import *

from app.tools.variable import *
from app.tools.path_utils import *
from app.tools.personalised import *
from app.tools.settings_default import *
from app.tools.settings_access import *
from app.Language.obtain_language import *

# ==================================================
# 基本设置
# ==================================================
class basic_settings(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # 创建垂直布局
        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout.setSpacing(10)

        # 添加基本功能设置组件
        self.basic_function_widget = basic_settings_function(self)
        self.vBoxLayout.addWidget(self.basic_function_widget)

        # 添加数据管理组件
        self.data_management_widget = basic_settings_data_management(self)
        self.vBoxLayout.addWidget(self.data_management_widget)

        # 添加个性化设置组件
        self.personalised_widget = basic_settings_personalised(self)
        self.vBoxLayout.addWidget(self.personalised_widget)

class basic_settings_function(GroupHeaderCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(get_content_name("basic_settings", "basic_function"))
        self.setBorderRadius(8)

        # 开机自启设置
        self.autostart_switch = SwitchButton()
        self.autostart_switch.setOffText(get_content_switchbutton_name("basic_settings", "autostart", "disable"))
        self.autostart_switch.setOnText(get_content_switchbutton_name("basic_settings", "autostart", "enable"))
        self.autostart_switch.setChecked(readme_settings("basic_settings", "autostart"))
        self.autostart_switch.checkedChanged.connect(lambda: update_settings("basic_settings", "autostart", self.autostart_switch.isChecked()))

        # 自动检查更新设置
        self.check_update_switch = SwitchButton()
        self.check_update_switch.setOffText(get_content_switchbutton_name("basic_settings", "check_update", "disable"))
        self.check_update_switch.setOnText(get_content_switchbutton_name("basic_settings", "check_update", "enable"))
        self.check_update_switch.setChecked(readme_settings("basic_settings", "check_update"))
        self.check_update_switch.checkedChanged.connect(lambda: update_settings("basic_settings", "check_update", self.check_update_switch.isChecked()))

        # 显示启动窗口设置
        self.show_startup_window_switch = SwitchButton()
        self.show_startup_window_switch.setOffText(get_content_switchbutton_name("basic_settings", "show_startup_window", "disable"))
        self.show_startup_window_switch.setOnText(get_content_switchbutton_name("basic_settings", "show_startup_window", "enable"))
        self.show_startup_window_switch.setChecked(readme_settings("basic_settings", "show_startup_window"))
        self.show_startup_window_switch.checkedChanged.connect(lambda: update_settings("basic_settings", "show_startup_window", self.show_startup_window_switch.isChecked()))

        # 添加设置项到分组
        self.addGroup(get_theme_icon("ic_fluent_arrow_sync_20_filled"), 
                        get_content_name("basic_settings", "autostart"), get_content_description("basic_settings", "autostart"), self.autostart_switch)
        self.addGroup(get_theme_icon("ic_fluent_cloud_sync_20_filled"), 
                        get_content_name("basic_settings", "check_update"), get_content_description("basic_settings", "check_update"), self.check_update_switch)
        self.addGroup(get_theme_icon("ic_fluent_window_play_20_filled"), 
                        get_content_name("basic_settings", "show_startup_window"), get_content_description("basic_settings", "show_startup_window"), self.show_startup_window_switch)

class basic_settings_data_management(GroupHeaderCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(get_content_name("basic_settings", "data_management"))
        self.setBorderRadius(8)

        # 导出诊断数据按钮
        self.export_diagnostic_data_button = PushButton(get_content_pushbutton_name("basic_settings", "export_diagnostic_data"))
        self.export_diagnostic_data_button.clicked.connect(lambda: self.export_diagnostic_data())

        # 导出设置按钮
        self.export_settings_button = PushButton(get_content_pushbutton_name("basic_settings", "export_settings"))
        self.export_settings_button.clicked.connect(lambda: self.export_settings())

        # 导入设置按钮
        self.import_settings_button = PushButton(get_content_pushbutton_name("basic_settings", "import_settings"))
        self.import_settings_button.clicked.connect(lambda: self.import_settings())

        # 导出软件所有数据按钮
        self.export_all_data_button = PushButton(get_content_pushbutton_name("basic_settings", "export_all_data"))
        self.export_all_data_button.clicked.connect(lambda: self.export_all_data())

        # 导入软件所有数据按钮
        self.import_all_data_button = PushButton(get_content_pushbutton_name("basic_settings", "import_all_data"))
        self.import_all_data_button.clicked.connect(lambda: self.import_all_data())

        # 添加设置项到分组
        self.addGroup(get_theme_icon("ic_fluent_database_arrow_down_20_filled"), 
                        get_content_name("basic_settings", "export_diagnostic_data"), get_content_description("basic_settings", "export_diagnostic_data"), self.export_diagnostic_data_button)
        self.addGroup(get_theme_icon("ic_fluent_arrow_clockwise_dashes_settings_20_filled"), 
                        get_content_name("basic_settings", "export_settings"), get_content_description("basic_settings", "export_settings"), self.export_settings_button)
        self.addGroup(get_theme_icon("ic_fluent_arrow_clockwise_dashes_settings_20_filled"), 
                        get_content_name("basic_settings", "import_settings"), get_content_description("basic_settings", "import_settings"), self.import_settings_button)
        self.addGroup(get_theme_icon("ic_fluent_database_window_20_filled"), 
                        get_content_name("basic_settings", "export_all_data"), get_content_description("basic_settings", "export_all_data"), self.export_all_data_button)
        self.addGroup(get_theme_icon("ic_fluent_database_window_20_filled"), 
                        get_content_name("basic_settings", "import_all_data"), get_content_description("basic_settings", "import_all_data"), self.import_all_data_button)

class basic_settings_personalised(GroupHeaderCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(get_content_name("basic_settings", "personalised"))
        self.setBorderRadius(8)

        # 主题色
        self.theme_color_button = ColorConfigItem("Theme", "Color", readme_settings("basic_settings", "theme"))

        # 添加设置项到分组

        self.themeColorCard = ColorSettingCard(
            self.theme_color_button,    
            get_theme_icon("ic_fluent_text_color_20_filled"),
            self.tr(get_content_name("basic_settings", "theme")),
            self.tr(get_content_description("basic_settings", "theme")),
            self
        )

        self.vBoxLayout.addWidget(self.themeColorCard)
