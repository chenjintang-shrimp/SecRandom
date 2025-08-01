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
from app.common.config import get_theme_icon, load_custom_font

from app.common.history_settings import history_SettinsCard
from app.view.main_page.pumping_people import pumping_people

class history(QFrame):
    def __init__(self, parent: QFrame = None):
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

        self.show_table()

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

    def show_table(self):
        """显示历史记录表格"""
        # 显示加载状态
        self.loading_widget.show()
        self.table.hide()
        
        # 使用QTimer延迟加载数据，避免界面卡顿
        QTimer.singleShot(100, self._load_data_async)

    def _load_data_async(self):
        """异步加载数据"""
        try:
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
                    position=InfoBarPosition.TOP
                )

            # 隐藏加载状态，显示真实数据
            self.loading_widget.hide()
            self.table.show()
            self._setup_table_by_mode(student_name, data)
            self.__initWidget()
            
        except Exception as e:
            logger.error(f"加载历史记录数据失败: {e}")
            InfoBar.error(
                title="加载失败",
                content="加载历史记录数据失败，请稍后重试",
                duration=3000,
                orient=Qt.Horizontal,
                parent=self,
                isClosable=True,
                position=InfoBarPosition.TOP
            )
            # 隐藏加载状态，显示空表格
            self.loading_widget.hide()
            self.table.show()
            self._setup_table_by_mode('', [])

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
            data = [['0', '无', '无', '无', '无', '无']] if include_probability else [['无', '0', '无', '无', '无']]
        
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
            data = [[current_time, '无', '无', '无', '无']]

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
        try:
            with open('app/Settings/Settings.json', 'r', encoding='utf-8') as f:
                settings = json.load(f)
                return settings[section][key]
        except Exception as e:
            logger.error(f"加载设置时出错: {e}, 使用默认设置")
            return default

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
                        
                    # 使用SQLite数据库读取历史记录
                    from app.common.sqlite_utils import history_manager
                    
                    # 获取学生历史记录
                    student_stats = history_manager.get_student_stats(class_name)
                    
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
                        
                        # 从数据库获取学生被抽中次数
                        count_key = f'student_{student_name}'
                        if count_key in student_stats:
                            total = student_stats[count_key]
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
                    
                    # 从SQLite数据库获取已抽取学生记录
                    drawn_students = history_manager.get_drawn_students(
                        class_name=class_name,
                        group_name=group_name,
                        gender=genders,
                        draw_mode=self.draw_mode
                    )

                    # 预加载设置文件
                    try:
                        with open('app/Settings/Settings.json', 'r', encoding='utf-8') as f:
                            settings = json.load(f)
                            probability_weight = settings['history']['probability_weight']
                    except Exception as e:
                        probability_weight = 1
                        logger.error(f"加载设置时出错: {e}, 使用默认设置")

                    # 从SQLite数据库获取统计信息
                    stats = history_manager.get_student_stats(class_name)
                    
                    # 预计算有效统计
                    valid_groups = {group: count for group, count in stats.get("group_stats", {}).items() if count > 0}
                    valid_genders = {gender: count for gender, count in stats.get("gender_stats", {}).items() if count > 0}

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

                        # 🌸 小鸟游星野提醒：从数据库获取学生历史记录并确保类型安全
                        student_history = stats.get(f'student_{student_name}', {})

                        # ✨ 星穹铁道白露提示：强制转换为字典并确保包含必要字段
                        if not isinstance(student_history, dict):
                            student_history = {"total_number_of_times": int(student_history) if isinstance(student_history, (int, float)) else 0}

                        # 🌟 确保必须字段存在默认值
                        student_history.setdefault("total_number_of_times", 0)
                        student_history.setdefault("total_number_auxiliary", 0)

                        # 💫 频率因子计算
                        freq = int(student_history["total_number_of_times"])
                        frequency_factor = 1.0 / math.sqrt(max(freq, 0) * 2 + 1)

                        # 小组因子
                        group_history = valid_groups.get(current_student_group, 0)
                        group_factor = 1.0 / (group_history * 0.2 + 1) if len(valid_groups) > 3 else 1.0

                        # 性别因子
                        gender_history = valid_genders.get(current_student_gender, 0)
                        gender_factor = 1.0 / (gender_history * 0.2 + 1) if len(valid_genders) > 3 else 1.0

                        # 冷启动处理
                        current_round = stats.get("total_rounds", 0)
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

                        # 🌸 小鸟游星野提醒：为每个学生正确获取历史记录
                        student_history = stats.get(f'student_{student_name}', {})
                        
                        # ✨ 星穹铁道白露提示：确保类型安全
                        if not isinstance(student_history, dict):
                            student_history = {"total_number_of_times": int(student_history) if isinstance(student_history, (int, float)) else 0}
                        
                        # 🌟 确保必须字段存在默认值
                        student_history.setdefault("total_number_of_times", 0)
                        student_history.setdefault("total_number_auxiliary", 0)
                        
                        # 💫 安全获取抽取次数
                        pumping_count = int(student_history["total_number_of_times"])
                        pumping_count_auxiliary = int(student_history["total_number_auxiliary"])
                        total_pumping = pumping_count + pumping_count_auxiliary

                        # 🌸 小鸟游星野提醒：直接显示数字，避免前导零
                        student_data.append([
                            str(cleaned[0]).zfill(max_digits['id']),
                            student_name,
                            cleaned[2],
                            cleaned[3],
                            str(total_pumping),
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
                
                # 读取学生名单
                try:
                    with open(student_file, 'r', encoding='utf-8') as f:
                        class_data = json.load(f)
                except (FileNotFoundError, json.JSONDecodeError):
                    return []

                # 清理学生数据
                cleaned_students = {}
                for name, info in class_data.items():
                    if isinstance(info, dict) and info.get('exist', True):
                        cleaned_name = name.replace('【', '').replace('】', '')
                        cleaned_students[cleaned_name] = {
                            'id': str(info.get('id', '')),
                            'gender': info.get('gender', ''),
                            'group': info.get('group', '')
                        }

                # 🌸 小鸟游星野提醒：使用SQLite数据库获取全班时间排序记录
                from app.common.sqlite_utils import history_manager
                
                # 获取全班历史记录
                all_history = history_manager.get_student_history(class_name)
                
                # 转换为时间排序的格式
                all_records = []
                for record in all_history:
                    student_name = record['student_name']
                    if student_name in cleaned_students:
                        student_info = cleaned_students[student_name]
                        all_records.append([
                            record['draw_time'],
                            student_info['id'],
                            student_name,
                            student_info['gender'],
                            student_info['group']
                        ])
                
                # 按时间降序排序
                all_records.sort(reverse=True, key=lambda x: x[0])
                
                return all_records
            else:
                return []
        
        else:
            if class_name:
                _student_name = _student_name if not (_student_name.startswith('【') and _student_name.endswith('】')) else _student_name[1:-1]
                try:
                    # 🌸 小鸟游星野提醒：使用SQLite数据库获取单个学生的历史记录
                    from app.common.sqlite_utils import history_manager
                    
                    # 直接从数据库获取该学生的历史记录
                    student_history = history_manager.get_student_history(class_name, _student_name)
                    
                    student_data = []
                    for record in student_history:
                        # 转换抽取方式文本
                        draw_method_map = {
                            'random': '重复抽取',
                            'until_reboot': '不重复抽取(直到软件重启)',
                            'until_all': '不重复抽取(直到抽完全部人)'
                        }
                        draw_method_text = draw_method_map.get(record['draw_method'], record['draw_method'])
                        
                        student_data.append([
                            record['draw_time'],
                            draw_method_text,
                            str(record['draw_count']),
                            record['draw_group'] or '',
                            record['draw_gender'] or ''
                        ])
                    
                    return student_data
                    
                except Exception as e:
                    logger.error(f"读取学生历史记录失败: {e}")
                    InfoBar.error(
                        title="读取学生历史记录失败",
                        content=f"错误信息: {str(e)}",
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
