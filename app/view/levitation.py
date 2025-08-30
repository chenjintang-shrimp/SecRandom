from qfluentwidgets import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtNetwork import *

import os
import sys
import importlib.util
import json
import random
import re
from loguru import logger
from pathlib import Path

from app.common.config import load_custom_font, is_dark_theme
from app.common.path_utils import path_manager
from app.common.path_utils import open_file, ensure_dir

dark_mode = is_dark_theme(qconfig)

class LevitationWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.app_dir = path_manager._app_root
        self._load_settings()  # 加载配置
        self._load_plugin_settings()  # 加载插件设置
        self._init_ui_components()  # 初始化UI组件
        self._setup_event_handlers()  # 设置事件处理器
        self._init_drag_system()  # 初始化拖动系统
        self._init_keep_top_timer()  # 初始化保持置顶定时器
        self.max_count = 0 # 初始化最大抽取人数
        self.is_drawing = False # 标记是否正在抽取
        self.update_total_count() # 更新最大抽取人数
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
                self.floating_visible = foundation_settings.get('pumping_floating_visible', 3)
                self.button_arrangement_mode = foundation_settings.get('button_arrangement_mode', 0)
                # 确保透明度值在有效范围内
                self.transparency_mode = max(0, min(self.transparency_mode, 9))
                # 确保按钮排列方式值在有效范围内
                self.button_arrangement_mode = max(0, min(self.button_arrangement_mode, 2))
        except (FileNotFoundError, json.JSONDecodeError) as e:
            self.transparency_mode = 6
            self.floating_visible = 3
            self.button_arrangement_mode = 0
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
        # 白露：初始化所有UI组件 - 根据floating_visible值进行功能组合显示
        self._setup_main_layout()
        
        # 根据floating_visible值（0-14）初始化对应的组件组合
        # 映射关系：
        # 0: 显示 拖动
        # 1: 显示 主界面
        # 2: 显示 闪抽
        # 3: 显示 拖动+主界面
        # 4: 显示 拖动+闪抽
        # 5: 显示 主界面+闪抽
        # 6: 显示 拖动+主界面+闪抽
        # 7: 显示 即抽

        if self.floating_visible == 0:  # 显示 拖动
            self._init_menu_label()
        elif self.floating_visible == 1:  # 显示 主界面
            self._init_people_label()
        elif self.floating_visible == 2:  # 显示 闪抽
            self._init_flash_button()
        elif self.floating_visible == 3:  # 显示 拖动+主界面
            self._init_menu_label()
            self._init_people_label()
        elif self.floating_visible == 4:  # 显示 拖动+闪抽
            self._init_menu_label()
            self._init_flash_button()
        elif self.floating_visible == 5:  # 显示 主界面+闪抽
            self._init_people_label()
            self._init_flash_button()
        elif self.floating_visible == 6:  # 显示 拖动+主界面+闪抽
            # 3个按钮：拖动、主界面在上面，闪抽在下面
            self._init_menu_label()
            self._init_people_label()
            self._init_flash_button()
        elif self.floating_visible == 7:  # 测试 即抽(带调节人数功能)
            self._init_instant_draw_button()
        
        self._apply_window_styles()

    def _setup_main_layout(self):
        # 小鸟游星野：设置主布局容器 - 支持多种排列方式
        self.container_button = QWidget()
        
        # 根据显示的按钮数量和排列方式决定布局
        button_count = self._get_button_count()
        
        if self.button_arrangement_mode == 0:  # 矩形排列（当前方式）
            if button_count >= 3:
                # 3个或4个按钮时使用垂直布局，文字按钮放在下面
                main_layout = QVBoxLayout(self.container_button)
                main_layout.setContentsMargins(0, 0, 0, 0)
                main_layout.setSpacing(0)
                
                # 创建上下两个容器
                self.top_container = QWidget()
                self.bottom_container = QWidget()
                
                # 上层使用水平布局
                top_layout = QHBoxLayout(self.top_container)
                top_layout.setContentsMargins(0, 0, 0, 0)
                top_layout.setSpacing(0)
                
                # 下层使用水平布局，如果是3个按钮则让按钮填满容器宽度
                bottom_layout = QHBoxLayout(self.bottom_container)
                bottom_layout.setContentsMargins(0, 0, 0, 0)
                bottom_layout.setSpacing(0)
                
                # 添加到主布局
                main_layout.addWidget(self.top_container)
                main_layout.addWidget(self.bottom_container)
                
                # 设置下层高度
                self.bottom_container.setFixedHeight(50)
                
            else:
                # 1个或2个按钮时使用水平布局
                button_layout = QHBoxLayout(self.container_button)
                button_layout.setContentsMargins(0, 0, 0, 0)
                button_layout.setSpacing(0)
                
                # 创建单个容器
                self.top_container = self.container_button
                self.bottom_container = None
                
        elif self.button_arrangement_mode == 1:  # 竖着排列
            # 所有按钮都垂直排列
            main_layout = QVBoxLayout(self.container_button)
            main_layout.setContentsMargins(0, 0, 0, 0)
            main_layout.setSpacing(0)
            
            # 创建专用的垂直容器，避免布局冲突
            self.top_container = QWidget()
            self.bottom_container = None
            
            # 为垂直容器设置垂直布局
            vertical_layout = QVBoxLayout(self.top_container)
            vertical_layout.setContentsMargins(0, 0, 0, 0)
            vertical_layout.setSpacing(0)
            
            # 将垂直容器添加到主布局
            main_layout.addWidget(self.top_container)
            
        elif self.button_arrangement_mode == 2:  # 横着排列
            # 所有按钮都水平排列
            main_layout = QHBoxLayout(self.container_button)
            main_layout.setContentsMargins(0, 0, 0, 0)
            main_layout.setSpacing(0)
            
            # 创建专用的水平容器，与竖着排列区分
            self.horizontal_container = QWidget()
            horizontal_layout = QHBoxLayout(self.horizontal_container)
            horizontal_layout.setContentsMargins(0, 0, 0, 0)
            horizontal_layout.setSpacing(0)
            
            # 将水平容器添加到主布局
            main_layout.addWidget(self.horizontal_container)
            
            # 设置其他容器为None，确保独立性
            self.top_container = None
            self.bottom_container = None

        # 设置窗口主布局
        window_layout = QHBoxLayout(self)
        window_layout.addWidget(self.container_button)
        self.setLayout(window_layout)
        
    def _get_button_count(self):
        # 小鸟游星野：根据floating_visible值计算要显示的按钮数量
        # 映射关系：
        # 0: 显示 拖动 (1个)
        # 1: 显示 主界面 (1个)
        # 2: 显示 闪抽 (1个)
        # 3: 显示 拖动+主界面 (2个)
        # 4: 显示 拖动+闪抽 (2个)
        # 5: 显示 主界面+闪抽 (2个)
        # 6: 显示 拖动+主界面+闪抽 (3个)
        # 7: 显示 即抽

        if self.floating_visible in [0, 1, 2]:
            return 1
        elif self.floating_visible in [3, 4, 5]:
            return 2
        elif self.floating_visible == 6:
            return 3
        elif self.floating_visible == 7:
            return 4
        else:
            return 1  # 默认值

    def _init_menu_label(self):
        # 白露：初始化菜单标签 - 只有在拖动+抽人模式时显示图标
        if self.floating_visible == 3:  # 拖动+抽人模式
            MENU_DEFAULT_ICON_PATH = path_manager.get_resource_path("icon", "SecRandom_menu_30%.png")
            self.menu_label = BodyLabel(self.container_button)
            try:
                # 根据主题设置不同的颜色
                if dark_mode:
                    # 深色模式
                    icon_path = path_manager.get_resource_path("icon", f"SecRandom_menu_{(10 - self.transparency_mode) * 10}%_light.png")
                else:
                    # 浅色模式
                    icon_path = path_manager.get_resource_path("icon", f"SecRandom_menu_{(10 - self.transparency_mode) * 10}%_black.png")
                if not icon_path.exists():
                    icon_path = MENU_DEFAULT_ICON_PATH
                pixmap = QPixmap(str(icon_path))
                self.menu_label.setPixmap(pixmap.scaled(27, 27, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            except FileNotFoundError as e:
                pixmap = QPixmap(str(MENU_DEFAULT_ICON_PATH))
                self.menu_label.setPixmap(pixmap.scaled(27, 27, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                logger.error(f"加载菜单图标失败: {e}")
     
            self.menu_label.setStyleSheet('opacity: 0;')
            self.menu_label.setFixedSize(50, 50)
            self.menu_label.setAlignment(Qt.AlignCenter)
        else:
            # 其他模式显示文字按钮
            self.menu_label = PushButton("拖动")
            if dark_mode:
                self.menu_label.setStyleSheet('opacity: 0; border: none; background: transparent; font-weight: bold; color: #ffffff;')
            else:
                self.menu_label.setStyleSheet('opacity: 0; border: none; background: transparent; font-weight: bold;')
            self.menu_label.setFont(QFont(load_custom_font(), 12))
        
        # 根据排列方式决定按钮大小和添加位置
        button_count = self._get_button_count()
        
        if self.button_arrangement_mode == 0:  # 矩形排列
            if button_count >= 3:
                # 3个或4个按钮时，拖动按钮放在上面
                if self.floating_visible != 3:  # 非图标模式需要设置按钮大小
                    self.menu_label.setFixedSize(50, 50)
                if hasattr(self, 'top_container') and self.top_container:
                    self.top_container.layout().addWidget(self.menu_label)
                else:
                    self.container_button.layout().addWidget(self.menu_label)
            else:
                # 1个或2个按钮时使用水平布局
                if self.floating_visible != 3:  # 非图标模式需要设置按钮大小
                    self.menu_label.setFixedSize(50, 50)
                if hasattr(self, 'top_container') and self.top_container:
                    self.top_container.layout().addWidget(self.menu_label)
                else:
                    self.container_button.layout().addWidget(self.menu_label)
                    
        elif self.button_arrangement_mode == 1:  # 竖着排列
            # 所有按钮都垂直排列
            if self.floating_visible != 3:  # 非图标模式需要设置按钮大小
                self.menu_label.setFixedSize(50, 50)
            if hasattr(self, 'top_container') and self.top_container:
                self.top_container.layout().addWidget(self.menu_label)
            else:
                self.container_button.layout().addWidget(self.menu_label)
                
        elif self.button_arrangement_mode == 2:  # 横着排列
            # 所有按钮都水平排列
            if self.floating_visible != 3:  # 非图标模式需要设置按钮大小
                self.menu_label.setFixedSize(50, 50)
            if hasattr(self, 'horizontal_container') and self.horizontal_container:
                self.horizontal_container.layout().addWidget(self.menu_label)
            elif hasattr(self, 'top_container') and self.top_container:
                self.top_container.layout().addWidget(self.menu_label)
            else:
                self.container_button.layout().addWidget(self.menu_label)

    def _init_people_label(self):
        # 小鸟游星野：初始化人物标签 - 只有在拖动+抽人模式时显示图标
        if self.floating_visible == 3:  # 拖动+抽人模式
            FLOATING_DEFAULT_ICON_PATH = path_manager.get_resource_path("icon", "SecRandom_floating_30%.png")
            self.people_label = BodyLabel(self.container_button)
            try:
                # 根据主题设置不同的颜色
                if dark_mode:
                    # 深色模式
                    icon_path = path_manager.get_resource_path("icon", f"SecRandom_floating_{(10 - self.transparency_mode) * 10}%_light.png")
                else:
                    # 浅色模式
                    icon_path = path_manager.get_resource_path("icon", f"SecRandom_floating_{(10 - self.transparency_mode) * 10}%_black.png")
                if not icon_path.exists():
                    icon_path = FLOATING_DEFAULT_ICON_PATH
                pixmap = QPixmap(str(icon_path))
                self.people_label.setPixmap(pixmap.scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            except FileNotFoundError as e:
                pixmap = QPixmap(str(FLOATING_DEFAULT_ICON_PATH))
                self.people_label.setPixmap(pixmap.scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                logger.error(f"加载人物图标失败: {e}")
     
            self.people_label.setStyleSheet('opacity: 0;')
            self.people_label.setFixedSize(50, 50)
            self.people_label.setAlignment(Qt.AlignCenter)
        else:
            # 其他模式显示文字按钮
            self.people_label = PushButton("抽人")
            if dark_mode:
                self.people_label.setStyleSheet('opacity: 0; border: none; background: transparent; font-weight: bold; color: #ffffff;')
            else:
                self.people_label.setStyleSheet('opacity: 0; border: none; background: transparent; font-weight: bold;')
            self.people_label.setFont(QFont(load_custom_font(), 12))
        
        # 根据排列方式决定按钮大小和添加位置
        button_count = self._get_button_count()
        
        if self.button_arrangement_mode == 0:  # 矩形排列
            if button_count >= 3:
                # 3个或4个按钮时，人物按钮放在上面
                if self.floating_visible != 3:  # 非图标模式需要设置按钮大小
                    self.people_label.setFixedSize(50, 50)
                if hasattr(self, 'top_container') and self.top_container:
                    self.top_container.layout().addWidget(self.people_label)
                else:
                    self.container_button.layout().addWidget(self.people_label)
            else:
                # 1个或2个按钮时使用水平布局
                if self.floating_visible != 3:  # 非图标模式需要设置按钮大小
                    self.people_label.setFixedSize(50, 50)
                if hasattr(self, 'top_container') and self.top_container:
                    self.top_container.layout().addWidget(self.people_label)
                else:
                    self.container_button.layout().addWidget(self.people_label)
                    
        elif self.button_arrangement_mode == 1:  # 竖着排列
            # 所有按钮都垂直排列
            if self.floating_visible != 3:  # 非图标模式需要设置按钮大小
                self.people_label.setFixedSize(50, 50)
            if hasattr(self, 'top_container') and self.top_container:
                self.top_container.layout().addWidget(self.people_label)
            else:
                self.container_button.layout().addWidget(self.people_label)
                
        elif self.button_arrangement_mode == 2:  # 横着排列
            # 所有按钮都水平排列
            if self.floating_visible != 3:  # 非图标模式需要设置按钮大小
                self.people_label.setFixedSize(50, 50)
            if hasattr(self, 'horizontal_container') and self.horizontal_container:
                self.horizontal_container.layout().addWidget(self.people_label)
            elif hasattr(self, 'top_container') and self.top_container:
                self.top_container.layout().addWidget(self.people_label)
            else:
                self.container_button.layout().addWidget(self.people_label)

    def _init_flash_button(self):
        # 小鸟游星野：初始化闪抽按钮 - 纯文字按钮 ✧(๑•̀ㅂ•́)๑
        self.flash_button = PushButton("闪抽")
        
        # 根据排列方式决定按钮大小和添加位置
        button_count = self._get_button_count()
        
        if self.button_arrangement_mode == 0:  # 矩形排列
            if button_count >= 3:
                # 3个或4个按钮时，闪抽按钮放在下面
                self.flash_button.setFixedSize(50, 50)
                if hasattr(self, 'bottom_container') and self.bottom_container:
                    self.bottom_container.layout().addWidget(self.flash_button)
                else:
                    self.container_button.layout().addWidget(self.flash_button)
            else:
                # 1个或2个按钮时使用水平布局
                self.flash_button.setFixedSize(50, 50)
                if hasattr(self, 'top_container') and self.top_container:
                    self.top_container.layout().addWidget(self.flash_button)
                else:
                    self.container_button.layout().addWidget(self.flash_button)
                    
        elif self.button_arrangement_mode == 1:  # 竖着排列
            # 所有按钮都垂直排列
            self.flash_button.setFixedSize(50, 50)
            if hasattr(self, 'top_container') and self.top_container:
                self.top_container.layout().addWidget(self.flash_button)
            else:
                self.container_button.layout().addWidget(self.flash_button)
                
        elif self.button_arrangement_mode == 2:  # 横着排列
            # 所有按钮都水平排列
            self.flash_button.setFixedSize(50, 50)
            if hasattr(self, 'horizontal_container') and self.horizontal_container:
                self.horizontal_container.layout().addWidget(self.flash_button)
            elif hasattr(self, 'top_container') and self.top_container:
                self.top_container.layout().addWidget(self.flash_button)
            else:
                self.container_button.layout().addWidget(self.flash_button)

        if dark_mode:
            self.flash_button.setStyleSheet('opacity: 0; border: none; background: transparent; font-weight: bold; color: #ffffff;')
        else:
            self.flash_button.setStyleSheet('opacity: 0; border: none; background: transparent; font-weight: bold;')
        self.flash_button.setFont(QFont(load_custom_font(), 12))
        self.flash_button.clicked.connect(self._show_direct_extraction_window)

    def _init_instant_draw_button(self):
        # 小鸟游星野：初始化即抽按钮和人数调节功能
        # 创建主容器
        self.instant_draw_container = QWidget()
        main_layout = QVBoxLayout(self.instant_draw_container)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)
        
        # 创建抽取按钮 - 增大尺寸并居中
        self.instant_draw_button = PushButton("抽取")
        self.instant_draw_button.setFixedSize(65, 30)
        
        # 创建人数调节容器 - 优化布局
        count_control_container = QWidget()
        # 根据排列模式决定水平或垂直布局
        if self.button_arrangement_mode == 1:  # 竖着排列
            # 竖排模式下使用垂直布局
            count_control_layout = QVBoxLayout(count_control_container)
        else:
            # 其他模式使用水平布局
            count_control_layout = QHBoxLayout(count_control_container)
        count_control_layout.setContentsMargins(0, 0, 0, 0)
        count_control_layout.setSpacing(5)
        
        # 创建-按钮
        self.decrease_button = PushButton("-")
        # 竖排模式下宽度为60，其他模式保持原尺寸
        if self.button_arrangement_mode == 1:  # 竖着排列
            self.decrease_button.setFixedSize(65, 30)
        else:
            self.decrease_button.setFixedSize(41, 30)
        
        # 创建当前人数显示文本 - 增大并美化
        self.count_label = BodyLabel("1")
        self.count_label.setAlignment(Qt.AlignCenter)
        # 竖排模式下宽度为60，其他模式保持原尺寸
        if self.button_arrangement_mode == 1:  # 竖着排列
            self.count_label.setFixedSize(65, 30)
        else:
            self.count_label.setFixedSize(43, 30)
        
        # 创建+按钮
        self.increase_button = PushButton("+")
        # 竖排模式下宽度为60，其他模式保持原尺寸
        if self.button_arrangement_mode == 1:  # 竖着排列
            self.increase_button.setFixedSize(65, 30)
        else:
            self.increase_button.setFixedSize(41, 30)
        
        # 创建重置按钮 - 调整大小
        self.reset_button = PushButton("重置")
        self.reset_button.setFixedSize(65, 30)
        
        if self.button_arrangement_mode == 1:  # 竖着排列
            # 竖排模式下使用垂直布局
            count_control_layout.addStretch()
            count_control_layout.addWidget(self.increase_button)
            count_control_layout.addWidget(self.count_label)
            count_control_layout.addWidget(self.decrease_button)
            count_control_layout.addWidget(self.reset_button)
            count_control_layout.addStretch()
        else:
            # 其他模式使用水平布局
            count_control_layout.addStretch()
            count_control_layout.addWidget(self.decrease_button)
            count_control_layout.addWidget(self.count_label)
            count_control_layout.addWidget(self.increase_button)
            count_control_layout.addStretch()

        
        # 为抽取按钮和重置按钮创建布局 - 根据排列模式决定水平或垂直
        if self.button_arrangement_mode == 1:  # 竖着排列
            # 竖排模式下使用垂直布局
            button_layout = QVBoxLayout()
            button_layout.addWidget(self.instant_draw_button)
        else:
            # 其他模式使用水平布局
            button_layout = QHBoxLayout()
            button_layout.addWidget(self.instant_draw_button)
            button_layout.addWidget(self.reset_button)
        button_layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建按钮容器
        button_container = QWidget()
        button_container.setLayout(button_layout)
        
        # 将按钮容器和人数调节容器添加到主布局 - 居中对齐
        main_layout.addStretch()
        main_layout.addWidget(button_container, 0, Qt.AlignCenter)
        main_layout.addWidget(count_control_container, 0, Qt.AlignCenter)
        main_layout.addStretch()
        
        self.instant_draw_button.setFont(QFont(load_custom_font(), 12))
        self.increase_button.setFont(QFont(load_custom_font(), 12))
        self.decrease_button.setFont(QFont(load_custom_font(), 12))
        self.reset_button.setFont(QFont(load_custom_font(), 12))
        self.count_label.setFont(QFont(load_custom_font(), 12))
        
        # 连接信号
        self.instant_draw_button.clicked.connect(self._show_instant_draw_window)
        self.increase_button.clicked.connect(self._increase_count)
        self.decrease_button.clicked.connect(self._decrease_count)
        self.reset_button.clicked.connect(self._reset_count)
        
        # 初始化当前抽取人数
        self.current_count = 1
        
        # 为整个即抽容器添加拖动功能（仅空白区域）
        self.instant_draw_container.mousePressEvent = self.on_instant_draw_container_press
        self.instant_draw_container.mouseReleaseEvent = self.on_instant_draw_container_release

        # 根据排列方式决定添加位置
        target_container = None
        
        # 确定目标容器 - 支持3种独立排列样式
        if self.button_arrangement_mode == 0:  # 矩形排列
            target_container = self.bottom_container if hasattr(self, 'bottom_container') and self.bottom_container else None
        elif self.button_arrangement_mode == 1:  # 竖着排列
            target_container = self.top_container if hasattr(self, 'top_container') and self.top_container else None
        elif self.button_arrangement_mode == 2:  # 横着排列
            # 横着排列使用专用的水平容器，确保与竖着排列区分
            if hasattr(self, 'horizontal_container') and self.horizontal_container:
                target_container = self.horizontal_container
            elif hasattr(self, 'top_container') and self.top_container:
                # 如果没有专门的horizontal_container，则使用top_container
                target_container = self.top_container
        
        # 添加即抽容器到目标位置
        if target_container:
            target_container.layout().addWidget(self.instant_draw_container)
        else:
            self.container_button.layout().addWidget(self.instant_draw_container)

    def _apply_window_styles(self):
        # 白露：应用窗口样式和标志
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        try:
            opacity = (10 - self.transparency_mode) * 0.1
            # 根据主题设置不同的背景颜色
            if dark_mode:
                # 深色模式背景颜色
                bg_color = f'rgba(65, 66, 66, {opacity})'
            else:
                # 浅色模式背景颜色
                bg_color = f'rgba(240, 240, 240, {opacity})'
            self.setStyleSheet(f'border-radius: 5px; background-color: {bg_color};')
        except Exception as e:
            self.setStyleSheet('border-radius: 5px; background-color: rgba(65, 66, 66, 0.3);')
            logger.error(f"应用窗口样式失败: {e}")

    def _setup_event_handlers(self):
        # 小鸟游星野：设置所有事件处理器 - 无论控件是否显示都要绑定 ✧(๑•̀ㅂ•́)ow✧
        if hasattr(self, 'menu_label') and self.menu_label is not None:
            self.menu_label.mousePressEvent = lambda event: self.start_drag(event)
            self.menu_label.mouseReleaseEvent = self.stop_drag

        # 白露：人物标签始终存在，必须绑定事件处理器
        if hasattr(self, 'people_label') and self.people_label is not None:
            self.people_label.mousePressEvent = self.on_people_press
            self.people_label.mouseReleaseEvent = self.on_people_release

        # 小鸟游星野：闪抽按钮事件处理器 - 与抽人按钮相同的拖动功能 ✧(๑•̀ㅂ•́)๑
        if hasattr(self, 'flash_button') and self.flash_button is not None:
            self.flash_button.mousePressEvent = self.on_flash_press
            self.flash_button.mouseReleaseEvent = self.on_flash_release
            
        # 即抽按钮和重置按钮的拖动事件处理器 - 支持长按拖动
        if hasattr(self, 'instant_draw_button') and self.instant_draw_button is not None:
            self.instant_draw_button.mousePressEvent = self.on_instant_draw_button_press
            self.instant_draw_button.mouseReleaseEvent = self.on_instant_draw_button_release
            
        if hasattr(self, 'reset_button') and self.reset_button is not None:
            self.reset_button.mousePressEvent = self.on_reset_button_press
            self.reset_button.mouseReleaseEvent = self.on_reset_button_release
            
        # 加减按钮的拖动事件处理器 - 支持长按拖动
        if hasattr(self, 'increase_button') and self.increase_button is not None:
            self.increase_button.mousePressEvent = self.on_increase_button_press
            self.increase_button.mouseReleaseEvent = self.on_increase_button_release
            
        if hasattr(self, 'decrease_button') and self.decrease_button is not None:
            self.decrease_button.mousePressEvent = self.on_decrease_button_press
            self.decrease_button.mouseReleaseEvent = self.on_decrease_button_release

    def _init_drag_system(self):
        # 白露：初始化拖动系统
        self.drag_position = QPoint()
        self.drag_start_position = QPoint()
        self.is_dragging = False
        self.click_timer = QTimer(self)
        self.click_timer.setSingleShot(True)
        self.click_timer.timeout.connect(lambda: self.start_drag(None))

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
            
    def on_instant_draw_button_press(self, event):
        # 即抽按钮按下事件 - 支持长按拖动
        self.drag_start_position = event.pos()
        # 启动长按计时器（100毫秒）
        self.click_timer.start(100)
        
    def on_instant_draw_button_release(self, event):
        if self.click_timer.isActive():
            # 短按：停止计时器并触发点击事件
            self.click_timer.stop()
            self._show_instant_draw_window()
            # 长按：计时器已触发拖动，不执行点击
            
    def on_reset_button_press(self, event):
        # 重置按钮按下事件 - 支持长按拖动
        self.drag_start_position = event.pos()
        # 启动长按计时器（100毫秒）
        self.click_timer.start(100)
        
    def on_reset_button_release(self, event):
        if self.click_timer.isActive():
            # 短按：停止计时器并触发点击事件
            self.click_timer.stop()
            self._reset_count()
            # 长按：计时器已触发拖动，不执行点击
            
    def on_increase_button_press(self, event):
        # 增加按钮按下事件 - 支持长按拖动
        self.drag_start_position = event.pos()
        # 启动长按计时器（100毫秒）
        self.click_timer.start(100)
        
    def on_increase_button_release(self, event):
        if self.click_timer.isActive():
            # 短按：停止计时器并触发点击事件
            self.click_timer.stop()
            self._increase_count()
            # 长按：计时器已触发拖动，不执行点击
            
    def on_decrease_button_press(self, event):
        # 减少按钮按下事件 - 支持长按拖动
        self.drag_start_position = event.pos()
        # 启动长按计时器（100毫秒）
        self.click_timer.start(100)
        
    def on_decrease_button_release(self, event):
        if self.click_timer.isActive():
            # 短按：停止计时器并触发点击事件
            self.click_timer.stop()
            self._decrease_count()
            # 长按：计时器已触发拖动，不执行点击

    # 白露：处理人物标签点击事件（忽略事件参数）
    def on_people_clicked(self, event=None): 
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
        # 白露：开始拖动逻辑 - 使用鼠标按下的全局位置作为起始位置
        if event:
            # 使用事件的全局位置减去窗口当前位置，得到相对于窗口的偏移量
            self.drag_position = event.globalPos() - self.pos()
        else:
            # 如果没有事件参数，使用之前记录的起始位置
            self.drag_position = self.drag_start_position
        self.is_dragging = True

    def mouseMoveEvent(self, event):
        # 白露：处理鼠标移动事件 - 实现窗口跟随拖动
        # 检测长按计时期间的鼠标移动，超过阈值立即触发拖动
        if self.click_timer.isActive() and event.buttons() == Qt.LeftButton:
            delta = event.pos() - self.drag_start_position
            if abs(delta.x()) > 2 or abs(delta.y()) > 2:
                self.click_timer.stop()
                self.start_drag(event)

        if hasattr(self, 'is_dragging') and self.is_dragging and event.buttons() == Qt.LeftButton:
            # 计算鼠标移动偏移量并保持相对位置
            # drag_position现在存储的是鼠标相对于窗口的偏移量
            if hasattr(self, 'drag_position') and self.drag_position is not None:
                new_pos = event.globalPos() - self.drag_position

                # 获取屏幕尺寸
                screen = QApplication.desktop().screenGeometry()

                # 限制窗口不超出屏幕
                new_pos.setX(max(0, min(new_pos.x(), screen.width() - self.width())))
                new_pos.setY(max(0, min(new_pos.y(), screen.height() - self.height())))

                self.move(new_pos)
            else:
                # 如果drag_position未正确设置，重新初始化拖动
                self.start_drag(event)
        super().mouseMoveEvent(event)

    def on_people_release(self, event):
        # 星穹铁道白露：人物标签释放事件处理 - 区分点击和拖动 (≧∇≦)ﾉ
        was_dragging = getattr(self, 'is_dragging', False)
        self.is_dragging = False
        
        if self.click_timer.isActive():
            # 小鸟游星野：短按点击，触发主页面打开 ✧(๑•̀ㅂ•́)๑
            self.click_timer.stop()
            self.on_people_clicked()
        elif was_dragging:
            # 白露：拖动结束，保存新位置 (≧∇≦)ﾉ
            self.save_position()
        
        event.accept()

    def on_flash_press(self, event):
        # 小鸟游星野：闪抽按钮按下事件 - 记录拖动起始位置 ✧(๑•̀ㅂ•́)ow✧
        self.drag_start_position = event.pos()
        # 启动长按计时器（100毫秒 - 进一步优化响应速度）
        self.click_timer.start(100)

    def on_flash_release(self, event):
        # 星穹铁道白露：闪抽按钮释放事件处理 - 区分点击和拖动 (≧∇≦)ﾉ
        was_dragging = getattr(self, 'is_dragging', False)
        self.is_dragging = False
        
        if self.click_timer.isActive():
            # 小鸟游星野：短按点击，触发闪抽窗口 ✧(๑•̀ㅂ•́)๑
            self.click_timer.stop()
            self.on_flash_clicked()
        elif was_dragging:
            # 白露：拖动结束，保存新位置 (≧∇≦)ﾉ
            self.save_position()
        
        event.accept()

    def on_flash_clicked(self, event=None):
        # 小鸟游星野：闪抽按钮点击事件 - 显示直接抽取窗口 ✧(๑•̀ㅂ•́)๑
        self._show_direct_extraction_window()

    def on_auxiliary_press(self, event):
        # 小鸟游星野：辅窗按钮按下事件 - 记录拖动起始位置 ✧(๑•̀ㅂ•́)ow✧
        self.drag_start_position = event.pos()
        # 启动长按计时器（100毫秒 - 进一步优化响应速度）
        self.click_timer.start(100)

    def on_auxiliary_release(self, event):
        # 星穹铁道白露：辅窗按钮释放事件处理 - 区分点击和拖动 (≧∇≦)ﾉ
        was_dragging = getattr(self, 'is_dragging', False)
        self.is_dragging = False
        
        if self.click_timer.isActive():
            # 小鸟游星野：短按点击，触发辅窗窗口 ✧(๑•̀ㅂ•́)๑
            self.click_timer.stop()
            self.on_auxiliary_clicked()
        elif was_dragging:
            # 白露：拖动结束，保存新位置 (≧∇≦)ﾉ
            self.save_position()
        
        event.accept()

    def on_auxiliary_clicked(self, event=None):
        # 小鸟游星野：辅窗按钮点击事件 - 显示辅窗窗口 ✧(๑•̀ㅂ•́)๑
        self._show_auxiliary_window()
    
    def on_instant_draw_container_press(self, event):
        """处理即抽容器鼠标按下事件，支持拖动（仅空白区域）"""
        if event.button() == Qt.LeftButton:
            # 获取点击位置的子控件
            child = self.instant_draw_container.childAt(event.pos())
            # 如果点击的是容器空白区域（没有子控件或子控件不是按钮），则触发拖动
            if child is None or not isinstance(child, QPushButton):
                self.drag_start_position = event.pos()
                # 启动长按计时器
                if hasattr(self, 'click_timer'):
                    self.click_timer.start(100)  # 100ms后开始拖动
                event.accept()
            else:
                # 如果点击的是按钮，不处理拖动，让按钮保持原有功能
                event.ignore()
        else:
            event.ignore()
    
    def on_instant_draw_container_release(self, event):
        """处理即抽容器鼠标释放事件（仅空白区域）"""
        was_dragging = getattr(self, 'is_dragging', False)
        self.is_dragging = False
        
        if hasattr(self, 'click_timer') and self.click_timer.isActive():
            # 短按点击容器空白区域，触发即抽窗口
            self.click_timer.stop()
            self._show_instant_draw_window()
        elif was_dragging:
            # 拖动结束，保存新位置
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
        # 星穹铁道白露：右键点击也会触发事件哦~ 现在整个窗口都可以拖动啦 (๑•̀ㅂ•́)๑
        if event.button() == Qt.LeftButton:
            # 记录拖动起始位置
            self.drag_start_position = event.pos()
            # 启动长按计时器（100毫秒 - 优化响应速度）
            self.click_timer.start(100)
        else:
            event.ignore()

    def _animate_button_press(self, button):
        """按钮按下动画效果"""
        # 使用样式表实现简单的按下效果
        original_style = button.styleSheet()
        pressed_style = original_style + "transform: scale(0.95);"
        button.setStyleSheet(pressed_style)
        # 保存原始样式以便恢复
        if not hasattr(button, '_original_style'):
            button._original_style = original_style
    
    def _animate_button_release(self, button):
        """按钮释放动画效果"""
        # 恢复原始样式
        if hasattr(button, '_original_style'):
            button.setStyleSheet(button._original_style)
    
    def _animate_count_change(self, new_count):
        """人数变化动画效果"""
        # 使用定时器实现简单的淡入淡出效果
        original_style = self.count_label.styleSheet()
        
        # 淡出效果
        fade_out_style = original_style + "opacity: 0.3;"
        self.count_label.setStyleSheet(fade_out_style)
        
        def update_text():
            self.count_label.setText(str(new_count))
            # 淡入效果
            self.count_label.setStyleSheet(original_style)
        
        QTimer.singleShot(150, update_text)
    
    def stop_drag(self, event=None):
        # 小鸟游星野：停止拖动时的处理逻辑 - 菜单标签专用 ✧(๑•̀ㅂ•́)๑
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

    def _show_direct_extraction_window(self, draw_count=1):
        # 小鸟游星野：显示直接抽取窗口 - 包含pumping_people功能 ✧(๑•̀ㅂ•́)๑
        try:
            # 导入pumping_people模块
            from app.view.main_page.flash_pumping_people import pumping_people
            
            # 初始化当前抽取人数
            self.current_count = draw_count
            
            # 创建自定义标题栏的对话框
            self.pumping_widget = QDialog()
            self.pumping_widget.setWindowFlags(Qt.FramelessWindowHint | Qt.Window | Qt.Tool | Qt.WindowStaysOnTopHint)
            self.pumping_widget.setWindowTitle("SecRandom - 闪抽")
            # self.pumping_widget.setSizeGripEnabled(True)
            
            # 🐦 小鸟游星野：创建自定义标题栏啦~ (≧∇≦)ﾉ
            self.title_bar = QWidget()
            self.title_bar.setObjectName("CustomTitleBar")
            self.title_bar.setFixedHeight(35)
            
            # 标题栏布局
            title_layout = QHBoxLayout(self.title_bar)
            title_layout.setContentsMargins(10, 0, 10, 0)
            
            # 窗口标题
            title_text = "SecRandom - 抽取"
            self.title_label = BodyLabel(title_text)
            self.title_label.setObjectName("TitleLabel")
            self.title_label.setFont(QFont(load_custom_font(), 12))
            
            # 窗口控制按钮
            self.close_btn = QPushButton("✕")
            self.close_btn.setObjectName("CloseButton")
            self.close_btn.setFixedSize(25, 25)
            self.close_btn.clicked.connect(self.pumping_widget.reject)

            # 添加组件到标题栏
            title_layout.addWidget(self.title_label)
            title_layout.addStretch()
            title_layout.addWidget(self.close_btn)
            
            # 创建pumping_people内容
            self.pumping_content = pumping_people(draw_count=self.current_count)
            
            # 获取字体大小设置以动态调整窗口大小
            try:
                from app.common.path_utils import path_manager, open_file
                settings_file = path_manager.get_settings_path()
                with open_file(settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    font_size = settings['pumping_people']['font_size']
                    show_student_image = settings['pumping_people']['show_student_image']
            except Exception as e:
                font_size = 50  # 默认字体大小
                show_student_image = False
                logger.error(f"加载字体设置时出错: {e}, 使用默认设置")
            
            # 根据字体大小计算窗口尺寸
            # 基础尺寸 + 字体大小相关缩放，确保内容完整显示
            base_width = 310
            base_height = 350
            
            # 字体大小对应的缩放因子，确保小字号有足够空间，适配到200字号
            if font_size <= 30:
                scale_factor = 0.7
            elif font_size <= 40:
                scale_factor = 0.9
            elif font_size <= 50:
                scale_factor = 1.1
            elif font_size <= 60:
                scale_factor = 1.3
            elif font_size <= 80:
                scale_factor = 1.5
            elif font_size <= 100:
                scale_factor = 1.8
            elif font_size <= 120:
                scale_factor = 2.1
            elif font_size <= 150:
                scale_factor = 2.5
            elif font_size <= 180:
                scale_factor = 3.0
            else:
                scale_factor = 3.5
            
            # 计算动态窗口大小，确保最小和最大尺寸限制，适配200字号
            # 如果显示学生图片，需要增加窗口宽度
            if show_student_image:
                # 显示图片时根据字体大小动态计算图片额外宽度
                if font_size <= 30:
                    image_width_bonus = 170   # 小字体时的图片额外宽度
                elif font_size <= 50:
                    image_width_bonus = 170  # 中等字体时的图片额外宽度
                elif font_size <= 80:
                    image_width_bonus = 240  # 较大字体时的图片额外宽度
                elif font_size <= 120:
                    image_width_bonus = 320  # 大字体时的图片额外宽度
                elif font_size <= 150:
                    image_width_bonus = 450  # 很大字体时的图片额外宽度
                elif font_size <= 180:
                    image_width_bonus = 600  # 很大字体时的图片额外宽度
                else:
                    image_width_bonus = 800  # 超大字体时的图片额外宽度
                dynamic_width = max(150, min(1920, int((base_width + image_width_bonus) * scale_factor)))
            elif self.current_count > 1:
                # 显示更多人时根据字体大小动态计算额外宽度
                if font_size <= 30:
                    dynamic_width_bonus = 150   # 小字体时的额外宽度
                elif font_size <= 50:
                    dynamic_width_bonus = 150  # 中等字体时的额外宽度
                elif font_size <= 80:
                    dynamic_width_bonus = 220  # 较大字体时的额外宽度
                elif font_size <= 120:
                    dynamic_width_bonus = 300  # 大字体时的额外宽度
                elif font_size <= 150:
                    dynamic_width_bonus = 430  # 很大字体时的额外宽度
                elif font_size <= 180:
                    dynamic_width_bonus = 580  # 很大字体时的额外宽度
                else:
                    dynamic_width_bonus = 780  # 超大字体时的额外宽度
                dynamic_width = max(150, min(1920, int((base_width + dynamic_width_bonus) * scale_factor)))
            else:
                dynamic_width = max(150, min(1920, int(base_width * scale_factor)))
            dynamic_height = max(170, min(1080, int(base_height * scale_factor)))
            
            self.pumping_widget.setFixedSize(dynamic_width, dynamic_height)
            
            # 创建倒计时标签
            self.countdown_label = BodyLabel("")
            self.countdown_label.setObjectName("CountdownLabel")
            self.countdown_label.setFont(QFont(load_custom_font(), 12))
            self.countdown_label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)

            # 创建底部布局
            bottom_layout = QHBoxLayout()
            bottom_layout.setContentsMargins(10, 5, 10, 5)
            bottom_layout.addWidget(self.countdown_label)

            # 主布局
            main_layout = QVBoxLayout(self.pumping_widget)
            main_layout.setContentsMargins(0, 0, 0, 0)
            main_layout.setSpacing(0)
            # 添加自定义标题栏
            main_layout.addWidget(self.title_bar)
            # 添加内容区域
            main_layout.addWidget(self.pumping_content)
            # 添加底部布局
            main_layout.addLayout(bottom_layout)
            
            # 添加窗口拖动功能 - 整个窗口都可以拖动
            self.dragging = False
            self.drag_position = None
            self.pumping_widget.mousePressEvent = self._on_window_press
            self.pumping_widget.mouseMoveEvent = self._on_window_move
            self.pumping_widget.mouseReleaseEvent = self._on_window_release
            
            # 连接窗口关闭事件以清理定时器
            self.pumping_widget.finished.connect(self._on_pumping_widget_closed)
            
            # 标题栏也保持拖动功能
            self.title_bar.mousePressEvent = self._on_title_bar_press
            self.title_bar.mouseMoveEvent = self._on_title_bar_move
            self.title_bar.mouseReleaseEvent = self._on_title_bar_release
            self.update_theme_style()
            
            # 窗口居中显示 - 相对于屏幕居中
            screen = QApplication.desktop().screenGeometry()
            x = (screen.width() - self.pumping_widget.width()) // 2
            y = (screen.height() - self.pumping_widget.height()) // 2
            self.pumping_widget.move(QPoint(x, y))
            
            # 直接显示窗口
            self.pumping_widget.show()
            logger.info("直接抽取窗口已打开")
            
            # 禁用闪抽按钮，防止重复点击
            if hasattr(self, 'flash_button') and self.flash_button is not None:
                self.flash_button.setEnabled(False)
                logger.info("闪抽按钮已禁用")
            
            # 禁用即抽按钮，防止重复点击
            if hasattr(self, 'instant_draw_button') and self.instant_draw_button is not None:
                self.instant_draw_button.setEnabled(False)
                logger.info("即抽按钮已禁用")
            
            # 标记抽取正在进行
            self.is_drawing = True
            logger.info("抽取状态已设置为进行中")
            
            self.pumping_content.start_draw()
            
            # 连接抽取完成信号，在抽取完成后才开始倒计时
            self.pumping_content.draw_finished.connect(self._start_countdown_after_draw)
            
            # 初始显示提示信息
            self.countdown_label.setText("抽取进行中，完成后将开始倒计时")
            self.countdown_label.setFont(QFont(load_custom_font(), 12))
            
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
            
    def _on_title_bar_press(self, event):
        # 🐦 小鸟游星野：窗口拖动功能~ 按住标题栏就能移动啦 (๑•̀ㅂ•́)๑
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.drag_position = event.globalPos() - self.pumping_widget.frameGeometry().topLeft()
            event.accept()

    def _on_title_bar_move(self, event):
        if self.dragging and event.buttons() == Qt.LeftButton:
            self.pumping_widget.move(event.globalPos() - self.drag_position)
            event.accept()

    def _on_title_bar_release(self, event):
        self.dragging = False

    def _start_countdown_after_draw(self):
        """抽取完成后开始倒计时"""
        # 从设置中获取闪抽窗口自动关闭设置
        try:
            # 获取设置
            settings_file = path_manager.get_settings_path()
            with open_file(settings_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                
            # 检查是否启用自动关闭
            auto_close_enabled = settings.get('flash_window_auto_close', True)
            close_time = settings.get('flash_window_close_time', 2)
            close_time = close_time + 1
            
            if auto_close_enabled:
                # 初始化倒计时
                self.remaining_time = close_time
                self.countdown_label.setText(f"将在{self.remaining_time}秒自动关闭该窗口")
                self.countdown_label.setFont(QFont(load_custom_font(), 12))

                # 创建倒计时定时器
                self.countdown_timer = QTimer(self.pumping_widget)
                self.countdown_timer.timeout.connect(self._update_countdown)
                self.countdown_timer.start(1000)  # 每秒更新一次

                # 创建自动关闭定时器
                self.auto_close_timer = QTimer(self.pumping_widget)
                self.auto_close_timer.setSingleShot(True)
                self.auto_close_timer.timeout.connect(self.pumping_widget.reject)
                self.auto_close_timer.start(close_time * 1000)  # 转换为毫秒
                logger.info(f"闪抽窗口将在{close_time}秒后自动关闭")
            else:
                logger.info("闪抽窗口自动关闭功能已禁用")
        except Exception as e:
            logger.error(f"加载闪抽窗口设置时出错: {e}, 使用默认设置")
            # 默认启用3秒自动关闭
            close_time = 3
            self.remaining_time = close_time
            self.countdown_label.setText(f"将在{self.remaining_time}秒自动关闭该窗口")
            self.countdown_label.setFont(QFont(load_custom_font(), 12))

            # 创建倒计时定时器
            self.countdown_timer = QTimer(self.pumping_widget)
            self.countdown_timer.timeout.connect(self._update_countdown)
            self.countdown_timer.start(1000)  # 每秒更新一次

            self.auto_close_timer = QTimer(self.pumping_widget)
            self.auto_close_timer.setSingleShot(True)
            self.auto_close_timer.timeout.connect(self.pumping_widget.reject)
            self.auto_close_timer.start(close_time * 1000)  # 3秒后自动关闭
    
    def _update_countdown(self):
        # 更新倒计时
        self.remaining_time -= 1
        self.countdown_label.setText(f"将在{self.remaining_time}秒自动关闭该窗口")
        self.countdown_label.setFont(QFont(load_custom_font(), 12))

        # 当倒计时结束时停止定时器
        if self.remaining_time <= 0:
            if hasattr(self, 'countdown_timer'):
                self.countdown_timer.stop()

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
            BodyLabel, QPushButton, QTextEdit {{ color: {colors['text']}; }}
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

    def _on_window_press(self, event):
        """窗口鼠标按下事件 - 整个窗口都可以拖动"""
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.drag_position = event.globalPos() - self.pumping_widget.frameGeometry().topLeft()
            event.accept()
    
    def _on_window_move(self, event):
        """窗口鼠标移动事件"""
        if self.dragging and event.buttons() == Qt.LeftButton:
            self.pumping_widget.move(event.globalPos() - self.drag_position)
            event.accept()
    
    def _on_window_release(self, event):
        """窗口鼠标释放事件"""
        if event.button() == Qt.LeftButton:
            self.dragging = False
            event.accept()
            
    def _on_pumping_widget_closed(self):
        """直接抽取窗口关闭事件 - 清理定时器资源并重新启用闪抽按钮"""
        # 停止自动关闭定时器
        if hasattr(self, 'auto_close_timer') and self.auto_close_timer.isActive():
            self.auto_close_timer.stop()
            logger.info("直接抽取窗口已关闭，自动关闭定时器已停止")

        # 停止倒计时定时器
        if hasattr(self, 'countdown_timer') and self.countdown_timer.isActive():
            self.countdown_timer.stop()
            logger.info("直接抽取窗口已关闭，倒计时定时器已停止")
        
        # 重新启用闪抽按钮
        if hasattr(self, 'flash_button') and self.flash_button is not None:
            self.flash_button.setEnabled(True)
            logger.info("闪抽按钮已重新启用")
        
        # 重新启用即抽按钮
        if hasattr(self, 'instant_draw_button') and self.instant_draw_button is not None:
            self.instant_draw_button.setEnabled(True)
            logger.info("即抽按钮已重新启用")
        
        # 标记抽取已结束
        self.is_drawing = False
        logger.info("抽取状态已设置为结束")
    
    def closeEvent(self, event):
        """窗口关闭事件 - 清理所有定时器资源"""
        # 停止保持置顶定时器
        if hasattr(self, 'keep_top_timer') and self.keep_top_timer.isActive():
            self.keep_top_timer.stop()
            logger.info("浮窗置顶定时器已停止")
        
        # 停止点击定时器
        if hasattr(self, 'click_timer') and self.click_timer.isActive():
            self.click_timer.stop()
            logger.info("点击定时器已停止")
        
        # 停止移动定时器
        if hasattr(self, 'move_timer') and self.move_timer.isActive():
            self.move_timer.stop()
            logger.info("移动定时器已停止")
        
        # 停止自动关闭定时器
        if hasattr(self, 'auto_close_timer') and self.auto_close_timer.isActive():
            self.auto_close_timer.stop()
            logger.info("自动关闭定时器已停止")
        
        # 停止倒计时定时器
        if hasattr(self, 'countdown_timer') and self.countdown_timer.isActive():
            self.countdown_timer.stop()
            logger.info("倒计时定时器已停止")
        
        # 调用父类的closeEvent
        super().closeEvent(event)

    def _init_keep_top_timer(self):
        """初始化保持置顶定时器 - 每5秒钟让浮窗置顶一下"""
        self.keep_top_timer = QTimer(self)
        self.keep_top_timer.timeout.connect(self._keep_window_on_top)
        self.keep_top_timer.start(5000)
        logger.info("浮窗置顶定时器已启动")

    def _keep_window_on_top(self):
        """保持窗口置顶"""
        try:
            self.raise_()  # 将窗口提升到最前面
            # self.activateWindow()  # 激活窗口
        except Exception as e:
            logger.warning(f"保持窗口置顶失败: {e}")

    # 对用户的选择进行返回学生数量或小组数量
    def _get_cleaned_data(self, student_file, group_name, genders):
        with open_file(student_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # 初始化不同情况的列表
            group_data = []
            student_data = []
            for student_name, student_info in data.items():
                if isinstance(student_info, dict) and 'id' in student_info:
                    id = student_info.get('id', '')
                    name = student_name.replace('【', '').replace('】', '')
                    gender = student_info.get('gender', '')
                    group = student_info.get('group', '')
                    exist = student_info.get('exist', True)
                    if group_name == '抽取小组组号':
                        group_data.append((id, group, exist))
                    elif group_name == group:
                        if (not genders) or (genders and gender in genders) or (genders == '抽取所有性别'):
                            student_data.append((id, name, exist))
                    elif group_name == '抽取全班学生':
                        if (not genders) or (genders and gender in genders) or (genders == '抽取所有性别'):
                            student_data.append((id, name, exist))
                        
            if group_name == '抽取小组组号':
                valid_groups = set()
                group_exist_map = {}
                for _, group, exist in group_data:
                    if group not in group_exist_map:
                        group_exist_map[group] = exist
                    else:
                        group_exist_map[group] = group_exist_map[group] or exist
                for group, has_exist in group_exist_map.items():
                    if has_exist:
                        valid_groups.add(group)
                unique_groups = sorted(valid_groups, key=self.sort_key)
                cleaned_data = [(group_id, group, True) for group_id, group in enumerate(sorted(unique_groups, key=self.sort_key), start=1)]
            else:
                cleaned_data = [data for data in student_data if data[2]]
            return cleaned_data

    # 增加抽取人数
    def _increase_count(self):
        """增加抽取人数"""
        if self.current_count < self.max_count:
            self.current_count += 1
            self._animate_count_change(self.current_count)
            self._update_count_display()

    # 减少抽取人数        
    def _decrease_count(self):
        """减少抽取人数"""
        if self.current_count > 1:
            self.current_count -= 1
            self._animate_count_change(self.current_count)
            self._update_count_display()

    # 更新人数显示        
    def _update_count_display(self):
        """更新人数显示"""
        self.count_label.setText(str(self.current_count))
        
        # 根据当前人数启用/禁用按钮
        self.increase_button.setEnabled(self.current_count < self.max_count)
        self.decrease_button.setEnabled(self.current_count > 1)
        
        # 只有在不在抽取过程中时才根据人数条件启用/禁用即抽按钮
        if not self.is_drawing:
            self.instant_draw_button.setEnabled(self.current_count <= self.max_count and self.current_count > 0)
        # 如果正在抽取，保持按钮禁用状态
        
        # 如果当前人数超过最大人数，自动调整到最大人数
        if self.current_count > self.max_count:
            self.current_count = self.max_count
            self.count_label.setText(str(self.current_count))
            self._animate_count_change(self.current_count)
            # 重新更新按钮状态
            self.increase_button.setEnabled(self.current_count < self.max_count)
            self.decrease_button.setEnabled(self.current_count > 1)
            # 只有在不在抽取过程中时才根据人数条件启用/禁用即抽按钮
            if not self.is_drawing:
                self.instant_draw_button.setEnabled(self.current_count <= self.max_count and self.current_count > 0)
    
    def _reset_count(self):
        # 小鸟游星野：重置抽取人数和已抽取名单 ✧(๑•̀ㅂ•́)๑
        self.current_count = 1
        self._animate_count_change(self.current_count)
        self._update_count_display()
        self._clean_temp_files()

    # 清理临时文件
    def _clean_temp_files(self):
        import glob
        temp_dir = path_manager.get_temp_path()
        if path_manager.file_exists(temp_dir):
            for file in glob.glob(f"{temp_dir}/until_*.json"):
                try:
                    path_manager.remove_file(file)
                    logger.info(f"已清理临时抽取记录文件: {file}")
                except Exception as e:
                    logger.error(f"清理临时抽取记录文件失败: {e}")

    def _load_classes(self):
        # 初始化班级下拉框
        self.class_combo = ComboBox()
        self.class_combo.setFixedSize(180, 50)
        self.class_combo.setFont(QFont(load_custom_font(), 13))
        # 加载班级列表
        try:
            list_folder = path_manager.get_resource_path("list")
            if path_manager.file_exists(list_folder) and os.path.isdir(list_folder):
                files = os.listdir(list_folder)
                classes = []
                for file in files:
                    if file.endswith('.json'):
                        class_name = os.path.splitext(file)[0]
                        classes.append(class_name)
                
                self.class_combo.clear()
                if classes:
                    self.class_combo.addItems(classes)
                else:
                    logger.error("你暂未添加班级")
                    self.class_combo.addItem("你暂未添加班级")
            else:
                logger.error("你暂未添加班级")
                self.class_combo.addItem("你暂未添加班级")
        except Exception as e:
            logger.error(f"加载班级列表失败: {str(e)}")
            self.class_combo.addItem("加载班级列表失败")

    def _load_groups(self):
        # 小组下拉框
        self.group_combo = ComboBox()
        self.group_combo.setFixedSize(180, 50)
        self.group_combo.setFont(QFont(load_custom_font(), 13))
        self.group_combo.addItem('抽取全班学生')
        self.group_combo.currentIndexChanged.connect(self.update_total_count)

        class_name = self.class_combo.currentText()
        pumping_people_file = path_manager.get_resource_path("list", f"{class_name}.json")
        try:
            if path_manager.file_exists(pumping_people_file):
                with open_file(pumping_people_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    groups = set()
                    for student_name, student_info in data.items():
                        if isinstance(student_info, dict) and 'id' in student_info:
                            id = student_info.get('id', '')
                            name = student_name.replace('【', '').replace('】', '')
                            gender = student_info.get('gender', '')
                            group = student_info.get('group', '')
                            if group:  # 只添加非空小组
                                groups.add(group)
                    cleaned_data = sorted(list(groups), key=lambda x: self.sort_key(str(x)))
                    if groups:
                        self.group_combo.addItem('抽取小组组号')
                        self.group_combo.addItems(cleaned_data)
                    else:
                        logger.error("你暂未添加小组")
                        self.group_combo.addItem("你暂未添加小组")
            else:
                logger.error("你暂未添加小组")
                self.group_combo.addItem("你暂未添加小组")
        except Exception as e:
            logger.error(f"加载小组列表失败: {str(e)}")
            self.group_combo.addItem("加载小组列表失败")
        
    def _load_genders(self):
        # 性别下拉框
        self.gender_combo = ComboBox()
        self.gender_combo.setFixedSize(180, 50)
        self.gender_combo.setFont(QFont(load_custom_font(), 13))
        self.gender_combo.addItem('抽取所有性别')
        self.gender_combo.currentIndexChanged.connect(self.update_total_count)

        class_name = self.class_combo.currentText()
        pumping_people_file = path_manager.get_resource_path("list", f"{class_name}.json")
        try:
            if path_manager.file_exists(pumping_people_file):
                with open_file(pumping_people_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    genders = set()
                    for student_name, student_info in data.items():
                        if isinstance(student_info, dict) and 'id' in student_info:
                            id = student_info.get('id', '')
                            name = student_name.replace('【', '').replace('】', '')
                            gender = student_info.get('gender', '')
                            group = student_info.get('group', '')
                            if gender:  # 只添加非空小组
                                genders.add(gender)
                    cleaned_data = sorted(list(genders), key=lambda x: self.sort_key(str(x)))
                    if genders:
                        self.gender_combo.addItems(cleaned_data)
                    else:
                        logger.error("你暂未添加性别")
                        self.gender_combo.addItem("你暂未添加性别")
            else:
                logger.error("你暂未添加性别")
                self.gender_combo.addItem("你暂未添加性别")
        except Exception as e:
            logger.error(f"加载性别列表失败: {str(e)}")
            self.gender_combo.addItem("加载性别列表失败")

    # 将小组名称转换为排序键
    def sort_key(self, group):
        # 尝试匹配 '第X小组' 或 '第X组' 格式
        match = re.match(r'第\s*(\d+|一|二|三|四|五|六|七|八|九|十)\s*(小组|组)', group)
        if match:
            num = match.group(1)
            num_map = {'一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9, '十': 10}
            if num in num_map:
                return (1, num_map[num])  # 类型1: 中文数字组
            else:
                return (1, int(num))       # 类型1: 阿拉伯数字组
        
        # 尝试匹配仅数字格式
        try:
            return (2, int(group))         # 类型2: 纯数字组
        except ValueError:
            pass
        
        # 🌟 星穹铁道白露：自定义组名直接使用中文排序啦~
        return (3, group) # ✨ 小鸟游星野：类型3: 其他名称组，保持排序功能不变

    def update_total_count(self):
        """更新总人数"""
        self._load_classes()
        self._load_groups()
        self._load_genders()
            
        class_name = self.class_combo.currentText()
        group_name = self.group_combo.currentText()
        gender_name = self.gender_combo.currentText()

        student_file = path_manager.get_resource_path("list", f"{class_name}.json")

        cleaned_data = self._get_cleaned_data(student_file, group_name, gender_name)

        self.max_count = len(cleaned_data)
    
    def _show_instant_draw_window(self):
        # 小鸟游星野：显示即抽窗口 - 使用_show_direct_extraction_window传递抽取人数 ✧(๑•̀ㅂ•́)๑
        try:
            # 确保当前抽取人数已设置
            if not hasattr(self, 'current_count'):
                self.current_count = 1

            self.update_total_count()
            
            # 调用直接抽取窗口方法，会自动传递抽取人数
            self._show_direct_extraction_window(self.current_count)
            
        except Exception as e:
            logger.error(f"执行抽取功能失败: {e}")
            error_dialog = Dialog("抽取失败", f"执行抽取功能时发生错误: {str(e)}", self)
            error_dialog.yesButton.setText("确定")
            error_dialog.cancelButton.hide()
            error_dialog.buttonLayout.insertStretch(1)
            error_dialog.exec()
