from qfluentwidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import os
from loguru import logger

from app.common.config import cfg, AUTHOR, VERSION, YEAR
from app.common.config import load_custom_font

from app.common.Changeable_history_settings import history_SettinsCard

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
            )
        
        if student_name == '全班同学':
            # 设置表格行数为实际学生数量
            self.table.setRowCount(len(data))
            self.table.setSortingEnabled(False)
            self.table.setColumnCount(7)
            
            # 填充表格数据
            for i, row in enumerate(data):
                for j in range(7):
                    self.table.setItem(i, j, QTableWidgetItem(row[j]))
                    self.table.item(i, j).setTextAlignment(Qt.AlignmentFlag.AlignCenter) # 居中
                    self.table.item(i, j).setFont(QFont(load_custom_font(), 14)) # 设置字体
                    
            # 设置表头
            self.table.setHorizontalHeaderLabels(['学号', '姓名', '性别', '所处小组', '抽多人被点次数', '抽小组被点次数', '总计被点次数'])
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
            self.table.setColumnCount(2)
            
            # 填充表格数据
            for i, row in enumerate(data):
                for j in range(2):
                    self.table.setItem(i, j, QTableWidgetItem(row[j]))
                    self.table.item(i, j).setTextAlignment(Qt.AlignmentFlag.AlignCenter) # 居中
                    self.table.item(i, j).setFont(QFont(load_custom_font(), 14)) # 设置字体
                    
            # 设置表头
            self.table.setHorizontalHeaderLabels(['时间', '抽取方式'])
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
                        for student_name, student_info in data.items():
                            if isinstance(student_info, dict) and 'id' in student_info:
                                id = student_info.get('id', '')
                                name = student_name.replace('【', '').replace('】', '')
                                gender = student_info.get('gender', '')
                                group = student_info.get('group', '')
                                cleaned_data.append((id, name, gender, group))
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
                        'multi': 0,
                        'group': 0,
                        'total': 0
                    }

                    for i, student in enumerate(students):
                        student_name = student if not (student.startswith('【') and student.endswith('】')) else student[1:-1]
                        max_digits['id'] = max(max_digits['id'], len(str(cleaned_data[i][0])))
                        if 'multi' in history_data and student_name in history_data['multi']:
                            count = int(history_data['multi'][student_name]['total_number_of_times'])
                            max_digits['multi'] = max(max_digits['multi'], len(str(count)))
                        if 'group' in history_data and student_name in history_data['group']:
                            count = int(history_data['group'][student_name]['total_number_of_times'])
                            max_digits['group'] = max(max_digits['group'], len(str(count)))

                    # 计算总计列的最大位数
                    max_digits['total'] = max(max_digits['multi'], max_digits['group'])

                    # 生成最终数据
                    for i, student in enumerate(students):
                        student_name = student if not (student.startswith('【') and student.endswith('】')) else student[1:-1]
                        multi_count = int(history_data['multi'].get(student_name, {}).get('total_number_of_times', 0)) if 'multi' in history_data else 0
                        group_count = int(history_data['group'].get(student_name, {}).get('total_number_of_times', 0)) if 'group' in history_data else 0
                        total_count = multi_count + group_count

                        student_data.append([
                            str(cleaned_data[i][0]).zfill(max_digits['id']),
                            student_name,
                            cleaned_data[i][2],
                            students_group[i],
                            str(multi_count).zfill(max_digits['multi']),
                            str(group_count).zfill(max_digits['group']),
                            str(total_count).zfill(max_digits['total'])
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
                    if _student_name in history_data.get('multi', {}):
                        multi_history = history_data['multi'][_student_name]['time']
                        for record in multi_history:
                            time_data = record.get('draw_method', {})
                            time = next(iter(time_data.values())) if isinstance(time_data, dict) and time_data else ''
                            draw_method = next(iter(time_data.keys())) if isinstance(time_data, dict) and time_data else ''
                            if draw_method == 'random':
                                draw_method_text = '重复抽取'
                            elif draw_method == 'until_reboot':
                                draw_method_text = '不重复抽取(直到软件重启)'
                            elif draw_method == 'until_all':
                                draw_method_text = '不重复抽取(直到抽完全部人)'
                            else:
                                draw_method_text = draw_method
                            student_data.append([time, draw_method_text])
                    if _student_name in history_data.get('group', {}):
                        group_history = history_data['group'][_student_name]['time']
                        for record in group_history:
                            time_data = record.get('draw_method', {})
                            time = next(iter(time_data.values())) if isinstance(time_data, dict) and time_data else ''
                            draw_method = next(iter(time_data.keys())) if isinstance(time_data, dict) and time_data else ''
                            if draw_method == 'random':
                                draw_method_text = '重复抽取'
                            elif draw_method == 'until_reboot':
                                draw_method_text = '不重复抽取(直到软件重启)'
                            elif draw_method == 'until_all':
                                draw_method_text = '不重复抽取(直到抽完全部人)'
                            else:
                                draw_method_text = draw_method
                            student_data.append([time, draw_method_text])
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
