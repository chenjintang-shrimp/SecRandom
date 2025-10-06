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
import asyncio
from pathlib import Path
from datetime import datetime
from loguru import logger
import winreg

from app.common.config import get_theme_icon, load_custom_font, is_dark_theme, VERSION
from app.common.path_utils import path_manager
from app.common.path_utils import open_file, ensure_dir

is_dark = is_dark_theme(qconfig)

class foundation_settingsCard(GroupHeaderCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("基础设置")
        self.setBorderRadius(8)
        self.settings_file = path_manager.get_settings_path()
        self.default_settings = {
            "check_on_startup": True,
            "self_starting_enabled": False,
            "main_window_focus_mode": 0,
            "main_window_focus_time": 0,
            "main_window_mode": 0,
            "settings_window_mode": 0,
            "topmost_switch": False,
            "url_protocol_enabled": False,
            "flash_window_auto_close": True,
            "flash_window_close_time": 2,
            "global_shortcut_enabled": False,
            "global_shortcut_target": 0,
            "global_shortcut_key": "",
            "local_pumping_shortcut_key": "",
            "local_reward_shortcut_key": "",
            "show_startup_window_switch": True,
        }

        self.self_starting_switch = SwitchButton()
        self.main_window_focus_comboBox = ComboBox()
        self.main_window_focus_time_comboBox = ComboBox()
        self.main_window_comboBox = ComboBox()
        self.settings_window_comboBox = ComboBox()

        # 开机自启动按钮
        self.self_starting_switch.setOnText("开启")
        self.self_starting_switch.setOffText("关闭")
        self.self_starting_switch.setFont(QFont(load_custom_font(), 12))
        self.self_starting_switch.checkedChanged.connect(self._on_startup_switch_changed)

        # 定时清理按钮
        self.cleanup_button = PushButton("设置定时清理")
        self.cleanup_button.clicked.connect(self.show_cleanup_dialog)
        self.cleanup_button.setFont(QFont(load_custom_font(), 12))

        # 设置主窗口不是焦点时关闭延迟
        self.main_window_focus_comboBox.addItems(
            ["不关闭", "直接关闭", "3秒后关闭", "5秒后关闭", "10秒后关闭", "15秒后关闭", "30秒后关闭", "1分钟后关闭",
             "2分钟后关闭", "3分钟后关闭", "5分钟后关闭", "10分钟后关闭", "30分钟后关闭", "45分钟后关闭", "1小时后关闭",
             "2小时后关闭", "3小时后关闭", "6小时后关闭", "12小时后关闭"])
        self.main_window_focus_comboBox.currentIndexChanged.connect(self.on_focus_mode_changed)
        self.main_window_focus_comboBox.setFont(QFont(load_custom_font(), 12))

        # 设置检测主窗口焦点时间
        self.main_window_focus_time_comboBox.addItems(
            ["不检测", "1秒", "2秒", "3秒", "5秒", "10秒", "15秒", "30秒",
             "1分钟", "5分钟", "10分钟", "15分钟", "30分钟",
             "1小时", "2小时", "3小时", "6小时"])
        self.main_window_focus_time_comboBox.currentIndexChanged.connect(self.on_focus_time_changed)
        self.main_window_focus_time_comboBox.setFont(QFont(load_custom_font(), 12))

        # 主窗口窗口显示位置下拉框
        self.main_window_comboBox.addItems(["居中", "居中向下3/5"])
        self.main_window_comboBox.currentIndexChanged.connect(self.save_settings)
        self.main_window_comboBox.setFont(QFont(load_custom_font(), 12))

        # 设置窗口显示位置下拉框
        self.settings_window_comboBox.addItems(["居中", "居中向下3/5"])
        self.settings_window_comboBox.currentIndexChanged.connect(self.save_settings)
        self.settings_window_comboBox.setFont(QFont(load_custom_font(), 12))

        # 添加组件到分组中
        self.check_on_startup = SwitchButton()
        self.check_on_startup.setOnText("开启")
        self.check_on_startup.setOffText("关闭")
        self.check_on_startup.setFont(QFont(load_custom_font(), 12))
        self.check_on_startup.checkedChanged.connect(self.save_settings)
        
        # 浮窗
        # 闪抽窗口自动关闭开关
        self.flash_window_auto_close_switch = SwitchButton()
        self.flash_window_auto_close_switch.setOnText("开启")
        self.flash_window_auto_close_switch.setOffText("关闭")
        self.flash_window_auto_close_switch.setFont(QFont(load_custom_font(), 12))
        self.flash_window_auto_close_switch.checkedChanged.connect(self.save_settings)

        # 闪抽窗口自动关闭时间设置
        self.flash_window_close_time_comboBox = ComboBox()
        self.flash_window_close_time_comboBox.addItems(["1秒", "2秒", "3秒", "5秒", "10秒", "15秒", "30秒"])
        self.flash_window_close_time_comboBox.currentIndexChanged.connect(self.save_settings)
        self.flash_window_close_time_comboBox.setFont(QFont(load_custom_font(), 12))

        # 主界面置顶功能
        self.topmost_switch = SwitchButton()
        self.topmost_switch.setOnText("置顶")
        self.topmost_switch.setOffText("取消置顶")
        self.topmost_switch.setFont(QFont(load_custom_font(), 12))
        self.topmost_switch.checkedChanged.connect(self.save_settings)
        
        # URL协议注册功能
        self.url_protocol_switch = SwitchButton()
        self.url_protocol_switch.setOnText("已注册")
        self.url_protocol_switch.setOffText("未注册")
        self.url_protocol_switch.setFont(QFont(load_custom_font(), 12))
        self.url_protocol_switch.checkedChanged.connect(self.toggle_url_protocol)

        # 设置是否显示启动窗口
        self.show_startup_window_switch = SwitchButton()
        self.show_startup_window_switch.setOnText("开启")
        self.show_startup_window_switch.setOffText("关闭")
        self.show_startup_window_switch.setFont(QFont(load_custom_font(), 12))
        self.show_startup_window_switch.checkedChanged.connect(self.save_settings)

        # 快捷键设置功能
        # 全局快捷键开关
        self.global_shortcut_switch = SwitchButton()
        self.global_shortcut_switch.setOnText("开启")
        self.global_shortcut_switch.setOffText("关闭")
        self.global_shortcut_switch.setFont(QFont(load_custom_font(), 12))
        self.global_shortcut_switch.checkedChanged.connect(self.save_settings)
        
        # 全局快捷键目标选择下拉框
        self.global_shortcut_target_comboBox = ComboBox()
        self.global_shortcut_target_comboBox.addItems(["点名界面", "闪抽界面", "抽奖界面"])
        self.global_shortcut_target_comboBox.setFont(QFont(load_custom_font(), 12))
        self.global_shortcut_target_comboBox.currentIndexChanged.connect(self.save_settings)
        
        # 全局快捷键设置按钮
        self.global_shortcut_button = PushButton("设置快捷键")
        self.global_shortcut_button.setFont(QFont(load_custom_font(), 12))
        self.global_shortcut_button.clicked.connect(self.set_global_shortcut)
        
        # 全局快捷键清除按钮
        self.global_shortcut_clear_button = PushButton("清除")
        self.global_shortcut_clear_button.setFont(QFont(load_custom_font(), 12))
        self.global_shortcut_clear_button.clicked.connect(self.clear_global_shortcut)
        
        # 全局快捷键显示标签
        self.global_shortcut_label = BodyLabel("未设置")
        self.global_shortcut_label.setFont(QFont(load_custom_font(), 12))
        
        # 创建水平布局来容纳按钮和标签
        self.global_shortcut_layout = QHBoxLayout()
        self.global_shortcut_layout.addWidget(self.global_shortcut_button)
        self.global_shortcut_layout.addWidget(self.global_shortcut_label)
        self.global_shortcut_layout.addWidget(self.global_shortcut_clear_button)
        self.global_shortcut_layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建容器widget来包含布局
        self.global_shortcut_widget = QWidget()
        self.global_shortcut_widget.setLayout(self.global_shortcut_layout)
        
        # 局部快捷键设置 - 点名操作
        self.local_pumping_shortcut_button = PushButton("设置点名快捷键")
        self.local_pumping_shortcut_button.setFont(QFont(load_custom_font(), 12))
        self.local_pumping_shortcut_button.clicked.connect(self.set_pumping_shortcut)
        
        # 点名快捷键清除按钮
        self.local_pumping_shortcut_clear_button = PushButton("清除")
        self.local_pumping_shortcut_clear_button.setFont(QFont(load_custom_font(), 12))
        self.local_pumping_shortcut_clear_button.clicked.connect(self.clear_pumping_shortcut)
        
        # 点名快捷键显示标签
        self.local_pumping_shortcut_label = BodyLabel("未设置")
        self.local_pumping_shortcut_label.setFont(QFont(load_custom_font(), 12))
        
        # 创建水平布局来容纳按钮和标签
        self.local_pumping_shortcut_layout = QHBoxLayout()
        self.local_pumping_shortcut_layout.addWidget(self.local_pumping_shortcut_button)
        self.local_pumping_shortcut_layout.addWidget(self.local_pumping_shortcut_label)
        self.local_pumping_shortcut_layout.addWidget(self.local_pumping_shortcut_clear_button)
        self.local_pumping_shortcut_layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建容器widget来包含布局
        self.local_pumping_shortcut_widget = QWidget()
        self.local_pumping_shortcut_widget.setLayout(self.local_pumping_shortcut_layout)
        
        # 局部快捷键设置 - 抽奖操作
        self.local_reward_shortcut_button = PushButton("设置抽奖快捷键")
        self.local_reward_shortcut_button.setFont(QFont(load_custom_font(), 12))
        self.local_reward_shortcut_button.clicked.connect(self.set_reward_shortcut)
        
        # 抽奖快捷键清除按钮
        self.local_reward_shortcut_clear_button = PushButton("清除")
        self.local_reward_shortcut_clear_button.setFont(QFont(load_custom_font(), 12))
        self.local_reward_shortcut_clear_button.clicked.connect(self.clear_reward_shortcut)
        
        # 抽奖快捷键显示标签
        self.local_reward_shortcut_label = BodyLabel("未设置")
        self.local_reward_shortcut_label.setFont(QFont(load_custom_font(), 12))
        
        # 创建水平布局来容纳按钮和标签
        self.local_reward_shortcut_layout = QHBoxLayout()
        self.local_reward_shortcut_layout.addWidget(self.local_reward_shortcut_button)
        self.local_reward_shortcut_layout.addWidget(self.local_reward_shortcut_label)
        self.local_reward_shortcut_layout.addWidget(self.local_reward_shortcut_clear_button)
        self.local_reward_shortcut_layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建容器widget来包含布局
        self.local_reward_shortcut_widget = QWidget()
        self.local_reward_shortcut_widget.setLayout(self.local_reward_shortcut_layout)


        # 系统功能设置
        self.addGroup(get_theme_icon("ic_fluent_arrow_sync_20_filled"), "更新设置", "软件启动时自动检查并提示可用更新", self.check_on_startup)
        self.addGroup(get_theme_icon("ic_fluent_branch_compare_20_filled"), "开机自启", "系统开机时自动运行SecRandom(启用后将默认隐藏主窗口)", self.self_starting_switch)
        self.addGroup(get_theme_icon("ic_fluent_branch_fork_link_20_filled"), "URL协议注册", "注册SecRandom协议，支持通过URL链接快速启动特定功能", self.url_protocol_switch)
        
        # 显示启动窗口
        self.addGroup(get_theme_icon("ic_fluent_branch_fork_link_20_filled"), "显示启动窗口", "系统开机时自动运行SecRandom(启用后将默认隐藏主窗口)", self.show_startup_window_switch)
        
        # 快捷键设置
        self.addGroup(get_theme_icon("ic_fluent_window_ad_20_filled"), "全局快捷键", "启用全局快捷键功能，快速访问指定界面", self.global_shortcut_switch)
        self.addGroup(get_theme_icon("ic_fluent_window_ad_20_filled"), "快捷键目标", "选择全局快捷键触发时打开的界面", self.global_shortcut_target_comboBox)
        self.addGroup(get_theme_icon("ic_fluent_window_ad_20_filled"), "全局快捷键", "设置用于快速打开指定界面的全局快捷键", self.global_shortcut_widget)
        self.addGroup(get_theme_icon("ic_fluent_window_ad_20_filled"), "点名快捷键", "设置点名操作的开始/停止快捷键", self.local_pumping_shortcut_widget)
        self.addGroup(get_theme_icon("ic_fluent_window_ad_20_filled"), "抽奖快捷键", "设置抽奖操作的开始/停止快捷键", self.local_reward_shortcut_widget)
        
        # 窗口位置设置
        self.addGroup(get_theme_icon("ic_fluent_window_location_target_20_filled"), "主窗口位置", "设置主窗口在屏幕上的默认显示位置", self.main_window_comboBox)
        self.addGroup(get_theme_icon("ic_fluent_window_location_target_20_filled"), "设置窗口位置", "设置设置窗口在屏幕上的默认显示位置", self.settings_window_comboBox)
        self.addGroup(get_theme_icon("ic_fluent_window_inprivate_20_filled"), "主窗口置顶", "使主窗口始终显示在其他窗口之上(需重新打开窗口生效)", self.topmost_switch)
        
        # 闪抽设置
        self.addGroup(get_theme_icon("ic_fluent_window_inprivate_20_filled"), "闪抽自动关闭", "启用后闪抽窗口将在完成操作后自动关闭", self.flash_window_auto_close_switch)
        self.addGroup(get_theme_icon("ic_fluent_window_inprivate_20_filled"), "闪抽关闭时间", "设置闪抽窗口自动关闭的延迟时间", self.flash_window_close_time_comboBox)

        # 智能检测设置
        self.addGroup(get_theme_icon("ic_fluent_layout_row_two_focus_top_settings_20_filled"), "窗口焦点延迟", "设置主窗口失去焦点后的自动关闭延迟时间", self.main_window_focus_comboBox)
        self.addGroup(get_theme_icon("ic_fluent_timer_20_filled"), "焦点检测间隔", "配置主窗口焦点状态的检测频率", self.main_window_focus_time_comboBox)
        
        # 数据管理设置
        self.addGroup(get_theme_icon("ic_fluent_clock_20_filled"), "定时清理记录", "配置自动清理抽取记录的时间间隔", self.cleanup_button)
        
        # 定时检查清理
        self.cleanup_timer = QTimer(self)
        self.cleanup_timer.timeout.connect(self.check_cleanup_time)
        self.cleanup_timer.start(1000)

        self.load_settings()
        self.save_settings()

    def on_pumping_floating_switch_changed(self, checked):
        self.save_settings()

    def on_focus_mode_changed(self):
        self.save_settings()  # 先保存设置
        index = self.main_window_focus_comboBox.currentIndex()
        main_window = None
        for widget in QApplication.topLevelWidgets():
            if hasattr(widget, 'update_focus_mode'):  # 通过特征识别主窗口
                main_window = widget
                break
        if main_window:
            main_window.update_focus_mode(index)

    def on_focus_time_changed(self):
        self.save_settings()  # 先保存设置
        index = self.main_window_focus_time_comboBox.currentIndex()
        main_window = None
        for widget in QApplication.topLevelWidgets():
            if hasattr(widget, 'update_focus_time'):  # 通过特征识别主窗口
                main_window = widget
                break
        if main_window:
            main_window.update_focus_time(index)

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

        self.save_settings()

        try:
            # 读取设置文件
            from app.common.path_utils import path_manager
            settings_file = path_manager.get_settings_path('Settings.json')
            
            # 直接读取文件
            with open_file(settings_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)
            
            foundation_settings = settings.get('foundation', {})
            self_starting_enabled = foundation_settings.get('self_starting_enabled', False)

            # 处理Windows系统的启动文件夹操作
            if platform.system() == 'Windows':
                # Windows系统：使用启动文件夹快捷方式
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
                        self.self_starting_switch.setChecked(self_starting_enabled)
                    except Exception as e:
                        logger.error(f"创建快捷方式失败: {e}")
                else:
                    try:
                        if path_manager.file_exists(shortcut_path):
                            os.remove(shortcut_path)
                            logger.success("开机自启动取消成功")
                            self.self_starting_switch.setChecked(self_starting_enabled)
                        else:
                            logger.info("开机自启动项不存在，无需取消")
                    except Exception as e:
                        logger.error(f"删除快捷方式失败: {e}")
            else:
                # 不支持的系统
                self.self_starting_switch.setChecked(self.default_settings["self_starting_enabled"])
                logger.error(f"不支持的操作系统: {platform.system()}")
                return

        except json.JSONDecodeError as e:
            logger.error(f"设置文件格式错误: {e}")
        except Exception as e:
            logger.error(f"读取设置文件时出错: {e}")

    def _on_startup_switch_changed(self):
        """处理开机自启动开关变化的包装器方法"""
        # 创建一个任务来运行异步的setting_startup方法
        self.setting_startup()

    def load_settings(self):
        try:
            if path_manager.file_exists(self.settings_file):
                with open_file(self.settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    foundation_settings = settings.get("foundation", {})
                    
                    # 优先使用保存的文字选项
                    self_starting_enabled = foundation_settings.get("self_starting_enabled", self.default_settings["self_starting_enabled"])
                        
                    main_window_mode = foundation_settings.get("main_window_mode", self.default_settings["main_window_mode"])
                    if main_window_mode < 0 or main_window_mode >= self.main_window_comboBox.count():
                        # 如果索引值无效，则使用默认值
                        main_window_mode = self.default_settings["main_window_mode"]

                    main_window_focus_mode = foundation_settings.get("main_window_focus_mode", self.default_settings["main_window_focus_mode"])
                    if main_window_focus_mode < 0 or main_window_focus_mode >= self.main_window_focus_comboBox.count():
                        # 如果索引值无效，则使用默认值
                        main_window_focus_mode = self.default_settings["main_window_focus_mode"]

                    main_window_focus_time = foundation_settings.get("main_window_focus_time", self.default_settings["main_window_focus_time"])
                    if main_window_focus_time < 0 or main_window_focus_time >= self.main_window_focus_time_comboBox.count():
                        # 如果索引值无效，则使用默认值
                        main_window_focus_time = self.default_settings["main_window_focus_time"]

                    settings_window_mode = foundation_settings.get("settings_window_mode", self.default_settings["settings_window_mode"])
                    if settings_window_mode < 0 or settings_window_mode >= self.settings_window_comboBox.count():
                        # 如果索引值无效，则使用默认值
                        settings_window_mode = self.default_settings["settings_window_mode"]

                    check_on_startup = foundation_settings.get("check_on_startup", self.default_settings["check_on_startup"])

                    topmost_switch = foundation_settings.get("topmost_switch", self.default_settings["topmost_switch"])

                    url_protocol_enabled = foundation_settings.get("url_protocol_enabled", self.default_settings["url_protocol_enabled"])

                    # 闪抽窗口自动关闭设置
                    flash_window_auto_close = foundation_settings.get("flash_window_auto_close", self.default_settings["flash_window_auto_close"])
                    flash_window_close_time = foundation_settings.get("flash_window_close_time", self.default_settings["flash_window_close_time"])
                    if flash_window_close_time < 0 or flash_window_close_time >= self.flash_window_close_time_comboBox.count():
                        # 如果索引值无效，则使用默认值
                        flash_window_close_time = self.default_settings["flash_window_close_time"]
                    
                    # 快捷键设置
                    global_shortcut_enabled = foundation_settings.get("global_shortcut_enabled", self.default_settings["global_shortcut_enabled"])
                    global_shortcut_target = foundation_settings.get("global_shortcut_target", self.default_settings["global_shortcut_target"])
                    if global_shortcut_target < 0 or global_shortcut_target >= self.global_shortcut_target_comboBox.count():
                        # 如果索引值无效，则使用默认值
                        global_shortcut_target = self.default_settings["global_shortcut_target"]
                    global_shortcut_key = foundation_settings.get("global_shortcut_key", self.default_settings["global_shortcut_key"])
                    local_pumping_shortcut_key = foundation_settings.get("local_pumping_shortcut_key", self.default_settings["local_pumping_shortcut_key"])
                    local_reward_shortcut_key = foundation_settings.get("local_reward_shortcut_key", self.default_settings["local_reward_shortcut_key"])

                    # 显示启动窗口
                    show_startup_window_switch = foundation_settings.get("show_startup_window_switch", self.default_settings["show_startup_window_switch"])
                    
                    self.self_starting_switch.setChecked(self_starting_enabled)
                    self.main_window_focus_comboBox.setCurrentIndex(main_window_focus_mode)
                    self.main_window_focus_time_comboBox.setCurrentIndex(main_window_focus_time)
                    self.main_window_comboBox.setCurrentIndex(main_window_mode)
                    self.settings_window_comboBox.setCurrentIndex(settings_window_mode)
                    self.check_on_startup.setChecked(check_on_startup)
                    self.topmost_switch.setChecked(topmost_switch)
                    self.url_protocol_switch.setChecked(url_protocol_enabled)
                    self.flash_window_auto_close_switch.setChecked(flash_window_auto_close)
                    self.flash_window_close_time_comboBox.setCurrentIndex(flash_window_close_time)
                    self.show_startup_window_switch.setChecked(show_startup_window_switch)
                    
                    # 更新快捷键设置
                    self.global_shortcut_switch.setChecked(global_shortcut_enabled)
                    self.global_shortcut_target_comboBox.setCurrentIndex(global_shortcut_target)
                    self.global_shortcut_label.setText(global_shortcut_key if global_shortcut_key else "未设置")
                    self.local_pumping_shortcut_label.setText(local_pumping_shortcut_key if local_pumping_shortcut_key else "未设置")
                    self.local_reward_shortcut_label.setText(local_reward_shortcut_key if local_reward_shortcut_key else "未设置")
                    
                    # 注册快捷键
                    if global_shortcut_enabled and global_shortcut_key:
                        self.register_global_shortcut(global_shortcut_key)
                    self.register_local_shortcuts()
            else:
                logger.error(f"设置文件不存在: {self.settings_file}")
                self.self_starting_switch.setChecked(self.default_settings["self_starting_enabled"])
                self.main_window_focus_comboBox.setCurrentIndex(self.default_settings["main_window_focus_mode"])
                self.main_window_focus_time_comboBox.setCurrentIndex(self.default_settings["main_window_focus_time"])
                self.main_window_comboBox.setCurrentIndex(self.default_settings["main_window_mode"])
                self.settings_window_comboBox.setCurrentIndex(self.default_settings["settings_window_mode"])
                self.check_on_startup.setChecked(self.default_settings["check_on_startup"])
                self.topmost_switch.setChecked(self.default_settings["topmost_switch"])
                self.url_protocol_switch.setChecked(self.default_settings["url_protocol_enabled"])
                self.flash_window_auto_close_switch.setChecked(self.default_settings["flash_window_auto_close"])
                self.flash_window_close_time_comboBox.setCurrentIndex(self.default_settings["flash_window_close_time"])
                self.show_startup_window_switch.setChecked(self.default_settings["show_startup_window_switch"])
                
                # 加载快捷键设置的默认值
                self.global_shortcut_switch.setChecked(self.default_settings["global_shortcut_enabled"])
                self.global_shortcut_target_comboBox.setCurrentIndex(self.default_settings["global_shortcut_target"])
                self.global_shortcut_label.setText(self.default_settings["global_shortcut_key"] if self.default_settings["global_shortcut_key"] else "未设置")
                self.local_pumping_shortcut_label.setText(self.default_settings["local_pumping_shortcut_key"] if self.default_settings["local_pumping_shortcut_key"] else "未设置")
                self.local_reward_shortcut_label.setText(self.default_settings["local_reward_shortcut_key"] if self.default_settings["local_reward_shortcut_key"] else "未设置")
                self.save_settings()
        except Exception as e:
            logger.error(f"加载设置时出错: {e}")
            self.self_starting_switch.setChecked(self.default_settings["self_starting_enabled"])
            self.main_window_focus_comboBox.setCurrentIndex(self.default_settings["main_window_focus_mode"])
            self.main_window_focus_time_comboBox.setCurrentIndex(self.default_settings["main_window_focus_time"])
            self.main_window_comboBox.setCurrentIndex(self.default_settings["main_window_mode"])
            self.settings_window_comboBox.setCurrentIndex(self.default_settings["settings_window_mode"])
            self.check_on_startup.setChecked(self.default_settings["check_on_startup"])
            self.topmost_switch.setChecked(self.default_settings["topmost_switch"])
            self.url_protocol_switch.setChecked(self.default_settings["url_protocol_enabled"])
            self.flash_window_auto_close_switch.setChecked(self.default_settings["flash_window_auto_close"])
            self.flash_window_close_time_comboBox.setCurrentIndex(self.default_settings["flash_window_close_time"])
            self.show_startup_window_switch.setChecked(self.default_settings["show_startup_window_switch"])
            
            # 加载快捷键设置的默认值
            self.global_shortcut_switch.setChecked(self.default_settings["global_shortcut_enabled"])
            self.global_shortcut_target_comboBox.setCurrentIndex(self.default_settings["global_shortcut_target"])
            self.global_shortcut_label.setText(self.default_settings["global_shortcut_key"] if self.default_settings["global_shortcut_key"] else "未设置")
            self.local_pumping_shortcut_label.setText(self.default_settings["local_pumping_shortcut_key"] if self.default_settings["local_pumping_shortcut_key"] else "未设置")
            self.local_reward_shortcut_label.setText(self.default_settings["local_reward_shortcut_key"] if self.default_settings["local_reward_shortcut_key"] else "未设置")
            self.save_settings()
            
            # 注册快捷键
            if self.global_shortcut_switch.isChecked() and self.global_shortcut_label.text() != "未设置":
                self.register_global_shortcut(self.global_shortcut_label.text())
            self.register_local_shortcuts()

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
        if "foundation" not in existing_settings:
            existing_settings["foundation"] = {}
            
        foundation_settings = existing_settings["foundation"]
        # 删除保存文字选项的代码
        foundation_settings["self_starting_enabled"] = self.self_starting_switch.isChecked()
        foundation_settings["main_window_focus_mode"] = self.main_window_focus_comboBox.currentIndex()
        foundation_settings["main_window_focus_time"] = self.main_window_focus_time_comboBox.currentIndex()
        foundation_settings["main_window_mode"] = self.main_window_comboBox.currentIndex()
        foundation_settings["settings_window_mode"] = self.settings_window_comboBox.currentIndex()
        foundation_settings["check_on_startup"] = self.check_on_startup.isChecked()
        foundation_settings["topmost_switch"] = self.topmost_switch.isChecked()
        foundation_settings["url_protocol_enabled"] = self.url_protocol_switch.isChecked()
        foundation_settings["flash_window_auto_close"] = self.flash_window_auto_close_switch.isChecked()
        foundation_settings["flash_window_close_time"] = self.flash_window_close_time_comboBox.currentIndex()
        # 显示启动窗口
        foundation_settings["show_startup_window_switch"] = self.show_startup_window_switch.isChecked()
        
        # 保存快捷键设置
        foundation_settings["global_shortcut_enabled"] = self.global_shortcut_switch.isChecked()
        foundation_settings["global_shortcut_target"] = self.global_shortcut_target_comboBox.currentIndex()
        foundation_settings["global_shortcut_key"] = self.global_shortcut_label.text() if self.global_shortcut_label.text() != "未设置" else ""
        foundation_settings["local_pumping_shortcut_key"] = self.local_pumping_shortcut_label.text() if self.local_pumping_shortcut_label.text() != "未设置" else ""
        foundation_settings["local_reward_shortcut_key"] = self.local_reward_shortcut_label.text() if self.local_reward_shortcut_label.text() != "未设置" else ""
        
        os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
        with open_file(self.settings_file, 'w', encoding='utf-8') as f:
            json.dump(existing_settings, f, indent=4)
    
    def show_cleanup_dialog(self):
        dialog = CleanupTimeDialog(self)
        if dialog.exec():
            cleanup_times = dialog.textEdit.toPlainText()
            try:
                # 确保Settings目录存在
                from app.common.path_utils import path_manager
                cleanup_times_file = path_manager.get_settings_path('CleanupTimes.json')
                os.makedirs(os.path.dirname(cleanup_times_file), exist_ok=True)
                
                settings = {}
                if path_manager.file_exists(cleanup_times_file):
                    with open_file(cleanup_times_file, 'r', encoding='utf-8') as f:
                        settings = json.load(f)
                
                # 处理多个时间输入
                time_list = [time.strip() for time in cleanup_times.split('\n') if time.strip()]
                
                # 清空现有设置
                if 'cleanuptimes' in settings:
                    settings['cleanuptimes'] = {}
                
                # 验证并收集所有有效时间
                valid_times = []
                for time_str in time_list:
                    try:
                        # 验证时间格式
                        time_str = time_str.replace('：', ':')  # 中文冒号转英文
                        
                        # 支持HH:MM或HH:MM:SS格式
                        parts = time_str.split(':')
                        if len(parts) == 2:
                            hours, minutes = parts
                            seconds = '00'
                            time_str = f"{hours}:{minutes}:{seconds}"  # 转换为完整格式
                        elif len(parts) == 3:
                            hours, minutes, seconds = parts
                        else:
                            raise ValueError(f"时间格式应为'HH:MM'或'HH:MM:SS'，当前输入: {time_str}")
                        
                        # 确保所有部分都存在
                        if not all([hours, minutes, seconds]):
                            raise ValueError(f"时间格式不完整，应为'HH:MM'或'HH:MM:SS'，当前输入: {time_str}")
                            
                        hours = int(hours.strip())
                        minutes = int(minutes.strip())
                        seconds = int(seconds.strip())
                        
                        if hours < 0 or hours > 23:
                            raise ValueError(f"小时数必须在0-23之间，当前输入: {hours}")
                        if minutes < 0 or minutes > 59:
                            raise ValueError(f"分钟数必须在0-59之间，当前输入: {minutes}")
                        if seconds < 0 or seconds > 59:
                            raise ValueError(f"秒数必须在0-59之间，当前输入: {seconds}")
                        
                        valid_times.append(time_str)
                    except Exception as e:
                        logger.error(f"时间格式验证失败: {str(e)}")
                        continue
                
                # 按时间排序
                valid_times.sort(key=lambda x: tuple(map(int, x.split(':'))))
                
                # 重新编号并保存
                for idx, time_str in enumerate(valid_times, 1):
                    settings.setdefault('cleanuptimes', {})[str(idx)] = time_str
                
                with open_file(cleanup_times_file, 'w', encoding='utf-8') as f:
                    json.dump(settings, f, ensure_ascii=False, indent=4)
                    logger.info(f"成功保存{len(time_list)}个定时清理时间设置")
                    InfoBar.success(
                        title='设置成功',
                        content=f"成功保存{len(time_list)}个定时清理时间!",
                        orient=Qt.Horizontal,
                        isClosable=True,
                        position=InfoBarPosition.TOP,
                        duration=3000,
                        parent=self
                    )
            except Exception as e:
                logger.error(f"保存定时清理时间失败: {str(e)}")
                InfoBar.error(
                    title='设置失败',
                    content=f"保存定时清理时间失败: {str(e)}",
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=3000,
                    parent=self
                )
    
    def check_cleanup_time(self):
        try:
            current_time = QTime.currentTime().toString("HH:mm:ss")
            from app.common.path_utils import path_manager
            cleanup_times_file = path_manager.get_settings_path('CleanupTimes.json')
            if path_manager.file_exists(cleanup_times_file):
                with open_file(cleanup_times_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    # 检查所有设置的时间
                    foundation_times = settings.get('cleanuptimes', {})
                    for time_id, cleanup_time in foundation_times.items():
                        if cleanup_time and current_time == cleanup_time:
                            self.cleanup_temp_files()
                            InfoBar.success(
                                title='清理完成',
                                content=f"定时清理时间 {cleanup_time} 已触发，已清理抽取记录",
                                orient=Qt.Horizontal,
                                isClosable=True,
                                position=InfoBarPosition.TOP,
                                duration=3000,
                                parent=self
                            )
                            break
        except Exception as e:
            logger.error(f"检查定时清理时间时出错: {str(e)}")
    
    def cleanup_temp_files(self):
        try:
            temp_dir = path_manager.get_resource_path('Temp', '')
            if temp_dir.exists():
                for filename in temp_dir.iterdir():
                    if filename.suffix == ".json":
                        filename.unlink()
                        logger.info(f"已清理文件: {filename}")
        except Exception as e:
            logger.error(f"清理TEMP文件夹时出错: {str(e)}")
        
    def set_global_shortcut(self):
        """设置全局快捷键"""
        
        # 获取当前快捷键
        current_shortcut = self.global_shortcut_label.text() if self.global_shortcut_label.text() != "未设置" else ""
        
        # 创建一个对话框来捕获快捷键
        dialog = MessageBoxBase(self)
        dialog.setWindowTitle("设置抽奖快捷键")
        dialog.yesButton.setText("确定")
        dialog.cancelButton.setText("取消")
        
        # 创建垂直布局
        layout = QVBoxLayout()
        
        # 添加说明标签
        info_label = BodyLabel(f"当前快捷键: {current_shortcut if current_shortcut else '无'}\n请点击输入框后按下快捷键组合（如Ctrl+Alt+P）：")
        info_label.setFont(QFont(load_custom_font(), 12))
        layout.addWidget(info_label)
        
        # 添加快捷键输入框
        key_sequence_edit = QKeySequenceEdit()
        key_sequence_edit.setFont(QFont(load_custom_font(), 12))
        if current_shortcut:
            key_sequence_edit.setKeySequence(QKeySequence(current_shortcut))
        layout.addWidget(key_sequence_edit)
        
        dialog.viewLayout.addLayout(layout)
        
        # 设置对话框最小宽度
        dialog.widget.setMinimumWidth(300)
        
        # 显示为无模态窗口
        dialog.show()
        
        # 连接按钮信号
        def on_ok():
            key_sequence = key_sequence_edit.keySequence()
            if not key_sequence.isEmpty():
                captured_shortcut = key_sequence.toString()
                # 更新标签显示
                self.global_shortcut_label.setText(captured_shortcut)
                # 保存设置
                self.save_settings()
                
                # 注册全局快捷键
                self.register_global_shortcut(captured_shortcut)
                
                InfoBar.success(
                    title='设置成功',
                    content=f'全局快捷键已设置为: {captured_shortcut}',
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=3000,
                    parent=self
                )
            dialog.close()
        
        def on_cancel():
            dialog.close()
        
        dialog.yesButton.clicked.connect(on_ok)
        dialog.cancelButton.clicked.connect(on_cancel)
    
    def set_pumping_shortcut(self):
        """设置点名操作快捷键"""
        # 获取当前快捷键
        current_shortcut = self.local_pumping_shortcut_label.text() if self.local_pumping_shortcut_label.text() != "未设置" else ""
        
        # 创建一个对话框来捕获快捷键
        dialog = MessageBoxBase(self)
        dialog.setWindowTitle("设置点名快捷键")
        dialog.yesButton.setText("确定")
        dialog.cancelButton.setText("取消")
        
        # 创建垂直布局
        layout = QVBoxLayout()
        
        # 添加说明标签
        info_label = BodyLabel(f"当前快捷键: {current_shortcut if current_shortcut else '无'}\n请点击输入框后按下快捷键组合（如F1）：")
        info_label.setFont(QFont(load_custom_font(), 12))
        layout.addWidget(info_label)
        
        # 添加快捷键输入框
        key_sequence_edit = QKeySequenceEdit()
        key_sequence_edit.setFont(QFont(load_custom_font(), 12))
        if current_shortcut:
            key_sequence_edit.setKeySequence(QKeySequence(current_shortcut))
        layout.addWidget(key_sequence_edit)
        
        dialog.viewLayout.addLayout(layout)
        
        # 设置对话框最小宽度
        dialog.widget.setMinimumWidth(300)
        
        # 显示为无模态窗口
        dialog.show()
        
        # 连接按钮信号
        def on_ok():
            key_sequence = key_sequence_edit.keySequence()
            if not key_sequence.isEmpty():
                captured_shortcut = key_sequence.toString()
                # 更新标签显示
                self.local_pumping_shortcut_label.setText(captured_shortcut)
                # 保存设置
                self.save_settings()
                
                # 注册局部快捷键
                self.register_local_shortcuts()
                
                InfoBar.success(
                    title='设置成功',
                    content=f'点名快捷键已设置为: {captured_shortcut}',
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=3000,
                    parent=self
                )
            dialog.close()
        
        def on_cancel():
            dialog.close()
        
        dialog.yesButton.clicked.connect(on_ok)
        dialog.cancelButton.clicked.connect(on_cancel)
    
    def set_reward_shortcut(self):
        """设置抽奖操作快捷键"""
        # 获取当前快捷键
        current_shortcut = self.local_reward_shortcut_label.text() if self.local_reward_shortcut_label.text() != "未设置" else ""
        
        # 创建一个对话框来捕获快捷键
        dialog = MessageBoxBase(self)
        dialog.setWindowTitle("设置抽奖快捷键")
        dialog.yesButton.setText("确定")
        dialog.cancelButton.setText("取消")
        
        # 创建垂直布局
        layout = QVBoxLayout()
        
        # 添加说明标签
        info_label = BodyLabel(f"当前快捷键: {current_shortcut if current_shortcut else '无'}\n请点击输入框后按下快捷键组合（如F2）：")
        info_label.setFont(QFont(load_custom_font(), 12))
        layout.addWidget(info_label)
        
        # 添加快捷键输入框
        key_sequence_edit = QKeySequenceEdit()
        key_sequence_edit.setFont(QFont(load_custom_font(), 12))
        if current_shortcut:
            key_sequence_edit.setKeySequence(QKeySequence(current_shortcut))
        layout.addWidget(key_sequence_edit)
        
        dialog.viewLayout.addLayout(layout)
        
        # 设置对话框最小宽度
        dialog.widget.setMinimumWidth(300)
        
        # 显示为无模态窗口
        dialog.show()
        
        # 连接按钮信号
        def on_ok():
            key_sequence = key_sequence_edit.keySequence()
            if not key_sequence.isEmpty():
                captured_shortcut = key_sequence.toString()
                # 更新标签显示
                self.local_reward_shortcut_label.setText(captured_shortcut)
                # 保存设置
                self.save_settings()
                
                # 注册局部快捷键
                self.register_local_shortcuts()
                
                InfoBar.success(
                    title='设置成功',
                    content=f'抽奖快捷键已设置为: {captured_shortcut}',
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=3000,
                    parent=self
                )
            dialog.close()
        
        def on_cancel():
            dialog.close()
        
        dialog.yesButton.clicked.connect(on_ok)
        dialog.cancelButton.clicked.connect(on_cancel)
    
    def register_global_shortcut(self, shortcut):
        """注册全局快捷键"""
        try:
            # 导入keyboard库用于全局快捷键
            import keyboard
            
            # 如果之前有注册的快捷键，先取消注册
            if hasattr(self, '_current_global_shortcut') and self._current_global_shortcut:
                try:
                    keyboard.remove_hotkey(self._current_global_shortcut)
                except:
                    pass
            
            # 注册新的快捷键
            keyboard.add_hotkey(shortcut, self.trigger_global_shortcut)
            
            # 保存当前注册的快捷键
            self._current_global_shortcut = shortcut
            
            logger.info(f"注册全局快捷键成功: {shortcut}")
        except ImportError:
            logger.error("keyboard库未安装，无法注册全局快捷键")
            InfoBar.warning(
                title='缺少依赖',
                content='keyboard库未安装，无法注册全局快捷键，请安装keyboard库',
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )
        except Exception as e:
            logger.error(f"注册全局快捷键失败: {str(e)}")
            InfoBar.error(
                title='注册失败',
                content=f'全局快捷键注册失败: {str(e)}',
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )
    
    def trigger_global_shortcut(self):
        """触发全局快捷键"""
        if not self.global_shortcut_switch.isChecked():
            return
            
        # 获取目标界面
        target_index = self.global_shortcut_target_comboBox.currentIndex()
        
        # 根据目标索引打开对应界面
        try:
            # 获取主窗口
            main_window = None
            for widget in QApplication.topLevelWidgets():
                if hasattr(widget, 'toggle_window'):  # 通过特征识别主窗口
                    main_window = widget
                    break

            if not main_window:
                logger.error("未找到主窗口实例")
                return
            
            if target_index == 0:  # 点名界面
                # 打开点名界面
                logger.info("通过全局快捷键打开点名界面")
                # 使用QMetaObject.invokeMethod确保在主线程中执行UI操作
                QMetaObject.invokeMethod(main_window, "_show_pumping_interface_from_shortcut", Qt.QueuedConnection)

            elif target_index == 1:  # 闪抽界面
                # 打开闪抽界面
                logger.info("通过全局快捷键打开闪抽界面")
                # 使用QMetaObject.invokeMethod确保在主线程中执行UI操作
                QMetaObject.invokeMethod(main_window, "_show_direct_extraction_window_from_shortcut", Qt.QueuedConnection)

            elif target_index == 2:  # 抽奖界面
                # 打开抽奖界面
                logger.info("通过全局快捷键打开抽奖界面")
                # 使用QMetaObject.invokeMethod确保在主线程中执行UI操作
                QMetaObject.invokeMethod(main_window, "_show_reward_interface_from_shortcut", Qt.QueuedConnection)

        except Exception as e:
            logger.error(f"触发全局快捷键失败: {str(e)}")

    def register_local_shortcuts(self):
        """注册全局快捷键（点名和抽奖）"""
        try:
            # 导入keyboard库用于全局快捷键
            import keyboard
            
            # 获取点名和抽奖快捷键
            pumping_shortcut = self.local_pumping_shortcut_label.text()
            reward_shortcut = self.local_reward_shortcut_label.text()
            
            # 如果之前有注册的快捷键，先取消注册
            if hasattr(self, '_pumping_shortcut') and self._pumping_shortcut:
                try:
                    keyboard.remove_hotkey(self._pumping_shortcut)
                except:
                    pass
            
            if hasattr(self, '_reward_shortcut') and self._reward_shortcut:
                try:
                    keyboard.remove_hotkey(self._reward_shortcut)
                except:
                    pass
            
            # 注册点名快捷键
            if pumping_shortcut and pumping_shortcut != "未设置":
                keyboard.add_hotkey(pumping_shortcut, lambda: self.trigger_local_shortcut('pumping'))
                self._pumping_shortcut = pumping_shortcut
                logger.info(f"注册点名全局快捷键成功: {pumping_shortcut}")
            
            # 注册抽奖快捷键
            if reward_shortcut and reward_shortcut != "未设置":
                keyboard.add_hotkey(reward_shortcut, lambda: self.trigger_local_shortcut('reward'))
                self._reward_shortcut = reward_shortcut
                logger.info(f"注册抽奖全局快捷键成功: {reward_shortcut}")
                
        except ImportError:
            logger.error("keyboard库未安装，无法注册全局快捷键")
            InfoBar.warning(
                title='缺少依赖',
                content='keyboard库未安装，无法注册全局快捷键，请安装keyboard库',
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )
        except Exception as e:
            logger.error(f"注册全局快捷键失败: {str(e)}")
            InfoBar.error(
                title='注册失败',
                content=f'全局快捷键注册失败: {str(e)}',
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )
    
    def trigger_local_shortcut(self, shortcut_type):
        """触发全局快捷键（点名和抽奖）"""
        if not self.global_shortcut_switch.isChecked():
            return

        try:
            # 获取主窗口
            main_window = None
            for widget in QApplication.topLevelWidgets():
                if hasattr(widget, 'toggle_window'):  # 通过特征识别主窗口
                    main_window = widget
                    break

            if not main_window:
                logger.error("未找到主窗口实例")
                return
            
            if shortcut_type == 'pumping':
                # 触发点名操作
                logger.info("通过全局快捷键触发点名操作")
                
                # 使用QMetaObject.invokeMethod确保在主线程中执行UI操作
                QMetaObject.invokeMethod(main_window, "_trigger_pumping_from_shortcut", Qt.QueuedConnection)
                    
            elif shortcut_type == 'reward':
                # 触发抽奖操作
                logger.info("通过全局快捷键触发抽奖操作")
                
                # 使用QMetaObject.invokeMethod确保在主线程中执行UI操作
                QMetaObject.invokeMethod(main_window, "_trigger_reward_from_shortcut", Qt.QueuedConnection)
                    
        except Exception as e:
            logger.error(f"触发全局快捷键失败: {str(e)}")
    
    def clear_global_shortcut(self):
        """清除全局快捷键"""
        try:
            # 导入keyboard库用于全局快捷键
            import keyboard
            
            # 如果有注册的快捷键，先取消注册
            if hasattr(self, '_current_global_shortcut') and self._current_global_shortcut:
                try:
                    keyboard.remove_hotkey(self._current_global_shortcut)
                    self._current_global_shortcut = ""
                    logger.info("全局快捷键已清除")
                except Exception as e:
                    logger.error(f"清除全局快捷键失败: {str(e)}")
            
            # 更新标签显示
            self.global_shortcut_label.setText("未设置")
            
            # 保存设置
            self.save_settings()
            
            InfoBar.success(
                title='清除成功',
                content='全局快捷键已清除',
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )
        except ImportError:
            logger.error("keyboard库未安装，无法清除全局快捷键")
            InfoBar.warning(
                title='缺少依赖',
                content='keyboard库未安装，无法清除全局快捷键',
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )
        except Exception as e:
            logger.error(f"清除全局快捷键失败: {str(e)}")
            InfoBar.error(
                title='清除失败',
                content=f'清除全局快捷键失败: {str(e)}',
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )
    
    def clear_pumping_shortcut(self):
        """清除点名快捷键"""
        try:
            # 导入keyboard库用于全局快捷键
            import keyboard
            
            # 如果有注册的快捷键，先取消注册
            if hasattr(self, '_pumping_shortcut') and self._pumping_shortcut:
                try:
                    keyboard.remove_hotkey(self._pumping_shortcut)
                    self._pumping_shortcut = ""
                    logger.info("点名快捷键已清除")
                except Exception as e:
                    logger.error(f"清除点名快捷键失败: {str(e)}")
            
            # 更新标签显示
            self.local_pumping_shortcut_label.setText("未设置")
            
            # 保存设置
            self.save_settings()
            
            InfoBar.success(
                title='清除成功',
                content='点名快捷键已清除',
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )
        except ImportError:
            logger.error("keyboard库未安装，无法清除点名快捷键")
            InfoBar.warning(
                title='缺少依赖',
                content='keyboard库未安装，无法清除点名快捷键',
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )
        except Exception as e:
            logger.error(f"清除点名快捷键失败: {str(e)}")
            InfoBar.error(
                title='清除失败',
                content=f'清除点名快捷键失败: {str(e)}',
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )
    
    def clear_reward_shortcut(self):
        """清除抽奖快捷键"""
        try:
            # 导入keyboard库用于全局快捷键
            import keyboard
            
            # 如果有注册的快捷键，先取消注册
            if hasattr(self, '_reward_shortcut') and self._reward_shortcut:
                try:
                    keyboard.remove_hotkey(self._reward_shortcut)
                    self._reward_shortcut = ""
                    logger.info("抽奖快捷键已清除")
                except Exception as e:
                    logger.error(f"清除抽奖快捷键失败: {str(e)}")
            
            # 更新标签显示
            self.local_reward_shortcut_label.setText("未设置")
            
            # 保存设置
            self.save_settings()
            
            InfoBar.success(
                title='清除成功',
                content='抽奖快捷键已清除',
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )
        except ImportError:
            logger.error("keyboard库未安装，无法清除抽奖快捷键")
            InfoBar.warning(
                title='缺少依赖',
                content='keyboard库未安装，无法清除抽奖快捷键',
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )
        except Exception as e:
            logger.error(f"清除抽奖快捷键失败: {str(e)}")
            InfoBar.error(
                title='清除失败',
                content=f'清除抽奖快捷键失败: {str(e)}',
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )

    def toggle_url_protocol(self, enabled):
        """切换URL协议注册状态"""
        try:
            if enabled:
                success = self.register_url_protocol()
                if success:
                    logger.success("URL协议注册成功")
                    InfoBar.success(
                        title='注册成功',
                        content='SecRandom URL协议已成功注册，现在可以通过secrandom://链接启动程序',
                        orient=Qt.Horizontal,
                        isClosable=True,
                        position=InfoBarPosition.TOP,
                        duration=3000,
                        parent=self
                    )
                    self.save_settings()
                else:
                    self.url_protocol_switch.setChecked(False)
                    logger.error("URL协议注册失败")
                    
                    # 检查是否是权限问题
                    try:
                        import ctypes
                        if not ctypes.windll.shell32.IsUserAnAdmin():
                            # 不是管理员，提供更具体的错误信息
                            InfoBar.warning(
                                title='权限不足',
                                content='URL协议注册需要管理员权限，请以管理员身份运行程序',
                                orient=Qt.Horizontal,
                                isClosable=True,
                                position=InfoBarPosition.TOP,
                                duration=5000,
                                parent=self
                            )
                        else:
                            # 已经是管理员但仍然失败
                            InfoBar.error(
                                title='注册失败',
                                content='URL协议注册失败，即使以管理员权限运行也无法完成',
                                orient=Qt.Horizontal,
                                isClosable=True,
                                position=InfoBarPosition.TOP,
                                duration=5000,
                                parent=self
                            )
                    except Exception:
                        # 无法检查管理员权限
                        InfoBar.error(
                            title='注册失败',
                            content='URL协议注册失败，请检查权限设置',
                            orient=Qt.Horizontal,
                            isClosable=True,
                            position=InfoBarPosition.TOP,
                            duration=3000,
                            parent=self
                        )
                    
                    self.url_protocol_switch.setChecked(False)
                    self.save_settings()
            else:
                success = self.unregister_url_protocol()
                if success:
                    logger.success("URL协议注销成功")
                    InfoBar.success(
                        title='注销成功',
                        content='SecRandom URL协议已成功注销',
                        orient=Qt.Horizontal,
                        isClosable=True,
                        position=InfoBarPosition.TOP,
                        duration=3000,
                        parent=self
                    )
                else:
                    self.url_protocol_switch.setChecked(True)
                    logger.error("URL协议注销失败")
                    InfoBar.error(
                        title='注销失败',
                        content='URL协议注销失败，请检查权限设置',
                        orient=Qt.Horizontal,
                        isClosable=True,
                        position=InfoBarPosition.TOP,
                        duration=3000,
                        parent=self
                    )
        except Exception as e:
            logger.error(f"URL协议操作失败: {str(e)}")
            InfoBar.error(
                title='操作失败',
                content=f'URL协议操作失败: {str(e)}',
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )
    
    def register_url_protocol(self):
        """注册SecRandom URL协议"""
        try:
            import sys
            import os
            
            # 获取当前程序路径
            executable = sys.executable
            if not executable:
                logger.error("无法获取可执行文件路径")
                return False
            
            if platform.system() == "Windows":
                # Windows平台使用注册表
                # 构建命令行参数，包含URL处理
                command = f'"{executable}" --url="%1"'
                
                # 注册URL协议到注册表
                protocol_key = "secrandom"
                
                # 尝试以管理员权限注册URL协议
                try:
                    # 创建协议主键
                    with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, protocol_key) as key:
                        winreg.SetValue(key, None, winreg.REG_SZ, "URL:SecRandom Protocol")
                        winreg.SetValueEx(key, "URL Protocol", 0, winreg.REG_SZ, "")
                    
                    # 创建默认图标
                    with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, f"{protocol_key}\\DefaultIcon") as key:
                        winreg.SetValue(key, None, winreg.REG_SZ, executable)
                    
                    # 创建shell\open\command
                    with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, f"{protocol_key}\\shell\\open\\command") as key:
                        winreg.SetValue(key, None, winreg.REG_SZ, command)
                    
                    logger.info(f"URL协议注册成功: {protocol_key}")
                    return True
                except PermissionError as e:
                    logger.error(f"权限不足，无法注册URL协议: {str(e)}")
                    # 提示用户需要管理员权限
                    try:
                        import ctypes
                        if ctypes.windll.shell32.IsUserAnAdmin():
                            # 已经是管理员，但仍然失败
                            logger.error("即使以管理员权限运行，URL协议注册仍然失败")
                            return False
                        else:
                            # 不是管理员，提示用户
                            logger.error("需要管理员权限才能注册URL协议")
                            return False
                    except Exception:
                        logger.error("无法检查管理员权限")
                        return False
                except Exception as e:
                    logger.error(f"注册URL协议时发生未知错误: {str(e)}")
                    return False
            
        except Exception as e:
            logger.error(f"注册URL协议失败: {str(e)}")
            return False
    
    def unregister_url_protocol(self):
        """注销SecRandom URL协议"""
        try:
            if platform.system() == "Windows":
                protocol_key = "secrandom"
                
                # 删除注册表项
                try:
                    winreg.DeleteKey(winreg.HKEY_CLASSES_ROOT, f"{protocol_key}\\shell\\open\\command")
                    winreg.DeleteKey(winreg.HKEY_CLASSES_ROOT, f"{protocol_key}\\shell\\open")
                    winreg.DeleteKey(winreg.HKEY_CLASSES_ROOT, f"{protocol_key}\\shell")
                    winreg.DeleteKey(winreg.HKEY_CLASSES_ROOT, f"{protocol_key}\\DefaultIcon")
                    winreg.DeleteKey(winreg.HKEY_CLASSES_ROOT, protocol_key)
                except Exception:
                    # 如果键不存在，忽略错误
                    pass
                
                logger.info(f"URL协议注销成功: {protocol_key}")
                return True
            
        except Exception as e:
            logger.error(f"注销URL协议失败: {str(e)}")
            return False
    
    def is_url_protocol_registered(self):
        """检查URL协议是否已注册"""
        try:
            if platform.system() == "Windows":
                protocol_key = "secrandom"
                with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, protocol_key) as key:
                    return True
        except Exception:
            return False
    
def register_url_protocol_on_startup():
    """在应用程序启动时自动注册URL协议
    
    该函数会在应用程序启动时自动调用，尝试注册SecRandom URL协议。
    如果注册失败（通常是由于权限不足），会静默失败，不会影响程序正常启动。
    """
    try:
        import sys
        import os
        import platform
        import winreg
        
        # 获取当前程序路径
        executable = sys.executable
        if not executable:
            logger.error("无法获取可执行文件路径")
            return False
        
        if platform.system() == "Windows":
            # Windows平台使用注册表
            # 构建命令行参数，包含URL处理
            command = f'"{executable}" --url="%1"'
            
            # 注册URL协议到注册表
            protocol_key = "secrandom"
            
            # 检查是否已经注册
            try:
                with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, protocol_key):
                    # 如果能打开键，说明已经注册
                    logger.info(f"URL协议已注册: {protocol_key}")
                    return True
            except Exception:
                # 键不存在，需要注册
                pass
            
            # 尝试注册URL协议
            try:
                # 创建协议主键
                with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, protocol_key) as key:
                    winreg.SetValue(key, None, winreg.REG_SZ, "URL:SecRandom Protocol")
                    winreg.SetValueEx(key, "URL Protocol", 0, winreg.REG_SZ, "")
                
                # 创建默认图标
                with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, f"{protocol_key}\\DefaultIcon") as key:
                    winreg.SetValue(key, None, winreg.REG_SZ, executable)
                
                # 创建shell\open\command
                with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, f"{protocol_key}\\shell\\open\\command") as key:
                    winreg.SetValue(key, None, winreg.REG_SZ, command)
                
                logger.info(f"URL协议注册成功: {protocol_key}")
                return True
            except PermissionError as e:
                logger.error(f"权限不足，无法注册URL协议: {str(e)}")
                return False
            except Exception as e:
                logger.error(f"注册URL协议时发生未知错误: {str(e)}")
                return False
        
        return False
        
    except Exception as e:
        logger.error(f"注册URL协议失败: {str(e)}")
        return False

class FoundationSettingCard(ExpandGroupSettingCard):
    def handle_url_command(self, url):
        """处理URL命令，打开指定界面"""
        try:
            if not url.startswith("secrandom://"):
                logger.error(f"无效的SecRandom URL: {url}")
                return False
            
            # 解析URL
            from urllib.parse import urlparse, parse_qs
            parsed_url = urlparse(url)
            path = parsed_url.path.strip('/')
            query_params = parse_qs(parsed_url.query)
            
            # 界面映射字典
            interface_map = {
                "main": "open_main_window",
                "settings": "open_settings_window",
                "pumping": "open_pumping_window",
                "reward": "open_reward_window",
                "history": "open_history_window",
                "floating": "open_floating_window"
            }
            
            # 根据路径打开对应界面
            if path in interface_map:
                method_name = interface_map[path]
                main_window = self.get_main_window()
                if main_window and hasattr(main_window, method_name):
                    method = getattr(main_window, method_name)
                    method()
                    logger.info(f"通过URL打开界面: {path}")
                    return True
                else:
                    logger.error(f"找不到对应的方法: {method_name}")
            else:
                logger.error(f"未知的界面路径: {path}")
            
            return False
            
        except Exception as e:
            logger.error(f"处理URL命令失败: {str(e)}")
            return False
    
    def get_main_window(self):
        """获取主窗口实例"""
        try:
            for widget in QApplication.topLevelWidgets():
                if hasattr(widget, 'update_focus_mode'):  # 通过特征识别主窗口
                    return widget
            return None
        except Exception as e:
            logger.error(f"获取主窗口失败: {str(e)}")
            return None
    
    def closeEvent(self, event):
        if not self.saved:
            w = Dialog('未保存内容', '确定要关闭吗？', self)
            w.setFont(QFont(load_custom_font(), 12))
            w.yesButton.setText("确定")
            w.cancelButton.setText("取消")
            w.yesButton = PrimaryPushButton('确定')
            w.cancelButton = PushButton('取消')
            
            if w.exec():
                self.reject
                return
            else:
                event.ignore()
                return
        event.accept()
    
    def getText(self):
        return self.textEdit.toPlainText()

class CleanupTimeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self.setWindowTitle("输入定时清理记录时间")
        self.setMinimumSize(400, 335)  # 设置最小大小而不是固定大小
        self.saved = False
        self.dragging = False
        self.drag_position = None
        
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
        self.title_label = BodyLabel("输入定时清理记录时间")
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
        
        self.text_label = BodyLabel('请输入定时清理记录时间，每行一个\n格式为：HH:mm:ss\n例如：12:00:00 或 20:00:00\n中文冒号自动转英文冒号\n自动补秒位为00')
        self.text_label.setFont(QFont(load_custom_font(), 12))

        self.update_theme_style()
        qconfig.themeChanged.connect(self.update_theme_style)
        
        self.textEdit = PlainTextEdit()
        self.textEdit.setPlaceholderText("请输入定时清理记录时间，每行一个")
        self.textEdit.setFont(QFont(load_custom_font(), 12))
        
        self.setFont(QFont(load_custom_font(), 12))

        try:
            cleanup_file = path_manager.get_settings_path('CleanupTimes.json')
            if path_manager.file_exists(cleanup_file):
                with open_file(cleanup_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    
                    # 获取所有清理时间并格式化为字符串
                    cleanup_times = settings.get('cleanuptimes', {})
                    if cleanup_times:
                        times_list = [str(time) for time_id, time in cleanup_times.items()]
                        self.textEdit.setPlainText('\n'.join(times_list))
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
        # 主题样式更新 包含自定义标题栏
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
            BodyLabel, QPushButton, QTextEdit {{ color: {colors['text']}; }}
        """)
        
        # 设置标题栏颜色以匹配背景色（仅Windows系统）
        if os.name == 'nt':
            try:
                import ctypes
                hwnd = int(self.winId())  # 转换为整数句柄
                
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
