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
        
        # 创建Pivot导航栏
        self.pivot = Pivot(self)
        self.stackedWidget = QStackedWidget(self)
        
        # 创建内容页面
        self.pumping_people_page = QWidget()
        self.pumping_reward_page = QWidget()
        
        # 添加子页面
        self.addSubInterface(self.pumping_people_page, 'pumping_People_history', '抽人记录')
        self.addSubInterface(self.pumping_reward_page, 'pumping_Reward_history', '抽奖记录')

        # 抽人历史记录
        # 创建滚动区域
        pumping_people_scroll_area_personal = SingleDirectionScrollArea(self.pumping_people_page)
        pumping_people_scroll_area_personal.setWidgetResizable(True)
        # 设置样式表
        pumping_people_scroll_area_personal.setStyleSheet("""
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
        QScroller.grabGesture(pumping_people_scroll_area_personal.viewport(), QScroller.LeftMouseButtonGesture)
        # 创建内部框架
        pumping_people_inner_frame_personal = QWidget(pumping_people_scroll_area_personal)
        pumping_people_inner_layout_personal = QVBoxLayout(pumping_people_inner_frame_personal)
        pumping_people_inner_layout_personal.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignTop)
        pumping_people_scroll_area_personal.setWidget(pumping_people_inner_frame_personal)
        # 抽人历史记录卡片组
        self.pumping_people_card = history(load_on_init=False)
        pumping_people_inner_layout_personal.addWidget(self.pumping_people_card)
        # 设置抽人历史记录页面布局
        pumping_people_layout = QVBoxLayout(self.pumping_people_page)
        pumping_people_layout.addWidget(pumping_people_scroll_area_personal)

        # 抽奖历史记录
        # 创建滚动区域
        pumping_reward_scroll_area_personal = SingleDirectionScrollArea(self.pumping_reward_page)
        pumping_reward_scroll_area_personal.setWidgetResizable(True)
        # 设置样式表
        pumping_reward_scroll_area_personal.setStyleSheet("""
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
        QScroller.grabGesture(pumping_reward_scroll_area_personal.viewport(), QScroller.LeftMouseButtonGesture)
        # 创建内部框架
        pumping_reward_inner_frame_personal = QWidget(pumping_reward_scroll_area_personal)
        pumping_reward_inner_layout_personal = QVBoxLayout(pumping_reward_inner_frame_personal)
        pumping_reward_inner_layout_personal.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignTop)
        pumping_reward_scroll_area_personal.setWidget(pumping_reward_inner_frame_personal)
        # 抽奖历史记录卡片组
        self.pumping_reward_card = history_reward(load_on_init=False)
        pumping_reward_inner_layout_personal.addWidget(self.pumping_reward_card)
        # 设置抽奖历史记录页面布局
        pumping_reward_layout = QVBoxLayout(self.pumping_reward_page)
        pumping_reward_layout.addWidget(pumping_reward_scroll_area_personal)
        
        # 设置主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addWidget(self.pivot, 0, Qt.AlignHCenter)
        main_layout.addWidget(self.stackedWidget)
        
        self.stackedWidget.setCurrentWidget(self.pumping_people_page)
        self.pivot.setCurrentItem('pumping_People_history')

        self.__connectSignalToSlot()
        
    def addSubInterface(self, widget: QWidget, objectName: str, text: str):
        widget.setObjectName(objectName)
        self.stackedWidget.addWidget(widget)
        
        # 添加导航项
        self.pivot.addItem(
            routeKey=objectName,
            text=text,
            onClick=lambda: self.stackedWidget.setCurrentWidget(widget)
        )

    def __connectSignalToSlot(self):
        cfg.themeChanged.connect(setTheme)
        self.stackedWidget.currentChanged.connect(self.onCurrentIndexChanged)
        
    def onCurrentIndexChanged(self, index):
        widget = self.stackedWidget.widget(index)
        self.pivot.setCurrentItem(widget.objectName())

        # 根据页面切换加载对应数据
        if widget.objectName() == 'pumping_People_history':
            self.pumping_people_card.load_data()
        elif widget.objectName() == 'pumping_Reward_history':
            self.pumping_reward_card.load_data()

        # 首次加载后设置标志
        self.first_load = False
        
        # 页面切换时加载对应的数据
        if widget.objectName() == 'pumping_People_history':
            self.pumping_people_card.load_data()
        elif widget.objectName() == 'pumping_Reward_history':
            self.pumping_reward_card.load_data()