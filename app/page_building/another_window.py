# 导入页面模板
from app.page_building.page_template import PageTemplate
from app.page_building.window_template import SimpleWindowTemplate
from app.view.another_window.contributor import contributor_page
from app.view.another_window.import_student_name import ImportStudentNameWindow
from app.view.another_window.set_class_name import SetClassNameWindow
from app.Language.obtain_language import *

# 全局变量，用于保持窗口引用，防止被垃圾回收
_window_instances = {}

# ==================================================
# 班级名称设置窗口
# ==================================================
class set_class_name_window_template(PageTemplate):
    """班级名称设置窗口类
    使用PageTemplate创建班级名称设置页面"""
    def __init__(self, parent=None):
        super().__init__(content_widget_class=SetClassNameWindow, parent=parent)

def create_set_class_name_window():
    """
    创建班级名称设置窗口

    Returns:
        创建的窗口实例
    """
    title = get_content_name_async("set_class_name", "title")
    window = SimpleWindowTemplate(title, width=800, height=600)
    window.add_page_from_template("set_class_name", set_class_name_window_template)
    window.switch_to_page("set_class_name")
    _window_instances["set_class_name"] = window
    window.windowClosed.connect(lambda: _window_instances.pop("set_class_name", None))
    window.show()
    return

# ==================================================
# 导入学生名单导入窗口
# ==================================================
class import_student_name_window_template(PageTemplate):
    """学生名单导入窗口类
    使用PageTemplate创建学生名单导入页面"""
    def __init__(self, parent=None):
        super().__init__(content_widget_class=ImportStudentNameWindow, parent=parent)

def create_import_student_name_window():
    """
    创建学生名单导入窗口

    Returns:
        创建的窗口实例
    """
    title = get_content_name_async("import_student_name", "title")
    window = SimpleWindowTemplate(title, width=800, height=600)
    window.add_page_from_template("import_student_name", import_student_name_window_template)
    window.switch_to_page("import_student_name")
    _window_instances["import_student_name"] = window
    window.windowClosed.connect(lambda: _window_instances.pop("import_student_name", None))
    window.show()
    return


# ==================================================
# 贡献者窗口
# ==================================================
class contributor_window_template(PageTemplate):
    """贡献者窗口类
    使用PageTemplate创建贡献者页面"""
    def __init__(self, parent=None):
        super().__init__(content_widget_class=contributor_page, parent=parent)

def create_contributor_window():
    """
    创建贡献者窗口

    Returns:
        创建的窗口实例
    """
    title = get_content_name_async("about", "contributor")
    window = SimpleWindowTemplate(title, width=800, height=600)
    window.add_page_from_template("contributor", contributor_window_template)
    window.switch_to_page("contributor")
    _window_instances["contributor"] = window
    window.windowClosed.connect(lambda: _window_instances.pop("contributor", None))
    window.show()
    return
