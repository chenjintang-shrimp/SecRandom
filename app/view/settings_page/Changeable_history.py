from qfluentwidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import os
import math
from loguru import logger

from app.common.config import cfg, AUTHOR, VERSION, YEAR
from app.common.config import get_theme_icon, load_custom_font

from app.common.Changeable_history_settings import history_SettinsCard
from app.view.main_page.pumping_people import pumping_people

class changeable_history(QFrame):
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
        # 检测是否点击清除历史记录按钮，如果点击则刷新表格
        self.history_setting_card.clear_history_Button.clicked.connect(self._refresh_table)
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

        # 如果data为空，则显示提示信息
        # 获取当前时间
        current_time = QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm:ss")

        # 获取班级名称和学生名称
        class_name = self.history_setting_card.class_comboBox.currentText()
        student_name = self.history_setting_card.student_comboBox.currentText()

        if data:
            InfoBar.success(
                title="读取历史记录文件成功",
                content=f"读取历史记录文件成功,班级:{class_name},学生:{student_name}",
                duration=6000,
                orient=Qt.Horizontal,
                parent=self,
                isClosable=True,
                position=InfoBarPosition.TOP
            )
        
        if student_name == '全班同学':
            if not data:
                data = [['0', '无', '无', '无', '无', '无']]
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
                        self.table.item(i, j).setFont(QFont(load_custom_font(), 12)) # 设置字体
                # 设置表头
                probability_weight_method = self.get_probability_weight_method_setting()
                if probability_weight_method == 1:
                    self.table.setHorizontalHeaderLabels(['学号', '姓名', '性别', '所处小组', '总抽取次数', '下次抽取概率'])
                else:
                    self.table.setHorizontalHeaderLabels(['学号', '姓名', '性别', '所处小组', '总抽取次数', '下次抽取权重'])
            else:
                self.table.setColumnCount(5)
                # 填充表格数据
                for i, row in enumerate(data):
                    for j in range(5):
                        self.table.setItem(i, j, QTableWidgetItem(row[j]))
                        self.table.item(i, j).setTextAlignment(Qt.AlignmentFlag.AlignCenter) # 居中
                        self.table.item(i, j).setFont(QFont(load_custom_font(), 12)) # 设置字体
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

        elif student_name == '全班同学_时间排序':
            if not data:
                data = [['无', '0', '无', '无', '无']]
            # 设置表格行数为实际学生数量
            self.table.setRowCount(len(data))
            self.table.setSortingEnabled(False)
            use_system_random = self.get_random_method_setting()
            self.table.setColumnCount(5)
            # 填充表格数据
            for i, row in enumerate(data):
                for j in range(5):
                    self.table.setItem(i, j, QTableWidgetItem(row[j]))
                    self.table.item(i, j).setTextAlignment(Qt.AlignmentFlag.AlignCenter) # 居中
                    self.table.item(i, j).setFont(QFont(load_custom_font(), 12)) # 设置字体
            # 设置表头
            self.table.setHorizontalHeaderLabels(['时间', '学号', '姓名', '性别', '所处小组'])

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
            if not data:
                data = [[f'{current_time}', '无', '无', '无', '无']]
            self.table.setRowCount(len(data))
            self.table.setSortingEnabled(False) # 禁止排序
            self.table.setColumnCount(5)
            
            # 填充表格数据
            for i, row in enumerate(data):
                for j in range(5):
                    self.table.setItem(i, j, QTableWidgetItem(row[j]))
                    self.table.item(i, j).setTextAlignment(Qt.AlignmentFlag.AlignCenter) # 居中
                    self.table.item(i, j).setFont(QFont(load_custom_font(), 12)) # 设置字体
                    
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

    def get_probability_weight_method_setting(self):
        """获取随机抽取方法的设置"""
        try:
            with open('app/Settings/Settings.json', 'r', encoding='utf-8') as f:
                settings = json.load(f)
                probability_weight_method = settings['history']['probability_weight']
                return probability_weight_method
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
                            count_auxiliary = int(history_data['pumping_people'][student_name]['total_number_auxiliary'])
                            total = count + count_auxiliary
                            max_digits['pumping_people'] = max(max_digits['pumping_people'], len(str(total)))

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

                    # 预加载设置文件
                    try:
                        with open('app/Settings/Settings.json', 'r', encoding='utf-8') as f:
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
                    for i, (student, cleaned) in enumerate(zip(students, cleaned_data)):
                        student_name = student[1:-1] if student.startswith('【') and student.endswith('】') else student
                        
                        # 计算概率/权重值
                        weight_value = available_students_weights.get(student_name, 0)
                        if probability_weight == 1:
                            prob = (weight_value / total_weight) * 100 if total_weight > 0 else 0
                            probability_str = f"{prob:.2f}%"
                        else:
                            probability_str = f"{weight_value:.2f}"

                        # 获取抽取次数
                        pumping_count = history_data.get('pumping_people', {}).get(student_name, {}).get('total_number_of_times', 0)
                        pumping_count_auxiliary = history_data.get('pumping_people', {}).get(student_name, {}).get('total_number_auxiliary', 0)

                        student_data.append([
                            str(cleaned[0]).zfill(max_digits['id']),
                            student_name,
                            cleaned[2],
                            cleaned[3],
                            str(pumping_count + pumping_count_auxiliary).zfill(max_digits['pumping_people']),
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
                        position=InfoBarPosition.TOP
                    )
                    return []
            else:
                return []

        elif _student_name == '全班同学_时间排序':
            if class_name:
                student_file = f'app/resource/list/{class_name}.json'
                history_file = f'app/resource/history/{class_name}.json'
                
                # 读取学生名单
                try:
                    with open(student_file, 'r', encoding='utf-8') as f:
                        class_data = json.load(f)
                except (FileNotFoundError, json.JSONDecodeError):
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
                if os.path.exists(history_file):
                    try:
                        with open(history_file, 'r', encoding='utf-8') as f:
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
                        position=InfoBarPosition.TOP
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
