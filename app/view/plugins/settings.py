from qfluentwidgets import *
from qfluentwidgets import FluentIcon as FIF
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import os
import json
from loguru import logger

from app.common.config import get_theme_icon, load_custom_font


class PluginSettingsPage(GroupHeaderCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("插件设置")
        self.setBorderRadius(8)
        self.settings_file = "app/Settings/plugin_settings.json"
        self.default_settings = {
            "run_plugins_on_startup": True,
            "fetch_plugin_list_on_startup": True
        }

        self.run_plugins_on_startup_switch = SwitchButton()
        self.fetch_plugin_list_on_startup_switch = SwitchButton()

        # 插件运行开关
        self.run_plugins_on_startup_switch.setOnText("开启")
        self.run_plugins_on_startup_switch.setOffText("关闭")
        self.run_plugins_on_startup_switch.checkedChanged.connect(self.save_settings)
        self.run_plugins_on_startup_switch.setFont(QFont(load_custom_font(), 12))

        # 插件列表更新开关
        self.fetch_plugin_list_on_startup_switch.setOnText("开启")
        self.fetch_plugin_list_on_startup_switch.setOffText("关闭")
        self.fetch_plugin_list_on_startup_switch.checkedChanged.connect(self.save_settings)
        self.fetch_plugin_list_on_startup_switch.setFont(QFont(load_custom_font(), 12))

        self.addGroup(get_theme_icon("ic_fluent_arrow_sync_20_filled"), "自启动", "一键控制全部插件是否自启动", self.run_plugins_on_startup_switch)
        self.addGroup(get_theme_icon("ic_fluent_arrow_sync_20_filled"), "插件列表", "是否获取插件广场插件列表", self.fetch_plugin_list_on_startup_switch)

        self.load_settings()
        self.save_settings()

    def load_settings(self):
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    plugin_settings_settings = settings.get("plugin_settings", {})
                    
                    # 优先使用保存的文字选项
                    run_plugins_on_startup = plugin_settings_settings.get("run_plugins_on_startup", self.default_settings["run_plugins_on_startup"])
                    fetch_plugin_list_on_startup = plugin_settings_settings.get("fetch_plugin_list_on_startup", self.default_settings["fetch_plugin_list_on_startup"])

                    self.run_plugins_on_startup_switch.setChecked(run_plugins_on_startup)
                    self.fetch_plugin_list_on_startup_switch.setChecked(fetch_plugin_list_on_startup)
            else:
                logger.warning(f"设置文件不存在: {self.settings_file}")
                self.run_plugins_on_startup_switch.setChecked(self.default_settings["run_plugins_on_startup"])
                self.fetch_plugin_list_on_startup_switch.setChecked(self.default_settings["fetch_plugin_list_on_startup"])

                self.save_settings()
        except Exception as e:
            self.run_plugins_on_startup_switch.setChecked(self.default_settings["run_plugins_on_startup"])
            self.fetch_plugin_list_on_startup_switch.setChecked(self.default_settings["fetch_plugin_list_on_startup"])
            self.save_settings()
 
    def save_settings(self):
        # 先读取现有设置
        existing_settings = {}
        if os.path.exists(self.settings_file):
            with open(self.settings_file, 'r', encoding='utf-8') as f:
                try:
                    existing_settings = json.load(f)
                except json.JSONDecodeError:
                    existing_settings = {}
        
        # 更新plugin_settings部分的所有设置
        if "plugin_settings" not in existing_settings:
            existing_settings["plugin_settings"] = {}
            
        plugin_settings_settings = existing_settings["plugin_settings"]
        # 删除保存文字选项的代码
        plugin_settings_settings["run_plugins_on_startup"] = self.run_plugins_on_startup_switch.isChecked()
        plugin_settings_settings["fetch_plugin_list_on_startup"] = self.fetch_plugin_list_on_startup_switch.isChecked()
        
        os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
        with open(self.settings_file, 'w', encoding='utf-8') as f:
            json.dump(existing_settings, f, indent=4)