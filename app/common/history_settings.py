from re import S
from qfluentwidgets import *
from qfluentwidgets import FluentIcon as FIF
from PyQt5.QtGui import *

import os
from loguru import logger

from app.common.config import load_custom_font

class history_SettinsCard(GroupHeaderCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("历史记录")
        self.setBorderRadius(8)
        self.settings_file = "app/Settings/Settings.json"

        # 刷新按钮
        self.refresh_button = PrimaryPushButton('刷新列表/记录')
        self.refresh_button.setFixedSize(150, 35)
        self.refresh_button.setFont(QFont(load_custom_font(), 14))
        self.refresh_button.clicked.connect(self.refresh_class_list)
        self.refresh_button.clicked.connect(self.load_students)
        
        # 选择班级的下拉框
        self.class_comboBox = ComboBox()
        self.class_comboBox.setFixedWidth(250)
        self.class_comboBox.setPlaceholderText("选择需要查看历史记录的班级")
        self.class_comboBox.addItems([])
        self.class_comboBox.setFont(QFont(load_custom_font(), 12))
        self.class_comboBox.currentIndexChanged.connect(self.load_students)

        # 选择同学的下拉框
        self.student_comboBox = ComboBox()
        self.student_comboBox.setFixedWidth(250)
        self.student_comboBox.setPlaceholderText("选择需要查看历史记录的同学")
        self.student_comboBox.addItems([])
        self.student_comboBox.setFont(QFont(load_custom_font(), 12))
        
        # 程序启动时自动加载班级名称
        self.refresh_class_list()
        # 当选择班级时加载对应的学生名称
        self.load_students()

        # 添加组件到分组中
        self.addGroup(QIcon("app/resource/assets/ic_fluent_arrow_sync_20_filled.svg"), "刷新列表/记录", "点击按钮刷新班级列表/记录表格", self.refresh_button)
        self.addGroup(QIcon("app/resource/assets/ic_fluent_class_20_filled.svg"), "选择班级", "选择一个需要查看历史记录的班级", self.class_comboBox)
        self.addGroup(QIcon("app/resource/assets/ic_fluent_person_20_filled.svg"), "选择同学", "全班同学是详细的内容,个人是只有抽取的时间与方式", self.student_comboBox)

    def refresh_class_list(self):
        try:
            list_folder = "app/resource/list"
            if os.path.exists(list_folder) and os.path.isdir(list_folder):
                files = os.listdir(list_folder)
                classes = []
                for file in files:
                    if file.endswith('.json'):
                        class_name = os.path.splitext(file)[0]
                        classes.append(class_name)
                
                self.class_comboBox.clear()
                self.class_comboBox.addItems(classes)
        except Exception as e:
            logger.error(f"加载班级名称失败: {str(e)}")

    def load_students(self):
        class_name = self.class_comboBox.currentText()
        try:
            student_file = f"app/resource/list/{class_name}.json"

            if os.path.exists(student_file):
                with open(student_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    cleaned_data = []
                    for student_name, student_info in data.items():
                        if isinstance(student_info, dict) and 'id' in student_info:
                            id = student_info.get('id', '')
                            name = student_name.replace('【', '').replace('】', '')
                            gender = student_info.get('gender', '')
                            group = student_info.get('group', '')
                            cleaned_data.append(name)

                    students = cleaned_data
                    self.student_comboBox.clear()
                    students = ['全班同学'] + students
                    self.student_comboBox.addItems(students)
            else:
                self.student_comboBox.clear()
        except Exception as e:
            logger.error(f"加载学生名称失败: {str(e)}")