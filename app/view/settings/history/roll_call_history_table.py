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
        self.current_mode = 0
        self.batch_size = 50  # 每次加载的行数
        self.current_row = 0  # 当前加载到的行数
        self.total_rows = 0   # 总行数
        self.is_loading = False  # 是否正在加载数据
        
        # 创建班级选择区域
        QTimer.singleShot(APPLY_DELAY, self.create_class_selection)
        
        # 创建表格区域
        QTimer.singleShot(APPLY_DELAY, self.create_table)
        
        # 创建按钮区域
        QTimer.singleShot(APPLY_DELAY, self.create_buttons)
        
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
        self.mode_comboBox = ComboBox()
        self.mode_comboBox.addItems(get_content_combo_name_async("roll_call_history_table", "select_mode"))
        self.mode_comboBox.setCurrentIndex(readme_settings_async("roll_call_history_table", "select_mode"))
        self.mode_comboBox.currentIndexChanged.connect(lambda: update_settings("roll_call_history_table", "select_mode", self.mode_comboBox.currentIndex()))
        self.mode_comboBox.currentTextChanged.connect(self.refresh_data)

        self.addGroup(get_theme_icon("ic_fluent_class_20_filled"), 
                        get_content_name_async("roll_call_history_table", "select_class_name"), get_content_description_async("roll_call_history_table", "select_class_name"), self.class_comboBox)
        self.addGroup(get_theme_icon("ic_fluent_reading_mode_mobile_20_filled"), 
                        get_content_name_async("roll_call_history_table", "select_mode"), get_content_description_async("roll_call_history_table", "select_mode"), self.mode_comboBox)
        
    def create_buttons(self):
        """创建按钮区域"""
        # 创建清除历史记录按钮
        self.clear_button = PushButton(get_content_name_async("roll_call_history_table", "clear_history"))
        self.clear_button.clicked.connect(self.clear_history)
        self.clear_button.setEnabled(False)
        
        # 添加按钮到布局
        self.addGroup(get_theme_icon("ic_fluent_delete_20_filled"), 
                        get_content_name_async("roll_call_history_table", "clear_history"), 
                        get_content_description_async("roll_call_history_table", "clear_history"), 
                        self.clear_button)
        
    def clear_history(self):
        """清除当前班级的历史记录"""
        class_name = self.class_comboBox.currentText()
        if not class_name:
            return
        dialog = Dialog(
            get_content_name_async("roll_call_history_table", "confirm_clear_title"),
            get_content_name_async("roll_call_history_table", "confirm_clear_message").format(class_name=class_name),
            self
        )
        dialog.yesButton.setText(get_content_name_async("roll_call_history_table", "confirm_yes"))
        dialog.cancelButton.setText(get_content_name_async("roll_call_history_table", "confirm_no"))
        if dialog.exec():
            success = clear_history("roll_call", class_name)
            
            if success:
                success_dialog = Dialog(
                    get_content_name_async("roll_call_history_table", "clear_success_title"),
                    get_content_name_async("roll_call_history_table", "clear_success_message").format(class_name=class_name),
                    self
                )
                success_dialog.cancelButton.hide()
                success_dialog.buttonLayout.insertStretch(1)
                success_dialog.yesButton.setText(get_content_name_async("roll_call_history_table", "dialog_ok"))
                success_dialog.exec()
                self.refresh_class_history()
            else:
                error_dialog = Dialog(
                    get_content_name_async("roll_call_history_table", "clear_error_title"),
                    get_content_name_async("roll_call_history_table", "clear_error_message").format(class_name=class_name),
                    self
                )
                error_dialog.cancelButton.hide()
                error_dialog.buttonLayout.insertStretch(1)
                error_dialog.yesButton.setText(get_content_name_async("roll_call_history_table", "dialog_ok"))
                error_dialog.exec()
        
    def create_table(self):
        """创建表格区域"""
        # 创建表格
        self.table = TableWidget()
        self.table.setBorderVisible(True)
        self.table.setBorderRadius(8)
        self.table.setWordWrap(False)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSortingEnabled(True)
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
        
        # 当滚动到接近底部时，加载更多数据
        if current_value >= max_value * 0.8:  # 滚动到80%位置时触发
            self._load_more_data()
    
    def _load_more_data(self):
        """加载更多数据"""
        if self.is_loading or self.current_row >= self.total_rows:
            return
            
        self.is_loading = True

        self.current_mode = readme_settings_async("roll_call_history_table", "select_mode")
        
        # 根据当前模式加载数据
        if self.current_mode == 0:
            self._load_more_students_data()
        elif self.current_mode == 1:
            self._load_more_sessions_data()
        elif self.current_mode == 2:
            self._load_more_stats_data()
            
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
            
            students_data = []
            for student_id, name, gender, group in cleaned_students:
                count = int(history_data.get('student', {}).get(name, {}).get('total_count', 0))
                group_gender_count = int(history_data.get('student', {}).get(name, {}).get('group_gender_count', 0))
                total_count = count + group_gender_count
                students_data.append({
                    'id': str(student_id).zfill(max_id_length),
                    'name': name,
                    'gender': gender,
                    'group': group, 
                    'total_count': total_count
                })
            
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
                total_count_item = create_table_item(str(student.get('total_count', 0)))
                self.table.setItem(row, 4, total_count_item)
                
                # 如果需要显示权重
                if self.table.columnCount() > 5:
                    # 计算权重
                    weight = calculate_weight(student)
                    weight_item = create_table_item(format_table_item(weight))
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
            # 初始化历史数据字典
            history_data = {}
            # 读取历史记录文件
            history_file = get_resources_path('history/roll_call_history', f'{self.current_class_name}.json')

            if file_exists(history_file):
                try:
                    with open_file(history_file, 'r', encoding='utf-8') as f:
                        history_data = json.load(f)
                except json.JSONDecodeError:
                    history_data = {}
            
            # 获取会话数据
            sessions_data = []
            
            # 按时间排序
            sessions_data.sort(key=lambda x: x.get('draw_time', ''), reverse=True)
            
            # 计算本次加载的起始和结束位置
            start_row = self.current_row
            end_row = min(start_row + self.batch_size, self.total_rows)
            
            # 填充表格数据
            for i in range(start_row, end_row):
                if i >= len(sessions_data):
                    break
                    
                session = sessions_data[i]
                row = i
                
                # 时间
                time_item = create_table_item(session.get('draw_time', session.get('timestamp', '')))
                self.table.setItem(row, 0, time_item)
                
                # 学号
                selected_students = session.get('selected_students', [])
                student_ids = []
                for student in selected_students:
                    student_ids.append(str(student.get('student_id', student.get('id', ''))))
                
                id_item = create_table_item(', '.join(student_ids))
                self.table.setItem(row, 1, id_item)
                
                # 姓名（显示选中学生的姓名列表）
                names = [student.get('name', '') for student in selected_students]
                name_item = create_table_item(', '.join(names))
                self.table.setItem(row, 2, name_item)
                
                # 性别
                gender = session.get('parameters', {}).get('gender', '全部')
                gender_item = create_table_item(str(gender) if gender else '全部')
                self.table.setItem(row, 3, gender_item)
                
                # 小组
                group = session.get('parameters', {}).get('group', '全部')
                group_item = create_table_item(str(group) if group else '全部')
                self.table.setItem(row, 4, group_item)
            
            # 更新当前行数
            self.current_row = end_row
            
        except Exception as e:
            logger.error(f"加载会话数据失败: {e}")
            # 显示错误信息
            Dialog(
                "错误",
                f"加载会话数据失败: {e}",
                self
            ).exec()
    
    def _load_more_stats_data(self):
        """加载更多统计数据"""
        if not self.current_class_name:
            return
            
        # 使用Changeable_history.py中的_get_class_students方法获取数据
        try:
            # 读取历史记录文件
            history_file = get_resources_path('history/roll_call_history', f'{self.current_class_name}.json')
            
            # 初始化历史数据字典
            history_data = {}
            if file_exists(history_file):
                try:
                    with open_file(history_file, 'r', encoding='utf-8') as f:
                        history_data = json.load(f)
                except json.JSONDecodeError:
                    history_data = {}
            
            # 获取统计数据
            stats_data = []
            # 首先尝试从pumping_people获取数据
            if 'pumping_people' in history_data:
                pumping_people = history_data['pumping_people']
                # 从每个学生的time数组中提取统计信息
                for student_name, student_data in pumping_people.items():
                    if 'time' in student_data and isinstance(student_data['time'], list):
                        for session in student_data['time']:
                            # 创建统计对象
                            stat_obj = {
                                'time': session.get('draw_time', ''),
                                'mode': session.get('draw_method', ''),
                                'people_count': len(session.get('draw_people_numbers', [])) if 'draw_people_numbers' in session else 0,
                                'gender': '全部',  # 默认值
                                'group': '全部'   # 默认值
                            }
                            
                            stats_data.append(stat_obj)
            
            # 如果没有从pumping_people获取到数据，尝试从statistics获取
            elif 'statistics' in history_data:
                stats_data = history_data['statistics']
            
            # 按时间排序
            stats_data.sort(key=lambda x: x.get('time', ''), reverse=True)
            
            # 计算本次加载的起始和结束位置
            start_row = self.current_row
            end_row = min(start_row + self.batch_size, self.total_rows)
            
            # 填充表格数据
            for i in range(start_row, end_row):
                if i >= len(stats_data):
                    break
                    
                stat = stats_data[i]
                row = i
                
                # 时间
                time_item = create_table_item(stat.get('time', ''))
                self.table.setItem(row, 0, time_item)
                
                # 模式
                mode_item = create_table_item(stat.get('mode', ''))
                self.table.setItem(row, 1, mode_item)
                
                # 人数
                people_count_item = create_table_item(str(stat.get('people_count', stat.get('count', 0))))
                self.table.setItem(row, 2, people_count_item)
                
                # 性别
                gender = stat.get('gender', '')
                gender_item = create_table_item(gender if gender else '全部')
                self.table.setItem(row, 3, gender_item)
                
                # 小组
                group = stat.get('group', '')
                group_item = create_table_item(group if group else '全部')
                self.table.setItem(row, 4, group_item)
            
            # 更新当前行数
            self.current_row = end_row
            
        except Exception as e:
            logger.error(f"加载统计数据失败: {e}")
            # 显示错误信息
            Dialog(
                "错误",
                f"加载统计数据失败: {e}",
                self
            ).exec()
        
    def setup_file_watcher(self):
        """设置文件系统监视器，监控班级历史记录文件夹的变化"""
        # 获取班级历史记录文件夹路径
        roll_call_history_dir = get_path("app/resources/history/roll_call_history")
        
        # 确保目录存在
        if not roll_call_history_dir.exists():
            logger.warning(f"班级历史记录文件夹不存在: {roll_call_history_dir}")
            return
            
        # 创建文件系统监视器
        self.file_watcher = QFileSystemWatcher()
        
        # 监视目录
        self.file_watcher.addPath(str(roll_call_history_dir))
        
        # 连接信号
        self.file_watcher.directoryChanged.connect(self.on_directory_changed)
        # logger.debug(f"已设置文件监视器，监控目录: {roll_call_history_dir}")

    def on_directory_changed(self, path):
        """当目录内容发生变化时调用此方法
        
        Args:
            path: 发生变化的目录路径
        """
        # logger.debug(f"检测到目录变化: {path}")
        # 延迟刷新，避免文件操作未完成
        QTimer.singleShot(1000, self.refresh_class_history)
        
    def refresh_class_history(self):
        """刷新班级下拉框列表"""
        # 检查class_comboBox是否存在
        if not hasattr(self, 'class_comboBox'):
            return
            
        # 保存当前选中的班级名称
        current_class_name = self.class_comboBox.currentText()
        
        # 获取最新的班级列表
        class_history = get_all_history_names("roll_call")
        
        # 清空并重新添加班级列表
        self.class_comboBox.clear()
        self.class_comboBox.addItems(class_history)
        
        # 尝试恢复之前选中的班级
        if current_class_name and current_class_name in class_history:
            index = class_history.index(current_class_name)
            self.class_comboBox.setCurrentIndex(index)
        elif not class_history:
            self.class_comboBox.setCurrentIndex(-1)
            self.class_comboBox.setPlaceholderText(get_content_name_async("roll_call_history_table", "select_class_name"))
        
        # 启用或禁用清除按钮
        if hasattr(self, 'clear_button'):
            self.clear_button.setEnabled(bool(current_class_name))
            
    def on_class_changed(self, index):
        """班级选择变化时刷新表格数据"""
        # 检查class_comboBox是否存在
        if not hasattr(self, 'class_comboBox'):
            return
            
        # 更新设置（当index有效时）
        if index >= 0:
            update_settings("roll_call_history_table", "select_class_name", index)
        
        # 更新清除按钮状态
        if hasattr(self, 'clear_button'):
            self.clear_button.setEnabled(self.class_comboBox.currentIndex() >= 0)
        
        # 更新当前班级名称
        self.current_class_name = self.class_comboBox.currentText()
        
        # 刷新表格数据
        self.refresh_data()
        
        # logger.debug(f"班级列表已刷新，共 {len(class_history)} 个班级")
        # 只有在表格已经创建时才刷新数据
        if hasattr(self, 'table'):
            self.refresh_data()
            
    def refresh_data(self):
        """刷新表格数据"""
        # 确保表格已经创建
        if not hasattr(self, 'table'):
            return
            
        # 检查class_comboBox是否存在
        if not hasattr(self, 'class_comboBox'):
            return
            
        class_name = self.class_comboBox.currentText()
        if not class_name:
            self.table.setRowCount(0)
            return
            
        # 更新当前班级名称
        self.current_class_name = class_name
            
        # 更新表格头
        self.update_table_headers()
            
        # 重置分页参数
        self.current_row = 0
        self.is_loading = False
        
        # 清空表格
        self.table.setRowCount(0)
            
        # 临时阻止信号，避免初始化时触发保存操作
        self.table.blockSignals(True)
            
        try:
            # 检查mode_comboBox是否存在
            if not hasattr(self, 'mode_comboBox'):
                # 如果mode_comboBox不存在，使用默认模式
                self.current_mode = 0
                # 获取学生数据
                students = get_student_history(class_name)
                if students:
                    # 设置总行数
                    self.total_rows = len(students)
                    # 设置初始行数
                    initial_rows = min(self.batch_size, self.total_rows)
                    self.table.setRowCount(initial_rows)
                    # 加载第一批数据
                    self._load_more_students_data()
                return
                
            # 获取当前选择的模式
            mode_index = self.mode_comboBox.currentIndex()
            mode_items = get_content_combo_name_async("roll_call_history_table", "select_mode")
            
            if mode_index >= 0 and mode_index < len(mode_items):
                mode = mode_items[mode_index]
                # 更新当前模式
                self.current_mode = mode
                
                # 根据模式获取不同的数据
                if mode == 0:
                    # 获取学生数据
                    students = get_student_history(class_name)
                    if students:
                        # 设置总行数
                        self.total_rows = len(students)
                        # 设置初始行数
                        initial_rows = min(self.batch_size, self.total_rows)
                        self.table.setRowCount(initial_rows)
                        # 加载第一批数据
                        self._load_more_students_data()
                elif mode == 1:
                    # 获取时间模式数据
                    sessions = get_draw_sessions_history(class_name)
                    if sessions:
                        # 设置总行数
                        self.total_rows = len(sessions)
                        # 设置初始行数
                        initial_rows = min(self.batch_size, self.total_rows)
                        self.table.setRowCount(initial_rows)
                        # 加载第一批数据
                        self._load_more_sessions_data()
                elif mode == 2:
                    # 获取个人统计模式数据
                    stats = get_individual_statistics(class_name)
                    if stats:
                        # 设置总行数
                        self.total_rows = len(stats)
                        # 设置初始行数
                        initial_rows = min(self.batch_size, self.total_rows)
                        self.table.setRowCount(initial_rows)
                        # 加载第一批数据
                        self._load_more_stats_data()
                else:
                    # 默认使用全部模式
                    self.current_mode = 0
                    students = get_student_history(class_name)
                    if students:
                        # 设置总行数
                        self.total_rows = len(students)
                        # 设置初始行数
                        initial_rows = min(self.batch_size, self.total_rows)
                        self.table.setRowCount(initial_rows)
                        # 加载第一批数据
                        self._load_more_students_data()
            else:
                # 默认使用全部模式
                self.current_mode = 0
                students = get_student_history(class_name)
                if students:
                    # 设置总行数
                    self.total_rows = len(students)
                    # 设置初始行数
                    initial_rows = min(self.batch_size, self.total_rows)
                    self.table.setRowCount(initial_rows)
                    # 加载第一批数据
                    self._load_more_students_data()
                
            # 调整列宽
            for i in range(self.table.columnCount()):
                self.table.horizontalHeader().setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)
                self.table.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)
            
        except Exception as e:
            logger.error(f"刷新表格数据失败: {str(e)}")
        finally:
            # 恢复信号
            self.table.blockSignals(False)
            
    def update_table_headers(self):
        """根据选择的模式更新表格头"""
        # 检查mode_comboBox是否存在
        if not hasattr(self, 'mode_comboBox'):
            # 如果mode_comboBox不存在，使用默认模式
            headers = get_content_name_async("roll_call_history_table", "HeaderLabels_all_not_weight")
            self.table.setColumnCount(len(headers))
            self.table.setHorizontalHeaderLabels(headers)
            return
            
        # 获取当前选择的模式
        mode_index = self.mode_comboBox.currentIndex()
        mode_items = get_content_combo_name_async("roll_call_history_table", "select_mode")
        
        if mode_index >= 0 and mode_index < len(mode_items):
            mode = mode_items[mode_index]
            
            # 根据模式设置表格头和列数
            if mode == 0:
                # 默认显示不包含权重的全部信息
                headers = get_content_name_async("roll_call_history_table", "HeaderLabels_all_not_weight")
                self.table.setColumnCount(len(headers))
                self.table.setHorizontalHeaderLabels(headers)
            elif mode == 1:
                # 显示时间模式
                headers = get_content_name_async("roll_call_history_table", "HeaderLabels_time")
                self.table.setColumnCount(len(headers))
                self.table.setHorizontalHeaderLabels(headers)
            elif mode == 2:
                # 显示个人统计模式
                headers = get_content_name_async("roll_call_history_table", "HeaderLabels_Individual")
                self.table.setColumnCount(len(headers))
                self.table.setHorizontalHeaderLabels(headers)
            else:
                # 默认使用不包含权重的全部信息
                headers = get_content_name_async("roll_call_history_table", "HeaderLabels_all_not_weight")
                self.table.setColumnCount(len(headers))
                self.table.setHorizontalHeaderLabels(headers)
        else:
            # 默认使用不包含权重的全部信息
            headers = get_content_name_async("roll_call_history_table", "HeaderLabels_all_not_weight")
            self.table.setColumnCount(len(headers))
            self.table.setHorizontalHeaderLabels(headers)
