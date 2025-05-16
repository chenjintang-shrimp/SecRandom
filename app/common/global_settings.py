from qfluentwidgets import *
from qfluentwidgets import FluentIcon as FIF
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

import json
import os
from loguru import logger

from app.common.config import load_custom_font


class global_SettinsCard(GroupHeaderCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("全局设置")
        self.setBorderRadius(8)
        self.settings_file = "app/Settings/Settings.json"
        self.default_settings = {
            "extraction_scope": 0,
            "draw_mode": 0,
            "animation_mode": 0,
            "voice_enabled": True,
            "student_id": 0,
            "student_name": 0,
            "student_quantity": True,
            "class_quantity": True,
        }

        self.global_extraction_scope_comboBox = ComboBox()
        self.global_Draw_comboBox = ComboBox()
        self.global_Animation_comboBox = ComboBox()
        self.global_Voice_switch = SwitchButton()
        self.global_student_id_comboBox = ComboBox()
        self.global_student_name_comboBox = ComboBox()
        self.global_student_quantity_switch = SwitchButton()
        self.global_class_quantity_switch = SwitchButton()

        # 抽取模式作用范围下拉框
        self.global_extraction_scope_comboBox.setFixedWidth(320)
        self.global_extraction_scope_comboBox.addItems(["共享单人和多人的已被抽到的学生名单", "隔离单人和多人的已被抽到的学生名单"])
        self.global_extraction_scope_comboBox.currentIndexChanged.connect(self.save_settings)
        self.global_extraction_scope_comboBox.setFont(QFont(load_custom_font(), 12))
        
        # 抽取模式下拉框
        self.global_Draw_comboBox.setFixedWidth(320) # 设置下拉框宽度为320像素
        self.global_Draw_comboBox.addItems(["重复抽取", "不重复抽取(直到软件重启)", "不重复抽取(直到抽完全部人)"])
        self.global_Draw_comboBox.currentIndexChanged.connect(self.save_settings)
        self.global_Draw_comboBox.setFont(QFont(load_custom_font(), 14))

        # 语音播放按钮
        self.global_Voice_switch.setOnText("开启")
        self.global_Voice_switch.setOffText("关闭")
        self.global_Voice_switch.checkedChanged.connect(self.on_global_Voice_switch_changed)
        self.global_Voice_switch.setFont(QFont(load_custom_font(), 14))

        # 动画模式下拉框
        self.global_Animation_comboBox.setFixedWidth(320) # 设置下拉框宽度为320像素
        self.global_Animation_comboBox.addItems(["手动停止动画", "自动播放完整动画", "直接显示结果"])
        self.global_Animation_comboBox.currentIndexChanged.connect(lambda: self.save_settings())
        self.global_Animation_comboBox.setFont(QFont(load_custom_font(), 14))

        # 学号格式下拉框
        self.global_student_id_comboBox.setFixedWidth(320) # 设置下拉框宽度为320像素
        self.global_student_id_comboBox.addItems(["⌈01⌋", "⌈ 1 ⌋"])
        self.global_student_id_comboBox.currentIndexChanged.connect(self.save_settings)
        self.global_student_id_comboBox.setFont(QFont(load_custom_font(), 14))

        # 姓名格式下拉框
        self.global_student_name_comboBox.setFixedWidth(320) # 设置下拉框宽度为320像素
        self.global_student_name_comboBox.addItems(["⌈张  三⌋", "⌈ 张三 ⌋"])
        self.global_student_name_comboBox.currentIndexChanged.connect(self.save_settings)
        self.global_student_name_comboBox.setFont(QFont(load_custom_font(), 14))

        # 班级总人数下拉框
        self.global_student_quantity_switch.setOnText("显示")
        self.global_student_quantity_switch.setOffText("隐藏")
        self.global_student_quantity_switch.checkedChanged.connect(self.on_global_Voice_switch_changed)
        self.global_student_quantity_switch.setFont(QFont(load_custom_font(), 14))

        # 便捷修改班级功能显示下拉框
        self.global_class_quantity_switch.setOnText("显示")
        self.global_class_quantity_switch.setOffText("隐藏")
        self.global_class_quantity_switch.checkedChanged.connect(self.on_global_Voice_switch_changed)
        self.global_class_quantity_switch.setFont(QFont(load_custom_font(), 14))

        # 添加组件到分组中
        self.addGroup(QIcon("app/resource/assets/ic_fluent_arrow_sync_20_filled.svg"), "抽取模式", "设置抽取模式", self.global_Draw_comboBox)
        self.addGroup(QIcon("app/resource/assets/ic_fluent_share_20_filled.svg"), "抽取作用范围", "设置抽取模式的作用范围", self.global_extraction_scope_comboBox)
        self.addGroup(QIcon("app/resource/assets/ic_fluent_person_feedback_20_filled.svg"), "语音播放", "设置结果公布时是否播放语音", self.global_Voice_switch)
        self.addGroup(QIcon("app/resource/assets/ic_fluent_calendar_video_20_filled.svg"), "动画模式", "设置抽取时的动画播放方式", self.global_Animation_comboBox)
        self.addGroup(QIcon("app/resource/assets/ic_fluent_number_symbol_square_20_filled.svg"), "学号格式", "设置学号格式设置", self.global_student_id_comboBox)
        self.addGroup(QIcon("app/resource/assets/ic_fluent_rename_20_filled.svg"), "姓名格式", "设置姓名格式设置", self.global_student_name_comboBox)
        self.addGroup(QIcon("app/resource/assets/ic_fluent_people_eye_20_filled.svg"), "班级总人数", "设置班级总人数是否显示", self.global_student_quantity_switch)
        self.addGroup(QIcon("app/resource/assets/ic_fluent_class_20_filled.svg"), "便捷修改班级/小组", "设置便捷修改班级/小组功能是否显示", self.global_class_quantity_switch)

        self.load_settings()  # 加载设置
        self.save_settings()  # 保存设置

    def on_global_Voice_switch_changed(self, checked):
        self.save_settings()
        
    def load_settings(self):
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    global_settings = settings.get("global", {})
                    
                    # 直接使用索引值
                    draw_mode = global_settings.get("draw_mode", self.default_settings["draw_mode"])
                    if draw_mode < 0 or draw_mode >= self.global_Draw_comboBox.count():
                        logger.warning(f"无效的抽取模式索引: {draw_mode}")
                        draw_mode = self.default_settings["draw_mode"]
                        
                    animation_mode = global_settings.get("animation_mode", self.default_settings["animation_mode"])
                    if animation_mode < 0 or animation_mode >= self.global_Animation_comboBox.count():
                        logger.warning(f"无效的动画模式索引: {animation_mode}")
                        animation_mode = self.default_settings["animation_mode"]
                        
                    voice_enabled = global_settings.get("voice_enabled", self.default_settings["voice_enabled"])

                    student_id = global_settings.get("student_id", self.default_settings["student_id"])
                    if student_id < 0 or student_id >= self.global_student_id_comboBox.count():
                        logger.warning(f"无效的学号格式索引: {student_id}")
                        student_id = self.default_settings["student_id"]
                    
                    student_name = global_settings.get("student_name", self.default_settings["student_name"])
                    if student_name < 0 or student_name >= self.global_student_name_comboBox.count():
                        logger.warning(f"无效的姓名格式索引: {student_name}")
                        student_name = self.default_settings["student_name"]

                    student_quantity = global_settings.get("student_quantity", self.default_settings["student_quantity"])

                    class_quantity = global_settings.get("class_quantity", self.default_settings["class_quantity"])

                    extraction_scope = global_settings.get("extraction_scope", self.default_settings["extraction_scope"])
                    if extraction_scope < 0 or extraction_scope >= self.global_extraction_scope_comboBox.count():
                        logger.warning(f"无效的抽取作用范围索引: {extraction_scope}")
                        extraction_scope = self.default_settings["extraction_scope"]
                    
                    self.global_Draw_comboBox.setCurrentIndex(draw_mode)
                    self.global_Animation_comboBox.setCurrentIndex(animation_mode)
                    self.global_Voice_switch.setChecked(voice_enabled)
                    self.global_student_id_comboBox.setCurrentIndex(student_id)
                    self.global_student_name_comboBox.setCurrentIndex(student_name)
                    self.global_student_quantity_switch.setChecked(student_quantity)
                    self.global_class_quantity_switch.setChecked(class_quantity)
                    self.global_extraction_scope_comboBox.setCurrentIndex(extraction_scope)
                    logger.info(f"加载全局设置完成")
            else:
                self.global_Draw_comboBox.setCurrentIndex(self.default_settings["draw_mode"])
                self.global_extraction_scope_comboBox.setCurrentIndex(self.default_settings["extraction_scope"])
                self.global_Animation_comboBox.setCurrentIndex(self.default_settings["animation_mode"])
                self.global_Voice_switch.setChecked(self.default_settings["voice_enabled"])
                self.global_student_id_comboBox.setCurrentIndex(self.default_settings["student_id"])
                self.global_student_name_comboBox.setCurrentIndex(self.default_settings["student_name"])
                self.global_student_quantity_switch.setChecked(self.default_settings["student_quantity"])
                self.global_class_quantity_switch.setChecked(self.default_settings["class_quantity"])
                self.save_settings()
        except Exception as e:
            logger.error(f"加载设置时出错: {e}")
            self.global_Draw_comboBox.setCurrentIndex(self.default_settings["draw_mode"])
            self.global_extraction_scope_comboBox.setCurrentIndex(self.default_settings["extraction_scope"])
            self.global_Animation_comboBox.setCurrentIndex(self.default_settings["animation_mode"])
            self.global_Voice_switch.setChecked(self.default_settings["voice_enabled"])
            self.global_student_id_comboBox.setCurrentIndex(self.default_settings["student_id"])
            self.global_student_name_comboBox.setCurrentIndex(self.default_settings["student_name"])
            self.global_student_quantity_switch.setChecked(self.default_settings["student_quantity"])
            self.global_class_quantity_switch.setChecked(self.default_settings["class_quantity"])
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
        
        # 更新global部分的所有设置
        if "global" not in existing_settings:
            existing_settings["global"] = {}
            
        global_settings = existing_settings["global"]
        # 只保存索引值
        global_settings["draw_mode"] = self.global_Draw_comboBox.currentIndex()
        global_settings["animation_mode"] = self.global_Animation_comboBox.currentIndex()
        global_settings["voice_enabled"] = self.global_Voice_switch.isChecked()
        global_settings["student_id"] = self.global_student_id_comboBox.currentIndex()
        global_settings["student_name"] = self.global_student_name_comboBox.currentIndex()
        global_settings["student_quantity"] = self.global_student_quantity_switch.isChecked()
        global_settings["class_quantity"] = self.global_class_quantity_switch.isChecked()
        global_settings["extraction_scope"] = self.global_extraction_scope_comboBox.currentIndex()
        
        os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
        with open(self.settings_file, 'w', encoding='utf-8') as f:
            json.dump(existing_settings, f, indent=4)
