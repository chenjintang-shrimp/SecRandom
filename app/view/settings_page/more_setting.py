from venv import logger
import os
import sys

from qfluentwidgets import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

from app.common.config import cfg, AUTHOR, YEAR
from app.common.config import get_theme_icon, load_custom_font

from app.common.foundation_settings import foundation_settingsCard
from app.common.advanced_settings import advanced_settingsCard


class more_setting(QFrame):
    def __init__(self, parent: QFrame = None):
        super().__init__(parent=parent)

        # 创建一个 QScrollArea
        self.scroll_area_personal = SingleDirectionScrollArea(self)
        self.scroll_area_personal.setWidgetResizable(True)
        # 设置滚动条样式
        self.scroll_area_personal.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollArea QWidget {
                border: none;
                background-color: transparent;
            }
        """)
        # 启用触屏滚动
        QScroller.grabGesture(self.scroll_area_personal.viewport(), QScroller.LeftMouseButtonGesture)

        # 创建一个内部的 QFrame 用于放置内容
        self.inner_frame_personal = QWidget(self.scroll_area_personal)
        self.inner_layout_personal = QVBoxLayout(self.inner_frame_personal)
        self.inner_layout_personal.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignTop)

        # 基础设置卡片组 - 后台创建
        self.foundation_settings_created = False
        # foundation_settings_Card = foundation_settingsCard()
        # self.inner_layout_personal.addWidget(foundation_settings_Card)

        # 高级设置卡片组 - 后台创建
        self.advanced_settings_created = False
        # advanced_settings_Card = advanced_settingsCard()
        # self.inner_layout_personal.addWidget(advanced_settings_Card)

        # 将内部的 QFrame 设置为 QScrollArea 的内容
        self.scroll_area_personal.setWidget(self.inner_frame_personal)

        # 设置主布局
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.scroll_area_personal)

        self.__connectSignalToSlot()
        
        # 后台创建设置卡片，避免堵塞进程
        QTimer.singleShot(0, self.create_settings_cards)

    def __connectSignalToSlot(self):
        cfg.themeChanged.connect(setTheme)
        
    def create_settings_cards(self):
        """后台创建设置卡片"""
        # 创建基础设置卡片
        if not self.foundation_settings_created:
            foundation_settings_Card = foundation_settingsCard()
            self.inner_layout_personal.addWidget(foundation_settings_Card)
            self.foundation_settings_created = True
            
        # 创建高级设置卡片
        if not self.advanced_settings_created:
            advanced_settings_Card = advanced_settingsCard()
            self.inner_layout_personal.addWidget(advanced_settings_Card)
            self.advanced_settings_created = True
