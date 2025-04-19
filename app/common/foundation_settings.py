from qfluentwidgets import *
from qfluentwidgets import FluentIcon as FIF
from PyQt5.QtGui import *

import json
import os
from loguru import logger

from app.common.config import load_custom_font

class foundation_settingsCard(GroupHeaderCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("基础设置")
        self.setBorderRadius(8)
        self.settings_file = "app/Settings/Settings.json"
        self.default_settings = {
            "self_starting_enabled": False,
            "pumping_floating_enabled": False,
            "pumping_floating_transparency_mode": 6,
            "main_window_mode": 0,
            "convenient_window_mode": 0,
            "settings_window_mode": 0,
            "main_window_size": 0,
            "convenient_window_size": 0,
            "settings_window_size": 0
        }

        self.self_starting_switch = SwitchButton()
        self.pumping_floating_switch = SwitchButton()
        self.pumping_floating_transparency_comboBox = ComboBox()
        self.main_window_comboBox = ComboBox()
        self.main_window_size_comboBox = ComboBox()
        self.convenient_window_comboBox = ComboBox()
        self.convenient_window_size_comboBox = ComboBox()
        self.settings_window_comboBox = ComboBox()
        self.settings_window_size_comboBox = ComboBox()

        # 开机自启动按钮
        self.self_starting_switch.setOnText("开启")
        self.self_starting_switch.setOffText("关闭")
        self.self_starting_switch.setFont(QFont(load_custom_font(), 14))
        self.self_starting_switch.checkedChanged.connect(self.on_pumping_floating_switch_changed)
        self.self_starting_switch.checkedChanged.connect(self.setting_startup)

        # 浮窗显示/隐藏按钮
        self.pumping_floating_switch.setOnText("显示")
        self.pumping_floating_switch.setOffText("隐藏")
        self.pumping_floating_switch.checkedChanged.connect(self.on_pumping_floating_switch_changed)
        self.pumping_floating_switch.setFont(QFont(load_custom_font(), 14))

        # 浮窗透明度设置下拉框
        self.pumping_floating_transparency_comboBox.setFixedWidth(200)
        self.pumping_floating_transparency_comboBox.addItems(["100%", "90%", "80%", "70%", "60%", "50%", "40%", "30%", "20%", "10%"])
        self.pumping_floating_transparency_comboBox.currentIndexChanged.connect(self.save_settings)
        self.pumping_floating_transparency_comboBox.setFont(QFont(load_custom_font(), 12))

        # 主窗口窗口显示位置下拉框
        self.main_window_comboBox.setFixedWidth(200)
        self.main_window_comboBox.addItems(["居中", "居中向下3/5"])
        self.main_window_comboBox.currentIndexChanged.connect(self.save_settings)
        self.main_window_comboBox.setFont(QFont(load_custom_font(), 12))

        # 主窗口窗口显示大小下拉框
        self.main_window_size_comboBox.setFixedWidth(200)
        self.main_window_size_comboBox.addItems(["800x600", "1200x800"])
        self.main_window_size_comboBox.currentIndexChanged.connect(self.save_settings)
        self.main_window_size_comboBox.setFont(QFont(load_custom_font(), 12))

        # 便捷抽人窗口显示位置下拉框
        self.convenient_window_comboBox.setFixedWidth(200)
        self.convenient_window_comboBox.addItems(["居中", "居中向下3/5"])
        self.convenient_window_comboBox.currentIndexChanged.connect(self.save_settings)
        self.convenient_window_comboBox.setFont(QFont(load_custom_font(), 12))

        # 便捷抽人窗口显示大小下拉框
        self.convenient_window_size_comboBox.setFixedWidth(200)
        self.convenient_window_size_comboBox.addItems(["800x600", "1200x800"])
        self.convenient_window_size_comboBox.currentIndexChanged.connect(self.save_settings)
        self.convenient_window_size_comboBox.setFont(QFont(load_custom_font(), 12))

        # 设置窗口显示位置下拉框
        self.settings_window_comboBox.setFixedWidth(200)
        self.settings_window_comboBox.addItems(["居中", "居中向下3/5"])
        self.settings_window_comboBox.currentIndexChanged.connect(self.save_settings)
        self.settings_window_comboBox.setFont(QFont(load_custom_font(), 12))

        # 设置窗口显示大小下拉框
        self.settings_window_size_comboBox.setFixedWidth(200)
        self.settings_window_size_comboBox.addItems(["800x600", "1200x800"])
        self.settings_window_size_comboBox.currentIndexChanged.connect(self.save_settings)
        self.settings_window_size_comboBox.setFont(QFont(load_custom_font(), 12))

        # 添加组件到分组中
        self.addGroup(FIF.PLAY, "开机自启", "系统启动时自动启动本应用(启用后将自动设置不显示主窗口)", self.self_starting_switch)
        self.addGroup(QIcon("app\\resource\\icon\\SecRandom_floating_100%.png"), "浮窗显隐", "设置便捷抽人的浮窗显示/隐藏", self.pumping_floating_switch)
        self.addGroup(FIF.ZOOM, "浮窗透明度", "设置便捷抽人的浮窗透明度", self.pumping_floating_transparency_comboBox)
        self.addGroup(FIF.ZOOM, "主窗口位置", "设置主窗口的显示位置", self.main_window_comboBox)
        self.addGroup(FIF.ZOOM, "主窗口大小", "设置主窗口的显示大小", self.main_window_size_comboBox)
        self.addGroup(FIF.ZOOM, "便捷抽人窗口位置", "设置便捷抽人窗口的显示位置", self.convenient_window_comboBox)
        self.addGroup(FIF.ZOOM, "便捷抽人窗口大小", "设置便捷抽人窗口的显示大小", self.convenient_window_size_comboBox)
        self.addGroup(FIF.ZOOM, "设置窗口位置", "设置设置窗口的显示位置", self.settings_window_comboBox)
        self.addGroup(FIF.ZOOM, "设置窗口大小", "设置设置窗口的显示大小", self.settings_window_size_comboBox)

        self.load_settings()
        self.save_settings()

    def on_pumping_floating_switch_changed(self, checked):
        self.save_settings()

    def setting_startup(self):
        import sys
        import os
        import platform

        # 获取当前程序路径
        executable = sys.executable
        logger.info(f"设置开机自启动的程序路径: {executable}")

        if not executable:
            logger.error("无法获取可执行文件路径")
            return

        try:
            # 读取设置文件
            with open('app/Settings/Settings.json', 'r', encoding='utf-8') as f:
                settings = json.load(f)
                foundation_settings = settings.get('foundation', {})
                self_starting_enabled = foundation_settings.get('self_starting_enabled', False)

                # 处理启动文件夹操作
                if platform.system() != 'Windows':
                    self.self_starting_switch.setChecked(self.default_settings["self_starting_enabled"])
                    logger.error("仅支持Windows系统")
                    return

                # 获取启动文件夹路径
                startup_folder = os.path.join(
                    os.getenv('APPDATA'),
                    r'Microsoft\Windows\Start Menu\Programs\Startup'
                )
                shortcut_path = os.path.join(startup_folder, 'SecRandom.lnk')

                if self_starting_enabled:
                    try:
                        # 创建快捷方式
                        import winshell
                        from win32com.client import Dispatch

                        shell = Dispatch('WScript.Shell')
                        shortcut = shell.CreateShortCut(shortcut_path)
                        shortcut.Targetpath = executable
                        shortcut.WorkingDirectory = os.path.dirname(executable)
                        shortcut.save()
                        logger.success("开机自启动设置成功")
                    except Exception as e:
                        logger.error(f"创建快捷方式失败: {e}")
                else:
                    try:
                        if os.path.exists(shortcut_path):
                            os.remove(shortcut_path)
                            logger.success("开机自启动取消成功")
                        else:
                            logger.info("开机自启动项不存在，无需取消")
                    except Exception as e:
                        logger.error(f"删除快捷方式失败: {e}")

        except json.JSONDecodeError as e:
            logger.error(f"设置文件格式错误: {e}")
        except Exception as e:
            logger.error(f"读取设置文件时出错: {e}")

        
    def load_settings(self):
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    foundation_settings = settings.get("foundation", {})
                    
                    # 优先使用保存的文字选项
                    self_starting_enabled = foundation_settings.get("self_starting_enabled", self.default_settings["self_starting_enabled"])

                    pumping_floating_enabled = foundation_settings.get("pumping_floating_enabled", self.default_settings["pumping_floating_enabled"])
                        
                    main_window_mode = foundation_settings.get("main_window_mode", self.default_settings["main_window_mode"])
                    if main_window_mode < 0 or main_window_mode >= self.main_window_comboBox.count():
                        # 如果索引值无效，则使用默认值
                        main_window_mode = self.default_settings["main_window_mode"]
                        
                    convenient_window_mode = foundation_settings.get("convenient_window_mode", self.default_settings["convenient_window_mode"])
                    if convenient_window_mode < 0 or convenient_window_mode >= self.convenient_window_comboBox.count():
                        # 如果索引值无效，则使用默认值
                        convenient_window_mode = self.default_settings["convenient_window_mode"]

                    pumping_floating_transparency_mode = foundation_settings.get("pumping_floating_transparency_mode", self.default_settings["pumping_floating_transparency_mode"])
                    if pumping_floating_transparency_mode < 0 or pumping_floating_transparency_mode >= self.pumping_floating_transparency_comboBox.count():
                        # 如果索引值无效，则使用默认值
                        pumping_floating_transparency_mode = self.default_settings["pumping_floating_transparency_mode"]

                    settings_window_mode = foundation_settings.get("settings_window_mode", self.default_settings["settings_window_mode"])
                    if settings_window_mode < 0 or settings_window_mode >= self.settings_window_comboBox.count():
                        # 如果索引值无效，则使用默认值
                        settings_window_mode = self.default_settings["settings_window_mode"]

                    main_window_size = foundation_settings.get("main_window_size", self.default_settings["main_window_size"])
                    if main_window_size < 0 or main_window_size >= self.settings_window_comboBox.count():
                        # 如果索引值无效，则使用默认值
                        main_window_size = self.default_settings["main_window_size"]

                    convenient_window_size = foundation_settings.get("convenient_window_size", self.default_settings["convenient_window_size"])
                    if convenient_window_size < 0 or convenient_window_size >= self.settings_window_comboBox.count():
                        # 如果索引值无效，则使用默认值
                        convenient_window_size = self.default_settings["convenient_window_size"]

                    settings_window_size = foundation_settings.get("settings_window_size", self.default_settings["settings_window_size"])
                    if settings_window_size < 0 or settings_window_size >= self.settings_window_comboBox.count():
                        # 如果索引值无效，则使用默认值
                        settings_window_size = self.default_settings["settings_window_size"]

                    self.self_starting_switch.setChecked(self_starting_enabled)
                    self.pumping_floating_switch.setChecked(pumping_floating_enabled)
                    self.pumping_floating_transparency_comboBox.setCurrentIndex(pumping_floating_transparency_mode)
                    self.main_window_comboBox.setCurrentIndex(main_window_mode)
                    self.convenient_window_comboBox.setCurrentIndex(convenient_window_mode)
                    self.settings_window_comboBox.setCurrentIndex(settings_window_mode)
                    self.main_window_size_comboBox.setCurrentIndex(main_window_size)
                    self.convenient_window_size_comboBox.setCurrentIndex(convenient_window_size)
                    self.settings_window_size_comboBox.setCurrentIndex(settings_window_size)
                    logger.info(f"加载基础设置完成")
            else:
                logger.warning(f"设置文件不存在: {self.settings_file}")
                self.self_starting_switch.setChecked(self.default_settings["self_starting_enabled"])
                self.pumping_floating_switch.setChecked(self.default_settings["pumping_floating_enabled"])
                self.pumping_floating_transparency_comboBox.setCurrentIndex(self.default_settings["pumping_floating_transparency_mode"])
                self.main_window_comboBox.setCurrentIndex(self.default_settings["main_window_mode"])
                self.convenient_window_comboBox.setCurrentIndex(self.default_settings["convenient_window_mode"])
                self.settings_window_comboBox.setCurrentIndex(self.default_settings["settings_window_mode"])
                self.main_window_size_comboBox.setCurrentIndex(self.default_settings["main_window_size"])
                self.convenient_window_size_comboBox.setCurrentIndex(self.default_settings["convenient_window_size"])
                self.settings_window_size_comboBox.setCurrentIndex(self.default_settings["settings_window_size"])
                self.save_settings()
        except Exception as e:
            logger.error(f"加载设置时出错: {e}")
            self.self_starting_switch.setChecked(self.default_settings["self_starting_enabled"])
            self.pumping_floating_switch.setChecked(self.default_settings["pumping_floating_enabled"])
            self.pumping_floating_transparency_comboBox.setCurrentIndex(self.default_settings["pumping_floating_transparency_mode"])
            self.main_window_comboBox.setCurrentIndex(self.default_settings["main_window_mode"])
            self.convenient_window_comboBox.setCurrentIndex(self.default_settings["convenient_window_mode"])
            self.settings_window_comboBox.setCurrentIndex(self.default_settings["settings_window_mode"])
            self.main_window_size_comboBox.setCurrentIndex(self.default_settings["main_window_size"])
            self.convenient_window_size_comboBox.setCurrentIndex(self.default_settings["convenient_window_size"])
            self.settings_window_size_comboBox.setCurrentIndex(self.default_settings["settings_window_size"])
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
        
        # 更新foundation部分的所有设置
        if "foundation" not in existing_settings:
            existing_settings["foundation"] = {}
            
        foundation_settings = existing_settings["foundation"]
        # 删除保存文字选项的代码
        foundation_settings["self_starting_enabled"] = self.self_starting_switch.isChecked()
        foundation_settings["pumping_floating_enabled"] = self.pumping_floating_switch.isChecked()
        foundation_settings["pumping_floating_transparency_mode"] = self.pumping_floating_transparency_comboBox.currentIndex()
        foundation_settings["main_window_mode"] = self.main_window_comboBox.currentIndex()
        foundation_settings["convenient_window_mode"] = self.convenient_window_comboBox.currentIndex()
        foundation_settings["settings_window_mode"] = self.settings_window_comboBox.currentIndex()
        foundation_settings["main_window_size"] = self.main_window_size_comboBox.currentIndex()
        foundation_settings["convenient_window_size"] = self.convenient_window_size_comboBox.currentIndex()
        foundation_settings["settings_window_size"] = self.settings_window_size_comboBox.currentIndex()
        
        os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
        with open(self.settings_file, 'w', encoding='utf-8') as f:
            json.dump(existing_settings, f, indent=4)