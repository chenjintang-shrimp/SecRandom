from qfluentwidgets import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from app.common.config import cfg, AUTHOR, VERSION, YEAR
from app.common.config import load_custom_font

from app.common.fixed_url_setting import fixed_url_SettinsCard
from app.common.theme_settings import theme_settingsCard
from app.common.sidebar_settings import sidebar_settingsCard
from app.common.tray_settings import tray_settingsCard
from app.common.floating_window_settings import floating_window_settingsCard
from app.common.roll_call_settings import roll_call_settingsCard
from app.common.rewards_settings import reward_settingsCard
from app.common.instant_draw_settings import instant_draw_settingsCard
from app.common.Program_functionality_settings import Program_functionality_settingsCard

class custom_setting(QFrame):
    # 背景设置变化信号
    background_settings_changed = pyqtSignal()
    
    def __init__(self, parent: QFrame = None):
        super().__init__(parent=parent)
        
        # 创建SegmentedWidget导航栏
        self.SegmentedWidget = SegmentedWidget(self)
        self.stackedWidget = QStackedWidget(self)
        
        # 创建内容页面
        self.fixed_url_page = QWidget()
        self.user_defined_url_page = QWidget()
        self.theme_settings_page = QWidget()
        self.sidebar_settings_page = QWidget()
        self.floating_window_page = QWidget()
        self.extraction_management_page = QWidget()
        self.Program_functionality_settings_page = QWidget()
        
        # 添加子页面
        self.addSubInterface(self.extraction_management_page, 'extraction_management', '抽取设置')
        self.addSubInterface(self.sidebar_settings_page, 'sidebar_settings', '侧边/托盘设置')
        self.addSubInterface(self.floating_window_page, 'floating_window', '浮窗设置')
        self.addSubInterface(self.fixed_url_page, 'fixed_url_setting', 'Url管理')
        self.addSubInterface(self.theme_settings_page, 'theme_settings', '主题设置')
        self.addSubInterface(self.Program_functionality_settings_page, 'Program_functionality_settings', '软件功能设置')

        # 固定Url设置
        # 创建滚动区域
        fixed_url_scroll_area = SingleDirectionScrollArea(self.fixed_url_page)
        fixed_url_scroll_area.setWidgetResizable(True)
        # 设置样式表
        fixed_url_scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollArea QWidget {
                border: none;
                background-color: transparent;
            }
        """)
        # 启用鼠标滚轮
        QScroller.grabGesture(fixed_url_scroll_area.viewport(), QScroller.LeftMouseButtonGesture)
        # 创建内部框架
        fixed_url_inner_frame = QWidget(fixed_url_scroll_area)
        fixed_url_inner_layout = QVBoxLayout(fixed_url_inner_frame)
        fixed_url_inner_layout.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignTop)
        fixed_url_scroll_area.setWidget(fixed_url_inner_frame)
        # 固定Url设置卡片组
        fixed_url_card = fixed_url_SettinsCard()
        fixed_url_inner_layout.addWidget(fixed_url_card)
        # 设置固定Url设置页面布局
        fixed_url_layout = QVBoxLayout(self.fixed_url_page)
        fixed_url_layout.addWidget(fixed_url_scroll_area)

        # 主题设置
        # 创建滚动区域
        theme_settings_scroll_area = SingleDirectionScrollArea(self.theme_settings_page)
        theme_settings_scroll_area.setWidgetResizable(True)
        # 设置样式表
        theme_settings_scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollArea QWidget {
                border: none;
                background-color: transparent;
            }
        """)
        # 启用鼠标滚轮
        QScroller.grabGesture(theme_settings_scroll_area.viewport(), QScroller.LeftMouseButtonGesture)
        # 创建内部框架
        theme_settings_inner_frame = QWidget(theme_settings_scroll_area)
        theme_settings_inner_layout = QVBoxLayout(theme_settings_inner_frame)
        theme_settings_inner_layout.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignTop)
        theme_settings_scroll_area.setWidget(theme_settings_inner_frame)
        # 主题设置卡片组
        self.theme_settings_card = theme_settingsCard()
        theme_settings_inner_layout.addWidget(self.theme_settings_card)
        # 连接主题设置卡片的背景设置变化信号
        self.theme_settings_card.background_settings_changed.connect(self.on_background_settings_changed)
        # 设置主题设置页面布局
        theme_settings_layout = QVBoxLayout(self.theme_settings_page)
        theme_settings_layout.addWidget(theme_settings_scroll_area)

        # 侧边栏设置
        # 创建滚动区域
        sidebar_settings_scroll_area = SingleDirectionScrollArea(self.sidebar_settings_page)
        sidebar_settings_scroll_area.setWidgetResizable(True)
        # 设置样式表
        sidebar_settings_scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollArea QWidget {
                border: none;
                background-color: transparent;
            }
        """)
        # 启用鼠标滚轮
        QScroller.grabGesture(sidebar_settings_scroll_area.viewport(), QScroller.LeftMouseButtonGesture)
        # 创建内部框架
        sidebar_settings_inner_frame = QWidget(sidebar_settings_scroll_area)
        sidebar_settings_inner_layout = QVBoxLayout(sidebar_settings_inner_frame)
        sidebar_settings_inner_layout.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignTop)
        sidebar_settings_scroll_area.setWidget(sidebar_settings_inner_frame)
        
        # 创建分隔线
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("background-color: rgba(0, 0, 0, 0.1); margin: 10px 0;")
        
        # 侧边栏设置卡片组
        sidebar_settings_card = sidebar_settingsCard()
        sidebar_settings_inner_layout.addWidget(sidebar_settings_card)
        sidebar_settings_inner_layout.addWidget(separator)
        
        # 系统托盘设置卡片组
        tray_settings_card = tray_settingsCard()
        sidebar_settings_inner_layout.addWidget(tray_settings_card)
        
        # 设置侧边栏设置页面布局
        sidebar_settings_layout = QVBoxLayout(self.sidebar_settings_page)
        sidebar_settings_layout.addWidget(sidebar_settings_scroll_area)

        # 浮窗管理设置
        # 创建滚动区域
        floating_window_scroll_area = SingleDirectionScrollArea(self.floating_window_page)
        floating_window_scroll_area.setWidgetResizable(True)
        # 设置样式表
        floating_window_scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollArea QWidget {
                border: none;
                background-color: transparent;
            }
        """)
        # 启用鼠标滚轮
        QScroller.grabGesture(floating_window_scroll_area.viewport(), QScroller.LeftMouseButtonGesture)
        # 创建内部框架
        floating_window_inner_frame = QWidget(floating_window_scroll_area)
        floating_window_inner_layout = QVBoxLayout(floating_window_inner_frame)
        floating_window_inner_layout.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignTop)
        floating_window_scroll_area.setWidget(floating_window_inner_frame)
        # 浮窗管理设置卡片组
        floating_window_card = floating_window_settingsCard()
        floating_window_inner_layout.addWidget(floating_window_card)
        # 设置浮窗管理设置页面布局
        floating_window_layout = QVBoxLayout(self.floating_window_page)
        floating_window_layout.addWidget(floating_window_scroll_area)

        # 抽取管理设置
        # 创建滚动区域
        extraction_management_scroll_area = SingleDirectionScrollArea(self.extraction_management_page)
        extraction_management_scroll_area.setWidgetResizable(True)
        # 设置样式表
        extraction_management_scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollArea QWidget {
                border: none;
                background-color: transparent;
            }
        """)
        # 启用鼠标滚轮
        QScroller.grabGesture(extraction_management_scroll_area.viewport(), QScroller.LeftMouseButtonGesture)
        # 创建内部框架
        extraction_management_inner_frame = QWidget(extraction_management_scroll_area)
        extraction_management_inner_layout = QVBoxLayout(extraction_management_inner_frame)
        extraction_management_inner_layout.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignTop)
        extraction_management_scroll_area.setWidget(extraction_management_inner_frame)
        
        # 创建分隔线
        separator1 = QFrame()
        separator1.setFrameShape(QFrame.HLine)
        separator1.setFrameShadow(QFrame.Sunken)
        separator1.setStyleSheet("background-color: rgba(0, 0, 0, 0.1); margin: 10px 0;")
        
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.HLine)
        separator2.setFrameShadow(QFrame.Sunken)
        separator2.setStyleSheet("background-color: rgba(0, 0, 0, 0.1); margin: 10px 0;")
        
        # 点名界面设置卡片组
        roll_call_card = roll_call_settingsCard()
        extraction_management_inner_layout.addWidget(roll_call_card)
        extraction_management_inner_layout.addWidget(separator1)
        
        # 抽奖界面设置卡片组
        reward_card = reward_settingsCard()
        extraction_management_inner_layout.addWidget(reward_card)
        extraction_management_inner_layout.addWidget(separator2)
        
        # 即抽管理设置卡片组
        instant_draw_card = instant_draw_settingsCard()
        extraction_management_inner_layout.addWidget(instant_draw_card)
        
        # 设置抽取管理设置页面布局
        extraction_management_layout = QVBoxLayout(self.extraction_management_page)
        extraction_management_layout.addWidget(extraction_management_scroll_area)

        # 软件功能设置
        # 创建滚动区域
        Program_functionality_settings_scroll_area = SingleDirectionScrollArea(self.Program_functionality_settings_page)
        Program_functionality_settings_scroll_area.setWidgetResizable(True)
        # 设置样式表
        Program_functionality_settings_scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollArea QWidget {
                border: none;
                background-color: transparent;
            }
        """)
        # 启用鼠标滚轮
        QScroller.grabGesture(Program_functionality_settings_scroll_area.viewport(), QScroller.LeftMouseButtonGesture)
        # 创建内部框架
        Program_functionality_settings_inner_frame = QWidget(Program_functionality_settings_scroll_area)
        Program_functionality_settings_inner_layout = QVBoxLayout(Program_functionality_settings_inner_frame)
        Program_functionality_settings_inner_layout.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignTop)
        Program_functionality_settings_scroll_area.setWidget(Program_functionality_settings_inner_frame)
        # 软件功能设置卡片组
        Program_functionality_settings_card = Program_functionality_settingsCard()
        Program_functionality_settings_inner_layout.addWidget(Program_functionality_settings_card)
        # 设置软件功能设置页面布局
        Program_functionality_settings_layout = QVBoxLayout(self.Program_functionality_settings_page)
        Program_functionality_settings_layout.addWidget(Program_functionality_settings_scroll_area)
        
        # 设置主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addWidget(self.SegmentedWidget, 0, Qt.AlignHCenter)
        main_layout.addWidget(self.stackedWidget)
        
        self.stackedWidget.setCurrentWidget(self.extraction_management_page)
        self.SegmentedWidget.setCurrentItem('extraction_management')

        self.__connectSignalToSlot()
        
    def addSubInterface(self, widget: QWidget, objectName: str, text: str):
        widget.setObjectName(objectName)
        self.stackedWidget.addWidget(widget)
        
        # 添加导航项
        self.SegmentedWidget.addItem(
            routeKey=objectName,
            text=text,
            onClick=lambda: self.stackedWidget.setCurrentWidget(widget)
        )

    def __connectSignalToSlot(self):
        cfg.themeChanged.connect(setTheme)
        self.stackedWidget.currentChanged.connect(self.onCurrentIndexChanged)
        
    def onCurrentIndexChanged(self, index):
        widget = self.stackedWidget.widget(index)
        self.SegmentedWidget.setCurrentItem(widget.objectName())
    
    def on_background_settings_changed(self):
        """处理背景设置变化信号"""
        # 发送信号给上层设置界面
        self.background_settings_changed.emit()