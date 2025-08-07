import json
import zipfile
import importlib.util
import shutil
import os
from pathlib import Path
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from qfluentwidgets import *
from loguru import logger

from app.common.config import get_theme_icon, load_custom_font
from app.common.deps_loader import load_plugin_dependencies

def get_plugin_icon_path(icon_path):
    """获取相对于程序根目录的插件图标路径
    
    Args:
        icon_path (str): 插件图标的相对路径，格式为 'plugins/插件名/assets/icon.png' 或 'plugins/插件名/icon.png'
    
    Returns:
        str: 相对于程序根目录的完整图标路径，如果找不到则返回None
    """
    if not icon_path:
        return None
    
    # 如果已经是绝对路径，直接返回
    if os.path.isabs(icon_path):
        return icon_path if os.path.exists(icon_path) else None
    
    # 获取程序根目录
    app_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # 构建相对于程序根目录的完整路径
    full_path = os.path.join(app_root, icon_path)
    
    # 如果文件存在，返回完整路径
    if os.path.exists(full_path):
        return full_path
    
    # 如果文件不存在，尝试其他可能的路径
    
    # 尝试相对于当前工作目录的路径
    if os.path.exists(icon_path):
        return os.path.abspath(icon_path)
    
    # 如果路径以plugins开头，尝试在插件目录中查找
    if icon_path.startswith('plugins/') or icon_path.startswith('plugins\\'):
        # 解析插件名和图标文件名
        path_parts = icon_path.replace('\\', '/').split('/')
        if len(path_parts) >= 3:
            plugin_name = path_parts[1]
            icon_filename = path_parts[-1]
            
            # 构建插件目录路径
            plugin_dir = os.path.join(app_root, 'plugins', plugin_name)
            
            # 支持的图标文件格式
            icon_extensions = ['.png', '.ico', '.svg']
            
            # 1. 优先在assets文件夹中查找
            assets_dir = os.path.join(plugin_dir, 'assets')
            if os.path.exists(assets_dir):
                for ext in icon_extensions:
                    # 检查是否已有扩展名
                    if icon_filename.lower().endswith(ext):
                        icon_file = icon_filename
                    else:
                        # 添加扩展名
                        name_without_ext = os.path.splitext(icon_filename)[0]
                        icon_file = f"{name_without_ext}{ext}"
                    
                    icon_file_path = os.path.join(assets_dir, icon_file)
                    if os.path.exists(icon_file_path):
                        return icon_file_path
            
            # 2. 如果assets中没有找到，在插件根目录中查找（向后兼容）
            for ext in icon_extensions:
                # 检查是否已有扩展名
                if icon_filename.lower().endswith(ext):
                    icon_file = icon_filename
                else:
                    # 添加扩展名
                    name_without_ext = os.path.splitext(icon_filename)[0]
                    icon_file = f"{name_without_ext}{ext}"
                
                icon_file_path = os.path.join(plugin_dir, icon_file)
                if os.path.exists(icon_file_path):
                    return icon_file_path
    
    # 如果所有尝试都失败，返回None
    return None

class PluginManagerThread(QThread):
    """插件管理线程，处理文件IO操作"""
    plugin_loaded = pyqtSignal(list)  # 插件列表加载完成信号
    plugin_installed = pyqtSignal(dict)  # 插件安装完成信号
    plugin_uninstalled = pyqtSignal(str)  # 插件卸载完成信号
    error_occurred = pyqtSignal(str)  # 错误信号
    plugin_enabled = pyqtSignal(str)  # 插件启用完成信号
    plugin_disabled = pyqtSignal(str)  # 插件禁用完成信号
    
    def __init__(self):
        super().__init__()
        self.plugins_dir = './app/plugins'
        self.plugin_states = {}  # 存储插件启用状态
        self.plugin_autostart = {}  # 存储插件自启状态
        self.plugin_threads = {}  # 存储插件后台线程
        self.states_file = './app/plugins/plugin_states.json'  # 插件状态文件
        self._load_plugin_states()  # 加载插件状态
        
    def load_plugins(self):
        """加载插件列表"""
        try:
            plugins = []
            
            # 检查插件目录是否存在
            if not os.path.exists(self.plugins_dir):
                os.makedirs(self.plugins_dir)
                self.plugin_loaded.emit(plugins)
                return
            
            # 获取插件目录下的所有子目录
            for plugin_name in os.listdir(self.plugins_dir):
                plugin_path = os.path.join(self.plugins_dir, plugin_name)
                if os.path.isdir(plugin_path):
                    # 检查插件是否有main.py
                    main_file = os.path.join(plugin_path, 'main.py')
                    if os.path.exists(main_file):
                        # 尝试读取插件信息
                        plugin_info = self._read_plugin_info(plugin_name, plugin_path)
                        plugins.append(plugin_info)
            
            self.plugin_loaded.emit(plugins)
        except Exception as e:
            self.error_occurred.emit(f"加载插件失败: {str(e)}")
    
    def install_plugin(self, file_path):
        """安装插件"""
        try:
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                # 获取 zip 中的顶层目录
                top_level_dirs = set()
                for name in zip_ref.namelist():
                    if '/' in name:
                        top_level_dir = name.split('/')[0]
                        top_level_dirs.add(top_level_dir)
                    elif '\\' in name:
                        top_level_dir = name.split('\\')[0]
                        top_level_dirs.add(top_level_dir)
                
                # 如果只有一个顶层目录，使用它作为插件名称
                if len(top_level_dirs) == 1:
                    plugin_name = list(top_level_dirs)[0]
                    plugin_path = os.path.join(self.plugins_dir, plugin_name)
                    
                    # 确保目标目录不存在
                    if os.path.exists(plugin_path):
                        self.error_occurred.emit(f"插件 {plugin_name} 已存在")
                        return
                    
                    # 创建目标目录
                    os.makedirs(plugin_path)
                    
                    # 解压文件
                    for name in zip_ref.namelist():
                        # 跳过顶层目录
                        if name.startswith(plugin_name + '/') or name.startswith(plugin_name + '\\'):
                            # 获取相对路径
                            rel_path = name[len(plugin_name) + 1:]
                            # 创建目标文件路径
                            target_path = os.path.join(plugin_path, rel_path)
                            # 确保目标目录存在
                            os.makedirs(os.path.dirname(target_path), exist_ok=True)
                            # 写入文件
                            with open(target_path, 'wb') as f:
                                f.write(zip_ref.read(name))
                    
                    # 读取插件信息
                    plugin_info = self._read_plugin_info(plugin_name, plugin_path)
                    self.plugin_installed.emit(plugin_info)
                else:
                    self.error_occurred.emit("插件格式不正确: 必须包含一个顶层目录")
        except Exception as e:
            self.error_occurred.emit(f"安装插件失败: {str(e)}")
    
    def uninstall_plugin(self, plugin_name):
        """卸载插件"""
        try:
            plugin_path = os.path.join(self.plugins_dir, plugin_name)
            if os.path.exists(plugin_path):
                shutil.rmtree(plugin_path)
                self.plugin_uninstalled.emit(plugin_name)
            else:
                self.error_occurred.emit(f"插件 {plugin_name} 不存在")
        except Exception as e:
            self.error_occurred.emit(f"卸载插件失败: {str(e)}")
    
    def _read_plugin_info(self, plugin_name, plugin_path):
        """读取插件信息"""
        # 默认插件信息
        plugin_info = {
            'name': plugin_name,
            'version': '1.0.0',
            'author': 'Unknown',
            'description': '无描述',
            'icon': None,
            'has_page': False,
            'has_readme': False
        }
        
        # 尝试读取plugin.json
        config_file = os.path.join(plugin_path, 'plugin.json')
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    plugin_info.update(config)
            except:
                pass
        
        # 检查是否有page.py
        page_file = os.path.join(plugin_path, 'page.py')
        plugin_info['has_page'] = os.path.exists(page_file)
        
        # 检查是否有readme文件
        readme_files = ['README.md', 'readme.md', 'README.txt', 'readme.txt', 'README', 'readme']
        for readme_file in readme_files:
            readme_path = os.path.join(plugin_path, readme_file)
            if os.path.exists(readme_path):
                plugin_info['has_readme'] = True
                plugin_info['readme_path'] = readme_path
                break
        
        # 检查图标文件 - 在插件目录的assets文件夹中查找
        assets_dir = os.path.join(plugin_path, 'assets')
        icon_files = ['icon.png', 'icon.ico', 'icon.svg']
        
        # 首先在assets文件夹中查找图标
        for icon_file in icon_files:
            icon_path = os.path.join(assets_dir, icon_file)
            if os.path.exists(icon_path):
                # 将图标路径转换为相对于程序根目录的路径
                app_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                relative_path = os.path.relpath(icon_path, app_root)
                plugin_info['icon'] = relative_path
                break
        else:
            # 如果assets文件夹中没有找到图标，则在插件根目录中查找（保持向后兼容）
            for icon_file in icon_files:
                icon_path = os.path.join(plugin_path, icon_file)
                if os.path.exists(icon_path):
                    # 将图标路径转换为相对于程序根目录的路径
                    app_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                    relative_path = os.path.relpath(icon_path, app_root)
                    plugin_info['icon'] = relative_path
                    break
        
        # 添加插件启用状态
        plugin_info['enabled'] = self.is_plugin_enabled(plugin_name)
        # 添加插件自启状态
        plugin_info['autostart'] = self.is_plugin_autostart(plugin_name)
        
        return plugin_info
    
    def _load_plugin_states(self):
        """加载插件状态"""
        try:
            if os.path.exists(self.states_file):
                with open(self.states_file, 'r', encoding='utf-8') as f:
                    states_data = json.load(f)
                    self.plugin_states = states_data.get('enabled', {})
                    self.plugin_autostart = states_data.get('autostart', {})
        except Exception as e:
            logger.warning(f"加载插件状态失败: {str(e)}")
            self.plugin_states = {}
            self.plugin_autostart = {}
    
    def _save_plugin_states(self):
        """保存插件状态"""
        try:
            os.makedirs(os.path.dirname(self.states_file), exist_ok=True)
            states_data = {
                'enabled': self.plugin_states,
                'autostart': self.plugin_autostart
            }
            with open(self.states_file, 'w', encoding='utf-8') as f:
                json.dump(states_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存插件状态失败: {str(e)}")
    
    def enable_plugin(self, plugin_name):
        """启用插件"""
        try:
            # 如果插件已启用，直接返回
            if self.plugin_states.get(plugin_name, False):
                return
            
            # 加载插件依赖
            plugin_path = os.path.join(self.plugins_dir, plugin_name)
            if not load_plugin_dependencies(plugin_path, plugin_name):
                self.error_occurred.emit(f"插件 {plugin_name} 依赖加载失败，无法启用")
                return
            
            # 创建后台线程
            thread = PluginBackgroundThread(plugin_name, self.plugins_dir)
            self.plugin_threads[plugin_name] = thread
            thread.start()
            
            # 更新状态
            self.plugin_states[plugin_name] = True
            self._save_plugin_states()
            
            # 发送信号
            self.plugin_enabled.emit(plugin_name)
        except Exception as e:
            self.error_occurred.emit(f"启用插件失败: {str(e)}")
    
    def disable_plugin(self, plugin_name):
        """禁用插件"""
        try:
            # 如果插件已禁用，直接返回
            if not self.plugin_states.get(plugin_name, False):
                return
            
            # 停止后台线程
            if plugin_name in self.plugin_threads:
                thread = self.plugin_threads[plugin_name]
                thread.stop()
                
                # 等待线程完全停止，设置超时时间
                if thread.wait(2000):  # 等待最多2秒
                    logger.info(f"插件 {plugin_name} 后台线程已正常停止")
                else:
                    logger.warning(f"插件 {plugin_name} 后台线程停止超时，强制终止")
                    thread.terminate()  # 强制终止线程
                    thread.wait(500)   # 再等待0.5秒
                
                del self.plugin_threads[plugin_name]
            
            # 更新状态
            self.plugin_states[plugin_name] = False
            self._save_plugin_states()
            
            # 发送信号
            self.plugin_disabled.emit(plugin_name)
        except Exception as e:
            self.error_occurred.emit(f"禁用插件失败: {str(e)}")
    
    def is_plugin_enabled(self, plugin_name):
        """检查插件是否启用"""
        return self.plugin_states.get(plugin_name, False)
    
    def set_plugin_autostart(self, plugin_name, autostart=True):
        """设置插件自启状态"""
        try:
            self.plugin_autostart[plugin_name] = autostart
            self._save_plugin_states()
        except Exception as e:
            logger.error(f"设置插件自启状态失败: {str(e)}")
    
    def is_plugin_autostart(self, plugin_name):
        """检查插件是否设置自启"""
        return self.plugin_autostart.get(plugin_name, False)
    
    def get_autostart_plugins(self):
        """获取所有设置自启的插件列表"""
        return [name for name, autostart in self.plugin_autostart.items() if autostart]


class PluginBackgroundThread(QThread):
    """插件后台运行线程"""
    def __init__(self, plugin_name, plugins_dir):
        super().__init__()
        self.plugin_name = plugin_name
        self.plugins_dir = plugins_dir
        self.plugin_path = os.path.join(plugins_dir, plugin_name)
        self.running = False
        self.plugin_instance = None
    
    def run(self):
        """运行插件后台任务"""
        self.running = True
        try:
            # 确保插件依赖已加载
            from app.common.deps_loader import get_dependency_loader
            import sys
            
            # 获取应用程序根目录
            app_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            loader = get_dependency_loader(app_root)
            
            # 加载插件依赖
            if not loader.load_plugin_dependencies(self.plugin_path, self.plugin_name):
                logger.error(f"插件 {self.plugin_name} 依赖加载失败")
                return
            
            # 动态导入插件主模块
            main_file = os.path.join(self.plugin_path, 'main.py')
            if not os.path.exists(main_file):
                logger.warning(f"插件 {self.plugin_name} 没有main.py文件")
                return
            
            spec = importlib.util.spec_from_file_location(f"{self.plugin_name}_main", main_file)
            if spec is None or spec.loader is None:
                logger.error(f"无法加载插件 {self.plugin_name} 的主模块")
                return
            
            main_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(main_module)
            
            # 查找插件后台类
            plugin_class = None
            for attr_name in dir(main_module):
                attr = getattr(main_module, attr_name)
                if (isinstance(attr, type) and 
                    attr_name in ['PluginBackground', 'PluginWorker', 'BackgroundTask'] and
                    (hasattr(attr, 'run') or hasattr(attr, 'start') or hasattr(attr, 'update'))):
                    plugin_class = attr
                    break
            
            if plugin_class is None:
                logger.warning(f"插件 {self.plugin_name} 没有找到后台运行类")
                return
            
            # 创建插件实例
            self.plugin_instance = plugin_class()
            
            # 后台运行成功记录日志
            logger.info(f"插件 {self.plugin_name} 后台运行成功")
            
            # 运行插件
            while self.running:
                try:
                    # 优先调用run方法
                    if hasattr(self.plugin_instance, 'run'):
                        self.plugin_instance.run()
                    elif hasattr(self.plugin_instance, 'start'):
                        self.plugin_instance.start()
                    elif hasattr(self.plugin_instance, 'update'):
                        self.plugin_instance.update()
                    
                    # 休眠一段时间，避免CPU占用过高
                    self.msleep(100)  # 100ms
                except Exception as e:
                    logger.error(f"插件 {self.plugin_name} 运行出错: {str(e)}")
                    if hasattr(self.plugin_instance, 'on_error'):
                        try:
                            self.plugin_instance.on_error(e)
                        except:
                            pass
                    break
        
        except Exception as e:
            logger.error(f"插件 {self.plugin_name} 后台线程启动失败: {str(e)}")
        finally:
            self.running = False
    
    def stop(self):
        """停止插件后台任务"""
        self.running = False
        if self.plugin_instance:
            try:
                # 调用插件的停止方法
                if hasattr(self.plugin_instance, 'stop'):
                    self.plugin_instance.stop()
                elif hasattr(self.plugin_instance, 'cleanup'):
                    self.plugin_instance.cleanup()
                elif hasattr(self.plugin_instance, 'destroy'):
                    self.plugin_instance.destroy()
            except Exception as e:
                logger.error(f"停止插件 {self.plugin_name} 时出错: {str(e)}")
        
        # 等待线程完全停止
        if self.isRunning():
            self.quit()
            self.wait(1000)  # 等待最多1秒


class PluginDialog(QDialog):
    """插件管理对话框"""
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 设置插件目录
        self.plugins_dir = './app/plugins'
        
        # 🌟 星穹铁道白露：设置无边框窗口样式并解决屏幕设置冲突~ 
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self.setWindowTitle('插件管理')
        self.setMinimumSize(800, 400)
        self.setSizeGripEnabled(True) #启用右下角拖动柄
        
        self.update_theme_style()
        qconfig.themeChanged.connect(self.update_theme_style)
        
        self.dragging = False
        self.drag_position = None

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
        self.title_label = QLabel("插件管理")
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
        
        # 主布局
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        # 添加自定义标题栏
        self.layout.addWidget(self.title_bar)
        
        # 创建内容区域
        self.content_area = QWidget()
        self.content_layout = QVBoxLayout(self.content_area)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(self.content_area)
        
        # 初始化插件管理器
        self.plugin_manager_thread = PluginManagerThread()
        self.plugin_manager_thread.plugin_loaded.connect(self.on_plugins_loaded)
        self.plugin_manager_thread.plugin_installed.connect(self.on_plugin_installed)
        self.plugin_manager_thread.plugin_uninstalled.connect(self.on_plugin_uninstalled)
        self.plugin_manager_thread.error_occurred.connect(self.on_plugin_error)
        self.plugin_manager_thread.plugin_enabled.connect(self.on_plugin_enabled)
        self.plugin_manager_thread.plugin_disabled.connect(self.on_plugin_disabled)
        
        self.plugin_cards = []

        # 启动自启插件
        self.start_autostart_plugins()
        
        # 初始化插件管理界面
        self.init_plugins_ui()
    
    def init_plugins_ui(self):
        """初始化插件管理界面"""
        # 清空内容区域
        self.clear_content_area()
        
        # 创建垂直滚动区域
        scroll_area = ScrollArea()
        scroll_area.setWidgetResizable(True)
        
        # 创建内容容器
        content_widget = QWidget()
        self.plugins_layout = QVBoxLayout(content_widget)
        self.plugins_layout.setContentsMargins(10, 10, 10, 10)
        self.plugins_layout.setSpacing(10)
        
        scroll_area.setWidget(content_widget)
        self.content_layout.addWidget(scroll_area)
        
        # 添加顶部控制区域
        top_control_layout = QHBoxLayout()
        
        top_control_layout.addStretch()
        
        # 添加安装按钮
        install_button = PrimaryPushButton('安装插件')
        install_button.clicked.connect(self.install_plugin)
        top_control_layout.addWidget(install_button)
        
        self.plugins_layout.addLayout(top_control_layout)
        
        # 添加插件卡片容器
        self.plugin_cards_container = QWidget()
        self.plugin_cards_layout = QVBoxLayout(self.plugin_cards_container)
        self.plugin_cards_layout.setContentsMargins(0, 0, 0, 0)
        self.plugin_cards_layout.setSpacing(10)
        self.plugins_layout.addWidget(self.plugin_cards_container)
        
        # 加载插件
        if not self.plugin_manager_thread.isRunning():
            self.plugin_manager_thread.start()
        self.plugin_manager_thread.load_plugins()
    
    def clear_content_area(self):
        """清空内容区域"""
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
    
    def create_plugin_card(self, plugin_info):
        """创建插件卡片"""
        card = SimpleCardWidget()
        # 移除固定高度，让卡片自适应内容
        
        # 卡片主布局
        card_layout = QHBoxLayout(card)
        card_layout.setContentsMargins(15, 15, 15, 15)
        
        # 插件图标
        icon_widget = IconWidget()
        if plugin_info.get('icon'):
            # 使用辅助函数获取正确的图标路径
            icon_path = get_plugin_icon_path(plugin_info['icon'])
            if icon_path and os.path.exists(icon_path):
                icon = QIcon(icon_path)
                icon_widget.setIcon(icon)
            else:
                default_icon = get_theme_icon('plugin')
                icon_widget.setIcon(default_icon)
        else:
            default_icon = get_theme_icon('plugin')
            icon_widget.setIcon(default_icon)
        icon_widget.setFixedSize(48, 48)
        card_layout.addWidget(icon_widget)
        
        # 插件信息区域
        info_layout = QVBoxLayout()
        info_layout.setSpacing(5)
        
        # 名称 + 版本 + 作者
        name_label = BodyLabel(f"{plugin_info['name']} v{plugin_info['version']}")
        name_label.setFont(QFont(load_custom_font(), 12, QFont.Bold))
        info_layout.addWidget(name_label)
        
        author_label = BodyLabel(f"作者: {plugin_info['author']}")
        author_label.setFont(QFont(load_custom_font(), 10))
        info_layout.addWidget(author_label)
        
        # 描述
        desc_label = CaptionLabel(plugin_info['description'])
        desc_label.setFont(QFont(load_custom_font(), 8))
        desc_label.setWordWrap(True)
        # 设置描述标签的最大宽度，避免过长文本导致卡片过宽
        desc_label.setMaximumWidth(400)
        info_layout.addWidget(desc_label)
        
        # 按钮区域 - 水平布局
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        button_layout.setContentsMargins(0, 10, 0, 0)
        
        info_layout.addLayout(button_layout)
        info_layout.addStretch()
        card_layout.addLayout(info_layout, stretch=1)
        
        # 打开页面按钮
        open_btn = PrimaryPushButton('打开页面')
        open_btn.setFixedWidth(120)
        open_btn.setFont(QFont(load_custom_font(), 12))
        open_btn.setEnabled(plugin_info.get('has_page', False) and plugin_info.get('enabled', False))
        open_btn.clicked.connect(lambda: self.open_plugin_page(plugin_info['name']))
        button_layout.addWidget(open_btn)
        
        # 启用/禁用开关
        toggle_btn = ToggleButton()
        toggle_btn.setFixedWidth(120)
        toggle_btn.setFont(QFont(load_custom_font(), 12))
        toggle_btn.setChecked(plugin_info.get('enabled', False))
        toggle_btn.setText('启用' if not plugin_info.get('enabled', False) else '禁用')
        toggle_btn.toggled.connect(lambda checked: self.toggle_plugin(plugin_info['name'], checked))
        button_layout.addWidget(toggle_btn)
        
        # 自启按钮
        autostart_btn = ToggleButton()
        autostart_btn.setFixedWidth(120)
        autostart_btn.setFont(QFont(load_custom_font(), 12))
        autostart_btn.setChecked(plugin_info.get('autostart', False))
        autostart_btn.setEnabled(plugin_info.get('enabled', False))
        autostart_btn.setText('开机自启')
        autostart_btn.toggled.connect(lambda checked: self.toggle_autostart(plugin_info['name'], checked))
        button_layout.addWidget(autostart_btn)
        
        # 打开readme按钮
        readme_btn = PushButton('查看说明')
        readme_btn.setFixedWidth(120)
        readme_btn.setFont(QFont(load_custom_font(), 12))
        readme_btn.setEnabled(plugin_info.get('has_readme', False))
        readme_btn.clicked.connect(lambda: self.open_plugin_readme(plugin_info))
        button_layout.addWidget(readme_btn)
        
        # 删除按钮
        delete_btn = PushButton('删除')
        delete_btn.setFixedWidth(120)
        delete_btn.setFont(QFont(load_custom_font(), 12))
        delete_btn.clicked.connect(lambda: self.delete_plugin(plugin_info['name']))
        button_layout.addWidget(delete_btn)
        
        # 存储插件信息
        card.plugin_info = plugin_info
        
        # 更新主题样式
        self.update_plugin_card_theme_style(card)
        
        # 设置卡片大小策略为自适应内容
        card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        
        return card
    
    def update_plugin_card_theme_style(self, card):
        """更新插件卡片主题样式"""
        if qconfig.theme == Theme.AUTO:
            # 获取系统当前主题
            lightness = QApplication.palette().color(QPalette.Window).lightness()
            is_dark = lightness <= 127
        else:
            is_dark = qconfig.theme == Theme.DARK
        
        # 🌟 星穹铁道白露：插件卡片主题样式更新 ~ 
        if is_dark:
            card.setStyleSheet('''
                SimpleCardWidget {
                    background: #1E1E1E;
                    border: 1px solid #333333;
                    border-radius: 8px;
                }
                SimpleCardWidget:hover {
                    background: #252525;
                    border: 1px solid #444444;
                }
            ''')
        else:
            card.setStyleSheet('''
                SimpleCardWidget {
                    background: #FFFFFF;
                    border: 1px solid #E0E0E0;
                    border-radius: 8px;
                }
                SimpleCardWidget:hover {
                    background: #F8F9FA;
                    border: 1px solid #D0D0D0;
                }
            ''')
    
    def install_plugin(self):
        """安装插件"""
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        file_dialog.setNameFilter("插件文件 (*.zip)")
        
        if file_dialog.exec_():
            file_path = file_dialog.selectedFiles()[0]
            if file_path:
                self.plugin_manager_thread.install_plugin(file_path)
    
    def delete_plugin(self, plugin_name):
        """删除插件"""
        # 确认对话框
        dialog = MessageBox(
            '确认删除',
            f'确定要删除插件 {plugin_name} 吗？此操作不可撤销。',
            self
        )

        dialog.yesButton.setText("确定")
        dialog.cancelButton.setText("取消")
        
        if dialog.exec_():
            self.plugin_manager_thread.uninstall_plugin(plugin_name)
    
    def open_plugin_page(self, plugin_name):
        """打开插件页面"""
        try:
            # 检查插件是否已启用
            if not self.plugin_manager_thread.is_plugin_enabled(plugin_name):
                InfoBar.warning(
                    title='警告',
                    content=f'插件 {plugin_name} 未启用，请先启用插件',
                    duration=2000,
                    parent=self
                )
                return
            
            # 构建插件路径
            plugin_path = os.path.join(self.plugins_dir, plugin_name)
            page_file = os.path.join(plugin_path, 'page.py')
            
            # 检查插件页面文件是否存在
            if not os.path.exists(page_file):
                InfoBar.warning(
                    title='警告',
                    content=f'插件 {plugin_name} 没有页面文件',
                    duration=2000,
                    parent=self
                )
                return
            
            # 动态导入插件页面模块
            spec = importlib.util.spec_from_file_location(f"{plugin_name}_page", page_file)
            if spec is None or spec.loader is None:
                InfoBar.error(
                    title='错误',
                    content=f'无法加载插件 {plugin_name} 的页面模块',
                    duration=3000,
                    parent=self
                )
                return
            
            page_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(page_module)
            
            # 检查插件页面类是否存在
            if not hasattr(page_module, 'PluginPage'):
                InfoBar.error(
                    title='错误',
                    content=f'插件 {plugin_name} 的页面文件中缺少 PluginPage 类',
                    duration=3000,
                    parent=self
                )
                return
            
            # 创建插件页面实例
            PluginPageClass = getattr(page_module, 'PluginPage')
            plugin_page = PluginPageClass(None)
            
            # 设置插件页面属性
            plugin_page.setWindowTitle(f'{plugin_name} 插件页面')
            plugin_page.setMinimumSize(600, 400)
            # 设置窗口标志，确保作为独立窗口显示
            plugin_page.setWindowFlags(Qt.Window | Qt.WindowCloseButtonHint | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint)
            
            # 显示插件页面
            plugin_page.show()
            
            InfoBar.success(
                title='成功',
                content=f'已打开插件 {plugin_name} 的页面',
                duration=2000,
                parent=self
            )
            
        except Exception as e:
            logger.error(f'打开插件页面失败: {str(e)}')
            InfoBar.error(
                title='错误',
                content=f'打开插件页面失败: {str(e)}',
                duration=3000,
                parent=self
            )
    
    def open_plugin_readme(self, plugin_info):
        """打开插件readme文件"""
        if plugin_info.get('has_readme', False) and plugin_info.get('readme_path'):
            try:
                # 创建readme显示对话框
                readme_dialog = ReadmeDialog(plugin_info, self)
                readme_dialog.show()
                
                InfoBar.success(
                    title='打开说明',
                    content=f'已打开 {plugin_info["name"]} 的说明文件',
                    duration=2000,
                    parent=self
                )
            except Exception as e:
                InfoBar.error(
                    title='错误',
                    content=f'无法打开说明文件: {str(e)}',
                    duration=3000,
                    parent=self
                )
        else:
            InfoBar.warning(
                title='警告',
                content=f'插件 {plugin_info["name"]} 没有说明文件',
                duration=2000,
                parent=self
            )
    
    def on_plugins_loaded(self, plugins):
        """插件加载完成"""
        # 清空现有卡片
        while self.plugin_cards_layout.count():
            item = self.plugin_cards_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        
        self.plugin_cards.clear()
        
        # 创建插件卡片
        for plugin_info in plugins:
            card = self.create_plugin_card(plugin_info)
            self.plugin_cards.append(card)
            self.plugin_cards_layout.addWidget(card)
            card.show()  # 确保卡片可见
        
        if not plugins:
            # 显示无插件提示
            no_plugin_label = BodyLabel('暂无插件')
            no_plugin_label.setAlignment(Qt.AlignCenter)
            no_plugin_label.setFont(QFont(load_custom_font(), 12))
            self.plugin_cards_layout.addWidget(no_plugin_label)
        
        # 强制更新布局
        self.plugin_cards_container.update()
        self.plugin_cards_container.adjustSize()
    
    def on_plugin_installed(self, plugin_info):
        """插件安装完成"""
        InfoBar.success(
            title='安装成功',
            content=f'插件 {plugin_info["name"]} 安装成功',
            duration=2000,
            parent=self
        )
        
        # 重新加载插件列表
        self.plugin_manager_thread.load_plugins()
    
    def on_plugin_uninstalled(self, plugin_name):
        """插件卸载完成"""
        InfoBar.success(
            title='卸载成功',
            content=f'插件 {plugin_name} 卸载成功',
            duration=2000,
            parent=self
        )
        
        # 重新加载插件列表
        self.plugin_manager_thread.load_plugins()
    
    def on_plugin_error(self, error_message):
        """插件操作错误"""
        InfoBar.error(
            title='错误',
            content=error_message,
            duration=3000,
            parent=self
        )
    
    def toggle_plugin(self, plugin_name, enabled):
        """切换插件启用/禁用状态"""
        if enabled:
            self.plugin_manager_thread.enable_plugin(plugin_name)
        else:
            self.plugin_manager_thread.disable_plugin(plugin_name)
    
    def on_plugin_enabled(self, plugin_name):
        """插件启用成功处理"""
        InfoBar.success(
            title='启用成功',
            content=f'插件 {plugin_name} 已启用',
            duration=2000,
            parent=self
        )
        # 重新加载插件列表以更新状态
        self.plugin_manager_thread.load_plugins()
    
    def on_plugin_disabled(self, plugin_name):
        """插件禁用成功处理"""
        InfoBar.success(
            title='禁用成功',
            content=f'插件 {plugin_name} 已禁用',
            duration=2000,
            parent=self
        )
        # 重新加载插件列表以更新状态
        self.plugin_manager_thread.load_plugins()
    
    def toggle_autostart(self, plugin_name, autostart):
        """切换插件自启状态"""
        # 检查插件是否已启用
        if not self.plugin_manager_thread.is_plugin_enabled(plugin_name):
            InfoBar.warning(
                title='警告',
                content=f'插件 {plugin_name} 未启用，无法设置开机自启',
                duration=2000,
                parent=self
            )
            # 重新加载插件列表以恢复按钮状态
            self.plugin_manager_thread.load_plugins()
            return
        
        self.plugin_manager_thread.set_plugin_autostart(plugin_name, autostart)
        
        if autostart:
            InfoBar.success(
                title='设置成功',
                content=f'插件 {plugin_name} 已设置开机自启',
                duration=2000,
                parent=self
            )
        else:
            InfoBar.success(
                title='取消成功',
                content=f'插件 {plugin_name} 已取消开机自启',
                duration=2000,
                parent=self
            )
        
        # 重新加载插件列表以更新状态
        self.plugin_manager_thread.load_plugins()
    
    def start_autostart_plugins(self):
        """启动所有设置自启的插件"""
        autostart_plugins = self.plugin_manager_thread.get_autostart_plugins()
        for plugin_name in autostart_plugins:
            if not self.plugin_manager_thread.is_plugin_enabled(plugin_name):
                try:
                    self.plugin_manager_thread.enable_plugin(plugin_name)
                    logger.info(f"自动启动插件 {plugin_name}")
                except Exception as e:
                    logger.error(f"自动启动插件 {plugin_name} 失败: {str(e)}")
            # 确保自启状态已设置
            try:
                self.plugin_manager_thread.set_plugin_autostart(plugin_name, True)
                logger.info(f"已设置插件 {plugin_name} 为开机自启")
            except Exception as e:
                logger.error(f"设置插件 {plugin_name} 自启状态失败: {str(e)}")
    
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
        """根据当前主题更新样式"""
        if qconfig.theme == Theme.AUTO:
            # 获取系统当前主题
            lightness = QApplication.palette().color(QPalette.Window).lightness()
            is_dark = lightness <= 127
        else:
            is_dark = qconfig.theme == Theme.DARK
        
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
    
    def closeEvent(self, event):
        """关闭事件处理，确保所有线程都被正确停止"""
        self.cleanup_threads()
        event.accept()
    
    def __del__(self):
        """析构函数，确保所有线程都被正确停止"""
        self.cleanup_threads()
    
    def cleanup_threads(self):
        """清理所有插件后台线程"""
        try:
            # 停止插件管理器线程
            if hasattr(self, 'plugin_manager_thread') and self.plugin_manager_thread:
                if self.plugin_manager_thread.isRunning():
                    self.plugin_manager_thread.quit()
                    self.plugin_manager_thread.wait(1000)
            
            # 停止所有插件后台线程
            if hasattr(self.plugin_manager_thread, 'plugin_threads'):
                for plugin_name, thread in self.plugin_manager_thread.plugin_threads.items():
                    if thread and thread.isRunning():
                        thread.stop()
                        if thread.wait(2000):  # 等待最多2秒
                            logger.info(f"插件 {plugin_name} 后台线程已正常停止")
                        else:
                            logger.warning(f"插件 {plugin_name} 后台线程停止超时，强制终止")
                            thread.terminate()
                            thread.wait(500)
        except Exception as e:
            logger.error(f"清理线程时发生错误: {str(e)}")


class ReadmeDialog(QDialog):
    """插件说明文件显示对话框"""
    def __init__(self, plugin_info, parent=None):
        super().__init__(parent)
        
        self.plugin_info = plugin_info
        self.readme_path = plugin_info['readme_path']
        
        # 🌟 星穹铁道白露：设置无边框窗口样式并解决屏幕设置冲突~ 
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self.setWindowTitle(f'{plugin_info["name"]} - 说明文件')
        self.setMinimumSize(800, 600)
        self.setSizeGripEnabled(True) #启用右下角拖动柄
        
        self.update_theme_style()
        qconfig.themeChanged.connect(self.update_theme_style)
        
        self.dragging = False
        self.drag_position = None
        
        # 🐦 小鸟游星野：创建自定义标题栏啦~ (≧∇≦)ﾉ
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
        self.text_browser.setFont(QFont(load_custom_font(), 10))
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
            
            # 检查文件扩展名，如果是markdown则进行基本格式化
            if self.readme_path.lower().endswith('.md'):
                # 简单的markdown格式化
                content = self._format_markdown(content)
            
            self.text_browser.setPlainText(content)
        except UnicodeDecodeError:
            # 如果UTF-8解码失败，尝试其他编码
            try:
                with open(self.readme_path, 'r', encoding='gbk') as f:
                    content = f.read()
                self.text_browser.setPlainText(content)
            except Exception as e:
                self.text_browser.setPlainText(f"无法读取文件内容: {str(e)}")
        except Exception as e:
            self.text_browser.setPlainText(f"读取文件时发生错误: {str(e)}")
    
    def _format_markdown(self, content):
        """简单的markdown格式化"""
        # 处理标题
        import re
        
        # # 标题
        content = re.sub(r'^# (.+)$', r'\1\n' + '='*50, content, flags=re.MULTILINE)
        content = re.sub(r'^## (.+)$', r'\1\n' + '-'*30, content, flags=re.MULTILINE)
        content = re.sub(r'^### (.+)$', r'\1\n' + '~'*20, content, flags=re.MULTILINE)
        
        # 处理粗体
        content = re.sub(r'\*\*(.+?)\*\*', r'\1', content)
        
        # 处理斜体
        content = re.sub(r'\*(.+?)\*', r'\1', content)
        
        # 处理代码块
        content = re.sub(r'```([\s\S]+?)```', lambda m: m.group(1), content)
        content = re.sub(r'`(.+?)`', lambda m: m.group(1), content)
        
        # 处理链接
        content = re.sub(r'\[(.+?)\]\((.+?)\)', r'\1 (链接: \2)', content)
        
        return content
    
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
        """根据当前主题更新样式"""
        if qconfig.theme == Theme.AUTO:
            # 获取系统当前主题
            lightness = QApplication.palette().color(QPalette.Window).lightness()
            is_dark = lightness <= 127
        else:
            is_dark = qconfig.theme == Theme.DARK
        
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
                