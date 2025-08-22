from qfluentwidgets import *
from qfluentwidgets import FluentIcon as FIF
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import os
import json
import glob
from loguru import logger

from app.common.config import get_theme_icon, load_custom_font
from app.common.path_utils import path_manager
from app.common.path_utils import open_file, ensure_dir


class PluginSettingsPage(GroupHeaderCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("插件设置")
        self.setBorderRadius(8)
        self.settings_file = path_manager.get_settings_path("plugin_settings.json")
        self.plugin_dir = path_manager.get_plugin_path("plugin")
        self.default_settings = {
            "run_plugins_on_startup": True,
            "fetch_plugin_list_on_startup": True,
            "selected_plugin": "主窗口",

        }

        self.run_plugins_on_startup_switch = SwitchButton()
        self.fetch_plugin_list_on_startup_switch = SwitchButton()
        self.plugin_combo_box = ComboBox()

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

        # 插件选择下拉框
        self.plugin_combo_box.setFont(QFont(load_custom_font(), 12))
        self.plugin_combo_box.currentTextChanged.connect(lambda: self._on_plugin_selected())

        self.addGroup(get_theme_icon("ic_fluent_arrow_sync_20_filled"), "自启动", "一键控制全部插件是否自启动", self.run_plugins_on_startup_switch)
        self.addGroup(get_theme_icon("ic_fluent_arrow_sync_20_filled"), "插件列表", "是否获取插件广场插件列表", self.fetch_plugin_list_on_startup_switch)
        self.addGroup(get_theme_icon("ic_fluent_window_inprivate_20_filled"), "浮窗按钮功能", "选择浮窗可打开的插件界面", self.plugin_combo_box)

        self.load_settings()
        self.save_settings()
        self._load_available_plugins()

    def _load_available_plugins(self):
        """扫描插件目录，获取有main.py入口文件的插件列表"""
        self.plugin_combo_box.clear()
        self.plugin_combo_box.addItem("主窗口")
        
        if not os.path.exists(self.plugin_dir):
            logger.warning(f"插件目录不存在: {self.plugin_dir}")
            return
        
        try:
            for item in os.listdir(self.plugin_dir):
                item_path = os.path.join(self.plugin_dir, item)
                
                # 只处理文件夹
                if not os.path.isdir(item_path):
                    continue
                
                # 检查是否有main.py入口文件
                main_py_path = os.path.join(item_path, "main.py")
                if not os.path.exists(main_py_path):
                    continue
                
                # 检查是否有plugin.json配置文件
                plugin_json_path = os.path.join(item_path, "plugin.json")
                if os.path.exists(plugin_json_path):
                    try:
                        with open_file(plugin_json_path, 'r', encoding='utf-8') as f:
                            plugin_config = json.load(f)
                            plugin_name = plugin_config.get("name", item)
                    except Exception as e:
                        logger.warning(f"读取插件 {item} 配置文件失败: {e}")
                        plugin_name = item
                else:
                    plugin_name = item
                
                # 添加到下拉框
                self.plugin_combo_box.addItem(plugin_name)
                logger.info(f"发现可用插件: {plugin_name}")
                
        except Exception as e:
            logger.error(f"扫描插件目录失败: {e}")
    
    def load_settings(self):
        try:
            if os.path.exists(self.settings_file):
                with open_file(self.settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    plugin_settings_settings = settings.get("plugin_settings", {})
                    
                    # 优先使用保存的文字选项
                    run_plugins_on_startup = plugin_settings_settings.get("run_plugins_on_startup", self.default_settings["run_plugins_on_startup"])
                    fetch_plugin_list_on_startup = plugin_settings_settings.get("fetch_plugin_list_on_startup", self.default_settings["fetch_plugin_list_on_startup"])

                    selected_plugin = plugin_settings_settings.get("selected_plugin", self.default_settings["selected_plugin"])

                    self.run_plugins_on_startup_switch.setChecked(run_plugins_on_startup)
                    self.fetch_plugin_list_on_startup_switch.setChecked(fetch_plugin_list_on_startup)
                    self.plugin_combo_box.setCurrentText(selected_plugin)

            else:
                logger.warning(f"设置文件不存在: {self.settings_file}")
                self.run_plugins_on_startup_switch.setChecked(self.default_settings["run_plugins_on_startup"])
                self.fetch_plugin_list_on_startup_switch.setChecked(self.default_settings["fetch_plugin_list_on_startup"])
                self.plugin_combo_box.setCurrentText(self.default_settings["selected_plugin"])

                self.save_settings()
        except Exception as e:
            self.run_plugins_on_startup_switch.setChecked(self.default_settings["run_plugins_on_startup"])
            self.fetch_plugin_list_on_startup_switch.setChecked(self.default_settings["fetch_plugin_list_on_startup"])
            self.plugin_combo_box.setCurrentText(self.default_settings["selected_plugin"])

            self.save_settings()
 
    def save_settings(self):
        # 先读取现有设置
        existing_settings = {}
        if os.path.exists(self.settings_file):
            with open_file(self.settings_file, 'r', encoding='utf-8') as f:
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
        plugin_settings_settings["selected_plugin"] = self.plugin_combo_box.currentText()

        ensure_dir(os.path.dirname(self.settings_file))
        with open_file(self.settings_file, 'w', encoding='utf-8') as f:
            json.dump(existing_settings, f, indent=4)
    
    def _on_plugin_selected(self):
        """插件选择变化时的回调函数"""
        selected_plugin = self.plugin_combo_box.currentText()
        logger.info(f"插件选择变化: {selected_plugin}")
        self.save_settings()