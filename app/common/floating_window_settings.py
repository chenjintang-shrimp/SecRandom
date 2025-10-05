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

class floating_window_settingsCard(GroupHeaderCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("浮窗管理")
        self.setBorderRadius(8)
        self.settings_file = path_manager.get_settings_path('custom_settings.json')
        self.default_settings = {
            "pumping_floating_enabled": True,
            "pumping_floating_transparency_mode": 80,
            "pumping_floating_visible": 3,
            "button_arrangement_mode": 0,
            "floating_icon_mode": 0,
            "flash_window_side_switch": False,
            "custom_retract_time": 5,
            "custom_display_mode": 1,
            "floating_window_visibility": 0
        }
        
        # 浮窗显示/隐藏按钮
        self.pumping_floating_switch = SwitchButton()
        self.pumping_floating_switch.setOnText("显示")
        self.pumping_floating_switch.setOffText("隐藏")
        self.pumping_floating_switch.checkedChanged.connect(self.save_settings)
        self.pumping_floating_switch.setFont(QFont(load_custom_font(), 12))

        # 浮窗透明度设置下拉框
        self.pumping_floating_transparency_SpinBox = SpinBox()
        self.pumping_floating_transparency_SpinBox.setRange(0, 100)
        self.pumping_floating_transparency_SpinBox.setValue(30)
        self.pumping_floating_transparency_SpinBox.setSingleStep(10)
        self.pumping_floating_transparency_SpinBox.setSuffix("%")
        self.pumping_floating_transparency_SpinBox.valueChanged.connect(self.save_settings)
        self.pumping_floating_transparency_SpinBox.setFont(QFont(load_custom_font(), 12))

        # 浮窗功能显示
        self.left_pumping_floating_switch = ComboBox()
        self.left_pumping_floating_switch.addItems([
            # 单个功能
            "显示 拖动",
            "显示 主界面",
            "显示 闪抽",
            
            # 两个功能组合
            "显示 拖动+主界面",
            "显示 拖动+闪抽",
            "显示 主界面+闪抽",
            
            # 三个功能组合
            "显示 拖动+主界面+闪抽",

            # 即抽
            "显示 即抽"
        ])
        self.left_pumping_floating_switch.setFont(QFont(load_custom_font(), 12))
        self.left_pumping_floating_switch.currentIndexChanged.connect(self.save_settings)

        # 浮窗按钮排列方式
        self.button_arrangement_comboBox = ComboBox()
        self.button_arrangement_comboBox.addItems([
            "矩形排列",
            "竖向排列",
            "横向排列"
        ])
        self.button_arrangement_comboBox.setFont(QFont(load_custom_font(), 12))
        self.button_arrangement_comboBox.currentIndexChanged.connect(self.save_settings)

        # 浮窗图标显示模式设置下拉框
        self.floating_icon_mode_comboBox = ComboBox()
        self.floating_icon_mode_comboBox.addItems(["图标+文字", "图标", "文字"])
        self.floating_icon_mode_comboBox.setCurrentIndex(0)  # 默认选择"图标+文字"
        self.floating_icon_mode_comboBox.currentIndexChanged.connect(self.save_settings)
        self.floating_icon_mode_comboBox.setFont(QFont(load_custom_font(), 12))

        # 浮窗贴边
        self.flash_window_side_switch = SwitchButton()
        self.flash_window_side_switch.setOnText("开启")
        self.flash_window_side_switch.setOffText("关闭")
        self.flash_window_side_switch.setFont(QFont(load_custom_font(), 12))
        self.flash_window_side_switch.checkedChanged.connect(self.save_settings)

        # 自定义收回秒数设置
        self.custom_retract_time_spinBox = SpinBox()
        self.custom_retract_time_spinBox.setRange(1, 60)  # 1-60秒
        self.custom_retract_time_spinBox.setValue(5)  # 默认5秒
        self.custom_retract_time_spinBox.setSingleStep(1)
        self.custom_retract_time_spinBox.setSuffix("秒")
        self.custom_retract_time_spinBox.valueChanged.connect(self.save_settings)
        self.custom_retract_time_spinBox.setFont(QFont(load_custom_font(), 12))

        # 自定义显示方式设置
        self.custom_display_mode_comboBox = ComboBox()
        self.custom_display_mode_comboBox.addItems(["箭头", "文字", "图标"])
        self.custom_display_mode_comboBox.currentIndexChanged.connect(self.save_settings)
        self.custom_display_mode_comboBox.setFont(QFont(load_custom_font(), 12))

        # 浮窗显隐条件
        self.floating_window_visibility_comboBox = ComboBox()
        self.floating_window_visibility_comboBox.addItems([
            "不检测",
            "类名-前台应用存在->显示",
            "类名-前台应用存在->隐藏",
            "标题-前台应用存在->显示",
            "标题-前台应用存在->隐藏",
            "进程-前台应用存在->显示",
            "进程-前台应用存在->隐藏",
            "类名+标题-前台应用存在->显示",
            "类名+标题-前台应用存在->隐藏",
            "类名+进程-前台应用存在->显示",
            "类名+进程-前台应用存在->隐藏",
            "标题+进程-前台应用存在->显示",
            "标题+进程-前台应用存在->隐藏",
            "类名+标题+进程-前台应用存在->显示",
            "类名+标题+进程-前台应用存在->隐藏"
        ])
        self.floating_window_visibility_comboBox.setFont(QFont(load_custom_font(), 12))
        self.floating_window_visibility_comboBox.currentIndexChanged.connect(self.save_settings)

        # 检测前台软件列表
        self.foreground_software_class_button = PushButton("设置前台窗口类名")
        self.foreground_software_class_button.clicked.connect(lambda: self.show_foreground_software_dialog("class"))
        self.foreground_software_class_button.setFont(QFont(load_custom_font(), 12))

        # 检测前台软件列表
        self.foreground_software_title_button = PushButton("设置前台窗口标题")
        self.foreground_software_title_button.clicked.connect(lambda: self.show_foreground_software_dialog("title"))
        self.foreground_software_title_button.setFont(QFont(load_custom_font(), 12))

        # 检测前台软件列表
        self.foreground_software_process_button = PushButton("设置前台窗口进程")
        self.foreground_software_process_button.clicked.connect(lambda: self.show_foreground_software_dialog("process"))
        self.foreground_software_process_button.setFont(QFont(load_custom_font(), 12))

        # 添加设置组
        self.addGroup(get_theme_icon("ic_fluent_window_ad_20_filled"), "浮窗显隐", "控制便捷点名悬浮窗的显示和隐藏状态", self.pumping_floating_switch)
        self.addGroup(get_theme_icon("ic_fluent_window_inprivate_20_filled"), "浮窗透明度", "调整悬浮窗的透明度以适应不同使用场景", self.pumping_floating_transparency_SpinBox)
        self.addGroup(get_theme_icon("ic_fluent_window_inprivate_20_filled"), "浮窗按钮数量", "自定义悬浮窗中显示的功能按钮数量", self.left_pumping_floating_switch)
        self.addGroup(get_theme_icon("ic_fluent_window_inprivate_20_filled"), "按钮排列方式", "选择悬浮窗按钮的水平或垂直排列布局", self.button_arrangement_comboBox)
        self.addGroup(get_theme_icon("ic_fluent_window_inprivate_20_filled"), "浮窗图标显示模式", "选择悬浮窗按钮的显示样式", self.floating_icon_mode_comboBox)
        self.addGroup(get_theme_icon("ic_fluent_window_inprivate_20_filled"), "浮窗贴边", "控制便捷点名悬浮窗是否贴边", self.flash_window_side_switch)
        self.addGroup(get_theme_icon("ic_fluent_timer_20_filled"), "浮窗贴边收回秒数", "设置浮窗贴边自定义收回的秒数(1-60秒)", self.custom_retract_time_spinBox)
        self.addGroup(get_theme_icon("ic_fluent_window_inprivate_20_filled"), "浮窗贴边显示方式", "选择浮窗贴边的显示方式(箭头/文字)", self.custom_display_mode_comboBox)
        self.addGroup(get_theme_icon("ic_fluent_timer_20_filled"), "前台软件检测", "启用基于前台软件的悬浮窗智能显示控制", self.floating_window_visibility_comboBox)
        self.addGroup(get_theme_icon("ic_fluent_timer_20_filled"), "软件类名检测", "设置用于检测的前台软件窗口类名", self.foreground_software_class_button)
        self.addGroup(get_theme_icon("ic_fluent_timer_20_filled"), "软件标题检测", "设置用于检测的前台软件窗口标题", self.foreground_software_title_button)
        self.addGroup(get_theme_icon("ic_fluent_timer_20_filled"), "软件进程检测", "设置用于检测的前台软件进程名称", self.foreground_software_process_button)
        
        # 前台软件检测定时器
        self.foreground_check_timer = QTimer(self)
        self.foreground_check_timer.timeout.connect(self.update_floating_window_visibility)
        self.foreground_check_timer.start(1000)

        # 加载设置
        self.load_settings()
        
    def load_settings(self):
        """加载设置"""
        try:
            # 使用get_setting_value函数获取设置值
            self.pumping_floating_switch.setChecked(get_setting_value("floating_window", "pumping_floating_enabled", self.default_settings.get("pumping_floating_enabled", True)))
            self.pumping_floating_transparency_SpinBox.setValue(get_setting_value("floating_window", "pumping_floating_transparency_mode", self.default_settings.get("pumping_floating_transparency_mode", 80)))
            self.left_pumping_floating_switch.setCurrentIndex(get_setting_value("floating_window", "pumping_floating_visible", self.default_settings.get("pumping_floating_visible", 3)))
            self.button_arrangement_comboBox.setCurrentIndex(get_setting_value("floating_window", "button_arrangement_mode", self.default_settings.get("button_arrangement_mode", 0)))
            self.floating_icon_mode_comboBox.setCurrentIndex(get_setting_value("floating_window", "floating_icon_mode", self.default_settings.get("floating_icon_mode", 0)))
            self.flash_window_side_switch.setChecked(get_setting_value("floating_window", "flash_window_side_switch", self.default_settings.get("flash_window_side_switch", False)))
            self.custom_retract_time_spinBox.setValue(get_setting_value("floating_window", "custom_retract_time", self.default_settings.get("custom_retract_time", 5)))
            self.custom_display_mode_comboBox.setCurrentIndex(get_setting_value("floating_window", "custom_display_mode", self.default_settings.get("custom_display_mode", 1)))
            self.floating_window_visibility_comboBox.setCurrentIndex(get_setting_value("floating_window", "floating_window_visibility", self.default_settings.get("floating_window_visibility", 0)))
            
        except Exception as e:
            logger.error(f"加载浮窗设置时出错: {str(e)}")
            self.pumping_floating_switch.setChecked(self.default_settings.get("pumping_floating_enabled", True))
            self.pumping_floating_transparency_SpinBox.setValue(self.default_settings.get("pumping_floating_transparency_mode", 80))
            self.left_pumping_floating_switch.setCurrentIndex(self.default_settings.get("pumping_floating_visible", 3))
            self.button_arrangement_comboBox.setCurrentIndex(self.default_settings.get("button_arrangement_mode", 0))
            self.floating_icon_mode_comboBox.setCurrentIndex(self.default_settings.get("floating_icon_mode", 0))
            self.flash_window_side_switch.setChecked(self.default_settings.get("flash_window_side_switch", False))
            self.custom_retract_time_spinBox.setValue(self.default_settings.get("custom_retract_time", 5))
            self.custom_display_mode_comboBox.setCurrentIndex(self.default_settings.get("custom_display_mode", 1))
            self.floating_window_visibility_comboBox.setCurrentIndex(self.default_settings.get("floating_window_visibility", 0))
    
    def save_settings(self):
        """保存设置"""
        try:
            # 准备要保存的设置
            floating_window_settings = {
                "pumping_floating_enabled": self.pumping_floating_switch.isChecked(),
                "pumping_floating_transparency_mode": self.pumping_floating_transparency_SpinBox.value(),
                "pumping_floating_visible": self.left_pumping_floating_switch.currentIndex(),
                "button_arrangement_mode": self.button_arrangement_comboBox.currentIndex(),
                "floating_icon_mode": self.floating_icon_mode_comboBox.currentIndex(),
                "flash_window_side_switch": self.flash_window_side_switch.isChecked(),
                "custom_retract_time": self.custom_retract_time_spinBox.value(),
                "custom_display_mode": self.custom_display_mode_comboBox.currentIndex(),
                "floating_window_visibility": self.floating_window_visibility_comboBox.currentIndex()
            }
            
            # 使用update_settings函数保存设置
            update_settings("floating_window", floating_window_settings)
                
        except Exception as e:
            logger.error(f"保存浮窗设置时出错: {str(e)}")


    class ForegroundSoftwareDialog(QDialog):
        def __init__(self, parent=None, current_software_mode=None):
            super().__init__(parent)
            self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
            if current_software_mode == 'class':
                self.setWindowTitle("输入前台窗口类名")
            elif current_software_mode == 'title':
                self.setWindowTitle("输入前台窗口标题")
            elif current_software_mode == 'process':
                self.setWindowTitle("输入前台窗口进程")
            self.setMinimumSize(400, 335)  # 设置最小大小而不是固定大小
            self.saved = False
            self.dragging = False
            self.drag_position = None
            self.load_software_settings
            
            # 确保不设置子窗口的屏幕属性
            if parent is not None:
                self.setParent(parent)
            
            # 创建自定义标题栏
            self.title_bar = QWidget()
            self.title_bar.setObjectName("CustomTitleBar")
            self.title_bar.setFixedHeight(35)
            
            # 标题栏布局
            title_layout = QHBoxLayout(self.title_bar)
            title_layout.setContentsMargins(10, 0, 10, 0)
            
            # 窗口标题
            if current_software_mode == 'class':
                self.title_label = QLabel("输入前台窗口类名")
            elif current_software_mode == 'title':
                self.title_label = QLabel("输入前台窗口标题")
            elif current_software_mode == 'process':
                self.title_label = QLabel("输入前台窗口进程")
            self.title_label.setObjectName("TitleLabel")
            self.title_label.setFont(QFont(load_custom_font(), 12))
            
            # 窗口控制按钮
            self.close_btn = QPushButton("✕")
            self.close_btn.setObjectName("CloseButton")
            self.close_btn.setFixedSize(25, 25)
            self.close_btn.clicked.connect(self.reject)
            
            # 添加组件到标题栏
            title_layout.addWidget(self.title_label)
            title_layout.addStretch()
            title_layout.addWidget(self.close_btn)
            
            if current_software_mode == 'class':
                self.text_label = BodyLabel("输入前台窗口类名,每行一个")
            elif current_software_mode == 'title':
                self.text_label = BodyLabel("输入前台窗口标题,每行一个")
            elif current_software_mode == 'process':
                self.text_label = BodyLabel("输入前台窗口进程,每行一个")
            self.text_label.setFont(QFont(load_custom_font(), 12))

            self.update_theme_style()
            qconfig.themeChanged.connect(self.update_theme_style)
            
            self.textEdit = PlainTextEdit()
            if current_software_mode == 'class':
                self.textEdit.setPlaceholderText("输入前台窗口类名,每行一个")
            elif current_software_mode == 'title':
                self.textEdit.setPlaceholderText("输入前台窗口标题,每行一个")
            elif current_software_mode == 'process':
                self.textEdit.setPlaceholderText("输入前台窗口进程,每行一个")
            self.textEdit.setFont(QFont(load_custom_font(), 12))
            
            self.setFont(QFont(load_custom_font(), 12))

            try:
                # 使用get_all_settings函数获取所有设置
                settings = get_settings_by_category("foreground_software")
                    
                # 获取所有清理时间并格式化为字符串
                if current_software_mode == 'class':
                    foreground_software = settings.get('foregroundsoftware_class', {})
                elif current_software_mode == 'title':
                    foreground_software = settings.get('foregroundsoftware_title', {})
                elif current_software_mode == 'process':
                    foreground_software = settings.get('foregroundsoftware_process', {})
                if foreground_software:
                    software_list = [str(software) for software_id, software in foreground_software.items()]
                    self.textEdit.setPlainText('\n'.join(software_list))
                else:
                    pass
            except Exception as e:
                logger.error(f"加载定时清理记录时间失败: {str(e)}")

            self.saveButton = PrimaryPushButton("保存")
            self.cancelButton = PushButton("取消")
            self.saveButton.clicked.connect(self.accept)
            self.cancelButton.clicked.connect(self.reject)
            self.saveButton.setFont(QFont(load_custom_font(), 12))
            self.cancelButton.setFont(QFont(load_custom_font(), 12))
            
            layout = QVBoxLayout()
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(0)
            # 添加自定义标题栏
            layout.addWidget(self.title_bar)
            # 添加内容区域
            content_layout = QVBoxLayout()
            content_layout.setSpacing(10)
            content_layout.addWidget(self.text_label)
            content_layout.addWidget(self.textEdit)
            
            buttonLayout = QHBoxLayout()
            buttonLayout.addStretch(1)
            buttonLayout.addWidget(self.cancelButton)
            buttonLayout.addWidget(self.saveButton)
            
            content_layout.addLayout(buttonLayout)
            content_layout.setContentsMargins(20, 10, 20, 20)
            layout.addLayout(content_layout)
            self.setLayout(layout)

        def mousePressEvent(self, event):
            # 窗口拖动功能 按住标题栏就能移动
            if event.button() == Qt.LeftButton and self.title_bar.underMouse():
                self.dragging = True
                self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
                event.accept()

        def mouseMoveEvent(self, event):
            if self.dragging and event.buttons() == Qt.LeftButton:
                self.move(event.globalPos() - self.drag_position)
                event.accept()

        def mouseReleaseEvent(self, event):
            self.dragging = False

        def update_theme_style(self):
            colors = {'text': '#F5F5F5', 'bg': '#111116', 'title_bg': '#2D2D2D'} if is_dark_theme else {'text': '#111116', 'bg': '#F5F5F5', 'title_bg': '#E0E0E0'}
            self.setStyleSheet(f"""
                QDialog {{ background-color: {colors['bg']}; border-radius: 5px; }}
                #CustomTitleBar {{ background-color: {colors['title_bg']}; }}
                #TitleLabel {{ color: {colors['text']}; font-weight: bold; padding: 5px; }}
                #CloseButton {{ 
                    background-color: transparent; 
                    color: {colors['text']}; 
                    border-radius: 4px; 
                    font-weight: bold; 
                }}
                #CloseButton:hover {{ background-color: #ff4d4d; color: white; }}
                QLabel, QPushButton, QTextEdit {{ color: {colors['text']}; }}
            """)
            
            # 设置标题栏颜色以匹配背景色（仅Windows系统）
            if os.name == 'nt':
                try:
                    import ctypes
                    hwnd = int(self.winId())  # 转换为整数句柄
                    
                    # 颜色格式要改成ARGB 添加透明度通道
                    bg_color = colors['bg'].lstrip('#')
                    # 转换为ARGB格式（添加不透明通道）
                    rgb_color = int(f'FF{bg_color}', 16) if len(bg_color) == 6 else int(bg_color, 16)
                    
                    # 设置窗口标题栏颜色
                    ctypes.windll.dwmapi.DwmSetWindowAttribute(
                        ctypes.c_int(hwnd),  # 窗口句柄（整数类型）
                        35,  # DWMWA_CAPTION_COLOR
                        ctypes.byref(ctypes.c_uint(rgb_color)),  # 颜色值指针
                        ctypes.sizeof(ctypes.c_uint)  # 数据大小
                    )
                except Exception as e:
                    logger.error(f"设置标题栏颜色失败: {str(e)}")

        def load_software_settings(self):
            """加载已保存的软件设置"""
            try:
                # 使用get_settings_by_category函数获取设置值
                settings = get_settings_by_category("foreground_software")
                
                # 根据当前模式加载对应的设置
                if self.current_software_mode == 'class' and 'foregroundsoftware_class' in settings:
                    software_list = list(settings['foregroundsoftware_class'].values())
                elif self.current_software_mode == 'title' and 'foregroundsoftware_title' in settings:
                    software_list = list(settings['foregroundsoftware_title'].values())
                elif self.current_software_mode == 'process' and 'foregroundsoftware_process' in settings:
                    software_list = list(settings['foregroundsoftware_process'].values())
                else:
                    software_list = []
                    
                self.textEdit.setPlainText('\n'.join(software_list))
            except Exception as e:
                logger.error(f"加载前台软件设置时出错: {str(e)}")

    def get_foreground_window_info(self):
        """获取前台窗口信息"""
        try:
            import win32gui
            import win32process
            import psutil
            
            # 获取前台窗口句柄
            hwnd = win32gui.GetForegroundWindow()
            
            # 获取窗口标题
            title = win32gui.GetWindowText(hwnd)
            
            # 获取窗口类名
            class_name = win32gui.GetClassName(hwnd)
            
            # 获取进程ID
            _, process_id = win32process.GetWindowThreadProcessId(hwnd)
            
            # 获取进程名称
            process_name = psutil.Process(process_id).name()
            
            return {
                'class_name': class_name,
                'title': title,
                'process_name': process_name
            }
        except Exception as e:
            logger.error(f"获取前台窗口信息时出错: {str(e)}")
            return None

    def check_foreground_software(self):
        """检查前台软件是否匹配设置"""
        try:
            # 使用get_settings_by_category函数获取前台软件设置
            settings = get_settings_by_category("foreground_software")
                
            # 获取前台窗口信息
            foreground_info = self.get_foreground_window_info()
            if not foreground_info:
                return False
            
            # 获取当前选择的检测模式
            current_mode = self.floating_window_visibility_comboBox.currentIndex()

            if current_mode == 0:
                return False

            # 确定检测类型和操作
            detection_type = (current_mode - 1) // 2
            is_show_mode = (current_mode % 2) == 1

            # 获取设置值
            class_names = settings.get('foregroundsoftware_class', {}).values()
            titles = settings.get('foregroundsoftware_title', {}).values()
            processes = settings.get('foregroundsoftware_process', {}).values()

            # 检测逻辑
            if detection_type == 0:  # 类名检测
                is_matched = any(software and software in foreground_info['class_name'] for software in class_names)
            elif detection_type == 1:  # 标题检测
                is_matched = any(software and software in foreground_info['title'] for software in titles)
            elif detection_type == 2:  # 进程检测
                is_matched = any(software and software in foreground_info['process_name'] for software in processes)
            elif detection_type == 3:  # 类名+标题检测
                is_matched = (any(software and software in foreground_info['class_name'] for software in class_names) and
                             any(software and software in foreground_info['title'] for software in titles))
            elif detection_type == 4:  # 类名+进程检测
                is_matched = (any(software and software in foreground_info['class_name'] for software in class_names) and
                             any(software and software in foreground_info['process_name'] for software in processes))
            elif detection_type == 5:  # 标题+进程检测
                is_matched = (any(software and software in foreground_info['title'] for software in titles) and
                             any(software and software in foreground_info['process_name'] for software in processes))
            elif detection_type == 6:  # 类名+标题+进程检测
                is_matched = (any(software and software in foreground_info['class_name'] for software in class_names) and
                             any(software and software in foreground_info['title'] for software in titles) and
                             any(software and software in foreground_info['process_name'] for software in processes))
            else:
                is_matched = False

            # 根据模式决定返回值
            return is_matched if is_show_mode else not is_matched
        except Exception as e:
            logger.error(f"检查前台软件时出错: {str(e)}")
            return False

    def update_floating_window_visibility(self):
        """根据前台软件检测结果更新浮窗可见性"""
        try:
            
            # 获取浮窗可见性设置
            visibility_mode = self.floating_window_visibility_comboBox.currentIndex()
            
            # 如果设置为不检测，则不做任何操作
            if visibility_mode == 0:
                return
            
            # 检查前台软件是否匹配
            is_matched = self.check_foreground_software()
            
            # 获取浮窗实例
            floating_window = None
            for widget in QApplication.topLevelWidgets():
                if hasattr(widget, '__class__') and widget.__class__.__name__ == 'Window':
                    if hasattr(widget, 'levitation_window') and widget.levitation_window is not None:
                        floating_window = widget.levitation_window
                        break

            if not floating_window:
                logger.error("未找到浮窗实例")
                return
            
            # 根据检测结果更新浮窗可见性
            floating_window.setVisible(is_matched)
        except Exception as e:
            logger.error(f"更新浮窗可见性时出错: {str(e)}")

    def show_foreground_software_dialog(self, current_software_mode=None):
        dialog = self.ForegroundSoftwareDialog(self, current_software_mode)
        if dialog.exec():
            foreground_software = dialog.textEdit.toPlainText()
            try:
                # 获取前台软件设置
                settings = get_settings_by_category("foreground_software")
                
                # 清空现有设置
                if current_software_mode == 'class':
                    settings['foregroundsoftware_class'] = {}
                elif current_software_mode == 'title':
                    settings['foregroundsoftware_title'] = {}
                elif current_software_mode == 'process':
                    settings['foregroundsoftware_process'] = {}
                
                # 重新编号并保存
                for idx, software_str in enumerate(foreground_software.splitlines(), 1):
                    software_str = software_str.strip()
                    if software_str:
                        if current_software_mode == 'class':
                            settings.setdefault('foregroundsoftware_class', {})[str(idx)] = software_str
                        elif current_software_mode == 'title':
                            settings.setdefault('foregroundsoftware_title', {})[str(idx)] = software_str
                        elif current_software_mode == 'process':
                            settings.setdefault('foregroundsoftware_process', {})[str(idx)] = software_str
                
                # 使用update_settings函数保存设置
                update_settings("foreground_software", settings)
                logger.info(f"成功保存{len([s for s in foreground_software.splitlines() if s.strip()])}个前台软件设置")
                InfoBar.success(
                    title='设置成功',
                    content=f"成功保存{len([s for s in foreground_software.splitlines() if s.strip()])}个前台软件设置!",
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=3000,
                    parent=self
                )
            except Exception as e:
                logger.error(f"保存前台软件设置失败: {str(e)}")
                InfoBar.error(
                    title='设置失败',
                    content=f"保存前台软件设置失败: {str(e)}",
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=3000,
                    parent=self
                )