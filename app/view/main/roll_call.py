# ==================================================
# 导入库
# ==================================================

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
# 班级点名类
# ==================================================
class roll_call(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        pass
    def stary_draw(self):
        """绘制点名界面"""
        self.setWindowTitle(get_content_name_async("roll_call", "title"))
        self.setWindowIcon(get_theme_icon("ic_fluent_people_20_filled"))
        self.setGeometry(100, 100, 800, 600)
        self.show()
        pass
