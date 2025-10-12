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
from app.common.global_signals import font_signal

is_dark = is_dark_theme(qconfig)

class personal_settingsCard(GroupHeaderCardWidget):
    # 定义背景设置变化信号
    background_settings_changed = pyqtSignal()
    # 定义字体变更信号
    font_changed = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("个性化")
        self.setBorderRadius(8)
        self.settings_file = path_manager.get_settings_path('custom_settings.json')
        self.default_settings = {
            "enable_background_icon": False,
            "background_blur": 10,
            "background_brightness": 30,
            "enable_main_background": False,
            "enable_settings_background": False,
            "enable_flash_background": False,
            "main_background_image": "",
            "settings_background_image": "",
            "flash_background_image": "",
            "font_family": "HarmonyOS Sans SC",
            "enable_background_color": False,
            "enable_main_background_color": False,
            "enable_settings_background_color": False,
            "enable_flash_background_color": False,
            "main_background_color": "#FFFFFF",
            "settings_background_color": "#FFFFFF",
            "flash_background_color": "#FFFFFF"
        }

        # 背景图标开关
        self.background_icon_switch = SwitchButton()
        self.background_icon_switch.setOnText("开启")
        self.background_icon_switch.setOffText("关闭")
        self.background_icon_switch.setFont(QFont(load_custom_font(), 12))
        self.background_icon_switch.checkedChanged.connect(self.on_background_icon_switch_changed)
        
        # 背景图标选择按钮
        self.background_icon_button = PushButton("打开背景图文件夹")
        self.background_icon_button.setFont(QFont(load_custom_font(), 12))
        self.background_icon_button.clicked.connect(self.on_background_icon_button_clicked)

        # 背景模糊度SpinBox
        self.blur_spinbox = SpinBox()
        self.blur_spinbox.setRange(0, 20)
        self.blur_spinbox.setValue(0)
        self.blur_spinbox.setSingleStep(1)
        self.blur_spinbox.setFont(QFont(load_custom_font(), 12))
        self.blur_spinbox.valueChanged.connect(self.save_settings)
        
        # 背景亮度SpinBox
        self.brightness_spinbox = SpinBox()
        self.brightness_spinbox.setRange(0, 200)
        self.brightness_spinbox.setValue(100)
        self.brightness_spinbox.setSingleStep(1)
        self.brightness_spinbox.setFont(QFont(load_custom_font(), 12))
        self.brightness_spinbox.valueChanged.connect(self.save_settings)

        # 主界面背景图开关
        self.main_background_switch = SwitchButton()
        self.main_background_switch.setOnText("开启")
        self.main_background_switch.setOffText("关闭")
        self.main_background_switch.setFont(QFont(load_custom_font(), 12))
        self.main_background_switch.checkedChanged.connect(self.save_settings)
        
        # 设置界面背景图开关
        self.settings_background_switch = SwitchButton()
        self.settings_background_switch.setOnText("开启")
        self.settings_background_switch.setOffText("关闭")
        self.settings_background_switch.setFont(QFont(load_custom_font(), 12))
        self.settings_background_switch.checkedChanged.connect(self.save_settings)
        
        # 闪抽界面背景图开关
        self.flash_background_switch = SwitchButton()
        self.flash_background_switch.setOnText("开启")
        self.flash_background_switch.setOffText("关闭")
        self.flash_background_switch.setFont(QFont(load_custom_font(), 12))
        self.flash_background_switch.checkedChanged.connect(self.save_settings)
        
        # 主界面背景图下拉框
        self.main_background_combo = ComboBox()
        self.main_background_combo.setFont(QFont(load_custom_font(), 12))
        self.main_background_combo.currentIndexChanged.connect(self.save_settings)
        
        # 设置界面背景图下拉框
        self.settings_background_combo = ComboBox()
        self.settings_background_combo.setFont(QFont(load_custom_font(), 12))
        self.settings_background_combo.currentIndexChanged.connect(self.save_settings)
        
        # 闪抽界面背景图下拉框
        self.flash_background_combo = ComboBox()
        self.flash_background_combo.setFont(QFont(load_custom_font(), 12))
        self.flash_background_combo.currentIndexChanged.connect(self.save_settings)
        
        # 字体选择下拉框
        self.font_combo = ComboBox()
        self.font_combo.setFont(QFont(load_custom_font(), 12))
        # 添加字体到下拉框
        self.font_combo.addItem("HarmonyOS Sans SC")
        self.font_combo.addItem("汉仪文黑-85W")
        # 然后添加系统字体
        for font in sorted(QFontDatabase().families()):
            self.font_combo.addItem(font)
        self.font_combo.currentIndexChanged.connect(self.save_settings)
        self.font_combo.currentIndexChanged.connect(lambda: font_signal.font_changed.emit(self.font_combo.currentText()))
        self.font_combo.currentIndexChanged.connect(lambda: self.font_changed.emit(self.font_combo.currentText()))

        # 背景颜色开关
        self.background_color_switch = SwitchButton()
        self.background_color_switch.setOnText("开启")
        self.background_color_switch.setOffText("关闭")
        self.background_color_switch.setFont(QFont(load_custom_font(), 12))
        self.background_color_switch.checkedChanged.connect(self.on_background_color_switch_changed)
        
        # 主界面背景颜色开关
        self.main_background_color_switch = SwitchButton()
        self.main_background_color_switch.setOnText("开启")
        self.main_background_color_switch.setOffText("关闭")
        self.main_background_color_switch.setFont(QFont(load_custom_font(), 12))
        self.main_background_color_switch.checkedChanged.connect(self.on_main_background_color_switch_changed)
        
        # 设置界面背景颜色开关
        self.settings_background_color_switch = SwitchButton()
        self.settings_background_color_switch.setOnText("开启")
        self.settings_background_color_switch.setOffText("关闭")
        self.settings_background_color_switch.setFont(QFont(load_custom_font(), 12))
        self.settings_background_color_switch.checkedChanged.connect(self.on_settings_background_color_switch_changed)
        
        # 闪抽界面背景颜色开关
        self.flash_background_color_switch = SwitchButton()
        self.flash_background_color_switch.setOnText("开启")
        self.flash_background_color_switch.setOffText("关闭")
        self.flash_background_color_switch.setFont(QFont(load_custom_font(), 12))
        self.flash_background_color_switch.checkedChanged.connect(self.on_flash_background_color_switch_changed)
        
        # 主界面背景颜色选择器
        self.main_background_color_button = PushButton("主界面背景颜色")
        self.main_background_color_button.setFont(QFont(load_custom_font(), 12))
        self.main_background_color_button.clicked.connect(lambda: self.on_background_color_dialog("main"))
        
        # 设置界面背景颜色选择器
        self.settings_background_color_button = PushButton("设置界面背景颜色")
        self.settings_background_color_button.setFont(QFont(load_custom_font(), 12))
        self.settings_background_color_button.clicked.connect(lambda: self.on_background_color_dialog("settings"))
        
        # 闪抽界面背景颜色选择器
        self.flash_background_color_button = PushButton("闪抽界面背景颜色")
        self.flash_background_color_button.setFont(QFont(load_custom_font(), 12))
        self.flash_background_color_button.clicked.connect(lambda: self.on_background_color_dialog("flash"))

        # 添加个性化设置组
        self.addGroup(get_theme_icon("ic_fluent_window_ad_20_filled"), "界面背景图", "是否启用界面背景图", self.background_icon_switch)
        self.addGroup(get_theme_icon("ic_fluent_window_ad_20_filled"), "选择背景图", "点击选择自定义背景图", self.background_icon_button)
        self.addGroup(get_theme_icon("ic_fluent_window_ad_20_filled"), "背景模糊度", "调整背景图片的模糊程度(0-20)", self.blur_spinbox)
        self.addGroup(get_theme_icon("ic_fluent_window_ad_20_filled"), "背景亮度", "调整背景图片的亮度(0-200)", self.brightness_spinbox)
        
        # 添加各界面背景图设置组
        self.addGroup(get_theme_icon("ic_fluent_window_ad_20_filled"), "主界面背景图", "是否启用主界面背景图", self.main_background_switch)
        self.addGroup(get_theme_icon("ic_fluent_window_ad_20_filled"), "主界面背景图选择", "选择主界面使用的背景图片", self.main_background_combo)
        
        self.addGroup(get_theme_icon("ic_fluent_window_ad_20_filled"), "设置界面背景图", "是否启用设置界面背景图", self.settings_background_switch)
        self.addGroup(get_theme_icon("ic_fluent_window_ad_20_filled"), "设置界面背景图选择", "选择设置界面使用的背景图片", self.settings_background_combo)
        
        self.addGroup(get_theme_icon("ic_fluent_window_ad_20_filled"), "闪抽界面背景图", "是否启用闪抽界面背景图", self.flash_background_switch)
        self.addGroup(get_theme_icon("ic_fluent_window_ad_20_filled"), "闪抽界面背景图选择", "选择闪抽界面使用的背景图片", self.flash_background_combo)
        
        # 添加背景颜色设置组
        self.addGroup(get_theme_icon("ic_fluent_paint_brush_20_filled"), "界面背景颜色", "是否启用界面背景颜色", self.background_color_switch)
        self.addGroup(get_theme_icon("ic_fluent_paint_brush_20_filled"), "主界面背景颜色", "是否启用主界面背景颜色", self.main_background_color_switch)
        self.addGroup(get_theme_icon("ic_fluent_paint_brush_20_filled"), "主界面背景颜色选择", "选择主界面使用的背景颜色", self.main_background_color_button)
        self.addGroup(get_theme_icon("ic_fluent_paint_brush_20_filled"), "设置界面背景颜色", "是否启用设置界面背景颜色", self.settings_background_color_switch)
        self.addGroup(get_theme_icon("ic_fluent_paint_brush_20_filled"), "设置界面背景颜色选择", "选择设置界面使用的背景颜色", self.settings_background_color_button)
        self.addGroup(get_theme_icon("ic_fluent_paint_brush_20_filled"), "闪抽界面背景颜色", "是否启用闪抽界面背景颜色", self.flash_background_color_switch)
        self.addGroup(get_theme_icon("ic_fluent_paint_brush_20_filled"), "闪抽界面背景颜色选择", "选择闪抽界面使用的背景颜色", self.flash_background_color_button)
        
        # 添加字体设置组
        self.addGroup(get_theme_icon("ic_fluent_text_font_20_filled"), "字体设置", "选择应用程序使用的字体", self.font_combo)

        # 初始化背景颜色属性
        self.main_background_color = self.default_settings["main_background_color"]
        self.settings_background_color = self.default_settings["settings_background_color"]
        self.flash_background_color = self.default_settings["flash_background_color"]
        
        # 加载设置
        self.load_settings()
        self.save_settings()

    def load_settings(self):
        try:
            if path_manager.file_exists(self.settings_file):
                with open_file(self.settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    personal_settings = settings.get("personal", {})
                    
                    # 加载背景图标开关状态
                    background_icon_enabled = personal_settings.get("enable_background_icon", self.default_settings["enable_background_icon"])
                    
                    # 加载背景颜色开关状态
                    background_color_enabled = personal_settings.get("enable_background_color", self.default_settings["enable_background_color"])
                    
                    # 检查互斥性：如果两者都启用，则禁用背景颜色开关
                    if background_icon_enabled and background_color_enabled:
                        background_color_enabled = False
                    
                    # 设置开关状态
                    self.background_icon_switch.setChecked(background_icon_enabled)
                    self.background_color_switch.setChecked(background_color_enabled)
                    
                    # 加载背景模糊度设置
                    self.blur_spinbox.setValue(personal_settings.get("background_blur", self.default_settings["background_blur"]))
                    
                    # 加载背景亮度设置
                    self.brightness_spinbox.setValue(personal_settings.get("background_brightness", self.default_settings["background_brightness"]))
                    
                    # 加载主界面背景图开关状态
                    self.main_background_switch.setChecked(personal_settings.get("enable_main_background", self.default_settings["enable_main_background"]))
                    
                    # 加载设置界面背景图开关状态
                    self.settings_background_switch.setChecked(personal_settings.get("enable_settings_background", self.default_settings["enable_settings_background"]))
                    
                    # 加载闪抽界面背景图开关状态
                    self.flash_background_switch.setChecked(personal_settings.get("enable_flash_background", self.default_settings["enable_flash_background"]))
                    
                    # 加载背景图片列表
                    self._load_background_images()
                    
                    # 加载主界面背景图选择
                    main_bg_image = personal_settings.get("main_background_image", self.default_settings["main_background_image"])
                    if main_bg_image and main_bg_image in [self.main_background_combo.itemText(i) for i in range(self.main_background_combo.count())]:
                        self.main_background_combo.setCurrentText(main_bg_image)
                    
                    # 加载设置界面背景图选择
                    settings_bg_image = personal_settings.get("settings_background_image", self.default_settings["settings_background_image"])
                    if settings_bg_image and settings_bg_image in [self.settings_background_combo.itemText(i) for i in range(self.settings_background_combo.count())]:
                        self.settings_background_combo.setCurrentText(settings_bg_image)
                    
                    # 加载闪抽界面背景图选择
                    flash_bg_image = personal_settings.get("flash_background_image", self.default_settings["flash_background_image"])
                    if flash_bg_image and flash_bg_image in [self.flash_background_combo.itemText(i) for i in range(self.flash_background_combo.count())]:
                        self.flash_background_combo.setCurrentText(flash_bg_image)
                    
                    # 加载字体设置
                    font_family = personal_settings.get("font_family", self.default_settings["font_family"])
                    if font_family and font_family in [self.font_combo.itemText(i) for i in range(self.font_combo.count())]:
                        self.font_combo.setCurrentText(font_family)
                    
                    # 加载主界面背景颜色开关状态
                    self.main_background_color_switch.setChecked(personal_settings.get("enable_main_background_color", self.default_settings["enable_main_background_color"]))
                    
                    # 加载设置界面背景颜色开关状态
                    self.settings_background_color_switch.setChecked(personal_settings.get("enable_settings_background_color", self.default_settings["enable_settings_background_color"]))
                    
                    # 加载闪抽界面背景颜色开关状态
                    self.flash_background_color_switch.setChecked(personal_settings.get("enable_flash_background_color", self.default_settings["enable_flash_background_color"]))
                    
                    # 加载主界面背景颜色
                    main_bg_color = personal_settings.get("main_background_color", self.default_settings["main_background_color"])
                    self.main_background_color = main_bg_color
                    
                    # 加载设置界面背景颜色
                    settings_bg_color = personal_settings.get("settings_background_color", self.default_settings["settings_background_color"])
                    self.settings_background_color = settings_bg_color
                    
                    # 加载闪抽界面背景颜色
                    flash_bg_color = personal_settings.get("flash_background_color", self.default_settings["flash_background_color"])
                    self.flash_background_color = flash_bg_color

            else:
                # logger.error(f"设置文件不存在: {self.settings_file}")
                self.background_icon_switch.setChecked(self.default_settings["enable_background_icon"])
                self.blur_spinbox.setValue(self.default_settings["background_blur"])
                self.brightness_spinbox.setValue(self.default_settings["background_brightness"])
                self.main_background_switch.setChecked(self.default_settings["enable_main_background"])
                self.settings_background_switch.setChecked(self.default_settings["enable_settings_background"])
                self.flash_background_switch.setChecked(self.default_settings["enable_flash_background"])
                self.background_color_switch.setChecked(self.default_settings["enable_background_color"])
                self.main_background_color_switch.setChecked(self.default_settings["enable_main_background_color"])
                self.settings_background_color_switch.setChecked(self.default_settings["enable_settings_background_color"])
                self.flash_background_color_switch.setChecked(self.default_settings["enable_flash_background_color"])
                self.main_background_color = self.default_settings["main_background_color"]
                self.settings_background_color = self.default_settings["settings_background_color"]
                self.flash_background_color = self.default_settings["flash_background_color"]
                
                self.save_settings()
        except Exception as e:
            logger.error(f"加载设置时出错: {e}")
            self.background_icon_switch.setChecked(self.default_settings["enable_background_icon"])
            self.blur_spinbox.setValue(self.default_settings["background_blur"])
            self.brightness_spinbox.setValue(self.default_settings["background_brightness"])
            self.main_background_switch.setChecked(self.default_settings["enable_main_background"])
            self.settings_background_switch.setChecked(self.default_settings["enable_settings_background"])
            self.flash_background_switch.setChecked(self.default_settings["enable_flash_background"])
            self.background_color_switch.setChecked(self.default_settings["enable_background_color"])
            self.main_background_color_switch.setChecked(self.default_settings["enable_main_background_color"])
            self.settings_background_color_switch.setChecked(self.default_settings["enable_settings_background_color"])
            self.flash_background_color_switch.setChecked(self.default_settings["enable_flash_background_color"])
            self.main_background_color = self.default_settings["main_background_color"]
            self.settings_background_color = self.default_settings["settings_background_color"]
            self.flash_background_color = self.default_settings["flash_background_color"]
        
        # 根据总开关状态设置子开关的启用/禁用状态
        self.on_background_icon_switch_changed()
        self.on_background_color_switch_changed()

    def save_settings(self):
        # 先读取现有设置
        existing_settings = {}
        if path_manager.file_exists(self.settings_file):
            with open_file(self.settings_file, 'r', encoding='utf-8') as f:
                try:
                    existing_settings = json.load(f)
                except json.JSONDecodeError:
                    existing_settings = {}
        
        # 更新personal部分的所有设置
        if "personal" not in existing_settings:
            existing_settings["personal"] = {}
            
        personal_settings = existing_settings["personal"]
        
        # 检查互斥性：背景图标和背景颜色不能同时启用
        background_icon_enabled = self.background_icon_switch.isChecked()
        background_color_enabled = self.background_color_switch.isChecked()
        
        if background_icon_enabled and background_color_enabled:
            # 如果两者都启用，则禁用背景颜色开关
            self.background_color_switch.setChecked(False)
            background_color_enabled = False
        
        # 保存背景图标开关状态
        personal_settings["enable_background_icon"] = background_icon_enabled
        
        # 保存背景模糊度设置
        personal_settings["background_blur"] = self.blur_spinbox.value()
        
        # 保存背景亮度设置
        personal_settings["background_brightness"] = self.brightness_spinbox.value()
        
        # 保存主界面背景图开关状态
        personal_settings["enable_main_background"] = self.main_background_switch.isChecked()
        
        # 保存设置界面背景图开关状态
        personal_settings["enable_settings_background"] = self.settings_background_switch.isChecked()
        
        # 保存闪抽界面背景图开关状态
        personal_settings["enable_flash_background"] = self.flash_background_switch.isChecked()
        
        # 保存主界面背景图选择
        personal_settings["main_background_image"] = self.main_background_combo.currentText() if self.main_background_combo.currentIndex() >= 0 else ""
        
        # 保存设置界面背景图选择
        personal_settings["settings_background_image"] = self.settings_background_combo.currentText() if self.settings_background_combo.currentIndex() >= 0 else ""
        
        # 保存闪抽界面背景图选择
        personal_settings["flash_background_image"] = self.flash_background_combo.currentText() if self.flash_background_combo.currentIndex() >= 0 else ""
        
        # 保存字体设置
        if self.font_combo.currentIndex() >= 0:
            new_font = self.font_combo.currentText()
            # 只有当字体确实发生变化时才更新设置
            if "font_family" not in personal_settings or personal_settings["font_family"] != new_font:
                personal_settings["font_family"] = new_font
        
        # 保存背景颜色开关状态
        personal_settings["enable_background_color"] = background_color_enabled
        
        # 保存主界面背景颜色开关状态
        personal_settings["enable_main_background_color"] = self.main_background_color_switch.isChecked()
        
        # 保存设置界面背景颜色开关状态
        personal_settings["enable_settings_background_color"] = self.settings_background_color_switch.isChecked()
        
        # 保存闪抽界面背景颜色开关状态
        personal_settings["enable_flash_background_color"] = self.flash_background_color_switch.isChecked()
        
        # 保存主界面背景颜色
        personal_settings["main_background_color"] = self.main_background_color
        
        # 保存设置界面背景颜色
        personal_settings["settings_background_color"] = self.settings_background_color
        
        # 保存闪抽界面背景颜色
        personal_settings["flash_background_color"] = self.flash_background_color

        os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
        with open_file(self.settings_file, 'w', encoding='utf-8') as f:
            json.dump(existing_settings, f, indent=4)
    
    def on_background_icon_switch_changed(self):
        """处理背景图标总开关变化"""
        # 获取总开关状态
        is_enabled = self.background_icon_switch.isChecked()
        
        # 如果背景图标开关打开，则关闭背景颜色开关
        if is_enabled:
            self.background_color_switch.setChecked(False)
        
        # 如果总开关关闭，则关闭所有子开关并禁用它们
        if not is_enabled:
            # 保存当前子开关状态
            self.main_background_switch.setChecked(False)
            self.settings_background_switch.setChecked(False)
            self.flash_background_switch.setChecked(False)
            
            # 禁用子开关和下拉框
            self.main_background_switch.setEnabled(False)
            self.settings_background_switch.setEnabled(False)
            self.flash_background_switch.setEnabled(False)
            self.main_background_combo.setEnabled(False)
            self.settings_background_combo.setEnabled(False)
            self.flash_background_combo.setEnabled(False)
        else:
            # 启用子开关和下拉框
            self.main_background_switch.setEnabled(True)
            self.settings_background_switch.setEnabled(True)
            self.flash_background_switch.setEnabled(True)
            self.main_background_combo.setEnabled(True)
            self.settings_background_combo.setEnabled(True)
            self.flash_background_combo.setEnabled(True)
        
        # 保存设置
        self.save_settings()
    
    def on_main_background_color_switch_changed(self):
        """处理主界面背景颜色开关变化"""
        # 获取主界面开关状态
        is_enabled = self.main_background_color_switch.isChecked()
        
        # 根据开关状态启用/禁用颜色选择器
        self.main_background_color_button.setEnabled(is_enabled)
        
        # 保存设置
        self.save_settings()
    
    def on_settings_background_color_switch_changed(self):
        """处理设置界面背景颜色开关变化"""
        # 获取设置界面开关状态
        is_enabled = self.settings_background_color_switch.isChecked()
        
        # 根据开关状态启用/禁用颜色选择器
        self.settings_background_color_button.setEnabled(is_enabled)
        
        # 保存设置
        self.save_settings()
    
    def on_flash_background_color_switch_changed(self):
        """处理闪抽界面背景颜色开关变化"""
        # 获取闪抽界面开关状态
        is_enabled = self.flash_background_color_switch.isChecked()
        
        # 根据开关状态启用/禁用颜色选择器
        self.flash_background_color_button.setEnabled(is_enabled)
        
        # 保存设置
        self.save_settings()

    def on_background_color_dialog(self, color_type):
        """处理背景颜色选择对话框
        
        Args:
            color_type: 颜色类型，可以是 "main"、"settings" 或 "flash"
        """
        # 根据颜色类型确定默认颜色和标题
        if color_type == "main":
            default_color = QColor(self.default_settings["main_background_color"])
            dialog_title = "主界面背景颜色"
            current_color = QColor(self.main_background_color)
        elif color_type == "settings":
            default_color = QColor(self.default_settings["settings_background_color"])
            dialog_title = "设置界面背景颜色"
            current_color = QColor(self.settings_background_color)
        elif color_type == "flash":
            default_color = QColor(self.default_settings["flash_background_color"])
            dialog_title = "闪抽界面背景颜色"
            current_color = QColor(self.flash_background_color)
        else:
            return
        
        # 创建颜色选择对话框
        color_dialog = ColorDialog(current_color, dialog_title, self, enableAlpha=False)
        color_dialog.setModal(False)
        color_dialog.colorChanged.connect(lambda color: self.save_background_color_settings(color.name(), color_type))
        color_dialog.setFont(QFont(load_custom_font(), 12))
        color_dialog.show()

    def save_background_color_settings(self, color_value, color_type):
        """保存背景颜色设置
        
        Args:
            color_value: 颜色值（十六进制字符串）
            color_type: 颜色类型，可以是 "main"、"settings" 或 "flash"
        """
        # 根据颜色类型设置对应的颜色值
        if color_type == "main":
            self.main_background_color = color_value
        elif color_type == "settings":
            self.settings_background_color = color_value
        elif color_type == "flash":
            self.flash_background_color = color_value
        
        # 保存设置
        self.save_settings()
    
    def on_background_color_switch_changed(self):
        """处理背景颜色总开关变化"""
        # 获取总开关状态
        is_enabled = self.background_color_switch.isChecked()
        
        # 如果背景颜色开关打开，则关闭背景图标开关
        if is_enabled:
            self.background_icon_switch.setChecked(False)
        
        # 如果总开关关闭，则关闭所有子开关并禁用它们
        if not is_enabled:
            # 关闭页面开关
            self.main_background_color_switch.setChecked(False)
            self.settings_background_color_switch.setChecked(False)
            self.flash_background_color_switch.setChecked(False)
            
            # 禁用页面开关
            self.main_background_color_switch.setEnabled(False)
            self.settings_background_color_switch.setEnabled(False)
            self.flash_background_color_switch.setEnabled(False)
            
            # 禁用颜色选择器
            self.main_background_color_button.setEnabled(False)
            self.settings_background_color_button.setEnabled(False)
            self.flash_background_color_button.setEnabled(False)
        else:
            # 启用页面开关
            self.main_background_color_switch.setEnabled(True)
            self.settings_background_color_switch.setEnabled(True)
            self.flash_background_color_switch.setEnabled(True)
            
            # 根据各个页面开关的状态启用/禁用颜色选择器
            self.main_background_color_button.setEnabled(self.main_background_color_switch.isChecked())
            self.settings_background_color_button.setEnabled(self.settings_background_color_switch.isChecked())
            self.flash_background_color_button.setEnabled(self.flash_background_color_switch.isChecked())
        
        # 保存设置
        self.save_settings()
    
    def on_background_icon_button_clicked(self):
        """背景图标文件夹打开按钮点击处理函数"""
        # 获取背景图标文件夹路径
        background_dir = path_manager.get_resource_path("images/background")
        
        # 确保文件夹存在
        os.makedirs(background_dir, exist_ok=True)
        
        # 打开文件夹
        import subprocess
        if platform.system() == "Windows":
            subprocess.run(["explorer", background_dir])
        
        # 显示提示消息
        InfoBar.info(
            title="背景图标文件夹",
            content="已打开背景图标文件夹，您可以将图片文件复制到此文件夹中",
            duration=3000,
            parent=self
        )
        
        # 刷新背景图片列表
        self._load_background_images()
    
    def _load_background_images(self):
        """加载背景图片列表到下拉框"""
        # 获取背景图标文件夹路径
        background_dir = path_manager.get_resource_path("images/background")
        
        # 确保文件夹存在
        os.makedirs(background_dir, exist_ok=True)
        
        # 支持的图片格式
        image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.svg']
        
        # 获取所有图片文件
        image_files = []
        if os.path.exists(background_dir):
            for file in os.listdir(background_dir):
                if os.path.splitext(file)[1].lower() in image_extensions:
                    image_files.append(file)
        
        # 保存当前选择
        main_current = self.main_background_combo.currentText() if self.main_background_combo.currentIndex() >= 0 else ""
        settings_current = self.settings_background_combo.currentText() if self.settings_background_combo.currentIndex() >= 0 else ""
        flash_current = self.flash_background_combo.currentText() if self.flash_background_combo.currentIndex() >= 0 else ""
        
        # 清空下拉框
        self.main_background_combo.clear()
        self.settings_background_combo.clear()
        self.flash_background_combo.clear()
        
        # 添加"无背景图"选项
        self.main_background_combo.addItem("无背景图")
        self.settings_background_combo.addItem("无背景图")
        self.flash_background_combo.addItem("无背景图")
        
        # 添加图片文件到下拉框
        for image_file in sorted(image_files):
            self.main_background_combo.addItem(image_file)
            self.settings_background_combo.addItem(image_file)
            self.flash_background_combo.addItem(image_file)
        
        # 恢复之前的选择
        if main_current and main_current in [self.main_background_combo.itemText(i) for i in range(self.main_background_combo.count())]:
            self.main_background_combo.setCurrentText(main_current)
        elif main_current == "无背景图":
            self.main_background_combo.setCurrentText("无背景图")
            
        if settings_current and settings_current in [self.settings_background_combo.itemText(i) for i in range(self.settings_background_combo.count())]:
            self.settings_background_combo.setCurrentText(settings_current)
        elif settings_current == "无背景图":
            self.settings_background_combo.setCurrentText("无背景图")
            
        if flash_current and flash_current in [self.flash_background_combo.itemText(i) for i in range(self.flash_background_combo.count())]:
            self.flash_background_combo.setCurrentText(flash_current)
        elif flash_current == "无背景图":
            self.flash_background_combo.setCurrentText("无背景图")