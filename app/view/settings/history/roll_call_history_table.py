# ==================================================
# 导入库
# ==================================================
import json
import os
import sys
import subprocess
import pandas as pd
from collections import OrderedDict
from datetime import datetime

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
from app.tools.history import *

# ==================================================
# 点名历史记录表格
# ==================================================

class roll_call_history_table(GroupHeaderCardWidget):
    """点名历史记录表格卡片"""
    
    refresh_signal = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setTitle(get_content_name_async("roll_call_history_table", "title"))
        self.setBorderRadius(8)
        
        # 初始化数据加载器
        self.data_loader = None
        self.current_class_name = ""
        self.current_mode = get_content_combo_name_async("roll_call_history_table", "select_mode")
        self.batch_size = 30  # 每次加载的行数
        self.current_row = 0  # 当前加载到的行数
        self.total_rows = 0   # 总行数
        self.is_loading = False  # 是否正在加载数据
        
        # 创建班级选择区域
        QTimer.singleShot(APPLY_DELAY, self.create_class_selection)
        
        # 创建表格区域
        QTimer.singleShot(APPLY_DELAY, self.create_table)
        
        # 初始化班级列表
        QTimer.singleShot(APPLY_DELAY, self.refresh_class_history)
        
        # 设置文件系统监视器
        QTimer.singleShot(APPLY_DELAY, self.setup_file_watcher)
        
        # 初始化数据
        QTimer.singleShot(APPLY_DELAY, self.refresh_data)
        
        # 连接信号
        self.refresh_signal.connect(self.refresh_data)
        
    def create_class_selection(self):
        """创建班级选择区域"""
        self.class_comboBox = ComboBox()
        self.class_comboBox.setCurrentIndex(readme_settings_async("roll_call_history_table", "select_class_name"))
        if not get_all_history_names("roll_call"):
            self.class_comboBox.setCurrentIndex(-1)
            self.class_comboBox.setPlaceholderText(get_content_name_async("roll_call_history_table", "select_class_name"))
        self.class_comboBox.currentIndexChanged.connect(self.on_class_changed)
        self.class_comboBox.currentTextChanged.connect(lambda: self.on_class_changed(-1))

        # 选择查看模式
        self.all_names = get_all_names("roll_call", self.class_comboBox.currentText())
        self.mode_comboBox = ComboBox()
        self.mode_comboBox.addItems(get_content_combo_name_async("roll_call_history_table", "select_mode") + self.all_names)
        self.mode_comboBox.setCurrentIndex(readme_settings_async("roll_call_history_table", "select_mode"))
        self.mode_comboBox.currentIndexChanged.connect(lambda: update_settings("roll_call_history_table", "select_mode", self.mode_comboBox.currentIndex()))
        self.mode_comboBox.currentIndexChanged.connect(self.refresh_data)

        # 选择是否查看权重
        self.weight_switch = SwitchButton()
        self.weight_switch.setOffText(get_content_switchbutton_name_async("roll_call_history_table", "select_weight", "disable"))
        self.weight_switch.setOnText(get_content_switchbutton_name_async("roll_call_history_table", "select_weight", "enable"))
        self.weight_switch.setChecked(readme_settings_async("roll_call_history_table", "select_weight"))
        self.weight_switch.checkedChanged.connect(lambda: update_settings("roll_call_history_table", "select_weight", self.weight_switch.isChecked()))
        self.weight_switch.checkedChanged.connect(self.refresh_data)

        self.addGroup(get_theme_icon("ic_fluent_class_20_filled"), 
                        get_content_name_async("roll_call_history_table", "select_class_name"), get_content_description_async("roll_call_history_table", "select_class_name"), self.class_comboBox)
        self.addGroup(get_theme_icon("ic_fluent_reading_mode_mobile_20_filled"), 
                        get_content_name_async("roll_call_history_table", "select_mode"), get_content_description_async("roll_call_history_table", "select_mode"), self.mode_comboBox)
        self.addGroup(get_theme_icon("ic_fluent_box_multiple_search_20_filled"), 
                        get_content_name_async("roll_call_history_table", "select_weight"), get_content_description_async("roll_call_history_table", "select_weight"), self.weight_switch)

    def create_table(self):
        """创建表格区域"""
        # 创建表格
        self.table = TableWidget()
        self.table.setBorderVisible(True)
        self.table.setBorderRadius(8)
        self.table.setWordWrap(False)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        # 暂时禁用排序，在数据加载完成后再启用
        self.table.setSortingEnabled(False)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.verticalHeader().hide()

        # 根据当前选择的模式设置表格头
        self.update_table_headers()
        
        # 设置表格属性
        for i in range(self.table.columnCount()):
            self.table.horizontalHeader().setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)
            self.table.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)
            
        # 连接滚动事件，用于分段加载
        self.table.verticalScrollBar().valueChanged.connect(self._on_scroll)
        
        # 连接排序信号，在排序时重新加载数据
        self.table.horizontalHeader().sectionClicked.connect(self._on_header_clicked)
        
        self.layout().addWidget(self.table)
        
    def _on_scroll(self, value):
        """处理表格滚动事件，实现分段加载
        
        Args:
            value: 滚动条当前位置
        """
        # 如果正在加载或没有更多数据，直接返回
        if self.is_loading or self.current_row >= self.total_rows:
            return
            
        # 获取滚动条最大值和当前值
        max_value = self.table.verticalScrollBar().maximum()
        current_value = self.table.verticalScrollBar().value()
        
        # 使用更精确的滚动检测，确保在滚动到底部时触发
        scroll_threshold = max(20, max_value * 0.1)  # 至少20像素或10%的位置
        if current_value >= max_value - scroll_threshold:
            self._load_more_data()
    
    def _on_header_clicked(self, column):
        """处理表头点击事件，实现排序
        
        Args:
            column: 被点击的列索引
        """
        # 保存当前排序状态
        self.sort_column = column
        self.sort_order = self.table.horizontalHeader().sortIndicatorOrder()
        
        # 重置数据加载状态
        self.current_row = 0
        self.table.setRowCount(0)
        
        # 重新加载数据
        self.refresh_data()
    
    def _load_more_data(self):
        """加载更多数据"""
        if self.is_loading or self.current_row >= self.total_rows:
            return
        
        self.is_loading = True
        
        # 计算新的行数
        new_row_count = min(self.current_row + self.batch_size, self.total_rows)
        
        # 增加表格行数
        self.table.setRowCount(new_row_count)
        
        # 根据当前模式加载数据，与refresh_data方法保持一致
        if hasattr(self, 'mode_comboBox'):
            self.current_mode = self.mode_comboBox.currentIndex()
        else:
            self.current_mode = readme_settings_async("roll_call_history_table", "select_mode")
        
        if self.current_mode == 0:
            self._load_more_students_data()
        elif self.current_mode == 1:
            self._load_more_sessions_data()
        else:
            # 当模式值大于等于2时，表示选择了特定的学生姓名
            if hasattr(self, 'mode_comboBox'):
                self.current_student_name = self.mode_comboBox.currentText()
            else:
                # 如果没有mode_comboBox，从设置中获取学生姓名
                self.current_student_name = readme_settings_async("roll_call_history_table", "select_student_name")
            self._load_more_stats_data(self.current_student_name)
        
        # 数据加载完成后启用排序
        if self.current_row >= self.total_rows:
            self.table.setSortingEnabled(True)
        
        self.is_loading = False
    
    def _load_more_students_data(self):
        """加载更多学生数据"""
        if not self.current_class_name:
            return
        try:
            student_file = get_resources_path('list/roll_call_list', f'{self.current_class_name}.json')
            history_file = get_resources_path('history/roll_call_history', f'{self.current_class_name}.json')
            with open_file(student_file, 'r', encoding='utf-8') as f:
                class_data = json.load(f)

            cleaned_students = []
            for name, info in class_data.items():
                if isinstance(info, dict) and info.get('exist', True):
                    cleaned_students.append((
                        info.get('id', ''),
                        name,
                        info.get('gender', ''),
                        info.get('group', '')
                    ))
            
            history_data = {}
            if file_exists(history_file):
                try:
                    with open_file(history_file, 'r', encoding='utf-8') as f:
                        history_data = json.load(f)
                except json.JSONDecodeError:
                    pass
            
            max_id_length = max(len(str(student[0])) for student in cleaned_students) if cleaned_students else 0
            max_total_count_length = max(len(str(history_data.get('students', {}).get(name, {}).get('total_count', 0))) for _, name, _, _ in cleaned_students) if cleaned_students else 0

            students_data = []
            for student_id, name, gender, group in cleaned_students:
                count = int(history_data.get('students', {}).get(name, {}).get('total_count', 0))
                group_gender_count = int(history_data.get('students', {}).get(name, {}).get('group_gender_count', 0))
                total_count = count + group_gender_count
                students_data.append({
                    'id': str(student_id).zfill(max_id_length),
                    'name': name,
                    'gender': gender,
                    'group': group,
                    'total_count': total_count,
                    'total_count_str': str(total_count).zfill(max_total_count_length)
                })
            
            students_weight_data = calculate_weight(students_data)
            max_weight_length = max(len(str(student.get('next_weight', '1.0'))) for student in students_weight_data) if students_weight_data else 0
            
            # 计算本次加载的行范围
            start_row = self.current_row
            end_row = min(start_row + self.batch_size, self.total_rows)
            
            # 填充表格数据
            for i in range(start_row, end_row):
                if i >= len(students_data):
                    break
                    
                student = students_data[i]
                row = i
                
                # 学号
                id_item = create_table_item(student.get('id', str(row + 1)))
                self.table.setItem(row, 0, id_item)
                
                # 姓名
                name_item = create_table_item(student.get('name', ''))
                self.table.setItem(row, 1, name_item)
                
                # 性别
                gender_item = create_table_item(student.get('gender', ''))
                self.table.setItem(row, 2, gender_item)
                
                # 小组
                group_item = create_table_item(student.get('group', ''))
                self.table.setItem(row, 3, group_item)
                
                # 总次数
                total_count_item = create_table_item(str(student.get('total_count_str', student.get('total_count', 0))))
                self.table.setItem(row, 4, total_count_item)
                
                # 如果需要显示权重
                if self.table.columnCount() > 5:
                    weight_item = create_table_item(str(students_weight_data[i].get('next_weight', '1.0')).zfill(max_weight_length))
                    self.table.setItem(row, 5, weight_item)
            
            # 更新当前行数
            self.current_row = end_row
            
        except Exception as e:
            logger.error(f"加载学生数据失败: {e}")
            Dialog(
                "错误",
                f"加载学生数据失败: {e}",
                self
            ).exec()
    
    def _load_more_sessions_data(self):
        """加载更多会话数据"""
        if not self.current_class_name:
            return
        try:
            student_file = get_resources_path('list/roll_call_list', f'{self.current_class_name}.json')
            history_file = get_resources_path('history/roll_call_history', f'{self.current_class_name}.json')
            with open_file(student_file, 'r', encoding='utf-8') as f:
                class_data = json.load(f)

            cleaned_students = []
            for name, info in class_data.items():
                if isinstance(info, dict) and info.get('exist', True):
                    cleaned_students.append((
                        info.get('id', ''),
                        name,
                        info.get('gender', ''),
                        info.get('group', '')
                    ))
            
            history_data = {}
            if file_exists(history_file):
                try:
                    with open_file(history_file, 'r', encoding='utf-8') as f:
                        history_data = json.load(f)
                except json.JSONDecodeError:
                    pass
            
            max_id_length = max(len(str(student[0])) for student in cleaned_students) if cleaned_students else 0

            students_data = []
            for student_id, name, gender, group in cleaned_students:
                time_records = history_data.get('students', {}).get(name, {}).get('history', [{}])
                for record in time_records:
                        draw_time = record.get('draw_time', '')
                        if draw_time:
                            students_data.append({
                                'draw_time': draw_time,
                                'id': str(student_id).zfill(max_id_length),
                                'name': name,
                                'gender': gender,
                                'group': group
                            })

            students_data.sort(key=lambda x: x.get('draw_time', ''), reverse=True)
            
            # 计算本次加载的行范围
            start_row = self.current_row
            end_row = min(start_row + self.batch_size, self.total_rows)
            
            # 填充表格数据
            for i in range(start_row, end_row):
                if i >= len(students_data):
                    break
                    
                student = students_data[i]
                row = i
                
                # 时间
                draw_time_item = create_table_item(student.get('draw_time', ''))
                self.table.setItem(row, 0, draw_time_item)
                
                # 学号
                id_item = create_table_item(student.get('id', str(row + 1)))
                self.table.setItem(row, 1, id_item)
                
                # 姓名
                name_item = create_table_item(student.get('name', ''))
                self.table.setItem(row, 2, name_item)
                
                # 性别
                gender = student.get('gender', '')
                gender_item = create_table_item(str(gender) if gender else '')
                self.table.setItem(row, 3, gender_item)
                
                # 小组
                group = student.get('group', '')
                group_item = create_table_item(str(group) if group else '')
                self.table.setItem(row, 4, group_item)

            # 更新当前行数
            self.current_row = end_row
            
        except Exception as e:
            logger.error(f"加载会话数据失败: {e}")
            Dialog(
                "错误",
                f"加载会话数据失败: {e}",
                self
            ).exec()
    
    def _load_more_stats_data(self, student_name):
        """加载更多统计数据"""
        if not self.current_class_name:
            return
        try:
            student_file = get_resources_path('list/roll_call_list', f'{self.current_class_name}.json')
            history_file = get_resources_path('history/roll_call_history', f'{self.current_class_name}.json')
            with open_file(student_file, 'r', encoding='utf-8') as f:
                class_data = json.load(f)

            cleaned_students = []
            for name, info in class_data.items():
                if isinstance(info, dict) and info.get('exist', True) and name == student_name:
                    cleaned_students.append((
                        info.get('id', ''),
                        name,
                        info.get('gender', ''),
                        info.get('group', '')
                    ))
            
            history_data = {}
            if file_exists(history_file):
                try:
                    with open_file(history_file, 'r', encoding='utf-8') as f:
                        history_data = json.load(f)
                except json.JSONDecodeError:
                    pass

            students_data = []
            for student_id, name, gender, group in cleaned_students:
                time_records = history_data.get('students', {}).get(name, {}).get('history', [{}])
                for record in time_records:
                        draw_time = record.get('draw_time', '')
                        if draw_time:
                            students_data.append({
                                'draw_time': draw_time,
                                'draw_method': str(record.get('draw_method', '')),
                                'draw_people_numbers': str(record.get('draw_people_numbers', 0)),
                                'draw_gender': str(record.get('draw_gender', '')),
                                'draw_group': str(record.get('draw_group', ''))
                            })
            students_data.sort(key=lambda x: x.get('draw_time', ''), reverse=True)
            
            # 计算本次加载的行范围
            start_row = self.current_row
            end_row = min(start_row + self.batch_size, self.total_rows)
            
            # 填充表格数据
            for i in range(start_row, end_row):
                if i >= len(students_data):
                    break
                    
                student = students_data[i]
                row = i
                
                # 时间
                time_item = create_table_item(student.get('draw_time', ''))
                self.table.setItem(row, 0, time_item)
                
                # 模式
                mode_item = create_table_item(student.get('draw_method', ''))
                self.table.setItem(row, 1, mode_item)
                
                # 人数
                draw_people_numbers_item = create_table_item(str(student.get('draw_people_numbers', 0)))
                self.table.setItem(row, 2, draw_people_numbers_item)
                
                # 性别
                draw_gender = student.get('draw_gender', '')
                gender_item = create_table_item(draw_gender if draw_gender else '')
                self.table.setItem(row, 3, gender_item)
                
                # 小组
                draw_group = student.get('draw_group', '')
                group_item = create_table_item(draw_group if draw_group else '')
                self.table.setItem(row, 4, group_item)

            # 更新当前行数
            self.current_row = end_row
            
        except Exception as e:
            logger.error(f"加载统计数据失败: {e}")
            Dialog(
                "错误",
                f"加载统计数据失败: {e}",
                self
            ).exec()
        
    def setup_file_watcher(self):
        """设置文件系统监视器，监控班级历史记录文件夹的变化"""
        roll_call_history_dir = get_path("app/resources/history/roll_call_history")
        if not roll_call_history_dir.exists():
            logger.warning(f"班级历史记录文件夹不存在: {roll_call_history_dir}")
            return
        self.file_watcher = QFileSystemWatcher()
        self.file_watcher.addPath(str(roll_call_history_dir))
        self.file_watcher.directoryChanged.connect(self.on_directory_changed)
        # logger.debug(f"已设置文件监视器，监控目录: {roll_call_history_dir}")

    def on_directory_changed(self, path):
        """当目录内容发生变化时调用此方法
        
        Args:
            path: 发生变化的目录路径
        """
        # logger.debug(f"检测到目录变化: {path}")
        QTimer.singleShot(1000, self.refresh_class_history)
        
    def refresh_class_history(self):
        """刷新班级下拉框列表"""
        if not hasattr(self, 'class_comboBox'):
            return
        current_class_name = self.class_comboBox.currentText()
        class_history = get_all_history_names("roll_call")
        self.class_comboBox.clear()
        self.class_comboBox.addItems(class_history)
        if current_class_name and current_class_name in class_history:
            index = class_history.index(current_class_name)
            self.class_comboBox.setCurrentIndex(index)
        elif not class_history:
            self.class_comboBox.setCurrentIndex(-1)
            self.class_comboBox.setPlaceholderText(get_content_name_async("roll_call_history_table", "select_class_name"))
        if hasattr(self, 'clear_button'):
            self.clear_button.setEnabled(bool(current_class_name))
            
    def on_class_changed(self, index):
        """班级选择变化时刷新表格数据"""
        if not hasattr(self, 'class_comboBox'):
            return
        if index >= 0:
            update_settings("roll_call_history_table", "select_class_name", index)
        if hasattr(self, 'clear_button'):
            self.clear_button.setEnabled(self.class_comboBox.currentIndex() >= 0)
        self.current_class_name = self.class_comboBox.currentText()
        self.refresh_data()
        if hasattr(self, 'table'):
            self.refresh_data()
            
    def refresh_data(self):
        """刷新表格数据"""
        if not hasattr(self, 'table'):
            return
        if not hasattr(self, 'class_comboBox'):
            return
        class_name = self.class_comboBox.currentText()
        if not class_name:
            self.table.setRowCount(0)
            return
        self.current_class_name = class_name
        self.update_table_headers()
        
        # 重置数据加载状态
        self.current_row = 0
        self.is_loading = False
        self.table.setRowCount(0)
        self.table.blockSignals(True)
        
        try:
            if not hasattr(self, 'mode_comboBox'):
                self.current_mode = readme_settings_async("roll_call_history_table", "select_mode")
                if self.current_mode == 0:
                    students = get_student_history(class_name)
                    if students:
                        self.total_rows = len(students)
                        # 设置初始行数为批次大小或总行数，取较小值
                        initial_rows = min(self.batch_size, self.total_rows)
                        self.table.setRowCount(initial_rows)
                        # 加载第一批数据
                        self._load_more_students_data()
                elif self.current_mode == 1:
                    sessions = get_draw_sessions_history(class_name)
                    if sessions:
                        self.total_rows = len(sessions)
                        # 设置初始行数为批次大小或总行数，取较小值
                        initial_rows = min(self.batch_size, self.total_rows)
                        self.table.setRowCount(initial_rows)
                        # 加载第一批数据
                        self._load_more_sessions_data()
                else:
                    # 当模式值大于等于2时，从设置中获取学生姓名
                    self.current_student_name = readme_settings_async("roll_call_history_table", "select_student_name")
                    stats = get_individual_statistics(class_name, self.current_student_name)
                    if stats:
                        self.total_rows = len(stats)
                        # 设置初始行数为批次大小或总行数，取较小值
                        initial_rows = min(self.batch_size, self.total_rows)
                        self.table.setRowCount(initial_rows)
                        # 加载第一批数据
                        self._load_more_stats_data(self.current_student_name)
                return
                
            self.current_mode = self.mode_comboBox.currentIndex()
            if self.current_mode == 0:
                students = get_student_history(class_name)
                if students:
                    self.total_rows = len(students)
                    # 设置初始行数为批次大小或总行数，取较小值
                    initial_rows = min(self.batch_size, self.total_rows)
                    self.table.setRowCount(initial_rows)
                    # 加载第一批数据
                    self._load_more_students_data()
            elif self.current_mode == 1:
                sessions = get_draw_sessions_history(class_name)
                if sessions:
                    self.total_rows = len(sessions)
                    # 设置初始行数为批次大小或总行数，取较小值
                    initial_rows = min(self.batch_size, self.total_rows)
                    self.table.setRowCount(initial_rows)
                    # 加载第一批数据
                    self._load_more_sessions_data()
            else:
                stats = get_individual_statistics(class_name, self.mode_comboBox.currentText())
                if stats:
                    self.total_rows = len(stats)
                    # 设置初始行数为批次大小或总行数，取较小值
                    initial_rows = min(self.batch_size, self.total_rows)
                    self.table.setRowCount(initial_rows)
                    self.current_student_name = self.mode_comboBox.currentText()
                    # 加载第一批数据
                    self._load_more_stats_data(self.current_student_name)
                    
            # 设置表格列属性
            for i in range(self.table.columnCount()):
                self.table.horizontalHeader().setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)
                self.table.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)
                
        except Exception as e:
            logger.error(f"刷新表格数据失败: {str(e)}")
        finally:
            self.table.blockSignals(False)
            
    def update_table_headers(self):
        """更新表格标题"""
        if not hasattr(self, 'table'):
            return
            
        if hasattr(self, 'mode_comboBox'):
            self.current_mode = self.mode_comboBox.currentIndex()
        else:
            self.current_mode = readme_settings_async("roll_call_history_table", "select_mode")
            
        if self.current_mode == 0:
            if readme_settings_async("roll_call_history_table", "select_weight"):
                headers = get_content_name_async("roll_call_history_table", "HeaderLabels_all_weight")
            else:
                headers = get_content_name_async("roll_call_history_table", "HeaderLabels_all_not_weight")
            self.table.setColumnCount(len(headers))
            self.table.setHorizontalHeaderLabels(headers)
        elif self.current_mode == 1:
            headers = get_content_name_async("roll_call_history_table", "HeaderLabels_Session")
            self.table.setColumnCount(len(headers))
            self.table.setHorizontalHeaderLabels(headers)
        else:
            headers = get_content_name_async("roll_call_history_table", "HeaderLabels_Individual")
            self.table.setColumnCount(len(headers))
            self.table.setHorizontalHeaderLabels(headers)
