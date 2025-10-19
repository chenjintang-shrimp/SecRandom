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

# ==================================================
# 高级安全设置
# ==================================================
class advanced_safety_settings(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # 创建垂直布局
        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout.setSpacing(10)

        # 添加强力防删除设置组件
        self.strong_protection_widget = advanced_safety_strong_protection(self)
        self.vBoxLayout.addWidget(self.strong_protection_widget)

        # 添加数据加密设置组件
        self.data_encryption_widget = advanced_safety_data_encryption(self)
        self.vBoxLayout.addWidget(self.data_encryption_widget)


class advanced_safety_strong_protection(GroupHeaderCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(get_setting_name("advanced_safety_settings", "strong_protection"))
        self.setBorderRadius(8)

        # 是否启动软件自我保护功能开关
        self.encryption_strong_switch = SwitchButton()
        self.encryption_strong_switch.setOffText(get_setting_switchbutton_name("advanced_safety_settings", "encryption_strong_switch", "disable"))
        self.encryption_strong_switch.setOnText(get_setting_switchbutton_name("advanced_safety_settings", "encryption_strong_switch", "enable"))
        self.encryption_strong_switch.setChecked(readme_settings("advanced_safety_settings", "encryption_strong_switch"))
        self.encryption_strong_switch.checkedChanged.connect(lambda: update_settings("advanced_safety_settings", "encryption_strong_switch", self.encryption_strong_switch.isChecked()))
        self.encryption_strong_switch.setFont(QFont(load_custom_font(), 12))

        # 选择强力防删除程度模式
        self.encryption_strong_mode_combo = ComboBox()
        self.encryption_strong_mode_combo.addItems(get_setting_combo_name("advanced_safety_settings", "encryption_strong_mode"))
        self.encryption_strong_mode_combo.setCurrentIndex(readme_settings("advanced_safety_settings", "encryption_strong_mode"))
        self.encryption_strong_mode_combo.currentIndexChanged.connect(lambda: update_settings("advanced_safety_settings", "encryption_strong_mode", self.encryption_strong_mode_combo.currentIndex()))
        self.encryption_strong_mode_combo.setFont(QFont(load_custom_font(), 12))

        # 是否开启强力防删除名单开关
        self.strong_list_switch = SwitchButton()
        self.strong_list_switch.setOffText(get_setting_switchbutton_name("advanced_safety_settings", "strong_list_switch", "disable"))
        self.strong_list_switch.setOnText(get_setting_switchbutton_name("advanced_safety_settings", "strong_list_switch", "enable"))
        self.strong_list_switch.setChecked(readme_settings("advanced_safety_settings", "strong_list_switch"))
        self.strong_list_switch.checkedChanged.connect(lambda: update_settings("advanced_safety_settings", "strong_list_switch", self.strong_list_switch.isChecked()))
        self.strong_list_switch.setFont(QFont(load_custom_font(), 12))

        # 是否开启强力防删除历史记录开关
        self.strong_history_switch = SwitchButton()
        self.strong_history_switch.setOffText(get_setting_switchbutton_name("advanced_safety_settings", "strong_history_switch", "disable"))
        self.strong_history_switch.setOnText(get_setting_switchbutton_name("advanced_safety_settings", "strong_history_switch", "enable"))
        self.strong_history_switch.setChecked(readme_settings("advanced_safety_settings", "strong_history_switch"))
        self.strong_history_switch.checkedChanged.connect(lambda: update_settings("advanced_safety_settings", "strong_history_switch", self.strong_history_switch.isChecked()))
        self.strong_history_switch.setFont(QFont(load_custom_font(), 12))

        # 是否开启强力防删除临时已抽取记录开关
        self.strong_temp_switch = SwitchButton()
        self.strong_temp_switch.setOffText(get_setting_switchbutton_name("advanced_safety_settings", "strong_temp_switch", "disable"))
        self.strong_temp_switch.setOnText(get_setting_switchbutton_name("advanced_safety_settings", "strong_temp_switch", "enable"))
        self.strong_temp_switch.setChecked(readme_settings("advanced_safety_settings", "strong_temp_switch"))
        self.strong_temp_switch.checkedChanged.connect(lambda: update_settings("advanced_safety_settings", "strong_temp_switch", self.strong_temp_switch.isChecked()))
        self.strong_temp_switch.setFont(QFont(load_custom_font(), 12))

        # 添加设置项到分组
        self.addGroup(get_theme_icon("ic_fluent_lock_closed_key_20_filled"), 
                        get_setting_name("advanced_safety_settings", "encryption_strong_switch"), get_setting_description("advanced_safety_settings", "encryption_strong_switch"), self.encryption_strong_switch)
        self.addGroup(get_theme_icon("ic_fluent_haptic_strong_20_filled"), 
                        get_setting_name("advanced_safety_settings", "encryption_strong_mode"), get_setting_description("advanced_safety_settings", "encryption_strong_mode"), self.encryption_strong_mode_combo)
        self.addGroup(get_theme_icon("ic_fluent_document_bullet_list_clock_20_filled"), 
                        get_setting_name("advanced_safety_settings", "strong_list_switch"), get_setting_description("advanced_safety_settings", "strong_list_switch"), self.strong_list_switch)
        self.addGroup(get_theme_icon("ic_fluent_document_data_lock_20_filled"), 
                        get_setting_name("advanced_safety_settings", "strong_history_switch"), get_setting_description("advanced_safety_settings", "strong_history_switch"), self.strong_history_switch)
        self.addGroup(get_theme_icon("ic_fluent_document_lock_20_filled"), 
                        get_setting_name("advanced_safety_settings", "strong_temp_switch"), get_setting_description("advanced_safety_settings", "strong_temp_switch"), self.strong_temp_switch)


class advanced_safety_data_encryption(GroupHeaderCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(get_setting_name("advanced_safety_settings", "data_encryption"))
        self.setBorderRadius(8)

        # 是否开启名单加密开关
        self.encryption_list_switch = SwitchButton()
        self.encryption_list_switch.setOffText(get_setting_switchbutton_name("advanced_safety_settings", "encryption_list_switch", "disable"))
        self.encryption_list_switch.setOnText(get_setting_switchbutton_name("advanced_safety_settings", "encryption_list_switch", "enable"))
        self.encryption_list_switch.setChecked(readme_settings("advanced_safety_settings", "encryption_list_switch"))
        self.encryption_list_switch.checkedChanged.connect(lambda: update_settings("advanced_safety_settings", "encryption_list_switch", self.encryption_list_switch.isChecked()))
        self.encryption_list_switch.setFont(QFont(load_custom_font(), 12))

        # 是否开启历史记录文件加密开关
        self.encryption_history_switch = SwitchButton()
        self.encryption_history_switch.setOffText(get_setting_switchbutton_name("advanced_safety_settings", "encryption_history_switch", "disable"))
        self.encryption_history_switch.setOnText(get_setting_switchbutton_name("advanced_safety_settings", "encryption_history_switch", "enable"))
        self.encryption_history_switch.setChecked(readme_settings("advanced_safety_settings", "encryption_history_switch"))
        self.encryption_history_switch.checkedChanged.connect(lambda: update_settings("advanced_safety_settings", "encryption_history_switch", self.encryption_history_switch.isChecked()))
        self.encryption_history_switch.setFont(QFont(load_custom_font(), 12))

        # 是否开启临时已抽取记录加密开关
        self.encryption_temp_switch = SwitchButton()
        self.encryption_temp_switch.setOffText(get_setting_switchbutton_name("advanced_safety_settings", "encryption_temp_switch", "disable"))
        self.encryption_temp_switch.setOnText(get_setting_switchbutton_name("advanced_safety_settings", "encryption_temp_switch", "enable"))
        self.encryption_temp_switch.setChecked(readme_settings("advanced_safety_settings", "encryption_temp_switch"))
        self.encryption_temp_switch.checkedChanged.connect(lambda: update_settings("advanced_safety_settings", "encryption_temp_switch", self.encryption_temp_switch.isChecked()))
        self.encryption_temp_switch.setFont(QFont(load_custom_font(), 12))

        # 添加设置项到分组
        self.addGroup(get_theme_icon("ic_fluent_document_bullet_list_clock_20_filled"), 
                        get_setting_name("advanced_safety_settings", "encryption_list_switch"), get_setting_description("advanced_safety_settings", "encryption_list_switch"), self.encryption_list_switch)
        self.addGroup(get_theme_icon("ic_fluent_document_data_lock_20_filled"), 
                        get_setting_name("advanced_safety_settings", "encryption_history_switch"), get_setting_description("advanced_safety_settings", "encryption_history_switch"), self.encryption_history_switch)
        self.addGroup(get_theme_icon("ic_fluent_document_lock_20_filled"), 
                        get_setting_name("advanced_safety_settings", "encryption_temp_switch"), get_setting_description("advanced_safety_settings", "encryption_temp_switch"), self.encryption_temp_switch)
