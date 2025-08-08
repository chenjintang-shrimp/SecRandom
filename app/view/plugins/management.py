from qfluentwidgets import *
from qfluentwidgets import FluentIcon as FIF
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import os
import json
import shutil
import importlib
import importlib.util
import subprocess
import sys
from loguru import logger

from app.common.config import get_theme_icon, load_custom_font


class ReadmeDialog(QDialog):
    """插件说明文件显示对话框"""
    def __init__(self, plugin_info, parent=None):
        super().__init__(parent)
        
        self.plugin_info = plugin_info
        self.readme_path = plugin_info['readme_path']
        
        # 设置无边框窗口样式
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self.setWindowTitle(f'{plugin_info["name"]} - 说明文件')
        self.setMinimumSize(800, 600)
        self.setSizeGripEnabled(True)  # 启用右下角拖动柄
        
        self.update_theme_style()
        qconfig.themeChanged.connect(self.update_theme_style)
        
        self.dragging = False
        self.drag_position = None
        
        # 创建自定义标题栏
        self.title_bar = QWidget()
        self.title_bar.setObjectName("CustomTitleBar")
        self.title_bar.setFixedHeight(35)
        
        # 标题栏布局
        title_layout = QHBoxLayout(self.title_bar)
        title_layout.setContentsMargins(10, 0, 10, 0)
        
        # 窗口标题
        self.title_label = QLabel(f'{plugin_info["name"]} - 说明文件')
        self.title_label.setObjectName("TitleLabel")
        self.title_label.setFont(QFont(load_custom_font(), 12))
        
        # 窗口控制按钮
        self.close_btn = QPushButton("✕")
        self.close_btn.setObjectName("CloseButton")
        self.close_btn.setFixedSize(25, 25)
        self.close_btn.clicked.connect(self.reject)
        
        # 添加到标题栏布局
        title_layout.addWidget(self.title_label)
        title_layout.addStretch()
        title_layout.addWidget(self.close_btn)
        
        # 创建主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 添加标题栏
        main_layout.addWidget(self.title_bar)
        
        # 创建内容区域
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        
        # 创建文本浏览器
        self.text_browser = TextBrowser()
        self.text_browser.setReadOnly(True)
        self.text_browser.setOpenLinks(True)
        self.text_browser.setOpenExternalLinks(True)
        # 加载readme内容
        self._load_readme_content()
        # 添加到内容布局
        content_layout.addWidget(self.text_browser)
        # 添加内容区域到主布局
        main_layout.addWidget(content_widget)
        # 设置布局
        self.setLayout(main_layout)
    
    def _load_readme_content(self):
        """加载readme文件内容"""
        try:
            with open(self.readme_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.text_browser.setMarkdown(content)
            self.text_browser.setFont(QFont(load_custom_font()))
        except UnicodeDecodeError:
            # 如果UTF-8解码失败，尝试其他编码
            try:
                with open(self.readme_path, 'r', encoding='gbk') as f:
                    content = f.read()
                self.text_browser.setMarkdown(content)
                self.text_browser.setFont(QFont(load_custom_font()))
            except Exception as e:
                self.text_browser.setMarkdown(f"无法读取文件内容: {str(e)}")
                self.text_browser.setFont(QFont(load_custom_font()))
        except Exception as e:
            self.text_browser.setMarkdown(f"读取文件时发生错误: {str(e)}")
            self.text_browser.setFont(QFont(load_custom_font()))
    
    def mousePressEvent(self, event):
        # 窗口拖动功能
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
        """根据当前主题更新样式"""
        if qconfig.theme == Theme.AUTO:
            # 获取系统当前主题
            lightness = QApplication.palette().color(QPalette.Window).lightness()
            is_dark = lightness <= 127
        else:
            is_dark = qconfig.theme == Theme.DARK
        
        # 主题样式更新
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
                border: none;
            }}
            #CloseButton:hover {{ 
                background-color: #ff4d4d; 
                color: white; 
                border: none;
            }}
            QTextBrowser {{ 
                background-color: {colors['bg']}; 
                color: {colors['text']}; 
                border: 1px solid #555555; 
                border-radius: 4px; 
                padding: 10px; 
                font-family: 'Consolas', 'Monaco', monospace;
            }}
        """)


class PluginButtonGroup(QWidget):
    def _get_python_executable(self):
        """获取可用的Python可执行文件，包括嵌入式Python"""
        import shutil
        import tempfile
        import urllib.request
        import zipfile
        import os
        
        # 首先尝试系统Python
        if shutil.which("python"):
            return "python"
        if shutil.which("python3"):
            return "python3"
        if sys.executable and os.path.exists(sys.executable):
            return sys.executable
            
        # 尝试查找嵌入式Python
        app_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        embedded_python_paths = [
            os.path.join(app_dir, "python", "python.exe"),
            os.path.join(app_dir, "python", "python.exe"),
            os.path.join(os.getcwd(), "python", "python.exe"),
            os.path.join(tempfile.gettempdir(), "secrandom_python", "python.exe")
        ]
        
        for path in embedded_python_paths:
            if os.path.exists(path):
                return path
                
        # 如果没有找到Python，尝试下载嵌入式Python
        try:
            return self._download_embedded_python()
        except Exception as e:
            logger.error(f"下载嵌入式Python失败: {e}")
            return None
    
    def _download_embedded_python(self):
        """下载嵌入式Python解释器"""
        import tempfile
        import urllib.request
        import zipfile
        import os
        
        # 创建临时目录
        temp_dir = os.path.join(tempfile.gettempdir(), "secrandom_python")
        os.makedirs(temp_dir, exist_ok=True)
        
        python_exe = os.path.join(temp_dir, "python.exe")
        
        # 如果已经下载过，直接返回
        if os.path.exists(python_exe):
            return python_exe
            
        # 检测系统架构
        import platform
        architecture = platform.machine().lower()
        logger.info(f"检测到系统架构: {architecture}")
        
        # Python嵌入式版本下载URL（Windows版本）
        python_version = "3.8.10"  # 使用稳定的Python版本
        
        # 根据系统架构选择对应的Python版本
        if architecture in ('amd64', 'x86_64', 'x64'):
            # 64位系统
            download_url = f"https://www.python.org/ftp/python/{python_version}/python-{python_version}-embed-amd64.zip"
            logger.info("使用64位Python嵌入式版本")
        elif architecture in ('x86', 'i386', 'i686'):
            # 32位系统
            download_url = f"https://www.python.org/ftp/python/{python_version}/python-{python_version}-embed-win32.zip"
            logger.info("使用32位Python嵌入式版本")
        else:
            # 默认使用64位版本
            logger.warning(f"未识别的架构 {architecture}，默认使用64位Python嵌入式版本")
            download_url = f"https://www.python.org/ftp/python/{python_version}/python-{python_version}-embed-amd64.zip"
        
        logger.info(f"正在下载嵌入式Python: {download_url}")
        
        try:
            # 下载zip文件
            zip_path = os.path.join(temp_dir, "python_embedded.zip")
            urllib.request.urlretrieve(download_url, zip_path)
            
            # 解压文件
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            
            # 删除zip文件
            os.remove(zip_path)
            
            # 下载get-pip.py
            pip_url = "https://bootstrap.pypa.io/get-pip.py"
            get_pip_path = os.path.join(temp_dir, "get-pip.py")
            urllib.request.urlretrieve(pip_url, get_pip_path)
            
            # 创建pip配置文件，允许安装到目标目录
            pip_conf_path = os.path.join(temp_dir, "pip.ini")
            with open(pip_conf_path, 'w') as f:
                f.write("""[global]
                            target = 
                            break-system-packages = true
                        """)
            
            # 使用嵌入式Python安装pip
            subprocess.run([python_exe, get_pip_path, "--no-warn-script-location"], 
                         capture_output=True, text=True, check=True)
            
            logger.info(f"嵌入式Python下载并配置完成: {python_exe}")
            return python_exe
            
        except Exception as e:
            logger.error(f"下载嵌入式Python失败: {e}")
            return None
    
    def _install_dependency_offline(self, dependency_name, target_dir):
        """离线安装依赖库"""
        import tempfile
        import urllib.request
        import os
        
        # 尝试从预打包的wheel文件安装
        app_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        wheels_dir = os.path.join(app_dir, "wheels")
        
        if os.path.exists(wheels_dir):
            # 查找匹配的wheel文件
            for file in os.listdir(wheels_dir):
                if dependency_name.lower() in file.lower() and file.endswith(".whl"):
                    wheel_path = os.path.join(wheels_dir, file)
                    python_executable = self._get_python_executable()
                    if python_executable:
                        try:
                            subprocess.run([
                                python_executable, "-m", "pip", "install",
                                "--target", target_dir,
                                wheel_path
                            ], capture_output=True, text=True, check=True)
                            logger.info(f"离线安装依赖成功: {dependency_name}")
                            return True
                        except Exception as e:
                            logger.error(f"离线安装失败: {e}")
        
        return False
    def __init__(self, plugin_info, parent=None):
        super().__init__(parent)
        self.plugin_info = plugin_info
        
        # 主水平布局
        self.hBoxLayout = QHBoxLayout(self)
        self.hBoxLayout.setContentsMargins(10, 10, 10, 10)
        self.hBoxLayout.setSpacing(10)
        
        # 设置按钮
        self.settingsButton = PushButton("设置", self)
        self.settingsButton.setIcon(FIF.SETTING)
        self.settingsButton.clicked.connect(lambda: self.on_settings_clicked())
        
        # 启用按钮
        self.enableButton = ToggleButton("启用", self)
        self.enableButton.setChecked(plugin_info.get("enabled", False))  # 根据plugin.json中的enabled字段设置初始状态
        self.enableButton.clicked.connect(lambda: self.on_enable_clicked())
        
        # 查看说明按钮
        self.readmeButton = PushButton("查看说明", self)
        self.readmeButton.setIcon(FIF.DOCUMENT)
        self.readmeButton.clicked.connect(lambda: self.on_readme_clicked())
        
        # 删除按钮
        self.deleteButton = PushButton("删除", self)
        self.deleteButton.setIcon(FIF.DELETE)
        self.deleteButton.clicked.connect(lambda: self.on_delete_clicked())
        
        # 添加到布局
        self.hBoxLayout.addWidget(self.settingsButton)
        self.hBoxLayout.addWidget(self.enableButton)
        self.hBoxLayout.addWidget(self.readmeButton)
        self.hBoxLayout.addWidget(self.deleteButton)
        self.hBoxLayout.addStretch(1)
        
        # 设置固定高度
        self.setFixedHeight(50)
    
    def on_settings_clicked(self):
        """处理设置按钮点击事件"""
        # 获取插件入口文件路径
        entry_point = self.plugin_info.get("entry_point", "main.py")
        plugin_file_path = os.path.join(self.plugin_info["path"], entry_point)
        
        if not os.path.exists(plugin_file_path):
            logger.warning(f"插件 {self.plugin_info['name']} 的入口文件 {entry_point} 不存在")
            error_dialog = Dialog("文件不存在", f"插件 {self.plugin_info['name']} 的入口文件 {entry_point} 不存在", self)
            error_dialog.yesButton.setText("确定")
            error_dialog.cancelButton.hide()
            error_dialog.buttonLayout.insertStretch(1)
            error_dialog.exec()
            return
        
        logger.info(f"正在加载插件设置: {self.plugin_info['name']}")
        
        try:
            # 使用importlib动态导入插件
            spec = importlib.util.spec_from_file_location(f"plugin_{self.plugin_info['folder_name']}", plugin_file_path)
            if spec is None or spec.loader is None:
                raise ImportError(f"无法加载插件文件: {plugin_file_path}")
            
            plugin_module = importlib.util.module_from_spec(spec)
            
            # 添加插件目录到sys.path，以便插件可以导入自己的模块
            plugin_dir = self.plugin_info["path"]
            if plugin_dir not in sys.path:
                sys.path.insert(0, plugin_dir)
            
            # 添加插件专属site-packages目录到sys.path，以便插件可以使用安装的依赖
            plugin_site_packages = os.path.join(self.plugin_info["path"], "site-packages")
            if os.path.exists(plugin_site_packages) and plugin_site_packages not in sys.path:
                sys.path.insert(0, plugin_site_packages)
                logger.info(f"已添加插件专属site-packages到Python路径: {plugin_site_packages}")
            
            # 尝试加载模块
            try:
                spec.loader.exec_module(plugin_module)
                logger.info(f"成功加载插件模块: {self.plugin_info['name']}")
                
                # 检查插件是否有设置界面函数
                if hasattr(plugin_module, 'show_dialog'):
                    logger.info(f"调用插件主函数: {self.plugin_info['name']}")
                    plugin_module.show_dialog(self)
                else:
                    # 如果没有标准函数，显示提示
                    info_dialog = Dialog("插件信息", f"插件 {self.plugin_info['name']} 已成功加载，但没有提供标准的设置界面函数", self)
                    info_dialog.yesButton.setText("确定")
                    info_dialog.cancelButton.hide()
                    info_dialog.buttonLayout.insertStretch(1)
                    info_dialog.exec()
                    
            except ImportError as ie:
                # 处理导入错误，可能是缺少依赖库
                logger.error(f"插件 {self.plugin_info['name']} 导入失败: {ie}")
                
                # 尝试自动安装依赖
                dependencies = self.plugin_info.get("dependencies", [])
                if dependencies:
                    install_dialog = Dialog("安装依赖", f"插件 {self.plugin_info['name']} 缺少依赖库，是否自动安装？\n需要安装的库: {', '.join(dependencies)}", self)
                    install_dialog.yesButton.setText("安装")
                    install_dialog.cancelButton.setText("取消")
                    
                    if install_dialog.exec():
                        # 安装依赖
                        for dep in dependencies:
                            try:
                                logger.info(f"正在安装依赖: {dep}")
                                target_dir = os.path.join(self.plugin_info["path"], "site-packages")
                                os.makedirs(target_dir, exist_ok=True)
                                
                                # 首先尝试离线安装
                                if self._install_dependency_offline(dep, target_dir):
                                    logger.info(f"离线安装依赖成功: {dep}")
                                    continue
                                
                                # 离线安装失败，尝试在线安装
                                python_executable = self._get_python_executable()
                                if not python_executable:
                                    # 如果没有Python环境，提供替代方案
                                    error_dialog = Dialog("安装失败", f"无法安装依赖 {dep}。\n\n可能的解决方案：\n1. 检查网络连接\n2. 联系开发者获取包含依赖的插件版本\n3. 手动下载并放置依赖库到插件目录", self)
                                    error_dialog.yesButton.setText("确定")
                                    error_dialog.cancelButton.hide()
                                    error_dialog.buttonLayout.insertStretch(1)
                                    error_dialog.exec()
                                    return
                                
                                # 尝试在线安装依赖
                                try:
                                    result = subprocess.run([
                                        python_executable, "-m", "pip", "install", 
                                        "--target", target_dir,
                                        dep
                                    ], capture_output=True, text=True, check=True)
                                    logger.info(f"在线安装依赖成功: {dep}")
                                except subprocess.CalledProcessError as e:
                                    logger.error(f"在线安装依赖 {dep} 失败: {e}")
                                    # 提供详细的错误信息和解决方案
                                    error_msg = f"安装依赖 {dep} 失败\n\n错误信息: {e.stderr}\n\n解决方案：\n1. 检查网络连接\n2. 尝试使用管理员权限运行程序\n3. 联系开发者获取预打包版本"
                                    error_dialog = Dialog("安装失败", error_msg, self)
                                    error_dialog.yesButton.setText("确定")
                                    error_dialog.cancelButton.hide()
                                    error_dialog.buttonLayout.insertStretch(1)
                                    error_dialog.exec()
                                    return
                            except Exception as e:
                                logger.error(f"安装依赖 {dep} 失败: {e}")
                                # 提供详细的错误信息和解决方案
                                error_msg = f"安装依赖 {dep} 失败\n\n错误信息: {str(e)}\n\n解决方案：\n1. 检查网络连接\n2. 尝试使用管理员权限运行程序\n3. 联系开发者获取预打包版本"
                                error_dialog = Dialog("安装失败", error_msg, self)
                                error_dialog.yesButton.setText("确定")
                                error_dialog.cancelButton.hide()
                                error_dialog.buttonLayout.insertStretch(1)
                                error_dialog.exec()
                                return
                        
                        # 重新尝试加载插件
                        try:
                            # 将插件专属site-packages目录添加到sys.path
                            plugin_site_packages = os.path.join(self.plugin_info["path"], "site-packages")
                            if os.path.exists(plugin_site_packages) and plugin_site_packages not in sys.path:
                                sys.path.insert(0, plugin_site_packages)
                                logger.info(f"已添加插件专属site-packages到Python路径: {plugin_site_packages}")
                            
                            spec.loader.exec_module(plugin_module)
                            logger.info(f"依赖安装后成功加载插件: {self.plugin_info['name']}")
                            
                            if hasattr(plugin_module, 'show_dialog'):
                                plugin_module.show_dialog(self)
                            else:
                                info_dialog = Dialog("插件信息", f"插件 {self.plugin_info['name']} 已成功加载，但没有提供标准的设置界面函数", self)
                                info_dialog.yesButton.setText("确定")
                                info_dialog.cancelButton.hide()
                                info_dialog.buttonLayout.insertStretch(1)
                                info_dialog.exec()

                        except Exception as e:
                            logger.error(f"依赖安装后仍然无法加载插件: {e}")
                            error_dialog = Dialog("加载失败", f"依赖安装后仍然无法加载插件 {self.plugin_info['name']}: {str(e)}", self)
                            error_dialog.yesButton.setText("确定")
                            error_dialog.cancelButton.hide()
                            error_dialog.buttonLayout.insertStretch(1)
                            error_dialog.exec()

                    else:
                        # 用户取消安装
                        logger.info(f"用户取消安装插件依赖: {self.plugin_info['name']}")
                        cancel_dialog = Dialog("操作取消", f"已取消安装插件 {self.plugin_info['name']} 的依赖", self)
                        cancel_dialog.yesButton.setText("确定")
                        cancel_dialog.cancelButton.hide()
                        cancel_dialog.buttonLayout.insertStretch(1)
                        cancel_dialog.exec()
                else:
                    # 没有依赖信息，显示错误
                    error_dialog = Dialog("加载失败", f"无法加载插件 {self.plugin_info['name']}: {str(ie)}\n请检查插件是否缺少必要的依赖库", self)
                    error_dialog.yesButton.setText("确定")
                    error_dialog.cancelButton.hide()
                    error_dialog.buttonLayout.insertStretch(1)
                    error_dialog.exec()
                    
            except Exception as e:
                # 处理其他异常
                logger.error(f"插件 {self.plugin_info['name']} 执行失败: {e}")
                error_dialog = Dialog("执行失败", f"插件 {self.plugin_info['name']} 执行失败: {str(e)}", self)
                error_dialog.yesButton.setText("确定")
                error_dialog.cancelButton.hide()
                error_dialog.buttonLayout.insertStretch(1)
                error_dialog.exec()
                
        except Exception as e:
            # 处理模块加载失败
            logger.error(f"无法加载插件 {self.plugin_info['name']}: {e}")
            error_dialog = Dialog("加载失败", f"无法加载插件 {self.plugin_info['name']}: {str(e)}", self)
            error_dialog.yesButton.setText("确定")
            error_dialog.cancelButton.hide()
            error_dialog.buttonLayout.insertStretch(1)
            error_dialog.exec()
    
    def on_enable_clicked(self):
        """处理启用按钮点击事件"""
        is_enabled = self.enableButton.isChecked()
        status = "启用" if is_enabled else "禁用"
        logger.info(f"{status}插件: {self.plugin_info['name']}")
        
        # 获取plugin.json文件路径
        plugin_json_path = os.path.join(self.plugin_info["path"], "plugin.json")
        
        try:
            # 读取现有的plugin.json文件
            with open(plugin_json_path, 'r', encoding='utf-8') as f:
                plugin_config = json.load(f)
            
            # 更新enabled字段
            plugin_config["enabled"] = is_enabled
            
            # 写回plugin.json文件
            with open(plugin_json_path, 'w', encoding='utf-8') as f:
                json.dump(plugin_config, f, ensure_ascii=False, indent=2)
            
            logger.info(f"成功更新插件 {self.plugin_info['name']} 的启用状态为: {is_enabled}")
            
        except Exception as e:
            logger.error(f"更新插件 {self.plugin_info['name']} 启用状态失败: {e}")
            # 如果更新失败，恢复按钮状态
            self.enableButton.setChecked(not is_enabled)
            
            # 显示错误对话框
            error_dialog = Dialog("操作失败", f"更新插件启用状态失败: {str(e)}", self)
            error_dialog.yesButton.setText("确定")
            error_dialog.cancelButton.hide()
            error_dialog.buttonLayout.insertStretch(1)
            error_dialog.exec()
    
    def on_readme_clicked(self):
        """处理查看说明按钮点击事件"""
        readme_files = ['README.md', 'readme.md']
        readme_path = None
        
        for readme_file in readme_files:
            potential_path = os.path.join(self.plugin_info["path"], readme_file)
            if os.path.exists(potential_path):
                readme_path = potential_path
                break
        
        if readme_path:
            logger.info(f"查看插件说明: {self.plugin_info['name']}")
            # 准备插件信息用于ReadmeDialog
            dialog_plugin_info = self.plugin_info.copy()
            dialog_plugin_info['readme_path'] = readme_path
            
            # 创建自定义ReadmeDialog
            readme_dialog = ReadmeDialog(dialog_plugin_info, self)
            readme_dialog.exec()
            
        else:
            logger.warning(f"插件 {self.plugin_info['name']} 没有README文件")
            # 显示提示对话框
            no_readme_dialog = Dialog("提示", f"插件 {self.plugin_info['name']} 没有README文件", self)
            no_readme_dialog.yesButton.setText("确定")
            no_readme_dialog.cancelButton.hide()
            no_readme_dialog.buttonLayout.insertStretch(1)
            no_readme_dialog.exec()
    
    def on_delete_clicked(self):
        """处理删除按钮点击事件"""
        # 创建确认对话框
        delete_dialog = Dialog("确认删除插件", f"确定要删除插件 {self.plugin_info['name']} 吗？此操作将删除插件文件夹且无法恢复。", self)
        delete_dialog.yesButton.setText("删除")
        delete_dialog.cancelButton.setText("取消")
        if delete_dialog.exec():
                logger.info(f"删除插件: {self.plugin_info['name']}")
                try:
                    # 删除插件文件夹
                    shutil.rmtree(self.plugin_info['path'])
                    logger.info(f"成功删除插件文件夹: {self.plugin_info['path']}")
                    
                    # 禁用当前插件的所有按钮（仅影响当前插件按钮组）
                    self.settingsButton.setEnabled(False)
                    self.enableButton.setEnabled(False)
                    self.readmeButton.setEnabled(False)
                    self.deleteButton.setEnabled(False)
                    
                except Exception as e:
                    logger.error(f"删除插件文件夹失败: {e}")
                    error_dialog = Dialog("删除失败", f"删除插件 {self.plugin_info['name']} 失败: {str(e)}", self)
                    error_dialog.yesButton.setText("确定")
                    error_dialog.cancelButton.hide()
                    error_dialog.buttonLayout.insertStretch(1)
                    error_dialog.exec()


class PluginManagementPage(GroupHeaderCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("插件管理")
        self.setBorderRadius(8)
        self.settings_file = "app/Settings/plugin_settings.json"
        
        # 插件目录路径
        self.plugin_dir = "app/plugin"
        
        # 必需的插件配置字段
        self.required_fields = [
            "name", "version", "description", "author", 
            "entry_point", "min_app_version", "dependencies"
        ]
        
        # 初始化时加载插件
        self.load_plugins()
    
    def scan_plugins(self):
        """扫描插件目录，返回有效的插件列表"""
        plugins = []
        
        if not os.path.exists(self.plugin_dir):
            logger.warning(f"插件目录不存在: {self.plugin_dir}")
            return plugins
        
        for item in os.listdir(self.plugin_dir):
            item_path = os.path.join(self.plugin_dir, item)
            
            # 跳过文件，只处理文件夹
            if not os.path.isdir(item_path):
                continue
            
            # 检查是否有plugin.json文件
            plugin_json_path = os.path.join(item_path, "plugin.json")
            if not os.path.exists(plugin_json_path):
                continue
            
            try:
                # 读取plugin.json文件
                with open(plugin_json_path, 'r', encoding='utf-8') as f:
                    plugin_config = json.load(f)
                
                # 验证必需字段
                missing_fields = []
                for field in self.required_fields:
                    if field not in plugin_config:
                        missing_fields.append(field)
                
                if missing_fields:
                    logger.warning(f"插件 {item} 缺少必需字段: {missing_fields}")
                    continue
                
                # 添加插件信息
                plugin_info = {
                    "name": plugin_config["name"],
                    "version": plugin_config["version"],
                    "description": plugin_config["description"],
                    "author": plugin_config["author"],
                    "entry_point": plugin_config["entry_point"],
                    "min_app_version": plugin_config["min_app_version"],
                    "dependencies": plugin_config["dependencies"],
                    "path": item_path,
                    "folder_name": item,
                    "enabled": plugin_config.get("enabled", False)  # 如果没有enabled字段，默认为false
                }
                plugins.append(plugin_info)
                
            except Exception as e:
                logger.error(f"读取插件 {item} 配置文件失败: {e}")
                continue
        
        return plugins
    
    def get_plugin_icon(self, plugin_path):
        """获取插件图标文件路径"""
        # 支持的图标格式
        icon_formats = ['icon.png', 'icon.svg', 'icon.jpg']
        
        for icon_name in icon_formats:
            icon_path = os.path.join(plugin_path, icon_name)
            if os.path.exists(icon_path):
                return icon_path
        
        # 如果没有找到图标文件，返回None
        return None
    
    def create_plugin_button_group(self, plugin_info):
        """创建插件按钮组"""
        # 创建按钮组
        button_group = PluginButtonGroup(plugin_info, self)
        
        return button_group
    
    def load_plugins(self):
        """加载插件列表"""
        # 扫描插件
        plugins = self.scan_plugins()

        # 去重插件列表（基于插件路径和名称双重保险）
        unique_plugins = {}
        for plugin in plugins:
            # 使用路径和名称组合作为键，确保唯一性
            key = f"{plugin['path']}_{plugin['name']}"
            unique_plugins[key] = plugin
        plugins = list(unique_plugins.values())

        if not plugins:
            # 显示无插件提示组
            no_plugin_label = BodyLabel("暂无可用插件", self)
            no_plugin_label.setAlignment(Qt.AlignCenter)
            self.addGroup(get_theme_icon("ic_fluent_extensions_20_filled"), "暂无可用插件", "暂无可用插件", no_plugin_label)
        else:
            # 为每个插件创建按钮组
            for plugin in plugins:
                button_group = self.create_plugin_button_group(plugin)
                # 将每个按钮组作为独立的组添加到默认布局中
                get_plugin_icon = self.get_plugin_icon(plugin["path"])
                if get_plugin_icon:
                    icon = QIcon(get_plugin_icon)
                else:
                    icon = get_theme_icon("ic_fluent_extensions_20_filled")

                self.addGroup(icon, plugin["name"], f"版本: {plugin['version']}_作者: {plugin['author']}_描述: {plugin['description']}", button_group)

        logger.info(f"加载完成，共找到 {len(plugins)} 个插件")

