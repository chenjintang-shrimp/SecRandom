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

from app.tools.list import *
from app.tools.history import *
from app.tools.result_display import *

from random import SystemRandom
system_random = SystemRandom()

# ==================================================
# 班级点名类
# ==================================================
class roll_call(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        """初始化UI"""
        # 主容器
        container = QWidget()
        roll_call_container = QVBoxLayout(container)
        roll_call_container.setContentsMargins(0, 0, 0, 0)
        
        # 结果显示区域
        self.result_widget = QWidget()
        self.result_layout = QVBoxLayout(self.result_widget)
        self.result_grid = QGridLayout()
        self.result_layout.addStretch()
        self.result_layout.addLayout(self.result_grid)
        self.result_layout.addStretch()
        roll_call_container.addWidget(self.result_widget)

        # 控制面板
        self.start_button = PrimaryPushButton('开始')
        self.start_button.clicked.connect(lambda: self.start_draw())

        # 右侧控制区
        control_widget = QWidget()
        control_layout = QVBoxLayout(control_widget)
        control_layout.setContentsMargins(10, 10, 10, 10)
        control_layout.addStretch()
        control_layout.addWidget(self.start_button, alignment=Qt.AlignmentFlag.AlignCenter)

        # 滚动区
        scroll = SmoothScrollArea()
        scroll.setWidget(container)
        scroll.setWidgetResizable(True)

        # 主布局
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll, 1)
        main_layout.addWidget(control_widget)

    def start_draw(self):
        """开始抽取"""
        animation = readme_settings_async("roll_call_settings", "animation")
        autoplay_count = readme_settings_async("roll_call_settings", "autoplay_count")
        animation_interval = readme_settings_async("roll_call_settings", "animation_interval")
        if animation == 0: # 手动停止动画
            self.start_button.setText("停止")
            self.is_animating = True
            self.animation_timer = QTimer()
            self.animation_timer.timeout.connect(self.draw_random)
            self.animation_timer.start(animation_interval)
            self.start_button.clicked.disconnect()
            self.start_button.clicked.connect(lambda: self.stop_animation())
        elif animation == 1: # 自动停止动画
            self.is_animating = True
            self.animation_timer = QTimer()
            self.animation_timer.timeout.connect(self.draw_random)
            self.animation_timer.start(animation_interval)
            self.start_button.setEnabled(False)
            QTimer.singleShot(autoplay_count * animation_interval, lambda: [
                self.animation_timer.stop(),
                lambda: self.stop_animation(),
                self.start_button.setEnabled(True)
            ])
        elif animation == 2: # 直接显示结果
            self.draw_random()
    
    def stop_animation(self):
        """停止动画"""
        self.animation_timer.stop()
        self.start_button.setText("开始")
        self.is_animating = False
        self.start_button.clicked.disconnect()
        self.start_button.clicked.connect(self.draw_random)

    def draw_random(self):
        """抽取随机结果"""
        class_name = "测试-1"
        group_index = 0
        gender_index = 0

        student_file = get_resources_path("list/roll_call_list", f"{class_name}.json")
        with open_file(student_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        students_data = filter_students_data(data, group_index, gender_index)
        if group_index == 1:
            students_data = sorted(students_data, key=lambda x: str(x))
        random_student = system_random.choice(students_data)
        id = random_student[0]
        random_name = random_student[1]
        exist = random_student[4]
        self.display_result(id, random_name, exist)
    
    def display_result(self, id, name, exist):
        """显示抽取结果"""
        selected_students = [(id, name, exist)]
        student_labels = ResultDisplayUtils.create_student_label(
            selected_students=selected_students,
            draw_count=1,
            font_size=readme_settings_async("roll_call_settings", "font_size"),
            animation_color=readme_settings_async("roll_call_settings", "animation_color_theme"),
            display_format=readme_settings_async("roll_call_settings", "display_format"),
            show_student_image=readme_settings_async("roll_call_settings", "student_image"),
            group_index=0
        )
        ResultDisplayUtils.display_results_in_grid(self.result_grid, student_labels)