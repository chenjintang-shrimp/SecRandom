from qfluentwidgets import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from app.common.config import cfg, load_custom_font

from app.view.plugins.management import PluginManagementPage
from app.view.plugins.market import PluginMarketPage
from app.view.plugins.settings import PluginSettingsPage

class PluginHandoffWindow(QFrame):
    def __init__(self, parent: QFrame = None):
        super().__init__(parent=parent)
        
        # 创建SegmentedWidget导航栏
        self.SegmentedWidget = SegmentedWidget(self)
        self.stackedWidget = QStackedWidget(self)
        
        # 创建内容页面
        self.plugin_management_page = QWidget()
        self.plugin_market_page = QWidget()
        self.plugin_settings_page = QWidget()
        
        # 添加子页面
        self.addSubInterface(self.plugin_management_page, 'plugin_management', '插件管理')
        self.addSubInterface(self.plugin_market_page, 'plugin_market', '插件广场')
        self.addSubInterface(self.plugin_settings_page, 'plugin_settings', '插件设置')

        # 插件管理页面
        # 创建滚动区域
        plugin_management_scroll_area = SingleDirectionScrollArea(self.plugin_management_page)
        plugin_management_scroll_area.setWidgetResizable(True)
        # 设置样式表
        plugin_management_scroll_area.setStyleSheet("""
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
        QScroller.grabGesture(plugin_management_scroll_area.viewport(), QScroller.LeftMouseButtonGesture)
        # 创建内部框架
        plugin_management_inner_frame = QWidget(plugin_management_scroll_area)
        plugin_management_inner_layout = QVBoxLayout(plugin_management_inner_frame)
        plugin_management_inner_layout.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignTop)
        plugin_management_scroll_area.setWidget(plugin_management_inner_frame)
        # 插件管理内容标签
        plugin_management_label = PluginManagementPage()
        plugin_management_inner_layout.addWidget(plugin_management_label)
        # 设置插件管理页面布局
        plugin_management_layout = QVBoxLayout(self.plugin_management_page)
        plugin_management_layout.addWidget(plugin_management_scroll_area)

        # 插件广场页面
        # 创建滚动区域
        plugin_market_scroll_area = SingleDirectionScrollArea(self.plugin_market_page)
        plugin_market_scroll_area.setWidgetResizable(True)
        # 设置样式表
        plugin_market_scroll_area.setStyleSheet("""
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
        QScroller.grabGesture(plugin_market_scroll_area.viewport(), QScroller.LeftMouseButtonGesture)
        # 创建内部框架
        plugin_market_inner_frame = QWidget(plugin_market_scroll_area)
        plugin_market_inner_layout = QVBoxLayout(plugin_market_inner_frame)
        plugin_market_inner_layout.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignTop)
        plugin_market_scroll_area.setWidget(plugin_market_inner_frame)
        # 插件广场内容标签
        plugin_market_label = PluginMarketPage()
        plugin_market_inner_layout.addWidget(plugin_market_label)
        # 设置插件广场页面布局
        plugin_market_layout = QVBoxLayout(self.plugin_market_page)
        plugin_market_layout.addWidget(plugin_market_scroll_area)

        # 插件设置页面
        # 创建滚动区域
        plugin_settings_scroll_area = SingleDirectionScrollArea(self.plugin_settings_page)
        plugin_settings_scroll_area.setWidgetResizable(True)
        # 设置样式表
        plugin_settings_scroll_area.setStyleSheet("""
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
        QScroller.grabGesture(plugin_settings_scroll_area.viewport(), QScroller.LeftMouseButtonGesture)
        # 创建内部框架
        plugin_settings_inner_frame = QWidget(plugin_settings_scroll_area)
        plugin_settings_inner_layout = QVBoxLayout(plugin_settings_inner_frame)
        plugin_settings_inner_layout.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignTop)
        plugin_settings_scroll_area.setWidget(plugin_settings_inner_frame)
        # 插件设置内容标签
        plugin_settings_label = PluginSettingsPage()
        plugin_settings_inner_layout.addWidget(plugin_settings_label)
        # 设置插件设置页面布局
        plugin_settings_layout = QVBoxLayout(self.plugin_settings_page)
        plugin_settings_layout.addWidget(plugin_settings_scroll_area)
        
        # 设置主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addWidget(self.SegmentedWidget, 0, Qt.AlignHCenter)
        main_layout.addWidget(self.stackedWidget)
        
        self.stackedWidget.setCurrentWidget(self.plugin_management_page)
        self.SegmentedWidget.setCurrentItem('plugin_management')

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
        
        # 页面切换时可以在这里添加对应的逻辑
        if widget.objectName() == 'plugin_management':
            pass  # 插件管理页面逻辑
        elif widget.objectName() == 'plugin_market':
            pass  # 插件广场页面逻辑
        elif widget.objectName() == 'plugin_settings':
            pass  # 插件设置页面逻辑