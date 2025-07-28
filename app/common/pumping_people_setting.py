from qfluentwidgets import *
from qfluentwidgets import FluentIcon as FIF
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

import json
import os
from loguru import logger

from app.common.config import get_theme_icon, load_custom_font
from app.view.main_page import pumping_people


class pumping_people_SettinsCard(GroupHeaderCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("抽人设置")
        self.setBorderRadius(8)
        self.settings_file = "app/Settings/Settings.json"
        self.default_settings = {
            "system_volume_enabled": False,
            "system_volume_value": 100,
            "extraction_scope": 0,
            "font_size": 50.0,
            "draw_mode": 0,
            "draw_pumping": 0,
            "animation_mode": 0,
            "voice_enabled": True,
            "student_id": 0,
            "student_name": 0,
            "people_theme": 0,
            "list_refresh_button": True,
            "class_quantity": True,
            "group_quantity": True,
            "gender_quantity": True,
            "refresh_button": True,
            "voice_volume": 100,
            "voice_speed": 100,
            "show_random_member": False,
            "random_member_format": 2,
            "animation_interval": 100,
            "animation_auto_play": 5,
            "animation_music_enabled": False,
            "result_music_enabled": False,
            "animation_music_volume": 5,
            "result_music_volume": 5,
            "music_fade_in": 300,
            "music_fade_out": 300,
        }

        self.pumping_people_Draw_comboBox = ComboBox()
        self.pumping_Draw_comboBox = ComboBox()
        self.pumping_people_Animation_comboBox = ComboBox()
        self.pumping_people_Voice_switch = SwitchButton()
        self.pumping_people_student_id_comboBox = ComboBox()
        self.pumping_people_student_name_comboBox = ComboBox()
        self.pumping_people_theme_comboBox = ComboBox()
        self.pumping_people_voice_volume_SpinBox = SpinBox()
        self.pumping_people_voice_speed_SpinBox = SpinBox()
        self.pumping_people_font_size_SpinBox = DoubleSpinBox()
        self.pumping_people_system_volume_switch = SwitchButton()
        self.pumping_people_system_volume_SpinBox = SpinBox()
        self.show_random_member_checkbox = SwitchButton()
        self.pumping_people_Animation_interval_SpinBox = SpinBox()
        self.pumping_people_Animation_auto_play_SpinBox = SpinBox()
        
        # 抽取模式下拉框
        self.pumping_people_Draw_comboBox.setFixedWidth(250)
        self.pumping_people_Draw_comboBox.addItems(["重复抽取", "不重复抽取(直到软件重启)", "不重复抽取(直到抽完全部人)"])
        self.pumping_people_Draw_comboBox.currentIndexChanged.connect(self.save_settings)
        self.pumping_people_Draw_comboBox.setFont(QFont(load_custom_font(), 12))

        # 抽取方式下拉框
        self.pumping_Draw_comboBox.setFixedWidth(250)
        self.pumping_Draw_comboBox.addItems(["可预测抽取", "不可预测抽取", "公平可预测抽取", "公平不可预测抽取"])
        self.pumping_Draw_comboBox.currentIndexChanged.connect(self.save_settings)
        self.pumping_Draw_comboBox.setFont(QFont(load_custom_font(), 12))

        # 字体大小
        self.pumping_people_font_size_SpinBox.setRange(30.0, 200.0)
        self.pumping_people_font_size_SpinBox.setValue(50.0)
        self.pumping_people_font_size_SpinBox.setSingleStep(0.5)
        self.pumping_people_font_size_SpinBox.setDecimals(1)
        self.pumping_people_font_size_SpinBox.valueChanged.connect(self.save_settings)
        self.pumping_people_font_size_SpinBox.setFont(QFont(load_custom_font(), 12))

        # 语音播放按钮
        self.pumping_people_Voice_switch.setOnText("开启")
        self.pumping_people_Voice_switch.setOffText("关闭")
        self.pumping_people_Voice_switch.checkedChanged.connect(self.on_pumping_people_Voice_switch_changed)
        self.pumping_people_Voice_switch.setFont(QFont(load_custom_font(), 12))

        # 动画模式下拉框
        self.pumping_people_Animation_comboBox.setFixedWidth(250)
        self.pumping_people_Animation_comboBox.addItems(["手动停止动画", "自动播放完整动画", "直接显示结果"])
        self.pumping_people_Animation_comboBox.currentIndexChanged.connect(lambda: self.save_settings())
        self.pumping_people_Animation_comboBox.setFont(QFont(load_custom_font(), 12))

        # 结果动画间隔（毫秒）
        self.pumping_people_Animation_interval_SpinBox.setRange(50, 2000)
        self.pumping_people_Animation_interval_SpinBox.setValue(100)
        self.pumping_people_Animation_interval_SpinBox.setSingleStep(10) 
        self.pumping_people_Animation_interval_SpinBox.setSuffix("ms")
        self.pumping_people_Animation_interval_SpinBox.valueChanged.connect(self.save_settings)
        self.pumping_people_Animation_interval_SpinBox.setFont(QFont(load_custom_font(), 12))

        # 自动播放间隔结果次数
        self.pumping_people_Animation_auto_play_SpinBox.setRange(1, 200)
        self.pumping_people_Animation_auto_play_SpinBox.setValue(5)
        self.pumping_people_Animation_auto_play_SpinBox.setSingleStep(5)
        self.pumping_people_Animation_auto_play_SpinBox.setSuffix("次")
        self.pumping_people_Animation_auto_play_SpinBox.valueChanged.connect(self.save_settings)
        self.pumping_people_Animation_auto_play_SpinBox.setFont(QFont(load_custom_font(), 12))

        # 学号格式下拉框
        self.pumping_people_student_id_comboBox.setFixedWidth(150)
        self.pumping_people_student_id_comboBox.addItems(["⌈01⌋", "⌈ 1 ⌋"])
        self.pumping_people_student_id_comboBox.currentIndexChanged.connect(self.save_settings)
        self.pumping_people_student_id_comboBox.setFont(QFont(load_custom_font(), 12))

        # 姓名格式下拉框
        self.pumping_people_student_name_comboBox.setFixedWidth(150)
        self.pumping_people_student_name_comboBox.addItems(["⌈张  三⌋", "⌈ 张三 ⌋"])
        self.pumping_people_student_name_comboBox.currentIndexChanged.connect(self.save_settings)
        self.pumping_people_student_name_comboBox.setFont(QFont(load_custom_font(), 12))

        # 人数/组数样式下拉框
        self.pumping_people_theme_comboBox.setFixedWidth(150)
        self.pumping_people_theme_comboBox.addItems(["总数 | 剩余", "总数", "剩余"])
        self.pumping_people_theme_comboBox.currentIndexChanged.connect(self.save_settings)
        self.pumping_people_theme_comboBox.setFont(QFont(load_custom_font(), 12))

        # 音量
        self.pumping_people_voice_volume_SpinBox.setRange(0, 100)
        self.pumping_people_voice_volume_SpinBox.setValue(100)
        self.pumping_people_voice_volume_SpinBox.setSingleStep(5)
        self.pumping_people_voice_volume_SpinBox.setSuffix("%")
        self.pumping_people_voice_volume_SpinBox.valueChanged.connect(self.save_settings)
        self.pumping_people_voice_volume_SpinBox.setFont(QFont(load_custom_font(), 12))

        # 语速
        self.pumping_people_voice_speed_SpinBox.setRange(1, 500)
        self.pumping_people_voice_speed_SpinBox.setValue(100)
        self.pumping_people_voice_speed_SpinBox.setSingleStep(10)
        self.pumping_people_voice_speed_SpinBox.setSuffix("wpm")
        self.pumping_people_voice_speed_SpinBox.valueChanged.connect(self.save_settings)
        self.pumping_people_voice_speed_SpinBox.setFont(QFont(load_custom_font(), 12))

        # 系统音量控制开关
        self.pumping_people_system_volume_switch.setOnText("开启")
        self.pumping_people_system_volume_switch.setOffText("关闭")
        self.pumping_people_system_volume_switch.checkedChanged.connect(self.save_settings)
        self.pumping_people_system_volume_switch.setFont(QFont(load_custom_font(), 12))

        # 系统音量
        self.pumping_people_system_volume_SpinBox.setRange(0, 100)
        self.pumping_people_system_volume_SpinBox.setValue(100)
        self.pumping_people_system_volume_SpinBox.setSingleStep(5)
        self.pumping_people_system_volume_SpinBox.setSuffix("%")
        self.pumping_people_system_volume_SpinBox.valueChanged.connect(self.save_settings)
        self.pumping_people_system_volume_SpinBox.setFont(QFont(load_custom_font(), 12))

        # 随机组员显示设置
        self.show_random_member_checkbox.setOnText("开启")
        self.show_random_member_checkbox.setOffText("关闭")
        self.show_random_member_checkbox.checkedChanged.connect(self.on_pumping_people_Voice_switch_changed)
        self.show_random_member_checkbox.setFont(QFont(load_custom_font(), 12))

        # 随机组员格式设置
        self.random_member_format_comboBox = ComboBox()
        self.random_member_format_comboBox.addItems([
            "[组名]-随机组员:[姓名]",
            "[组名]-随机:[姓名]",
            "[组名]-[姓名]",
            "[组名]>[姓名]",
            "[组名]>[姓名]<"
        ])
        self.random_member_format_comboBox.setCurrentIndex(2)
        self.random_member_format_comboBox.currentIndexChanged.connect(self.save_settings)
        self.random_member_format_comboBox.setFont(QFont(load_custom_font(), 12))

        # 动画音乐开关
        self.pumping_people_Animation_music_switch = SwitchButton()
        self.pumping_people_Animation_music_switch.setOnText("开启")
        self.pumping_people_Animation_music_switch.setOffText("关闭")
        self.pumping_people_Animation_music_switch.checkedChanged.connect(self.save_settings)
        self.pumping_people_Animation_music_switch.setFont(QFont(load_custom_font(), 12))

        # 结果音乐开关
        self.pumping_people_result_music_switch = SwitchButton()
        self.pumping_people_result_music_switch.setOnText("开启")
        self.pumping_people_result_music_switch.setOffText("关闭")
        self.pumping_people_result_music_switch.checkedChanged.connect(self.save_settings)
        self.pumping_people_result_music_switch.setFont(QFont(load_custom_font(), 12))

        # 动画音乐文件夹
        self.pumping_people_Animation_music_path_button = PushButton("动画音乐文件夹")
        self.pumping_people_Animation_music_path_button.setFont(QFont(load_custom_font(), 12))
        self.pumping_people_Animation_music_path_button.clicked.connect(lambda: self.open_music_path('Animation_music'))

        # 结果音乐文件夹
        self.pumping_people_result_music_path_button = PushButton("结果音乐文件夹")
        self.pumping_people_result_music_path_button.setFont(QFont(load_custom_font(), 12))
        self.pumping_people_result_music_path_button.clicked.connect(lambda: self.open_music_path('result_music'))

        # 动画音乐音量
        self.pumping_people_Animation_music_volume_SpinBox = SpinBox()
        self.pumping_people_Animation_music_volume_SpinBox.setRange(0, 100)
        self.pumping_people_Animation_music_volume_SpinBox.setValue(5)
        self.pumping_people_Animation_music_volume_SpinBox.setSingleStep(5)
        self.pumping_people_Animation_music_volume_SpinBox.setSuffix("%")
        self.pumping_people_Animation_music_volume_SpinBox.valueChanged.connect(self.save_settings)
        self.pumping_people_Animation_music_volume_SpinBox.setFont(QFont(load_custom_font(), 12))

        # 结果音乐音量
        self.pumping_people_result_music_volume_SpinBox = SpinBox()
        self.pumping_people_result_music_volume_SpinBox.setRange(0, 100)
        self.pumping_people_result_music_volume_SpinBox.setValue(5)
        self.pumping_people_result_music_volume_SpinBox.setSingleStep(5)
        self.pumping_people_result_music_volume_SpinBox.setSuffix("%")
        self.pumping_people_result_music_volume_SpinBox.valueChanged.connect(self.save_settings)
        self.pumping_people_result_music_volume_SpinBox.setFont(QFont(load_custom_font(), 12))

        # 渐入时间
        self.pumping_people_music_fade_in_SpinBox = SpinBox()
        self.pumping_people_music_fade_in_SpinBox.setRange(0, 1000)
        self.pumping_people_music_fade_in_SpinBox.setValue(300)
        self.pumping_people_music_fade_in_SpinBox.setSingleStep(100)
        self.pumping_people_music_fade_in_SpinBox.setSuffix("ms")
        self.pumping_people_music_fade_in_SpinBox.valueChanged.connect(self.save_settings)
        self.pumping_people_music_fade_in_SpinBox.setFont(QFont(load_custom_font(), 12))

        # 渐出时间
        self.pumping_people_music_fade_out_SpinBox = SpinBox()
        self.pumping_people_music_fade_out_SpinBox.setRange(0, 1000)
        self.pumping_people_music_fade_out_SpinBox.setValue(300)
        self.pumping_people_music_fade_out_SpinBox.setSingleStep(100)
        self.pumping_people_music_fade_out_SpinBox.setSuffix("ms")
        self.pumping_people_music_fade_out_SpinBox.valueChanged.connect(self.save_settings)
        self.pumping_people_music_fade_out_SpinBox.setFont(QFont(load_custom_font(), 12))

        # 添加组件到分组中
        self.addGroup(get_theme_icon("ic_fluent_arrow_sync_20_filled"), "抽取模式", "设置抽取模式", self.pumping_people_Draw_comboBox)
        self.addGroup(get_theme_icon("ic_fluent_arrow_sync_20_filled"), "抽取方式", "设置抽取方式", self.pumping_Draw_comboBox)
        self.addGroup(get_theme_icon("ic_fluent_text_font_size_20_filled"), "字体大小", "设置抽取结果的字体大小(支持小数)", self.pumping_people_font_size_SpinBox)
        self.addGroup(get_theme_icon("ic_fluent_number_symbol_square_20_filled"), "学号格式", "设置学号格式设置", self.pumping_people_student_id_comboBox)
        self.addGroup(get_theme_icon("ic_fluent_rename_20_filled"), "姓名格式", "设置姓名格式设置", self.pumping_people_student_name_comboBox)
        self.addGroup(get_theme_icon("ic_fluent_person_20_filled"), "显示随机组员", "抽取小组时是否显示随机组员", self.show_random_member_checkbox)
        self.addGroup(get_theme_icon("ic_fluent_people_eye_20_filled"), "组员显示格式", "设置随机组员的显示格式", self.random_member_format_comboBox)
        self.addGroup(get_theme_icon("ic_fluent_people_eye_20_filled"), "班级人|组数", "设置该功能的显示格式", self.pumping_people_theme_comboBox)
        self.addGroup(get_theme_icon("ic_fluent_calendar_video_20_filled"), "动画模式", "设置抽取时的动画播放方式", self.pumping_people_Animation_comboBox)
        self.addGroup(get_theme_icon("ic_fluent_calendar_video_20_filled"), "动画间隔", "设置抽取时的动画播放间隔(50-2000)(<1,2号动画模式>适用)", self.pumping_people_Animation_interval_SpinBox)
        self.addGroup(get_theme_icon("ic_fluent_calendar_video_20_filled"), "自动播放次数", "设置抽取时的自动播放次数(1-200)(<2号动画模式>适用)", self.pumping_people_Animation_auto_play_SpinBox)
        self.addGroup(get_theme_icon("ic_fluent_person_feedback_20_filled"), "语音播放", "设置结果公布时是否播放语音", self.pumping_people_Voice_switch)
        self.addGroup(get_theme_icon("ic_fluent_music_note_2_20_filled"), "音量大小", "调节播报音量 (0-100)", self.pumping_people_voice_volume_SpinBox)
        self.addGroup(get_theme_icon("ic_fluent_person_feedback_20_filled"), "语速调节", "调节播报语速 (1-500)", self.pumping_people_voice_speed_SpinBox)
        self.addGroup(get_theme_icon("ic_fluent_person_voice_20_filled"), "系统音量控制", "抽取完成后自动设置系统音量", self.pumping_people_system_volume_switch)
        self.addGroup(get_theme_icon("ic_fluent_music_note_2_20_filled"), "系统音量大小", "设置抽取完成后的系统音量 (0-100)", self.pumping_people_system_volume_SpinBox)
        self.addGroup(get_theme_icon("ic_fluent_music_note_2_20_filled"), "动画音乐", "抽取动画背景音乐是否进行播放", self.pumping_people_Animation_music_switch)
        self.addGroup(get_theme_icon("ic_fluent_music_note_2_20_filled"), "结果音乐", "抽取结果背景音乐是否进行播放", self.pumping_people_result_music_switch)
        self.addGroup(get_theme_icon("ic_fluent_music_note_2_20_filled"), "动画音乐文件夹", "点击打开抽取动画背景音乐目录", self.pumping_people_Animation_music_path_button)
        self.addGroup(get_theme_icon("ic_fluent_music_note_2_20_filled"), "结果音乐文件夹", "点击打开抽取结果背景音乐目录", self.pumping_people_result_music_path_button)
        self.addGroup(get_theme_icon("ic_fluent_music_note_2_20_filled"), "动画音乐音量", "设置抽取动画背景音乐音量 (0-100)", self.pumping_people_Animation_music_volume_SpinBox)
        self.addGroup(get_theme_icon("ic_fluent_music_note_2_20_filled"), "结果音乐音量", "设置抽取结果背景音乐音量 (0-100)", self.pumping_people_result_music_volume_SpinBox)
        self.addGroup(get_theme_icon("ic_fluent_music_note_2_20_filled"), "动画/结果音乐渐入时间", "设置抽取动画/结果背景音乐渐入时间 (0-1000)(ms)", self.pumping_people_music_fade_in_SpinBox)
        self.addGroup(get_theme_icon("ic_fluent_music_note_2_20_filled"), "动画/结果音乐渐出时间", "设置抽取动画/结果背景音乐渐出时间 (0-1000)(ms)", self.pumping_people_music_fade_out_SpinBox)

        self.load_settings()  # 加载设置
        self.save_settings()  # 保存设置

    def on_pumping_people_Voice_switch_changed(self, checked):
        self.save_settings()

    def open_music_path(self, button):
        BGM_ANIMATION_PATH = './app/resource/music/pumping_people/Animation_music'
        BGM_RESULT_PATH = './app/resource/music/pumping_people/result_music'
        if not os.path.exists(BGM_ANIMATION_PATH):
            os.makedirs(BGM_ANIMATION_PATH)
        if not os.path.exists(BGM_RESULT_PATH):
            os.makedirs(BGM_RESULT_PATH)
        # 星野引导：根据按钮选择打开对应的音乐文件夹 (๑•̀ㅂ•́)و✧
        if button == 'Animation_music':
            # 白露提示：确保路径是文件夹格式再打开哦～
            os.startfile(os.path.abspath(BGM_ANIMATION_PATH))
        elif button == 'result_music':
            # 星野守护：用绝对路径确保文件夹正确打开～
            os.startfile(os.path.abspath(BGM_RESULT_PATH))

    def apply_font_size(self):
        try:
            font_size_str = self.pumping_people_font_size_SpinBox.value()
            # 检查是否为一位小数
            if '.' in font_size_str:
                integer_part, decimal_part = font_size_str.split('.', 1)
                if len(decimal_part) > 1:
                    raise ValueError("最多只能输入一位小数")
            font_size = float(font_size_str)
            if 30.0 <= font_size <= 200.0:
                # 格式化保留一位小数
                self.pumping_people_font_size_SpinBox.setValue(font_size)
                self.save_settings()
                InfoBar.success(
                    title='设置成功',
                    content=f"设置字体大小为: {font_size:.1f}",
                    orient=Qt.Horizontal, parent=self, isClosable=True, duration=3000, position=InfoBarPosition.TOP
                )
            else:
                logger.warning(f"字体大小超出范围: {font_size}")
                InfoBar.warning(
                    title='字体大小超出范围',
                    content=f"字体大小超出范围，请输入30.0-200.0之间的数字，最多一位小数: {font_size}",
                    orient=Qt.Horizontal, parent=self, isClosable=True, duration=3000, position=InfoBarPosition.TOP
                )
        except ValueError as e:
            logger.warning(f"无效的字体大小输入: {self.pumping_people_font_size_SpinBox.value()}")
            InfoBar.warning(
                title='无效的字体大小输入',
                content=f"无效的字体大小输入: {str(e)}",
                orient=Qt.Horizontal, parent=self, isClosable=True, duration=3000, position=InfoBarPosition.TOP
            )

    def reset_font_size(self):
        try:
            self.pumping_people_font_size_SpinBox.setValue("50.0")
        except FileNotFoundError as e:
            logger.error(f"加载设置时出错: {e}, 使用默认大小:50.0")
            self.pumping_people_font_size_SpinBox.setValue("50.0")
        except KeyError:
            logger.error(f"设置文件中缺少'foundation'键, 使用默认大小:50.0")
            self.pumping_people_font_size_SpinBox.setValue("50.0")
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

                    draw_pumping = pumping_people_settings.get("draw_pumping", self.default_settings["draw_pumping"])
                    if draw_pumping < 0 or draw_pumping >= self.pumping_Draw_comboBox.count():
                        logger.warning(f"无效的抽取方式索引: {draw_pumping}")
                        draw_pumping = self.default_settings["draw_pumping"]
                        
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

                    people_theme = pumping_people_settings.get("people_theme", self.default_settings["people_theme"])
                    if people_theme < 0 or people_theme >= self.pumping_people_theme_comboBox.count():
                        logger.warning(f"无效的人数/组数样式索引: {people_theme}")
                        people_theme = self.default_settings["people_theme"]

                    # 加载语音设置
                    voice_volume = pumping_people_settings.get("voice_volume", self.default_settings["voice_volume"])
                    if voice_volume < 0 or voice_volume > 100:
                        logger.warning(f"无效的音量值: {voice_volume}")
                        voice_volume = self.default_settings["voice_volume"]

                    voice_speed = pumping_people_settings.get("voice_speed", self.default_settings["voice_speed"])
                    if voice_speed < 1 or voice_speed > 500:
                        logger.warning(f"无效的语速值: {voice_speed}")
                        voice_speed = self.default_settings["voice_speed"]

                    # 加载系统音量设置
                    system_volume_enabled = pumping_people_settings.get("system_volume_enabled", self.default_settings["system_volume_enabled"])
                    system_volume_value = pumping_people_settings.get("system_volume_value", self.default_settings["system_volume_value"])

                    # 加载随机组员显示设置
                    show_random_member = pumping_people_settings.get("show_random_member", self.default_settings["show_random_member"])
                    random_member_format = pumping_people_settings.get("random_member_format", self.default_settings["random_member_format"])

                    # 加载动画设置
                    animation_interval = pumping_people_settings.get("animation_interval", self.default_settings["animation_interval"])
                    animation_auto_play = pumping_people_settings.get("animation_auto_play", self.default_settings["animation_auto_play"])

                    # 加载动画音乐设置
                    animation_music_enabled = pumping_people_settings.get("animation_music_enabled", self.default_settings["animation_music_enabled"])
                    result_music_enabled = pumping_people_settings.get("result_music_enabled", self.default_settings["result_music_enabled"])
                    animation_music_volume = pumping_people_settings.get("animation_music_volume", self.default_settings["animation_music_volume"])
                    result_music_volume = pumping_people_settings.get("result_music_volume", self.default_settings["result_music_volume"])
                    music_fade_in = pumping_people_settings.get("music_fade_in", self.default_settings["music_fade_in"])
                    music_fade_out = pumping_people_settings.get("music_fade_out", self.default_settings["music_fade_out"])

                    
                    self.pumping_people_Draw_comboBox.setCurrentIndex(draw_mode)
                    self.pumping_Draw_comboBox.setCurrentIndex(draw_pumping)
                    self.pumping_people_font_size_SpinBox.setValue(font_size)
                    self.pumping_people_Animation_comboBox.setCurrentIndex(animation_mode)
                    self.pumping_people_Voice_switch.setChecked(voice_enabled)
                    self.pumping_people_student_id_comboBox.setCurrentIndex(student_id)
                    self.pumping_people_student_name_comboBox.setCurrentIndex(student_name)
                    self.pumping_people_theme_comboBox.setCurrentIndex(people_theme)
                    self.pumping_people_voice_volume_SpinBox.setValue(voice_volume)
                    self.pumping_people_voice_speed_SpinBox.setValue(voice_speed)
                    self.pumping_people_system_volume_switch.setChecked(system_volume_enabled)
                    self.pumping_people_system_volume_SpinBox.setValue(system_volume_value)
                    self.show_random_member_checkbox.setChecked(show_random_member)
                    self.random_member_format_comboBox.setCurrentIndex(random_member_format)
                    self.pumping_people_Animation_interval_SpinBox.setValue(animation_interval)
                    self.pumping_people_Animation_auto_play_SpinBox.setValue(animation_auto_play)
                    self.pumping_people_Animation_music_switch.setChecked(animation_music_enabled)
                    self.pumping_people_result_music_switch.setChecked(result_music_enabled)
                    self.pumping_people_Animation_music_volume_SpinBox.setValue(animation_music_volume)
                    self.pumping_people_result_music_volume_SpinBox.setValue(result_music_volume)
                    self.pumping_people_music_fade_in_SpinBox.setValue(music_fade_in)
                    self.pumping_people_music_fade_out_SpinBox.setValue(music_fade_out)
            else:
                self.pumping_people_Draw_comboBox.setCurrentIndex(self.default_settings["draw_mode"])
                self.pumping_Draw_comboBox.setCurrentIndex(self.default_settings["draw_pumping"])
                self.pumping_people_font_size_SpinBox.setValue(self.default_settings["font_size"])
                self.pumping_people_Animation_comboBox.setCurrentIndex(self.default_settings["animation_mode"])
                self.pumping_people_Voice_switch.setChecked(self.default_settings["voice_enabled"])
                self.pumping_people_student_id_comboBox.setCurrentIndex(self.default_settings["student_id"])
                self.pumping_people_student_name_comboBox.setCurrentIndex(self.default_settings["student_name"])
                self.pumping_people_theme_comboBox.setCurrentIndex(self.default_settings["people_theme"])
                self.pumping_people_voice_volume_SpinBox.setValue(self.default_settings["voice_volume"])
                self.pumping_people_voice_speed_SpinBox.setValue(self.default_settings["voice_speed"])
                self.pumping_people_system_volume_switch.setChecked(self.default_settings["system_volume_enabled"])
                self.pumping_people_system_volume_SpinBox.setValue(self.default_settings["system_volume_value"])
                self.show_random_member_checkbox.setChecked(self.default_settings["show_random_member"])
                self.random_member_format_comboBox.setCurrentIndex(self.default_settings["random_member_format"])
                self.pumping_people_Animation_interval_SpinBox.setValue(self.default_settings["animation_interval"])
                self.pumping_people_Animation_auto_play_SpinBox.setValue(self.default_settings["animation_auto_play"])
                self.pumping_people_Animation_music_switch.setChecked(self.default_settings["animation_music_enabled"])
                self.pumping_people_result_music_switch.setChecked(self.default_settings["result_music_enabled"])
                self.pumping_people_Animation_music_volume_SpinBox.setValue(self.default_settings["animation_music_volume"])
                self.pumping_people_result_music_volume_SpinBox.setValue(self.default_settings["result_music_volume"])
                self.pumping_people_music_fade_in_SpinBox.setValue(self.default_settings["music_fade_in"])
                self.pumping_people_music_fade_out_SpinBox.setValue(self.default_settings["music_fade_out"])
                self.save_settings()
        except Exception as e:
            logger.error(f"加载设置时出错: {e}")
            self.pumping_people_Draw_comboBox.setCurrentIndex(self.default_settings["draw_mode"])
            self.pumping_Draw_comboBox.setCurrentIndex(self.default_settings["draw_pumping"])
            self.pumping_people_font_size_SpinBox.setValue(self.default_settings["font_size"])
            self.pumping_people_Animation_comboBox.setCurrentIndex(self.default_settings["animation_mode"])
            self.pumping_people_Voice_switch.setChecked(self.default_settings["voice_enabled"])
            self.pumping_people_student_id_comboBox.setCurrentIndex(self.default_settings["student_id"])
            self.pumping_people_student_name_comboBox.setCurrentIndex(self.default_settings["student_name"])
            self.pumping_people_theme_comboBox.setCurrentIndex(self.default_settings["people_theme"])
            self.pumping_people_voice_volume_SpinBox.setValue(self.default_settings["voice_volume"])
            self.pumping_people_voice_speed_SpinBox.setValue(self.default_settings["voice_speed"])
            self.pumping_people_system_volume_switch.setChecked(self.default_settings["system_volume_enabled"])
            self.pumping_people_system_volume_SpinBox.setValue(self.default_settings["system_volume_value"])
            self.show_random_member_checkbox.setChecked(self.default_settings["show_random_member"])
            self.random_member_format_comboBox.setCurrentIndex(self.default_settings["random_member_format"])
            self.pumping_people_Animation_interval_SpinBox.setValue(self.default_settings["animation_interval"])
            self.pumping_people_Animation_auto_play_SpinBox.setValue(self.default_settings["animation_auto_play"])
            self.pumping_people_Animation_music_switch.setChecked(self.default_settings["animation_music_enabled"])
            self.pumping_people_result_music_switch.setChecked(self.default_settings["result_music_enabled"])
            self.pumping_people_Animation_music_volume_SpinBox.setValue(self.default_settings["animation_music_volume"])
            self.pumping_people_result_music_volume_SpinBox.setValue(self.default_settings["result_music_volume"])
            self.pumping_people_music_fade_in_SpinBox.setValue(self.default_settings["music_fade_in"])
            self.pumping_people_music_fade_out_SpinBox.setValue(self.default_settings["music_fade_out"])

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
        pumping_people_settings["draw_pumping"] = self.pumping_Draw_comboBox.currentIndex()
        pumping_people_settings["animation_mode"] = self.pumping_people_Animation_comboBox.currentIndex()
        pumping_people_settings["voice_enabled"] = self.pumping_people_Voice_switch.isChecked()
        pumping_people_settings["student_id"] = self.pumping_people_student_id_comboBox.currentIndex()
        pumping_people_settings["student_name"] = self.pumping_people_student_name_comboBox.currentIndex()
        pumping_people_settings["people_theme"] = self.pumping_people_theme_comboBox.currentIndex()
        pumping_people_settings["voice_volume"] = self.pumping_people_voice_volume_SpinBox.value()
        pumping_people_settings["voice_speed"] = self.pumping_people_voice_speed_SpinBox.value()
        pumping_people_settings["system_volume_enabled"] = self.pumping_people_system_volume_switch.isChecked()
        pumping_people_settings["system_volume_value"] = self.pumping_people_system_volume_SpinBox.value()
        pumping_people_settings["show_random_member"] = self.show_random_member_checkbox.isChecked()
        pumping_people_settings["random_member_format"] = self.random_member_format_comboBox.currentIndex()
        pumping_people_settings["animation_interval"] = self.pumping_people_Animation_interval_SpinBox.value()
        pumping_people_settings["animation_auto_play"] = self.pumping_people_Animation_auto_play_SpinBox.value()
        pumping_people_settings["animation_music_enabled"] = self.pumping_people_Animation_music_switch.isChecked()
        pumping_people_settings["result_music_enabled"] = self.pumping_people_result_music_switch.isChecked()
        pumping_people_settings["animation_music_volume"] = self.pumping_people_Animation_music_volume_SpinBox.value()
        pumping_people_settings["result_music_volume"] = self.pumping_people_result_music_volume_SpinBox.value()
        pumping_people_settings["music_fade_in"] = self.pumping_people_music_fade_in_SpinBox.value()
        pumping_people_settings["music_fade_out"] = self.pumping_people_music_fade_out_SpinBox.value()

        # 保存字体大小
        try:
            font_size = float(self.pumping_people_font_size_SpinBox.value())
            if 30.0 <= font_size <= 200.0:
                pumping_people_settings["font_size"] = font_size
            # else:
            #     logger.warning(f"字体大小超出范围: {font_size}")
        except ValueError:
            # logger.warning(f"无效的字体大小输入: {self.pumping_people_font_size_edit.text()}")
            pass
        
        os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
        with open(self.settings_file, 'w', encoding='utf-8') as f:
            json.dump(existing_settings, f, indent=4)
