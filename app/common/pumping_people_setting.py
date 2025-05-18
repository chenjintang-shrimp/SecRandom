from qfluentwidgets import *
from qfluentwidgets import FluentIcon as FIF
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

import json
import os
from loguru import logger

from app.common.config import load_custom_font


class pumping_people_SettinsCard(GroupHeaderCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("抽人设置")
        self.setBorderRadius(8)
        self.settings_file = "app/Settings/Settings.json"
        self.default_settings = {
            "extraction_scope": 0,
            "font_size": 50,
            "draw_mode": 0,
            "animation_mode": 0,
            "voice_enabled": True,
            "student_id": 0,
            "student_name": 0,
            "student_quantity": True,
            "class_quantity": True,
        }

        self.pumping_people_Draw_comboBox = ComboBox()
        self.pumping_people_Animation_comboBox = ComboBox()
        self.pumping_people_Voice_switch = SwitchButton()
        self.pumping_people_student_id_comboBox = ComboBox()
        self.pumping_people_student_name_comboBox = ComboBox()
        self.pumping_people_student_quantity_switch = SwitchButton()
        self.pumping_people_class_quantity_switch = SwitchButton()
        self.pumping_people_font_size_edit = LineEdit()
        
        # 抽取模式下拉框
        self.pumping_people_Draw_comboBox.setFixedWidth(320) # 设置下拉框宽度为320像素
        self.pumping_people_Draw_comboBox.addItems(["重复抽取", "不重复抽取(直到软件重启)", "不重复抽取(直到抽完全部人)"])
        self.pumping_people_Draw_comboBox.currentIndexChanged.connect(self.save_settings)
        self.pumping_people_Draw_comboBox.setFont(QFont(load_custom_font(), 14))

        # 字体大小
        self.pumping_people_font_size_edit.setPlaceholderText("请输入字体大小 (30-200)")
        self.pumping_people_font_size_edit.setClearButtonEnabled(True)
        # 设置宽度和高度
        self.pumping_people_font_size_edit.setFixedWidth(250)
        self.pumping_people_font_size_edit.setFixedHeight(32)
        # 设置字体
        self.pumping_people_font_size_edit.setFont(QFont(load_custom_font(), 14))

        # 添加应用按钮
        apply_action = QAction(FluentIcon.SAVE.qicon(), "", triggered=self.apply_font_size)
        self.pumping_people_font_size_edit.addAction(apply_action, QLineEdit.TrailingPosition)

        # 添加重置按钮
        reset_action = QAction(FluentIcon.SYNC.qicon(), "", triggered=self.reset_font_size)
        self.pumping_people_font_size_edit.addAction(reset_action, QLineEdit.LeadingPosition)

        # 语音播放按钮
        self.pumping_people_Voice_switch.setOnText("开启")
        self.pumping_people_Voice_switch.setOffText("关闭")
        self.pumping_people_Voice_switch.checkedChanged.connect(self.on_pumping_people_Voice_switch_changed)
        self.pumping_people_Voice_switch.setFont(QFont(load_custom_font(), 14))

        # 动画模式下拉框
        self.pumping_people_Animation_comboBox.setFixedWidth(320) # 设置下拉框宽度为320像素
        self.pumping_people_Animation_comboBox.addItems(["手动停止动画", "自动播放完整动画", "直接显示结果"])
        self.pumping_people_Animation_comboBox.currentIndexChanged.connect(lambda: self.save_settings())
        self.pumping_people_Animation_comboBox.setFont(QFont(load_custom_font(), 14))

        # 学号格式下拉框
        self.pumping_people_student_id_comboBox.setFixedWidth(320) # 设置下拉框宽度为320像素
        self.pumping_people_student_id_comboBox.addItems(["⌈01⌋", "⌈ 1 ⌋"])
        self.pumping_people_student_id_comboBox.currentIndexChanged.connect(self.save_settings)
        self.pumping_people_student_id_comboBox.setFont(QFont(load_custom_font(), 14))

        # 姓名格式下拉框
        self.pumping_people_student_name_comboBox.setFixedWidth(320) # 设置下拉框宽度为320像素
        self.pumping_people_student_name_comboBox.addItems(["⌈张  三⌋", "⌈ 张三 ⌋"])
        self.pumping_people_student_name_comboBox.currentIndexChanged.connect(self.save_settings)
        self.pumping_people_student_name_comboBox.setFont(QFont(load_custom_font(), 14))

        # 班级总人数下拉框
        self.pumping_people_student_quantity_switch.setOnText("显示")
        self.pumping_people_student_quantity_switch.setOffText("隐藏")
        self.pumping_people_student_quantity_switch.checkedChanged.connect(self.on_pumping_people_Voice_switch_changed)
        self.pumping_people_student_quantity_switch.setFont(QFont(load_custom_font(), 14))

        # 便捷修改班级功能显示下拉框
        self.pumping_people_class_quantity_switch.setOnText("显示")
        self.pumping_people_class_quantity_switch.setOffText("隐藏")
        self.pumping_people_class_quantity_switch.checkedChanged.connect(self.on_pumping_people_Voice_switch_changed)
        self.pumping_people_class_quantity_switch.setFont(QFont(load_custom_font(), 14))

        # 添加组件到分组中
        self.addGroup(QIcon("app/resource/assets/ic_fluent_arrow_sync_20_filled.svg"), "抽取模式", "设置抽取模式", self.pumping_people_Draw_comboBox)
        self.addGroup(QIcon("app/resource/assets/ic_fluent_text_font_size_20_filled.svg"), "字体大小", "设置抽取结果的字体大小", self.pumping_people_font_size_edit)
        self.addGroup(QIcon("app/resource/assets/ic_fluent_person_feedback_20_filled.svg"), "语音播放", "设置结果公布时是否播放语音", self.pumping_people_Voice_switch)
        self.addGroup(QIcon("app/resource/assets/ic_fluent_calendar_video_20_filled.svg"), "动画模式", "设置抽取时的动画播放方式", self.pumping_people_Animation_comboBox)
        self.addGroup(QIcon("app/resource/assets/ic_fluent_number_symbol_square_20_filled.svg"), "学号格式", "设置学号格式设置", self.pumping_people_student_id_comboBox)
        self.addGroup(QIcon("app/resource/assets/ic_fluent_rename_20_filled.svg"), "姓名格式", "设置姓名格式设置", self.pumping_people_student_name_comboBox)
        self.addGroup(QIcon("app/resource/assets/ic_fluent_people_eye_20_filled.svg"), "班级总人数", "设置班级总人数是否显示", self.pumping_people_student_quantity_switch)
        self.addGroup(QIcon("app/resource/assets/ic_fluent_class_20_filled.svg"), "便捷修改班级/小组", "设置便捷修改班级/小组功能是否显示", self.pumping_people_class_quantity_switch)

        self.load_settings()  # 加载设置
        self.save_settings()  # 保存设置

    def on_pumping_people_Voice_switch_changed(self, checked):
        self.save_settings()

    def apply_font_size(self):
        try:
            font_size = int(self.pumping_people_font_size_edit.text())
            if 30 <= font_size <= 200:
                self.pumping_people_font_size_edit.setText(str(font_size))
                self.save_settings()
                InfoBar.success(
                    title='设置成功',
                    content=f"设置字体大小为: {font_size}",
                    orient=Qt.Horizontal,
                    parent=self,
                    isClosable=True,
                    duration=3000
                )
            else:
                logger.warning(f"字体大小超出范围: {font_size}")
                InfoBar.warning(
                    title='字体大小超出范围',
                    content=f"字体大小超出范围，请输入30-200之间的整数: {font_size}",
                    orient=Qt.Horizontal,
                    parent=self,
                    isClosable=True,
                    duration=3000
                )
        except ValueError:
            logger.warning(f"无效的字体大小输入: {self.pumping_people_font_size_edit.text()}")
            InfoBar.warning(
                title='无效的字体大小输入',
                content=f"无效的字体大小输入(需要是整数)：{self.pumping_people_font_size_edit.text()}",
                orient=Qt.Horizontal,
                parent=self,
                isClosable=True,
                duration=3000
            )

    def reset_font_size(self):
        try:
            with open('app/Settings/Settings.json', 'r', encoding='utf-8') as f:
                settings = json.load(f)
                foundation_settings = settings.get('foundation', {})
                main_window_size = foundation_settings.get('main_window_size', 0)
                if main_window_size == 0:
                    self.pumping_people_font_size_edit.setText(str("50"))
                elif main_window_size == 1:
                    self.pumping_people_font_size_edit.setText(str("85"))
                else:
                    self.pumping_people_font_size_edit.setText(str("50"))
        except FileNotFoundError as e:
            logger.error(f"加载设置时出错: {e}, 使用默认大小:50")
            self.pumping_people_font_size_edit.setText(str("50"))
        except KeyError:
            logger.error(f"设置文件中缺少'foundation'键, 使用默认大小:50")
            self.pumping_people_font_size_edit.setText(str("50"))
        self.save_settings()
        self.load_settings()
        
    def load_settings(self):
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    pumping_people_settings = settings.get("pumping_people", {})

                    font_size = pumping_people_settings.get("font_size", self.default_settings["font_size"])
                    
                    # 直接使用索引值
                    draw_mode = pumping_people_settings.get("draw_mode", self.default_settings["draw_mode"])
                    if draw_mode < 0 or draw_mode >= self.pumping_people_Draw_comboBox.count():
                        logger.warning(f"无效的抽取模式索引: {draw_mode}")
                        draw_mode = self.default_settings["draw_mode"]
                        
                    animation_mode = pumping_people_settings.get("animation_mode", self.default_settings["animation_mode"])
                    if animation_mode < 0 or animation_mode >= self.pumping_people_Animation_comboBox.count():
                        logger.warning(f"无效的动画模式索引: {animation_mode}")
                        animation_mode = self.default_settings["animation_mode"]
                        
                    voice_enabled = pumping_people_settings.get("voice_enabled", self.default_settings["voice_enabled"])

                    student_id = pumping_people_settings.get("student_id", self.default_settings["student_id"])
                    if student_id < 0 or student_id >= self.pumping_people_student_id_comboBox.count():
                        logger.warning(f"无效的学号格式索引: {student_id}")
                        student_id = self.default_settings["student_id"]
                    
                    student_name = pumping_people_settings.get("student_name", self.default_settings["student_name"])
                    if student_name < 0 or student_name >= self.pumping_people_student_name_comboBox.count():
                        logger.warning(f"无效的姓名格式索引: {student_name}")
                        student_name = self.default_settings["student_name"]

                    student_quantity = pumping_people_settings.get("student_quantity", self.default_settings["student_quantity"])

                    class_quantity = pumping_people_settings.get("class_quantity", self.default_settings["class_quantity"])
                    
                    self.pumping_people_Draw_comboBox.setCurrentIndex(draw_mode)
                    self.pumping_people_font_size_edit.setText(str(font_size))
                    self.pumping_people_Animation_comboBox.setCurrentIndex(animation_mode)
                    self.pumping_people_Voice_switch.setChecked(voice_enabled)
                    self.pumping_people_student_id_comboBox.setCurrentIndex(student_id)
                    self.pumping_people_student_name_comboBox.setCurrentIndex(student_name)
                    self.pumping_people_student_quantity_switch.setChecked(student_quantity)
                    self.pumping_people_class_quantity_switch.setChecked(class_quantity)
                    logger.info(f"加载抽人设置完成")
            else:
                self.pumping_people_Draw_comboBox.setCurrentIndex(self.default_settings["draw_mode"])
                self.pumping_people_font_size_edit.setText(str(self.default_settings["font_size"]))
                self.pumping_people_Animation_comboBox.setCurrentIndex(self.default_settings["animation_mode"])
                self.pumping_people_Voice_switch.setChecked(self.default_settings["voice_enabled"])
                self.pumping_people_student_id_comboBox.setCurrentIndex(self.default_settings["student_id"])
                self.pumping_people_student_name_comboBox.setCurrentIndex(self.default_settings["student_name"])
                self.pumping_people_student_quantity_switch.setChecked(self.default_settings["student_quantity"])
                self.pumping_people_class_quantity_switch.setChecked(self.default_settings["class_quantity"])
                self.save_settings()
        except Exception as e:
            logger.error(f"加载设置时出错: {e}")
            self.pumping_people_Draw_comboBox.setCurrentIndex(self.default_settings["draw_mode"])
            self.pumping_people_font_size_edit.setText(str(self.default_settings["font_size"]))
            self.pumping_people_Animation_comboBox.setCurrentIndex(self.default_settings["animation_mode"])
            self.pumping_people_Voice_switch.setChecked(self.default_settings["voice_enabled"])
            self.pumping_people_student_id_comboBox.setCurrentIndex(self.default_settings["student_id"])
            self.pumping_people_student_name_comboBox.setCurrentIndex(self.default_settings["student_name"])
            self.pumping_people_student_quantity_switch.setChecked(self.default_settings["student_quantity"])
            self.pumping_people_class_quantity_switch.setChecked(self.default_settings["class_quantity"])
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
        
        # 更新pumping_people部分的所有设置
        if "pumping_people" not in existing_settings:
            existing_settings["pumping_people"] = {}
            
        pumping_people_settings = existing_settings["pumping_people"]
        # 只保存索引值
        pumping_people_settings["draw_mode"] = self.pumping_people_Draw_comboBox.currentIndex()
        pumping_people_settings["animation_mode"] = self.pumping_people_Animation_comboBox.currentIndex()
        pumping_people_settings["voice_enabled"] = self.pumping_people_Voice_switch.isChecked()
        pumping_people_settings["student_id"] = self.pumping_people_student_id_comboBox.currentIndex()
        pumping_people_settings["student_name"] = self.pumping_people_student_name_comboBox.currentIndex()
        pumping_people_settings["student_quantity"] = self.pumping_people_student_quantity_switch.isChecked()
        pumping_people_settings["class_quantity"] = self.pumping_people_class_quantity_switch.isChecked()

        # 保存字体大小
        try:
            font_size = int(self.pumping_people_font_size_edit.text())
            if 30 <= font_size <= 200:
                pumping_people_settings["font_size"] = font_size
            else:
                logger.warning(f"字体大小超出范围: {font_size}")
                InfoBar.warning(
                    title='字体大小超出范围',
                    content=f"字体大小超出范围，请输入30-200之间的整数: {font_size}",
                    orient=Qt.Horizontal,
                    parent=self,
                    isClosable=True,
                    duration=3000
                )
        except ValueError:
            logger.warning(f"无效的字体大小输入: {self.pumping_people_font_size_edit.text()}")
            InfoBar.warning(
                title='无效的字体大小输入',
                content=f"无效的字体大小输入(需要是整数)：{self.pumping_people_font_size_edit.text()}",
                orient=Qt.Horizontal,
                parent=self,
                isClosable=True,
                duration=3000
            )
        
        os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
        with open(self.settings_file, 'w', encoding='utf-8') as f:
            json.dump(existing_settings, f, indent=4)
