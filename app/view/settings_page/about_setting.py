from venv import logger
import os
import sys

from qfluentwidgets import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

from app.common.config import cfg, AUTHOR, VERSION, YEAR
from app.common.config import load_custom_font

from app.common.about import aboutCard


class about(QFrame):
    def __init__(self, parent: QFrame = None):
        super().__init__(parent=parent)

        # 创建一个 QScrollArea
        scroll_area_personal = SingleDirectionScrollArea(self)
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
        """)
        # 启用触屏滚动
        QScroller.grabGesture(scroll_area_personal.viewport(), QScroller.LeftMouseButtonGesture)

        # 创建一个内部的 QFrame 用于放置内容
        inner_frame_personal = QWidget(scroll_area_personal)
        inner_layout_personal = QVBoxLayout(inner_frame_personal)
        inner_layout_personal.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignTop)

        self.aboutCard = aboutCard()
        inner_layout_personal.addWidget(self.aboutCard)

        # 将内部的 QFrame 设置为 QScrollArea 的内容
        scroll_area_personal.setWidget(inner_frame_personal)

        # 设置主布局
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(scroll_area_personal)

        self.__connectSignalToSlot()

    def __connectSignalToSlot(self):
        cfg.themeChanged.connect(setTheme)
