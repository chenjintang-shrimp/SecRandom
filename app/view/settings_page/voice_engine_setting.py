from qfluentwidgets import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from app.common.config import cfg
from app.common.voice_engine_settings import VoiceEngine_SettingsCard


class voice_engine_settings(QFrame):
    def __init__(self, parent: QFrame = None):
        super().__init__(parent=parent)
        # 🌟 星穹铁道白露：初始化语音引擎设置页面 ~ (๑•̀ㅂ•́)ญ✧

        # 创建一个 QScrollArea
        scroll_area_voice = SingleDirectionScrollArea(self)
        scroll_area_voice.setWidgetResizable(True)
        # 设置滚动条样式
        scroll_area_voice.setStyleSheet("""
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
        QScroller.grabGesture(scroll_area_voice.viewport(), QScroller.LeftMouseButtonGesture)

        # 创建一个内部的 QFrame 用于放置内容
        inner_frame_voice = QWidget(scroll_area_voice)
        inner_layout_voice = QVBoxLayout(inner_frame_voice)
        inner_layout_voice.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignTop)

        # 语音引擎设置卡片
        voice_engine_settings_card = VoiceEngine_SettingsCard()
        inner_layout_voice.addWidget(voice_engine_settings_card)

        # 将内部的 QFrame 设置为 QScrollArea 的内容
        scroll_area_voice.setWidget(inner_frame_voice)

        # 设置主布局
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(scroll_area_voice)

        self.__connectSignalToSlot()
        # 🌟 小鸟游星野：语音引擎设置页面加载完成啦 ~ (≧∇≦)ﾉ

    def __connectSignalToSlot(self):
        cfg.themeChanged.connect(setTheme)