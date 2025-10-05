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

class tray_settingsCard(GroupHeaderCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("托盘管理")
        self.setBorderRadius(8)
        self.settings_file = path_manager.get_settings_path('custom_settings.json')
        self.default_settings = {
            "show_main_window": True,
            "show_floating_window": True,
            "restart": True,
            "exit": True,
            "flash": False,
        }

        # 暂时显示/隐藏主界面 选项显隐 开关
        self.show_main_window_switch = SwitchButton(self)
        self.show_main_window_switch.setOnText("显示")
        self.show_main_window_switch.setOffText("隐藏")
        self.show_main_window_switch.checkedChanged.connect(self.save_settings)
        self.show_main_window_switch.setFont(QFont(load_custom_font(), 12))

        # 暂时显示/隐藏浮窗 选项显隐 开关
        self.show_floating_window_switch = SwitchButton(self)
        self.show_floating_window_switch.setOnText("显示")
        self.show_floating_window_switch.setOffText("隐藏")
        self.show_floating_window_switch.checkedChanged.connect(self.save_settings)
        self.show_floating_window_switch.setFont(QFont(load_custom_font(), 12))

        # 重启 选项显隐 开关
        self.restart_switch = SwitchButton(self)
        self.restart_switch.setOnText("显示")
        self.restart_switch.setOffText("隐藏")
        self.restart_switch.checkedChanged.connect(self.save_settings)
        self.restart_switch.setFont(QFont(load_custom_font(), 12))

        # 退出 选项显隐 开关
        self.exit_switch = SwitchButton(self)
        self.exit_switch.setOnText("显示")
        self.exit_switch.setOffText("隐藏")
        self.exit_switch.checkedChanged.connect(self.save_settings)
        self.exit_switch.setFont(QFont(load_custom_font(), 12))

        # 闪抽 选项显隐 开关
        self.flash_switch = SwitchButton(self)
        self.flash_switch.setOnText("显示")
        self.flash_switch.setOffText("隐藏")
        self.flash_switch.checkedChanged.connect(self.save_settings)
        self.flash_switch.setFont(QFont(load_custom_font(), 12))


        self.addGroup(get_theme_icon("ic_fluent_power_20_filled"), "暂时显示/隐藏主界面", "暂时显示/隐藏主界面 选项显隐", self.show_main_window_switch)
        self.addGroup(get_theme_icon("ic_fluent_window_ad_20_filled"), "暂时显示/隐藏浮窗", "暂时显示/隐藏浮窗 选项显隐", self.show_floating_window_switch)
        self.addGroup(get_theme_icon("ic_fluent_flash_20_filled"), "闪抽", "闪抽 选项显隐", self.flash_switch)
        self.addGroup(get_theme_icon("ic_fluent_arrow_sync_20_filled"), "重启", "重启 选项显隐", self.restart_switch)
        self.addGroup(get_theme_icon("ic_fluent_arrow_exit_20_filled"), "退出", "退出 选项显隐", self.exit_switch)
        
        # 加载设置
        self.load_settings()

    def load_settings(self):
        try:
            if path_manager.file_exists(self.settings_file):
                with open_file(self.settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    tray_settings = settings.get("tray", {})

                    self.show_main_window_switch.setChecked(tray_settings.get("show_main_window", self.default_settings["show_main_window"]))
                    self.show_floating_window_switch.setChecked(tray_settings.get("show_floating_window", self.default_settings["show_floating_window"]))
                    self.restart_switch.setChecked(tray_settings.get("restart", self.default_settings["restart"]))
                    self.exit_switch.setChecked(tray_settings.get("exit", self.default_settings["exit"]))
                    self.flash_switch.setChecked(tray_settings.get("flash", self.default_settings["flash"]))

            else:
                logger.error(f"设置文件不存在: {self.settings_file}")

                self.show_main_window_switch.setChecked(self.default_settings["show_main_window"])
                self.show_floating_window_switch.setChecked(self.default_settings["show_floating_window"])
                self.restart_switch.setChecked(self.default_settings["restart"])
                self.exit_switch.setChecked(self.default_settings["exit"])
                self.flash_switch.setChecked(self.default_settings["flash"])

                self.save_settings()
        except Exception as e:
            logger.error(f"加载设置时出错: {e}")

            self.show_main_window_switch.setChecked(self.default_settings["show_main_window"])
            self.show_floating_window_switch.setChecked(self.default_settings["show_floating_window"])
            self.restart_switch.setChecked(self.default_settings["restart"])
            self.exit_switch.setChecked(self.default_settings["exit"])
            self.flash_switch.setChecked(self.default_settings["flash"])
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
        
        # 更新tray部分的所有设置
        if "tray" not in existing_settings:
            existing_settings["tray"] = {}
            
        tray_settings = existing_settings["tray"]

        tray_settings["show_main_window"] = self.show_main_window_switch.isChecked()
        tray_settings["show_floating_window"] = self.show_floating_window_switch.isChecked()
        tray_settings["restart"] = self.restart_switch.isChecked()
        tray_settings["exit"] = self.exit_switch.isChecked()
        tray_settings["flash"] = self.flash_switch.isChecked()

        os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
        with open_file(self.settings_file, 'w', encoding='utf-8') as f:
            json.dump(existing_settings, f, indent=4)