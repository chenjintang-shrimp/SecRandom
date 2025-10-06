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

from app.common.Changeable_history_settings import history_SettinsCard
from app.view.main_page.pumping_people import pumping_people

class HistoryDataLoader(QThread):
    """历史记录数据加载线程"""
    data_loaded = pyqtSignal(str, str, list)  # class_name, student_name, data
    data_segment_loaded = pyqtSignal(str, str, list, int, int)  # class_name, student_name, data, current_segment, total_segments
    error_occurred = pyqtSignal(str)  # error_message
    
    def __init__(self, history_setting_card):
        super().__init__()
        self.history_setting_card = history_setting_card
        self._is_running = True
        self.batch_size = 30  # 初始加载30条数据
        self.enable_segmented_loading = True  # 启用分段加载
        self.total_data = []  # 存储所有数据
        self.current_offset = 0  # 当前加载的偏移量
    
    def run(self):
        """执行数据加载"""
        try:
            class_name = self.history_setting_card.class_comboBox.currentText()
            student_name = self.history_setting_card.student_comboBox.currentText()
            
            # 获取总数据量
            self.total_data = self._get_class_students()
            total_count = len(self.total_data)
            
            if total_count == 0:
                if self._is_running:
                    self.data_loaded.emit(class_name, student_name, [])
                return
            
            # 重置偏移量
            self.current_offset = 0
            
            # 计算初始分段数量
            initial_segments = 1  # 初始只加载一段
            
            # 加载初始数据
            if self._is_running:
                end_idx = min(self.batch_size, total_count)
                initial_data = self.total_data[0:end_idx]
                self.current_offset = end_idx
                
                # 发送初始数据
                self.data_segment_loaded.emit(
                    class_name, 
                    student_name, 
                    initial_data, 
                    1, 
                    math.ceil(total_count / self.batch_size) if total_count > self.batch_size else 1
                )
                
                # 如果数据量小于等于初始加载量，直接发送完成信号
                if total_count <= self.batch_size:
                    if self._is_running:
                        self.data_loaded.emit(class_name, student_name, self.total_data)
        except Exception as e:
            if self._is_running:
                self.error_occurred.emit(str(e))
    
    @pyqtSlot()
    def load_more_data(self):
        """加载更多数据"""
        if not self._is_running or self.current_offset >= len(self.total_data):
            return False
        
        try:
            class_name = self.history_setting_card.class_comboBox.currentText()
            student_name = self.history_setting_card.student_comboBox.currentText()
            
            # 计算当前段和总段数
            current_segment = math.ceil(self.current_offset / self.batch_size) + 1
            total_segments = math.ceil(len(self.total_data) / self.batch_size)
            
            # 加载下一段数据
            end_idx = min(self.current_offset + self.batch_size, len(self.total_data))
            segment_data = self.total_data[self.current_offset:end_idx]
            self.current_offset = end_idx
            
            # 发送分段数据
            self.data_segment_loaded.emit(
                class_name, 
                student_name, 
                segment_data, 
                current_segment, 
                total_segments
            )
            
            # 如果已经加载完所有数据，发送完成信号
            if self.current_offset >= len(self.total_data):
                if self._is_running:
                    self.data_loaded.emit(class_name, student_name, self.total_data)
            
            return True
        except Exception as e:
            if self._is_running:
                self.error_occurred.emit(str(e))
            return False
    
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
                            max_draw_times_per_person = settings['pumping_people']['Draw_pumping']
                    except Exception as e:
                        max_draw_times_per_person = 1
                        logger.error(f"加载设置时出错: {e}, 使用默认设置")

                    # 实例化 pumping_people 一次
                    if not hasattr(self, 'pumping_people_instance'):
                        self.pumping_people_instance = pumping_people()

                    group_name = self.pumping_people_instance.group_combo.currentText()
                    genders = self.pumping_people_instance.gender_combo.currentText()

                    if group_name == '抽取全班学生':
                        draw_record_file = f"app/resource/Temp/{class_name}_{group_name}_{genders}.json"
                    elif group_name == '抽取小组组号':
                        draw_record_file = f"app/resource/Temp/{class_name}_{group_name}.json"
                    else:
                        draw_record_file = f"app/resource/Temp/{class_name}_{group_name}_{genders}.json"
                    
                    if max_draw_times_per_person > 0:
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
                        if max_draw_times_per_person > 0 and \
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
                            row_data = {
                                '学号': str(cleaned_student_info[0]).zfill(max_digits['id']),
                                '姓名': student_name,
                                '性别': cleaned_student_info[2],
                                '所处小组': cleaned_student_info[3],
                                '总抽取次数': str(total_pumping_count).zfill(max_digits['pumping_people'])
                            }
                            
                            # 如果需要显示概率/权重
                            if self.get_random_method_setting() in [2, 3]:
                                probability_method = self.get_probability_weight_method_setting()
                                weight = available_students_weights.get(student_name, 1.0)
                                if probability_method == 1:  # 概率
                                    probability = (weight / total_weight * 100) if total_weight > 0 else 0
                                    row_data['下次抽取概率'] = probability / 100  # 转换为小数形式，便于格式化显示
                                else:  # 权重
                                    row_data['下次抽取权重'] = weight
                            
                            student_data.append(row_data)

                    return student_data

                except Exception as e:
                    logger.error(f"读取学生名单文件失败: {e}")
                    raise Exception(f"读取学生名单文件失败: {e}")
            else:
                return []

        elif _student_name == '全班同学_时间排序':
            if class_name:
                student_file = path_manager.get_resource_path('list', f'{class_name}.json')
                history_file = path_manager.get_resource_path('history', f'{class_name}.json')
                
                # 读取学生名单
                try:
                    with open_file(student_file, 'r', encoding='utf-8') as f:
                        class_data = json.load(f)
                except Exception:
                    return []

                # 清理学生数据
                cleaned_students = []
                for name, info in class_data.items():
                    if isinstance(info, dict) and info.get('exist', True):
                        cleaned_name = name.replace('【', '').replace('】', '')
                        cleaned_students.append((
                            info.get('id', ''),
                            cleaned_name,
                            info.get('gender', ''),
                            info.get('group', '')
                        ))

                # 读取历史记录
                history_data = {}
                if path_manager.file_exists(history_file):
                    try:
                        with open_file(history_file, 'r', encoding='utf-8') as f:
                            history_data = json.load(f).get('pumping_people', {})
                    except json.JSONDecodeError:
                        pass

                # 计算学号最大位数（用于补零对齐）
                max_id_length = max(len(str(student[0])) for student in cleaned_students) if cleaned_students else 0

                # 收集所有抽取记录
                all_records = []
                
                # 遍历每个学生的历史记录
                for (student_id, name, gender, group) in cleaned_students:
                    student_history = history_data.get(name, {})
                    time_records = student_history.get('time', [])
                    
                    for record in time_records:
                        draw_time = record.get('draw_time', '')
                        if draw_time:
                            formatted_id = str(student_id).zfill(max_id_length)
                            all_records.append({
                                'time': draw_time,
                                'id': formatted_id,
                                'name': name,
                                'gender': gender,
                                'group': group
                            })
                
                # 降序
                sorted_records = sorted(all_records, key=lambda x: x['time'], reverse=True)
                
                # 转换为列表格式返回
                result = []
                for record in sorted_records:
                    result.append([
                        record['time'],
                        record['id'],
                        record['name'],
                        record['gender'],
                        record['group']
                    ])
                
                return result
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
                            draw_max = record.get('draw_max', 1)
                            
                            # 统一处理抽取方式文本
                            draw_method_map = {
                                'random': '重复抽取',
                                'until_reboot': '不重复抽取(直到软件重启)',
                                'until_all': '不重复抽取(直到抽完全部人)'
                            }
                            
                            # 检查draw_method是否在映射表中
                            if draw_method in draw_method_map:
                                draw_method_text = draw_method_map[draw_method]
                            else:
                                # 不在映射表中，根据数值判断
                                try:
                                    draw_method_int = int(draw_max)
                                    if draw_method_int == 0:
                                        draw_method_text = '重复抽取'
                                    elif draw_method_int == 1:
                                        draw_method_text = '不重复抽取'
                                    elif draw_method_int >= 2:
                                        draw_method_text = f'半重复抽取({draw_max}次)'
                                    else:
                                        draw_method_text = f'半重复抽取({draw_max}次)'  
                                except (ValueError, TypeError):
                                    # 无法转换为整数，保持原值
                                    draw_method_text = draw_max
                            
                            # 获取抽取时的选择信息
                            draw_numbers = record.get('draw_people_numbers', '')
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
        return self._get_setting_value('pumping_people', 'draw_pumping', 1)
    
    def get_probability_weight_method_setting(self) -> int:
        """获取概率权重方法设置"""
        return self._get_setting_value('history', 'probability_weight', 0)
    
    def _get_setting_value(self, section: str, key: str, default: int) -> int:
        """通用设置读取方法"""
        settings_file = path_manager.get_settings_path()
        try:
            with open_file(settings_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                return settings[section].get(key, default)
        except Exception as e:
            logger.error(f"加载设置时出错: {e}, 使用默认设置")
            return default

class changeable_history(QFrame):
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
        
        # 添加滚动事件监听
        self.table.verticalScrollBar().valueChanged.connect(self._on_scroll)
        
        # 分段加载相关变量
        self._segmented_data = []  # 存储分段加载的数据
        self._current_segment = 0  # 当前加载的段
        self._total_segments = 0   # 总段数
        self._is_loading_segments = False  # 是否正在分段加载
        self._has_more_data = True  # 是否还有更多数据
        self._scroll_threshold = 5  # 滚动阈值，距离底部多少行时加载更多数据

        if load_on_init:
            self.load_data()

    def load_data(self):
        """加载数据"""
        # 检查是否有正在运行的线程
        if hasattr(self, '_data_loader') and self._data_loader and self._data_loader.isRunning():
            self._data_loader.stop()
        
        # 重置所有状态
        self._segmented_data = []
        self._current_segment = 0
        self._total_segments = 0
        self._is_loading_segments = False
        self._has_more_data = True
        
        # 显示加载状态
        self._show_loading_state()
        
        # 创建并启动数据加载线程
        self._data_loader = HistoryDataLoader(self.history_setting_card)
        self._data_loader.data_loaded.connect(self._on_data_loaded)
        self._data_loader.data_segment_loaded.connect(self._on_data_segment_loaded)
        self._data_loader.error_occurred.connect(self._on_load_error)
        self._data_loader.start()

    def _on_scroll(self, value):
        """滚动事件处理"""
        if not self._has_more_data or self._is_loading_segments:
            return
        
        # 获取滚动条最大值
        max_value = self.table.verticalScrollBar().maximum()
        
        # 如果滚动条值为0或者表格为空，不处理
        if max_value == 0 or self.table.rowCount() == 0:
            return
        
        # 获取当前可见的行数
        row_height = self.table.rowHeight(0)
        visible_rows = self.table.viewport().height() // row_height if row_height > 0 else 0
        
        # 计算当前滚动位置对应的行号
        current_row = value // row_height if row_height > 0 else 0
        
        # 计算距离底部还有多少行
        rows_to_bottom = self.table.rowCount() - current_row - visible_rows
        
        # 如果距离底部小于等于阈值，加载更多数据
        if rows_to_bottom <= self._scroll_threshold:
            self._load_more_data()
    
    def _load_more_data(self):
        """加载更多数据"""
        if self._is_loading_segments or not self._has_more_data:
            return
        
        # 设置加载状态
        self._is_loading_segments = True
        
        # 显示加载提示
        InfoBar.info(
            title="加载中",
            content="正在加载更多数据...",
            parent=self,
            duration=1000
        )
        
        # 调用数据加载器的 load_more_data 方法
        if hasattr(self, '_data_loader') and self._data_loader:
            # 使用 QMetaObject.invokeMethod 确保在主线程中调用
            QMetaObject.invokeMethod(self._data_loader, "load_more_data", Qt.QueuedConnection)
        else:
            # 如果没有数据加载器，重置状态
            self._is_loading_segments = False
    
    def _on_data_segment_loaded(self, class_name, student_name, data, current_segment, total_segments):
        """分段数据加载完成回调"""
        # 更新分段加载状态
        self._current_segment = current_segment
        self._total_segments = total_segments
        
        # 将分段数据添加到总数据中
        self._segmented_data.extend(data)
        
        # 如果是第一段数据，初始化表格
        if current_segment == 1:
            self._hide_loading_state()
            # 初始化表格结构，但不填充数据
            if student_name == '全班同学':
                self._setup_class_table_headers(include_probability=True, time_sort=False)
            elif student_name == '全班同学_时间排序':
                self._setup_class_table_headers(include_probability=False, time_sort=True)
            else:
                # 个人历史记录模式
                self._setup_individual_table_headers()
        
        # 填充当前段的数据
        self._fill_table_data(data)
        
        # 检查是否还有更多数据
        self._has_more_data = current_segment < total_segments
        
        # 重置加载状态，允许再次触发加载
        self._is_loading_segments = False
        
        # 更新加载进度
        if self._has_more_data:
            progress_text = f"已加载 {len(self._segmented_data)} 条数据"
            InfoBar.info(
                title="数据加载中",
                content=progress_text,
                parent=self,
                duration=1000
            )
    

    
    def _on_data_loaded(self, class_name, student_name, data):
        """所有数据加载完成回调"""
        self._hide_loading_state()
        
        # 重置加载状态
        self._is_loading_segments = False
        self._has_more_data = False
        
        # 如果是分段加载，所有数据已经通过 _on_data_segment_loaded 处理
        if self._segmented_data and len(self._segmented_data) > 0:
            InfoBar.success(
                title="加载完成",
                content=f"已加载全部 {len(self._segmented_data)} 条数据",
                parent=self,
                duration=2000
            )
        else:
            # 如果不是分段加载，初始化表格并填充数据
            if student_name == '全班同学':
                self._setup_class_table(data, include_probability=True, time_sort=False)
            elif student_name == '全班同学_时间排序':
                self._setup_class_table(data, include_probability=False, time_sort=True)
            else:
                # 个人历史记录模式
                self._setup_individual_table(data)
    
    def _on_load_error(self, error_message):
        """数据加载出错回调"""
        self._hide_loading_state()
        
        # 重置加载状态
        self._is_loading_segments = False
        self._has_more_data = False
        self._current_segment = 0
        self._total_segments = 0
        
        # 显示错误提示
        InfoBar.error(
            title="加载失败",
            content=error_message,
            parent=self,
            duration=3000
        )
        
        # 清空表格
        self.table.setRowCount(0)
        self.table.setColumnCount(0)
    
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
        # 设置列宽为拉伸模式，自动铺满表格
        self.loading_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        # 设置表头字体和居中
        header_font = QFont(load_custom_font(), 12, QFont.Bold)
        self.loading_table.horizontalHeader().setFont(header_font)
        self.loading_table.horizontalHeader().setDefaultAlignment(Qt.AlignCenter)
        
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



    def _setup_table_by_mode(self, student_name: str, data: list, is_segment: bool = False):
        """根据模式设置表格"""
        if student_name == '全班同学':
            self._setup_class_table(data, include_probability=True, is_segment=is_segment)
        elif student_name == '全班同学_时间排序':
            self._setup_class_table(data, include_probability=False, time_sort=True, is_segment=is_segment)
        else:
            self._setup_individual_table(data, is_segment=is_segment)
    
    def _setup_class_table_headers(self, include_probability: bool = True, time_sort: bool = False):
        """设置班级表格表头"""
        if time_sort:
            headers = ['时间', '学号', '姓名', '性别', '所处小组']
            self._configure_table(0, 5)
        elif include_probability and self.get_random_method_setting() in [2, 3]:
            probability_method = self.get_probability_weight_method_setting()
            headers = ['学号', '姓名', '性别', '所处小组', '总抽取次数', 
                      '下次抽取概率' if probability_method == 1 else '下次抽取权重']
            self._configure_table(0, 6)
        else:
            headers = ['学号', '姓名', '性别', '所处小组', '总抽取次数']
            self._configure_table(0, 5)
            
        self.table.setHorizontalHeaderLabels(headers)
    
    def _setup_individual_table_headers(self):
        """设置个人表格表头"""
        self._configure_table(0, 5)
        self.table.setHorizontalHeaderLabels(['时间', '抽取方式', '抽取时选择的人数', '抽取时选择的小组', '抽取时选择的性别'])

    def _setup_class_table(self, data: list, include_probability: bool = True, time_sort: bool = False, is_segment: bool = False):
        """设置班级表格"""
        if not data:
            data = []
        
        # 如果是分段加载，只更新表头一次
        if not is_segment:
            if time_sort:
                headers = ['时间', '学号', '姓名', '性别', '所处小组']
                self._configure_table(0, 5)  # 初始设置为0行，后面会根据数据添加
            elif include_probability and self.get_random_method_setting() in [2, 3]:
                probability_method = self.get_probability_weight_method_setting()
                headers = ['学号', '姓名', '性别', '所处小组', '总抽取次数', 
                          '下次抽取概率' if probability_method == 1 else '下次抽取权重']
                self._configure_table(0, 6)  # 初始设置为0行，后面会根据数据添加
            else:
                headers = ['学号', '姓名', '性别', '所处小组', '总抽取次数']
                self._configure_table(0, 5)  # 初始设置为0行，后面会根据数据添加
                
            self.table.setHorizontalHeaderLabels(headers)
        
        # 填充数据
        self._fill_table_data(data)
        
        # 只有在非分段加载或者数据加载完成后才进行排序
        if time_sort and not self._is_loading_segments:
            self.table.sortByColumn(0, Qt.SortOrder.DescendingOrder)

    def _setup_individual_table(self, data: list, is_segment: bool = False):
        """设置个人表格"""
        if not data:
            data = []

        # 如果是分段加载，只更新表头一次
        if not is_segment:
            self._configure_table(0, 5)  # 初始设置为0行，后面会根据数据添加
            self.table.setHorizontalHeaderLabels(['时间', '抽取方式', '抽取时选择的人数', '抽取时选择的小组', '抽取时选择的性别'])
        
        # 填充数据
        self._fill_table_data(data)
        
        # 只有在非分段加载或者数据加载完成后才进行排序
        if not self._is_loading_segments:
            self.table.sortByColumn(0, Qt.SortOrder.DescendingOrder)

    def _configure_table(self, row_count: int, column_count: int):
        """配置表格基本属性"""
        # 如果是分段加载模式，不重置行数
        if not self._is_loading_segments:
            self.table.setRowCount(row_count)
        self.table.setColumnCount(column_count)
        
        # 保存当前排序状态
        sort_enabled = self.table.isSortingEnabled()
        sort_column = -1
        sort_order = Qt.SortOrder.AscendingOrder
        
        if sort_enabled:
            sort_column = self.table.horizontalHeader().sortIndicatorSection()
            sort_order = self.table.horizontalHeader().sortIndicatorOrder()
        
        # 临时禁用排序以配置表格
        self.table.setSortingEnabled(False)
        self.table.verticalHeader().hide()
        # 设置列宽为拉伸模式，自动铺满表格
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        # 恢复排序状态
        if sort_enabled:
            self.table.setSortingEnabled(True)
            if sort_column >= 0:
                self.table.sortByColumn(sort_column, sort_order)

    def _fill_table_data(self, data: list):
        """填充表格数据"""
        if not data:
            return
            
        # 保存当前排序状态
        sort_enabled = self.table.isSortingEnabled()
        sort_column = -1
        sort_order = Qt.SortOrder.AscendingOrder
        
        if sort_enabled:
            sort_column = self.table.horizontalHeader().sortIndicatorSection()
            sort_order = self.table.horizontalHeader().sortIndicatorOrder()
            # 临时禁用排序以填充数据
            self.table.setSortingEnabled(False)
            
        # 如果是分段加载模式，只添加新数据，不重新设置整个表格
        if self._is_loading_segments:
            # 获取当前表格行数
            current_row_count = self.table.rowCount()
            # 添加新行
            self.table.setRowCount(current_row_count + len(data))
            
            # 填充新数据
            for i, item in enumerate(data):
                row = current_row_count + i
                
                if isinstance(item, dict):
                    # 班级历史记录模式
                    if '时间' in item:
                        # 时间排序模式
                        time_item = QTableWidgetItem(item['时间'])
                        time_item.setFont(QFont(load_custom_font(), 12))
                        time_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                        self.table.setItem(row, 0, time_item)
                        
                        id_item = QTableWidgetItem(item['学号'])
                        id_item.setFont(QFont(load_custom_font(), 12))
                        id_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                        self.table.setItem(row, 1, id_item)
                        
                        name_item = QTableWidgetItem(item['姓名'])
                        name_item.setFont(QFont(load_custom_font(), 12))
                        name_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                        self.table.setItem(row, 2, name_item)
                        
                        gender_item = QTableWidgetItem(item['性别'])
                        gender_item.setFont(QFont(load_custom_font(), 12))
                        gender_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                        self.table.setItem(row, 3, gender_item)
                        
                        group_item = QTableWidgetItem(item['所处小组'])
                        group_item.setFont(QFont(load_custom_font(), 12))
                        group_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                        self.table.setItem(row, 4, group_item)
                    else:
                        # 普通模式
                        col = 0
                        
                        id_item = QTableWidgetItem(item['学号'])
                        id_item.setFont(QFont(load_custom_font(), 12))
                        id_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                        self.table.setItem(row, col, id_item)
                        col += 1
                        
                        name_item = QTableWidgetItem(item['姓名'])
                        name_item.setFont(QFont(load_custom_font(), 12))
                        name_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                        self.table.setItem(row, col, name_item)
                        col += 1
                        
                        gender_item = QTableWidgetItem(item['性别'])
                        gender_item.setFont(QFont(load_custom_font(), 12))
                        gender_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                        self.table.setItem(row, col, gender_item)
                        col += 1
                        
                        group_item = QTableWidgetItem(item['所处小组'])
                        group_item.setFont(QFont(load_custom_font(), 12))
                        group_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                        self.table.setItem(row, col, group_item)
                        col += 1
                        
                        count_item = QTableWidgetItem(str(item['总抽取次数']))
                        count_item.setFont(QFont(load_custom_font(), 12))
                        count_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                        self.table.setItem(row, col, count_item)
                        
                        # 添加概率或权重列
                        if '下次抽取概率' in item:
                            col += 1
                            probability_value = item['下次抽取概率']
                            if isinstance(probability_value, (int, float)):
                                probability_item = QTableWidgetItem(f"{probability_value:.2%}")
                            else:
                                probability_item = QTableWidgetItem(str(probability_value))
                            # 设置字体和居中
                            probability_item.setFont(QFont(load_custom_font(), 12))
                            probability_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                            self.table.setItem(row, col, probability_item)
                        elif '下次抽取权重' in item:
                            col += 1
                            weight_value = item['下次抽取权重']
                            if isinstance(weight_value, (int, float)):
                                weight_item = QTableWidgetItem(f"{weight_value:.2f}")
                            else:
                                weight_item = QTableWidgetItem(str(weight_value))
                            # 设置字体和居中
                            weight_item.setFont(QFont(load_custom_font(), 12))
                            weight_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                            self.table.setItem(row, col, weight_item)
                else:
                    # 个人历史记录模式
                    time_item = QTableWidgetItem(item[0])  # 时间
                    time_item.setFont(QFont(load_custom_font(), 12))
                    time_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                    self.table.setItem(row, 0, time_item)
                    
                    method_item = QTableWidgetItem(item[1])  # 抽取方式
                    method_item.setFont(QFont(load_custom_font(), 12))
                    method_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                    self.table.setItem(row, 1, method_item)
                    
                    count_item = QTableWidgetItem(str(item[2]))  # 抽取时选择的人数
                    count_item.setFont(QFont(load_custom_font(), 12))
                    count_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                    self.table.setItem(row, 2, count_item)
                    
                    group_item = QTableWidgetItem(str(item[3]))  # 抽取时选择的小组
                    group_item.setFont(QFont(load_custom_font(), 12))
                    group_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                    self.table.setItem(row, 3, group_item)
                    
                    gender_item = QTableWidgetItem(str(item[4]))  # 抽取时选择的性别
                    gender_item.setFont(QFont(load_custom_font(), 12))
                    gender_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                    self.table.setItem(row, 4, gender_item)
        else:
            # 非分段加载模式，填充所有数据
            self.table.setRowCount(len(data))
            
            for i, item in enumerate(data):
                if isinstance(item, dict):
                    # 班级历史记录模式
                    if '时间' in item:
                        # 时间排序模式
                        time_item = QTableWidgetItem(item['时间'])
                        time_item.setFont(QFont(load_custom_font(), 12))
                        time_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                        self.table.setItem(i, 0, time_item)
                        
                        id_item = QTableWidgetItem(item['学号'])
                        id_item.setFont(QFont(load_custom_font(), 12))
                        id_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                        self.table.setItem(i, 1, id_item)
                        
                        name_item = QTableWidgetItem(item['姓名'])
                        name_item.setFont(QFont(load_custom_font(), 12))
                        name_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                        self.table.setItem(i, 2, name_item)
                        
                        gender_item = QTableWidgetItem(item['性别'])
                        gender_item.setFont(QFont(load_custom_font(), 12))
                        gender_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                        self.table.setItem(i, 3, gender_item)
                        
                        group_item = QTableWidgetItem(item['所处小组'])
                        group_item.setFont(QFont(load_custom_font(), 12))
                        group_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                        self.table.setItem(i, 4, group_item)
                    else:
                        # 普通模式
                        col = 0
                        
                        id_item = QTableWidgetItem(item['学号'])
                        id_item.setFont(QFont(load_custom_font(), 12))
                        id_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                        self.table.setItem(i, col, id_item)
                        col += 1
                        
                        name_item = QTableWidgetItem(item['姓名'])
                        name_item.setFont(QFont(load_custom_font(), 12))
                        name_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                        self.table.setItem(i, col, name_item)
                        col += 1
                        
                        gender_item = QTableWidgetItem(item['性别'])
                        gender_item.setFont(QFont(load_custom_font(), 12))
                        gender_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                        self.table.setItem(i, col, gender_item)
                        col += 1
                        
                        group_item = QTableWidgetItem(item['所处小组'])
                        group_item.setFont(QFont(load_custom_font(), 12))
                        group_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                        self.table.setItem(i, col, group_item)
                        col += 1
                        
                        count_item = QTableWidgetItem(str(item['总抽取次数']))
                        count_item.setFont(QFont(load_custom_font(), 12))
                        count_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                        self.table.setItem(i, col, count_item)
                        
                        # 添加概率或权重列
                        if '下次抽取概率' in item:
                            col += 1
                            probability_value = item['下次抽取概率']
                            if isinstance(probability_value, (int, float)):
                                probability_item = QTableWidgetItem(f"{probability_value:.2%}")
                            else:
                                probability_item = QTableWidgetItem(str(probability_value))
                            # 设置字体和居中
                            probability_item.setFont(QFont(load_custom_font(), 12))
                            probability_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                            self.table.setItem(i, col, probability_item)
                        elif '下次抽取权重' in item:
                            col += 1
                            weight_value = item['下次抽取权重']
                            if isinstance(weight_value, (int, float)):
                                weight_item = QTableWidgetItem(f"{weight_value:.2f}")
                            else:
                                weight_item = QTableWidgetItem(str(weight_value))
                            # 设置字体和居中
                            weight_item.setFont(QFont(load_custom_font(), 12))
                            weight_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                            self.table.setItem(i, col, weight_item)
                else:
                    # 个人历史记录模式
                    time_item = QTableWidgetItem(item[0])  # 时间
                    time_item.setFont(QFont(load_custom_font(), 12))
                    time_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                    self.table.setItem(i, 0, time_item)
                    
                    method_item = QTableWidgetItem(item[1])  # 抽取方式
                    method_item.setFont(QFont(load_custom_font(), 12))
                    method_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                    self.table.setItem(i, 1, method_item)
                    
                    count_item = QTableWidgetItem(str(item[2]))  # 抽取时选择的人数
                    count_item.setFont(QFont(load_custom_font(), 12))
                    count_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                    self.table.setItem(i, 2, count_item)
                    
                    group_item = QTableWidgetItem(str(item[3]))  # 抽取时选择的小组
                    group_item.setFont(QFont(load_custom_font(), 12))
                    group_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                    self.table.setItem(i, 3, group_item)
                    
                    gender_item = QTableWidgetItem(str(item[4]))  # 抽取时选择的性别
                    gender_item.setFont(QFont(load_custom_font(), 12))
                    gender_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                    self.table.setItem(i, 4, gender_item)
        
        # 恢复排序状态
        if sort_enabled:
            self.table.setSortingEnabled(True)
            if sort_column >= 0:
                self.table.sortByColumn(sort_column, sort_order)
        
        self._setup_layout()

    def _setup_layout(self):
        """设置布局"""
        self.inner_layout_personal.addWidget(self.table)
        self.scroll_area_personal.setWidget(self.inner_frame_personal)
        
        # 确保排序功能已启用
        if not self.table.isSortingEnabled():
            self.table.setSortingEnabled(True)
        
        if not self.layout():
            main_layout = QVBoxLayout(self)
            main_layout.addWidget(self.scroll_area_personal)
        else:
            self.layout().addWidget(self.scroll_area_personal)

    def get_random_method_setting(self) -> int:
        """获取随机抽取方法的设置"""
        return self._get_setting_value('pumping_people', 'draw_pumping', 1)

    def get_probability_weight_method_setting(self) -> int:
        """获取概率权重方法设置"""
        return self._get_setting_value('history', 'probability_weight', 0)

    def _get_setting_value(self, section: str, key: str, default: int) -> int:
        """通用设置读取方法"""
        settings_file = path_manager.get_settings_path()
        try:
            with open_file(settings_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                return settings[section].get(key, default)
        except Exception as e:
            logger.error(f"加载设置时出错: {e}, 使用默认设置")
            return default

    def _refresh_table(self):
        """刷新表格"""
        # 检查是否有正在运行的线程
        if hasattr(self, '_data_loader') and self._data_loader and self._data_loader.isRunning():
            self._data_loader.stop()
        
        # 重置所有状态
        self._segmented_data = []
        self._current_segment = 0
        self._total_segments = 0
        self._is_loading_segments = False
        self._has_more_data = True
        
        # 清空表格并重置排序状态
        self.table.setSortingEnabled(False)
        self.table.setRowCount(0)
        self.table.horizontalHeader().setSortIndicator(-1, Qt.SortOrder.AscendingOrder)
        
        # 重新加载表格数据
        self.load_data()

    def __initWidget(self):
        self.__connectSignalToSlot()

    def __connectSignalToSlot(self):
        cfg.themeChanged.connect(setTheme)
