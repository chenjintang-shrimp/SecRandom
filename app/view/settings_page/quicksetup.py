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
    def __init__(self, parent: QFrame = None, *args, **kwargs):
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
        self.list_settings_card = list_SettinsCard()
        self.list_settings_card.refresh_signal.connect(self._refresh_table)
        self.inner_layout_personal.addWidget(self.list_settings_card)

        # 创建表格
        self.table = TableWidget(self.inner_frame_personal) # 创建表格
        self.table.setBorderVisible(True) # 边框
        self.table.setBorderRadius(8) # 圆角
        self.table.setWordWrap(False) # 不换行
        self.table.setColumnCount(4) # 列数
        self.table.setEditTriggers(TableWidget.NoEditTriggers) # 静止编辑
        self.table.setSortingEnabled(True) # 启用排序
        self.table.setSelectionMode(QAbstractItemView.SingleSelection) # 单选
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows) # 整行选中

        self.show_table()

    def show_table(self):   
        # 根据班级名称获取学生名单数据
        data = self.__getClassStudents()
        class_name = self.list_settings_card.class_comboBox.currentText()

        if data:
            InfoBar.success(
                title="读取学生名单文件成功",
                content=f"读取学生名单文件成功,班级:{class_name}",
                duration=2000,
                orient=Qt.Horizontal,
                parent=self,
                isClosable=True,
            )
        
        self.table.setRowCount(len(data))
        self.table.clearContents()
        self.table.setSortingEnabled(False) # 禁止排序
        
        # 填充表格数据
        for i, row in enumerate(data):
            for j in range(4):
                self.table.setItem(i, j, QTableWidgetItem(row[j]))
                item = self.table.item(i, j)
                if item:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter) # 居中
                    item.setFont(QFont(load_custom_font(), 12)) # 设置字体
                
        # 设置表头
        self.table.setHorizontalHeaderLabels(['学号', '姓名', '性别', '所处小组'])
        self.table.verticalHeader().hide() # 隐藏垂直表头
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch) # 自适应
        
        self.inner_layout_personal.addWidget(self.table)
        self.scroll_area_personal.setWidget(self.inner_frame_personal)
        self.table.setSortingEnabled(True) # 启用排序

        if not self.layout():
            main_layout = QVBoxLayout(self)
            main_layout.addWidget(self.scroll_area_personal)
        else:
            self.layout().addWidget(self.scroll_area_personal)

    def __getClassStudents(self):
        class_name = self.list_settings_card.class_comboBox.currentText()
        if class_name:
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
                            cleaned_data.append((f'{id}', name, gender, group))
                    return cleaned_data
                    
            except Exception as e:
                logger.error(f"读取学生名单文件失败: {e}")
                InfoBar.error(
                    title="读取学生名单文件失败",
                    content=f"错误信息: {str(e)}",
                    duration=3000,
                    orient=Qt.Horizontal,
                    parent=self,
                    isClosable=True,
                )
                return []
        else:
            return []

    def _refresh_table(self):
        self.table.setRowCount(0)
        self.show_table()