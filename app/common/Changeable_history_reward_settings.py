from qfluentwidgets import *
from qfluentwidgets import FluentIcon as FIF
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import os
from loguru import logger

from app.common.config import get_theme_icon, load_custom_font

class history_reward_SettinsCard(GroupHeaderCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("历史记录")
        self.setBorderRadius(8)
        self.settings_file = "app/Settings/Settings.json"
        self.default_settings = {
            "reward_history_enabled": True,
            "history_reward_days": 0
        }

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

        self.history_reward_spinBox = SpinBox()
        self.history_reward_spinBox.setRange(0, 365)
        self.history_reward_spinBox.setValue(0)
        self.history_reward_spinBox.valueChanged.connect(self.save_settings)
        self.history_reward_spinBox.setSuffix("天")
        self.history_reward_spinBox.setFont(QFont(load_custom_font(), 12))

        # 清除历史记录按钮
        self.clear_history_Button = PushButton("清除历史记录")
        self.clear_history_Button.clicked.connect(self.clear_history)
        self.clear_history_Button.setFont(QFont(load_custom_font(), 12))

        # 历史记录开关
        self.history_switch = SwitchButton()
        self.history_switch.setOnText("开启")
        self.history_switch.setOffText("关闭")
        self.history_switch.checkedChanged.connect(self.on_switch_changed)
        self.history_switch.setFont(QFont(load_custom_font(), 12))
        
        # 程序启动时自动加载奖池名称
        self.refresh_reward_list()
        # 当选择奖池时加载对应的奖品名称
        self.load_students()

        # 添加组件到分组中
        self.addGroup(get_theme_icon("ic_fluent_arrow_sync_20_filled"), "刷新列表/记录", "点击按钮刷新奖池列表/记录表格", self.refresh_button)
        self.addGroup(get_theme_icon("ic_fluent_reward_20_filled"), "选择奖池", "选择一个需要查看历史记录的奖池", self.prize_pools_comboBox)
        self.addGroup(get_theme_icon("ic_fluent_person_20_filled"), "选择奖品", "这个一个可查看单个奖品的功能", self.reward_comboBox)
        self.addGroup(get_theme_icon("ic_fluent_delete_dismiss_20_filled"), "配置过期天数", "配置历史记录中抽取时间戳的过期天数", self.history_reward_spinBox)
        self.addGroup(get_theme_icon("ic_fluent_delete_dismiss_20_filled"), "清除历史记录", "点击按钮清除当前选择的奖池点名历史记录", self.clear_history_Button)
        self.addGroup(get_theme_icon("ic_fluent_people_eye_20_filled"), "历史记录", "选择是否开启该功能", self.history_switch)

        self.load_settings()
        self.save_settings()

    def on_switch_changed(self, checked):
        self.save_settings()

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
            else:
                self.prize_pools_comboBox.clear()
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

    def clear_history(self):
        reward_name = self.prize_pools_comboBox.currentText()
        try:
            if os.path.exists(f"app/resource/reward/history/{reward_name}.json"):
                os.remove(f"app/resource/reward/history/{reward_name}.json")
                logger.info("历史记录已清除！")
                InfoBar.success(
                    title='清除成功',
                    content="历史记录已清除！",
                    orient=Qt.Horizontal,
                    isClosable=True,
                    duration=3000,
                    position=InfoBarPosition.TOP,
                    parent=self
                )
            else:
                logger.info("没有找到历史记录文件。")
                InfoBar.info(
                    title='提示',
                    content="没有找到历史记录文件。",
                    orient=Qt.Horizontal,
                    isClosable=True,
                    duration=3000,
                    position=InfoBarPosition.TOP,
                    parent=self
                )
        except Exception as e:
            logger.error(f"清除历史记录失败: {str(e)}")
            InfoBar.error(
                title='错误',
                content=f"清除历史记录失败: {str(e)}",
                orient=Qt.Horizontal,
                isClosable=True,
                duration=3000,
                position=InfoBarPosition.TOP,
                parent=self
            )   

    def load_settings(self):
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    history_settings = settings.get("history", {})
                        
                    reward_history_enabled = history_settings.get("reward_history_enabled", self.default_settings["reward_history_enabled"])
                    history_reward_days = history_settings.get("history_days", self.default_settings["history_reward_days"])
                    
                    self.history_switch.setChecked(reward_history_enabled)
                    self.history_reward_spinBox.setValue(history_reward_days)
                    logger.info(f"加载历史记录设置完成")
            else:
                logger.warning(f"设置文件不存在: {self.settings_file}")
                self.history_switch.setChecked(self.default_settings["reward_history_enabled"])
                self.history_reward_spinBox.setValue(self.default_settings["history_reward_days"])
                self.save_settings()
        except Exception as e:
            logger.error(f"加载设置时出错: {e}")
            self.history_switch.setChecked(self.default_settings["reward_history_enabled"])
            self.history_reward_spinBox.setValue(self.default_settings["history_reward_days"])
            self.save_settings()
    
    def save_settings(self):
        # 先读取现有设置
        existing_settings = {}
        if os.path.exists(self.settings_file):
            with open(self.settings_file, 'r', encoding='utf-8') as f:
                try:
                    existing_settings = json.load(f)
                except json.JSONDecodeError:
                    existing_settings = {}

        if "history" not in existing_settings:
            existing_settings["history"] = {}
            
        history_settings = existing_settings["history"]
        history_settings["reward_history_enabled"] = self.history_switch.isChecked()
        history_settings["history_reward_days"] = self.history_reward_spinBox.value()
        
        os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
        with open(self.settings_file, 'w', encoding='utf-8') as f:
            json.dump(existing_settings, f, indent=4)