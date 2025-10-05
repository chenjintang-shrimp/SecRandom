from qfluentwidgets import *
from qfluentwidgets import FluentIcon as FIF
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import os
from pathlib import Path
from loguru import logger
from app.common.path_utils import path_manager, open_file, ensure_dir

from app.common.config import get_theme_icon, load_custom_font

class history_SettinsCard(GroupHeaderCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("历史记录")
        self.setBorderRadius(8)
        self.settings_file = path_manager.get_settings_path()
        self.default_settings = {
            "probability_weight": 0,
            "history_enabled": True,
            "history_days": 0
        }

        # 刷新按钮
        self.refresh_button = PrimaryPushButton('刷新列表/记录')
        self.refresh_button.setFixedSize(150, 35)
        self.refresh_button.setFont(QFont(load_custom_font(), 14))
        self.refresh_button.clicked.connect(self.refresh_class_list)
        self.refresh_button.clicked.connect(self.load_students)
        
        # 选择班级的下拉框
        self.class_comboBox = ComboBox()
        self.class_comboBox.setPlaceholderText("选择一个需要查看历史记录的班级")
        self.class_comboBox.addItems([])
        self.class_comboBox.setFont(QFont(load_custom_font(), 12))
        self.class_comboBox.currentIndexChanged.connect(self.load_students)

        # 选择同学的下拉框
        self.student_comboBox = ComboBox()
        self.student_comboBox.setPlaceholderText("选择需要查看历史记录的同学")
        self.student_comboBox.addItems([])
        self.student_comboBox.setFont(QFont(load_custom_font(), 12))

        # 选择过期天数
        self.history_spinBox = SpinBox()
        self.history_spinBox.setRange(0, 365)
        self.history_spinBox.setValue(0)
        self.history_spinBox.valueChanged.connect(self.save_settings)
        self.history_spinBox.setSuffix("天")
        self.history_spinBox.setFont(QFont(load_custom_font(), 12))

        # 清除历史记录按钮
        self.clear_history_Button = PushButton("清除历史记录")
        self.clear_history_Button.clicked.connect(self.clear_history)
        self.clear_history_Button.setFont(QFont(load_custom_font(), 12))

        # 权重还是概率
        self.probability_or_weight = ComboBox()
        self.probability_or_weight.setPlaceholderText("选择权重|概率")
        self.probability_or_weight.addItems(["权重", "概率"])
        self.probability_or_weight.currentIndexChanged.connect(self.save_settings)
        self.probability_or_weight.setFont(QFont(load_custom_font(), 12))

        # 历史记录开关
        self.history_switch = SwitchButton()
        self.history_switch.setOnText("开启")
        self.history_switch.setOffText("关闭")
        self.history_switch.checkedChanged.connect(self.save_settings)
        self.history_switch.setFont(QFont(load_custom_font(), 12))
        
        # 程序启动时自动加载班级名称
        self.refresh_class_list()
        # 当选择班级时加载对应的学生名称
        self.load_students()

        # 添加组件到分组中
        # ===== 数据刷新 =====
        self.addGroup(get_theme_icon("ic_fluent_arrow_sync_20_filled"), "刷新列表/记录", "重新加载班级列表和历史记录数据", self.refresh_button)
        
        # ===== 数据选择 =====
        self.addGroup(get_theme_icon("ic_fluent_class_20_filled"), "选择班级", "选择要查看历史记录的目标班级", self.class_comboBox)
        self.addGroup(get_theme_icon("ic_fluent_person_20_filled"), "选择学生", "选择查看范围：全班(详细记录)或个人(抽取时间与方式)", self.student_comboBox)
        
        # ===== 时间配置 =====
        self.addGroup(get_theme_icon("ic_fluent_clock_20_filled"), "配置过期天数", "设置历史记录的保留时间(0-365天)", self.history_spinBox)
        
        # ===== 数据管理 =====
        self.addGroup(get_theme_icon("ic_fluent_delete_dismiss_20_filled"), "清除历史记录", "删除当前班级的所有点名历史记录", self.clear_history_Button)
        
        # ===== 显示设置 =====
        self.addGroup(get_theme_icon("ic_fluent_people_eye_20_filled"), "权重|概率", "选择抽取数据显示方式：权重或概率模式", self.probability_or_weight)
        
        # ===== 功能开关 =====
        self.addGroup(get_theme_icon("ic_fluent_people_eye_20_filled"), "历史记录", "启用历史记录功能(精确公平抽取必需开启)", self.history_switch)

        self.load_settings()

    def refresh_class_list(self):
        try:
            list_folder = path_manager.get_resource_path('list')
            if list_folder.exists() and list_folder.is_dir():
                files = list_folder.iterdir()
                classes = []
                for file in files:
                    if file.suffix == '.json':
                        class_name = file.stem
                        classes.append(class_name)
                
                self.class_comboBox.clear()
                self.class_comboBox.addItems(classes)
            else:
                self.class_comboBox.clear()
        except Exception as e:
            logger.error(f"加载班级名称失败: {str(e)}")

    def load_students(self):
        class_name = self.class_comboBox.currentText()
        try:
            student_file = path_manager.get_resource_path('list', f'{class_name}.json')

            if student_file.exists():
                with open_file(student_file, 'r', encoding='utf-8') as f:
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
                    students = ['全班同学'] + ['全班同学_时间排序'] + students
                    self.student_comboBox.addItems(students)
            else:
                self.student_comboBox.clear()
        except Exception as e:
            logger.error(f"加载学生名称失败: {str(e)}")

    def clear_history(self):
        class_name = self.class_comboBox.currentText()
        try:
            if path_manager.get_resource_path('history', f'{class_name}.json').exists():
                os.remove(path_manager.get_resource_path('history', f'{class_name}.json'))
                logger.info(f"{class_name}的历史记录已清除！")
                InfoBar.success(
                    title='清除成功',
                    content=f"{class_name}的历史记录已清除！",
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
            if path_manager.file_exists(self.settings_file):
                with open_file(self.settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    history_settings = settings.get("history", {})
                        
                    history_enabled = history_settings.get("history_enabled", self.default_settings["history_enabled"])

                    probability_weight = history_settings.get("probability_weight", self.default_settings["probability_weight"])
                    if probability_weight < 0 or probability_weight >= self.probability_or_weight.count():
                        # 如果索引值无效，则使用默认值
                        probability_weight = self.default_settings["probability_weight"]

                    history_days = history_settings.get("history_days", self.default_settings["history_days"])
                    if history_days < 0 or history_days > 365:
                        # 如果索引值无效，则使用默认值
                        history_days = self.default_settings["history_days"]
                    
                    self.history_switch.setChecked(history_enabled)
                    self.probability_or_weight.setCurrentIndex(probability_weight)
                    self.history_spinBox.setValue(history_days)
            else:
                logger.error(f"设置文件不存在: {self.settings_file}")
                self.history_switch.setChecked(self.default_settings["history_enabled"])
                self.probability_or_weight.setCurrentIndex(self.default_settings["probability_weight"])
                self.history_spinBox.setValue(self.default_settings["history_days"])
                self.save_settings()
        except Exception as e:
            logger.error(f"加载设置时出错: {e}")
            self.history_switch.setChecked(self.default_settings["history_enabled"])
            self.probability_or_weight.setCurrentIndex(self.default_settings["probability_weight"])
            self.history_spinBox.setValue(self.default_settings["history_days"])
            self.save_settings()
    
    def save_settings(self):
        # 先读取现有设置
        existing_settings = {}
        if path_manager.file_exists(self.settings_file):
            with open_file(self.settings_file, 'r', encoding='utf-8') as f:
                try:
                    existing_settings = json.load(f)
                except json.JSONDecodeError:
                    existing_settings = {}

        if "history" not in existing_settings:
            existing_settings["history"] = {}
            
        history_settings = existing_settings["history"]
        history_settings["history_enabled"] = self.history_switch.isChecked()
        history_settings["probability_weight"] = self.probability_or_weight.currentIndex()
        history_settings["history_days"] = self.history_spinBox.value()
        
        ensure_dir(Path(self.settings_file).parent)
        with open_file(self.settings_file, 'w', encoding='utf-8') as f:
            json.dump(existing_settings, f, indent=4)
