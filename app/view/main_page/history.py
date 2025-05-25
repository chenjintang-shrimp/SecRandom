from qfluentwidgets import *
from qfluentwidgets import FluentIcon as FIF 
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import os
from datetime import datetime
import math
from loguru import logger

from app.common.config import cfg, AUTHOR, VERSION, YEAR
from app.common.config import load_custom_font

from app.common.history_settings import history_SettinsCard
from app.view.main_page.pumping_people import pumping_people

class history(QFrame):
    def __init__(self, parent: QFrame = None):
        super().__init__(parent=parent)

        # 创建一个 QScrollArea
        self.scroll_area_personal = QScrollArea(self)
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
            /* 垂直滚动条整体 */
            QScrollBar:vertical {
                background-color: #E5DDF8;   /* 背景透明 */
                width: 8px;                    /* 宽度 */
                margin: 0px;                   /* 外边距 */
            }
            /* 垂直滚动条的滑块 */
            QScrollBar::handle:vertical {
                background-color: rgba(0, 0, 0, 0.3);    /* 半透明滑块 */
                border-radius: 4px;                      /* 圆角 */
                min-height: 20px;                        /* 最小高度 */
            }
            /* 鼠标悬停在滑块上 */
            QScrollBar::handle:vertical:hover {
                background-color: rgba(0, 0, 0, 0.5);
            }
            /* 滚动条的上下按钮和顶部、底部区域 */
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical,
            QScrollBar::up-arrow:vertical,
            QScrollBar::down-arrow:vertical {
                height: 0px;
            }
        
            /* 水平滚动条整体 */
            QScrollBar:horizontal {
                background-color: #E5DDF8;   /* 背景透明 */
                height: 8px;
                margin: 0px;
            }
            /* 水平滚动条的滑块 */
            QScrollBar::handle:horizontal {
                background-color: rgba(0, 0, 0, 0.3);
                border-radius: 4px;
                min-width: 20px;
            }
            /* 鼠标悬停在滑块上 */
            QScrollBar::handle:horizontal:hover {
                background-color: rgba(0, 0, 0, 0.5);
            }
            /* 滚动条的左右按钮和左侧、右侧区域 */
            QScrollBar::add-line:horizontal,
            QScrollBar::sub-line:horizontal,
            QScrollBar::left-arrow:horizontal,
            QScrollBar::right-arrow:horizontal {
                width: 0px;
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

        # 创建表格
        self.table = TableWidget(self.inner_frame_personal) # 创建表格
        self.table.setBorderVisible(True) # 边框
        self.table.setBorderRadius(8) # 圆角
        self.table.setWordWrap(False) # 不换行
        self.table.setEditTriggers(TableWidget.NoEditTriggers) # 静止编辑
        self.table.scrollDelagate.verticalSmoothScroll.setSmoothMode(SmoothMode.NO_SMOOTH) # 静止平滑滚动
        self.table.setSortingEnabled(True) # 启用排序

        self.show_table()

    def show_table(self):   
        # 根据班级名称获取学生名单数据
        data = self.__getClassStudents()

        class_name = self.history_setting_card.class_comboBox.currentText()
        student_name = self.history_setting_card.student_comboBox.currentText()

        if data:
            InfoBar.success(
                title="读取历史记录文件成功",
                content=f"读取历史记录文件成功,班级:{class_name},学生:{student_name}",
                duration=3000,
                orient=Qt.Horizontal,
                parent=self,
                isClosable=True,
            )
        
        if student_name == '全班同学':
            # 设置表格行数为实际学生数量
            self.table.setRowCount(len(data))
            self.table.setSortingEnabled(False)
            use_system_random = self.get_random_method_setting()
            if use_system_random in [2, 3]:
                self.table.setColumnCount(6)
                # 填充表格数据
                for i, row in enumerate(data):
                    for j in range(6):
                        self.table.setItem(i, j, QTableWidgetItem(row[j]))
                        self.table.item(i, j).setTextAlignment(Qt.AlignmentFlag.AlignCenter) # 居中
                        self.table.item(i, j).setFont(QFont(load_custom_font(), 14)) # 设置字体
                # 设置表头
                self.table.setHorizontalHeaderLabels(['学号', '姓名', '性别', '所处小组', '总抽取次数', '下次抽取概率'])
            else:
                self.table.setColumnCount(5)
                # 填充表格数据
                for i, row in enumerate(data):
                    for j in range(5):
                        self.table.setItem(i, j, QTableWidgetItem(row[j]))
                        self.table.item(i, j).setTextAlignment(Qt.AlignmentFlag.AlignCenter) # 居中
                        self.table.item(i, j).setFont(QFont(load_custom_font(), 14)) # 设置字体
                # 设置表头
                self.table.setHorizontalHeaderLabels(['学号', '姓名', '性别', '所处小组', '总抽取次数'])

            self.table.verticalHeader().hide() # 隐藏垂直表头
            self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch) # 自适应
            
            # 添加到布局
            self.inner_layout_personal.addWidget(self.table)

            # 将内部的 QFrame 设置为 QScrollArea 的内容
            self.scroll_area_personal.setWidget(self.inner_frame_personal)

            self.table.setSortingEnabled(True) # 启用排序

            # 设置主布局
            if not self.layout():
                main_layout = QVBoxLayout(self)
                main_layout.addWidget(self.scroll_area_personal)
            else:
                # 如果已有布局，只需更新内容
                self.layout().addWidget(self.scroll_area_personal)
        else:
            self.table.setRowCount(len(data))
            self.table.setSortingEnabled(False) # 禁止排序
            self.table.setColumnCount(5)
            
            # 填充表格数据
            for i, row in enumerate(data):
                for j in range(5):
                    self.table.setItem(i, j, QTableWidgetItem(row[j]))
                    self.table.item(i, j).setTextAlignment(Qt.AlignmentFlag.AlignCenter) # 居中
                    self.table.item(i, j).setFont(QFont(load_custom_font(), 14)) # 设置字体
                    
            # 设置表头
            self.table.setHorizontalHeaderLabels(['时间', '抽取方式', '抽取时选择的人数', '抽取时选择的小组', '抽取时选择的性别'])
            self.table.verticalHeader().hide() # 隐藏垂直表头
            self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch) # 自适应
            self.table.setSortingEnabled(True) # 启用排序
            self.table.sortByColumn(0, Qt.SortOrder.DescendingOrder)
            
            # 添加到布局
            self.inner_layout_personal.addWidget(self.table)

            # 将内部的 QFrame 设置为 QScrollArea 的内容
            self.scroll_area_personal.setWidget(self.inner_frame_personal)

            # 设置主布局
            if not self.layout():
                main_layout = QVBoxLayout(self)
                main_layout.addWidget(self.scroll_area_personal)
            else:
                # 如果已有布局，只需更新内容
                self.layout().addWidget(self.scroll_area_personal)

        self.__initWidget()

    def get_random_method_setting(self):
        """获取随机抽取方法的设置"""
        try:
            with open('app/Settings/Settings.json', 'r', encoding='utf-8') as f:
                settings = json.load(f)
                random_method = settings['pumping_people']['draw_pumping']
                return random_method
        except Exception as e:
            logger.error(f"加载随机抽取方法设置时出错: {e}, 使用默认设置")
            return 0

    def __getClassStudents(self):
        """根据班级/学生名称获取历史记录数据"""
        # 获取班级名称
        class_name = self.history_setting_card.class_comboBox.currentText()
        _student_name = self.history_setting_card.student_comboBox.currentText()
        if _student_name == '全班同学':
            if class_name:
                # 读取配置文件
                student_file = f'app/resource/list/{class_name}.json'

                try:
                    with open(student_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        cleaned_data = []
                        __cleaned_data = []
                        for student_name, student_info in data.items():
                            if isinstance(student_info, dict) and 'id' in student_info:
                                id = student_info.get('id', '')
                                name = student_name.replace('【', '').replace('】', '')
                                gender = student_info.get('gender', '')
                                group = student_info.get('group', '')
                                cleaned_data.append((id, name, gender, group))
                                __cleaned_data.append((id, name))
                        students = [item[1] for item in cleaned_data]
                    
                    # 直接从JSON数据获取小组信息
                    students_group = [item[3] for item in cleaned_data]
                        
                    # 初始化历史数据字典
                    history_data = {}
                    # 读取历史记录文件
                    history_file = f'app/resource/history/{class_name}.json'

                    if os.path.exists(history_file):
                        try:
                            with open(history_file, 'r', encoding='utf-8') as f:
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
                            max_digits['pumping_people'] = max(max_digits['pumping_people'], len(str(count)))

                    available_students = __cleaned_data

                    # 获取当前抽取模式
                    try:
                        with open('app/Settings/Settings.json', 'r', encoding='utf-8') as f:
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
                        if os.path.exists(draw_record_file):
                            # 读取已抽取记录
                            drawn_students = []
                            with open(draw_record_file, 'r', encoding='utf-8') as f:
                                try:
                                    drawn_students = json.load(f)
                                except json.JSONDecodeError:
                                    drawn_students = []
                        else:
                            drawn_students = []
                    else:
                        drawn_students = []

                    # 生成最终数据
                    for i, student in enumerate(students):
                        # 计算所有学生的综合权重
                        total_weight = 0
                        available_students_weights = {}

                        for student_id, student_name in available_students:
                            # 获取学生历史记录
                            student_history = history_data.get("pumping_people", {}).get(student_name, {
                                "total_number_of_times": 0,
                                "last_drawn_time": None,
                                "rounds_missed": 0,
                                "time": []
                            })

                            def calculate_comprehensive_weight(student_history, student_info, history_data):
                                # 基础参数配置
                                COLD_START_ROUNDS = 10       # 冷启动轮次
                                BASE_WEIGHT = 1.0            # 基础权重

                                # 计算各权重因子
                                # 因子1: 抽取频率惩罚（被抽中次数越多权重越低）
                                frequency_factor = 1.0 / math.sqrt(student_history["total_number_of_times"] * 2 + 1)

                                # 因子2: 小组平衡（仅当有足够数据时生效）
                                group_factor = 1.0
                                if len(history_data.get("group_stats", {})) > 3:  # 至少3个小组有数据
                                    for student in cleaned_data:
                                        if student[1] == student_name:
                                            current_student_group = student[3]
                                            break
                                    else:
                                        current_student_group = ''
                                    group_history = history_data["group_stats"].get(current_student_group, 0)
                                    group_factor = 1.0 / (group_history * 0.2 + 1)  # 小组被抽1次→0.83, 2次→0.71

                                # 因子3: 性别平衡（仅当两种性别都有数据时生效）
                                gender_factor = 1.0
                                if len(history_data.get("gender_stats", {})) >= 2:
                                    for student in cleaned_data:
                                        if student[1] == student_name:
                                            current_student_gender = student[2]
                                            break
                                    else:
                                        current_student_gender = ''
                                    gender_history = history_data["gender_stats"].get(current_student_gender, 0)
                                    gender_factor = 1.0 / (gender_history * 0.2 + 1)

                                # 冷启动特殊处理
                                current_round = history_data.get("total_rounds", 0)
                                if current_round < COLD_START_ROUNDS:
                                    frequency_factor = min(0.8, frequency_factor)  # 防止新学生权重过低

                                # 综合权重计算
                                weights = {
                                    'base': BASE_WEIGHT * 0.2,
                                    'frequency': frequency_factor * 3.0,
                                    'group': group_factor * 0.8,
                                    'gender': gender_factor * 0.8
                                }
                                
                                comprehensive_weight = sum(weights.values())
                                
                                # 5. 最终调整与限制
                                # 确保权重在合理范围内 (0.5~5.0)
                                final_weight = max(0.5, min(comprehensive_weight, 5.0))
                                
                                # # 调试输出
                                # debug_info = {
                                #     'name': student_name,
                                #     'final': round(final_weight, 2),
                                #     'factors': {k: round(v, 2) for k,v in weights.items()},
                                #     'history': {
                                #         'drawn_times': student_history["total_number_of_times"],
                                #         'missed': student_history.get("rounds_missed", 0)
                                #     }
                                # }
                                # print(debug_info)
                                
                                return final_weight

                            if self.draw_mode in ['until_reboot', 'until_all'] and student_name in drawn_students and len(drawn_students) < len(students):
                                # 如果是不重复抽取模式，且该学生已被抽中，且未全部抽完，则权重为0
                                comprehensive_weight = 0
                            else:
                                comprehensive_weight = calculate_comprehensive_weight(student_history, student_info, history_data)
                            available_students_weights[student_name] = comprehensive_weight
                            total_weight += comprehensive_weight

                        for i, student in enumerate(students):
                            student_name = student if not (student.startswith('【') and student.endswith('】')) else student[1:-1]
                            if student_name in available_students_weights:
                                probability = available_students_weights[student_name] / total_weight if total_weight > 0 else 0
                                probability = probability * 100
                                if probability < 10:
                                    probability_str = '0{:.1f}%'.format(probability)
                                else:
                                    probability_str = '{:.1f}%'.format(probability)
                            else:
                                probability_str = '00.0%'

                            pumping_people_count = int(history_data['pumping_people'].get(student_name, {}).get('total_number_of_times', 0)) if 'pumping_people' in history_data else 0

                            student_data.append([
                                str(cleaned_data[i][0]).zfill(max_digits['id']),
                                student_name,
                                cleaned_data[i][2],
                                students_group[i],
                                str(pumping_people_count).zfill(max_digits['pumping_people']),
                                probability_str
                            ])

                        return student_data

                except Exception as e:
                    logger.error(f"读取学生名单文件失败: {e}")
                    InfoBar.error(
                        title="读取学生名单文件失败",
                        content=f"错误信息: （请到日志文件查看）",
                        duration=3000,
                        orient=Qt.Horizontal,
                        parent=self,
                        isClosable=True,
                    )
                    return []
            else:
                return []
        
        else:
            if class_name:
                _student_name = _student_name if not (_student_name.startswith('【') and _student_name.endswith('】')) else _student_name[1:-1]
                try:
                    # 初始化历史数据字典
                    history_data = {}
                    # 读取历史记录文件
                    history_file = f'app/resource/history/{class_name}.json'

                    if os.path.exists(history_file):
                        try:
                            with open(history_file, 'r', encoding='utf-8') as f:
                                history_data = json.load(f)
                        except json.JSONDecodeError:
                            history_data = {}
                    
                    # 假设历史数据中每个抽取记录有时间、抽取方式和被点次数信息
                    student_data = []
                    if _student_name in history_data.get('pumping_people', {}):
                        pumping_people_history = history_data['pumping_people'][_student_name]['time']
                        for record in pumping_people_history:
                            time = record.get('draw_time', '')
                            draw_method = record.get('draw_method', '')
                            if draw_method == 'random':
                                draw_method_text = '重复抽取'
                            elif draw_method == 'until_reboot':
                                draw_method_text = '不重复抽取(直到软件重启)'
                            elif draw_method == 'until_all':
                                draw_method_text = '不重复抽取(直到抽完全部人)'
                            else:
                                draw_method_text = draw_method
                            draw_people_numbers = record.get('draw_people_numbers', '')
                            draw_group = record.get('draw_group', '')
                            draw_gender = record.get('draw_gender', '')
                            student_data.append([time, draw_method_text, f'{draw_people_numbers}', draw_group, draw_gender])
                    return student_data
                    
                except Exception as e:
                    logger.error(f"读取学生名单文件失败: {e}")
                    InfoBar.error(
                        title="读取学生名单文件失败",
                        content=f"错误信息: （请到日志文件查看）",
                        duration=3000,
                        orient=Qt.Horizontal,
                        parent=self,
                        isClosable=True,
                    )
                    return []
            else:
                return []

    def _refresh_table(self):
        """刷新表格"""
        # 清空表格
        self.table.setRowCount(0)
        # 重新加载表格数据
        self.show_table()

    def __initWidget(self):
        self.__connectSignalToSlot()

    def __connectSignalToSlot(self):
        cfg.themeChanged.connect(setTheme)
