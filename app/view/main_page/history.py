from qfluentwidgets import *
from qfluentwidgets import FluentIcon as FIF 
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import os
from datetime import datetime
import math
import json
from loguru import logger

from app.common.config import cfg, AUTHOR, VERSION, YEAR
from app.common.config import get_theme_icon, load_custom_font
from app.common.path_utils import path_manager, open_file, remove_file

from app.common.history_settings import history_SettinsCard
from app.view.main_page.pumping_people import pumping_people

class HistoryDataLoader(QThread):
    """历史记录数据加载线程"""
    data_loaded = pyqtSignal(str, str, list)  # class_name, student_name, data
    error_occurred = pyqtSignal(str)  # error_message
    
    def __init__(self, history_setting_card):
        super().__init__()
        self.history_setting_card = history_setting_card
        self._is_running = True
    
    def run(self):
        """执行数据加载"""
        try:
            class_name = self.history_setting_card.class_comboBox.currentText()
            student_name = self.history_setting_card.student_comboBox.currentText()
            data = self._get_class_students()
            
            if self._is_running:
                self.data_loaded.emit(class_name, student_name, data)
        except Exception as e:
            if self._is_running:
                self.error_occurred.emit(str(e))
    
    def stop(self):
        """停止线程"""
        self._is_running = False
        self.wait()
    
    def _get_class_students(self):
        """根据班级/学生名称获取历史记录数据"""
        # 获取班级名称
        class_name = self.history_setting_card.class_comboBox.currentText()
        _student_name = self.history_setting_card.student_comboBox.currentText()
        if _student_name == '全班同学':
            if class_name:
                # 读取配置文件
                student_file = path_manager.get_resource_path('list', f'{class_name}.json')

                try:
                    with open_file(student_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        cleaned_data = []
                        __cleaned_data = []
                        for student_name, student_info in data.items():
                            if isinstance(student_info, dict) and 'id' in student_info:
                                id = student_info.get('id', '')
                                name = student_name.replace('【', '').replace('】', '')
                                gender = student_info.get('gender', '')
                                group = student_info.get('group', '')
                                exist = student_info.get('exist', True)
                                cleaned_data.append((id, name, gender, group, exist))
                                __cleaned_data.append((id, name, exist))

                    cleaned_data = list(filter(lambda x: x[4], cleaned_data))
                    __cleaned_data = list(filter(lambda x: x[2], __cleaned_data))

                    students = [item[1] for item in cleaned_data]
                    
                    # 直接从JSON数据获取小组信息
                    students_group = [item[3] for item in cleaned_data]
                        
                    # 初始化历史数据字典
                    history_data = {}
                    # 读取历史记录文件
                    history_file = path_manager.get_resource_path('history', f'{class_name}.json')

                    if path_manager.file_exists(history_file):
                        try:
                            with open_file(history_file, 'r', encoding='utf-8') as f:
                                history_data = json.load(f)
                        except json.JSONDecodeError:
                            history_data = {}

                    # 生成学号(从1开始)并返回学生数据，包含被点次数信息
                    student_data = []
                    # 先遍历一次计算各列最大位数
                    max_digits = {
                        'id': 0,
                        'pumping_people': 0
                    }

                    for i, student in enumerate(students):
                        student_name = student if not (student.startswith('【') and student.endswith('】')) else student[1:-1]
                        max_digits['id'] = max(max_digits['id'], len(str(cleaned_data[i][0])))
                        if 'pumping_people' in history_data and student_name in history_data['pumping_people']:
                            count = int(history_data['pumping_people'][student_name]['total_number_of_times'])
                            count_auxiliary = int(history_data['pumping_people'][student_name]['total_number_auxiliary'])
                            total = count + count_auxiliary
                            max_digits['pumping_people'] = max(max_digits['pumping_people'], len(str(total)))

                    available_students = __cleaned_data

                    # 获取当前抽取模式
                    settings_file = path_manager.get_settings_path()
                    try:
                        with open_file(settings_file, 'r', encoding='utf-8') as f:
                            settings = json.load(f)
                            pumping_people_draw_mode = settings['pumping_people']['draw_mode']
                    except Exception as e:
                        pumping_people_draw_mode = 0
                        logger.error(f"加载设置时出错: {e}, 使用默认设置")

                    # 根据抽选模式执行不同逻辑
                    # 跟随全局设置
                    if pumping_people_draw_mode == 0:  # 重复随机
                        self.draw_mode = "random"
                    elif pumping_people_draw_mode == 1:  # 不重复抽取(直到软件重启)
                        self.draw_mode = "until_reboot"
                    elif pumping_people_draw_mode == 2:  # 不重复抽取(直到抽完全部人)
                        self.draw_mode = "until_all"

                    # 实例化 pumping_people 一次
                    if not hasattr(self, 'pumping_people_instance'):
                        self.pumping_people_instance = pumping_people()

                    group_name = self.pumping_people_instance.group_combo.currentText()
                    genders = self.pumping_people_instance.gender_combo.currentText()

                    if self.draw_mode == "until_reboot":
                        if group_name == '抽取全班学生':
                            draw_record_file = f"app/resource/Temp/until_the_reboot_{class_name}_{group_name}_{genders}.json"
                        elif group_name == '抽取小组组号':
                            draw_record_file = f"app/resource/Temp/until_the_reboot_{class_name}_{group_name}.json"
                        else:
                            draw_record_file = f"app/resource/Temp/until_the_reboot_{class_name}_{group_name}_{genders}.json"
                    elif self.draw_mode == "until_all":
                        if group_name == '抽取全班学生':
                            draw_record_file = f"app/resource/Temp/until_all_draw_{class_name}_{group_name}_{genders}.json"
                        elif group_name == '抽取小组组号':
                            draw_record_file = f"app/resource/Temp/until_all_draw_{class_name}_{group_name}.json"
                        else:
                            draw_record_file = f"app/resource/Temp/until_all_draw_{class_name}_{group_name}_{genders}.json"
                    
                    if self.draw_mode in ['until_reboot', 'until_all']:
                        # 确保文件存在
                        if path_manager.file_exists(draw_record_file):
                            # 读取已抽取记录
                            drawn_students = []
                            with open_file(draw_record_file, 'r', encoding='utf-8') as f:
                                try:
                                    drawn_students = json.load(f)
                                except json.JSONDecodeError:
                                    drawn_students = []
                        else:
                            drawn_students = []
                    else:
                        drawn_students = []

                    # 预加载设置文件
                    try:
                        with open_file(settings_file, 'r', encoding='utf-8') as f:
                            settings = json.load(f)
                            probability_weight = settings['history']['probability_weight']
                    except Exception as e:
                        probability_weight = 1
                        logger.error(f"加载设置时出错: {e}, 使用默认设置")

                    # 预计算有效统计
                    valid_groups = {group: count for group, count in history_data.get("group_stats", {}).items() if count > 0}
                    valid_genders = {gender: count for gender, count in history_data.get("gender_stats", {}).items() if count > 0}

                    # 创建学生信息映射表
                    student_info_map = {
                        student[1]: (student[3], student[2]) 
                        for student in cleaned_data
                    }

                    # 批量计算权重
                    available_students_weights = {}
                    total_weight = 0

                    for student_id, student_name, exist in available_students:
                        if not exist:
                            continue

                        # 获取预存的学生信息
                        current_student_group, current_student_gender = student_info_map.get(student_name, ('', ''))

                        # 快速计算权重因子
                        student_history = history_data.get("pumping_people", {}).get(student_name, {
                            "total_number_of_times": 0,
                            "last_drawn_time": None,
                            "rounds_missed": 0,
                            "time": []
                        })

                        # 频率因子
                        freq = student_history["total_number_of_times"]
                        frequency_factor = 1.0 / math.sqrt(freq * 2 + 1)

                        # 小组因子
                        group_history = valid_groups.get(current_student_group, 0)
                        group_factor = 1.0 / (group_history * 0.2 + 1) if len(valid_groups) > 3 else 1.0

                        # 性别因子
                        gender_history = valid_genders.get(current_student_gender, 0)
                        gender_factor = 1.0 / (gender_history * 0.2 + 1) if len(valid_genders) > 3 else 1.0

                        # 冷启动处理
                        current_round = history_data.get("total_rounds", 0)
                        if current_round < 10:
                            frequency_factor = min(0.8, frequency_factor)

                        # 综合权重
                        comprehensive_weight = 0.2 + (frequency_factor * 3) + (group_factor * 0.8) + (gender_factor * 0.8)
                        comprehensive_weight = max(0.5, min(comprehensive_weight, 5.0))

                        # 处理不重复模式
                        if self.draw_mode in ['until_reboot', 'until_all'] and \
                           student_name in drawn_students and \
                           len(drawn_students) < len(students):
                            comprehensive_weight = 0

                        available_students_weights[student_name] = comprehensive_weight
                        total_weight += comprehensive_weight

                    # 批量生成结果数据
                    student_data = []
                    for i, (student, cleaned_student_info) in enumerate(zip(students, cleaned_data)):
                        student_name = student if not (student.startswith('【') and student.endswith('】')) else student[1:-1]
                        
                        pumping_people_count = int(history_data['pumping_people'].get(student_name, {}).get('total_number_of_times', 0)) if 'pumping_people' in history_data else 0
                        pumping_people_count_auxiliary = int(history_data['pumping_people'].get(student_name, {}).get('total_number_auxiliary', 0)) if 'pumping_people' in history_data else 0
                        total_pumping_count = pumping_people_count + pumping_people_count_auxiliary
                        
                        if _student_name == '全班同学_时间排序':
                            # 时间排序模式，需要从历史记录中提取时间信息
                            time_records = []
                            if 'pumping_people' in history_data and student_name in history_data['pumping_people']:
                                for record in history_data['pumping_people'][student_name].get('time', []):
                                    time_records.append(record.get('draw_time', ''))
                            
                            # 按时间倒序排序
                            time_records.sort(reverse=True)
                            
                            # 为每个时间记录创建一行数据
                            for time_record in time_records:
                                student_data.append([
                                    time_record,
                                    str(cleaned_student_info[0]).zfill(max_digits['id']),
                                    student_name,
                                    cleaned_student_info[2],
                                    cleaned_student_info[3]
                                ])
                        else:
                            # 普通模式，只显示一行学生信息
                            row_data = [
                                str(cleaned_student_info[0]).zfill(max_digits['id']),
                                student_name,
                                cleaned_student_info[2],
                                cleaned_student_info[3],
                                str(total_pumping_count).zfill(max_digits['pumping_people'])
                            ]
                            
                            # 如果需要显示概率/权重
                            if self.get_random_method_setting() in [2, 3]:
                                probability_method = self.get_probability_weight_method_setting()
                                weight = available_students_weights.get(student_name, 1.0)
                                if probability_method == 1:  # 概率
                                    probability = (weight / total_weight * 100) if total_weight > 0 else 0
                                    row_data.append(f"{probability:.2f}%")
                                else:  # 权重
                                    row_data.append(f"{weight:.2f}")
                            
                            student_data.append(row_data)

                    return student_data

                except Exception as e:
                    logger.error(f"读取学生名单文件失败: {e}")
                    raise Exception(f"读取学生名单文件失败: {e}")
            else:
                return []
        else:
            if class_name:
                try:
                    # 初始化历史数据字典
                    history_data = {}
                    # 读取历史记录文件
                    history_file = path_manager.get_resource_path('history', f'{class_name}.json')

                    if path_manager.file_exists(history_file):
                        try:
                            with open_file(history_file, 'r', encoding='utf-8') as f:
                                history_data = json.load(f)
                        except json.JSONDecodeError:
                            history_data = {}
                    
                    # 获取个人历史记录
                    student_data = []
                    if 'pumping_people' in history_data and _student_name in history_data['pumping_people']:
                        student_history = history_data['pumping_people'][_student_name]
                        
                        # 处理抽取记录
                        for record in student_history.get('time', []):
                            time = record.get('draw_time', '')
                            draw_method = record.get('draw_method', '')
                            
                            # 统一处理抽取方式文本
                            draw_method_map = {
                                'random': '重复抽取',
                                'until_reboot': '不重复抽取(直到软件重启)',
                                'until_all': '不重复抽取(直到抽完全部人)'
                            }
                            draw_method_text = draw_method_map.get(draw_method, draw_method)
                            
                            # 获取抽取时的选择信息
                            draw_numbers = record.get('draw_numbers', '')
                            if isinstance(draw_numbers, list):
                                draw_numbers = ', '.join(map(str, draw_numbers))
                            
                            draw_group = record.get('draw_group', '')
                            draw_gender = record.get('draw_gender', '')
                            
                            student_data.append([
                                time,
                                draw_method_text,
                                str(draw_numbers),
                                draw_group,
                                draw_gender
                            ])
                    
                    # 按时间倒序排序
                    student_data.sort(reverse=True, key=lambda x: x[0])
                    return student_data
                    
                except Exception as e:
                    logger.error(f"读取学生历史记录失败: {e}")
                    raise Exception(f"读取学生历史记录失败: {e}")
            else:
                return []
    
    def get_random_method_setting(self) -> int:
        """获取随机抽取方法的设置"""
        return self._get_setting_value('pumping_people', 'draw_pumping', 0)
    
    def get_probability_weight_method_setting(self) -> int:
        """获取概率权重方法设置"""
        return self._get_setting_value('history', 'probability_weight', 0)
    
    def _get_setting_value(self, section: str, key: str, default: int) -> int:
        """通用设置读取方法"""
        settings_file = path_manager.get_settings_path()
        try:
            with open_file(settings_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                return settings[section][key]
        except Exception as e:
            logger.error(f"加载设置时出错: {e}, 使用默认设置")
            return default

class history(QFrame):
    def __init__(self, parent: QFrame = None, load_on_init: bool = True):
        super().__init__(parent=parent)

        # 创建一个 QScrollArea
        self.scroll_area_personal = SingleDirectionScrollArea(self)
        self.scroll_area_personal.setWidgetResizable(True)
        # 设置滚动条样式
        self.scroll_area_personal.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollArea QWidget {
                border: none;
                background-color: transparent;
            }
        """)
        # 启用触屏滚动
        QScroller.grabGesture(self.scroll_area_personal.viewport(), QScroller.LeftMouseButtonGesture)

        # 创建一个内部的 QFrame 用于放置内容
        self.inner_frame_personal = QWidget(self.scroll_area_personal)
        self.inner_layout_personal = QVBoxLayout(self.inner_frame_personal)
        self.inner_layout_personal.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignTop)

        # 历史记录设置卡片组
        self.history_setting_card = history_SettinsCard()
        self.inner_layout_personal.addWidget(self.history_setting_card)
        # 检测选择的班级是否改变，如果改变则刷新表格
        self.history_setting_card.class_comboBox.currentIndexChanged.connect(self._refresh_table)
        # 检测选择的同学是否改变，如果改变则刷新表格
        self.history_setting_card.student_comboBox.currentIndexChanged.connect(self._refresh_table)

        # 创建加载状态指示器
        self.loading_widget = self._create_loading_widget()
        self.inner_layout_personal.addWidget(self.loading_widget)

        # 创建表格
        self.table = TableWidget(self.inner_frame_personal) # 创建表格
        self.table.setBorderVisible(True) # 边框
        self.table.setBorderRadius(8) # 圆角
        self.table.setWordWrap(False) # 不换行
        self.table.setEditTriggers(TableWidget.NoEditTriggers) # 静止编辑
        self.table.scrollDelagate.verticalSmoothScroll.setSmoothMode(SmoothMode.NO_SMOOTH) # 静止平滑滚动
        self.table.setSortingEnabled(True) # 启用排序
        self.table.hide()  # 初始隐藏表格

        if load_on_init:
            self.load_data()

    def load_data(self):
        """加载数据"""
        # 检查是否有正在运行的线程
        if hasattr(self, '_data_loader') and self._data_loader and self._data_loader.isRunning():
            self._data_loader.stop()
        
        # 显示加载状态
        self._show_loading_state()
        
        # 创建并启动数据加载线程
        self._data_loader = HistoryDataLoader(self.history_setting_card)
        self._data_loader.data_loaded.connect(self._on_data_loaded)
        self._data_loader.error_occurred.connect(self._on_load_error)
        self._data_loader.start()

    def _on_data_loaded(self, class_name, student_name, data):
        """数据加载完成回调"""
        self._hide_loading_state()
        
        # 显示数据
        self._setup_table_by_mode(student_name, data)
        
        # 显示成功消息
        InfoBar.success(
            title="数据加载成功",
            content=f"成功加载 {class_name} - {student_name} 的历史记录",
            parent=self,
            duration=2000
        )
    
    def _on_load_error(self, error_message):
        """数据加载错误回调"""
        self._hide_loading_state()
        
        # 记录错误
        logger.error(f"数据加载失败: {error_message}")
        
        # 显示错误消息
        InfoBar.error(
            title="数据加载失败",
            content=error_message,
            parent=self,
            duration=3000
        )
        
        # 显示空表格
        self._setup_table_by_mode('', [])
    
    def _show_loading_state(self):
        """显示加载状态"""
        self.loading_widget.show()
        self.table.hide()
    
    def _hide_loading_state(self):
        """隐藏加载状态"""
        self.loading_widget.hide()
        self.table.show()
    
    def _create_loading_widget(self):
        """创建加载状态组件"""
        loading_widget = QWidget()
        loading_layout = QVBoxLayout(loading_widget)
        loading_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 创建占位表格
        self.loading_table = TableWidget()
        self.loading_table.setBorderVisible(True)
        self.loading_table.setBorderRadius(8)
        self.loading_table.setRowCount(1)
        self.loading_table.setColumnCount(1)
        self.loading_table.setHorizontalHeaderLabels(['界面正在加载中...'])
        self.loading_table.verticalHeader().hide()
        self.loading_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        # 填充占位数据
        for i in range(1):
            for j in range(1):
                item = QTableWidgetItem("--")
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                item.setFont(QFont(load_custom_font(), 12))
                item.setForeground(QColor(200, 200, 200))  # 灰色占位符
                self.loading_table.setItem(i, j, item)
        
        loading_layout.addWidget(self.loading_table)
        
        return loading_widget



    def _setup_table_by_mode(self, student_name: str, data: list):
        """根据模式设置表格"""
        if student_name == '全班同学':
            self._setup_class_table(data, include_probability=True)
        elif student_name == '全班同学_时间排序':
            self._setup_class_table(data, include_probability=False, time_sort=True)
        else:
            self._setup_individual_table(data)

    def _setup_class_table(self, data: list, include_probability: bool = True, time_sort: bool = False):
        """设置班级表格"""
        if not data:
            data = []
        
        if time_sort:
            headers = ['时间', '学号', '姓名', '性别', '所处小组']
            self._configure_table(len(data), 5)
        elif include_probability and self.get_random_method_setting() in [2, 3]:
            probability_method = self.get_probability_weight_method_setting()
            headers = ['学号', '姓名', '性别', '所处小组', '总抽取次数', 
                      '下次抽取概率' if probability_method == 1 else '下次抽取权重']
            self._configure_table(len(data), 6)
        else:
            headers = ['学号', '姓名', '性别', '所处小组', '总抽取次数']
            self._configure_table(len(data), 5)
            
        self._fill_table_data(data)
        self.table.setHorizontalHeaderLabels(headers)

    def _setup_individual_table(self, data: list):
        """设置个人表格"""
        current_time = QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm:ss")
        if not data:
            data = []

        self._configure_table(len(data), 5)
        self._fill_table_data(data)
        self.table.setHorizontalHeaderLabels(['时间', '抽取方式', '抽取时选择的人数', '抽取时选择的小组', '抽取时选择的性别'])
        self.table.sortByColumn(0, Qt.SortOrder.DescendingOrder)

    def _configure_table(self, row_count: int, column_count: int):
        """配置表格基本属性"""
        self.table.setRowCount(row_count)
        self.table.setColumnCount(column_count)
        self.table.setSortingEnabled(False)
        self.table.verticalHeader().hide()
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def _fill_table_data(self, data: list):
        """填充表格数据"""
        for i, row in enumerate(data):
            for j in range(len(row)):
                item = QTableWidgetItem(str(row[j]))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                item.setFont(QFont(load_custom_font(), 12))
                self.table.setItem(i, j, item)

        self._setup_layout()

    def _setup_layout(self):
        """设置布局"""
        self.inner_layout_personal.addWidget(self.table)
        self.scroll_area_personal.setWidget(self.inner_frame_personal)
        self.table.setSortingEnabled(True)
        
        if not self.layout():
            main_layout = QVBoxLayout(self)
            main_layout.addWidget(self.scroll_area_personal)
        else:
            self.layout().addWidget(self.scroll_area_personal)

    def get_random_method_setting(self) -> int:
        """获取随机抽取方法的设置"""
        return self._get_setting_value('pumping_people', 'draw_pumping', 0)

    def get_probability_weight_method_setting(self) -> int:
        """获取概率权重方法设置"""
        return self._get_setting_value('history', 'probability_weight', 0)

    def _get_setting_value(self, section: str, key: str, default: int) -> int:
        """通用设置读取方法"""
        settings_file = path_manager.get_settings_path()
        try:
            with open_file(settings_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                return settings[section][key]
        except Exception as e:
            logger.error(f"加载设置时出错: {e}, 使用默认设置")
            return default

    def _refresh_table(self):
        """刷新表格"""
        # 清空表格
        self.table.setRowCount(0)
        # 重新加载表格数据
        self.load_data()

    def __initWidget(self):
        self.__connectSignalToSlot()

    def __connectSignalToSlot(self):
        cfg.themeChanged.connect(setTheme)
