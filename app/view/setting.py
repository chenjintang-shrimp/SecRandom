from qfluentwidgets import * # type: ignore
from qfluentwidgets import FluentIcon as FIF  # type: ignore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QFrame, QScrollArea, QVBoxLayout, QWidget, QScroller, QDialog, QHBoxLayout
# from loguru import logger

from ..common.config import cfg, AUTHOR, VERSION, YEAR # type: ignore
from ..common.config import load_custom_font
# 设置卡片
from ..common.list_settings import list_SettinsCard
from ..common.global_settings import global_SettinsCard
from ..common.single_player_settings import single_player_SettinsCard
from ..common.multi_player_settings import multi_player_SettinsCard
from ..common.group_player_settings import group_player_SettinsCard


class setting(QFrame):
    def __init__(self, parent: QFrame = None): # type: ignore
        super().__init__(parent=parent)

        # 创建一个 QScrollArea
        scroll_area_personal = QScrollArea(self)
        scroll_area_personal.setWidgetResizable(True)
        # 设置滚动条样式
        scroll_area_personal.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollArea QWidget {
                border: none;
                background-color: transparent;
            }
            /* 垂直滚动条整体 */
            QScrollBar:vertical {
                background-color: #E5DDF8;   /* 背景透明 */
                width: 8px;                    /* 宽度 */
                margin: 0px;                   /* 外边距 */
            }
            /* 垂直滚动条的滑块 */
            QScrollBar::handle:vertical {
                background-color: rgba(0, 0, 0, 0.3);    /* 半透明滑块 */
                border-radius: 4px;                      /* 圆角 */
                min-height: 20px;                        /* 最小高度 */
            }
            /* 鼠标悬停在滑块上 */
            QScrollBar::handle:vertical:hover {
                background-color: rgba(0, 0, 0, 0.5);
            }
            /* 滚动条的上下按钮和顶部、底部区域 */
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical,
            QScrollBar::up-arrow:vertical,
            QScrollBar::down-arrow:vertical {
                height: 0px;
            }
        
            /* 水平滚动条整体 */
            QScrollBar:horizontal {
                background-color: #E5DDF8;   /* 背景透明 */
                height: 8px;
                margin: 0px;
            }
            /* 水平滚动条的滑块 */
            QScrollBar::handle:horizontal {
                background-color: rgba(0, 0, 0, 0.3);
                border-radius: 4px;
                min-width: 20px;
            }
            /* 鼠标悬停在滑块上 */
            QScrollBar::handle:horizontal:hover {
                background-color: rgba(0, 0, 0, 0.5);
            }
            /* 滚动条的左右按钮和左侧、右侧区域 */
            QScrollBar::add-line:horizontal,
            QScrollBar::sub-line:horizontal,
            QScrollBar::left-arrow:horizontal,
            QScrollBar::right-arrow:horizontal {
                width: 0px;
            }
        """)
        # 启用触屏滚动
        QScroller.grabGesture(scroll_area_personal.viewport(), QScroller.LeftMouseButtonGesture) # type: ignore

        # 创建一个内部的 QFrame 用于放置内容
        inner_frame_personal = QWidget(scroll_area_personal)
        inner_layout_personal = QVBoxLayout(inner_frame_personal)
        inner_layout_personal.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignTop) # type: ignore

        # 创建标签并设置自定义字体
        settingLabel = SubtitleLabel("设置")
        settingLabel.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop) # type: ignore
        settingLabel.setWordWrap(True)
        settingLabel.setFont(QFont(load_custom_font(), 22))  # 设置自定义字体 # type: ignore

        # 名单设置卡片组
        self.list_setting_card = list_SettinsCard()
        inner_layout_personal.addWidget(self.list_setting_card)

        # 名单设置卡片组
        global_setting_card = global_SettinsCard()
        inner_layout_personal.addWidget(global_setting_card)

        # 抽单人设置卡片组
        single_player_setting_card = single_player_SettinsCard()
        inner_layout_personal.addWidget(single_player_setting_card)

        # 抽多人设置卡片组
        multi_player_setting_card = multi_player_SettinsCard()
        inner_layout_personal.addWidget(multi_player_setting_card)

        # 抽小组设置卡片组
        group_player_setting_card = group_player_SettinsCard()
        inner_layout_personal.addWidget(group_player_setting_card)

        # 创建个性化卡片组
        self.themeAndZoomCard = SettingCardGroup("个性化", self)
        
        # 应用主题设置卡片
        self.themeCard = OptionsSettingCard(
            cfg.themeMode,
            FluentIcon.BRUSH,
            "应用主题",
            "调整你的应用外观",
            ["浅色", "深色", "跟随系统设置"]
        )
        # 界面缩放设置卡片
        self.zoomCard = OptionsSettingCard(
            cfg.dpiScale,
            FIF.ZOOM,
            self.tr("界面缩放"),
            self.tr("更改界面和字体的大小"),
            texts=["100%", "125%", "150%", "175%", "200%", self.tr("使用系统设置"),]
        )
        
        # 添加组件到分组中
        self.themeAndZoomCard.addSettingCard(self.themeCard)
        self.themeAndZoomCard.addSettingCard(self.zoomCard)
        
        # 将卡片组添加到布局中
        inner_layout_personal.addWidget(self.themeAndZoomCard)

        # 将内部的 QFrame 设置为 QScrollArea 的内容
        scroll_area_personal.setWidget(inner_frame_personal)

        # 设置主布局
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(settingLabel)
        main_layout.addWidget(scroll_area_personal)
        # main_layout.addWidget(aboutLabel)
        # main_layout.addWidget(scroll_area_about)

        self.__initWidget()

    def __initWidget(self):
        self.__connectSignalToSlot()

    def __showRestartTooltip(self):
        InfoBar.success( # type: ignore
            self.tr('更新成功'),
            self.tr('设置在重启后生效'),
            duration=1500,
            parent=self
        )

    def __connectSignalToSlot(self):
        cfg.appRestartSig.connect(self.__showRestartTooltip)
        cfg.themeChanged.connect(setTheme)