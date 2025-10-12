from shlex import join
from qfluentwidgets import *
from qfluentwidgets import FluentIcon as FIF
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

import json
import os
import sys
import platform
from pathlib import Path
from datetime import datetime
from loguru import logger
import winreg
from app.common.config import get_theme_icon, load_custom_font, is_dark_theme
from app.common.path_utils import path_manager
from app.common.path_utils import open_file, ensure_dir

is_dark = is_dark_theme(qconfig)

class roll_call_settingsCard(GroupHeaderCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("点名界面管理")
        self.setBorderRadius(8)
        self.settings_file = path_manager.get_settings_path('custom_settings.json')
        self.default_settings = {
            "pumping_people_control_Switch": True,
            "modify_button_switch": False,
            "show_reset_button": True,
            "show_refresh_button": True,
            "show_quantity_control": True,
            "show_start_button": True,
            "show_list_toggle": True,
            "selection_range": True,
            "selection_gender": True,
            "people_theme": 0
        }

        # 点名控制面板
        self.pumping_people_control_Switch = SwitchButton()
        self.pumping_people_control_Switch.setOnText("右侧")
        self.pumping_people_control_Switch.setOffText("左侧")
        self.pumping_people_control_Switch.setFont(QFont(load_custom_font(), 12))
        self.pumping_people_control_Switch.checkedChanged.connect(self.save_settings)

        # 修改班级名单按钮是否显示
        self.modify_button_switch = SwitchButton()
        self.modify_button_switch.setOnText("显示")
        self.modify_button_switch.setOffText("隐藏")
        self.modify_button_switch.setFont(QFont(load_custom_font(), 12))
        self.modify_button_switch.checkedChanged.connect(self.save_settings)

        # 重置已抽取名单按钮是否显示
        self.reset_button_switch = SwitchButton()
        self.reset_button_switch.setOnText("显示")
        self.reset_button_switch.setOffText("隐藏")
        self.reset_button_switch.setFont(QFont(load_custom_font(), 12))
        self.reset_button_switch.checkedChanged.connect(self.save_settings)

        # 刷新列表按钮
        self.refresh_button_switch = SwitchButton()
        self.refresh_button_switch.setOnText("显示")
        self.refresh_button_switch.setOffText("隐藏")
        self.refresh_button_switch.setFont(QFont(load_custom_font(), 12))
        self.refresh_button_switch.checkedChanged.connect(self.save_settings)

        # 增加/减少抽取数量控制条
        self.quantity_control_switch = SwitchButton()
        self.quantity_control_switch.setOnText("显示")
        self.quantity_control_switch.setOffText("隐藏")
        self.quantity_control_switch.setFont(QFont(load_custom_font(), 12))
        self.quantity_control_switch.checkedChanged.connect(self.save_settings)

        # 开始按钮
        self.start_button_switch = SwitchButton()
        self.start_button_switch.setOnText("显示")
        self.start_button_switch.setOffText("隐藏")
        self.start_button_switch.setFont(QFont(load_custom_font(), 12))
        self.start_button_switch.checkedChanged.connect(self.save_settings)

        # 名单切换下拉框
        self.list_toggle_switch = SwitchButton()
        self.list_toggle_switch.setOnText("显示")
        self.list_toggle_switch.setOffText("隐藏")
        self.list_toggle_switch.setFont(QFont(load_custom_font(), 12))
        self.list_toggle_switch.checkedChanged.connect(self.save_settings)

        # 抽取范围下拉框
        self.selection_range_switch = SwitchButton()
        self.selection_range_switch.setOnText("显示")
        self.selection_range_switch.setOffText("隐藏")
        self.selection_range_switch.setFont(QFont(load_custom_font(), 12))
        self.selection_range_switch.checkedChanged.connect(self.save_settings)

        # 抽取性别下拉框
        self.selection_gender_switch = SwitchButton()
        self.selection_gender_switch.setOnText("显示")
        self.selection_gender_switch.setOffText("隐藏")
        self.selection_gender_switch.setFont(QFont(load_custom_font(), 12))
        self.selection_gender_switch.checkedChanged.connect(self.save_settings)

        # 人数/组数样式下拉框
        self.pumping_people_theme_comboBox = ComboBox()
        self.pumping_people_theme_comboBox.addItems(["总数 | 剩余", "总数", "剩余", "不显示"])
        self.pumping_people_theme_comboBox.currentIndexChanged.connect(self.save_settings)
        self.pumping_people_theme_comboBox.setFont(QFont(load_custom_font(), 12))

        # 添加个性化设置组
        self.addGroup(get_theme_icon("ic_fluent_window_ad_20_filled"), "点名控制面板", "配置点名控制面板的显示位置", self.pumping_people_control_Switch)
        self.addGroup(get_theme_icon("ic_fluent_people_community_20_filled"), "姓名设置按钮", "显隐'姓名设置'按钮", self.modify_button_switch)
        self.addGroup(get_theme_icon("ic_fluent_arrow_reset_20_filled"), "重置已抽取名单按钮", "显隐'重置已抽取名单'按钮", self.reset_button_switch)
        self.addGroup(get_theme_icon("ic_fluent_people_community_20_filled"), "刷新学生列表按钮", "显隐'刷新学生列表'按钮", self.refresh_button_switch)
        self.addGroup(get_theme_icon("ic_fluent_arrows_bidirectional_20_filled"), "增加/减少抽取数量控制条", "显隐'增加/减少抽取数量'控制条", self.quantity_control_switch)
        self.addGroup(get_theme_icon("ic_fluent_play_20_filled"), "开始按钮", "显隐'开始'按钮", self.start_button_switch)
        self.addGroup(get_theme_icon("ic_fluent_people_list_20_filled"), "名单切换下拉框", "显隐'名单切换'下拉框", self.list_toggle_switch)
        self.addGroup(get_theme_icon("ic_fluent_people_list_20_filled"), "抽取范围下拉框", "显隐'抽取范围'下拉框", self.selection_range_switch)
        self.addGroup(get_theme_icon("ic_fluent_people_list_20_filled"), "抽取性别下拉框", "显隐'抽取性别'下拉框", self.selection_gender_switch)
        self.addGroup(get_theme_icon("ic_fluent_people_eye_20_filled"), "班级人|组数", "设置人数或组数的显示样式", self.pumping_people_theme_comboBox)
        
        # 加载设置
        self.load_settings()
        self.save_settings()

    def load_settings(self):
        try:
            if path_manager.file_exists(self.settings_file):
                with open_file(self.settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    roll_call_settings = settings.get("roll_call", {})

                    self.pumping_people_control_Switch.setChecked(roll_call_settings.get("pumping_people_control_Switch", self.default_settings.get("pumping_people_control_Switch", True)))
                    self.modify_button_switch.setChecked(roll_call_settings.get("modify_button_switch", self.default_settings.get("modify_button_switch", True)))   
                    self.reset_button_switch.setChecked(roll_call_settings.get("show_reset_button", self.default_settings.get("show_reset_button", True)))
                    self.refresh_button_switch.setChecked(roll_call_settings.get("show_refresh_button", self.default_settings.get("show_refresh_button", True)))
                    self.quantity_control_switch.setChecked(roll_call_settings.get("show_quantity_control", self.default_settings.get("show_quantity_control", True)))
                    self.start_button_switch.setChecked(roll_call_settings.get("show_start_button", self.default_settings.get("show_start_button", True)))
                    self.list_toggle_switch.setChecked(roll_call_settings.get("show_list_toggle", self.default_settings.get("show_list_toggle", True)))
                    self.selection_range_switch.setChecked(roll_call_settings.get("selection_range", self.default_settings.get("selection_range", True)))
                    self.selection_gender_switch.setChecked(roll_call_settings.get("selection_gender", self.default_settings.get("selection_gender", True)))
                    self.pumping_people_theme_comboBox.setCurrentIndex(roll_call_settings.get("people_theme", self.default_settings.get("people_theme", 0)))

            else:
                logger.error(f"设置文件不存在: {self.settings_file}")

                self.pumping_people_control_Switch.setChecked(self.default_settings.get("pumping_people_control_Switch", True))
                self.modify_button_switch.setChecked(self.default_settings.get("modify_button_switch", True))
                self.reset_button_switch.setChecked(self.default_settings.get("show_reset_button", True))
                self.refresh_button_switch.setChecked(self.default_settings.get("show_refresh_button", True))
                self.quantity_control_switch.setChecked(self.default_settings.get("show_quantity_control", True))
                self.start_button_switch.setChecked(self.default_settings.get("show_start_button", True))
                self.list_toggle_switch.setChecked(self.default_settings.get("show_list_toggle", True))
                self.selection_range_switch.setChecked(self.default_settings.get("selection_range", True))
                self.selection_gender_switch.setChecked(self.default_settings.get("selection_gender", True))
                self.pumping_people_theme_comboBox.setCurrentIndex(self.default_settings.get("people_theme", 0))
                self.save_settings()
        except Exception as e:
            logger.error(f"加载设置时出错: {e}")

            self.pumping_people_control_Switch.setChecked(self.default_settings.get("pumping_people_control_Switch", True))
            self.modify_button_switch.setChecked(self.default_settings.get("modify_button_switch", True))
            self.reset_button_switch.setChecked(self.default_settings.get("show_reset_button", True))
            self.refresh_button_switch.setChecked(self.default_settings.get("show_refresh_button", True))
            self.quantity_control_switch.setChecked(self.default_settings.get("show_quantity_control", True))
            self.start_button_switch.setChecked(self.default_settings.get("show_start_button", True))
            self.list_toggle_switch.setChecked(self.default_settings.get("show_list_toggle", True))
            self.selection_range_switch.setChecked(self.default_settings.get("selection_range", True))
            self.selection_gender_switch.setChecked(self.default_settings.get("selection_gender", True))
            self.pumping_people_theme_comboBox.setCurrentIndex(self.default_settings.get("people_theme", 0))
            self.save_settings()

    def save_settings(self):
        # 先读取现有设置
        existing_settings = {}
        if path_manager.file_exists(self.settings_file):
            with open_file(self.settings_file, 'r', encoding='utf-8') as f:
                try:
                    existing_settings = json.load(f)
                except json.JSONDecodeError:
                    existing_settings = {}
        
        # 更新roll_call部分的所有设置
        if "roll_call" not in existing_settings:
            existing_settings["roll_call"] = {}
            
        roll_call_settings = existing_settings["roll_call"]

        roll_call_settings["pumping_people_control_Switch"] = self.pumping_people_control_Switch.isChecked()
        roll_call_settings["modify_button_switch"] = self.modify_button_switch.isChecked()
        roll_call_settings["show_reset_button"] = self.reset_button_switch.isChecked()
        roll_call_settings["show_refresh_button"] = self.refresh_button_switch.isChecked()
        roll_call_settings["show_quantity_control"] = self.quantity_control_switch.isChecked()
        roll_call_settings["show_start_button"] = self.start_button_switch.isChecked()
        roll_call_settings["show_list_toggle"] = self.list_toggle_switch.isChecked()
        roll_call_settings["selection_range"] = self.selection_range_switch.isChecked()
        roll_call_settings["selection_gender"] = self.selection_gender_switch.isChecked()
        roll_call_settings["people_theme"] = self.pumping_people_theme_comboBox.currentIndex()

        os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
        with open_file(self.settings_file, 'w', encoding='utf-8') as f:
            json.dump(existing_settings, f, indent=4)