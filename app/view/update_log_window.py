#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新日志窗口模块
(^・ω・^ ) 白露的更新日志窗口魔法！
显示新版本的更新内容和版本信息～ ✨
"""

import os
import json
from loguru import logger
from datetime import datetime
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from qfluentwidgets import *

# 🏰 应用内部魔法卷轴 🏰
from app.common.config import get_theme_icon, load_custom_font, VERSION

class UpdateLogWindow(QWidget):
    """(^・ω・^ ) 白露的更新日志窗口类！
    专门用于显示新版本更新内容的窗口～ ✨"""
    
    # 信号定义
    close_signal = pyqtSignal()  # 关闭窗口信号
    
    def __init__(self, parent=None):
        """(^・ω・^ ) 白露的初始化魔法！
        初始化更新日志窗口～ ✨"""
        super().__init__(parent)
        
        # 窗口基本设置
        self.setWindowTitle(f'更新日志 - v{VERSION}')
        self.setFixedSize(900, 600)
        self.setWindowFlags(Qt.Dialog | Qt.WindowCloseButtonHint)
        
        # 当前页面索引和总页数
        self.current_page_index = 0
        self.total_pages = 3  # 更新内容、版本信息、完成页面
        
        # 初始化UI
        self.init_ui()
        
        logger.info("白露更新日志: 更新日志窗口初始化完成～ ✧*｡٩(ˊᗜˋ*)و✧*｡")
    
    def init_ui(self):
        """(^・ω・^ ) 白露的UI初始化魔法！
        创建更新日志窗口的所有UI组件～ ✨"""
        
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 创建导航栏
        self.navigation_interface = NavigationInterface(self, showReturnButton=False)
        self.navigation_interface.setFixedWidth(150)
        
        # 创建内容区域
        self.content_widget = QWidget()
        self.content_widget.setObjectName("contentWidget")
        content_layout = QVBoxLayout(self.content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(20)
        
        # 创建各个页面
        self.create_update_content_page()
        self.create_version_info_page()
        self.create_complete_page()
        
        # 初始化导航
        self.init_navigation()
        
        # 创建底部按钮区域
        self.create_bottom_buttons()
        
        # 添加到主布局
        content_wrapper = QWidget()
        content_wrapper_layout = QHBoxLayout(content_wrapper)
        content_wrapper_layout.setContentsMargins(0, 0, 0, 0)
        content_wrapper_layout.addWidget(self.navigation_interface)
        content_wrapper_layout.addWidget(self.content_widget)
        content_wrapper_layout.setStretch(1, 1)
        
        main_layout.addWidget(content_wrapper)
        
        # 设置样式
        self.setStyleSheet("""
            QWidget#contentWidget {
                background: #f8f9fa;
            }
        """)
        
        # 显示第一个页面
        self.switch_to_current_page()
        self.update_navigation_buttons()
    
    def create_update_content_page(self):
        """(^・ω・^ ) 白露的更新内容页面魔法！
        创建显示更新内容的页面～ ✨"""
        
        self.update_content_interface = QWidget()
        layout = QVBoxLayout(self.update_content_interface)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)
        
        # 标题
        title = TitleLabel(f'🎉 新版本 v{VERSION} 更新内容')
        title.setFont(QFont(load_custom_font(), 24, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # 更新时间
        update_time = BodyLabel(f'更新时间：{self.get_current_time_string()}')
        update_time.setFont(QFont(load_custom_font(), 12))
        update_time.setAlignment(Qt.AlignCenter)
        update_time.setStyleSheet('color: #666666;')
        layout.addWidget(update_time)
        
        # 分隔线
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet('background: #dddddd;')
        layout.addWidget(separator)
        
        # 更新内容区域
        content_scroll = QScrollArea()
        content_scroll.setWidgetResizable(True)
        content_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(15)
        
        # 获取更新内容
        update_items = self.get_update_content()
        
        for category, items in update_items.items():
            # 分类标题
            category_label = SubtitleLabel(category)
            category_label.setFont(QFont(load_custom_font(), 18, QFont.Bold))
            content_layout.addWidget(category_label)
            
            # 更新项列表
            for item in items:
                item_widget = QWidget()
                item_layout = QHBoxLayout(item_widget)
                item_layout.setContentsMargins(10, 8, 10, 8)
                
                # 项目符号
                bullet = BodyLabel('•')
                bullet.setFont(QFont(load_custom_font(), 16, QFont.Bold))
                bullet.setStyleSheet('color: #007bff; margin-right: 10px;')
                item_layout.addWidget(bullet)
                
                # 项目内容
                item_text = BodyLabel(item)
                item_text.setFont(QFont(load_custom_font(), 14))
                item_text.setStyleSheet('color: #333333;')
                item_text.setWordWrap(True)
                item_layout.addWidget(item_text)
                
                content_layout.addWidget(item_widget)
            
            # 添加间距
            content_layout.addSpacing(10)
        
        content_layout.addStretch()
        content_scroll.setWidget(content_widget)
        layout.addWidget(content_scroll)
    
    def create_version_info_page(self):
        """(^・ω・^ ) 白露的版本信息页面魔法！
        创建显示版本详细信息的页面～ ✨"""
        
        self.version_info_interface = QWidget()
        layout = QVBoxLayout(self.version_info_interface)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)
        
        # 标题
        title = TitleLabel('📋 版本信息')
        title.setFont(QFont(load_custom_font(), 24, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # 版本信息卡片
        info_card = QWidget()
        info_card.setStyleSheet('background: white; border-radius: 8px; padding: 20px;')
        info_layout = QVBoxLayout(info_card)
        info_layout.setSpacing(15)
        
        # 版本号
        version_row = QWidget()
        version_row_layout = QHBoxLayout(version_row)
        version_row_layout.setContentsMargins(0, 0, 0, 0)
        
        version_label = StrongBodyLabel('当前版本：')
        version_label.setFont(QFont(load_custom_font(), 14))
        version_label.setStyleSheet('color: #666666;')
        version_row_layout.addWidget(version_label)
        
        version_value = StrongBodyLabel(f'v{VERSION}')
        version_value.setFont(QFont(load_custom_font(), 14, QFont.Bold))
        version_value.setStyleSheet('color: #007bff;')
        version_row_layout.addWidget(version_value)
        
        version_row_layout.addStretch()
        info_layout.addWidget(version_row)
        
        # 构建信息
        build_info = self.get_build_info()
        for key, value in build_info.items():
            info_row = QWidget()
            info_row_layout = QHBoxLayout(info_row)
            info_row_layout.setContentsMargins(0, 0, 0, 0)
            
            info_label = StrongBodyLabel(f'{key}：')
            info_label.setFont(QFont(load_custom_font(), 14))
            info_label.setStyleSheet('color: #666666;')
            info_row_layout.addWidget(info_label)
            
            info_value = BodyLabel(value)
            info_value.setFont(QFont(load_custom_font(), 14))
            info_value.setStyleSheet('color: #333333;')
            info_row_layout.addWidget(info_value)
            
            info_row_layout.addStretch()
            info_layout.addWidget(info_row)
        
        layout.addWidget(info_card)
        
        # 更新说明
        note_card = QWidget()
        note_card.setStyleSheet('background: #e3f2fd; border-radius: 8px; padding: 15px;')
        note_layout = QVBoxLayout(note_card)
        
        note_title = StrongBodyLabel('💡 温馨提示')
        note_title.setFont(QFont(load_custom_font(), 16, QFont.Bold))
        note_title.setStyleSheet('color: #1976d2;')
        note_layout.addWidget(note_title)
        
        note_text = BodyLabel('本次更新包含重要的功能改进和错误修复，建议您仔细阅读更新内容。如遇到问题，请通过官方渠道反馈。')
        note_text.setFont(QFont(load_custom_font(), 14))
        note_text.setStyleSheet('color: #333333;')
        note_text.setWordWrap(True)
        note_layout.addWidget(note_text)
        
        layout.addWidget(note_card)
        layout.addStretch()
    
    def create_complete_page(self):
        """(^・ω・^ ) 白露的完成页面魔法！
        创建更新日志完成页面～ ✨"""
        
        self.complete_interface = QWidget()
        layout = QVBoxLayout(self.complete_interface)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)
        
        # 标题
        title = TitleLabel('🎊 更新完成')
        title.setFont(QFont(load_custom_font(), 24, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # 完成图标
        icon_label = QLabel()
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet('font-size: 80px;')
        icon_label.setText('✨')
        layout.addWidget(icon_label)
        
        # 完成信息
        complete_text = BodyLabel('您已了解本次更新的所有内容')
        complete_text.setFont(QFont(load_custom_font(), 16))
        complete_text.setAlignment(Qt.AlignCenter)
        complete_text.setStyleSheet('color: #333333;')
        layout.addWidget(complete_text)
        
        # 感谢信息
        thanks_text = BodyLabel('感谢您的支持与使用！')
        thanks_text.setFont(QFont(load_custom_font(), 14))
        thanks_text.setAlignment(Qt.AlignCenter)
        thanks_text.setStyleSheet('color: #666666;')
        layout.addWidget(thanks_text)
        
        layout.addStretch()
    
    def init_navigation(self):
        """(^・ω・^ ) 白露的导航初始化魔法！
        创建导航栏和连接信号～ ✨"""
        
        # 添加页面到导航
        update_item = self.navigation_interface.addSubInterface(
            self.update_content_interface, FluentIcon.UPDATE, '更新内容', 
            position=NavigationItemPosition.TOP
        )
        version_item = self.navigation_interface.addSubInterface(
            self.version_info_interface, FluentIcon.INFO, '版本信息', 
            position=NavigationItemPosition.TOP
        )
        complete_item = self.navigation_interface.addSubInterface(
            self.complete_interface, FluentIcon.CHECK_MARK, '完成', 
            position=NavigationItemPosition.TOP
        )
        
        # 连接导航信号
        update_item.clicked.connect(lambda: self.on_navigation_changed(self.update_content_interface))
        version_item.clicked.connect(lambda: self.on_navigation_changed(self.version_info_interface))
        complete_item.clicked.connect(lambda: self.on_navigation_changed(self.complete_interface))
    
    def create_bottom_buttons(self):
        """(^・ω・^ ) 白露的底部按钮魔法！
        创建底部导航按钮区域～ ✨"""
        
        # 按钮容器
        self.button_container = QWidget()
        self.button_container.setFixedHeight(60)
        self.button_container.setStyleSheet('background: white; border-top: 1px solid #dddddd;')
        
        button_layout = QHBoxLayout(self.button_container)
        button_layout.setContentsMargins(20, 10, 20, 10)
        
        # 上一个按钮
        self.prev_button = PushButton('← 上一个')
        self.prev_button.setFont(QFont(load_custom_font(), 14))
        self.prev_button.clicked.connect(self.show_previous_page)
        self.prev_button.setEnabled(False)
        
        # 页面指示器
        self.page_label = BodyLabel('1 / 3')
        self.page_label.setFont(QFont(load_custom_font(), 14))
        self.page_label.setAlignment(Qt.AlignCenter)
        
        # 下一个按钮
        self.next_button = PushButton('下一个 →')
        self.next_button.setFont(QFont(load_custom_font(), 14))
        self.next_button.clicked.connect(self.show_next_page)
        
        # 完成按钮（最后一页显示）
        self.complete_button = PrimaryPushButton('✨ 完成')
        self.complete_button.setFont(QFont(load_custom_font(), 14))
        self.complete_button.clicked.connect(self.complete_update)
        self.complete_button.hide()
        
        button_layout.addWidget(self.prev_button)
        button_layout.addStretch()
        button_layout.addWidget(self.page_label)
        button_layout.addStretch()
        button_layout.addWidget(self.next_button)
        button_layout.addWidget(self.complete_button)
        
        # 添加到主布局
        main_layout = self.layout()
        if main_layout:
            main_layout.addWidget(self.button_container)
    
    def on_navigation_changed(self, interface):
        """(^・ω・^ ) 白露的导航切换魔法！
        处理导航项点击事件～ ✨"""
        
        if interface == self.update_content_interface:
            self.current_page_index = 0
        elif interface == self.version_info_interface:
            self.current_page_index = 1
        elif interface == self.complete_interface:
            self.current_page_index = 2
        
        self.update_navigation_buttons()
    
    def show_previous_page(self):
        """(^・ω・^ ) 白露的上一页魔法！
        切换到上一页～ ✨"""
        if self.current_page_index > 0:
            self.current_page_index -= 1
            self.switch_to_current_page()
            self.update_navigation_buttons()
    
    def show_next_page(self):
        """(^・ω・^ ) 白露的下一页魔法！
        切换到下一页～ ✨"""
        if self.current_page_index < self.total_pages - 1:
            self.current_page_index += 1
            self.switch_to_current_page()
            self.update_navigation_buttons()
    
    def switch_to_current_page(self):
        """(^・ω・^ ) 白露的页面切换魔法！
        切换到当前页面～ ✨"""
        if self.current_page_index == 0:
            self.navigation_interface.switchTo(self.update_content_interface)
        elif self.current_page_index == 1:
            self.navigation_interface.switchTo(self.version_info_interface)
        elif self.current_page_index == 2:
            self.navigation_interface.switchTo(self.complete_interface)
    
    def update_navigation_buttons(self):
        """(^・ω・^ ) 白露的按钮更新魔法！
        更新按钮状态和显示～ ✨"""
        
        # 更新页面指示器
        self.page_label.setText(f'{self.current_page_index + 1} / {self.total_pages}')
        
        # 更新上一个按钮状态
        self.prev_button.setEnabled(self.current_page_index > 0)
        
        # 更新下一个/完成按钮显示
        if self.current_page_index < self.total_pages - 1:
            self.next_button.show()
            self.complete_button.hide()
        else:
            self.next_button.hide()
            self.complete_button.show()
    
    def complete_update(self):
        """(^・ω・^ ) 白露的完成更新魔法！
        用户完成查看更新日志～ ✨"""
        logger.info("白露更新日志: 用户完成查看更新日志～ ")
        
        # 更新版本信息文件
        self.update_version_file()
        
        # 关闭窗口
        self.close()
        
        # 发射关闭信号
        self.close_signal.emit()
    
    def update_version_file(self):
        """(^・ω・^ ) 白露的版本文件更新魔法！
        更新引导完成文件中的版本信息～ ✨"""
        
        guide_complete_file = 'app/Settings/guide_complete.json'
        
        try:
            if os.path.exists(guide_complete_file):
                with open(guide_complete_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # 更新版本号
                data['version'] = VERSION
                data['last_update_time'] = self.get_current_time_string()
                
                with open(guide_complete_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)
                
                logger.info("白露更新日志: 版本信息文件更新成功～ ✧*｡٩(ˊᗜˋ*)و✧*｡")
        except Exception as e:
            logger.error(f"白露错误: 更新版本信息文件失败: {e}")
    
    def get_update_content(self):
        """(^・ω・^ ) 白露的更新内容获取魔法！
        获取当前版本的更新内容～ ✨"""
        return {
            '🚀 新功能': [
                '新增更新日志界面,方便用户了解版本更新内容',
                '新增MD5校验功能,检验捐献支持二维码是否被篡改',
                '新增'
            ],
            '🐛 问题修复': [
                '优化引导流程,区分首次使用和版本更新情况',
                '解决引导界面在版本更新时错误显示的问题',
                '优化文件路径处理，提高跨平台兼容性'
            ],
            '💡 体验优化': [
                '优化界面布局，提升视觉体验',
                '改进字体加载机制，确保字体显示正常',
                '增强日志记录，便于问题排查'
            ]
        }
    
    def get_build_info(self):
        """(^・ω・^ ) 白露的构建信息获取魔法！
        获取构建相关信息～ ✨"""
        
        return {
            '构建时间': self.get_current_time_string(),
            '构建环境': 'Windows',
            'Python版本': '3.8+',
            'Qt版本': '5.15+'
        }
    
    def get_current_time_string(self):
        """(^・ω・^ ) 白露的时间获取魔法！
        获取当前时间字符串～ ✨"""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def closeEvent(self, event):
        """(^・ω・^ ) 白露的窗口关闭魔法！
        处理窗口关闭事件～ ✨"""
        logger.debug("白露更新日志: 更新日志窗口已关闭～ ")
        super().closeEvent(event)


# 测试代码
if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    window = UpdateLogWindow()
    window.show()
    sys.exit(app.exec_())