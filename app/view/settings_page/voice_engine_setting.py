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
        self.scroll_area_voice = SingleDirectionScrollArea(self)
        self.scroll_area_voice.setWidgetResizable(True)
        # 设置滚动条样式
        self.scroll_area_voice.setStyleSheet("""
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
        QScroller.grabGesture(self.scroll_area_voice.viewport(), QScroller.LeftMouseButtonGesture)

        # 创建一个内部的 QFrame 用于放置内容
        self.inner_frame_voice = QWidget(self.scroll_area_voice)
        self.inner_layout_voice = QVBoxLayout(self.inner_frame_voice)
        self.inner_layout_voice.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignTop)

        # 语音引擎设置卡片 - 后台创建
        self.voice_engine_settings_created = False
        # voice_engine_settings_card = VoiceEngine_SettingsCard()
        # self.inner_layout_voice.addWidget(voice_engine_settings_card)

        # 将内部的 QFrame 设置为 QScrollArea 的内容
        self.scroll_area_voice.setWidget(self.inner_frame_voice)

        # 设置主布局
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.scroll_area_voice)

        self.__connectSignalToSlot()
        
        # 后台创建语音引擎设置卡片，避免堵塞进程
        QTimer.singleShot(0, self.create_voice_engine_settings_card)
        # 🌟 小鸟游星野：语音引擎设置页面加载完成啦 ~ (≧∇≦)ﾉ

    def __connectSignalToSlot(self):
        cfg.themeChanged.connect(setTheme)
        
    def create_voice_engine_settings_card(self):
        """后台创建语音引擎设置卡片"""
        if not self.voice_engine_settings_created:
            # 创建语音引擎设置卡片
            voice_engine_settings_card = VoiceEngine_SettingsCard()
            self.inner_layout_voice.addWidget(voice_engine_settings_card)
            self.voice_engine_settings_created = True