# ================================================== ✧*｡٩(ˊᗜˋ*)و✧*｡
# 魔法导入水晶球 🔮
# ================================================== ✧*｡٩(ˊᗜˋ*)و✧*｡

# ✨ 系统自带魔法道具 ✨
import os
import json
import webbrowser
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from qfluentwidgets import *
from loguru import logger

# 🏰 应用内部魔法卷轴 🏰
from app.common.config import get_theme_icon, load_custom_font, VERSION


class UpdateLogWindow(MSFluentWindow):
    """(^・ω・^ ) 白露的更新日志精灵！
    为SecRandom用户提供更新日志查看功能～
    让用户了解每个版本的更新内容和新功能！✨"""
    
    # 定义信号
    start_signal_update = pyqtSignal()
    
    # 更新内容数据结构
    UPDATE_CONTENTS = {
        "major_updates": [
            '• 新增 更新日志界面,方便用户了解版本更新内容',
            '• 新增 MD5校验功能,检验捐献支持二维码是否被篡改'
        ],
        "feature_optimizations": [
            '• 优化 引导流程,区分首次使用和版本更新情况'
        ],
        "bug_fixes": [
            '• 修复 不开图片模式,字体显示异常的问题',
            '• 修复 不开图片模式,控件不居中的问题',
            '• 修复 插件管理界面自启动按钮问题',
            '• 修复 插件广场界面卸载插件时定位错误导致误卸载其他插件的问题',
            '• 修复 引导窗口关闭时,主窗口不启动的问题',
            '• 修复 引导窗口字体太大,导致内容看不全的问题',
            '• 修复 缩减插件广场的插件信息',
            '• 修复 历史记录界面,加载数据时,界面通知飞了一下的问题'
        ]
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('SecRandom 更新日志')
        self.setWindowIcon(QIcon('./app/resource/icon/SecRandom.png'))
        self.resize(800, 600)
        
        # 设置窗口居中
        self.center_window()
        
        # 创建更新日志界面
        self.setup_ui()
        
        logger.info("白露更新日志: 更新日志窗口已创建～ ")
    
    def center_window(self):
        """(^・ω・^ ) 白露的窗口居中魔法！
        让更新日志窗口出现在屏幕正中央，视觉效果最佳哦～ ✨"""
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)
    
    def setup_ui(self):
        """(^・ω・^ ) 白露的界面布置魔法！
        精心设计更新日志界面的布局和内容～ 让用户一目了然！(๑•̀ㅂ•́)و✧)"""
        
        # 创建更新日志页面
        self.create_update_log_pages()
        
        # 初始化导航系统
        self.initNavigation()
        
        # 显示第一个更新日志页面
        self.switchTo(self.currentVersionInterface)
        
        # 当前页面索引
        self.current_page_index = 0
        self.total_pages = 2
        
        # 将底部按钮容器添加到窗口主布局
        self.add_bottom_buttons()
    
    def create_update_log_pages(self):
        """(^・ω・^ ) 白露的更新日志页面创建魔法！
        创建简洁的更新日志页面，展示当前版本的更新内容～ ✨"""
        
        # 1. 当前版本页面
        self.currentVersionInterface = QWidget()
        self.currentVersionInterface.setObjectName("currentVersionInterface")
        current_layout = QVBoxLayout(self.currentVersionInterface)
        current_layout.setSpacing(15)
        current_layout.setContentsMargins(30, 30, 30, 30)
        current_layout.setAlignment(Qt.AlignTop)
        
        # 版本标题
        version_title = TitleLabel(f'🎉 当前版本：{VERSION}')
        version_title.setFont(QFont(load_custom_font(), 20))
        version_title.setAlignment(Qt.AlignCenter)
        current_layout.addWidget(version_title)
        
        # 主要更新
        major_widget = QWidget()
        major_layout = QVBoxLayout(major_widget)
        
        major_title = SubtitleLabel('🚀 主要更新')
        major_title.setFont(QFont(load_custom_font(), 16))
        major_layout.addWidget(major_title)
        
        major_updates = self.UPDATE_CONTENTS["major_updates"]
        
        for update in major_updates:
            update_label = BodyLabel(update)
            update_label.setFont(QFont(load_custom_font(), 12))
            update_label.setWordWrap(True)
            major_layout.addWidget(update_label)
        
        current_layout.addWidget(major_widget)
        
        # 功能优化
        opt_widget = QWidget()
        opt_layout = QVBoxLayout(opt_widget)
        
        opt_title = SubtitleLabel('💡 功能优化')
        opt_title.setFont(QFont(load_custom_font(), 16))
        opt_layout.addWidget(opt_title)
        
        opt_updates = self.UPDATE_CONTENTS["feature_optimizations"]
        
        for update in opt_updates:
            update_label = BodyLabel(update)
            update_label.setFont(QFont(load_custom_font(), 12))
            update_label.setWordWrap(True)
            opt_layout.addWidget(update_label)
        
        current_layout.addWidget(opt_widget)
        
        # 问题修复
        fix_widget = QWidget()
        fix_layout = QVBoxLayout(fix_widget)
        
        fix_title = SubtitleLabel('🐛 修复问题')
        fix_title.setFont(QFont(load_custom_font(), 16))
        fix_layout.addWidget(fix_title)
        
        fix_updates = self.UPDATE_CONTENTS["bug_fixes"]
        
        for update in fix_updates:
            update_label = BodyLabel(update)
            update_label.setFont(QFont(load_custom_font(), 12))
            update_label.setWordWrap(True)
            fix_layout.addWidget(update_label)
        
        current_layout.addWidget(fix_widget)
        current_layout.addStretch()
        
        # 2. 关于页面
        self.aboutInterface = QWidget()
        self.aboutInterface.setObjectName("aboutInterface")
        about_layout = QVBoxLayout(self.aboutInterface)
        about_layout.setSpacing(15)
        about_layout.setContentsMargins(30, 30, 30, 30)
        about_layout.setAlignment(Qt.AlignTop)
        
        # 关于标题
        about_title = TitleLabel('ℹ️ 关于')
        about_title.setFont(QFont(load_custom_font(), 20))
        about_title.setAlignment(Qt.AlignCenter)
        about_layout.addWidget(about_title)
        
        # 版本信息
        version_info = BodyLabel(f'SecRandom {VERSION}')
        version_info.setFont(QFont(load_custom_font(), 16))
        version_info.setAlignment(Qt.AlignCenter)
        about_layout.addWidget(version_info)
        
        # 说明
        desc_widget = QWidget()
        desc_layout = QVBoxLayout(desc_widget)
        
        desc_content = BodyLabel(
            'SecRandom 是一个简洁易用的随机抽取工具，\n'
            '支持抽人和抽奖功能，为您的活动提供便利。\n\n'
            '感谢您的使用和支持！'
        )
        desc_content.setFont(QFont(load_custom_font(), 12))
        desc_content.setWordWrap(True)
        desc_content.setAlignment(Qt.AlignCenter)
        desc_layout.addWidget(desc_content)
        
        about_layout.addWidget(desc_widget)
        about_layout.addStretch()
    
    def initNavigation(self):
        """(^・ω・^ ) 白露的导航系统初始化魔法！
        创建顶部导航栏和底部按钮区域～ ✨"""
        
        # 添加更新日志页面到导航并获取导航项
        current_item = self.addSubInterface(self.currentVersionInterface, '📋', '更新日志', position=NavigationItemPosition.TOP)
        about_item = self.addSubInterface(self.aboutInterface, 'ℹ️', '关于', position=NavigationItemPosition.TOP)
        
        # 创建底部导航按钮区域
        self.nav_button_container = QWidget()
        self.nav_button_container.setObjectName("navButtonContainer")
        self.nav_button_container.setFixedHeight(60)
        nav_button_layout = QHBoxLayout(self.nav_button_container)
        nav_button_layout.setContentsMargins(90, 10, 20, 10)
        
        # 上一个按钮
        self.prev_button = PushButton('← 上一个')
        self.prev_button.setFont(QFont(load_custom_font(), 12))
        self.prev_button.clicked.connect(self.show_previous_page)
        self.prev_button.setEnabled(False)  # 第一页时禁用
        
        # 页面指示器
        self.page_label = BodyLabel('1 / 2')
        self.page_label.setFont(QFont(load_custom_font(), 12))
        self.page_label.setAlignment(Qt.AlignCenter)
        
        # 下一个按钮
        self.next_button = PushButton('下一个 →')
        self.next_button.setFont(QFont(load_custom_font(), 12))
        self.next_button.clicked.connect(self.show_next_page)
        
        # 关闭按钮
        self.close_button = PrimaryPushButton('❌ 关闭')
        self.close_button.setFont(QFont(load_custom_font(), 12))
        self.close_button.clicked.connect(self.close_window)
        
        nav_button_layout.addWidget(self.prev_button)
        nav_button_layout.addStretch()
        nav_button_layout.addWidget(self.page_label)
        nav_button_layout.addStretch()
        nav_button_layout.addWidget(self.next_button)
        nav_button_layout.addWidget(self.close_button)
        
        # 连接导航切换信号
        current_item.clicked.connect(lambda: self.on_navigation_changed(self.currentVersionInterface))
        about_item.clicked.connect(lambda: self.on_navigation_changed(self.aboutInterface))
    
    def on_navigation_changed(self, interface):
        """(^・ω・^ ) 白露的导航切换魔法！
        当用户点击导航项时更新页面状态～ ✨"""
        
        # 更新当前页面索引
        if interface == self.currentVersionInterface:
            self.current_page_index = 0
        elif interface == self.aboutInterface:
            self.current_page_index = 1
        
        self.update_navigation_buttons()
    
    def show_previous_page(self):
        """(^・ω・^ ) 白露的上一页魔法！
        切换到上一个更新日志页面～ ✨"""
        if self.current_page_index > 0:
            self.current_page_index -= 1
            self.switch_to_current_page()
            self.update_navigation_buttons()
    
    def show_next_page(self):
        """(^・ω・^ ) 白露的下一页魔法！
        切换到下一个更新日志页面～ ✨"""
        if self.current_page_index < self.total_pages - 1:
            self.current_page_index += 1
            self.switch_to_current_page()
            self.update_navigation_buttons()
    
    def switch_to_current_page(self):
        """(^・ω・^ ) 白露的页面切换魔法！
        根据当前索引切换到对应的更新日志页面～ ✨"""
        if self.current_page_index == 0:
            self.switchTo(self.currentVersionInterface)
        elif self.current_page_index == 1:
            self.switchTo(self.aboutInterface)
    
    def update_navigation_buttons(self):
        """(^・ω・^ ) 白露的按钮状态更新魔法！
        根据当前页面更新按钮状态和显示～ ✨"""
        
        # 更新页面指示器
        self.page_label.setText(f'{self.current_page_index + 1} / {self.total_pages}')
        
        # 更新上一个按钮状态
        self.prev_button.setEnabled(self.current_page_index > 0)
        
        # 更新下一个按钮状态
        self.next_button.setEnabled(self.current_page_index < self.total_pages - 1)
    
    def close_window(self):
        """(^・ω・^ ) 白露的窗口关闭魔法！
        关闭更新日志窗口并发送打开主界面信号～ ✨"""
        logger.info("白露更新日志: 用户关闭更新日志窗口，准备打开主界面～ ")
        # 发射信号通知主程序打开主界面
        self.start_signal_update.emit()
        self.close()
    
    def add_bottom_buttons(self):
        """(^・ω・^ ) 白露的底部按钮添加魔法！
        将按钮容器添加到窗口底部～ ✨"""
        # 设置按钮容器的父对象为窗口
        self.nav_button_container.setParent(self)
        
        # 将按钮容器移动到窗口底部
        self.nav_button_container.move(0, self.height() - 60)
        
        # 设置按钮容器宽度与窗口相同
        self.nav_button_container.setFixedWidth(self.width())
        
        # 显示按钮容器
        self.nav_button_container.show()
        
        # 连接窗口大小改变事件，以调整按钮容器位置
        self.resizeEvent = self.on_window_resized
    
    def on_window_resized(self, event):
        """(^・ω・^ ) 白露的窗口大小调整魔法！
        当窗口大小改变时调整按钮容器的位置和大小～ ✨"""
        # 调用父类的resizeEvent
        super().resizeEvent(event)
        
        # 调整按钮容器的位置和大小
        if hasattr(self, 'nav_button_container'):
            self.nav_button_container.move(0, self.height() - 60)
            self.nav_button_container.setFixedWidth(self.width())
    
    def closeEvent(self, event):
        """(^・ω・^ ) 白露的窗口关闭魔法！
        确保更新日志窗口关闭时正确清理资源并发送打开主界面信号～ ✨"""
        logger.debug("白露更新日志: 更新日志窗口已关闭，准备打开主界面～ ")
        # 发射信号通知主程序打开主界面
        self.start_signal_update.emit()
        super().closeEvent(event)