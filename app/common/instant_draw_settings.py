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
from app.common.config import get_theme_icon, load_custom_font, is_dark_theme, VERSION
from app.common.path_utils import path_manager
from app.common.path_utils import open_file, ensure_dir

is_dark = is_dark_theme(qconfig)

class instant_draw_settingsCard(GroupHeaderCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("闪抽/即抽窗口管理")
        self.setBorderRadius(8)
        self.settings_file = path_manager.get_settings_path('custom_settings.json')
        self.default_settings = {
            "show_reset_button": True,
            "show_quantity_control": True,
            "show_list_toggle": True,
            "selection_range": True,
            "selection_gender": True,
        }

        # 重置按钮是否显示
        self.reset_button_switch = SwitchButton()
        self.reset_button_switch.setOnText("显示")
        self.reset_button_switch.setOffText("隐藏")
        self.reset_button_switch.setFont(QFont(load_custom_font(), 12))
        self.reset_button_switch.checkedChanged.connect(self.save_settings)

        # 增加/减少抽取数量控制条
        self.quantity_control_switch = SwitchButton()
        self.quantity_control_switch.setOnText("显示")
        self.quantity_control_switch.setOffText("隐藏")
        self.quantity_control_switch.setFont(QFont(load_custom_font(), 12))
        self.quantity_control_switch.checkedChanged.connect(self.save_settings)

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

        # 添加个性化设置组
        self.addGroup(get_theme_icon("ic_fluent_arrow_reset_20_filled"), "重置按钮", "显隐'重置'按钮", self.reset_button_switch)
        self.addGroup(get_theme_icon("ic_fluent_arrows_bidirectional_20_filled"), "增加/减少抽取数量控制条", "显隐'增加/减少抽取数量'控制条", self.quantity_control_switch)
        self.addGroup(get_theme_icon("ic_fluent_people_list_20_filled"), "名单切换下拉框", "显隐'名单切换'下拉框", self.list_toggle_switch)
        self.addGroup(get_theme_icon("ic_fluent_people_list_20_filled"), "抽取范围下拉框", "显隐'抽取范围'下拉框", self.selection_range_switch)
        self.addGroup(get_theme_icon("ic_fluent_people_list_20_filled"), "抽取性别下拉框", "显隐'抽取性别'下拉框", self.selection_gender_switch)
        
        # 加载设置
        self.load_settings()
        self.save_settings()

    def load_settings(self):
        try:
            if path_manager.file_exists(self.settings_file):
                with open_file(self.settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    instant_draw_settings = settings.get("instant_draw", {})

                    self.reset_button_switch.setChecked(instant_draw_settings.get("show_reset_button", self.default_settings.get("show_reset_button", True)))
                    self.quantity_control_switch.setChecked(instant_draw_settings.get("show_quantity_control", self.default_settings.get("show_quantity_control", True)))
                    self.list_toggle_switch.setChecked(instant_draw_settings.get("show_list_toggle", self.default_settings.get("show_list_toggle", True)))
                    self.selection_range_switch.setChecked(instant_draw_settings.get("selection_range", self.default_settings.get("selection_range", True)))
                    self.selection_gender_switch.setChecked(instant_draw_settings.get("selection_gender", self.default_settings.get("selection_gender", True)))

            else:
                logger.warning(f"设置文件不存在: {self.settings_file}")

                self.reset_button_switch.setChecked(self.default_settings.get("show_reset_button", True))
                self.quantity_control_switch.setChecked(self.default_settings.get("show_quantity_control", True))
                self.list_toggle_switch.setChecked(self.default_settings.get("show_list_toggle", True))
                self.selection_range_switch.setChecked(self.default_settings.get("selection_range", True))
                self.selection_gender_switch.setChecked(self.default_settings.get("selection_gender", True))
                self.save_settings()
        except Exception as e:
            logger.error(f"加载设置时出错: {e}")

            self.reset_button_switch.setChecked(self.default_settings.get("show_reset_button", True))
            self.quantity_control_switch.setChecked(self.default_settings.get("show_quantity_control", True))
            self.list_toggle_switch.setChecked(self.default_settings.get("show_list_toggle", True))
            self.selection_range_switch.setChecked(self.default_settings.get("selection_range", True))
            self.selection_gender_switch.setChecked(self.default_settings.get("selection_gender", True))

    def save_settings(self):
        # 先读取现有设置
        existing_settings = {}
        if path_manager.file_exists(self.settings_file):
            with open_file(self.settings_file, 'r', encoding='utf-8') as f:
                try:
                    existing_settings = json.load(f)
                except json.JSONDecodeError:
                    existing_settings = {}
        
        # 更新instant_draw部分的所有设置
        if "instant_draw" not in existing_settings:
            existing_settings["instant_draw"] = {}
            
        instant_draw_settings = existing_settings["instant_draw"]

        instant_draw_settings["show_reset_button"] = self.reset_button_switch.isChecked()
        instant_draw_settings["show_quantity_control"] = self.quantity_control_switch.isChecked()
        instant_draw_settings["show_list_toggle"] = self.list_toggle_switch.isChecked()
        instant_draw_settings["selection_range"] = self.selection_range_switch.isChecked()
        instant_draw_settings["selection_gender"] = self.selection_gender_switch.isChecked()

        os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
        with open_file(self.settings_file, 'w', encoding='utf-8') as f:
            json.dump(existing_settings, f, indent=4)