from qfluentwidgets import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from app.common.config import cfg, AUTHOR, VERSION, YEAR
from app.common.config import load_custom_font

from app.common.password_settings import password_SettingsCard


class password_set(QFrame):
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

        # 密码设置卡片组 - 后台创建
        self.password_settings_created = False
        # password_settings_card = password_SettingsCard()
        # self.inner_layout_personal.addWidget(password_settings_card)

        # 将内部的 QFrame 设置为 QScrollArea 的内容
        self.scroll_area_personal.setWidget(self.inner_frame_personal)

        # 设置主布局
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.scroll_area_personal)

        self.__connectSignalToSlot()
        
        # 后台创建密码设置卡片，避免堵塞进程
        QTimer.singleShot(0, self.create_password_settings_card)

    def __connectSignalToSlot(self):
        cfg.themeChanged.connect(setTheme)
        
    def create_password_settings_card(self):
        """后台创建密码设置卡片"""
        if not self.password_settings_created:
            # 创建密码设置卡片
            password_settings_card = password_SettingsCard()
            self.inner_layout_personal.addWidget(password_settings_card)
            self.password_settings_created = True