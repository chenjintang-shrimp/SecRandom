# 导入页面模板
from app.page_building.page_template import PageTemplate
from app.page_building.window_template import SimpleWindowTemplate
from app.view.another_window.contributor import contributor_page

# 全局变量，用于保持窗口引用，防止被垃圾回收
_window_instances = {}

# ==================================================
# 贡献者窗口
# ==================================================
class contributor_window_template(PageTemplate):
    """贡献者窗口类
    使用PageTemplate创建贡献者页面"""
    def __init__(self, parent=None):
        super().__init__(content_widget_class=contributor_page, parent=parent)

def create_contributor_window(title):
    """
    创建贡献者窗口
    
    Args:
        title: 窗口标题
        
    Returns:
        创建的窗口实例
    """
    window = SimpleWindowTemplate(title)
    window.add_page_from_template("contributor", contributor_window_template, width=700, height=500)
    window.switch_to_page("contributor")
    _window_instances["contributor"] = window
    window.windowClosed.connect(lambda: _window_instances.pop("contributor", None))
    window.show()
    return window