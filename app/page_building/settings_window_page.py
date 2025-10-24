# 导入库
from PyQt6.QtWidgets import QFrame

# 导入页面模板
from app.page_building.page_template import PageTemplate, PivotPageTemplate

# 导入自定义页面内容组件
from app.view.settings.home import home
from app.view.settings.basic_settings import basic_settings

# 导入默认设置
from app.tools.settings_default import *
from app.Language.obtain_language import *

class home_page(PageTemplate):
    """创建主页页面"""
    def __init__(self, parent: QFrame = None):
        super().__init__(content_widget_class=home, parent=parent)

class basic_settings_page(PageTemplate):
    """创建基础设置页面"""
    def __init__(self, parent: QFrame = None):
        super().__init__(content_widget_class=basic_settings, parent=parent)

class list_management_page(PivotPageTemplate):
    """创建名单管理页面"""
    def __init__(self, parent: QFrame = None):
        page_config = {
            "roll_call_list": get_content_name("roll_call_list", "title"),
            "roll_call_table": get_content_name("roll_call_table", "title"),
            "custom_draw_list": get_content_name("custom_draw_list", "title"),
            "lottery_list": get_content_name("lottery_list", "title"),
            "lottery_table": get_content_name("lottery_table", "title")
        }
        super().__init__(page_config, parent)
        self.set_base_path("app.view.settings.list_management")

class extraction_settings_page(PivotPageTemplate):
    """创建抽取设置页面"""
    def __init__(self, parent: QFrame = None):
        page_config = {
            "roll_call_settings": get_content_name("roll_call_settings", "title"),
            "quick_draw_settings": get_content_name("quick_draw_settings", "title"),
            "instant_draw_settings": get_content_name("instant_draw_settings", "title"),
            "custom_draw_settings": get_content_name("custom_draw_settings", "title"),
            "lottery_settings": get_content_name("lottery_settings", "title")
        }
        super().__init__(page_config, parent)
        self.set_base_path("app.view.settings.extraction_settings")

class safety_settings_page(PivotPageTemplate):
    """创建安全设置页面"""
    def __init__(self, parent: QFrame = None):
        page_config = {
            "basic_safety_settings": get_content_name("basic_safety_settings", "title"),
            "advanced_safety_settings": get_content_name("advanced_safety_settings", "title")
        }
        super().__init__(page_config, parent)
        self.set_base_path("app.view.settings.safety_settings")

class custom_settings_page(PivotPageTemplate):
    """创建个性设置页面"""
    def __init__(self, parent: QFrame = None):
        page_config = {
            "page_management": get_content_name("page_management", "title"),
            "floating_window_management": get_content_name("floating_window_management", "title"),
            "sidebar_management": get_content_name("sidebar_management", "title"),
            "personalised_settings": get_content_name("personalised_settings", "title")
        }
        super().__init__(page_config, parent)
        self.set_base_path("app.view.settings.custom_settings")