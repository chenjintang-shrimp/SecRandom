from venv import logger
import os
import sys

from qfluentwidgets import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

from app.common.config import cfg, AUTHOR, YEAR
from app.common.config import load_custom_font

from app.common.about import aboutCard


class about(QFrame):
    def __init__(self, parent: QFrame = None):
        super().__init__(parent=parent)
        
        # 初始化标志位
        self.ui_created = False
        self.about_created = False
        
        # 连接信号
        self.__connectSignalToSlot()
        
        # 后台创建UI组件，避免堵塞进程
        QTimer.singleShot(0, self.create_ui_components)

    def __connectSignalToSlot(self):
        cfg.themeChanged.connect(setTheme)
    
    def create_ui_components(self):
        """后台创建UI组件，避免堵塞进程"""
        if self.ui_created:
            return
            
        # 创建一个 QScrollArea - 后台创建
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

        # 创建一个内部的 QFrame 用于放置内容 - 后台创建
        self.inner_frame_personal = QWidget(self.scroll_area_personal)
        self.inner_layout_personal = QVBoxLayout(self.inner_frame_personal)
        self.inner_layout_personal.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignTop)

        # 将内部的 QFrame 设置为 QScrollArea 的内容
        self.scroll_area_personal.setWidget(self.inner_frame_personal)

        # 设置主布局
        self.main_layout = QVBoxLayout(self)
        self.main_layout.addWidget(self.scroll_area_personal)
        
        self.ui_created = True
        
        # UI组件创建完成后，创建关于卡片
        QTimer.singleShot(0, self.create_about_card)
    
    def create_about_card(self):
        """后台创建关于卡片，避免堵塞进程"""
        if not self.ui_created or self.about_created:
            return
            
        self.aboutCard = aboutCard()
        self.inner_layout_personal.addWidget(self.aboutCard)
        self.about_created = True
