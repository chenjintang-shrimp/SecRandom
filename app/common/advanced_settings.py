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

# 平台特定导入
if platform.system() == "Windows":
    import winreg
else:
    # Linux平台使用subprocess处理注册表相关操作
    import subprocess
    import shutil
    import stat

from app.common.config import get_theme_icon, load_custom_font, is_dark_theme, VERSION
from app.common.path_utils import path_manager
from app.common.path_utils import open_file, ensure_dir


class advanced_settingsCard(GroupHeaderCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("高级设置")
        self.setBorderRadius(8)
        self.settings_file = path_manager.get_settings_path()
        self.default_settings = {
            "floating_window_visibility": 0
        }
        
        # 浮窗显隐条件
        self.floating_window_visibility_comboBox = ComboBox()
        self.floating_window_visibility_comboBox.setFixedWidth(200)
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

        # 导出诊断数据按钮
        self.export_diagnostic_button = PushButton("导出诊断数据")
        self.export_diagnostic_button.clicked.connect(self.export_diagnostic_data)
        self.export_diagnostic_button.setFont(QFont(load_custom_font(), 12))

        # 导入设置按钮
        self.import_settings_button = PushButton("导入设置")
        self.import_settings_button.clicked.connect(self.import_settings)
        self.import_settings_button.setFont(QFont(load_custom_font(), 12))

        # 导出设置按钮
        self.export_settings_button = PushButton("导出设置")
        self.export_settings_button.clicked.connect(self.export_settings)
        self.export_settings_button.setFont(QFont(load_custom_font(), 12))
        
        # 添加组件到分组中

        # 智能检测设置
        self.addGroup(get_theme_icon("ic_fluent_timer_20_filled"), "前台软件检测", "启用基于前台软件的悬浮窗智能显示控制", self.floating_window_visibility_comboBox)
        self.addGroup(get_theme_icon("ic_fluent_timer_20_filled"), "软件类名检测", "设置用于检测的前台软件窗口类名", self.foreground_software_class_button)
        self.addGroup(get_theme_icon("ic_fluent_timer_20_filled"), "软件标题检测", "设置用于检测的前台软件窗口标题", self.foreground_software_title_button)
        self.addGroup(get_theme_icon("ic_fluent_timer_20_filled"), "软件进程检测", "设置用于检测的前台软件进程名称", self.foreground_software_process_button)

        # 数据管理设置
        self.addGroup(get_theme_icon("ic_fluent_group_20_filled"), "导出诊断数据", "生成并导出系统诊断信息用于技术支持", self.export_diagnostic_button)
        self.addGroup(get_theme_icon("ic_fluent_multiselect_ltr_20_filled"), "导入设置", "从配置文件恢复软件的各项设置参数", self.import_settings_button)
        self.addGroup(get_theme_icon("ic_fluent_multiselect_ltr_20_filled"), "导出设置", "将当前软件设置保存到配置文件中", self.export_settings_button)
        
        # 前台软件检测定时器
        self.foreground_check_timer = QTimer(self)
        self.foreground_check_timer.timeout.connect(self.update_floating_window_visibility)
        self.foreground_check_timer.start(1000)

        self.load_settings()
        self.save_settings()
        
    def load_settings(self):
        try:
            if path_manager.file_exists(self.settings_file):
                with open_file(self.settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    advanced_settings = settings.get("advanced", {})
                    
                    floating_window_visibility = advanced_settings.get("floating_window_visibility", self.default_settings["floating_window_visibility"])
                    if floating_window_visibility < 0 or floating_window_visibility >= self.floating_window_visibility_comboBox.count():
                        # 如果索引值无效，则使用默认值
                        floating_window_visibility = self.default_settings["floating_window_visibility"]
                    
                    self.floating_window_visibility_comboBox.setCurrentIndex(floating_window_visibility)
            else:
                logger.warning(f"设置文件不存在: {self.settings_file}")
                self.floating_window_visibility_comboBox.setCurrentIndex(self.default_settings["floating_window_visibility"])
                self.save_settings()
        except Exception as e:
            logger.error(f"加载设置时出错: {e}")
            self.floating_window_visibility_comboBox.setCurrentIndex(self.default_settings["floating_window_visibility"])
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
        
        # 更新foundation部分的所有设置
        if "advanced" not in existing_settings:
            existing_settings["advanced"] = {}
            
        advanced_settings = existing_settings["advanced"]
        # 删除保存文字选项的代码
        advanced_settings["floating_window_visibility"] = self.floating_window_visibility_comboBox.currentIndex()
        
        os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
        with open_file(self.settings_file, 'w', encoding='utf-8') as f:
            json.dump(existing_settings, f, indent=4)





    class ForegroundSoftwareDialog(QDialog):
        def __init__(self, parent=None, current_software_mode=None):
            super().__init__(parent)
            # 🌟 星穹铁道白露：设置无边框但可调整大小的窗口样式并解决屏幕设置冲突~ 
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
            
            # 🐦 小鸟游星野：创建自定义标题栏啦~ (≧∇≦)ﾉ
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
                foreground_software_file = path_manager.get_settings_path('ForegroundSoftware.json')
                if path_manager.file_exists(foreground_software_file):
                    with open_file(foreground_software_file, 'r', encoding='utf-8') as f:
                        settings = json.load(f)
                        
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
            # 🐦 小鸟游星野：窗口拖动功能~ 按住标题栏就能移动啦 (๑•̀ㅂ•́)و✧
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
            # 🌟 星穹铁道白露：主题样式更新 ~ 现在包含自定义标题栏啦！
            colors = {'text': '#F5F5F5', 'bg': '#111116', 'title_bg': '#2D2D2D'} if is_dark else {'text': '#111116', 'bg': '#F5F5F5', 'title_bg': '#E0E0E0'}
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
                    # 🌟 星穹铁道白露：修复参数类型错误~ 现在要把窗口ID转成整数才行哦！
                    hwnd = int(self.winId())  # 转换为整数句柄
                    
                    # 🐦 小鸟游星野：颜色格式要改成ARGB才行呢~ 添加透明度通道(๑•̀ㅂ•́)و✧
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
                    logger.warning(f"设置标题栏颜色失败: {str(e)}")

        def load_software_settings(self):
            """加载已保存的软件设置"""
            try:
                from app.common.path_utils import path_manager
                foreground_software_file = path_manager.get_settings_path('ForegroundSoftware.json')
                
                if path_manager.file_exists(foreground_software_file):
                    with open_file(foreground_software_file, 'r', encoding='utf-8') as f:
                        settings = json.load(f)
                        
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
            from app.common.path_utils import path_manager
            foreground_software_file = path_manager.get_settings_path('ForegroundSoftware.json')
            
            if not path_manager.file_exists(foreground_software_file):
                return False
            
            with open_file(foreground_software_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                
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
                logger.warning("未找到浮窗实例")
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
                # 确保Settings目录存在
                from app.common.path_utils import path_manager
                foreground_software_file = path_manager.get_settings_path('ForegroundSoftware.json')
                os.makedirs(os.path.dirname(foreground_software_file), exist_ok=True)
                
                settings = {}
                if path_manager.file_exists(foreground_software_file):
                    with open_file(foreground_software_file, 'r', encoding='utf-8') as f:
                        settings = json.load(f)
                
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
                
                with open_file(foreground_software_file, 'w', encoding='utf-8') as f:
                    json.dump(settings, f, ensure_ascii=False, indent=4)
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




    def export_diagnostic_data(self):
        """导出诊断数据到压缩文件"""
        # 首先显示安全确认对话框，告知用户将要导出敏感数据
        try:
            # 创建安全确认对话框
            confirm_box = Dialog(
                title='⚠️ 敏感数据导出确认',
                content=(
                    '您即将导出诊断数据，这些数据可能包含敏感信息：\n\n'
                    '📋 包含的数据类型：\n'
                    '• 抽人名单数据、抽奖设置文件、历史记录文件\n'
                    '• 软件设置文件、插件配置文件、系统日志文件\n\n'
                    '⚠️ 注意事项：\n'
                    '• 这些数据可能包含个人信息和使用记录\n'
                    '• 请妥善保管导出的压缩包文件\n'
                    '• 不要将导出文件分享给不可信的第三方\n'
                    '• 如不再需要，请及时删除导出的文件\n\n'
                    '确认要继续导出诊断数据吗？'
                ),
                parent=self
            )
            confirm_box.yesButton.setText('确认导出')
            confirm_box.cancelButton.setText('取消')
            confirm_box.setFont(QFont(load_custom_font(), 12))
            
            # 如果用户取消导出，则直接返回
            if not confirm_box.exec():
                logger.info("用户取消了诊断数据导出")
                InfoBar.info(
                    title='导出已取消',
                    content='诊断数据导出操作已取消',
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=3000,
                    parent=self
                )
                return
                
        except Exception as e:
            logger.error(f"创建安全确认对话框失败: {str(e)}")
            pass

        try:
            from app.common.path_utils import path_manager
            enc_set_file = path_manager.get_enc_set_path()
            with open_file(enc_set_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                logger.debug("正在读取安全设置，准备执行导出诊断数据验证～ ")

                if settings.get('hashed_set', {}).get('start_password_enabled', False) == True:
                    from app.common.password_dialog import PasswordDialog
                    dialog = PasswordDialog(self)
                    if dialog.exec_() != QDialog.Accepted:
                        logger.warning("用户取消导出诊断数据操作，安全防御已解除～ ")
                        return
        except Exception as e:
            logger.error(f"密码验证系统出错喵～ {e}")
            return
            
        try:
            import zipfile
            from datetime import datetime
            
            # 获取桌面路径
            desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
            if not path_manager.file_exists(desktop_path):
                desktop_path = os.path.join(os.path.expanduser("~"), "桌面")
            
            # 创建诊断文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            zip_filename = f"SecRandom_诊断数据_{timestamp}.zip"
            zip_path = os.path.join(desktop_path, zip_filename)
            
            # 需要导出的文件夹列表
            export_folders = [
                path_manager.get_resource_path('list'), 
                path_manager.get_resource_path('reward'),
                path_manager.get_resource_path('history'),
                path_manager._app_root / "app" / "settings",
                path_manager.get_plugin_path(),
                path_manager._app_root / "logs"
            ]

            app_dir = path_manager._app_root
            
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                exported_count = 0
                
                for folder_path in export_folders:
                    if folder_path.exists():
                        for root, dirs, files in os.walk(folder_path):
                            for file in files:
                                file_path = Path(root) / file
                                arcname = str(file_path.relative_to(app_dir))
                                zipf.write(file_path, arcname)
                                exported_count += 1
                    else:
                        # 如果文件夹不存在，自动创建目录以确保导出完整
                        try:
                            folder_path.mkdir(parents=True, exist_ok=True)
                            logger.info(f"自动创建不存在的文件夹: {folder_path}")
                            
                            # 创建一个说明文件，记录该文件夹是自动创建的
                            readme_path = folder_path / "_auto_created_readme.txt"
                            with open(readme_path, 'w', encoding='utf-8') as f:
                                f.write(f"此文件夹是在诊断数据导出时自动创建的\n")
                                f.write(f"创建时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                                f.write(f"原因: 原文件夹不存在，为确保导出完整性而自动创建\n")
                            
                            # 将创建的说明文件添加到压缩包
                            arcname = str(readme_path.relative_to(app_dir))
                            zipf.write(readme_path, arcname)
                            exported_count += 1
                            
                        except Exception as create_error:
                            # 如果创建失败，记录错误但继续导出其他文件夹
                            logger.error(f"创建文件夹失败 {folder_path}: {str(create_error)}")
                            relative_path = str(folder_path.relative_to(app_dir))
                            error_info = {
                                "folder": relative_path,
                                "status": "creation_failed",
                                "error": str(create_error),
                                "note": "自动创建文件夹失败"
                            }
                            zipf.writestr(f"_error_{relative_path.replace('/', '_')}.json", 
                                        json.dumps(error_info, ensure_ascii=False, indent=2))
                
                # 创建结构化的系统信息报告 - 使用JSON格式便于程序解析
                system_info = {
                    # 【导出元数据】基础信息记录
                    "export_metadata": {
                        "software": "SecRandom",                                                # 软件名称
                        "export_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),            # 人类可读时间
                        "export_timestamp": datetime.now().isoformat(),                         # ISO标准时间戳
                        "version": VERSION,                                                     # 当前软件版本
                        "export_type": "diagnostic",                                            # 导出类型（诊断数据）
                    },
                    # 【系统环境信息】详细的运行环境数据
                    "system_info": {
                        "software_path": str(app_dir),                                           # 软件安装路径
                        "operating_system": self._get_operating_system(),                       # 操作系统版本（正确识别Win11）
                        "platform_details": {                                                   # 平台详细信息
                            "system": platform.system(),                                        # 系统类型 (Windows/Linux/Darwin)
                            "release": self._get_platform_release(),                          # 系统发行版本（正确识别Win11）
                            "version": self._get_platform_version(),                          # 完整系统版本（正确识别Win11）
                            "machine": platform.machine(),                                      # 机器架构 (AMD64/x86_64)
                            "processor": platform.processor()                                   # 处理器信息
                        },
                        "python_version": sys.version,                                          # Python完整版本信息
                        "python_executable": sys.executable                                     # Python可执行文件路径
                    },
                    # 【导出摘要】统计信息和导出详情
                    "export_summary": {
                        "total_files_exported": exported_count,                                 # 成功导出的文件总数
                        "export_folders": [str(folder) for folder in export_folders],         # 导出的文件夹列表（转换为字符串）
                        "export_location": str(zip_path)                                         # 导出压缩包的完整路径
                    }
                }
                # 将系统信息写入JSON文件，使用中文编码确保兼容性
                diagnostic_filename = f"SecRandom_诊断报告_{VERSION}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                zipf.writestr(diagnostic_filename, json.dumps(system_info, ensure_ascii=False, indent=2))
            
            # 显示成功提示
            InfoBar.success(
                title='导出成功',
                content=f'诊断数据已导出到: {zip_path}',
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=5000,
                parent=self
            )
            
            logger.success(f"诊断数据导出成功: {zip_path}")
            
            # 打开导出文件所在的文件夹 - 提供用户友好的选择提示
            try:
                # 创建消息框询问用户是否打开导出目录
                msg_box = Dialog(
                    title='诊断数据导出完成',
                    content=f'诊断数据已成功导出到桌面！\n\n文件位置: {zip_path}\n\n是否立即打开导出文件夹查看文件？',
                    parent=self
                )
                msg_box.yesButton.setText('打开文件夹')
                msg_box.cancelButton.setText('稍后再说')
                msg_box.setFont(QFont(load_custom_font(), 12))
                
                if msg_box.exec():
                    # 用户选择打开文件夹
                    self.open_folder(os.path.dirname(zip_path))
                    logger.info("用户选择打开诊断数据导出文件夹")
                else:
                    # 用户选择不打开
                    logger.info("用户选择不打开诊断数据导出文件夹")
                    
            except Exception as e:
                # 如果消息框创建失败，回退到简单的提示
                logger.error(f"创建消息框失败: {str(e)}")
                try:
                    self.open_folder(os.path.dirname(zip_path))
                except:
                    logger.error("无法打开诊断数据导出文件夹")
                    self.open_folder(desktop_path)
            except:
                pass
                
        except Exception as e:
            logger.error(f"导出诊断数据时出错: {str(e)}")
            InfoBar.error(
                title='导出失败',
                content=f'导出诊断数据时出错: {str(e)}',
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=5000,
                parent=self
            )

    def _get_operating_system(self):
        """
        获取操作系统版本信息，正确识别Windows 11系统
        
        Returns:
            str: 操作系统版本字符串
        """
        try:
            system = platform.system()
            if system != "Windows":
                # 非Windows系统直接返回标准信息
                return f"{system} {platform.release()}"
            
            # Windows系统特殊处理，正确识别Windows 11
            try:
                import winreg
                # 查询注册表获取当前Windows版本号
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion")
                current_build = winreg.QueryValueEx(key, "CurrentBuild")[0]
                display_version = winreg.QueryValueEx(key, "DisplayVersion")[0]
                product_name = winreg.QueryValueEx(key, "ProductName")[0]
                winreg.CloseKey(key)
                
                # Windows 11的构建版本号从22000开始
                if int(current_build) >= 22000:
                    return f"Windows 11 (Build {current_build}, Version {display_version})"
                else:
                    # Windows 10或其他版本
                    return f"{product_name} (Build {current_build}, Version {display_version})"
                    
            except Exception as e:
                logger.warning(f"从注册表获取Windows版本信息失败: {str(e)}")
                # 回退到标准方法
                release = platform.release()
                version = platform.version()
                # 通过版本号简单判断（不精确但比直接显示Windows 10好）
                if release == "10" and version and version.split(".")[-1] >= "22000":
                    return f"Windows 11 {version}"
                return f"Windows {release} {version}"
                
        except Exception as e:
            logger.error(f"获取操作系统版本信息失败: {str(e)}")
            # 最终回退方案
            return f"{platform.system()} {platform.release()} {platform.version()}"

    def _get_platform_release(self):
        """
        获取系统发行版本，正确识别Windows 11
        
        Returns:
            str: 系统发行版本
        """
        try:
            system = platform.system()
            if system != "Windows":
                # 非Windows系统直接返回标准信息
                return platform.release()
            
            # Windows系统特殊处理，正确识别Windows 11
            try:
                import winreg
                # 查询注册表获取当前Windows版本号
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion")
                current_build = winreg.QueryValueEx(key, "CurrentBuild")[0]
                product_name = winreg.QueryValueEx(key, "ProductName")[0]
                winreg.CloseKey(key)
                
                # Windows 11的构建版本号从22000开始
                if int(current_build) >= 22000:
                    return "11"
                else:
                    # 从产品名称中提取版本号
                    if "Windows 10" in product_name:
                        return "10"
                    elif "Windows 8" in product_name:
                        return "8"
                    elif "Windows 7" in product_name:
                        return "7"
                    else:
                        # 回退到标准方法
                        return platform.release()
                        
            except Exception as e:
                logger.warning(f"从注册表获取Windows版本信息失败: {str(e)}")
                # 回退到标准方法
                release = platform.release()
                version = platform.version()
                # 通过版本号简单判断
                if release == "10" and version and version.split(".")[-1] >= "22000":
                    return "11"
                return release
                
        except Exception as e:
            logger.error(f"获取系统发行版本失败: {str(e)}")
            # 最终回退方案
            return platform.release()
    
    def _get_platform_version(self):
        """
        获取完整系统版本，正确识别Windows 11
        
        Returns:
            str: 完整系统版本
        """
        try:
            system = platform.system()
            if system != "Windows":
                # 非Windows系统直接返回标准信息
                return platform.version()
            
            # Windows系统特殊处理，正确识别Windows 11
            try:
                import winreg
                # 查询注册表获取当前Windows版本号
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion")
                current_build = winreg.QueryValueEx(key, "CurrentBuild")[0]
                display_version = winreg.QueryValueEx(key, "DisplayVersion")[0]
                ubr = winreg.QueryValueEx(key, "UBR")[0]  # Update Build Revision
                winreg.CloseKey(key)
                
                # 构建更准确的版本字符串
                if int(current_build) >= 22000:
                    # Windows 11
                    return f"{current_build}.{ubr} (Version {display_version})"
                else:
                    # Windows 10或其他版本
                    return f"{current_build}.{ubr} (Version {display_version})"
                    
            except Exception as e:
                logger.warning(f"从注册表获取Windows版本信息失败: {str(e)}")
                # 回退到标准方法但进行修正
                version = platform.version()
                release = platform.release()
                if release == "10" and version and version.split(".")[-1] >= "22000":
                    # 修正为Windows 11版本信息
                    return version
                return version
                
        except Exception as e:
            logger.error(f"获取完整系统版本失败: {str(e)}")
            # 最终回退方案
            return platform.version()

    def import_settings(self):
        """导入设置"""
        try:
            # 打开文件选择对话框
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "选择要导入的设置文件",
                "",
                "设置文件 (*.json);;所有文件 (*.*)"
            )
            
            if not file_path:
                return
            
            # 读取导入的设置文件
            with open_file(file_path, 'r', encoding='utf-8') as f:
                imported_settings = json.load(f)
            
            # 显示设置选择对话框
            dialog = SettingsSelectionDialog(mode="import", parent=self)
            if dialog.exec_() == QDialog.Accepted:
                selected_settings = dialog.get_selected_settings()
                
                # 获取设置目录路径
                from app.common.path_utils import path_manager
                settings_dir = path_manager.get_settings_path()
                
                # 应用选中的设置
                for file_name, subcategories in selected_settings.items():
                    # 特殊处理：所有设置项实际上都在Settings.json文件中
                    if file_name in ["foundation", "pumping_people", "pumping_reward", "history", "channel", "position"]:
                        file_path = os.path.join(settings_dir, "Settings.json")
                    else:
                        file_path = os.path.join(settings_dir, f"{file_name}.json")
                    
                    if path_manager.file_exists(file_path):
                        # 读取现有设置
                        with open_file(file_path, 'r', encoding='utf-8') as f:
                            current_settings = json.load(f)
                        
                        # 更新选中的设置项
                        for subcategory_name, settings in subcategories.items():
                            if settings:  # 如果有选中的设置项
                                if file_name in ["foundation", "pumping_people", "pumping_reward", "history", "channel", "position"]:
                                    # 这些分类都在Settings.json文件中
                                    if file_name == "channel":
                                        # channel是根级别的字符串，不是嵌套对象
                                        if "channel" in imported_settings:
                                            current_settings["channel"] = imported_settings["channel"]
                                    elif file_name == "position":
                                        # position是根级别的对象
                                        if "position" in imported_settings:
                                            current_settings["position"] = imported_settings["position"]
                                    else:
                                        # foundation、pumping_people、pumping_reward、history等分类
                                        if file_name not in current_settings:
                                            current_settings[file_name] = {}
                                        
                                        for setting_name in settings:
                                            if file_name in imported_settings and setting_name in imported_settings[file_name]:
                                                current_settings[file_name][setting_name] = imported_settings[file_name][setting_name]
                                elif file_name == "voice_engine":
                                    # voice_engine文件中的设置在voice_engine分类下
                                    if "voice_engine" not in current_settings:
                                        current_settings["voice_engine"] = {}
                                    
                                    for setting_name in settings:
                                        if "voice_engine" in imported_settings and setting_name in imported_settings["voice_engine"]:
                                            current_settings["voice_engine"][setting_name] = imported_settings["voice_engine"][setting_name]
                                elif file_name == "plugin_settings":
                                    # plugin_settings文件中的设置在plugin_settings分类下
                                    if "plugin_settings" not in current_settings:
                                        current_settings["plugin_settings"] = {}
                                    
                                    for setting_name in settings:
                                        if "plugin_settings" in imported_settings and setting_name in imported_settings["plugin_settings"]:
                                            current_settings["plugin_settings"][setting_name] = imported_settings["plugin_settings"][setting_name]
                                elif file_name == "config":
                                    # config文件中的设置项分布在不同的分类下
                                    for setting_name in settings:
                                        if setting_name == "DpiScale":
                                            target_section = "Window"
                                        elif setting_name in ["ThemeColor", "ThemeMode"]:
                                            target_section = "QFluentWidgets"
                                        else:
                                            target_section = "config"
                                        
                                        if target_section not in current_settings:
                                            current_settings[target_section] = {}
                                        
                                        if target_section in imported_settings and setting_name in imported_settings[target_section]:
                                            current_settings[target_section][setting_name] = imported_settings[target_section][setting_name]
                                elif file_name == "CleanupTimes":
                                    if file_name not in current_settings:
                                        current_settings[file_name] = imported_settings["cleanuptimes"]
                                elif file_name == "ForegroundSoftware":
                                    if file_name not in current_settings:
                                        current_settings[file_name] = {}
                                    
                                    for setting_name in settings:
                                        if file_name in imported_settings and setting_name in imported_settings[file_name]:
                                            current_settings[file_name][setting_name] = imported_settings[file_name][setting_name]
                                
                        # 保存更新后的设置
                        with open_file(file_path, 'w', encoding='utf-8') as f:
                            json.dump(current_settings, f, indent=4, ensure_ascii=False)
                
                # 显示成功消息
                w = Dialog("导入成功", "设置已成功导入，现在需要重启应用才能生效。", None)
                w.yesButton.setText("确定")
                w.cancelButton.hide()
                w.buttonLayout.insertStretch(1)
                w.exec_()
        except Exception as e:
            logger.error(f"导入设置失败: {str(e)}")
            w = Dialog("导入失败", f"导入设置时发生错误: {str(e)}", None)
            w.yesButton.setText("确定")
            w.cancelButton.hide()
            w.buttonLayout.insertStretch(1)
            w.exec_()
    
    def export_settings(self):
        """导出设置"""
        try:
            # 显示设置选择对话框
            dialog = SettingsSelectionDialog(mode="export", parent=self)
            if dialog.exec_() == QDialog.Accepted:
                selected_settings = dialog.get_selected_settings()
                
                # 获取设置目录路径
                from app.common.path_utils import path_manager
                settings_dir = path_manager.get_settings_path()
                
                # 收集选中的设置
                exported_settings = {}
                
                # 遍历选中的设置项，现在category_name直接就是文件名
                for file_name, subcategories in selected_settings.items():
                    for subcategory_name, settings in subcategories.items():
                        if settings:  # 如果有选中的设置项
                                
                                # 特殊处理：所有设置项实际上都在Settings.json文件中
                                if file_name in ["foundation", "pumping_people", "pumping_reward", "history", "channel", "position"]:
                                    file_path = os.path.join(settings_dir, "Settings.json")
                                else:
                                    file_path = os.path.join(settings_dir, f"{file_name}.json")
                                
                                if path_manager.file_exists(file_path):
                                    # 读取设置文件
                                    with open_file(file_path, 'r', encoding='utf-8') as f:
                                        current_settings = json.load(f)
                                    
                                    # 添加选中的设置项到导出数据
                                    if file_name not in exported_settings:
                                        exported_settings[file_name] = {}
                                    
                                    # 确定在文件中的分类名
                                    section_name = file_name  # 默认分类名与文件名相同
                                    
                                    # 特殊处理Settings.json文件中的多个分类
                                    if file_name in ["foundation", "pumping_people", "pumping_reward", "history", "channel", "position"]:
                                        # 这些分类都在Settings.json文件中
                                        if file_name == "channel":
                                            # channel是根级别的字符串，不是嵌套对象
                                            if "channel" in current_settings:
                                                exported_settings[file_name] = current_settings["channel"]
                                        elif file_name == "position":
                                            # position是根级别的对象
                                            if "position" in current_settings:
                                                exported_settings[file_name] = current_settings["position"]
                                        else:
                                            # foundation、pumping_people、pumping_reward、history等分类直接导出
                                            if file_name in current_settings:
                                                # 如果该分类还没有在导出设置中，则创建
                                                if file_name not in exported_settings:
                                                    exported_settings[file_name] = {}
                                                
                                                # 导出该分类下的所有选中的设置项
                                                for setting_name in settings:
                                                    if setting_name in current_settings[file_name]:
                                                        exported_settings[file_name][setting_name] = current_settings[file_name][setting_name]
                                    elif file_name == "channel":
                                        # channel文件中的设置直接在根级别
                                        for setting_name in settings:
                                            if setting_name in current_settings:
                                                if section_name not in exported_settings[file_name]:
                                                    exported_settings[file_name][section_name] = {}
                                                exported_settings[file_name][section_name][setting_name] = current_settings[setting_name]
                                        continue
                                    elif file_name == "voice_engine":
                                        section_name = "voice_engine"
                                        if section_name not in exported_settings[file_name]:
                                            exported_settings[file_name][section_name] = {}
                                        
                                        for setting_name in settings:
                                            if section_name in current_settings and setting_name in current_settings[section_name]:
                                                exported_settings[file_name][section_name][setting_name] = current_settings[section_name][setting_name]
                                    elif file_name == "plugin_settings":
                                        section_name = "plugin_settings"
                                        if section_name not in exported_settings[file_name]:
                                            exported_settings[file_name][section_name] = {}
                                        
                                        for setting_name in settings:
                                            if section_name in current_settings and setting_name in current_settings[section_name]:
                                                exported_settings[file_name][section_name][setting_name] = current_settings[section_name][setting_name]
                                    elif file_name in ["pumping_people", "pumping_reward"]:
                                        # 特殊处理pumping_people和pumping_reward，需要包含音效设置
                                        section_name = file_name
                                        # 由于这些分类已经在Settings.json处理分支中处理过，这里不需要重复处理
                                        # 确保分类存在
                                        if section_name not in exported_settings:
                                            exported_settings[section_name] = {}
                                        
                                        for setting_name in settings:
                                            # 从Settings.json中对应的分类中获取设置值
                                            if section_name in current_settings and setting_name in current_settings[section_name]:
                                                exported_settings[section_name][setting_name] = current_settings[section_name][setting_name]
                                        
                                        # 如果当前处理的是pumping_reward，并且有音效设置被选中，需要添加音效设置
                                        if file_name == "pumping_reward":
                                            # 检查是否有音效设置被选中
                                            sound_settings = ["animation_music_enabled", "result_music_enabled", 
                                                           "animation_music_volume", "result_music_volume",
                                                           "music_fade_in", "music_fade_out"]
                                            
                                            # 获取选中的音效设置
                                            selected_sound_settings = []
                                            for category_name, subcategories in selected_settings.items():
                                                for subcategory_name, settings_list in subcategories.items():
                                                    if subcategory_name == "音效设置":
                                                        selected_sound_settings = settings_list
                                                        break
                                            
                                            # 如果有音效设置被选中，添加到pumping_reward分类中
                                            if selected_sound_settings:
                                                for sound_setting in selected_sound_settings:
                                                    if sound_setting in sound_settings and sound_setting in current_settings.get("pumping_reward", {}):
                                                        exported_settings[section_name][sound_setting] = current_settings["pumping_reward"][sound_setting]
                                    elif file_name == "config":
                                        # config文件中的设置项分布在不同的分类下
                                        for setting_name in settings:
                                            if setting_name == "DpiScale":
                                                target_section = "Window"
                                            elif setting_name in ["ThemeColor", "ThemeMode"]:
                                                target_section = "QFluentWidgets"
                                            else:
                                                target_section = "config"
                                            
                                            if target_section not in exported_settings[file_name]:
                                                exported_settings[file_name][target_section] = {}
                                            
                                            if target_section in current_settings and setting_name in current_settings[target_section]:
                                                exported_settings[file_name][target_section][setting_name] = current_settings[target_section][setting_name]
                                        continue
                                    else:
                                        # 其他文件的处理
                                        if section_name not in exported_settings[file_name]:
                                            exported_settings[file_name][section_name] = {}
                                        
                                        for setting_name in settings:
                                            if setting_name in current_settings.get(section_name, {}):
                                                exported_settings[file_name][section_name][setting_name] = current_settings[section_name][setting_name]
                                            elif setting_name in current_settings:
                                                # 处理根级别的设置项
                                                exported_settings[file_name][section_name][setting_name] = current_settings[setting_name]
                
                # 打开保存文件对话框
                file_path, _ = QFileDialog.getSaveFileName(
                    self,
                    "保存设置文件",
                    f"settings_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    "设置文件 (*.json)"
                )
                
                if file_path:
                    # 确保文件扩展名是.json
                    if not file_path.endswith('.json'):
                        file_path += '.json'
                    
                    # 保存导出的设置
                    with open_file(file_path, 'w', encoding='utf-8') as f:
                        json.dump(exported_settings, f, indent=4, ensure_ascii=False)
                    
                    # 显示成功消息
                    w = Dialog("导出成功", f"设置已成功导出到:\n{file_path}", None)
                    w.yesButton.setText("确定")
                    w.cancelButton.hide()
                    w.buttonLayout.insertStretch(1)
                    w.exec_()
        except Exception as e:
            logger.error(f"导出设置失败: {str(e)}")
            w = Dialog("导出失败", f"导出设置时发生错误: {str(e)}", None)
            w.yesButton.setText("确定")
            w.cancelButton.hide()
            w.buttonLayout.insertStretch(1)
            w.exec_()




class SettingsSelectionDialog(QDialog):
    """设置选择对话框，用于选择要导入导出的设置项"""
    def __init__(self, mode="export", parent=None):
        super().__init__(parent)
        self.mode = mode  # "export" 或 "import"
        self.setWindowTitle("选择设置项" if mode == "export" else "导入设置")
        self.setMinimumSize(600, 500)  # 设置最小大小而不是固定大小
        self.dragging = False
        self.drag_position = None
        
        # 设置无边框但可调整大小的窗口
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        
        # 创建自定义标题栏
        self.title_bar = QWidget()
        self.title_bar.setObjectName("CustomTitleBar")
        self.title_bar.setFixedHeight(35)
        
        title_layout = QHBoxLayout(self.title_bar)
        title_layout.setContentsMargins(10, 0, 10, 0)
        
        # 创建包含图标的标题布局
        title_content_layout = QHBoxLayout()
        title_content_layout.setContentsMargins(0, 0, 0, 0)
        
        # 添加设置图标
        settings_icon = BodyLabel()
        icon_path = path_manager.get_resource_path('icon', 'SecRandom.png')
        if path_manager.file_exists(icon_path):
            settings_icon.setPixmap(QIcon(str(icon_path)).pixmap(20, 20))
        else:
            # 如果图标文件不存在，使用备用图标
            settings_icon.setPixmap(QIcon.fromTheme("document-properties", QIcon()).pixmap(20, 20))
        title_content_layout.addWidget(settings_icon)
        
        # 添加功能描述标题
        title_text = "导出设置 - 选择要导出的设置项" if mode == "export" else "导入设置 - 选择要导入的设置项"
        self.title_label = BodyLabel(title_text)
        self.title_label.setObjectName("TitleLabel")
        self.title_label.setFont(QFont(load_custom_font(), 12))
        title_content_layout.addWidget(self.title_label)
        title_content_layout.addStretch()
        
        self.close_btn = QPushButton("✕")
        self.close_btn.setObjectName("CloseButton")
        self.close_btn.setFixedSize(25, 25)
        self.close_btn.clicked.connect(self.reject)
        
        # 将标题内容布局添加到主标题布局中
        title_layout.addLayout(title_content_layout)
        title_layout.addWidget(self.close_btn)
        
        # 创建滚动区域
        self.scroll_area = ScrollArea()
        self.scroll_area.setWidgetResizable(True)
        
        # 创建内容容器
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setAlignment(Qt.AlignLeft)
        
        # 创建设置项选择区域
        self.settings_groups = {}
        self.create_setting_selections()
        
        self.scroll_area.setWidget(self.content_widget)
        
        # 创建按钮
        self.select_all_button = PushButton("全选")
        self.deselect_all_button = PushButton("取消全选")
        self.ok_button = PrimaryPushButton("确定")
        self.cancel_button = PushButton("取消")
        
        self.select_all_button.clicked.connect(self.select_all)
        self.deselect_all_button.clicked.connect(self.deselect_all)
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
        
        # 设置字体
        for widget in [self.select_all_button, self.deselect_all_button, self.ok_button, self.cancel_button]:
            widget.setFont(QFont(load_custom_font(), 12))
        
        # 布局
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.select_all_button)
        button_layout.addWidget(self.deselect_all_button)
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.ok_button)
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.title_bar)
        main_layout.addWidget(self.scroll_area)
        main_layout.addLayout(button_layout)
        
        self.setLayout(main_layout)
        
        # 更新主题样式
        self.update_theme_style()
        qconfig.themeChanged.connect(self.update_theme_style)
    
    def create_setting_selections(self):
        """创建设置项选择界面"""
        # 定义按文件分类的设置项结构
        self.settings_structure = {
            "foundation": {
                "主窗口设置": [
                    "main_window_mode", "main_window_focus_mode", "main_window_focus_time",
                    "topmost_switch", "window_width", "window_height", "pumping_floating_side",
                    "pumping_reward_side", "show_settings_icon", "main_window_control_Switch"
                ],
                "设置窗口设置": [
                    "settings_window_mode", "settings_window_width", "settings_window_height"
                ],
                "浮窗设置": [
                    "pumping_floating_enabled", "pumping_floating_transparency_mode", "pumping_floating_visible",
                    "button_arrangement_mode", "flash_window_auto_close", "flash_window_close_time"
                ],
                "启动设置": [
                    "check_on_startup", "self_starting_enabled", "url_protocol_enabled"
                ],
                "全局快捷键设置": [
                    "global_shortcut_enabled", "global_shortcut_target", "global_shortcut_key",
                    "local_pumping_shortcut_key", "local_reward_shortcut_key",
                ]
            },
            "advanced": {
                "浮窗设置": [
                    "floating_window_visibility"
                ]
            },
            "pumping_people": {
                "基础设置": [
                    "draw_mode", "draw_pumping", "student_id", "student_name", "people_theme"
                ],
                "显示设置": [
                    "display_format", "font_size", "animation_color", "show_student_image",
                    "show_random_member", "random_member_format"
                ],
                "动画设置": [
                    "animation_mode", "animation_interval", "animation_auto_play"
                ],
                "音效设置": [
                    "animation_music_enabled", "result_music_enabled",
                    "animation_music_volume", "result_music_volume",
                    "music_fade_in", "music_fade_out"
                ]
            },
            "pumping_reward": {
                "基础设置": [
                    "draw_mode", "draw_pumping", "reward_theme"
                ],
                "显示设置": [
                    "display_format", "font_size", "animation_color", "show_reward_image"
                ],
                "动画设置": [
                    "animation_mode", "animation_interval", "animation_auto_play"
                ],
                "音效设置": [
                    "animation_music_enabled", "result_music_enabled",
                    "animation_music_volume", "result_music_volume",
                    "music_fade_in", "music_fade_out"
                ]
            },
            "history": {
                "抽人历史": [
                    "history_enabled", "probability_weight", "history_days"
                ],
                "抽奖历史": [
                    "reward_history_enabled", "history_reward_days"
                ]
            },
            "channel": {
                "更新设置": [
                    "channel"
                ]
            },
            "position": {
                "位置设置": [
                    "x", "y"
                ]
            },
            "config": {
                "主题与显示": [
                    "ThemeColor", "ThemeMode", "DpiScale"
                ]
            },
            "voice_engine": {
                "语音引擎设置": [
                    "voice_engine", "edge_tts_voice_name", "voice_enabled", "voice_volume",
                    "voice_speed", "system_volume_enabled", "system_volume_value"
                ]
            },
            "plugin_settings": {
                "插件设置": [
                    "run_plugins_on_startup", "fetch_plugin_list_on_startup", "selected_plugin"
                ]
            },
            "CleanupTimes": {
                "清理时间设置": [
                    "cleanuptimes"
                ]
            },
            "ForegroundSoftware": {
                "前台软件设置": [
                    "foregroundsoftware_class", "foregroundsoftware_title", "foregroundsoftware_process"
                ]
            },
        }
        
        # 为每个功能分类创建选择区域
        for category_name, subcategories in self.settings_structure.items():
            file_group = GroupHeaderCardWidget()
            file_group.setTitle(category_name)
            file_group.setBorderRadius(8)
            
            self.settings_groups[category_name] = {}
            
            # 遍历每个子分类和设置项，为每个设置项创建独立的分组
            for subcategory_name, settings in subcategories.items():
                self.settings_groups[category_name][subcategory_name] = {}
                
                # 为每个设置项创建独立的分组
                for setting in settings:
                    # 创建独立的设置项容器
                    setting_widget = QWidget()
                    setting_layout = QVBoxLayout(setting_widget)
                    setting_layout.setAlignment(Qt.AlignLeft)
                    setting_layout.setSpacing(4)
                    
                    # 创建复选框
                    checkbox = CheckBox(self.get_setting_display_name(setting))
                    checkbox.setFont(QFont(load_custom_font(), 10))
                    checkbox.setChecked(True)
                    self.settings_groups[category_name][subcategory_name][setting] = checkbox
                    
                    # 创建水平布局让复选框靠左
                    checkbox_layout = QHBoxLayout()
                    checkbox_layout.addWidget(checkbox)
                    checkbox_layout.setAlignment(Qt.AlignLeft)
                    checkbox_layout.addStretch()
                    
                    # 将复选框布局添加到设置布局中
                    checkbox_widget = QWidget()
                    checkbox_widget.setLayout(checkbox_layout)
                    setting_layout.addWidget(checkbox_widget)
                    
                    # 简化分类逻辑，直接使用子分类名称和设置项显示名称
                    display_name = self.get_setting_display_name(setting)
                    file_group.addGroup(None, subcategory_name, f"{display_name}设置项", setting_widget)
            
            self.content_layout.addWidget(file_group)

    def get_setting_display_name(self, setting_name):
        """获取设置项的显示名称"""
        display_names = {
            # foundation设置
            "check_on_startup": "启动时检查更新", # 有
            "self_starting_enabled": "开机自启动", # 有
            "pumping_floating_enabled": "浮窗启用", # 有
            "pumping_floating_side": "抽人侧边栏位置", # 有
            "pumping_reward_side": "抽奖侧边栏位置", # 有
            "show_settings_icon": "显示设置图标", # 有
            "pumping_floating_transparency_mode": "浮窗透明度", # 有
            "main_window_focus_mode": "主窗口焦点模式", # 有
            "main_window_focus_time": "焦点检测时间", # 有
            "main_window_mode": "主窗口位置", # 有
            "main_window_control_Switch": "控制面板位置", # 有
            "settings_window_mode": "设置窗口位置", # 有
            "pumping_floating_visible": "浮窗", # 有
            "button_arrangement_mode": "浮窗按钮布局", # 有
            "flash_window_auto_close": "闪抽窗口自动关闭", # 有
            "flash_window_close_time": "闪抽窗口关闭时间", # 有
            "topmost_switch": "主窗口置顶", # 有
            "window_width": "主窗口宽度", # 有
            "window_height": "主窗口高度", # 有
            "settings_window_width": "设置窗口宽度", # 有
            "settings_window_height": "设置窗口高度", # 有
            "url_protocol_enabled": "URL协议注册", # 有
            "global_shortcut_enabled": "全局快捷键启用", # 有
            "global_shortcut_target": "全局快捷键目标", # 有
            "global_shortcut_key": "全局快捷键", # 有
            "local_pumping_shortcut_key": "抽人操作快捷键", # 有
            "local_reward_shortcut_key": "抽奖操作快捷键", # 有
            # advanced设置
            "floating_window_visibility": "浮窗显隐条件", # 有
            # pumping_people设置（跟pumping_reward设置有重复的不计入）
            "student_id": "显示学号", # 有
            "student_name": "显示姓名", # 有
            "people_theme": "主题", # 有
            "show_random_member": "显示随机成员", # 有
            "random_member_format": "随机成员格式", # 有
            "show_student_image": "显示学生图片", # 有
            # pumping_reward设置（跟pumping_people设置有重复的不计入）
            "reward_theme": "主题", # 有
            "show_reward_image": "显示奖品图片", # 有
            # pumping_people设置和pumping_reward设置 重复设置项
            "draw_mode": "抽取模式", # 有
            "draw_pumping": "抽取方式", # 有
            "animation_mode": "动画模式", # 有
            "animation_interval": "动画间隔", # 有
            "animation_auto_play": "自动播放", # 有
            "animation_music_enabled": "动画音乐", # 有
            "result_music_enabled": "结果音乐", # 有
            "animation_music_volume": "动画音量", # 有
            "result_music_volume": "结果音量", # 有
            "music_fade_in": "音乐淡入", # 有
            "music_fade_out": "音乐淡出", # 有
            "display_format": "显示格式", # 有
            "animation_color": "动画颜色", # 有
            "font_size": "字体大小", # 有
            # history设置
            "history_enabled": "历史记录启用", # 有
            "probability_weight": "概率权重", # 有
            "history_days": "历史记录天数", # 有
            "reward_history_enabled": "奖品历史启用", # 有
            "history_reward_days": "奖品历史天数", # 有
            # position设置
            "x": "浮窗X坐标", # 有
            "y": "浮窗Y坐标", # 有
            # channel设置
            "channel": "更新通道", # 有
            # config设置
            "DpiScale": "DPI缩放", # 有
            "ThemeColor": "主题颜色", # 有
            "ThemeMode": "主题模式", # 有
            # plugin_settings设置
            "run_plugins_on_startup": "启动时运行插件", # 有
            "fetch_plugin_list_on_startup": "启动时获取插件列表", # 有
            "selected_plugin": "选中插件", # 有
            # voice_engine设置
            "voice_engine": "语音引擎", # 有
            "edge_tts_voice_name": "Edge TTS语音", # 有
            "voice_enabled": "语音启用", # 有
            "voice_volume": "语音音量", # 有
            "voice_speed": "语音速度", # 有
            "system_volume_enabled": "系统音量控制", # 有
            "system_volume_value": "系统音量值", # 有
            # CleanupTimes设置
            "cleanuptimes": "清理时间", # 有
            # ForegroundSoftware设置
            "foregroundsoftware_class": "前台软件类名", # 有
            "foregroundsoftware_title": "前台软件标题", # 有
            "foregroundsoftware_process": "前台软件进程名", # 有
        }
        return display_names.get(setting_name, setting_name)
    
    def select_all(self):
        """全选所有设置项"""
        for category_name in self.settings_groups:
            for subcategory_name in self.settings_groups[category_name]:
                for setting_name in self.settings_groups[category_name][subcategory_name]:
                    self.settings_groups[category_name][subcategory_name][setting_name].setChecked(True)
    
    def deselect_all(self):
        """取消全选所有设置项"""
        for category_name in self.settings_groups:
            for subcategory_name in self.settings_groups[category_name]:
                for setting_name in self.settings_groups[category_name][subcategory_name]:
                    self.settings_groups[category_name][subcategory_name][setting_name].setChecked(False)
    
    def get_selected_settings(self):
        """获取选中的设置项"""
        selected = {}
        for file_name in self.settings_groups:
            selected[file_name] = {}
            for subcategory_name in self.settings_groups[file_name]:
                selected[file_name][subcategory_name] = []
                for setting_name in self.settings_groups[file_name][subcategory_name]:
                    if self.settings_groups[file_name][subcategory_name][setting_name].isChecked():
                        selected[file_name][subcategory_name].append(setting_name)
        return selected
    
    def mousePressEvent(self, event):
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
        colors = {'text': '#F5F5F5', 'bg': '#111116', 'title_bg': '#2D2D2D'} if is_dark else {'text': '#111116', 'bg': '#F5F5F5', 'title_bg': '#E0E0E0'}
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
            QLabel, QPushButton, QCheckBox {{ color: {colors['text']}; }}
        """)
        
        # 设置标题栏颜色（仅Windows系统）
        if os.name == 'nt':
            try:
                import ctypes
                hwnd = int(self.winId())
                bg_color = colors['bg'].lstrip('#')
                rgb_color = int(f'FF{bg_color}', 16) if len(bg_color) == 6 else int(bg_color, 16)
                
                ctypes.windll.dwmapi.DwmSetWindowAttribute(
                    ctypes.c_int(hwnd), 35,
                    ctypes.byref(ctypes.c_uint(rgb_color)),
                    ctypes.sizeof(ctypes.c_uint)
                )
            except Exception as e:
                logger.warning(f"设置标题栏颜色失败: {str(e)}")
