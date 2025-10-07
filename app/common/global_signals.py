from PyQt5.QtCore import QObject, pyqtSignal

class FontSignal(QObject):
    """全局字体信号类"""
    font_changed = pyqtSignal(str)

# 创建全局字体信号实例
font_signal = FontSignal()