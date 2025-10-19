# 导入库
from PyQt6.QtWidgets import QFrame

# 导入页面模板
from app.page_building.page_template import PageTemplate

# 导入自定义页面内容组件
from app.view.main.about import about

class about_page(PageTemplate):
    """创建关于页面"""
    def __init__(self, parent: QFrame = None):
        super().__init__(content_widget_class=about, parent=parent)
