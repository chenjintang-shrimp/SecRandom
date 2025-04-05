from qfluentwidgets import *
from qfluentwidgets import FluentIcon as FIF 
import os
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QFrame, QScrollArea, QVBoxLayout, QWidget, QScroller, QTableWidgetItem, QHeaderView
from loguru import logger

from ..common.config import cfg, AUTHOR, VERSION, YEAR
from ..common.config import load_custom_font

from ..common.history_settings import history_SettinsCard


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

        # 创建标签并设置自定义字体
        self.settingLabel = SubtitleLabel("历史记录")
        self.settingLabel.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.settingLabel.setWordWrap(True)
        self.settingLabel.setFont(QFont(load_custom_font(), 22))  # 设置自定义字体

        # 历史记录设置卡片组
        self.history_setting_card = history_SettinsCard()
        self.inner_layout_personal.addWidget(self.history_setting_card)
        # 检测选择的班级是否改变，如果改变则刷新表格
        self.history_setting_card.class_comboBox.currentIndexChanged.connect(self._refresh_table)
        # 检测是否点击清除历史记录按钮，如果点击则刷新表格
        self.history_setting_card.clear_history_Button.clicked.connect(self._refresh_table)

        # 创建表格
        self.table = TableWidget(self.inner_frame_personal) # 创建表格
        self.table.setBorderVisible(True) # 边框
        self.table.setBorderRadius(8) # 圆角
        self.table.setWordWrap(False) # 不换行
        self.table.setColumnCount(7) # 列数
        self.table.setEditTriggers(TableWidget.NoEditTriggers) # 静止编辑
        self.table.scrollDelagate.verticalSmoothScroll.setSmoothMode(SmoothMode.NO_SMOOTH) # 静止平滑滚动
        self.table.setSortingEnabled(True) # 启用排序

        self.show_table()

    def show_table(self):   
        # 根据班级名称获取学生名单数据
        data = self.__getClassStudents()

        class_name = self.history_setting_card.class_comboBox.currentText()

        if data:
            InfoBar.success(
                title="读取历史记录文件成功",
                content=f"读取历史记录文件成功,班级:{class_name}",
                duration=5000,
                orient=Qt.Horizontal,
                parent=self,
                isClosable=True,
            )
        
        # 设置表格行数为实际学生数量
        self.table.setRowCount(len(data))

        self.table.setSortingEnabled(False) # 禁止排序
        
        # 填充表格数据
        for i, row in enumerate(data):
            for j in range(7):
                self.table.setItem(i, j, QTableWidgetItem(row[j]))
                self.table.item(i, j).setTextAlignment(Qt.AlignmentFlag.AlignCenter) # 居中
                self.table.item(i, j).setFont(QFont(load_custom_font(), 14)) # 设置字体
                
        # 设置表头
        self.table.setHorizontalHeaderLabels(['学号', '姓名', '所处小组', '抽单人被点次数', '抽多人被点次数', '抽小组被点次数', '总计被点次数'])
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
            main_layout.addWidget(self.settingLabel)
            main_layout.addWidget(self.scroll_area_personal)
        else:
            # 如果已有布局，只需更新内容
            self.layout().addWidget(self.settingLabel)
            self.layout().addWidget(self.scroll_area_personal)

        self.__initWidget()

    def __getClassStudents(self):
        """根据班级名称获取历史记录数据"""
        # 获取班级名称
        class_name = self.history_setting_card.class_comboBox.currentText()
        if class_name:
            # 读取配置文件
            student_file = f'app/resource/students/{class_name}.ini'
            try:
                with open(student_file, 'r', encoding='utf-8') as f:
                    students = [line.strip() for line in f if line.strip()]
                
                # 读取所有小组文件并建立学生-小组映射
                group_dict = {}
                group_files = [f for f in os.listdir('app/resource/group') 
                              if f.startswith(class_name + '_') and f.endswith('.ini') and not f.endswith('_group.ini')]
                
                for group_file in group_files:
                    group_name = group_file.split('_')[-1].split('.')[0]
                    with open(f'app/resource/group/{group_file}', 'r', encoding='utf-8') as f:
                        group_students = [line.strip() for line in f if line.strip()]
                        for student in group_students:
                            group_dict[student] = group_name
                
                # 为每个学生查找对应小组
                students_group = [group_dict.get(name, "") for name in students]
                    
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
                for i, student in enumerate(students):
                    student_name = student if not (student.startswith('【') and student.endswith('】')) else student[1:-1]
                    # 初始化抽单人、抽多人、抽小组被点次数和总计被点次数
                    single_count = 0
                    multi_count = 0
                    group_count = 0
                    total_count = 0
                    # 更新历史数据并统计被点次数
                    if 'single' in history_data and student_name in history_data['single']:
                        single_count = history_data['single'][student_name]['total_number_of_times']
                    if 'multi' in history_data and student_name in history_data['multi']:
                        multi_count = history_data['multi'][student_name]['total_number_of_times']
                    if 'group' in history_data and student_name in history_data['group']:
                        group_count = history_data['group'][student_name]['total_number_of_times']
                    # 确保相加的都是整数类型
                    single_count = int(single_count) if isinstance(single_count, (int, str)) else 0
                    multi_count = int(multi_count) if isinstance(multi_count, (int, str)) else 0
                    group_count = int(group_count) if isinstance(group_count, (int, str)) else 0
                    total_count = single_count + multi_count + group_count
                    student_data.append([str(i+1).zfill(2), student_name, students_group[i], str(single_count), str(multi_count), str(group_count), str(total_count)])
                return student_data
                
            except Exception as e:
                logger.error(f"读取学生名单文件失败: {e}")
                InfoBar.error(
                    title="读取学生名单文件失败",
                    content=f"错误信息: {str(e)}",
                    duration=5000,
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

    def __showRestartTooltip(self):
        InfoBar.success(
            self.tr('更新成功'),
            self.tr('设置在重启后生效'),
            duration=1500,
            parent=self
        )

    def __connectSignalToSlot(self):
        cfg.appRestartSig.connect(self.__showRestartTooltip)
        cfg.themeChanged.connect(setTheme)
