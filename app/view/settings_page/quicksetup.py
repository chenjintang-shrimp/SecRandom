from qfluentwidgets import *
from qfluentwidgets import FluentIcon as FIF 
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import os
from loguru import logger

from app.common.config import cfg, AUTHOR, VERSION, YEAR
from app.common.config import load_custom_font

from app.common.list_settings import list_SettinsCard

class quicksetup(QFrame):
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

        # 名单设置卡片组
        self.list_setting_card = list_SettinsCard()
        self.inner_layout_personal.addWidget(self.list_setting_card)
        # 检测self.list_setting_card是否更新了
        self.list_setting_card.class_comboBox.currentIndexChanged.connect(self._refresh_table)

        # 创建表格
        self.table = TableWidget(self.inner_frame_personal) # 创建表格
        self.table.setBorderVisible(True) # 边框
        self.table.setBorderRadius(8) # 圆角
        self.table.setWordWrap(False) # 不换行
        self.table.setColumnCount(3) # 列数
        self.table.setEditTriggers(TableWidget.NoEditTriggers) # 静止编辑
        self.table.scrollDelagate.verticalSmoothScroll.setSmoothMode(SmoothMode.NO_SMOOTH) # 静止平滑滚动
        self.table.setSortingEnabled(True) # 启用排序

        self.show_table()

    def show_table(self):   
        # 根据班级名称获取学生名单数据
        data = self.__getClassStudents()

        class_name = self.list_setting_card.class_comboBox.currentText()

        if data:
            InfoBar.success(
                title="读取学生名单文件成功",
                content=f"读取学生名单文件成功,班级:{class_name}",
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
            for j in range(3):
                self.table.setItem(i, j, QTableWidgetItem(row[j]))
                self.table.item(i, j).setTextAlignment(Qt.AlignmentFlag.AlignCenter) # 居中
                self.table.item(i, j).setFont(QFont(load_custom_font(), 14)) # 设置字体
                
        # 设置表头
        self.table.setHorizontalHeaderLabels(['学号', '姓名', '所处小组'])
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

        self.__initWidget()

    def __getClassStudents(self):
        """根据班级名称获取学生名单数据"""
        # 获取班级名称
        class_name = self.list_setting_card.class_comboBox.currentText()
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
                    
                # 生成学号(从1开始)并返回学生数据
                # 处理被【】包围的名字，去除括号
                processed_names = [name[1:-1] if name.startswith('【') and name.endswith('】') else name for name in students]
                return [[str(i+1).zfill(2), processed_names[i], students_group[i]] for i in range(len(students))]
                
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