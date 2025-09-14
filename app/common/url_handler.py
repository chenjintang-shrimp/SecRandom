import sys
import argparse
import json
import os
from loguru import logger
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from qfluentwidgets import *
from app.common.config import get_theme_icon, load_custom_font, check_for_updates, VERSION
from app.common.path_utils import path_manager
from app.common.path_utils import open_file, ensure_dir
from app.common.update_notification import UpdateNotification

class URLHandler:
    """URL处理器类"""
    
    def __init__(self):
        self.url_command = None
        self.fixed_url_settings = {}
        self.config_file_path = ""
        self.last_modified_time = 0
        self.load_fixed_url_settings()
        self.parse_command_line()
    
    def load_fixed_url_settings(self):
        """加载fixed_url设置"""
        try:
            # 获取配置文件路径
            self.config_file_path = path_manager.get_settings_path('custom_settings.json')
            
            # 检查配置文件是否存在
            if not os.path.exists(self.config_file_path):
                logger.warning(f"配置文件不存在: {self.config_file_path}")
                self._load_default_settings()
                return
            
            # 获取当前配置文件的修改时间
            current_modified_time = os.path.getmtime(self.config_file_path)
            
            # 如果配置文件未被修改，使用缓存的设置
            if current_modified_time == self.last_modified_time and self.fixed_url_settings:
                logger.debug("配置文件未修改，使用缓存的设置")
                return
            
            # 更新修改时间
            self.last_modified_time = current_modified_time
            
            # 读取配置文件
            with open(self.config_file_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                self.fixed_url_settings = config.get('fixed_url', {})
        except Exception as e:
            logger.error(f"加载fixed_url设置失败: {str(e)}")
            self._load_default_settings()
    
    def _load_default_settings(self):
        """加载默认设置"""
        self.fixed_url_settings = {
            "enable_main_url": True,
            "enable_settings_url": True,
            "enable_pumping_url": True,
            "enable_reward_url": True,
            "enable_history_url": True,
            "enable_floating_url": True,
            "enable_about_url": True,
            "enable_direct_extraction_url": True,
            "enable_pumping_action_url": True,
            "enable_reward_action_url": True,
            "enable_about_action_url": True,
            "enable_plugin_settings_action_url": True,
            "enable_pumping_start_url": True,
            "enable_pumping_stop_url": True,
            "enable_pumping_reset_url": True,
            "enable_reward_start_url": True,
            "enable_reward_stop_url": True,
            "enable_reward_reset_url": True,
            "enable_about_donation_url": True,
            "enable_about_contributor_url": True,
            "enable_plugin_settings_open_url": True,
            # 弹窗提醒设置(disabled, notify_only, confirm, confirm_with_security)
            "main_url_notification": "disabled",
            "settings_url_notification": "disabled",
            "pumping_url_notification": "disabled",
            "reward_url_notification": "disabled",
            "history_url_notification": "disabled",
            "floating_url_notification": "disabled",
            "about_url_notification": "disabled",
            "direct_extraction_url_notification": "disabled",
            "plugin_settings_url_notification": "disabled",
            "pumping_start_url_notification": "disabled",
            "pumping_stop_url_notification": "disabled",
            "pumping_reset_url_notification": "disabled",
            "reward_start_url_notification": "disabled",
            "reward_stop_url_notification": "disabled",
            "reward_reset_url_notification": "disabled",
            "about_donation_url_notification": "disabled",
            "about_contributor_url_notification": "disabled",
            "plugin_settings_open_url_notification": "disabled",
            # 跳过安全验证设置
            "settings_url_skip_security": False,
            "floating_url_skip_security": False,
            "plugin_settings_open_url_skip_security": False,
        }
    
    def is_url_enabled(self, url_type):
        """检查特定URL是否启用"""
        return self.fixed_url_settings.get(url_type, True)
    
    def get_notification_setting(self, url_type):
        """获取特定URL的弹窗提醒设置"""
        return self.fixed_url_settings.get(f"{url_type}_notification", "disabled")
    
    def show_url_notification(self, url, url_type, callback=None):
        """显示URL弹窗提醒"""
        try:
            notification_type = self.get_notification_setting(url_type)
            
            if notification_type == "disabled":
                # 如果弹窗提醒已禁用，直接执行回调
                if callback:
                    callback()
                return True
            
            # 创建弹窗
            notification = URLNotification(url, url_type, notification_type, callback)
            notification.show()
            
            return True
        except Exception as e:
            logger.error(f"显示URL弹窗提醒失败: {str(e)}")
            # 如果弹窗显示失败，直接执行回调
            if callback:
                callback()
            return False
    
    def force_reload_settings(self):
        """强制重新加载配置文件"""
        logger.info("强制重新加载配置文件")
        # 重置修改时间，强制重新加载
        self.last_modified_time = 0
        self.load_fixed_url_settings()
    
    def parse_command_line(self):
        """解析命令行参数"""
        try:
            parser = argparse.ArgumentParser(description='SecRandom URL处理器')
            parser.add_argument('--url', type=str, help='通过URL协议启动的URL')
            
            # 只解析已知的参数，忽略其他参数
            args, unknown = parser.parse_known_args()
            
            if args.url:
                self.url_command = args.url
                logger.info(f"接收到URL命令: {self.url_command}")
            
        except Exception as e:
            logger.error(f"解析命令行参数失败: {str(e)}")
    
    def has_url_command(self):
        """检查是否有URL命令"""
        return self.url_command is not None
    
    def get_url_command(self):
        """获取URL命令"""
        return self.url_command
    
    def process_url_command(self, main_window=None):
        """处理URL命令"""
        if not self.has_url_command():
            return False
        
        try:
            # 在处理URL之前重新检查配置文件是否有更新
            self.load_fixed_url_settings()
            
            url = self.get_url_command()
            logger.info(f"开始处理URL命令: {url}")
            
            if not url.startswith("secrandom://"):
                logger.error(f"无效的SecRandom URL: {url}")
                return False
            
            # 解析URL
            from urllib.parse import urlparse, parse_qs
            parsed_url = urlparse(url)
            path = parsed_url.path.strip('/')
            query_params = parse_qs(parsed_url.query)
            
            logger.info(f"URL路径: {path}")
            logger.info(f"URL参数: {query_params}")
            
            # 如果没有提供主窗口，尝试获取
            if main_window is None:
                main_window = self.get_main_window()
            
            if main_window is None:
                logger.error("找不到主窗口实例")
                return False
            
            # 界面映射字典
            interface_map = {
                "main": ("show_main_window", "enable_main_url"),
                "settings": ("show_settings_window", "enable_settings_url"),
                "pumping": ("show_pumping_window", "enable_pumping_url"),
                "reward": ("show_reward_window", "enable_reward_url"),
                "history": ("show_history_window", "enable_history_url"),
                "floating": ("show_floating_window", "enable_floating_url"),
                'direct_extraction': ('show_direct_extraction', 'enable_direct_extraction_url'),
                "plugin_settings": ("show_plugin_settings_window", "enable_plugin_settings_url")
            }
            
            # 根据路径打开对应界面
            if path in interface_map:
                method_name, setting_key = interface_map[path]
                
                # 检查该URL是否启用
                if not self.is_url_enabled(setting_key):
                    logger.warning(f"URL功能已禁用: {path} (设置项: {setting_key})")
                    return False
                
                # 显示弹窗提醒
                def open_interface():
                    if hasattr(main_window, method_name):
                        method = getattr(main_window, method_name)
                        method()
                        logger.info(f"通过URL成功打开界面: {path}")
                        
                        # 处理额外的参数
                        self.handle_additional_params(main_window, query_params, path)
                    else:
                        logger.error(f"主窗口缺少方法: {method_name}")
                
                # 显示弹窗提醒
                self.show_url_notification(url, setting_key, open_interface)
                
                return True
            else:
                logger.error(f"未知的界面路径: {path}")
                
                # 显示可用路径
                available_paths = ", ".join(interface_map.keys())
                logger.info(f"可用的界面路径: {available_paths}")
            
            return False
            
        except Exception as e:
            logger.error(f"处理URL命令失败: {str(e)}")
            return False
    
    def handle_additional_params(self, main_window, query_params, path=None):
        """处理额外的URL参数"""
        try:
            # 处理action参数
            if 'action' in query_params:
                action = query_params['action'][0]
                logger.info(f"执行动作: {action}")
                
                # 根据路径和动作检查是否启用
                action_enabled = True
                
                # 抽人相关操作
                if path == "pumping":
                    if action == 'start':
                        action_enabled = self.is_url_enabled("enable_pumping_start_url")
                    elif action == 'stop':
                        action_enabled = self.is_url_enabled("enable_pumping_stop_url")
                    elif action == 'reset':
                        action_enabled = self.is_url_enabled("enable_pumping_reset_url")
                    else:
                        action_enabled = self.is_url_enabled("enable_pumping_action_url")
                
                # 抽奖相关操作
                elif path == "reward":
                    if action == 'start':
                        action_enabled = self.is_url_enabled("enable_reward_start_url")
                    elif action == 'stop':
                        action_enabled = self.is_url_enabled("enable_reward_stop_url")
                    elif action == 'reset':
                        action_enabled = self.is_url_enabled("enable_reward_reset_url")
                    else:
                        action_enabled = self.is_url_enabled("enable_reward_action_url")
                
                # 关于界面相关操作
                elif path == "about":
                    if action == 'donation':
                        action_enabled = self.is_url_enabled("enable_about_donation_url")
                    elif action == 'contributor':
                        action_enabled = self.is_url_enabled("enable_about_contributor_url")
                    else:
                        action_enabled = self.is_url_enabled("enable_about_action_url")
                
                # 插件设置相关操作
                elif path == "plugin_settings":
                    if action == 'open':
                        action_enabled = self.is_url_enabled("enable_plugin_settings_open_url")
                    else:
                        action_enabled = self.is_url_enabled("enable_plugin_settings_action_url")
                
                # 如果操作未启用，记录日志并返回
                if not action_enabled:
                    logger.warning(f"URL操作已禁用: {path}?action={action}")
                    return
                
                # 执行相应的操作
                # 抽人相关操作
                if action == 'start' and hasattr(main_window, 'start_random_selection'):
                    main_window.start_random_selection()
                elif action == 'stop' and hasattr(main_window, 'stop_random_selection'):
                    main_window.stop_random_selection()
                elif action == 'reset' and hasattr(main_window, 'reset_selection'):
                    main_window.reset_selection()
                
                # 抽奖相关操作
                elif action == 'start' and hasattr(main_window, 'start_reward_selection'):
                    main_window.start_reward_selection()
                elif action == 'stop' and hasattr(main_window, 'stop_reward_selection'):
                    main_window.stop_reward_selection()
                elif action == 'reset' and hasattr(main_window, 'reset_reward_selection'):
                    main_window.reset_reward_selection()
                
                # 关于界面相关操作
                elif action == 'donation' and hasattr(main_window, 'show_donation_dialog'):
                    main_window.show_donation_dialog()
                elif action == 'contributor' and hasattr(main_window, 'show_contributor_dialog'):
                    main_window.show_contributor_dialog()
                
                # 插件设置相关操作
                elif action == 'open' and hasattr(main_window, 'show_plugin_settings_window'):
                    main_window.show_plugin_settings_window()
                
                else:
                    logger.warning(f"未知的动作或主窗口缺少对应方法: {action}")
            
        except Exception as e:
            logger.error(f"处理额外参数失败: {str(e)}")
    
    def get_main_window(self):
        """获取主窗口实例"""
        try:
            for widget in QApplication.topLevelWidgets():
                # 通过特征识别主窗口
                if hasattr(widget, 'update_focus_mode') or hasattr(widget, 'show_main_window'):
                    return widget
            return None
        except Exception as e:
            logger.error(f"获取主窗口失败: {str(e)}")
            return None
    
    def get_available_interfaces(self):
        """获取可用的界面列表"""
        return {
            "main": "主界面",
            "settings": "设置界面",
            "pumping": "抽人界面",
            "reward": "抽奖界面",
            "history": "历史记录界面",
            "floating": "浮窗界面",
            'direct_extraction': '闪抽界面',
            "plugin_settings": "插件设置界面"
        }
    
    def generate_url_examples(self):
        """生成URL使用示例"""
        # 在生成URL示例之前重新检查配置文件是否有更新
        self.load_fixed_url_settings()
        
        examples = []
        interfaces = self.get_available_interfaces()
        
        # 界面URL示例
        for path, name in interfaces.items():
            # 检查该URL是否启用
            setting_key = f"enable_{path}_url"
            if self.is_url_enabled(setting_key):
                examples.append(f"secrandom://{path} - 打开{name}")
        
        # 抽人相关操作示例
        if self.is_url_enabled("enable_pumping_start_url"):
            examples.append("secrandom://pumping?action=start - 开始抽人")
        if self.is_url_enabled("enable_pumping_stop_url"):
            examples.append("secrandom://pumping?action=stop - 停止抽人")
        if self.is_url_enabled("enable_pumping_reset_url"):
            examples.append("secrandom://pumping?action=reset - 重置抽人")
        
        # 抽奖相关操作示例
        if self.is_url_enabled("enable_reward_start_url"):
            examples.append("secrandom://reward?action=start - 开始抽奖")
        if self.is_url_enabled("enable_reward_stop_url"):
            examples.append("secrandom://reward?action=stop - 停止抽奖")
        if self.is_url_enabled("enable_reward_reset_url"):
            examples.append("secrandom://reward?action=reset - 重置抽奖")
        
        # 关于界面相关操作示例
        if self.is_url_enabled("enable_about_donation_url"):
            examples.append("secrandom://about?action=donation - 打开捐赠支持对话框")
        if self.is_url_enabled("enable_about_contributor_url"):
            examples.append("secrandom://about?action=contributor - 打开贡献者对话框")
        
        # 插件设置相关操作示例
        if self.is_url_enabled("enable_plugin_settings_open_url"):
            examples.append("secrandom://plugin_settings?action=open - 打开插件页面")
        
        return examples


# 全局URL处理器实例
url_handler = URLHandler()


def get_url_handler():
    """获取全局URL处理器实例"""
    return url_handler


def process_url_if_exists(main_window=None):
    """如果存在URL命令则处理"""
    handler = get_url_handler()
    if handler.has_url_command():
        return handler.process_url_command(main_window)
    return False


class URLNotification(UpdateNotification):
    """URL弹窗提醒窗口"""
    
    def __init__(self, url, url_type, notification_type, callback=None):
        # 初始化父类，使用URL作为版本信息
        super().__init__(url)
        self.url = url
        self.url_type = url_type
        self.notification_type = notification_type
        self.callback = callback
        self.security_verified = False
        
        # 根据URL类型设置标题和描述
        self.url_info = self.get_url_info()
        
        # 重新初始化UI
        self.init_ui()
        self.init_animation()
        self.start_auto_close_timer()
    
    def get_url_info(self):
        """根据URL类型获取URL信息"""
        url_info_map = {
            "main": {"title": "SecRandom 主界面", "desc": "即将打开SecRandom主界面"},
            "settings": {"title": "SecRandom 设置界面", "desc": "即将打开SecRandom设置界面"},
            "pumping": {"title": "SecRandom 抽人界面", "desc": "即将打开SecRandom抽人界面"},
            "reward": {"title": "SecRandom 抽奖界面", "desc": "即将打开SecRandom抽奖界面"},
            "history": {"title": "SecRandom 历史记录界面", "desc": "即将打开SecRandom历史记录界面"},
            "floating": {"title": "SecRandom 浮窗界面", "desc": "即将打开SecRandom浮窗界面"},
            "direct_extraction": {"title": "SecRandom 闪抽界面", "desc": "即将打开SecRandom闪抽界面"},
            "plugin_settings": {"title": "SecRandom 插件设置界面", "desc": "即将打开SecRandom插件设置界面"},
            "pumping_start": {"title": "SecRandom 开始抽人", "desc": "即将开始SecRandom抽人操作"},
            "pumping_stop": {"title": "SecRandom 停止抽人", "desc": "即将停止SecRandom抽人操作"},
            "pumping_reset": {"title": "SecRandom 重置抽人", "desc": "即将重置SecRandom抽人结果"},
            "reward_start": {"title": "SecRandom 开始抽奖", "desc": "即将开始SecRandom抽奖操作"},
            "reward_stop": {"title": "SecRandom 停止抽奖", "desc": "即将停止SecRandom抽奖操作"},
            "reward_reset": {"title": "SecRandom 重置抽奖", "desc": "即将重置SecRandom抽奖结果"},
            "about_donation": {"title": "SecRandom 捐赠支持", "desc": "即将打开SecRandom捐赠支持对话框"},
            "about_contributor": {"title": "SecRandom 贡献者", "desc": "即将打开SecRandom贡献者对话框"},
            "plugin_settings_open": {"title": "SecRandom 插件页面", "desc": "即将打开SecRandom插件页面"},
        }
        
        return url_info_map.get(self.url_type, {"title": "SecRandom URL请求", "desc": f"即将处理URL请求: {self.url}"})
    
    def init_ui(self):
        """初始化UI界面"""
        cursor_pos = QCursor.pos()
        for screen in QGuiApplication.screens():
            if screen.geometry().contains(cursor_pos):
                target_screen = screen
                break
        else:
            target_screen = QGuiApplication.primaryScreen()
        screen_geometry = target_screen.availableGeometry()
        max_width = min(int(screen_geometry.width() * 0.3), 500)  # 最大宽度为屏幕30%或500px取较小值
        self.setMaximumWidth(max_width)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        # 设置窗口标志
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setStyleSheet("""
            QDialog {
                background-color: rgba(235, 238, 242, 0.5);
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 5px;
                opacity: 0;
            }
        """)

        # 创建主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(20)

        # 标题栏（包含图标和标题）
        title_layout = QHBoxLayout()
        title_layout.setSpacing(10)

        # 更新图标
        icon_label = QLabel()
        icon_path = path_manager.get_resource_path('icon', 'SecRandom.png')
        icon_label.setPixmap(QIcon(str(icon_path)).pixmap(55, 55))
        icon_label.setStyleSheet("background: transparent; border: none;")

        # 标题文本
        title_label = BodyLabel(f"SecRandom {self.url_info['title']}")
        title_label.setFont(QFont(load_custom_font(), 14, QFont.Bold))
        title_label.setStyleSheet("color: #1a1a1a; border: none; background: transparent;")

        # URL信息
        url_label = BodyLabel(f"📌 URL: {self.url}\n🎉 {self.url_info['desc']}")
        url_label.setFont(QFont(load_custom_font(), 12))
        url_label.setStyleSheet("color: #2d3436; border: none; background: transparent;")
        url_label.setAlignment(Qt.AlignCenter)

        # 关闭按钮
        close_btn = PushButton("")
        close_icon_path = get_theme_icon("ic_fluent_arrow_exit_20_filled")
        close_btn.setIcon(QIcon(str(close_icon_path)))
        close_btn.setStyleSheet("background: transparent; border: none;")
        close_btn.clicked.connect(self.close_with_animation)

        # 添加到标题布局
        title_layout.addWidget(icon_label)
        title_layout.addWidget(title_label)
        title_layout.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))
        title_layout.addWidget(close_btn)

        # 按钮布局
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        # 根据通知类型添加不同的按钮
        if self.notification_type == "notify_only":
            # 仅提醒类型，只有一个关闭按钮
            close_btn = PushButton("关闭")
            close_btn.setStyleSheet(""
                "QPushButton {background-color: #6c757d; color: white; border-radius: 8px; padding: 8px 16px; font-weight: 500; border: none;}"
                "QPushButton:hover {background-color: #5a6268;}"
            )
            close_btn.setFont(QFont(load_custom_font(), 12))
            close_btn.clicked.connect(self.close_with_animation)
            btn_layout.addWidget(close_btn)
        else:
            # 确认类型，有确认和取消按钮
            cancel_btn = PushButton("取消")
            cancel_btn.setStyleSheet(""
                "QPushButton {background-color: #6c757d; color: white; border-radius: 8px; padding: 8px 16px; font-weight: 500; border: none;}"
                "QPushButton:hover {background-color: #5a6268;}"
            )
            cancel_btn.setFont(QFont(load_custom_font(), 12))
            cancel_btn.clicked.connect(self.close_with_animation)
            
            confirm_btn = PushButton("确认")
            if self.notification_type == "confirm_with_security":
                # 安全验证确认按钮，初始为禁用状态
                confirm_btn.setEnabled(False)
                confirm_btn.setStyleSheet(""
                    "QPushButton {background-color: #dc3545; color: white; border-radius: 8px; padding: 8px 16px; font-weight: 500; border: none;}"
                    "QPushButton:hover {background-color: #c82333;}"
                    "QPushButton:disabled {background-color: #6c757d;}"
                )
                
                # 添加安全验证复选框
                security_layout = QHBoxLayout()
                security_checkbox = QCheckBox("我确认这是一个安全的操作")
                security_checkbox.setFont(QFont(load_custom_font(), 10))
                security_checkbox.setStyleSheet("color: #2d3436;")
                security_checkbox.stateChanged.connect(self.on_security_checkbox_changed)
                security_layout.addWidget(security_checkbox)
                
                # 将安全验证布局添加到主布局
                main_layout.addLayout(security_layout)
            else:
                confirm_btn.setStyleSheet(""
                    "QPushButton {background-color: #28a745; color: white; border-radius: 8px; padding: 8px 16px; font-weight: 500; border: none;}"
                    "QPushButton:hover {background-color: #218838;}"
                )
            
            confirm_btn.setFont(QFont(load_custom_font(), 12))
            confirm_btn.clicked.connect(self.on_confirm_clicked)
            
            btn_layout.addWidget(cancel_btn)
            btn_layout.addWidget(confirm_btn)

        # 添加所有组件到主布局
        main_layout.addLayout(title_layout)
        main_layout.addWidget(url_label)
        main_layout.addLayout(btn_layout)

        self.move_to_bottom_right()
    
    def on_security_checkbox_changed(self, state):
        """安全验证复选框状态变化处理"""
        self.security_verified = (state == Qt.Checked)
        # 启用或禁用确认按钮
        for i in range(self.layout().count()):
            item = self.layout().itemAt(i)
            if isinstance(item, QHBoxLayout):
                for j in range(item.count()):
                    widget = item.itemAt(j).widget()
                    if isinstance(widget, PushButton) and widget.text() == "确认":
                        widget.setEnabled(self.security_verified)
                        break
    
    def on_confirm_clicked(self):
        """确认按钮点击事件"""
        # 执行回调函数
        if self.callback:
            self.callback()
        self.close_with_animation()


if __name__ == "__main__":
    # 测试URL处理器
    handler = URLHandler()
    
    if handler.has_url_command():
        print(f"URL命令: {handler.get_url_command()}")
    else:
        print("没有URL命令")
    
    # 显示可用界面
    interfaces = handler.get_available_interfaces()
    print("\n可用界面:")
    for path, name in interfaces.items():
        print(f"  {path}: {name}")
    
    # 显示URL示例
    examples = handler.generate_url_examples()
    print("\nURL使用示例:")
    for example in examples:
        print(f"  {example}")