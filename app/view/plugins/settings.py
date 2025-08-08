from qfluentwidgets import *
from qfluentwidgets import FluentIcon as FIF
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import os
import json
from loguru import logger

from app.common.config import get_theme_icon, load_custom_font


class PluginSettingsPage(GroupHeaderCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("插件设置")
        self.setBorderRadius(8)
        self.settings_file = "app/Settings/plugin_settings.json"