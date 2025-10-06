from qfluentwidgets import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from loguru import logger

from app.common.config import cfg, AUTHOR, VERSION, YEAR
from app.common.config import load_custom_font

from app.common.pumping_people_setting import pumping_people_SettinsCard
from app.common.instant_draw_setting import instant_draw_SettinsCard
from app.common.list_settings import list_SettinsCard
from app.common.pumping_reward_setting import pumping_reward_SettinsCard
from app.common.reward_settings import reward_SettinsCard  

class pumping_handoff_setting(QFrame):
    def __init__(self, parent: QFrame = None):
        super().__init__(parent=parent)
        
        # 添加界面完全初始化标志
        self.interface_fully_initialized = False
        
        # 创建SegmentedWidget导航栏
        self.SegmentedWidget = SegmentedWidget(self)
        self.stackedWidget = QStackedWidget(self)
        
        # 创建内容页面
        self.pumping_people_page = QWidget()
        self.instant_draw_page = QWidget()
        self.pumping_people_list_page = QWidget()
        self.pumping_reward_page = QWidget()
        self.pumping_reward_list_page = QWidget()
        
        # 添加子页面
        self.addSubInterface(self.pumping_people_page, 'pumping_People_setting', '点名设置')
        self.addSubInterface(self.instant_draw_page, 'instant_Draw_setting', '闪抽设置')
        self.addSubInterface(self.pumping_people_list_page, 'pumping_People_list', '点名名单')
        self.addSubInterface(self.pumping_reward_page, 'pumping_Reward_setting', '抽奖设置')
        self.addSubInterface(self.pumping_reward_list_page, 'pumping_Reward_list', '抽奖名单')

        # 点名设置
        # 创建滚动区域
        self.pumping_people_scroll_area_personal = SingleDirectionScrollArea(self.pumping_people_page)
        self.pumping_people_scroll_area_personal.setObjectName("pumping_people_scroll_area")
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
        # 点名设置卡片组 - 后台创建
        self.pumping_people_created = False
        # pumping_people_card = pumping_people_SettinsCard()
        # self.pumping_people_inner_layout_personal.addWidget(pumping_people_card)
        # 设置点名设置页面布局
        pumping_people_layout = QVBoxLayout(self.pumping_people_page)
        pumping_people_layout.addWidget(self.pumping_people_scroll_area_personal)

        # 闪抽设置
        # 创建滚动区域
        self.instant_draw_scroll_area_personal = SingleDirectionScrollArea(self.instant_draw_page)
        self.instant_draw_scroll_area_personal.setObjectName("instant_draw_scroll_area")
        self.instant_draw_scroll_area_personal.setWidgetResizable(True)
        # 设置样式表
        self.instant_draw_scroll_area_personal.setStyleSheet("""
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
        QScroller.grabGesture(self.instant_draw_scroll_area_personal.viewport(), QScroller.LeftMouseButtonGesture)
        # 创建内部框架
        self.instant_draw_inner_frame_personal = QWidget(self.instant_draw_scroll_area_personal)
        self.instant_draw_inner_layout_personal = QVBoxLayout(self.instant_draw_inner_frame_personal)
        self.instant_draw_inner_layout_personal.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignTop)
        self.instant_draw_scroll_area_personal.setWidget(self.instant_draw_inner_frame_personal)
        # 闪抽设置卡片组 - 后台创建
        self.instant_draw_created = False
        # instant_draw_card = instant_draw_SettinsCard()
        # self.instant_draw_inner_layout_personal.addWidget(instant_draw_card)
        # 设置闪抽设置页面布局  
        instant_draw_layout = QVBoxLayout(self.instant_draw_page)
        instant_draw_layout.addWidget(self.instant_draw_scroll_area_personal)
        
        # 连接信号：当pumping_people设置更新时，通知instant_draw刷新UI - 后台创建
        # pumping_people_card.settings_updated.connect(instant_draw_card.on_pumping_people_settings_updated)

        # 点名名单
        # 创建滚动区域
        self.pumping_people_list_scroll_area_personal = SingleDirectionScrollArea(self.pumping_people_list_page)
        self.pumping_people_list_scroll_area_personal.setObjectName("pumping_people_list_scroll_area")
        self.pumping_people_list_scroll_area_personal.setWidgetResizable(True)
        # 设置样式表
        self.pumping_people_list_scroll_area_personal.setStyleSheet("""
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
        QScroller.grabGesture(self.pumping_people_list_scroll_area_personal.viewport(), QScroller.LeftMouseButtonGesture)
        # 创建内部框架
        self.pumping_people_list_inner_frame_personal = QWidget(self.pumping_people_list_scroll_area_personal)
        self.pumping_people_list_inner_layout_personal = QVBoxLayout(self.pumping_people_list_inner_frame_personal)
        self.pumping_people_list_inner_layout_personal.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignTop)
        self.pumping_people_list_scroll_area_personal.setWidget(self.pumping_people_list_inner_frame_personal)
        # 点名名单设置卡片组 - 后台创建
        self.pumping_people_list_created = False
        # pumping_people_list_card = list_SettinsCard()
        # self.pumping_people_list_inner_layout_personal.addWidget(pumping_people_list_card)
        # 设置点名名单设置页面布局
        pumping_people_list_layout = QVBoxLayout(self.pumping_people_list_page)
        pumping_people_list_layout.addWidget(self.pumping_people_list_scroll_area_personal)

        # 抽奖设置
        # 创建滚动区域
        self.pumping_reward_scroll_area_personal = SingleDirectionScrollArea(self.pumping_reward_page)
        self.pumping_reward_scroll_area_personal.setObjectName("pumping_reward_scroll_area")
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
        # 抽奖设置卡片组 - 后台创建
        self.pumping_reward_created = False
        # personal_setting_card = pumping_reward_SettinsCard()
        # self.pumping_reward_inner_layout_personal.addWidget(personal_setting_card)
        # 设置抽奖设置页面布局
        pumping_reward_layout = QVBoxLayout(self.pumping_reward_page)
        pumping_reward_layout.addWidget(self.pumping_reward_scroll_area_personal)

        # 抽奖奖项
        # 创建滚动区域
        self.pumping_reward_list_scroll_area_personal = SingleDirectionScrollArea(self.pumping_reward_list_page)
        self.pumping_reward_list_scroll_area_personal.setObjectName("pumping_reward_list_scroll_area")
        self.pumping_reward_list_scroll_area_personal.setWidgetResizable(True)
        # 设置样式表
        self.pumping_reward_list_scroll_area_personal.setStyleSheet("""
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
        QScroller.grabGesture(self.pumping_reward_list_scroll_area_personal.viewport(), QScroller.LeftMouseButtonGesture)
        # 创建内部框架
        self.pumping_reward_list_inner_frame_personal = QWidget(self.pumping_reward_list_scroll_area_personal)
        self.pumping_reward_list_inner_layout_personal = QVBoxLayout(self.pumping_reward_list_inner_frame_personal)
        self.pumping_reward_list_inner_layout_personal.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignTop)
        self.pumping_reward_list_scroll_area_personal.setWidget(self.pumping_reward_list_inner_frame_personal)
        # 抽奖奖项设置卡片组 - 后台创建
        self.pumping_reward_list_created = False
        # personal_setting_card = reward_SettinsCard()
        # self.pumping_reward_list_inner_layout_personal.addWidget(personal_setting_card)
        # 设置抽奖设置页面布局
        pumping_reward_list_layout = QVBoxLayout(self.pumping_reward_list_page)
        pumping_reward_list_layout.addWidget(self.pumping_reward_list_scroll_area_personal)
        
        # 设置主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addWidget(self.SegmentedWidget, 0, Qt.AlignHCenter)
        main_layout.addWidget(self.stackedWidget)
        
        self.stackedWidget.setCurrentWidget(self.pumping_people_page)
        self.SegmentedWidget.setCurrentItem('pumping_People_setting')

        self.__connectSignalToSlot()
        
        # 启动后台加载所有设置卡片，增加延迟时间确保界面完全初始化
        QTimer.singleShot(500, self.create_all_settings_cards)
        
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
        
    def create_all_settings_cards(self):
        """后台创建所有设置卡片"""
        try:
            # 创建点名设置卡片
            if not self.pumping_people_created:
                self.create_pumping_people_card()
            
            # 创建闪抽设置卡片
            if not self.instant_draw_created:
                self.create_instant_draw_card()
            
            # 创建点名名单卡片
            if not self.pumping_people_list_created:
                self.create_pumping_people_list_card()
            
            # 创建抽奖设置卡片
            if not self.pumping_reward_created:
                self.create_pumping_reward_card()
            
            # 创建抽奖奖项卡片
            if not self.pumping_reward_list_created:
                self.create_pumping_reward_list_card()
            
            # 设置界面完全初始化完成标志
            self.interface_fully_initialized = True
        except Exception as e:
            logger.error(f"创建设置卡片时出错: {str(e)}")
            # 尝试逐个创建卡片，避免一个卡片创建失败影响其他卡片
            try:
                if not self.pumping_people_created:
                    self.create_pumping_people_card()
            except Exception as e:
                logger.error(f"创建点名设置卡片失败: {str(e)}")
            
            try:
                if not self.instant_draw_created:
                    self.create_instant_draw_card()
            except Exception as e:
                logger.error(f"创建闪抽设置卡片失败: {str(e)}")
            
            try:
                if not self.pumping_people_list_created:
                    self.create_pumping_people_list_card()
            except Exception as e:
                logger.error(f"创建点名名单卡片失败: {str(e)}")
            
            try:
                if not self.pumping_reward_created:
                    self.create_pumping_reward_card()
            except Exception as e:
                logger.error(f"创建抽奖设置卡片失败: {str(e)}")
            
            try:
                if not self.pumping_reward_list_created:
                    self.create_pumping_reward_list_card()
            except Exception as e:
                logger.error(f"创建抽奖奖项卡片失败: {str(e)}")
            
            # 即使有错误，也设置界面完全初始化完成标志
            self.interface_fully_initialized = True
        
    def onCurrentIndexChanged(self, index):
        widget = self.stackedWidget.widget(index)
        self.SegmentedWidget.setCurrentItem(widget.objectName())
        
        # 所有卡片已在后台创建，无需在切换页面时创建
            
    def create_pumping_people_card(self):
        """后台创建点名设置卡片"""
        try:
            # 直接使用实例变量访问滚动区域和内部框架
            if not hasattr(self, 'pumping_people_scroll_area_personal'):
                logger.error("无法找到点名设置页面的滚动区域")
                return
                
            inner_frame = self.pumping_people_inner_frame_personal
            if not inner_frame:
                logger.error("无法找到点名设置页面的内部框架")
                return
                
            layout = self.pumping_people_inner_layout_personal
            if layout is None:
                logger.error("无法找到点名设置页面的布局")
                return
                
            # 创建点名设置卡片
            pumping_people_card = pumping_people_SettinsCard()
            layout.addWidget(pumping_people_card)
            
            # 如果闪抽设置卡片已经创建，连接信号
            if self.instant_draw_created:
                # 直接使用实例变量访问闪抽设置卡片
                if hasattr(self, 'instant_draw_inner_layout_personal') and self.instant_draw_inner_layout_personal:
                    # 查找闪抽设置卡片
                    for i in range(self.instant_draw_inner_layout_personal.count()):
                        widget = self.instant_draw_inner_layout_personal.itemAt(i).widget()
                        if isinstance(widget, instant_draw_SettinsCard):
                            pumping_people_card.settings_updated.connect(widget.on_pumping_people_settings_updated)
                            break
            
            self.pumping_people_created = True
        except Exception as e:
            logger.error(f"创建点名设置卡片时出错: {str(e)}")
                    
    def create_instant_draw_card(self):
        """后台创建闪抽设置卡片"""
        try:
            # 直接使用实例变量访问滚动区域和内部框架
            if not hasattr(self, 'instant_draw_scroll_area_personal'):
                logger.error("无法找到闪抽设置页面的滚动区域")
                return
                
            inner_frame = self.instant_draw_inner_frame_personal
            if inner_frame is None:
                logger.error("无法找到闪抽设置页面的内部框架")
                return
                
            layout = self.instant_draw_inner_layout_personal
            if layout is None:
                logger.error("无法找到闪抽设置页面的布局")
                return
                
            # 创建闪抽设置卡片
            instant_draw_card = instant_draw_SettinsCard()
            layout.addWidget(instant_draw_card)
            
            # 如果点名设置卡片已经创建，连接信号
            if self.pumping_people_created:
                # 直接使用实例变量访问点名设置卡片
                if hasattr(self, 'pumping_people_inner_layout_personal') and self.pumping_people_inner_layout_personal:
                    # 查找点名设置卡片
                    for i in range(self.pumping_people_inner_layout_personal.count()):
                        widget = self.pumping_people_inner_layout_personal.itemAt(i).widget()
                        if isinstance(widget, pumping_people_SettinsCard):
                            widget.settings_updated.connect(instant_draw_card.on_pumping_people_settings_updated)
                            break
            
            self.instant_draw_created = True
        except Exception as e:
            logger.error(f"创建闪抽设置卡片时出错: {str(e)}")
                    
    def create_pumping_people_list_card(self):
        """后台创建点名名单卡片"""
        try:
            # 直接使用实例变量访问滚动区域和内部框架
            if not hasattr(self, 'pumping_people_list_scroll_area_personal'):
                logger.error("无法找到点名名单页面的滚动区域")
                return
                
            inner_frame = self.pumping_people_list_inner_frame_personal
            if inner_frame is None:
                logger.error("无法找到点名名单页面的内部框架")
                return
                
            layout = self.pumping_people_list_inner_layout_personal
            if layout is None:
                logger.error("无法找到点名名单页面的布局")
                return
                
            # 创建点名名单卡片
            pumping_people_list_card = list_SettinsCard()
            layout.addWidget(pumping_people_list_card)
            self.pumping_people_list_created = True
        except Exception as e:
            logger.error(f"创建点名名单卡片时出错: {str(e)}")
                    
    def create_pumping_reward_card(self):
        """后台创建抽奖设置卡片"""
        try:
            # 直接使用实例变量访问滚动区域和内部框架
            if not hasattr(self, 'pumping_reward_scroll_area_personal'):
                logger.error("无法找到抽奖设置页面的滚动区域")
                return
                
            inner_frame = self.pumping_reward_inner_frame_personal
            if inner_frame is None:
                logger.error("无法找到抽奖设置页面的内部框架")
                return
                
            layout = self.pumping_reward_inner_layout_personal
            if layout is None:
                logger.error("无法找到抽奖设置页面的布局")
                return
                
            # 创建抽奖设置卡片
            pumping_reward_card = pumping_reward_SettinsCard()
            layout.addWidget(pumping_reward_card)
            self.pumping_reward_created = True
        except Exception as e:
            logger.error(f"创建抽奖设置卡片时出错: {str(e)}")
                    
    def create_pumping_reward_list_card(self):
        """后台创建抽奖奖项卡片"""
        try:
            # 直接使用实例变量访问滚动区域和内部框架
            if not hasattr(self, 'pumping_reward_list_scroll_area_personal'):
                logger.error("无法找到抽奖奖项页面的滚动区域")
                return
                
            inner_frame = self.pumping_reward_list_inner_frame_personal
            if inner_frame is None:
                logger.error("无法找到抽奖奖项页面的内部框架")
                return
                
            layout = self.pumping_reward_list_inner_layout_personal
            if layout is None:
                logger.error("无法找到抽奖奖项页面的布局")
                return
                
            # 创建抽奖奖项卡片
            pumping_reward_list_card = reward_SettinsCard()
            layout.addWidget(pumping_reward_list_card)
            self.pumping_reward_list_created = True
        except Exception as e:
            logger.error(f"创建抽奖奖项卡片时出错: {str(e)}")