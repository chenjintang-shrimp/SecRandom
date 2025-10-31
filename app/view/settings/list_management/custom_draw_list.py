# ==================================================
# 导入库
# ==================================================
import json
import os
import sys
import subprocess

from loguru import logger
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtNetwork import *
from qfluentwidgets import *

from app.tools.variable import *
from app.tools.path_utils import *
from app.tools.personalised import *
from app.tools.settings_default import *
from app.tools.settings_access import *
from app.Language.obtain_language import *

# ==================================================
# 自定义抽奖名单
# ==================================================
class custom_draw_list(GroupHeaderCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(get_content_name_async("custom_draw_list", "title"))
        self.setBorderRadius(8)

        # 开机自启设置
        self.autostart_switch = SwitchButton()
        self.autostart_switch.setOffText(get_content_switchbutton_name_async("basic_settings", "autostart", "disable"))
        self.autostart_switch.setOnText(get_content_switchbutton_name_async("basic_settings", "autostart", "enable"))
        self.autostart_switch.setChecked(readme_settings_async("basic_settings", "autostart"))
        self.autostart_switch.checkedChanged.connect(lambda: update_settings("basic_settings", "autostart", self.autostart_switch.isChecked()))

        # 添加设置项到分组
        self.addGroup(get_theme_icon("ic_fluent_arrow_sync_20_filled"), 
                        get_content_name_async("basic_settings", "autostart"), get_content_description_async("basic_settings", "autostart"), self.autostart_switch)
