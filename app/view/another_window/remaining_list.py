"""
剩余名单页面
用于显示未抽取的学生名单
"""
import os
import json
from typing import Dict, List, Optional, Tuple, Any

from loguru import logger
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from qfluentwidgets import *

from app.tools.variable import *
from app.tools.path_utils import *
from app.tools.personalised import *
from app.tools.settings_default import *
from app.tools.settings_access import *
from app.Language.obtain_language import *
from app.Language.modules.remaining_list import remaining_list
from app.tools.config import *
from app.tools.list import *

class RemainingListPage(QWidget):
    """剩余名单页面类"""
    
    # 定义信号，当抽取人数改变时发送信号
    count_changed = pyqtSignal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.class_name = ""
        self.group_filter = ""
        self.gender_filter = ""
        self.half_repeat = 0
        self.group_index = 0
        self.gender_index = 0
        self.remaining_students = []
        self._updating = False 
        self.init_ui()
        
        # 连接内部信号
        self.count_changed.connect(self.on_count_changed)
        
    def on_count_changed(self, count):
        """响应count_changed信号的槽函数
        
        Args:
            count: 剩余人数
        """
        # 如果正在更新中，不执行刷新，防止无限递归
        if self._updating:
            return
            
        # 使用异步函数获取剩余人数标签文本
        count_text = get_any_position_value_async("remaining_list", "count_label", "name")
        
        # 更新剩余人数标签
        self.count_label.setText(count_text.format(count=count))
        
        # 使用QTimer延迟执行更新，避免在信号处理过程中直接更新UI
        QTimer.singleShot(50, lambda: self._delayed_update_students(count))
    
    def _delayed_update_students(self, count):
        """延迟更新学生数据的方法
        
        Args:
            count: 剩余人数
        """
        # 重新获取学生数据并更新UI，但不发送信号
        if self.class_name:
            # 确保group_index和gender_index属性存在
            if not hasattr(self, 'group_index'):
                self.group_index = 0
            if not hasattr(self, 'gender_index'):
                self.gender_index = 0
                
            self._load_and_update_students(count)
    
    def _load_and_update_students(self, count=None):
        """加载学生数据并更新UI的通用方法
        
        Args:
            count: 剩余人数，用于特殊处理当count为0时显示所有学生
        """
        # 设置更新标志，防止递归
        self._updating = True
        
        try:
            # 获取学生数据
            student_file = get_resources_path("list/roll_call_list", f"{self.class_name}.json")
            with open_file(student_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # 获取索引
            group_index = getattr(self, 'group_index', 0)
            gender_index = getattr(self, 'gender_index', 0)
            
            # 过滤学生数据
            students_data = filter_students_data(
                data, group_index, self.group_filter, gender_index, self.gender_filter
            )
            
            # 转换为字典格式
            students_dict_list = []
            for student_tuple in students_data:
                student_dict = {
                    "id": student_tuple[0],
                    "name": student_tuple[1],
                    "gender": student_tuple[2],
                    "group": student_tuple[3],
                    "exist": student_tuple[4],
                }
                students_dict_list.append(student_dict)
            
            # 根据half_repeat设置获取未抽取的学生
            if self.half_repeat > 0:
                # 读取已抽取记录
                drawn_records = read_drawn_record(self.class_name, self.gender_filter, self.group_filter)
                drawn_counts = {name: count for name, count in drawn_records}
                
                # 过滤掉已抽取次数达到或超过设置值的学生
                remaining_students = []
                for student in students_dict_list:
                    student_name = student["name"]
                    # 如果学生未被抽取过，或者抽取次数小于设置值，则保留该学生
                    if student_name not in drawn_counts or drawn_counts[student_name] < self.half_repeat:
                        remaining_students.append(student)
                    # 如果当前剩余人数等于零，则显示全部学生
                    elif count is not None and count == 0:
                        remaining_students.append(student)
            else:
                # 如果half_repeat为0，则所有学生都显示
                remaining_students = students_dict_list
            
            self.remaining_students = remaining_students
            
            # 使用QTimer延迟更新UI，避免在数据处理过程中直接更新UI
            QTimer.singleShot(10, self.update_ui)
        finally:
            # 清除更新标志
            self._updating = False
    
    def init_ui(self):
        """初始化UI"""
        # 主布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # 使用异步函数获取标题文本
        title_text = get_content_name_async("remaining_list", "title")
        count_text = get_any_position_value_async("remaining_list", "count_label", "name")
        
        # 标题
        self.title_label = SubtitleLabel(title_text)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setFont(QFont(load_custom_font(), 18))
        layout.addWidget(self.title_label)
        
        # 剩余人数标签
        self.count_label = BodyLabel(count_text.format(count=0))
        self.count_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.count_label.setFont(QFont(load_custom_font(), 12))
        layout.addWidget(self.count_label)
        
        # 内容容器
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(10, 10, 10, 10)
        self.content_layout.setSpacing(10)

        layout.addWidget(self.content_widget)
        
    def update_remaining_list(self, class_name: str, group_filter: str, gender_filter: str, half_repeat: int = 0, group_index: int = 0, gender_index: int = 0, emit_signal: bool = True):
        """更新剩余名单
        
        Args:
            class_name: 班级名称
            group_filter: 分组筛选条件
            gender_filter: 性别筛选条件
            half_repeat: 重复抽取次数
            group_index: 分组索引
            gender_index: 性别索引
            emit_signal: 是否发送信号，默认为True，在响应信号时设为False防止循环
        """
        # 如果正在更新中，直接返回，防止无限递归
        if self._updating:
            return
            
        # 设置更新标志
        self._updating = True
        
        # 更新属性
        self.class_name = class_name
        self.group_filter = group_filter
        self.gender_filter = gender_filter
        self.half_repeat = half_repeat
        self.group_index = group_index
        self.gender_index = gender_index
        
        # 使用QTimer延迟执行数据加载和UI更新，避免卡退
        QTimer.singleShot(10, lambda: self._delayed_load_and_update(emit_signal))
    
    def _delayed_load_and_update(self, emit_signal: bool):
        """延迟加载和更新数据的方法
        
        Args:
            emit_signal: 是否发送信号
        """
        try:
            # 使用通用方法加载和更新学生数据
            self._load_and_update_students()
            
            # 只有在emit_signal为True时才发送信号，防止信号循环
            if emit_signal:
                self.count_changed.emit(len(self.remaining_students))
        finally:
            # 清除更新标志
            self._updating = False
        
    def update_ui(self):
        """更新UI显示"""
        # 清空当前内容
        for i in reversed(range(self.content_layout.count())): 
            self.content_layout.itemAt(i).widget().setParent(None)
        
        # 使用异步函数获取文本
        title_text = get_any_position_value_async("remaining_list", "title_with_class", "name")
        count_text = get_any_position_value_async("remaining_list", "count_label", "name")
        no_students_text = get_any_position_value_async("remaining_list", "no_students", "name")
        
        # 更新标题和人数
        self.title_label.setText(title_text.format(class_name=self.class_name))
        self.count_label.setText(count_text.format(count=len(self.remaining_students)))
        
        # 强制更新UI
        self.title_label.update()
        self.count_label.update()
        self.content_widget.update()
        self.update()
        
        # 处理应用程序事件，确保UI立即更新
        QApplication.processEvents()
        
        if not self.remaining_students:
            # 如果没有剩余学生，显示提示信息
            no_students_label = BodyLabel(no_students_text)
            no_students_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            no_students_label.setFont(QFont(load_custom_font(), 14))
            self.content_layout.addWidget(no_students_label)
        else:
            # 创建学生卡片
            grid_widget = QWidget()
            grid_layout = QGridLayout(grid_widget)
            grid_layout.setContentsMargins(10, 10, 10, 10)
            grid_layout.setSpacing(15)
            
            # 计算每行显示的卡片数量
            columns = 4  # 每行显示4个卡片
            
            # 为每个学生创建卡片
            for i, student in enumerate(self.remaining_students):
                row = i // columns
                col = i % columns
                
                # 创建学生卡片
                card = self.create_student_card(student)
                grid_layout.addWidget(card, row, col)
            
            # 添加到内容布局
            self.content_layout.addWidget(grid_widget)
            
        # 再次强制更新UI，确保新添加的控件显示
        self.content_widget.update()
        self.update()
        QApplication.processEvents()
    
    def create_student_card(self, student: Dict[str, Any]) -> CardWidget:
        """创建学生卡片
        
        Args:
            student: 学生信息字典
            
        Returns:
            学生卡片
        """
        # 使用异步函数获取学生信息格式文本
        student_info_text = get_any_position_value_async("remaining_list", "student_info", "name")
        
        card = CardWidget()
        card.setFixedSize(180, 100)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)
        
        # 学生姓名
        name_label = BodyLabel(student["name"])
        name_label.setFont(QFont(load_custom_font(), 14))
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(name_label)
        
        # 学生信息
        info_text = student_info_text.format(
            id=student['id'],
            gender=student['gender'],
            group=student['group']
        )
        info_label = BodyLabel(info_text)
        info_label.setFont(QFont(load_custom_font(), 9))
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info_label)
        
        return card
    
    def refresh(self, emit_signal: bool = True):
        """刷新页面
        
        Args:
            emit_signal: 是否发送信号，默认为True，在响应信号时设为False防止循环
        """
        if self.class_name:
            self.update_remaining_list(
                self.class_name, 
                self.group_filter, 
                self.gender_filter, 
                self.half_repeat,
                getattr(self, 'group_index', 0),
                getattr(self, 'gender_index', 0),
                emit_signal=emit_signal
            )
