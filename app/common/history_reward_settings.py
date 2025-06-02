from re import S
from qfluentwidgets import *
from qfluentwidgets import FluentIcon as FIF
from PyQt5.QtGui import *

import os
from loguru import logger

from app.common.config import load_custom_font

class history_reward_SettinsCard(GroupHeaderCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("历史记录")
        self.setBorderRadius(8)
        self.settings_file = "app/Settings/Settings.json"

        # 刷新按钮
        self.refresh_button = PrimaryPushButton('刷新列表/记录')
        self.refresh_button.setFixedSize(150, 35)
        self.refresh_button.setFont(QFont(load_custom_font(), 14))
        self.refresh_button.clicked.connect(self.refresh_reward_list)
        self.refresh_button.clicked.connect(self.load_students)
        
        # 选择奖池的下拉框
        self.prize_pools_comboBox = ComboBox()
        self.prize_pools_comboBox.setFixedWidth(250)
        self.prize_pools_comboBox.setPlaceholderText("选择一个需要查看历史记录的奖池")
        self.prize_pools_comboBox.addItems([])
        self.prize_pools_comboBox.setFont(QFont(load_custom_font(), 12))
        self.prize_pools_comboBox.currentIndexChanged.connect(self.load_students)

        # 选择奖品的下拉框
        self.reward_comboBox = ComboBox()
        self.reward_comboBox.setFixedWidth(250)
        self.reward_comboBox.setPlaceholderText("选择需要查看历史记录的奖品")
        self.reward_comboBox.addItems([])
        self.reward_comboBox.setFont(QFont(load_custom_font(), 12))
        
        # 程序启动时自动加载奖池名称
        self.refresh_reward_list()
        # 当选择奖池时加载对应的奖品名称
        self.load_students()

        # 添加组件到分组中
        self.addGroup(QIcon("app/resource/assets/ic_fluent_arrow_sync_20_filled.svg"), "刷新列表/记录", "点击按钮刷新奖池列表/记录表格", self.refresh_button)
        self.addGroup(QIcon("app/resource/assets/ic_fluent_reward_20_filled.svg"), "选择奖池", "选择一个需要查看历史记录的奖池", self.prize_pools_comboBox)
        self.addGroup(QIcon("app/resource/assets/ic_fluent_person_20_filled.svg"), "选择奖品", "这个一个可查看单个奖品的功能", self.reward_comboBox)

    def refresh_reward_list(self):
        try:
            list_folder = "app/resource/reward"
            if os.path.exists(list_folder) and os.path.isdir(list_folder):
                files = os.listdir(list_folder)
                classes = []
                for file in files:
                    if file.endswith('.json'):
                        reward_name = os.path.splitext(file)[0]
                        classes.append(reward_name)
                
                self.prize_pools_comboBox.clear()
                self.prize_pools_comboBox.addItems(classes)
        except Exception as e:
            logger.error(f"加载奖池名称失败: {str(e)}")

    def load_students(self):
        reward_name = self.prize_pools_comboBox.currentText()
        try:
            student_file = f"app/resource/reward/{reward_name}.json"

            if os.path.exists(student_file):
                with open(student_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    cleaned_data = []
                    for student_name, student_info in data.items():
                        if isinstance(student_info, dict) and 'id' in student_info:
                            id = student_info.get('id', '')
                            name = student_name
                            probability = student_info.get('probability', '')
                            cleaned_data.append(name)

                    students = cleaned_data
                    self.reward_comboBox.clear()
                    students = ['全部奖品'] + students
                    self.reward_comboBox.addItems(students)
            else:
                self.reward_comboBox.clear()
        except Exception as e:
            logger.error(f"加载奖品名称失败: {str(e)}")