from qfluentwidgets import *
from qfluentwidgets import FluentIcon as FIF
from PyQt5.QtGui import *

import os
from loguru import logger

from app.common.config import load_custom_font

# 配置日志记录
log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

logger.add(
    os.path.join(log_dir, "SecRandom_{time:YYYY-MM-DD}.log"),
    rotation="1 MB",
    encoding="utf-8",
    retention="30 days",
    format="{time:YYYY-MM-DD HH:mm:ss:SSS} | {level} | {name}:{function}:{line} - {message}"
)

class history_SettinsCard(GroupHeaderCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("历史记录")
        self.setBorderRadius(8)
        self.settings_file = "app/Settings/Settings.json"

        # 刷新按钮
        self.refresh_button = PrimaryPushButton('刷新列表/记录')
        self.refresh_button.setFixedSize(180, 50)
        self.refresh_button.setFont(QFont(load_custom_font(), 15))
        self.refresh_button.clicked.connect(self.refresh_class_list)
        
        # 选择班级的下拉框
        self.class_comboBox = ComboBox()
        self.class_comboBox.setFixedWidth(320)
        self.class_comboBox.setPlaceholderText("选择需要查看历史记录的班级")
        self.class_comboBox.addItems([])
        self.class_comboBox.setFont(QFont(load_custom_font(), 15))
        self.class_comboBox.currentIndexChanged.connect(self.load_students)

        # 选择同学的下拉框
        self.student_comboBox = ComboBox()
        self.student_comboBox.setFixedWidth(200)
        self.student_comboBox.setPlaceholderText("选择需要查看历史记录的同学")
        self.student_comboBox.addItems([])
        self.student_comboBox.setFont(QFont(load_custom_font(), 15))
        
        # 程序启动时自动加载班级名称
        self.refresh_class_list()
        # 当选择班级时加载对应的学生名称
        self.load_students()

        # 添加组件到分组中
        self.addGroup(FIF.SYNC, "刷新列表/记录", "点击按钮刷新班级列表/记录表格", self.refresh_button)
        self.addGroup(FIF.EDUCATION, "选择班级", "选择需要查看历史记录的班级", self.class_comboBox)
        self.addGroup(FIF.PEOPLE, "选择同学", "全班同学是详细的内容,个人是只有抽取的时间与方式", self.student_comboBox)

    def refresh_class_list(self):
        try:
            if os.path.exists("app/resource/class/class.ini"):
                with open("app/resource/class/class.ini", 'r', encoding='utf-8') as f:
                    classes = [line.strip() for line in f.read().split('\n') if line.strip()]
                    self.class_comboBox.clear()
                    self.class_comboBox.addItems(classes)
        except Exception as e:
            logger.error(f"加载班级名称失败: {str(e)}")

    def load_students(self):
        class_name = self.class_comboBox.currentText()
        try:
            if os.path.exists(f"app/resource/students/{class_name}.ini"):
                with open(f"app/resource/students/{class_name}.ini", 'r', encoding='utf-8') as f:
                    students = [line.strip() for line in f.read().split('\n') if line.strip()]
                    self.student_comboBox.clear()
                    students = ['全班同学'] + students
                    self.student_comboBox.addItems(students)
        except Exception as e:
            logger.error(f"加载学生名称失败: {str(e)}")