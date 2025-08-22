from qfluentwidgets import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtNetwork import *


import os
import sys
import importlib.util
import json
from loguru import logger
from pathlib import Path

from app.common.config import load_custom_font, is_dark_theme
from app.common.path_utils import path_manager
from app.common.path_utils import open_file, ensure_dir

class LevitationWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.app_dir = path_manager._app_root
        self._load_settings()  # 加载配置
        self._load_plugin_settings()  # 加载插件设置
        self._init_ui_components()  # 初始化UI组件
        self._setup_event_handlers()  # 设置事件处理器
        self._init_drag_system()  # 初始化拖动系统
        self.load_position()

    def _load_settings(self):
        # 小鸟游星野：加载基础设置和透明度配置
        settings_path = path_manager.get_settings_path()
        try:
            ensure_dir(settings_path.parent)
            with open_file(settings_path, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                foundation_settings = settings.get('foundation', {})
                self.transparency_mode = foundation_settings.get('pumping_floating_transparency_mode', 6)
                self.floating_visible = foundation_settings.get('pumping_floating_visible', 0)
                # 确保透明度值在有效范围内
                self.transparency_mode = max(0, min(self.transparency_mode, 9))
        except (FileNotFoundError, json.JSONDecodeError) as e:
            self.transparency_mode = 6
            self.floating_visible = 0
            logger.error(f"加载基础设置失败: {e}")

    def _load_plugin_settings(self):
        # 小鸟游星野：加载插件设置
        settings_path = path_manager.get_settings_path('plugin_settings.json')
        try:
            ensure_dir(settings_path.parent)
            with open_file(settings_path, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                plugin_settings = settings.get('plugin_settings', {})
                self.selected_plugin = plugin_settings.get('selected_plugin', '主窗口')
        except (FileNotFoundError, json.JSONDecodeError) as e:
            self.selected_plugin = '主窗口'
            logger.error(f"加载插件设置失败: {e}")

    def _init_ui_components(self):
        # 白露：初始化所有UI组件
        self._setup_main_layout()
        if self.floating_visible == 0:
            self._init_menu_label()
            self._init_people_label()
        elif self.floating_visible == 1:
            self._init_people_label()
        elif self.floating_visible == 2:
            self._init_people_label()
        self._apply_window_styles()

    def _setup_main_layout(self):
        # 小鸟游星野：设置主布局容器
        self.container_button = QWidget()
        button_layout = QHBoxLayout(self.container_button)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(0)

        main_layout = QHBoxLayout(self)
        main_layout.addWidget(self.container_button)
        self.setLayout(main_layout)

    def _init_menu_label(self):
        # 白露：初始化菜单标签
        MENU_DEFAULT_ICON_PATH = path_manager.get_resource_path("icon", "SecRandom_menu_30%.png")
        self.menu_label = QLabel(self.container_button)
        try:
            icon_path = path_manager.get_resource_path("icon", f"SecRandom_menu_{(10 - self.transparency_mode) * 10}%.png")
            if not icon_path.exists():
                icon_path = MENU_DEFAULT_ICON_PATH
            pixmap = QPixmap(str(icon_path))
            self.menu_label.setPixmap(pixmap.scaled(27, 27, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        except FileNotFoundError as e:
            pixmap = QPixmap(str(MENU_DEFAULT_ICON_PATH))
            self.menu_label.setPixmap(pixmap.scaled(27, 27, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            logger.error(f"加载菜单图标失败: {e}")

        self.menu_label.setStyleSheet('opacity: 0;')
        self.menu_label.setFixedSize(40, 50)
        self.menu_label.setAlignment(Qt.AlignCenter)
        self.menu_label.setFont(QFont(load_custom_font(), 12))
        self.container_button.layout().addWidget(self.menu_label)

    def _init_people_label(self):
        # 小鸟游星野：初始化人物标签
        FLOATING_DEFAULT_ICON_PATH = path_manager.get_resource_path("icon", "SecRandom_floating_30%.png")
        self.people_label = QLabel(self.container_button)
        try:
            icon_path = path_manager.get_resource_path("icon", f"SecRandom_floating_{(10 - self.transparency_mode) * 10}%.png")
            if not icon_path.exists():
                icon_path = FLOATING_DEFAULT_ICON_PATH
            pixmap = QPixmap(str(icon_path))
            self.people_label.setPixmap(pixmap.scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        except FileNotFoundError as e:
            pixmap = QPixmap(str(FLOATING_DEFAULT_ICON_PATH))
            self.people_label.setPixmap(pixmap.scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            logger.error(f"加载人物图标失败: {e}")

        self.people_label.setStyleSheet('opacity: 0;')
        self.people_label.setFixedSize(60, 50)
        self.people_label.setAlignment(Qt.AlignCenter)
        self.people_label.setFont(QFont(load_custom_font(), 12))
        self.container_button.layout().addWidget(self.people_label)

    def _apply_window_styles(self):
        # 白露：应用窗口样式和标志
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        try:
            opacity = (10 - self.transparency_mode) * 0.1
            self.setStyleSheet(f'border-radius: 5px; background-color: rgba(65, 66, 66, {opacity});')
        except Exception as e:
            self.setStyleSheet('border-radius: 5px; background-color: rgba(65, 66, 66, 0.3);')
            logger.error(f"应用窗口样式失败: {e}")

    def _setup_event_handlers(self):
        # 小鸟游星野：设置所有事件处理器 - 无论控件是否显示都要绑定 ✧(๑•̀ㅂ•́)و✧
        if hasattr(self, 'menu_label') and self.menu_label is not None:
            self.menu_label.mousePressEvent = self.start_drag
            self.menu_label.mouseReleaseEvent = self.stop_drag

        # 白露：人物标签始终存在，必须绑定事件处理器
        self.people_label.mousePressEvent = self.on_people_press
        self.people_label.mouseReleaseEvent = self.on_people_release

    def _init_drag_system(self):
        # 白露：初始化拖动系统
        self.drag_position = QPoint()
        self.drag_start_position = QPoint()
        self.is_dragging = False
        self.click_timer = QTimer(self)
        self.click_timer.setSingleShot(True)
        self.click_timer.timeout.connect(self.start_drag)

        self.move_timer = QTimer(self)
        self.move_timer.setSingleShot(True)
        self.move_timer.timeout.connect(self.save_position)

    def on_people_press(self, event):
        # 小鸟游星野：记录拖动起始位置 ✧(๑•̀ㅂ•́)ow✧
        self.drag_start_position = event.pos()
        # 启动长按计时器（100毫秒 - 进一步优化响应速度）
        self.click_timer.start(100)

    def on_people_release(self, event):
        if self.click_timer.isActive():
            # 短按：停止计时器并触发点击事件
            self.click_timer.stop()
            self.on_people_clicked()
            # 长按：计时器已触发拖动，不执行点击

    # 白露：处理人物标签点击事件（忽略事件参数）
    def on_people_clicked(self, event=None):
        # 小鸟游星野：检查floating_visible设置，决定显示内容 ✧(๑•̀ㅂ•́)و✧
        if self.floating_visible in [2, 3]:
            # 显示直接抽取窗口
            self._show_direct_extraction_window()
            return
            
        # 获取当前选中的插件
        self._load_plugin_settings()
        selected_plugin = self.selected_plugin
        logger.info(f"人物标签被点击，当前选中的插件: {selected_plugin}")
        
        if selected_plugin and selected_plugin != "主窗口":
            # 加载并打开选中的插件窗口
            self._open_plugin_window(selected_plugin)
        else:
            # 如果没有选中插件或选中的是主窗口插件，查找主窗口
            main_window = None
            for widget in QApplication.topLevelWidgets():
                if hasattr(widget, 'toggle_window'):  # 通过特征识别主窗口
                    main_window = widget
                    break

            if main_window:
                main_window.toggle_window()
            else:
                logger.error("未找到主窗口实例")
                self.show_connection_error_dialog()
    
    def _open_plugin_window(self, plugin_name):
        """打开指定插件的窗口"""
        # 获取插件目录
        plugin_dir = path_manager.get_plugin_path("plugin")
        
        # 查找插件信息
        plugin_info = None
        plugin_path = None
        
        # 遍历插件目录，查找匹配的插件
        if path_manager.file_exists(plugin_dir):
            for folder in os.listdir(plugin_dir):
                folder_path = os.path.join(plugin_dir, folder)
                if os.path.isdir(folder_path):
                    info_file = os.path.join(folder_path, "plugin.json")
                    if path_manager.file_exists(info_file):
                        try:
                            with open_file(info_file, "r", encoding="utf-8") as f:
                                info = json.load(f)
                                if info.get("name") == plugin_name:
                                    plugin_info = info
                                    plugin_path = folder_path
                                    break
                        except Exception as e:
                            logger.error(f"读取插件信息文件失败: {e}")
                            continue
        
        if not plugin_info or not plugin_path:
            logger.error(f"未找到插件: {plugin_name}")
            error_dialog = Dialog("插件未找到", f"未找到插件: {plugin_name}", self)
            error_dialog.yesButton.setText("确定")
            error_dialog.cancelButton.hide()
            error_dialog.buttonLayout.insertStretch(1)
            error_dialog.exec()
            return
        
            # 获取插件入口文件路径
        entry_point = plugin_info.get("entry_point", "main.py")
        plugin_file_path = path_manager.get_plugin_path(f"plugin/{os.path.basename(plugin_path)}/{entry_point}")
            
        if not path_manager.file_exists(plugin_file_path):
            logger.warning(f"插件 {plugin_name} 的入口文件 {entry_point} 不存在")
            error_dialog = Dialog("文件不存在", f"插件 {plugin_name} 的入口文件 {entry_point} 不存在", self)
            error_dialog.yesButton.setText("确定")
            error_dialog.cancelButton.hide()
            error_dialog.buttonLayout.insertStretch(1)
            error_dialog.exec()
            return
        
        logger.info(f"正在加载插件: {plugin_name}")
        
        try:
            # 使用importlib动态导入插件
            spec = importlib.util.spec_from_file_location(f"plugin_{plugin_info.get('folder_name', plugin_name)}", plugin_file_path)
            if spec is None or spec.loader is None:
                raise ImportError(f"无法加载插件文件: {plugin_file_path}")
            
            plugin_module = importlib.util.module_from_spec(spec)
            
            # 添加插件目录到sys.path，以便插件可以导入自己的模块
            if plugin_path not in sys.path:
                sys.path.insert(0, plugin_path)
            
            # 添加插件专属site-packages目录到sys.path，以便插件可以使用安装的依赖
            plugin_site_packages = path_manager.get_plugin_path(f"plugin/{os.path.basename(plugin_path)}/site-packages")
            if path_manager.file_exists(plugin_site_packages) and plugin_site_packages not in sys.path:
                sys.path.insert(0, plugin_site_packages)
                logger.info(f"已添加插件专属site-packages到Python路径: {plugin_site_packages}")
            
            # 尝试加载模块
            try:
                spec.loader.exec_module(plugin_module)
                logger.info(f"成功加载插件模块: {plugin_name}")
                
                # 检查插件是否有设置界面函数
                if hasattr(plugin_module, 'show_dialog'):
                    logger.info(f"调用插件主函数: {plugin_name}")
                    plugin_module.show_dialog(self)
                else:
                    # 如果没有标准函数，显示提示
                    info_dialog = Dialog("插件信息", f"插件 {plugin_name} 已成功加载，但没有提供标准的设置界面函数", self)
                    info_dialog.yesButton.setText("确定")
                    info_dialog.cancelButton.hide()
                    info_dialog.buttonLayout.insertStretch(1)
                    info_dialog.exec()
                    
            except ImportError as ie:
                # 处理导入错误，可能是缺少依赖库
                logger.error(f"插件 {plugin_name} 导入失败: {ie}")
                error_dialog = Dialog("加载失败", f"无法加载插件 {plugin_name}: {str(ie)}\n请检查插件是否缺少必要的依赖库", self)
                error_dialog.yesButton.setText("确定")
                error_dialog.cancelButton.hide()
                error_dialog.buttonLayout.insertStretch(1)
                error_dialog.exec()
                    
            except Exception as e:
                # 处理其他异常
                logger.error(f"插件 {plugin_name} 执行失败: {e}")
                error_dialog = Dialog("执行失败", f"插件 {plugin_name} 执行失败: {str(e)}", self)
                error_dialog.yesButton.setText("确定")
                error_dialog.cancelButton.hide()
                error_dialog.buttonLayout.insertStretch(1)
                error_dialog.exec()
                
        except Exception as e:
            # 处理模块加载失败
            logger.error(f"无法加载插件 {plugin_name}: {e}")
            error_dialog = Dialog("加载失败", f"无法加载插件 {plugin_name}: {str(e)}", self)
            error_dialog.yesButton.setText("确定")
            error_dialog.cancelButton.hide()
            error_dialog.buttonLayout.insertStretch(1)
            error_dialog.exec()

    def start_drag(self, event=None):
        # 白露：开始拖动逻辑 - 使用之前记录的起始位置
        self.drag_position = self.drag_start_position
        self.is_dragging = True

    def mouseMoveEvent(self, event):
        # 白露：处理鼠标移动事件 - 实现窗口跟随拖动
        # 检测长按计时期间的鼠标移动，超过阈值立即触发拖动
        if self.click_timer.isActive() and event.buttons() == Qt.LeftButton:
            delta = event.pos() - self.drag_start_position
            if abs(delta.x()) > 2 or abs(delta.y()) > 2:
                self.click_timer.stop()
                self.start_drag()

        if hasattr(self, 'is_dragging') and self.is_dragging and event.buttons() == Qt.LeftButton:
            # 计算鼠标移动偏移量并保持相对位置
            delta = event.globalPos() - self.mapToGlobal(self.drag_position)
            # 移动窗口到新位置
            new_pos = self.pos() + delta

            # 获取屏幕尺寸
            screen = QApplication.desktop().screenGeometry()

            # 限制窗口不超出屏幕
            new_pos.setX(max(0, min(new_pos.x(), screen.width() - self.width())))
            new_pos.setY(max(0, min(new_pos.y(), screen.height() - self.height())))

            self.move(new_pos)
        super().mouseMoveEvent(event)

    def on_people_release(self, event):
        # 星穹铁道白露：人物标签释放事件处理 - 区分点击和拖动 (≧∇≦)ﾉ
        was_dragging = getattr(self, 'is_dragging', False)
        self.is_dragging = False
        
        if self.click_timer.isActive():
            # 小鸟游星野：短按点击，触发主页面打开 ✧(๑•̀ㅂ•́)و✧
            self.click_timer.stop()
            self.on_people_clicked()
        elif was_dragging:
            # 白露：拖动结束，保存新位置 (≧∇≦)ﾉ
            self.save_position()
        
        event.accept()

    def show_connection_error_dialog(self):
        # 小鸟游星野：显示连接错误对话框
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setWindowTitle("连接错误")
        msg_box.setText("无法连接到主窗口")
        msg_box.setInformativeText("请检查应用程序是否正常运行")
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()

    def mousePressEvent(self, event):
        # 星穹铁道白露：右键点击也会触发事件哦~ 要检查正确的控件呀 (๑•̀ㅂ•́)و✧
        if event.button() and hasattr(self, 'menu_label') and event.pos() in self.menu_label.geometry():
            self.start_drag(event)
        else:
            event.ignore()

    def stop_drag(self, event=None):
        # 小鸟游星野：停止拖动时的处理逻辑 - 菜单标签专用 ✧(๑•̀ㅂ•́)و✧
        self.setCursor(Qt.ArrowCursor)
        self.move_timer.stop()
        
        # 白露：菜单标签拖动结束，保存新位置
        self.save_position()
        
        # 小鸟游星野：延迟保存，避免频繁写入
        self.move_timer.start(300)
        
        if event:
            event.accept()

    def save_position(self):
        pos = self.pos()
        settings_path = path_manager.get_settings_path("Settings.json")
        try:
            with open_file(settings_path, "r") as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            data = {}
        
        data["position"] = {
            "x": pos.x(), 
            "y": pos.y()
        }
        with open_file(settings_path, "w") as f:
            json.dump(data, f, indent=4)
        
    def load_position(self):
        settings_path = path_manager.get_settings_path("Settings.json")
        try:
            with open_file(settings_path, "r") as f:
                data = json.load(f)
                pos = data.get("position", {"x": 100, "y": 100})
                self.move(QPoint(pos["x"], pos["y"]))
        except (FileNotFoundError, json.JSONDecodeError):
            screen = QApplication.desktop().screenGeometry()
            x = (screen.width() - self.width()) // 2
            y = (screen.height() - self.height()) // 2
            self.move(QPoint(x, y))

    def _show_direct_extraction_window(self):
        # 小鸟游星野：显示直接抽取窗口 - 包含pumping_people功能 ✧(๑•̀ㅂ•́)و✧
        try:
            # 导入pumping_people模块
            from app.view.main_page.levitation_pumping_people import pumping_people
            from app.common.config import qconfig, is_dark_theme
            # 创建pumping_people实例，直接作为窗口的内容
            self.pumping_widget = pumping_people()

            self.pumping_widget.setWindowTitle("SecRandom")
            self.pumping_widget.setFixedSize(600, 400)
            self.pumping_widget.setWindowFlags(Qt.Window | Qt.WindowStaysOnTopHint)
            
            self.update_theme_style()
            
            # 窗口居中显示 - 相对于屏幕居中
            screen = QApplication.desktop().screenGeometry()
            x = (screen.width() - self.pumping_widget.width()) // 2
            y = (screen.height() - self.pumping_widget.height()) // 2
            self.pumping_widget.move(QPoint(x, y))
            
            # 直接显示窗口
            self.pumping_widget.show()
            logger.info("直接抽取窗口已打开")
            self.pumping_widget.start_draw()
            
        except ImportError as e:
            logger.error(f"导入pumping_people模块失败: {e}")
            error_dialog = Dialog("加载失败", "无法加载抽取功能模块，请检查文件是否存在", self)
            error_dialog.yesButton.setText("确定")
            error_dialog.cancelButton.hide()
            error_dialog.buttonLayout.insertStretch(1)
            error_dialog.exec()
            
        except Exception as e:
            logger.error(f"创建直接抽取窗口失败: {e}")
            error_dialog = Dialog("创建失败", f"创建抽取窗口时发生错误: {str(e)}", self)
            error_dialog.yesButton.setText("确定")
            error_dialog.cancelButton.hide()
            error_dialog.buttonLayout.insertStretch(1)
            error_dialog.exec()

    def update_theme_style(self):
        """根据当前主题更新样式"""
        if qconfig.theme == Theme.AUTO:
            lightness = QApplication.palette().color(QPalette.Window).lightness()
            is_dark = lightness <= 127
        else:
            is_dark = qconfig.theme == Theme.DARK
        
        colors = {'text': '#F5F5F5', 'bg': '#111116', 'title_bg': '#2D2D2D'} if is_dark else {'text': '#111116', 'bg': '#F5F5F5', 'title_bg': '#E0E0E0'}
        self.pumping_widget.setStyleSheet(f"""
            QDialog {{ background-color: {colors['bg']}; border-radius: 5px; }}
            #CustomTitleBar {{ background-color: {colors['title_bg']}; }}
            #TitleLabel {{ color: {colors['text']}; font-weight: bold; padding: 5px; }}
            #CloseButton {{ 
                background-color: transparent; 
                color: {colors['text']}; 
                border-radius: 4px; 
                font-weight: bold; 
                border: none;
            }}
            #CloseButton:hover {{ 
                background-color: #ff4d4d; 
                color: white; 
                border: none;
            }}
            QLabel, QPushButton, QTextEdit {{ color: {colors['text']}; }}
            QLineEdit {{ 
                background-color: {colors['bg']}; 
                color: {colors['text']}; 
                border: 1px solid #555555; 
                border-radius: 4px; 
                padding: 5px; 
            }}
            QPushButton {{ 
                background-color: {colors['bg']}; 
                color: {colors['text']}; 
                border: 1px solid #555555; 
                border-radius: 4px; 
                padding: 5px; 
            }}
            QPushButton:hover {{ background-color: #606060; }}
            QComboBox {{ 
                background-color: {colors['bg']}; 
                color: {colors['text']}; 
                border: 1px solid #555555; 
                border-radius: 4px; 
                padding: 5px; 
            }}
        """)
        
        # 设置标题栏颜色以匹配背景色（仅Windows系统）
        if os.name == 'nt':
            try:
                import ctypes
                hwnd = int(self.pumping_widget.winId())
                
                bg_color = colors['bg'].lstrip('#')
                rgb_color = int(f'FF{bg_color}', 16) if len(bg_color) == 6 else int(bg_color, 16)
                
                ctypes.windll.dwmapi.DwmSetWindowAttribute(
                    ctypes.c_int(hwnd),
                    35,
                    ctypes.byref(ctypes.c_uint(rgb_color)),
                    ctypes.sizeof(ctypes.c_uint)
                )
            except Exception as e:
                logger.warning(f"设置标题栏颜色失败: {str(e)}")

class ConvenientMiniWindow(QWidget):
    # 白露：便捷小窗类 - 提供便捷操作界面 (≧∇≦)ﾉ
    def __init__(self, parent=None):
        super().__init__(parent)
        # 便捷小窗的具体实现将在后续版本中完成
        pass
        
    def show_window(self):
        # 小鸟游星野：显示便捷小窗 ✧(๑•̀ㅂ•́)و✧
        # 具体实现将在后续版本中完成
        pass