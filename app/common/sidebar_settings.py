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
from app.common.settings_reader import (get_all_settings, get_settings_by_category, get_setting_value, 
                                        refresh_settings_cache, get_settings_summary, update_settings)

is_dark = is_dark_theme(qconfig)

class sidebar_settingsCard(GroupHeaderCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("侧边栏管理")
        self.setBorderRadius(8)
        self.settings_file = path_manager.get_settings_path('custom_settings.json')
        self.default_settings = {
            "pumping_floating_side": 0,
            "pumping_reward_side": 0,
            "show_settings_icon": 1,
            "main_window_history_switch": 1,
            "main_window_side_switch": 2,
            "show_security_settings_switch": 1,
            "show_voice_settings_switch": 1,
            "show_history_settings_switch": 1,
        }

        # 点名选项侧边栏位置设置
        self.pumping_floating_side_comboBox = ComboBox()
        self.pumping_floating_side_comboBox.addItems(["顶部", "底部", "不显示"])
        self.pumping_floating_side_comboBox.currentIndexChanged.connect(self.save_settings)
        self.pumping_floating_side_comboBox.setFont(QFont(load_custom_font(), 12))

        # 抽奖选项侧边栏位置设置
        self.pumping_reward_side_comboBox = ComboBox()
        self.pumping_reward_side_comboBox.addItems(["顶部", "底部", "不显示"])
        self.pumping_reward_side_comboBox.currentIndexChanged.connect(self.save_settings)
        self.pumping_reward_side_comboBox.setFont(QFont(load_custom_font(), 12))

        # 主界面侧边是否显示单词PK
        self.main_window_side_switch = ComboBox()
        self.main_window_side_switch.addItems(["顶部", "底部", "不显示"])
        self.main_window_side_switch.setFont(QFont(load_custom_font(), 12))
        self.main_window_side_switch.currentIndexChanged.connect(self.save_settings)

        # 主界面侧边是否显示历史记录
        self.main_window_history_switch = ComboBox()
        self.main_window_history_switch.addItems(["顶部", "底部", "不显示"])
        self.main_window_history_switch.setFont(QFont(load_custom_font(), 12))
        self.main_window_history_switch.currentIndexChanged.connect(self.save_settings)

        # 主界面侧边栏是否显示设置图标
        self.show_settings_icon_switch = ComboBox()
        self.show_settings_icon_switch.addItems(["顶部", "底部", "不显示"])
        self.show_settings_icon_switch.setFont(QFont(load_custom_font(), 12))
        self.show_settings_icon_switch.currentIndexChanged.connect(self.save_settings)

        # 设置页面侧边是否显示安全设置
        self.show_security_settings_switch = ComboBox()
        self.show_security_settings_switch.addItems(["顶部", "底部", "不显示"])
        self.show_security_settings_switch.setFont(QFont(load_custom_font(), 12))
        self.show_security_settings_switch.currentIndexChanged.connect(self.save_settings)

        # 设置页面侧边是否显示语音设置
        self.show_voice_settings_switch = ComboBox()
        self.show_voice_settings_switch.addItems(["顶部", "底部", "不显示"])
        self.show_voice_settings_switch.setFont(QFont(load_custom_font(), 12))
        self.show_voice_settings_switch.currentIndexChanged.connect(self.save_settings)

        # 设置页面是否显示历史记录
        self.show_history_settings_switch = ComboBox()
        self.show_history_settings_switch.addItems(["顶部", "底部", "不显示"])
        self.show_history_settings_switch.setFont(QFont(load_custom_font(), 12))
        self.show_history_settings_switch.currentIndexChanged.connect(self.save_settings)

        # 添加个性化设置组
        self.addGroup(get_theme_icon("ic_fluent_people_community_20_filled"), "点名选项侧边栏位置", "调整点名功能侧边栏的显示位置", self.pumping_floating_side_comboBox)
        self.addGroup(get_theme_icon("ic_fluent_reward_20_filled"), "抽奖选项侧边栏位置", "调整抽奖功能侧边栏的显示位置", self.pumping_reward_side_comboBox)
        self.addGroup(get_theme_icon("ic_fluent_text_whole_word_20_filled"), "主窗口侧边显示单词PK", "控制主窗口侧边栏中单词PK的显示状态", self.main_window_side_switch)
        self.addGroup(get_theme_icon("ic_fluent_chat_history_20_filled"), "主窗口侧边显示历史记录", "控制主窗口侧边栏中历史记录的显示状态", self.main_window_history_switch)
        self.addGroup(get_theme_icon("ic_fluent_content_settings_20_filled"), "设置图标显示", "控制主界面侧边栏中设置图标的显示状态", self.show_settings_icon_switch)
        self.addGroup(get_theme_icon("ic_fluent_shield_keyhole_20_filled"), "安全设置侧边栏位置", "调整安全设置侧边栏的显示位置", self.show_security_settings_switch)
        self.addGroup(get_theme_icon("ic_fluent_person_voice_20_filled"), "语音设置侧边栏位置", "调整语音设置侧边栏的显示位置", self.show_voice_settings_switch)
        self.addGroup(get_theme_icon("ic_fluent_chat_history_20_filled"), "历史记录设置侧边栏位置", "调整历史记录设置侧边栏的显示位置", self.show_history_settings_switch)
        
        # 加载设置
        self.load_settings()

    def load_settings(self):
        try:
            # 使用settings_reader模块获取设置
            sidebar_settings = get_settings_by_category("sidebar", {})
            sidebar_settings = sidebar_settings.get("sidebar", {})

            self.pumping_floating_side_comboBox.setCurrentIndex(sidebar_settings.get("pumping_floating_side", 0))
            self.pumping_reward_side_comboBox.setCurrentIndex(sidebar_settings.get("pumping_reward_side", 0))
            self.show_settings_icon_switch.setCurrentIndex(sidebar_settings.get("show_settings_icon", 1))
            self.main_window_history_switch.setCurrentIndex(sidebar_settings.get("main_window_history_switch", 1))
            self.main_window_side_switch.setCurrentIndex(sidebar_settings.get("main_window_side_switch", 2))
            self.show_security_settings_switch.setCurrentIndex(sidebar_settings.get("show_security_settings_switch", 1))
            self.show_voice_settings_switch.setCurrentIndex(sidebar_settings.get("show_voice_settings_switch", 1))
            self.show_history_settings_switch.setCurrentIndex(sidebar_settings.get("show_history_settings_switch", 1))

        except Exception as e:
            logger.error(f"加载设置时出错: {e}")

            self.pumping_floating_side_comboBox.setCurrentIndex(self.default_settings.get("pumping_floating_side", 0))
            self.pumping_reward_side_comboBox.setCurrentIndex(self.default_settings.get("pumping_reward_side", 0))
            self.show_settings_icon_switch.setCurrentIndex(self.default_settings.get("show_settings_icon", 1))
            self.main_window_history_switch.setCurrentIndex(self.default_settings.get("main_window_history_switch", 1))
            self.main_window_side_switch.setCurrentIndex(self.default_settings.get("main_window_side_switch", 2))
            self.show_security_settings_switch.setCurrentIndex(self.default_settings.get("show_security_settings_switch", 1))
            self.show_voice_settings_switch.setCurrentIndex(self.default_settings.get("show_voice_settings_switch", 1))
            self.show_history_settings_switch.setCurrentIndex(self.default_settings.get("show_history_settings_switch", 1))
            self.save_settings()    

    def save_settings(self):
        try:
            # 准备设置数据
            sidebar_settings = {
                "sidebar": {
                    "pumping_floating_side": self.pumping_floating_side_comboBox.currentIndex(),
                    "pumping_reward_side": self.pumping_reward_side_comboBox.currentIndex(),
                    "main_window_side_switch": self.main_window_side_switch.currentIndex(),
                    "main_window_history_switch": self.main_window_history_switch.currentIndex(),
                    "show_settings_icon": self.show_settings_icon_switch.currentIndex(),
                    "show_security_settings_switch": self.show_security_settings_switch.currentIndex(),
                    "show_voice_settings_switch": self.show_voice_settings_switch.currentIndex(),
                    "show_history_settings_switch": self.show_history_settings_switch.currentIndex()
                }
            }
            
            # 使用settings_reader模块保存设置
            update_settings("sidebar", sidebar_settings)
        except Exception as e:
            logger.error(f"保存设置时出错: {e}")