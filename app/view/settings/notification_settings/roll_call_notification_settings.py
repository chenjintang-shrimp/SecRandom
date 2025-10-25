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
        self.animation_switch.setOffText(get_content_switchbutton_name("roll_call_notification_settings", "animation", "disable"))
        self.animation_switch.setOnText(get_content_switchbutton_name("roll_call_notification_settings", "animation", "enable"))
        self.animation_switch.setChecked(readme_settings("roll_call_notification_settings", "animation"))
        self.animation_switch.checkedChanged.connect(lambda: update_settings("roll_call_notification_settings", "animation", self.animation_switch.isChecked()))

        # 添加设置项到分组
        self.addGroup(get_theme_icon("ic_fluent_comment_20_filled"), 
                        get_content_name("roll_call_notification_settings", "notification_mode"), get_content_description("roll_call_notification_settings", "notification_mode"), self.notification_mode_combo_box)
        self.addGroup(get_theme_icon("ic_fluent_sanitize_20_filled"), 
                        get_content_name("roll_call_notification_settings", "animation"), get_content_description("roll_call_notification_settings", "animation"), self.animation_switch)

class window_mode(GroupHeaderCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(get_content_name("roll_call_notification_settings", "window_mode"))
        self.setBorderRadius(8)
        
        # 设置窗口的显示位置下拉框
        self.window_position_combo_box = ComboBox()
        self.window_position_combo_box.addItems(get_content_combo_name("roll_call_notification_settings", "window_position"))
        self.window_position_combo_box.setCurrentIndex(readme_settings("roll_call_notification_settings", "window_position"))
        self.window_position_combo_box.currentIndexChanged.connect(lambda: update_settings("roll_call_notification_settings", "window_position", self.window_position_combo_box.currentIndex()))

        # 水平偏移值
        self.horizontal_offset_spin_spinbox = SpinBox()
        self.horizontal_offset_spin_spinbox.setFixedWidth(WIDTH_SPINBOX)
        self.horizontal_offset_spin_spinbox.setRange(-25600, 25600)
        self.horizontal_offset_spin_spinbox.setSuffix("px")
        self.horizontal_offset_spin_spinbox.setValue(readme_settings("roll_call_notification_settings", "horizontal_offset"))
        self.horizontal_offset_spin_spinbox.valueChanged.connect(lambda: update_settings("roll_call_notification_settings", "horizontal_offset", self.horizontal_offset_spin_spinbox.value()))

        # 垂直偏移值
        self.vertical_offset_spin_spinbox = SpinBox()
        self.vertical_offset_spin_spinbox.setFixedWidth(WIDTH_SPINBOX)
        self.vertical_offset_spin_spinbox.setRange(-25600, 25600)
        self.vertical_offset_spin_spinbox.setSuffix("px")
        self.vertical_offset_spin_spinbox.setValue(readme_settings("roll_call_notification_settings", "vertical_offset"))
        self.vertical_offset_spin_spinbox.valueChanged.connect(lambda: update_settings("roll_call_notification_settings", "vertical_offset", self.vertical_offset_spin_spinbox.value()))

        # 窗口透明度
        self.window_transparency_spin_spinbox = SpinBox()
        self.window_transparency_spin_spinbox.setFixedWidth(WIDTH_SPINBOX)
        self.window_transparency_spin_spinbox.setRange(0, 100)
        self.window_transparency_spin_spinbox.setSuffix("%")
        self.window_transparency_spin_spinbox.setValue(readme_settings("roll_call_notification_settings", "transparency") * 100)
        self.window_transparency_spin_spinbox.valueChanged.connect(lambda: update_settings("roll_call_notification_settings", "transparency", self.window_transparency_spin_spinbox.value() / 100))

        # 选择启用的第一个显示器下拉框
        self.enabled_first_monitor_combo_box = ComboBox()
        self.enabled_first_monitor_combo_box.addItems(self.get_monitor_list())
        if readme_settings("roll_call_notification_settings", "enabled_first_monitor") == "OFF":
            self.enabled_first_monitor_combo_box.setCurrentText(self.get_monitor_list()[0])
            update_settings("roll_call_notification_settings", "enabled_first_monitor", self.enabled_first_monitor_combo_box.currentText())
        self.enabled_first_monitor_combo_box.setCurrentText(readme_settings("roll_call_notification_settings", "enabled_first_monitor"))
        self.enabled_first_monitor_combo_box.currentTextChanged.connect(lambda: self.on_first_monitor_changed(self.enabled_first_monitor_combo_box.currentText()))

        # 选择启用的第一个显示器的窗口位置组合
        self.enabled_first_monitor_window_position_combo_box = ComboBox()
        self.enabled_first_monitor_window_position_combo_box.addItems(get_content_combo_name("roll_call_notification_settings", "enabled_first_monitor_window_position"))
        self.enabled_first_monitor_window_position_combo_box.setCurrentText(readme_settings("roll_call_notification_settings", "enabled_first_monitor_window_position"))
        self.enabled_first_monitor_window_position_combo_box.currentTextChanged.connect(lambda: update_settings("roll_call_notification_settings", "enabled_first_monitor_window_position", self.enabled_first_monitor_window_position_combo_box.currentText()))

        # 选择启用的第二个显示器下拉框
        self.enabled_second_monitor_combo_box = ComboBox()
        self.enabled_second_monitor_combo_box.addItems(["OFF"] + self.get_monitor_list())
        self.enabled_second_monitor_combo_box.setCurrentText(readme_settings("roll_call_notification_settings", "enabled_second_monitor"))
        self.enabled_second_monitor_combo_box.currentTextChanged.connect(lambda: self.on_second_monitor_changed(self.enabled_second_monitor_combo_box.currentText()))

        # 选择启用的第二个显示器的窗口位置组合
        self.enabled_second_monitor_window_position_combo_box = ComboBox()
        self.enabled_second_monitor_window_position_combo_box.addItems(get_content_combo_name("roll_call_notification_settings", "enabled_second_monitor_window_position"))
        self.enabled_second_monitor_window_position_combo_box.setCurrentText(readme_settings("roll_call_notification_settings", "enabled_second_monitor_window_position"))
        self.enabled_second_monitor_window_position_combo_box.currentTextChanged.connect(lambda: update_settings("roll_call_notification_settings", "enabled_second_monitor_window_position", self.enabled_second_monitor_window_position_combo_box.currentText()))

        # 选择启用的第三个显示器下拉框
        self.enabled_third_monitor_combo_box = ComboBox()
        self.enabled_third_monitor_combo_box.addItems(["OFF"] + self.get_monitor_list())
        self.enabled_third_monitor_combo_box.setCurrentText(readme_settings("roll_call_notification_settings", "enabled_third_monitor"))
        self.enabled_third_monitor_combo_box.currentTextChanged.connect(lambda: self.on_third_monitor_changed(self.enabled_third_monitor_combo_box.currentText()))

        # 选择启用的第三个显示器的窗口位置组合
        self.enabled_third_monitor_window_position_combo_box = ComboBox()
        self.enabled_third_monitor_window_position_combo_box.addItems(get_content_combo_name("roll_call_notification_settings", "enabled_third_monitor_window_position"))
        self.enabled_third_monitor_window_position_combo_box.setCurrentText(readme_settings("roll_call_notification_settings", "enabled_third_monitor_window_position"))
        self.enabled_third_monitor_window_position_combo_box.currentTextChanged.connect(lambda: update_settings("roll_call_notification_settings", "enabled_third_monitor_window_position", self.enabled_third_monitor_window_position_combo_box.currentText()))

        # 添加设置项到分组
        self.addGroup(get_theme_icon("ic_fluent_position_to_back_20_filled"), 
                        get_content_name("roll_call_notification_settings", "window_position"), get_content_description("roll_call_notification_settings", "window_position"), self.window_position_combo_box)
        self.addGroup(get_theme_icon("ic_fluent_align_stretch_horizontal_20_filled"), 
                        get_content_name("roll_call_notification_settings", "horizontal_offset"), get_content_description("roll_call_notification_settings", "horizontal_offset"), self.horizontal_offset_spin_spinbox)
        self.addGroup(get_theme_icon("ic_fluent_align_stretch_vertical_20_filled"), 
                        get_content_name("roll_call_notification_settings", "vertical_offset"), get_content_description("roll_call_notification_settings", "vertical_offset"), self.vertical_offset_spin_spinbox)
        self.addGroup(get_theme_icon("ic_fluent_transparency_square_20_filled"), 
                        get_content_name("roll_call_notification_settings", "transparency"), get_content_description("roll_call_notification_settings", "transparency"), self.window_transparency_spin_spinbox)
        self.addGroup(get_theme_icon("ic_fluent_window_text_20_filled"), 
                        get_content_name("roll_call_notification_settings", "enabled_first_monitor"), get_content_description("roll_call_notification_settings", "enabled_first_monitor"), self.enabled_first_monitor_combo_box)
        self.addGroup(get_theme_icon("ic_fluent_position_to_back_20_filled"), 
                        get_content_name("roll_call_notification_settings", "enabled_first_monitor_window_position"), get_content_description("roll_call_notification_settings", "enabled_first_monitor_window_position"), self.enabled_first_monitor_window_position_combo_box)
        self.addGroup(get_theme_icon("ic_fluent_window_text_20_filled"), 
                        get_content_name("roll_call_notification_settings", "enabled_second_monitor"), get_content_description("roll_call_notification_settings", "enabled_second_monitor"), self.enabled_second_monitor_combo_box)
        self.addGroup(get_theme_icon("ic_fluent_position_to_back_20_filled"), 
                        get_content_name("roll_call_notification_settings", "enabled_second_monitor_window_position"), get_content_description("roll_call_notification_settings", "enabled_second_monitor_window_position"), self.enabled_second_monitor_window_position_combo_box)
        self.addGroup(get_theme_icon("ic_fluent_window_text_20_filled"), 
                        get_content_name("roll_call_notification_settings", "enabled_third_monitor"), get_content_description("roll_call_notification_settings", "enabled_third_monitor"), self.enabled_third_monitor_combo_box)
        self.addGroup(get_theme_icon("ic_fluent_position_to_back_20_filled"), 
                        get_content_name("roll_call_notification_settings", "enabled_third_monitor_window_position"), get_content_description("roll_call_notification_settings", "enabled_third_monitor_window_position"), self.enabled_third_monitor_window_position_combo_box)

    # 获取显示器列表
    def get_monitor_list(self):
        monitor_list = []
        for screen in QApplication.instance().screens():
            monitor_list.append(screen.name())
        return monitor_list

    # 第一个显示器选择变化处理
    def on_first_monitor_changed(self, value):
        # 检查第二个显示器是否与第一个相同
        if self.enabled_second_monitor_combo_box.currentText() == value:
            # 获取所有显示器选项
            monitor_list = ["OFF"] + self.get_monitor_list()
            # 找到下一个可用的显示器
            for i, monitor in enumerate(monitor_list):
                if monitor != value and monitor != self.enabled_third_monitor_combo_box.currentText():
                    self.enabled_second_monitor_combo_box.setCurrentText(monitor)
                    update_settings("roll_call_notification_settings", "enabled_second_monitor", monitor)
                    break
        
        # 检查第三个显示器是否与第一个相同
        if self.enabled_third_monitor_combo_box.currentText() == value:
            # 获取所有显示器选项
            monitor_list = ["OFF"] + self.get_monitor_list()
            # 找到下一个可用的显示器
            for i, monitor in enumerate(monitor_list):
                if monitor != value and monitor != self.enabled_second_monitor_combo_box.currentText():
                    self.enabled_third_monitor_combo_box.setCurrentText(monitor)
                    update_settings("roll_call_notification_settings", "enabled_third_monitor", monitor)
                    break
        
        # 更新第一个显示器的设置
        update_settings("roll_call_notification_settings", "enabled_first_monitor", value)

    # 第二个显示器选择变化处理
    def on_second_monitor_changed(self, value):
        # 检查第一个显示器是否与第二个相同
        if self.enabled_first_monitor_combo_box.currentText() == value and value != "OFF":
            # 当第二个显示器与第一个相同时，优先设置为OFF
            self.enabled_second_monitor_combo_box.setCurrentText("OFF")
            value = "OFF"
        
        # 检查第三个显示器是否与第二个相同
        if self.enabled_third_monitor_combo_box.currentText() == value and value != "OFF":
            # 获取所有显示器选项
            monitor_list = ["OFF"] + self.get_monitor_list()
            # 找到下一个可用的显示器
            for i, monitor in enumerate(monitor_list):
                if monitor != value and monitor != self.enabled_first_monitor_combo_box.currentText():
                    self.enabled_third_monitor_combo_box.setCurrentText(monitor)
                    update_settings("roll_call_notification_settings", "enabled_third_monitor", monitor)
                    break
        
        # 更新第二个显示器的设置
        update_settings("roll_call_notification_settings", "enabled_second_monitor", value)

    # 第三个显示器选择变化处理
    def on_third_monitor_changed(self, value):
        # 检查第一个显示器是否与第三个相同
        if self.enabled_first_monitor_combo_box.currentText() == value and value != "OFF":
            # 当第三个显示器与第一个相同时，优先设置为OFF
            self.enabled_third_monitor_combo_box.setCurrentText("OFF")
            value = "OFF"
        
        # 检查第二个显示器是否与第三个相同
        if self.enabled_second_monitor_combo_box.currentText() == value and value != "OFF":
            # 获取所有显示器选项
            monitor_list = ["OFF"] + self.get_monitor_list()
            # 找到下一个可用的显示器
            for i, monitor in enumerate(monitor_list):
                if monitor != value and monitor != self.enabled_first_monitor_combo_box.currentText():
                    self.enabled_second_monitor_combo_box.setCurrentText(monitor)
                    update_settings("roll_call_notification_settings", "enabled_second_monitor", monitor)
                    break
        
        # 更新第三个显示器的设置
        update_settings("roll_call_notification_settings", "enabled_third_monitor", value)

class floating_window_settings(GroupHeaderCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(get_content_name("roll_call_notification_settings", "floating_window_mode"))
        self.setBorderRadius(8)
        
        # 窗口透明度
        self.window_transparency_spin_spinbox = SpinBox()
        self.window_transparency_spin_spinbox.setFixedWidth(WIDTH_SPINBOX)
        self.window_transparency_spin_spinbox.setRange(0, 100)
        self.window_transparency_spin_spinbox.setSuffix("%")
        self.window_transparency_spin_spinbox.setValue(readme_settings("roll_call_notification_settings", "floating_window_transparency") * 100)
        self.window_transparency_spin_spinbox.valueChanged.connect(lambda: update_settings("roll_call_notification_settings", "floating_window_transparency", self.window_transparency_spin_spinbox.value() / 100))

        # 选择启用的第一个显示器下拉框
        self.enabled_first_monitor_combo_box = ComboBox()
        self.enabled_first_monitor_combo_box.addItems(self.get_monitor_list())
        if readme_settings("roll_call_notification_settings", "floating_window_enabled_first_monitor") == "OFF":
            self.enabled_first_monitor_combo_box.setCurrentText(self.get_monitor_list()[0])
            update_settings("roll_call_notification_settings", "floating_window_enabled_first_monitor", self.enabled_first_monitor_combo_box.currentText())
        self.enabled_first_monitor_combo_box.setCurrentText(readme_settings("roll_call_notification_settings", "floating_window_enabled_first_monitor"))
        self.enabled_first_monitor_combo_box.currentTextChanged.connect(lambda: self.on_floating_first_monitor_changed(self.enabled_first_monitor_combo_box.currentText()))

        # 选择启用的第一个显示器的窗口位置组合
        self.enabled_first_monitor_window_position_combo_box = ComboBox()
        self.enabled_first_monitor_window_position_combo_box.addItems(get_content_combo_name("roll_call_notification_settings", "floating_window_enabled_first_monitor_window_position"))
        self.enabled_first_monitor_window_position_combo_box.setCurrentText(readme_settings("roll_call_notification_settings", "floating_window_enabled_first_monitor_window_position"))
        self.enabled_first_monitor_window_position_combo_box.currentTextChanged.connect(lambda: update_settings("roll_call_notification_settings", "floating_window_enabled_first_monitor_window_position", self.enabled_first_monitor_window_position_combo_box.currentText()))

        # 选择启用的第二个显示器下拉框
        self.enabled_second_monitor_combo_box = ComboBox()
        self.enabled_second_monitor_combo_box.addItems(["OFF"] + self.get_monitor_list())
        self.enabled_second_monitor_combo_box.setCurrentText(readme_settings("roll_call_notification_settings", "floating_window_enabled_second_monitor"))
        self.enabled_second_monitor_combo_box.currentTextChanged.connect(lambda: self.on_floating_second_monitor_changed(self.enabled_second_monitor_combo_box.currentText()))

        # 选择启用的第二个显示器的窗口位置组合
        self.enabled_second_monitor_window_position_combo_box = ComboBox()
        self.enabled_second_monitor_window_position_combo_box.addItems(get_content_combo_name("roll_call_notification_settings", "floating_window_enabled_second_monitor_window_position"))
        self.enabled_second_monitor_window_position_combo_box.setCurrentText(readme_settings("roll_call_notification_settings", "floating_window_enabled_second_monitor_window_position"))
        self.enabled_second_monitor_window_position_combo_box.currentTextChanged.connect(lambda: update_settings("roll_call_notification_settings", "floating_window_enabled_second_monitor_window_position", self.enabled_second_monitor_window_position_combo_box.currentText()))

        # 选择启用的第三个显示器下拉框
        self.enabled_third_monitor_combo_box = ComboBox()
        self.enabled_third_monitor_combo_box.addItems(["OFF"] + self.get_monitor_list())
        self.enabled_third_monitor_combo_box.setCurrentText(readme_settings("roll_call_notification_settings", "floating_window_enabled_third_monitor"))
        self.enabled_third_monitor_combo_box.currentTextChanged.connect(lambda: self.on_floating_third_monitor_changed(self.enabled_third_monitor_combo_box.currentText()))

        # 选择启用的第三个显示器的窗口位置组合
        self.enabled_third_monitor_window_position_combo_box = ComboBox()
        self.enabled_third_monitor_window_position_combo_box.addItems(get_content_combo_name("roll_call_notification_settings", "floating_window_enabled_third_monitor_window_position"))
        self.enabled_third_monitor_window_position_combo_box.setCurrentText(readme_settings("roll_call_notification_settings", "floating_window_enabled_third_monitor_window_position"))
        self.enabled_third_monitor_window_position_combo_box.currentTextChanged.connect(lambda: update_settings("roll_call_notification_settings", "floating_window_enabled_third_monitor_window_position", self.enabled_third_monitor_window_position_combo_box.currentText()))

        # 添加设置项到分组
        self.addGroup(get_theme_icon("ic_fluent_transparency_square_20_filled"), 
                        get_content_name("roll_call_notification_settings", "floating_window_transparency"), get_content_description("roll_call_notification_settings", "floating_window_transparency"), self.window_transparency_spin_spinbox)
        self.addGroup(get_theme_icon("ic_fluent_window_text_20_filled"), 
                        get_content_name("roll_call_notification_settings", "floating_window_enabled_first_monitor"), get_content_description("roll_call_notification_settings", "floating_window_enabled_first_monitor"), self.enabled_first_monitor_combo_box)
        self.addGroup(get_theme_icon("ic_fluent_position_to_back_20_filled"), 
                        get_content_name("roll_call_notification_settings", "floating_window_enabled_first_monitor_window_position"), get_content_description("roll_call_notification_settings", "floating_window_enabled_first_monitor_window_position"), self.enabled_first_monitor_window_position_combo_box)
        self.addGroup(get_theme_icon("ic_fluent_window_text_20_filled"), 
                        get_content_name("roll_call_notification_settings", "floating_window_enabled_second_monitor"), get_content_description("roll_call_notification_settings", "floating_window_enabled_second_monitor"), self.enabled_second_monitor_combo_box)
        self.addGroup(get_theme_icon("ic_fluent_position_to_back_20_filled"), 
                        get_content_name("roll_call_notification_settings", "floating_window_enabled_second_monitor_window_position"), get_content_description("roll_call_notification_settings", "floating_window_enabled_second_monitor_window_position"), self.enabled_second_monitor_window_position_combo_box)
        self.addGroup(get_theme_icon("ic_fluent_window_text_20_filled"), 
                        get_content_name("roll_call_notification_settings", "floating_window_enabled_third_monitor"), get_content_description("roll_call_notification_settings", "floating_window_enabled_third_monitor"), self.enabled_third_monitor_combo_box)
        self.addGroup(get_theme_icon("ic_fluent_position_to_back_20_filled"), 
                        get_content_name("roll_call_notification_settings", "floating_window_enabled_third_monitor_window_position"), get_content_description("roll_call_notification_settings", "floating_window_enabled_third_monitor_window_position"), self.enabled_third_monitor_window_position_combo_box)

    # 获取显示器列表
    def get_monitor_list(self):
        monitor_list = []
        for screen in QApplication.instance().screens():
            monitor_list.append(screen.name())
        return monitor_list

    # 浮窗第一个显示器选择变化处理
    def on_floating_first_monitor_changed(self, value):
        # 检查第二个显示器是否与第一个相同
        if self.enabled_second_monitor_combo_box.currentText() == value:
            # 获取所有显示器选项
            monitor_list = ["OFF"] + self.get_monitor_list()
            # 找到下一个可用的显示器
            for i, monitor in enumerate(monitor_list):
                if monitor != value and monitor != self.enabled_third_monitor_combo_box.currentText():
                    self.enabled_second_monitor_combo_box.setCurrentText(monitor)
                    update_settings("roll_call_notification_settings", "floating_window_enabled_second_monitor", monitor)
                    break
        
        # 检查第三个显示器是否与第一个相同
        if self.enabled_third_monitor_combo_box.currentText() == value:
            # 获取所有显示器选项
            monitor_list = ["OFF"] + self.get_monitor_list()
            # 找到下一个可用的显示器
            for i, monitor in enumerate(monitor_list):
                if monitor != value and monitor != self.enabled_second_monitor_combo_box.currentText():
                    self.enabled_third_monitor_combo_box.setCurrentText(monitor)
                    update_settings("roll_call_notification_settings", "floating_window_enabled_third_monitor", monitor)
                    break
        
        # 更新第一个显示器的设置
        update_settings("roll_call_notification_settings", "floating_window_enabled_first_monitor", value)

    # 浮窗第二个显示器选择变化处理
    def on_floating_second_monitor_changed(self, value):
        # 检查第一个显示器是否与第二个相同
        if self.enabled_first_monitor_combo_box.currentText() == value and value != "OFF":
            # 当第二个显示器与第一个相同时，优先设置为OFF
            self.enabled_second_monitor_combo_box.setCurrentText("OFF")
            value = "OFF"
        
        # 检查第三个显示器是否与第二个相同
        if self.enabled_third_monitor_combo_box.currentText() == value and value != "OFF":
            # 获取所有显示器选项
            monitor_list = ["OFF"] + self.get_monitor_list()
            # 找到下一个可用的显示器
            for i, monitor in enumerate(monitor_list):
                if monitor != value and monitor != self.enabled_first_monitor_combo_box.currentText():
                    self.enabled_third_monitor_combo_box.setCurrentText(monitor)
                    update_settings("roll_call_notification_settings", "floating_window_enabled_third_monitor", monitor)
                    break
        
        # 更新第二个显示器的设置
        update_settings("roll_call_notification_settings", "floating_window_enabled_second_monitor", value)

    # 浮窗第三个显示器选择变化处理
    def on_floating_third_monitor_changed(self, value):
        # 检查第一个显示器是否与第三个相同
        if self.enabled_first_monitor_combo_box.currentText() == value and value != "OFF":
            # 当第三个显示器与第一个相同时，优先设置为OFF
            self.enabled_third_monitor_combo_box.setCurrentText("OFF")
            value = "OFF"
        
        # 检查第二个显示器是否与第三个相同
        if self.enabled_second_monitor_combo_box.currentText() == value and value != "OFF":
            # 获取所有显示器选项
            monitor_list = ["OFF"] + self.get_monitor_list()
            # 找到下一个可用的显示器
            for i, monitor in enumerate(monitor_list):
                if monitor != value and monitor != self.enabled_first_monitor_combo_box.currentText():
                    self.enabled_second_monitor_combo_box.setCurrentText(monitor)
                    update_settings("roll_call_notification_settings", "floating_window_enabled_second_monitor", monitor)
                    break
        
        # 更新第三个显示器的设置
        update_settings("roll_call_notification_settings", "floating_window_enabled_third_monitor", value)
