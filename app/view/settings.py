from qfluentwidgets import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from typing import Dict, List, Tuple, Optional, Any, Union

import os
import json
from loguru import logger

from app.common.config import get_theme_icon, load_custom_font
from app.common.path_utils import path_manager, open_file, ensure_dir, file_exists

# 导入子页面
from app.view.settings_page.more_setting import more_setting
from app.view.settings_page.Changeable_history_handoff_setting import changeable_history_handoff_setting
from app.view.settings_page.password_setting import password_set
from app.view.settings_page.about_setting import about
from app.view.settings_page.custom_setting import custom_setting
from app.view.settings_page.pumping_handoff_setting import pumping_handoff_setting
from app.view.settings_page.voice_engine_setting import voice_engine_settings

# 常量定义
# 窗口尺寸常量
DEFAULT_WINDOW_WIDTH = 800
DEFAULT_WINDOW_HEIGHT = 600
MIN_WINDOW_WIDTH = 600
MIN_WINDOW_HEIGHT = 400
WINDOW_TITLE = 'SecRandom - 设置'

# 延迟时间常量
INTERFACE_CREATION_DELAY = 1  # 界面创建间隔（毫秒）
INTERFACE_CREATION_INITIAL_DELAY = 10  # 界面创建初始延迟（毫秒）
DELAYED_NAVIGATION_DELAY = 200  # 延迟添加导航项的延迟时间（毫秒）
RESIZE_DELAY = 500  # 窗口大小调整延迟(毫秒)
LAYOUT_UPDATE_DELAY = 100  # 布局更新延迟(毫秒)

# 背景效果常量
DEFAULT_BLUR_RADIUS = 10  # 默认模糊半径
DEFAULT_BRIGHTNESS_VALUE = 30  # 默认亮度值(0-100)
BRIGHTNESS_FACTOR_DIVISOR = 100.0  # 亮度因子除数

# 界面配置类型
InterfaceConfig = Tuple[Any, str, str]  # (界面类, 界面名称, 属性名)
NavigationItemConfig = Tuple[str, str, str, Any]  # (属性名, 图标名, 显示名, 位置或设置键)


class settings_Window(MSFluentWindow):
    # 定义个性化设置变化信号
    personal_settings_changed = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__()
        self.app_dir = path_manager._app_root
        
        # 初始化计时器
        self._init_timers()
        
        # 加载窗口设置
        self._load_window_settings()
        
        # 设置窗口基本属性
        self._setup_window_properties()
        
        # 应用背景
        self.apply_background_image()
        
        # 设置窗口位置
        self._position_window()
        
        # 后台创建子界面，避免阻塞进程
        QTimer.singleShot(0, self.createSubInterface)
    
    def _init_timers(self) -> None:
        """初始化所有计时器"""
        self.resize_timer = QTimer(self)
        self.resize_timer.setSingleShot(True)
        self.resize_timer.timeout.connect(self.save_settings_window_size)
        
        self.interface_creation_timer = QTimer(self)
        self.interface_creation_timer.setSingleShot(True)
    
    def _load_window_settings(self) -> None:
        """加载窗口大小设置"""
        settings_path = path_manager.get_settings_path()
        try:
            with open_file(settings_path, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                foundation_settings = settings.get('foundation', {})
                # 读取保存的窗口大小，使用默认值
                window_width = foundation_settings.get('settings_window_width', DEFAULT_WINDOW_WIDTH)
                window_height = foundation_settings.get('settings_window_height', DEFAULT_WINDOW_HEIGHT)
                self.resize(window_width, window_height)
        except FileNotFoundError as e:
            logger.error(f"加载设置时出错: {e}, 使用默认大小:{DEFAULT_WINDOW_WIDTH}x{DEFAULT_WINDOW_HEIGHT}")
            self.resize(DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT)
        except Exception as e:
            logger.error(f"加载窗口大小设置失败: {e}, 使用默认大小:{DEFAULT_WINDOW_WIDTH}x{DEFAULT_WINDOW_HEIGHT}")
            self.resize(DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT)
    
    def _setup_window_properties(self) -> None:
        """设置窗口基本属性"""
        self.setMinimumSize(MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT)
        self.setWindowTitle(WINDOW_TITLE)
        self.setWindowIcon(QIcon(str(path_manager.get_resource_path('icon', 'secrandom-icon-paper.png'))))
    
    def _position_window(self) -> None:
        """根据设置定位窗口"""
        screen = QApplication.primaryScreen()
        desktop = screen.availableGeometry()
        w, h = desktop.width(), desktop.height()
        
        settings_path = path_manager.get_settings_path()
        try:
            with open_file(settings_path, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                foundation_settings = settings.get('foundation', {})
                settings_window_mode = foundation_settings.get('settings_window_mode', 0)
                
                if settings_window_mode == 0:
                    # 居中显示
                    self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)
                elif settings_window_mode == 1:
                    # 靠下显示
                    self.move(w // 2 - self.width() // 2, h * 3 // 5 - self.height() // 2)
        except FileNotFoundError as e:
            logger.error(f"加载设置时出错: {e}, 使用默认窗口居中显示设置界面")
            self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)

    def createSubInterface(self) -> None:
        """异步创建所有设置界面，避免阻塞主界面"""
        # 定义界面创建配置：界面类、界面名称、属性名
        interface_configs: List[InterfaceConfig] = [
            (more_setting, "更多设置", "more_settingInterface"),
            (custom_setting, "自定义设置", "custom_settingInterface"),
            (pumping_handoff_setting, "抽取设置", "pumping_handoff_settingInterface"),
            (changeable_history_handoff_setting, "历史记录设置", "changeable_history_handoff_settingInterface"),
            (about, "关于", "about_settingInterface"),
            (password_set, "安全设置", "password_setInterface"),
            (voice_engine_settings, "语音设置", "voice_engine_settingsInterface")
        ]
        
        # 创建界面状态跟踪字典
        self.interface_status: Dict[str, bool] = {}
        
        # 保存界面配置列表，供后续使用
        self.remaining_interface_configs = interface_configs
        
        # 使用QTimer异步创建界面，避免阻塞主线程
        self.interface_creation_timer.timeout.connect(self._create_interface_async)
        self.interface_creation_timer.start(INTERFACE_CREATION_INITIAL_DELAY)  # 立即开始创建
    
    def _create_interface_async(self) -> None:
        """异步创建界面，每次只创建一个界面，避免阻塞主线程"""
        if not hasattr(self, 'remaining_interface_configs') or not self.remaining_interface_configs:
            # 所有界面创建完成，初始化导航栏
            self.interface_creation_timer.stop()
            self.initNavigation()
            logger.info("所有界面创建完成，初始化导航栏")
            return
        
        # 取出第一个配置
        interface_class, name, attr_name = self.remaining_interface_configs[0]
        
        try:
            # 直接创建界面实例
            interface = interface_class(self)
            interface.setObjectName(attr_name)
            
            setattr(self, attr_name, interface)
            
            # 记录创建状态
            self.interface_status[attr_name] = True
            logger.info(f"{name}界面创建成功")
            
        except Exception as e:
            logger.error(f"创建{name}界面失败: {e}")
            self.interface_status[attr_name] = False
        
        # 处理剩余的界面配置
        self.remaining_interface_configs = self.remaining_interface_configs[1:]
        
        # 如果还有界面需要创建，继续处理
        if self.remaining_interface_configs:
            # 使用较短延迟，让界面有机会响应其他事件
            self.interface_creation_timer.start(INTERFACE_CREATION_DELAY)
        else:
            # 所有界面创建完成，初始化导航栏
            self.interface_creation_timer.stop()
            self.initNavigation()
            logger.info("所有界面创建完成，初始化导航栏")
    
    def _check_process_completion(self) -> None:
        """检查进程完成状态并处理结果（保留此方法以避免可能的引用错误）"""
        pass
    
    def _create_interface_with_error_handling(self, interface_class: Any, interface_name: str, attr_name: str) -> Optional[QWidget]:
        """通用界面创建方法，包含错误处理
        
        Args:
            interface_class: 界面类
            interface_name: 界面名称（用于日志）
            attr_name: 界面属性名称
            
        Returns:
            创建的界面实例或None
        """
        try:
            interface = interface_class(self)
            interface.setObjectName(attr_name)
            logger.info(f"{interface_name}界面创建成功")
            return interface
        except Exception as e:
            logger.error(f"创建{interface_name}界面失败: {e}")
            if interface_name == "抽取设置":
                import traceback
                logger.error(f"错误堆栈信息: {traceback.format_exc()}")
            return None
    
    def _create_more_setting_interface(self) -> None:
        """后台创建更多设置界面"""
        self.more_settingInterface = self._create_interface_with_error_handling(
            more_setting, "更多设置", "more_settingInterface"
        )
    
    def _create_custom_setting_interface(self) -> None:
        """后台创建自定义设置界面"""
        self.custom_settingInterface = self._create_interface_with_error_handling(
            custom_setting, "自定义设置", "custom_settingInterface"
        )
    
    def _create_pumping_handoff_setting_interface(self) -> None:
        """后台创建抽取设置界面"""
        self.pumping_handoff_settingInterface = self._create_interface_with_error_handling(
            pumping_handoff_setting, "抽取设置", "pumping_handoff_settingInterface"
        )
    
    def _create_conditional_interface(self, interface_class: Any, interface_name: str, attr_name: str, setting_key: str) -> None:
        """根据设置条件创建界面
        
        Args:
            interface_class: 界面类
            interface_name: 界面名称（用于日志）
            attr_name: 界面属性名称
            setting_key: 设置键名
        """
        try:
            settings_path = path_manager.get_settings_path('custom_settings.json')
            with open_file(settings_path, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                sidebar_settings = settings.get('sidebar', {})
                setting_value = sidebar_settings.get(setting_key, 1)
                
                if setting_value != 2:  # 不为"不显示"时才创建界面
                    interface = interface_class(self)
                    interface.setObjectName(attr_name)
                    setattr(self, attr_name, interface)
                    logger.info(f"{interface_name}界面创建成功")
                else:
                    logger.info(f"{interface_name}界面已设置为不创建")
                    setattr(self, attr_name, None)
        except Exception as e:
            logger.error(f"读取{interface_name}界面设置失败: {e}, 默认创建界面")
            interface = interface_class(self)
            interface.setObjectName(attr_name)
            setattr(self, attr_name, interface)
            logger.info(f"{interface_name}界面创建成功")
    
    def _create_changeable_history_handoff_setting_interface(self) -> None:
        """后台创建历史记录设置界面"""
        self._create_conditional_interface(
            changeable_history_handoff_setting, 
            "历史记录设置", 
            "changeable_history_handoff_settingInterface",
            "show_history_settings_switch"
        )
    
    def _create_about_setting_interface(self) -> None:
        """后台创建关于界面"""
        self.about_settingInterface = self._create_interface_with_error_handling(
            about, "关于", "about_settingInterface"
        )
    
    def _create_password_set_interface(self) -> None:
        """后台创建安全设置界面"""
        self._create_conditional_interface(
            password_set, 
            "安全设置", 
            "password_setInterface",
            "show_security_settings_switch"
        )
    
    def _create_voice_engine_settings_interface(self) -> None:
        """后台创建语音设置界面"""
        self._create_conditional_interface(
            voice_engine_settings, 
            "语音设置", 
            "voice_engine_settingsInterface",
            "show_voice_settings_switch"
        )

    def _delayed_add_pumping_handoff_interface(self) -> None:
        """延迟添加抽取设置界面到导航栏"""
        # 检查抽取设置界面是否存在且完全初始化
        if hasattr(self, 'pumping_handoff_settingInterface') and self.pumping_handoff_settingInterface is not None:
            # 检查界面是否完全初始化完成
            if hasattr(self.pumping_handoff_settingInterface, 'interface_fully_initialized') and self.pumping_handoff_settingInterface.interface_fully_initialized:
                try:
                    self.addSubInterface(
                        self.pumping_handoff_settingInterface, 
                        get_theme_icon("ic_fluent_people_community_20_filled"), 
                        '抽取设置', 
                        position=NavigationItemPosition.TOP
                    )
                except Exception as e:
                    logger.error(f"延迟添加抽取设置界面到导航栏失败: {e}")
                    import traceback
                    logger.error(f"错误堆栈信息: {traceback.format_exc()}")
            else:
                # 再次延迟添加界面到导航栏
                QTimer.singleShot(300, self._delayed_add_pumping_handoff_interface)
        else:
            logger.error("抽取设置界面不存在，无法延迟添加到导航栏")

    def _add_interface_to_navigation(self, interface_attr: str, icon_name: str, display_name: str, position: Any) -> bool:
        """添加界面到导航栏的通用方法
        
        Args:
            interface_attr: 界面属性名
            icon_name: 图标名称
            display_name: 显示名称
            position: 导航位置
            
        Returns:
            是否成功添加
        """
        if hasattr(self, interface_attr) and getattr(self, interface_attr) is not None:
            interface = getattr(self, interface_attr)
            self.addSubInterface(
                interface, 
                get_theme_icon(icon_name), 
                display_name, 
                position=position
            )
            return True
        else:
            logger.error(f"{display_name}界面不存在，无法添加到导航栏")
            return False

    def _add_conditional_navigation_item(self, interface_attr: str, icon_name: str, display_name: str, setting_key: str) -> None:
        """根据设置条件添加导航项
        
        Args:
            interface_attr: 界面属性名
            icon_name: 图标名称
            display_name: 显示名称
            setting_key: 设置键名
        """
        try:
            settings_path = path_manager.get_settings_path('custom_settings.json')
            with open_file(settings_path, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                sidebar_settings = settings.get('sidebar', {})
                setting_value = sidebar_settings.get(setting_key, 1)
                
                if setting_value == 1:  # 底部
                    position = NavigationItemPosition.BOTTOM
                elif setting_value == 2:  # 不显示
                    logger.info(f"{display_name}导航项已设置为不显示")
                    return
                else:  # 顶部
                    position = NavigationItemPosition.TOP
                
                self._add_interface_to_navigation(interface_attr, icon_name, display_name, position)
                
        except Exception as e:
            logger.error(f"加载{display_name}导航项失败: {e}")
            # 默认添加到底部
            self._add_interface_to_navigation(interface_attr, icon_name, display_name, NavigationItemPosition.BOTTOM)

    def initNavigation(self) -> None:
        """初始化导航栏，处理界面可能还未创建的情况"""
        # 处理需要特殊检查的抽取设置界面
        if hasattr(self, 'pumping_handoff_settingInterface') and self.pumping_handoff_settingInterface is not None:
            if hasattr(self.pumping_handoff_settingInterface, 'interface_fully_initialized') and self.pumping_handoff_settingInterface.interface_fully_initialized:
                try:
                    self.addSubInterface(
                        self.pumping_handoff_settingInterface, 
                        get_theme_icon("ic_fluent_people_community_20_filled"), 
                        '抽取设置', 
                        position=NavigationItemPosition.TOP
                    )
                except Exception as e:
                    logger.error(f"添加抽取设置界面到导航栏失败: {e}")
                    import traceback
                    logger.error(f"错误堆栈信息: {traceback.format_exc()}")
            else:
                # 延迟添加界面到导航栏
                QTimer.singleShot(DELAYED_NAVIGATION_DELAY, self._delayed_add_pumping_handoff_interface)
        else:
            logger.error("抽取设置界面不存在，无法添加到导航栏")

        # 添加固定位置的导航项
        self._add_interface_to_navigation(
            "custom_settingInterface", 
            "ic_fluent_person_20_filled", 
            "个性设置", 
            NavigationItemPosition.TOP
        )
        
        # 添加根据设置条件决定位置的导航项
        self._add_conditional_navigation_item(
            "voice_engine_settingsInterface",
            "ic_fluent_person_voice_20_filled",
            "语音设置",
            "show_voice_settings_switch"
        )
        
        self._add_conditional_navigation_item(
            "password_setInterface",
            "ic_fluent_shield_keyhole_20_filled",
            "安全设置",
            "show_security_settings_switch"
        )
        
        # 历史记录设置有特殊的点击事件处理
        self._add_conditional_navigation_item(
            "changeable_history_handoff_settingInterface",
            "ic_fluent_chat_history_20_filled",
            "历史记录",
            "show_history_settings_switch"
        )
        
        # 添加固定在底部的导航项
        self._add_interface_to_navigation(
            "about_settingInterface", 
            "ic_fluent_info_20_filled", 
            "关于", 
            NavigationItemPosition.BOTTOM
        )
        
        self._add_interface_to_navigation(
            "more_settingInterface", 
            "ic_fluent_more_horizontal_20_filled", 
            "更多设置", 
            NavigationItemPosition.BOTTOM
        )

        self.apply_font_settings()

    def closeEvent(self, event: QCloseEvent) -> None:
        """窗口关闭时隐藏主界面"""
        # 停止resize_timer以优化CPU占用
        if hasattr(self, 'resize_timer') and self.resize_timer.isActive():
            self.resize_timer.stop()
            logger.info("设置窗口resize_timer已停止")
        
        self.hide()
        event.ignore()
        self.save_settings_window_size()

    def resizeEvent(self, event: QResizeEvent) -> None:
        """窗口大小改变事件处理"""
        # 调整大小时重启计时器，仅在停止调整后保存
        self.resize_timer.start(RESIZE_DELAY)  # 使用常量替代硬编码值
        
        # 调用原始的resizeEvent，确保布局正确更新
        super().resizeEvent(event)
        
        # 强制更新布局
        self.updateGeometry()
        self.update()
        
        # 处理窗口最大化状态
        if self.isMaximized():
            # 确保所有子控件适应最大化窗口
            for child in self.findChildren(QWidget):
                child.updateGeometry()
            # 强制重新布局
            QApplication.processEvents()

    def save_settings_window_size(self) -> None:
        """保存窗口大小设置"""
        if not self.isMaximized():
            try:
                settings_path = path_manager.get_settings_path()
                # 读取现有设置
                try:
                    with open_file(settings_path, 'r', encoding='utf-8') as f:
                        settings = json.load(f)
                except FileNotFoundError:
                    settings = {}
                
                # 确保foundation键存在
                if 'foundation' not in settings:
                    settings['foundation'] = {}
                
                # 更新窗口大小设置
                settings['foundation']['settings_window_width'] = self.width()
                settings['foundation']['settings_window_height'] = self.height()
                
                # 保存设置
                ensure_dir(settings_path.parent)
                with open_file(settings_path, 'w', encoding='utf-8') as f:
                    json.dump(settings, f, ensure_ascii=False, indent=4)
            except Exception as e:
                logger.error(f"保存窗口大小设置失败: {e}")

    # ==================================================
    # 字体设置相关函数
    # ==================================================
    def apply_font_settings(self):
        """应用字体设置，加载并应用保存的字体（后台创建，不阻塞进程）"""
        try:
            # 读取字体设置文件
            settings_file = path_manager.get_settings_path('custom_settings.json')
            ensure_dir(settings_file.parent)
            
            font_family = 'HarmonyOS Sans SC'  # 默认字体
            
            if file_exists(settings_file):
                try:
                    with open_file(settings_file, 'r', encoding='utf-8') as f:
                        settings = json.load(f)
                        personal_settings = settings.get('personal', {})
                        custom_font_family = personal_settings.get('font_family', '')
                        if custom_font_family:
                            font_family = custom_font_family
                except Exception as e:
                    logger.error(f"读取字体设置失败: {e}")
            
            # 应用字体设置（后台创建，不阻塞进程）
            logger.info(f"字体设置: {font_family}")
            # 用QTimer在后台应用字体，不阻塞主进程
            QTimer.singleShot(0, lambda: self.apply_font_to_application(font_family))
        except Exception as e:
            logger.error(f"初始化字体设置失败: {e}")
            # 发生错误时使用默认字体
            logger.info("初始化字体设置: 发生错误，使用默认字体")
            # 用QTimer在后台应用字体，不阻塞主进程
            QTimer.singleShot(0, lambda: self.apply_font_to_application('HarmonyOS Sans SC'))

    def apply_font_to_application(self, font_family):
        """应用字体设置到整个应用程序
        
        Args:
            font_family (str): 字体家族名称
        """
        try:
            # 获取当前应用程序默认字体
            current_font = QApplication.font()
            
            # 创建字体对象，只修改字体家族，保持原有字体大小
            app_font = QFont(font_family)
            app_font.setPointSize(current_font.pointSize())
            
            # 如果是HarmonyOS Sans SC字体，使用特定的字体文件路径
            if font_family == "HarmonyOS Sans SC":
                font_path = path_manager.get_font_path('HarmonyOS_Sans_SC_Bold.ttf')
                if font_path and path_manager.file_exists(font_path):
                    font_id = QFontDatabase.addApplicationFont(str(font_path))
                    if font_id >= 0:
                        font_families = QFontDatabase.applicationFontFamilies(font_id)
                        if font_families:
                            app_font = QFont(font_families[0])
                            app_font.setPointSize(current_font.pointSize())
                            # logger.debug(f"已加载HarmonyOS Sans SC字体文件: {font_path}")
                        else:
                            logger.error(f"无法从字体文件获取字体家族: {font_path}")
                    else:
                        logger.error(f"无法加载字体文件: {font_path}")
                else:
                    logger.error(f"HarmonyOS Sans SC字体文件不存在: {font_path}")
            
            # 获取所有顶级窗口并更新它们的字体
            widgets_updated = 0
            for widget in QApplication.allWidgets():
                if isinstance(widget, QWidget):
                    self.update_widget_fonts(widget, app_font)
                    widgets_updated += 1
                
            # logger.debug(f"已应用字体: {font_family}, 更新了{widgets_updated}个控件字体")
        except Exception as e:
            logger.error(f"应用字体失败: {e}")

    def update_widget_fonts(self, widget, font):
        """更新控件及其子控件的字体，优化版本减少内存占用
        
        Args:
            widget: 要更新字体的控件
            font: 要应用的字体
        """
        if widget is None:
            return
            
        try:
            # 获取控件当前字体
            current_widget_font = widget.font()
            
            # 创建新字体，只修改字体家族，保持原有字体大小和其他属性
            new_font = QFont(font.family(), current_widget_font.pointSize())
            # 保持原有字体的粗体和斜体属性
            new_font.setBold(current_widget_font.bold())
            new_font.setItalic(current_widget_font.italic())
            
            # 更新当前控件的字体
            widget.setFont(new_font)
            
            # 如果控件有子控件，递归更新子控件的字体
            if isinstance(widget, QWidget):
                children = widget.children()
                for child in children:
                    if isinstance(child, QWidget):
                        self.update_widget_fonts(child, font)
        except Exception as e:
            logger.error(f"更新控件字体时发生异常: {e}")

    def apply_background_image(self) -> None:
        """检查设置中的 enable_settings_background 和 enable_settings_background_color，
        如果开启则应用设置界面背景图片或背景颜色"""
        try:
            # 读取自定义设置
            custom_settings_path = path_manager.get_settings_path('custom_settings.json')
            with open_file(custom_settings_path, 'r', encoding='utf-8') as f:
                custom_settings = json.load(f)
                
            # 检查是否启用了设置界面背景图标
            personal_settings = custom_settings.get('personal', {})
            enable_settings_background = personal_settings.get('enable_settings_background', True)
            enable_settings_background_color = personal_settings.get('enable_settings_background_color', False)
            
            # 优先应用背景颜色（如果启用）
            if enable_settings_background_color:
                self._apply_background_color(personal_settings)
            # 如果背景颜色未启用，但背景图片启用了，则应用背景图片
            elif enable_settings_background:
                self._apply_background_image(personal_settings)
            else:
                # 如果两者都未启用，则使用默认背景
                self._reset_background()
                
        except FileNotFoundError:
            logger.error("自定义设置文件不存在，使用默认设置")
        except Exception as e:
            logger.error(f"应用设置界面背景图片或颜色时发生异常: {e}")
    
    def _apply_background_color(self, personal_settings: Dict[str, Any]) -> None:
        """应用背景颜色
        
        Args:
            personal_settings: 个人设置字典
        """
        settings_background_color = personal_settings.get('settings_background_color', '#FFFFFF')
        
        # 创建背景颜色标签并设置样式（使用标签方式，与图片保持一致）
        self.background_label = QLabel(self)
        self.background_label.setGeometry(0, 0, self.width(), self.height())
        self.background_label.setStyleSheet(f"background-color: {settings_background_color};")
        self.background_label.lower()  # 将背景标签置于底层
        
        # 设置窗口属性，确保背景可见
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("background: transparent;")
        
        # 保存原始的resizeEvent方法
        self.original_resizeEvent = self.resizeEvent
        
        # 重写resizeEvent方法，调整背景大小
        self.resizeEvent = self._on_resize_event
        
        logger.info(f"已成功应用设置界面背景颜色 {settings_background_color}")
    
    def _apply_background_image(self, personal_settings: Dict[str, Any]) -> None:
        """应用背景图片
        
        Args:
            personal_settings: 个人设置字典
        """
        # 获取设置界面背景图片设置
        settings_background_image = personal_settings.get('settings_background_image', '')
        
        # 检查是否选择了背景图片
        if not settings_background_image or settings_background_image == "无背景图":
            logger.info("未选择设置界面背景图片")
            self._reset_background()
            return
        
        # 获取背景图片文件夹路径
        background_dir = path_manager.get_resource_path('images', 'background')
        
        # 检查文件夹是否存在
        if not background_dir.exists():
            logger.error("背景图片文件夹不存在")
            return
        
        # 构建图片完整路径
        image_path = background_dir / settings_background_image
        
        # 检查图片文件是否存在
        if not image_path.exists():
            logger.error(f"设置界面背景图片 {settings_background_image} 不存在")
            return
        
        # 创建背景图片对象
        background_pixmap = QPixmap(str(image_path))
        
        # 如果图片加载失败
        if background_pixmap.isNull():
            logger.error(f"设置界面背景图片 {settings_background_image} 加载失败")
            return
        
        # 获取模糊度和亮度设置
        blur_value = personal_settings.get('background_blur', DEFAULT_BLUR_RADIUS)
        brightness_value = personal_settings.get('background_brightness', DEFAULT_BRIGHTNESS_VALUE)
        
        # 应用模糊效果
        if blur_value > 0:
            background_pixmap = self._apply_blur_effect(background_pixmap, blur_value)
        
        # 应用亮度效果
        if brightness_value != 100:
            background_pixmap = self._apply_brightness_effect(background_pixmap, brightness_value)
        
        # 创建背景标签并设置样式
        self.background_label = QLabel(self)
        self.background_label.setGeometry(0, 0, self.width(), self.height())
        self.background_label.setPixmap(background_pixmap.scaled(
            self.width(), self.height(), 
            Qt.IgnoreAspectRatio, 
            Qt.SmoothTransformation
        ))
        self.background_label.lower()  # 将背景标签置于底层
        
        # 保存原始图片，用于窗口大小调整时重新缩放
        self.original_background_pixmap = background_pixmap
        
        # 确保背景标签随窗口大小变化
        self.background_label.setAttribute(Qt.WA_StyledBackground, True)
        
        # 设置窗口属性，确保背景可见
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("background: transparent;")
        
        # 保存原始的resizeEvent方法
        self.original_resizeEvent = self.resizeEvent
        
        # 重写resizeEvent方法，调整背景大小
        self.resizeEvent = self._on_resize_event
        
        logger.info(f"已成功应用设置界面背景图片 {settings_background_image}，模糊度: {blur_value}，亮度: {brightness_value}%")
    
    def _apply_blur_effect(self, pixmap: QPixmap, blur_radius: int = DEFAULT_BLUR_RADIUS) -> QPixmap:
        """应用模糊效果
        
        Args:
            pixmap: 原始图片
            blur_radius: 模糊半径，默认使用常量DEFAULT_BLUR_RADIUS
            
        Returns:
            处理后的图片
        """
        # 创建模糊效果
        blur_effect = QGraphicsBlurEffect()
        blur_effect.setBlurRadius(blur_radius)
        
        # 创建临时场景和图形项来应用模糊效果
        scene = QGraphicsScene()
        item = QGraphicsPixmapItem(pixmap)
        item.setGraphicsEffect(blur_effect)
        scene.addItem(item)
        
        # 创建渲染图像
        result_image = QImage(pixmap.size(), QImage.Format_ARGB32)
        result_image.fill(Qt.transparent)
        painter = QPainter(result_image)
        scene.render(painter)
        painter.end()
        
        return QPixmap.fromImage(result_image)
    
    def _apply_brightness_effect(self, pixmap: QPixmap, brightness_value: int) -> QPixmap:
        """应用亮度效果
        
        Args:
            pixmap: 原始图片
            brightness_value: 亮度值 (0-100)
            
        Returns:
            处理后的图片
        """
        # 创建图像副本
        brightness_image = QImage(pixmap.size(), QImage.Format_ARGB32)
        brightness_image.fill(Qt.transparent)
        painter = QPainter(brightness_image)
        
        # 计算亮度调整因子，使用常量替代硬编码值
        brightness_factor = brightness_value / BRIGHTNESS_FACTOR_DIVISOR
        
        # 应用亮度调整
        painter.setOpacity(brightness_factor)
        painter.drawPixmap(0, 0, pixmap)
        painter.end()
        
        return QPixmap.fromImage(brightness_image)
    
    def _reset_background(self) -> None:
        """重置为默认背景"""
        self.setStyleSheet("background: transparent;")
        
        # 清除可能存在的背景图片标签
        if hasattr(self, 'background_label') and self.background_label:
            self.background_label.deleteLater()
            delattr(self, 'background_label')
        
        # 恢复原始的resizeEvent方法
        if hasattr(self, 'original_resizeEvent'):
            self.resizeEvent = self.original_resizeEvent
            delattr(self, 'original_resizeEvent')
        
        # logger.debug("设置界面背景图片和颜色功能均未启用，使用默认背景")
    
    def _on_resize_event(self, event: QResizeEvent) -> None:
        """当窗口大小改变时，自动调整背景图片大小，确保背景始终填满整个窗口
        
        Args:
            event: 窗口大小改变事件
        """
        # 添加防抖机制，避免频繁调整
        if hasattr(self, '_resize_timer') and self._resize_timer.isActive():
            # 如果已有定时器在运行，则取消之前的
            self._resize_timer.stop()
        
        # 创建新的定时器
        if not hasattr(self, '_resize_timer'):
            self._resize_timer = QTimer(self)
            self._resize_timer.setSingleShot(True)
            self._resize_timer.timeout.connect(lambda: self._perform_resize(event))
        
        # 延迟执行调整操作，避免频繁调整
        self._resize_timer.start(50)  # 50ms 延迟
        
        event.accept()
    
    def _perform_resize(self, event: QResizeEvent) -> None:
        """实际执行窗口大小调整操作
        
        Args:
            event: 窗口大小改变事件
        """
        # 调用原始的resizeEvent，确保布局正确更新
        if hasattr(self, 'original_resizeEvent'):
            self.original_resizeEvent(event)
        else:
            super(settings_Window, self).resizeEvent(event)
        
        # 如果存在背景标签，调整其大小
        if hasattr(self, 'background_label') and self.background_label:
            self.background_label.setGeometry(0, 0, self.width(), self.height())
            # 使用保存的原始图片进行缩放，避免重复缩放导致的像素化
            if hasattr(self, 'original_background_pixmap') and self.original_background_pixmap:
                self.background_label.setPixmap(self.original_background_pixmap.scaled(
                    self.width(), self.height(), 
                    Qt.IgnoreAspectRatio, 
                    Qt.SmoothTransformation
                ))
        
        # 处理窗口最大化状态
        if self.isMaximized():
            self._handle_maximized_state()
    
    def _handle_maximized_state(self) -> None:
        """当窗口最大化时，确保所有控件正确适应新的窗口大小"""
        # 确保所有子控件适应最大化窗口
        for child in self.findChildren(QWidget):
            child.updateGeometry()
        
        # 移除可能导致阻塞的 processEvents 调用
        # QApplication.processEvents()
        
        # 使用单次定时器延迟更新布局，避免递归调用
        if not hasattr(self, '_layout_update_timer'):
            self._layout_update_timer = QTimer(self)
            self._layout_update_timer.setSingleShot(True)
            self._layout_update_timer.timeout.connect(self._update_layout)
        
        # 如果定时器未激活，则启动布局更新
        if not self._layout_update_timer.isActive():
            self._layout_update_timer.start(LAYOUT_UPDATE_DELAY)
    
    def _update_layout(self) -> None:
        """更新布局"""
        # 添加标志防止递归调用
        if hasattr(self, '_updating_layout') and self._updating_layout:
            return
        
        self._updating_layout = True
        
        try:
            # 更新布局
            self.updateGeometry()
            self.update()
            
            # 确保所有子控件更新
            for child in self.findChildren(QWidget):
                child.updateGeometry()
        finally:
            # 重置标志
            self._updating_layout = False

    def _delayed_layout_update(self) -> None:
        """延迟布局更新"""
        # 使用单次定时器避免递归调用
        if not hasattr(self, '_delayed_layout_timer'):
            self._delayed_layout_timer = QTimer(self)
            self._delayed_layout_timer.setSingleShot(True)
            self._delayed_layout_timer.timeout.connect(self._update_layout)
        
        # 如果定时器未激活，则启动布局更新
        if not self._delayed_layout_timer.isActive():
            self._delayed_layout_timer.start(LAYOUT_UPDATE_DELAY)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """鼠标按下事件处理，使窗口可以移动"""
        # 只处理左键点击
        if event.button() == Qt.LeftButton:
            # 检查点击位置是否在可拖动区域（例如标题栏）
            # 这里简单地将整个窗口设为可拖动区域
            self._drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
        else:
            super(settings_Window, self).mousePressEvent(event)
    
    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """鼠标移动事件处理，实现窗口拖动"""
        # 只处理左键拖动
        if event.buttons() == Qt.LeftButton and hasattr(self, '_drag_position'):
            # 移动窗口
            self.move(event.globalPos() - self._drag_position)
            event.accept()
        else:
            super(settings_Window, self).mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """鼠标释放事件处理"""
        if event.button() == Qt.LeftButton and hasattr(self, '_drag_position'):
            # 清除拖动位置
            delattr(self, '_drag_position')
            event.accept()
        else:
            super(settings_Window, self).mouseReleaseEvent(event)
