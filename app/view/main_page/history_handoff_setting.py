from qfluentwidgets import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from app.common.config import cfg, AUTHOR, VERSION, YEAR
from app.common.config import load_custom_font

from app.view.main_page.history import history
from app.view.main_page.history_reward import history_reward

class history_handoff_setting(QFrame):
    def __init__(self, parent: QFrame = None):
        super().__init__(parent=parent)
        
        # 标记是否首次加载
        self.first_load = True
        
        # 创建SegmentedWidget导航栏
        self.SegmentedWidget = SegmentedWidget(self)
        self.stackedWidget = QStackedWidget(self)
        
        # 创建内容页面
        self.pumping_people_page = QWidget()
        self.pumping_reward_page = QWidget()
        
        # 添加子页面
        self.addSubInterface(self.pumping_people_page, 'pumping_People_history', '点名记录')
        self.addSubInterface(self.pumping_reward_page, 'pumping_Reward_history', '抽奖记录')

        # 点名历史记录 - 后台创建
        # 创建滚动区域
        self.pumping_people_scroll_area_personal = SingleDirectionScrollArea(self.pumping_people_page)
        self.pumping_people_scroll_area_personal.setWidgetResizable(True)
        # 设置样式表
        self.pumping_people_scroll_area_personal.setStyleSheet("""
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
        QScroller.grabGesture(self.pumping_people_scroll_area_personal.viewport(), QScroller.LeftMouseButtonGesture)
        # 创建内部框架
        self.pumping_people_inner_frame_personal = QWidget(self.pumping_people_scroll_area_personal)
        self.pumping_people_inner_layout_personal = QVBoxLayout(self.pumping_people_inner_frame_personal)
        self.pumping_people_inner_layout_personal.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignTop)
        self.pumping_people_scroll_area_personal.setWidget(self.pumping_people_inner_frame_personal)
        # 点名历史记录卡片组 - 后台创建
        self.pumping_people_created = False
        # 设置点名历史记录页面布局
        self.pumping_people_layout = QVBoxLayout(self.pumping_people_page)
        self.pumping_people_layout.addWidget(self.pumping_people_scroll_area_personal)

        # 抽奖历史记录 - 后台创建
        # 创建滚动区域
        self.pumping_reward_scroll_area_personal = SingleDirectionScrollArea(self.pumping_reward_page)
        self.pumping_reward_scroll_area_personal.setWidgetResizable(True)
        # 设置样式表
        self.pumping_reward_scroll_area_personal.setStyleSheet("""
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
        QScroller.grabGesture(self.pumping_reward_scroll_area_personal.viewport(), QScroller.LeftMouseButtonGesture)
        # 创建内部框架
        self.pumping_reward_inner_frame_personal = QWidget(self.pumping_reward_scroll_area_personal)
        self.pumping_reward_inner_layout_personal = QVBoxLayout(self.pumping_reward_inner_frame_personal)
        self.pumping_reward_inner_layout_personal.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignTop)
        self.pumping_reward_scroll_area_personal.setWidget(self.pumping_reward_inner_frame_personal)
        # 抽奖历史记录卡片组 - 后台创建
        self.pumping_reward_created = False
        # 设置抽奖历史记录页面布局
        self.pumping_reward_layout = QVBoxLayout(self.pumping_reward_page)
        self.pumping_reward_layout.addWidget(self.pumping_reward_scroll_area_personal)
        
        # 设置主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addWidget(self.SegmentedWidget, 0, Qt.AlignHCenter)
        main_layout.addWidget(self.stackedWidget)
        
        self.stackedWidget.setCurrentWidget(self.pumping_people_page)
        self.SegmentedWidget.setCurrentItem('pumping_People_history')

        self.__initWidget()
        self.__connectSignalToSlot()
        
        # 后台创建历史记录卡片，避免堵塞进程
        QTimer.singleShot(0, self.create_history_cards)
        
    def addSubInterface(self, widget: QWidget, objectName: str, text: str):
        widget.setObjectName(objectName)
        self.stackedWidget.addWidget(widget)
        
        # 添加导航项
        self.SegmentedWidget.addItem(
            routeKey=objectName,
            text=text,
            onClick=lambda: self.stackedWidget.setCurrentWidget(widget)
        )

    def __initWidget(self):
        """初始化窗口部件"""
        # 设置窗口属性
        self.setObjectName("history_handoff_setting")

    def __connectSignalToSlot(self):
        cfg.themeChanged.connect(setTheme)
        self.stackedWidget.currentChanged.connect(self.onCurrentIndexChanged)
        
    def onCurrentIndexChanged(self, index):
        widget = self.stackedWidget.widget(index)
        self.SegmentedWidget.setCurrentItem(widget.objectName())

        # 所有卡片和数据已在后台创建和加载，无需在切换页面时加载
        # 首次加载后设置标志
        self.first_load = False
    
    def create_history_cards(self):
        """后台创建历史记录卡片并加载数据，避免堵塞进程"""
        self.create_pumping_people_card()
        self.create_pumping_reward_card()
        # 启动后台数据加载
        QTimer.singleShot(100, self.load_all_data)
    
    def load_all_data(self):
        """后台加载所有历史记录数据"""
        # 加载点名历史记录数据
        if self.pumping_people_created and hasattr(self, 'pumping_people_card'):
            self.pumping_people_card.load_data()
        
        # 加载抽奖历史记录数据
        if self.pumping_reward_created and hasattr(self, 'pumping_reward_card'):
            self.pumping_reward_card.load_data()
    
    def create_pumping_people_card(self):
        """后台创建点名历史记录卡片"""
        if self.pumping_people_created:
            return
            
        self.pumping_people_card = history(load_on_init=False)
        self.pumping_people_inner_layout_personal.addWidget(self.pumping_people_card)
        self.pumping_people_created = True
    
    def create_pumping_reward_card(self):
        """后台创建抽奖历史记录卡片"""
        if self.pumping_reward_created:
            return
            
        self.pumping_reward_card = history_reward(load_on_init=False)
        self.pumping_reward_inner_layout_personal.addWidget(self.pumping_reward_card)
        self.pumping_reward_created = True