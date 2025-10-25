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
# 点名通知设置
# ==================================================
class roll_call_notification_settings(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # 创建垂直布局
        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout.setSpacing(10)

        # 添加基础设置组件
        self.basic_settings_widget = basic_settings(self)
        self.vBoxLayout.addWidget(self.basic_settings_widget)

        # 添加窗口模式设置组件
        self.window_mode_widget = window_mode(self)
        self.vBoxLayout.addWidget(self.window_mode_widget)
        
        # 添加浮窗模式设置组件
        self.floating_window_widget = floating_window_settings(self)
        self.vBoxLayout.addWidget(self.floating_window_widget)          

class basic_settings(GroupHeaderCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(get_content_name("roll_call_notification_settings", "basic_settings"))
        self.setBorderRadius(8)
        
        # 选择通知模式下拉框
        self.notification_mode_combo_box = ComboBox()
        self.notification_mode_combo_box.addItems(get_content_combo_name("roll_call_notification_settings", "notification_mode"))
        self.notification_mode_combo_box.setCurrentText(get_content_name("roll_call_notification_settings", "notification_mode"))
        self.notification_mode_combo_box.currentIndexChanged.connect(lambda: update_settings("roll_call_notification_settings", "notification_mode", self.notification_mode_combo_box.currentIndex()))

        # 是否开启动画开关
        self.animation_switch = SwitchButton()
        self.animation_switch.setOffText(get_content_name("roll_call_notification_settings", "animation_off"))
        self.animation_switch.setOnText(get_content_name("roll_call_notification_settings", "animation_on"))
        self.animation_switch.setChecked(get_settings("roll_call_notification_settings", "animation"))
        self.animation_switch.checkedChanged.connect(lambda: update_settings("roll_call_notification_settings", "animation", self.animation_switch.isChecked()))

class window_mode(GroupHeaderCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(get_content_name("roll_call_notification_settings", "window_mode"))
        self.setBorderRadius(8)
        
        # 设置窗口的显示位置下拉框
        self.window_position_combo_box = ComboBox()
        self.window_position_combo_box.addItems(get_content_combo_name("roll_call_notification_settings", "window_position"))
        self.window_position_combo_box.setCurrentText(get_content_name("roll_call_notification_settings", "window_position"))
        self.window_position_combo_box.currentIndexChanged.connect(lambda: update_settings("roll_call_notification_settings", "window_position", self.window_position_combo_box.currentIndex()))

        # 水平偏移值
        self.horizontal_offset_spin_spinbox = SpinBox()
        self.horizontal_offset_spin_spinbox.setRange(-25600, 25600)
        self.horizontal_offset_spin_spinbox.setSuffix("px")
        self.horizontal_offset_spin_spinbox.setValue(get_settings("roll_call_notification_settings", "horizontal_offset"))
        self.horizontal_offset_spin_spinbox.valueChanged.connect(lambda: update_settings("roll_call_notification_settings", "horizontal_offset", self.horizontal_offset_spin_spinbox.value()))

        # 垂直偏移值
        self.vertical_offset_spin_spinbox = SpinBox()
        self.vertical_offset_spin_spinbox.setRange(-25600, 25600)
        self.vertical_offset_spin_spinbox.setSuffix("px")
        self.vertical_offset_spin_spinbox.setValue(get_settings("roll_call_notification_settings", "vertical_offset"))
        self.vertical_offset_spin_spinbox.valueChanged.connect(lambda: update_settings("roll_call_notification_settings", "vertical_offset", self.vertical_offset_spin_spinbox.value()))

        # 窗口透明度
        self.window_transparency_spin_spinbox = SpinBox()
        self.window_transparency_spin_spinbox.setRange(0, 100)
        self.window_transparency_spin_spinbox.setSuffix("%")
        self.window_transparency_spin_spinbox.setValue(get_settings("roll_call_notification_settings", "transparency"))
        self.window_transparency_spin_spinbox.valueChanged.connect(lambda: update_settings("roll_call_notification_settings", "transparency", self.window_transparency_spin_spinbox.value()))

        # 选择启用的第一个显示器下拉框
        self.enabled_first_monitor_combo_box = ComboBox()
        self.enabled_first_monitor_combo_box.addItems(self.get_monitor_list())
        self.enabled_first_monitor_combo_box.setCurrentText(get_content_name("roll_call_notification_settings", "enabled_first_monitor"))
        self.enabled_first_monitor_combo_box.currentIndexChanged.connect(lambda: update_settings("roll_call_notification_settings", "enabled_first_monitor", self.enabled_first_monitor_combo_box.currentIndex()))

        # 选择启用的第一个显示器的窗口位置组合
        self.enabled_first_monitor_window_position_combo_box = ComboBox()
        self.enabled_first_monitor_window_position_combo_box.addItems(get_content_combo_name("roll_call_notification_settings", "enabled_first_monitor_window_position"))
        self.enabled_first_monitor_window_position_combo_box.setCurrentText(get_content_name("roll_call_notification_settings", "enabled_first_monitor_window_position"))
        self.enabled_first_monitor_window_position_combo_box.currentIndexChanged.connect(lambda: update_settings("roll_call_notification_settings", "enabled_first_monitor_window_position", self.enabled_first_monitor_window_position_combo_box.currentIndex()))

        # 选择启用的第二个显示器下拉框
        self.enabled_second_monitor_combo_box = ComboBox()
        self.enabled_second_monitor_combo_box.addItems(["OFF"] + self.get_monitor_list())
        self.enabled_second_monitor_combo_box.setCurrentText(get_content_name("roll_call_notification_settings", "enabled_second_monitor"))
        self.enabled_second_monitor_combo_box.currentIndexChanged.connect(lambda: update_settings("roll_call_notification_settings", "enabled_second_monitor", self.enabled_second_monitor_combo_box.currentIndex()))

        # 选择启用的第二个显示器的窗口位置组合
        self.enabled_second_monitor_window_position_combo_box = ComboBox()
        self.enabled_second_monitor_window_position_combo_box.addItems(get_content_combo_name("roll_call_notification_settings", "enabled_second_monitor_window_position"))
        self.enabled_second_monitor_window_position_combo_box.setCurrentText(get_content_name("roll_call_notification_settings", "enabled_second_monitor_window_position"))
        self.enabled_second_monitor_window_position_combo_box.currentIndexChanged.connect(lambda: update_settings("roll_call_notification_settings", "enabled_second_monitor_window_position", self.enabled_second_monitor_window_position_combo_box.currentIndex()))

        # 选择启用的第三个显示器下拉框
        self.enabled_third_monitor_combo_box = ComboBox()
        self.enabled_third_monitor_combo_box.addItems(["OFF"] + self.get_monitor_list())
        self.enabled_third_monitor_combo_box.setCurrentText(get_content_name("roll_call_notification_settings", "enabled_third_monitor"))
        self.enabled_third_monitor_combo_box.currentIndexChanged.connect(lambda: update_settings("roll_call_notification_settings", "enabled_third_monitor", self.enabled_third_monitor_combo_box.currentIndex()))

        # 选择启用的第三个显示器的窗口位置组合
        self.enabled_third_monitor_window_position_combo_box = ComboBox()
        self.enabled_third_monitor_window_position_combo_box.addItems(get_content_combo_name("roll_call_notification_settings", "enabled_third_monitor_window_position"))
        self.enabled_third_monitor_window_position_combo_box.setCurrentText(get_content_name("roll_call_notification_settings", "enabled_third_monitor_window_position"))
        self.enabled_third_monitor_window_position_combo_box.currentIndexChanged.connect(lambda: update_settings("roll_call_notification_settings", "enabled_third_monitor_window_position", self.enabled_third_monitor_window_position_combo_box.currentIndex()))

    # 获取显示器列表
    def get_monitor_list(self):
        monitor_list = []
        for screen in QApplication.instance().screens():
            monitor_list.append(screen.name())
        return monitor_list

class floating_window_settings(GroupHeaderCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(get_content_name("roll_call_notification_settings", "floating_window_mode"))
        self.setBorderRadius(8)
        
        # 窗口透明度
        self.window_transparency_spin_spinbox = SpinBox()
        self.window_transparency_spin_spinbox.setRange(0, 100)
        self.window_transparency_spin_spinbox.setSuffix("%")
        self.window_transparency_spin_spinbox.setValue(get_settings("roll_call_notification_settings", "transparency"))
        self.window_transparency_spin_spinbox.valueChanged.connect(lambda: update_settings("roll_call_notification_settings", "transparency", self.window_transparency_spin_spinbox.value()))

        # 选择启用的第一个显示器下拉框
        self.enabled_first_monitor_combo_box = ComboBox()
        self.enabled_first_monitor_combo_box.addItems(self.get_monitor_list())
        self.enabled_first_monitor_combo_box.setCurrentText(get_content_name("roll_call_notification_settings", "enabled_first_monitor"))
        self.enabled_first_monitor_combo_box.currentIndexChanged.connect(lambda: update_settings("roll_call_notification_settings", "enabled_first_monitor", self.enabled_first_monitor_combo_box.currentIndex()))

        # 选择启用的第一个显示器的窗口位置组合
        self.enabled_first_monitor_window_position_combo_box = ComboBox()
        self.enabled_first_monitor_window_position_combo_box.addItems(get_content_combo_name("roll_call_notification_settings", "enabled_first_monitor_window_position"))
        self.enabled_first_monitor_window_position_combo_box.setCurrentText(get_content_name("roll_call_notification_settings", "enabled_first_monitor_window_position"))
        self.enabled_first_monitor_window_position_combo_box.currentIndexChanged.connect(lambda: update_settings("roll_call_notification_settings", "enabled_first_monitor_window_position", self.enabled_first_monitor_window_position_combo_box.currentIndex()))

        # 选择启用的第二个显示器下拉框
        self.enabled_second_monitor_combo_box = ComboBox()
        self.enabled_second_monitor_combo_box.addItems(["OFF"] + self.get_monitor_list())
        self.enabled_second_monitor_combo_box.setCurrentText(get_content_name("roll_call_notification_settings", "enabled_second_monitor"))
        self.enabled_second_monitor_combo_box.currentIndexChanged.connect(lambda: update_settings("roll_call_notification_settings", "enabled_second_monitor", self.enabled_second_monitor_combo_box.currentIndex()))

        # 选择启用的第二个显示器的窗口位置组合
        self.enabled_second_monitor_window_position_combo_box = ComboBox()
        self.enabled_second_monitor_window_position_combo_box.addItems(get_content_combo_name("roll_call_notification_settings", "enabled_second_monitor_window_position"))
        self.enabled_second_monitor_window_position_combo_box.setCurrentText(get_content_name("roll_call_notification_settings", "enabled_second_monitor_window_position"))
        self.enabled_second_monitor_window_position_combo_box.currentIndexChanged.connect(lambda: update_settings("roll_call_notification_settings", "enabled_second_monitor_window_position", self.enabled_second_monitor_window_position_combo_box.currentIndex()))

        # 选择启用的第三个显示器下拉框
        self.enabled_third_monitor_combo_box = ComboBox()
        self.enabled_third_monitor_combo_box.addItems(["OFF"] + self.get_monitor_list())
        self.enabled_third_monitor_combo_box.setCurrentText(get_content_name("roll_call_notification_settings", "enabled_third_monitor"))
        self.enabled_third_monitor_combo_box.currentIndexChanged.connect(lambda: update_settings("roll_call_notification_settings", "enabled_third_monitor", self.enabled_third_monitor_combo_box.currentIndex()))

        # 选择启用的第三个显示器的窗口位置组合
        self.enabled_third_monitor_window_position_combo_box = ComboBox()
        self.enabled_third_monitor_window_position_combo_box.addItems(get_content_combo_name("roll_call_notification_settings", "_enabled_third_monitor_window_position"))
        self.enabled_third_monitor_window_position_combo_box.setCurrentText(get_content_name("roll_call_notification_settings", "enabled_third_monitor_window_position"))
        self.enabled_third_monitor_window_position_combo_box.currentIndexChanged.connect(lambda: update_settings("roll_call_notification_settings", "enabled_third_monitor_window_position", self.enabled_third_monitor_window_position_combo_box.currentIndex()))

    # 获取显示器列表
    def get_monitor_list(self):
        monitor_list = []
        for screen in QApplication.instance().screens():
            monitor_list.append(screen.name())
        return monitor_list
