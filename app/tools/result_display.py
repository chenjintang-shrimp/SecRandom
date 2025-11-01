# ==================================================
# 导入库
# ==================================================
import json
import random
import colorsys

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
# 结果显示工具类
# ==================================================

class ResultDisplayUtils:
    """结果显示工具类，提供通用的结果显示功能"""
    
    @staticmethod
    def _create_avatar_widget(image_path, name, font_size):
        """
        创建头像组件
        
        参数:
            image_path: 图片路径
            name: 学生姓名
            font_size: 字体大小
            
        返回:
            AvatarWidget: 创建的头像组件
        """
        if image_path is not None:
            avatar = AvatarWidget(image_path)
        else:
            avatar = AvatarWidget()
            avatar.setText(name)
        
        return avatar
    
    @staticmethod
    def _format_student_text(display_format, student_id_str, name, draw_count):
        """
        格式化学生显示文本
        
        参数:
            display_format: 显示格式 (0:学号+姓名, 1:仅姓名, 2:仅学号)
            student_id_str: 学号字符串
            name: 学生姓名
            draw_count: 抽取人数
            
        返回:
            str: 格式化后的文本
        """
        if display_format == 1:  # 仅显示姓名
            return f"{name}"
        elif display_format == 2:  # 仅显示学号
            return f"{student_id_str}"
        else:  # 显示学号+姓名
            if draw_count == 1:
                return f"{student_id_str}\n{name}"
            else:
                return f"{student_id_str} {name}"
    
    @staticmethod
    def _create_student_label_with_avatar(image_path, name, font_size, draw_count, text):
        """
        创建带头像的学生标签
        
        参数:
            image_path: 图片路径
            name: 学生姓名
            font_size: 字体大小
            draw_count: 抽取人数
            text: 显示文本
            
        返回:
            QWidget: 包含头像和文本的容器组件
        """
        # 创建水平布局
        h_layout = QHBoxLayout()
        h_layout.setSpacing(8)
        h_layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建容器widget
        container = QWidget()
        container.setLayout(h_layout)
        
        # 创建头像
        avatar = ResultDisplayUtils._create_avatar_widget(image_path, name, font_size)
        avatar.setRadius(font_size * 2 if draw_count == 1 else font_size // 2)
        
        # 创建文本标签
        text_label = BodyLabel(text)
        
        # 添加到布局
        h_layout.addWidget(avatar)
        h_layout.addWidget(text_label)
        
        return container
    
    @staticmethod
    def _apply_label_style(label, font_size, animation_color):
        """
        应用标签样式
        
        参数:
            label: 标签组件
            font_size: 字体大小
            animation_color: 动画颜色模式
        """
        fixed_color = readme_settings_async("roll_call_settings", "animation_fixed_color")
        # 根据label类型应用不同的样式设置
        if isinstance(label, QWidget) and hasattr(label, 'layout') and label.layout() is not None:
            # 如果是容器类型，对容器内的文本标签应用样式
            layout = label.layout()
            if layout:
                for i in range(layout.count()):
                    item = layout.itemAt(i)
                    widget = item.widget()
                    if isinstance(widget, BodyLabel):
                        widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
                        style_sheet = f"font-size: {font_size}pt; "
                        
                        if animation_color == 1:
                            style_sheet += f"color: {ResultDisplayUtils._generate_vibrant_color()};"
                        elif animation_color == 2:
                            style_sheet += f"color: {fixed_color};"
                            
                        widget.setStyleSheet(style_sheet)
        else:
            # 如果是普通的BodyLabel，直接应用样式
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            style_sheet = f"font-size: {font_size}pt; "
            fixed_color = readme_settings_async("roll_call_settings", "animation_fixed_color")
            if animation_color == 1:
                style_sheet += f"color: {ResultDisplayUtils._generate_vibrant_color()};"
            elif animation_color == 2:
                style_sheet += f"color: {fixed_color};"
                
            label.setStyleSheet(style_sheet)

    @staticmethod
    def create_student_label(selected_students, draw_count=1, font_size=50, 
                           animation_color=0, display_format=0,
                           show_student_image=False, group_index=0):
        """
        创建学生显示标签
        
        参数:
            selected_students: 选中的学生列表 [(num, selected, exist), ...]
            draw_count: 抽取人数
            font_size: 字体大小
            animation_color: 动画颜色模式 (0:默认, 1:随机颜色, 2:固定颜色)
            display_format: 显示格式 (0:学号+姓名, 1:仅姓名, 2:仅学号)
            show_student_image: 是否显示学生头像
            group_index: 小组索引 (0:全班, 1:随机小组, >1:指定小组)
            
        返回:
            list: 创建的标签列表
        """
        student_labels = []
        
        for num, selected, exist in selected_students:
            current_image_path = None
            if show_student_image:
                image_extensions = ['.png', '.jpg', '.jpeg', '.svg']
                for ext in image_extensions:
                    temp_path = get_resources_path("images", f"students/{selected}{ext}")
                    if file_exists(temp_path):
                        current_image_path = str(temp_path)
                        break
                    else:
                        current_image_path = None
                        continue

            student_id_str = f"{num:02}"
            if len(str(selected)) == 2 and group_index == 0:
                name = f"{str(selected)[0]}    {str(selected)[1]}"
            else:
                name = str(selected)
            text = ResultDisplayUtils._format_student_text(display_format, student_id_str, name, draw_count)
            if show_student_image:
                label = ResultDisplayUtils._create_student_label_with_avatar(
                    current_image_path, name, font_size, draw_count, text
                    )
            else:
                label = BodyLabel(text)
            ResultDisplayUtils._apply_label_style(label, font_size, animation_color)
            student_labels.append(label)
        
        return student_labels
    
    @staticmethod
    def _generate_vibrant_color():
        """生成鲜艳的颜色"""
        hue = random.random()
        saturation = 0.7 + random.random() * 0.3  # 0.7-1.0 之间
        lightness = 0.4 + random.random() * 0.2  # 0.4-0.6 之间
        r, g, b = colorsys.hsv_to_rgb(hue, saturation, lightness)
        return f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"
    
    @staticmethod
    def display_results_in_grid(result_grid, student_labels, alignment=None):
        """
        在网格布局中显示结果
        
        参数:
            result_grid: QGridLayout 网格布局
            student_labels: 学生标签列表
            alignment: 对齐方式 (默认为居中)
        """
        if alignment is None:
            alignment = Qt.AlignmentFlag.AlignCenter

        result_grid.setAlignment(alignment)
        while result_grid.count():
            item = result_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        columns = 3
        for i, label in enumerate(student_labels):
            row = i // columns
            col = i % columns
            result_grid.addWidget(label, row, col)