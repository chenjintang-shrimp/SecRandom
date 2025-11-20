"""
通知服务模块

该模块提供在独立通知窗口中显示抽取结果的功能。
"""

from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QApplication, QTextEdit
from PySide6.QtCore import Qt, QPoint, QTimer, Signal, QPropertyAnimation, QEasingCurve, QRect
from PySide6.QtGui import QFont, QScreen, QMouseEvent
from qfluentwidgets import CardWidget

from app.page_building.window_template import SimpleWindowTemplate
from app.page_building.page_template import PageTemplate


class NotificationContentWidget(QWidget):
    """通知内容控件，用于在窗口或浮动窗口中显示内容"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(15, 15, 15, 15)
        self.layout.setSpacing(10)
        self.content_widgets = []
        
    def update_content(self, widgets):
        """更新内容控件"""
        # 清除现有内容
        for widget in self.content_widgets:
            self.layout.removeWidget(widget)
            widget.deleteLater()
        self.content_widgets.clear()
        
        # 添加新内容
        for widget in widgets:
            self.layout.addWidget(widget)
            self.content_widgets.append(widget)


class NotificationWindowTemplate(PageTemplate):
    """通知窗口页面模板"""
    
    def __init__(self, parent=None):
        super().__init__(content_widget_class=NotificationContentWidget, parent=parent)


class NotificationWindow(CardWidget):
    """用于显示抽取结果的浮动通知窗口"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        
        # 添加拖动支持
        self.drag_position = QPoint()
        
        # 添加三击关闭功能支持
        self.click_count = 0
        self.click_timer = QTimer()
        self.click_timer.setSingleShot(True)
        self.click_timer.timeout.connect(self.reset_click_count)
        
        # 设置UI
        self.setup_ui()
        
        # 设置窗口圆角
        self.setBorderRadius(15)
        
        # 自动关闭定时器
        self.auto_close_timer = QTimer()
        self.auto_close_timer.setSingleShot(True)
        self.auto_close_timer.timeout.connect(self.hide)
        
        # 动画相关
        self.geometry_animation = None
        self.opacity_animation = None
        self.is_animation_enabled = True
        
    def mousePressEvent(self, event: QMouseEvent):
        """鼠标按下事件处理，用于窗口拖拽"""
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
            
    def mouseMoveEvent(self, event: QMouseEvent):
        """鼠标移动事件处理，用于窗口拖拽"""
        if event.buttons() == Qt.LeftButton and not self.drag_position.isNull():
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()
            
    def mouseReleaseEvent(self, event: QMouseEvent):
        """鼠标释放事件处理"""
        if event.button() == Qt.LeftButton:
            self.drag_position = QPoint()
            # 处理三击关闭功能
            self.handle_mouse_click()
        event.accept()
        
    def handle_mouse_click(self):
        """处理鼠标点击，实现三击关闭功能"""
        self.click_count += 1
        
        if self.click_count == 1:
            # 第一次点击启动计时器
            self.click_timer.start(500)  # 500毫秒内必须完成三次点击
        elif self.click_count == 3:
            # 第三次点击关闭窗口
            self.click_timer.stop()
            self.reset_click_count()
            self.hide()  # 隐藏窗口
            
    def reset_click_count(self):
        """重置点击计数"""
        self.click_count = 0
        
    def setup_ui(self):
        """初始化UI组件"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        
        self.content_layout = QVBoxLayout()
        self.content_layout.setSpacing(10)
        layout.addLayout(self.content_layout)
        
    def apply_settings(self, settings=None):
        """应用设置到通知窗口"""
        if settings:
            # 使用传递的设置
            transparency = settings.get("transparency", 0.6)
            auto_close_time = settings.get("auto_close_time", 5)
            self.is_animation_enabled = settings.get("animation", True)
        else:
            transparency = 0.6
            auto_close_time = 5
            self.is_animation_enabled = True
            
        # 设置透明度（背景和字体透明度统一）
        self.setWindowOpacity(transparency)
        
        # 根据设置定位窗口
        self.position_window(settings)
        
        # 设置自动关闭时间
        if auto_close_time > 0:
            self.auto_close_timer.stop()
            self.auto_close_timer.setInterval(auto_close_time * 1000)  # 转换为毫秒
            self.auto_close_timer.start()
        
    def position_window(self, settings=None):
        """根据设置定位窗口"""
        # 默认获取主屏幕
        screen = QApplication.primaryScreen()
        
        # 获取设置
        if settings:
            enabled_monitor_name = settings.get("enabled_monitor", "OFF")
            position_index = settings.get("window_position", 0)
            horizontal_offset = settings.get("horizontal_offset", 0)
            vertical_offset = settings.get("vertical_offset", 0)
            # 检查是否为浮动窗口模式，如果是则调整位置索引
            notification_mode = settings.get("notification_mode", 0)
            if notification_mode == 1:  # 浮动窗口模式
                position_index += 1
        else:
            enabled_monitor_name = "OFF"
            position_index = 0
            horizontal_offset = 0
            vertical_offset = 0
        
        # 尝试获取指定的显示器
        if enabled_monitor_name != "OFF":
            for s in QApplication.screens():
                if s.name() == enabled_monitor_name:
                    screen = s
                    break
        
        if screen is None:
            screen = QApplication.primaryScreen()
            
        screen_geometry = screen.geometry()
        
        # 不在定位阶段显示窗口，避免显示空白窗口
        # 通过默认尺寸计算位置，内容添加后再调整大小
        window_width = 300
        window_height = 200
        
        # 根据设置计算位置
        # 位置映射基于语言文件:
        # 0: 中心, 1: 顶部, 2: 底部, 3: 左侧, 4: 右侧, 
        # 5: 顶部左侧, 6: 顶部右侧, 7: 底部左侧, 8: 底部右侧
        if position_index == 0:  # 中心
            x = screen_geometry.center().x() - window_width // 2 + horizontal_offset
            y = screen_geometry.center().y() - window_height // 2 + vertical_offset
        elif position_index == 1:  # 顶部
            x = screen_geometry.center().x() - window_width // 2 + horizontal_offset
            y = screen_geometry.top() + vertical_offset
        elif position_index == 2:  # 底部
            x = screen_geometry.center().x() - window_width // 2 + horizontal_offset
            y = screen_geometry.bottom() - window_height + vertical_offset
        elif position_index == 3:  # 左侧
            x = screen_geometry.left() + horizontal_offset
            y = screen_geometry.center().y() - window_height // 2 + vertical_offset
        elif position_index == 4:  # 右侧
            x = screen_geometry.right() - window_width + horizontal_offset
            y = screen_geometry.center().y() - window_height // 2 + vertical_offset
        elif position_index == 5:  # 顶部左侧
            x = screen_geometry.left() + horizontal_offset
            y = screen_geometry.top() + vertical_offset
        elif position_index == 6:  # 顶部右侧
            x = screen_geometry.right() - window_width + horizontal_offset
            y = screen_geometry.top() + vertical_offset
        elif position_index == 7:  # 底部左侧
            x = screen_geometry.left() + horizontal_offset
            y = screen_geometry.bottom() - window_height + vertical_offset
        elif position_index == 8:  # 底部右侧
            x = screen_geometry.right() - window_width + horizontal_offset
            y = screen_geometry.bottom() - window_height + vertical_offset
        else:  # 默认为中心
            x = screen_geometry.center().x() - window_width // 2
            y = screen_geometry.center().y() - window_height // 2
            
        self.move(x, y)
        # 移除隐藏逻辑，保持窗口显示状态
        
    def start_show_animation(self, settings=None):
        """开始显示动画"""
        if not self.is_animation_enabled:
            self.show()
            return
            
        # 确保窗口大小已调整
        self.adjustSize()
        
        # 获取最终位置
        final_geometry = self.geometry()
        
        # 根据窗口位置确定动画起始位置
        screen = QApplication.screenAt(final_geometry.center())
        if not screen:
            screen = QApplication.primaryScreen()
            
        screen_geometry = screen.geometry()
        
        # 获取设置以确定动画类型
        position_index = 0
        notification_mode = 0
        if settings:
            position_index = settings.get("window_position", 0)
            notification_mode = settings.get("notification_mode", 0)
            if notification_mode == 1:  # 浮动窗口模式
                position_index = settings.get("floating_window_position", 0)
        
        # 根据位置确定动画起始位置，确保从屏幕外进入
        if position_index in [1, 5, 6]:  # 顶部相关位置
            start_geometry = QRect(
                final_geometry.x(),
                screen_geometry.top() - final_geometry.height(),  # 从屏幕顶部外一个窗口高度的位置进入
                final_geometry.width(),
                final_geometry.height()
            )
        elif position_index in [2, 7, 8]:  # 底部相关位置
            start_geometry = QRect(
                final_geometry.x(),
                screen_geometry.bottom(),  # 从屏幕底部外一个窗口高度的位置进入
                final_geometry.width(),
                final_geometry.height()
            )
        elif position_index == 3:  # 左侧
            start_geometry = QRect(
                screen_geometry.left() - final_geometry.width(),  # 从屏幕左侧外一个窗口宽度的位置进入
                final_geometry.y(),
                final_geometry.width(),
                final_geometry.height()
            )
        elif position_index == 4:  # 右侧
            start_geometry = QRect(
                screen_geometry.right(),  # 从屏幕右侧外一个窗口宽度的位置进入
                final_geometry.y(),
                final_geometry.width(),
                final_geometry.height()
            )
        else:  # 默认为中心，从中心缩放进入
            start_geometry = QRect(
                final_geometry.center().x() - final_geometry.width() // 2,
                final_geometry.center().y() - final_geometry.height() // 2,
                0, 0
            )
            
        # 创建几何动画
        self.geometry_animation = QPropertyAnimation(self, b"geometry")
        self.geometry_animation.setDuration(500)
        self.geometry_animation.setStartValue(start_geometry)
        self.geometry_animation.setEndValue(final_geometry)
        self.geometry_animation.setEasingCurve(QEasingCurve.Linear)  # 使用线性缓动曲线
        
        # 创建透明度动画
        self.opacity_animation = QPropertyAnimation(self, b"windowOpacity")
        self.opacity_animation.setDuration(300)
        self.opacity_animation.setStartValue(0.0)
        self.opacity_animation.setEndValue(self.windowOpacity())
        self.opacity_animation.setEasingCurve(QEasingCurve.Linear)  # 使用线性缓动曲线
        
        # 连接动画完成信号
        self.geometry_animation.finished.connect(self.on_animation_finished())
        
        # 设置窗口初始位置并开始动画
        self.setGeometry(start_geometry)
        self.setWindowOpacity(0.0)  # 初始透明度为0
        self.show()
        
        # 并行启动所有动画
        self.geometry_animation.start()
        self.opacity_animation.start()
        
    def on_animation_finished(self, ):
        """动画完成后的处理"""
        self.geometry_animation = None
        self.opacity_animation = None
        # 确保窗口完全不透明
        self.setWindowOpacity()
        
    def update_content(self, student_labels, settings=None):
        """更新通知窗口的内容
        
        Args:
            student_labels: 包含学生信息的QLabel控件列表
            settings: 通知设置参数
        """
        # 清除现有内容
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)  # 重要：先设置父控件为None
                item.widget().deleteLater()
                
        # 添加新内容
        if student_labels:
            for label in student_labels:
                self.content_layout.addWidget(label)
                
        # 调整窗口大小以适应内容
        self.adjustSize()
        
        # 重新应用设置以根据新大小更新位置
        self.apply_settings(settings)
        
        # 显示窗口
        # 确保窗口置顶显示
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        self.start_show_animation(settings)


class NotificationManager:
    """管理不同类型抽取的通知窗口"""
    
    _instance = None
    _initialized = False
    _window_instances = {}  # 用于存储窗口实例，防止被垃圾回收
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(NotificationManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.notification_windows = {}
            self.notification_window_templates = {}
            self._initialized = True

    def get_notification_title(self):
        """获取通知标题文本（支持多语言）"""
        try:
            from app.Language.obtain_language import get_content_name_async
            return get_content_name_async("notification_settings", "notification_result")
        except:
            # 如果无法获取多语言文本，则使用默认文本
            return "通知结果"

    def show_roll_call_result(self, class_name, selected_students, draw_count=1, settings=None):
        """在通知窗口中显示点名结果
        
        Args:
            class_name: 班级名称
            selected_students: 选中的学生列表 [(学号, 姓名, 是否存在), ...]
            draw_count: 抽取的学生数量
            settings: 通知设置参数
        """
        # 获取设置
        if settings:
            font_size = settings.get("font_size", 50)
            animation_color = settings.get("animation_color_theme", 0)
            display_format = settings.get("display_format", 0)
            show_student_image = settings.get("student_image", False)
            notification_mode = settings.get("notification_mode", 0)
            is_animation_enabled = settings.get("animation", True)
        else:
            # 当没有传递设置时，使用默认值
            font_size = 50
            animation_color = 0
            display_format = 0
            show_student_image = False
            notification_mode = 0
            is_animation_enabled = True
        
        # 使用ResultDisplayUtils创建学生标签（动态导入避免循环依赖）
        from app.tools.result_display import ResultDisplayUtils
        student_labels = ResultDisplayUtils.create_student_label(
            class_name=class_name,
            selected_students=selected_students,
            draw_count=draw_count,
            font_size=font_size,
            animation_color=animation_color,
            display_format=display_format,
            show_student_image=show_student_image
        )
        
        if notification_mode == 1:  # 浮动窗口模式
            # 创建或获取通知窗口
            if "floating" not in self.notification_windows:
                self.notification_windows["floating"] = NotificationWindow()
                
            window = self.notification_windows["floating"]
            window.is_animation_enabled = is_animation_enabled
            # 如果窗口已经存在并且有活动的自动关闭定时器，停止它以防止窗口被隐藏
            if window.auto_close_timer.isActive():
                window.auto_close_timer.stop()
            window.update_content(student_labels, settings)
        else:  # 窗口模式（默认）
            # 创建或获取通知窗口模板
            window_key = f"notification_{class_name}"
            if window_key not in self.notification_window_templates:
                # 创建窗口
                title = f"{class_name} - {self.get_notification_title()}"
                window = SimpleWindowTemplate(title, width=400, height=300)
                
                # 添加页面
                page = window.add_page_from_template("notification", NotificationWindowTemplate)
                self.notification_window_templates[window_key] = {
                    "window": window,
                    "page": page
                }
                
                # 保存窗口实例引用，防止被垃圾回收
                self._window_instances[window_key] = window
                
                # 连接窗口关闭信号
                window.windowClosed.connect(lambda: self._on_window_closed(window_key))
            else:
                window_data = self.notification_window_templates[window_key]
                window = window_data["window"]
                # 如果窗口已经存在，取消自动关闭定时器以防窗口被隐藏
                if window.auto_close_timer.isActive():
                    window.auto_close_timer.stop()
                
            # 获取页面内容控件并更新内容
            page_template = window.get_page("notification")
            if page_template and hasattr(page_template, "contentWidget"):
                content_widget = page_template.contentWidget
                if hasattr(content_widget, "update_content"):
                    content_widget.update_content(student_labels)
            
            # 显示窗口
            window.show()
            window.raise_()
            window.activateWindow()
        
    def _on_window_closed(self, window_key):
        """当窗口关闭时的处理"""
        if window_key in self._window_instances:
            del self._window_instances[window_key]
        if window_key in self.notification_window_templates:
            del self.notification_window_templates[window_key]
            
    def close_all_notifications(self):
        """关闭所有通知窗口"""
        # 关闭浮动窗口
        for window in self.notification_windows.values():
            if window.auto_close_timer.isActive():
                window.auto_close_timer.stop()
            window.close()
        self.notification_windows.clear()
        
        # 关闭普通窗口
        for window_key, window_data in list(self.notification_window_templates.items()):
            window = window_data["window"]
            window.close()
            
        self.notification_window_templates.clear()
        self._window_instances.clear()


def show_roll_call_notification(class_name, selected_students, draw_count=1, settings=None):
    """显示点名通知的便捷函数
    
    Args:
        class_name: 班级名称
        selected_students: 选中的学生列表 [(学号, 姓名, 是否存在), ...]
        draw_count: 抽取的学生数量
        settings: 通知设置参数
    """
    manager = NotificationManager()
    manager.show_roll_call_result(class_name, selected_students, draw_count, settings)
