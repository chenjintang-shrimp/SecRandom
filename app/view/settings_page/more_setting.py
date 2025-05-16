from venv import logger
import os
import sys

from qfluentwidgets import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

from ..common.config import cfg, AUTHOR, VERSION, YEAR
from ..common.config import load_custom_font

from ..common.foundation_settings import foundation_settingsCard
from ..common.senior_settings import senior_settingsCard
from ..common.about import aboutCard


class more_setting(QFrame):
    def __init__(self, parent: QFrame = None):
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
        QScroller.grabGesture(scroll_area_personal.viewport(), QScroller.LeftMouseButtonGesture)

        # 创建一个内部的 QFrame 用于放置内容
        inner_frame_personal = QWidget(scroll_area_personal)
        inner_layout_personal = QVBoxLayout(inner_frame_personal)
        inner_layout_personal.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignTop)

        # 基础设置卡片组
        foundation_settings_Card = foundation_settingsCard()
        inner_layout_personal.addWidget(foundation_settings_Card)

        # # 高级设置卡片组
        # senior_settings_Card = senior_settingsCard()
        # inner_layout_personal.addWidget(senior_settings_Card)

        self.aboutCard = aboutCard()
        inner_layout_personal.addWidget(self.aboutCard)

        # 创建个性化卡片组
        self.themeAndZoomCard = SettingCardGroup("个性化", self)

        # 界面缩放设置卡片
        self.zoomCard = OptionsSettingCard(
            cfg.dpiScale,
            QIcon("app/resource/assets/ic_fluent_zoom_fit_20_filled.svg"),
            self.tr("界面缩放"),
            self.tr("更改界面和字体的大小"),
            texts=["100%", "125%", "150%", "175%", "200%", self.tr("使用系统设置"),]
        )
        
        # 添加组件到分组中
        self.themeAndZoomCard.addSettingCard(self.zoomCard)
        
        # 将卡片组添加到布局中
        inner_layout_personal.addWidget(self.themeAndZoomCard)

        # 将内部的 QFrame 设置为 QScrollArea 的内容
        scroll_area_personal.setWidget(inner_frame_personal)

        # 设置主布局
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(scroll_area_personal)

        self.__connectSignalToSlot()

    def __connectSignalToSlot(self):
        cfg.themeChanged.connect(setTheme)
