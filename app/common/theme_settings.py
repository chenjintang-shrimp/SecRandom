from venv import logger
import os
import sys

from qfluentwidgets import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

from app.common.config import cfg, AUTHOR, YEAR, setThemeColor
from app.common.config import get_theme_icon, load_custom_font

from app.common.personal_settings import personal_settingsCard


class theme_settingsCard(QFrame):
    # 背景设置变化信号
    background_settings_changed = pyqtSignal()
    
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

        # 个性化设置卡片组
        self.personal_settings_Card = personal_settingsCard()
        inner_layout_personal.addWidget(self.personal_settings_Card)

        # 创建个性化卡片组
        self.themeAndZoomCard = SettingCardGroup("UI库の个性化", self)

        # 主题设置卡片
        self.themeCard = OptionsSettingCard(
            cfg.themeMode,
            get_theme_icon("ic_fluent_color_20_filled"),
            self.tr("主题"),
            self.tr("更改应用程序的主题(部分界面需重启生效)"),
            texts=["浅色", "深色", "跟随系统设置"]
        )

        # 主题色设置卡片
        self.themeColorCard = ColorSettingCard(
            cfg.themeColor,
            get_theme_icon("ic_fluent_color_20_filled"),
            self.tr("主题色"),
            self.tr("更改应用程序的主题色"),
            self
        )

        # 界面缩放设置卡片
        self.zoomCard = OptionsSettingCard(
            cfg.dpiScale,
            get_theme_icon("ic_fluent_zoom_fit_20_filled"),
            self.tr("界面缩放"),
            self.tr("更改界面和字体的大小"),
            texts=["100%", "125%", "150%", "175%", "200%", self.tr("使用系统设置"),]
        )
        
        # 添加组件到分组中
        self.themeAndZoomCard.addSettingCard(self.themeCard)
        self.themeAndZoomCard.addSettingCard(self.themeColorCard)
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
        cfg.themeColorChanged.connect(setThemeColor)
        # 连接个性化设置卡片的背景设置变化信号
        self.personal_settings_Card.background_settings_changed.connect(self.on_background_settings_changed)

    def on_background_settings_changed(self):
        """处理背景设置变化信号"""
        # 发送信号给上层设置界面
        if hasattr(self, 'background_settings_changed'):
            self.background_settings_changed.emit()
