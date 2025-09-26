from qfluentwidgets import *
from qfluentwidgets import FluentIcon as FIF
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

import json
import os
from pathlib import Path
from loguru import logger

from app.common.config import get_theme_icon, load_custom_font
from app.common.path_utils import path_manager
from app.common.path_utils import open_file, ensure_dir
from app.view.main_page import pumping_people


class pumping_people_SettinsCard(GroupHeaderCardWidget):
    # 定义信号，用于通知设置已更新
    settings_updated = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("点名设置")
        self.setBorderRadius(8)
        self.settings_file = path_manager.get_settings_path()
        self.default_settings = {
            "font_size": 50,
            "max_draw_count": 5,
            "Draw_pumping": 1,
            "draw_mode": 1,
            "clear_mode": 0,
            "draw_pumping": 0,
            "pumping_people_auto_clear": False,
            "animation_mode": 0,
            "student_id": 0,
            "student_name": 0,
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
            "display_format": 0,
            "animation_color": 0,
            "show_student_image": False
        }

        self.pumping_people_Draw_comboBox = ComboBox()
        self.pumping_Draw_comboBox = ComboBox()
        self.pumping_people_Animation_comboBox = ComboBox()
        self.pumping_people_student_id_comboBox = ComboBox()
        self.pumping_people_student_name_comboBox = ComboBox()
        self.pumping_people_font_size_SpinBox = DoubleSpinBox()
        self.show_random_member_checkbox = SwitchButton()
        self.pumping_people_Animation_interval_SpinBox = SpinBox()
        self.pumping_people_Animation_auto_play_SpinBox = SpinBox()
        
        # 抽取模式下拉框
        self.pumping_people_Draw_comboBox.addItems(["重复抽取", "不重复抽取", "半重复抽取"])
        self.pumping_people_Draw_comboBox.currentIndexChanged.connect(self.on_draw_mode_changed)
        self.pumping_people_Draw_comboBox.setFont(QFont(load_custom_font(), 12))

        # 清除抽取记录方式下拉框
        self.pumping_people_Clear_comboBox = ComboBox()
        self.pumping_people_Clear_comboBox.addItems(["重启后清除", "直到全部抽取完", "无需清除"])
        self.pumping_people_Clear_comboBox.currentIndexChanged.connect(self.save_settings)
        self.pumping_people_Clear_comboBox.setFont(QFont(load_custom_font(), 12))

        # 抽取后定时清除开关
        self.pumping_people_auto_clear_checkbox = SwitchButton()
        self.pumping_people_auto_clear_checkbox.setOnText("开启")
        self.pumping_people_auto_clear_checkbox.setOffText("关闭")
        self.pumping_people_auto_clear_checkbox.checkedChanged.connect(self.save_settings)
        self.pumping_people_auto_clear_checkbox.setFont(QFont(load_custom_font(), 12))

        # 定时清理临时记录时间
        self.pumping_people_auto_play_count_SpinBox = SpinBox()
        self.pumping_people_auto_play_count_SpinBox.setRange(1, 86400)
        self.pumping_people_auto_play_count_SpinBox.setValue(self.default_settings["max_draw_count"])
        self.pumping_people_auto_play_count_SpinBox.setSingleStep(1)
        self.pumping_people_auto_play_count_SpinBox.setSuffix("秒")
        self.pumping_people_auto_play_count_SpinBox.valueChanged.connect(self.save_settings)
        self.pumping_people_auto_play_count_SpinBox.setFont(QFont(load_custom_font(), 12))

        # 不重复抽取模式下的数字一个人的最多重复次数
        self.Draw_pumping_SpinBox = SpinBox()
        self.Draw_pumping_SpinBox.setRange(0, 100)
        self.Draw_pumping_SpinBox.setValue(self.default_settings["Draw_pumping"])
        self.Draw_pumping_SpinBox.setSingleStep(1)
        self.Draw_pumping_SpinBox.setSuffix("次")
        self.Draw_pumping_SpinBox.valueChanged.connect(self.save_settings)
        self.Draw_pumping_SpinBox.setFont(QFont(load_custom_font(), 12))

        # 抽取方式下拉框
        self.pumping_Draw_comboBox.addItems(["可预测抽取", "不可预测抽取", "公平可预测抽取", "公平不可预测抽取"])
        self.pumping_Draw_comboBox.currentIndexChanged.connect(self.save_settings)
        self.pumping_Draw_comboBox.setFont(QFont(load_custom_font(), 12))

        # 字体大小
        self.pumping_people_font_size_SpinBox.setRange(30, 200)
        self.pumping_people_font_size_SpinBox.setValue(50)
        self.pumping_people_font_size_SpinBox.setSingleStep(5)
        self.pumping_people_font_size_SpinBox.setDecimals(0)
        self.pumping_people_font_size_SpinBox.valueChanged.connect(self.save_settings)
        self.pumping_people_font_size_SpinBox.setFont(QFont(load_custom_font(), 12))

        # 动画模式下拉框
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
        self.pumping_people_student_id_comboBox.addItems(["⌈01⌋", "⌈ 1 ⌋"])
        self.pumping_people_student_id_comboBox.currentIndexChanged.connect(self.save_settings)
        self.pumping_people_student_id_comboBox.setFont(QFont(load_custom_font(), 12))

        # 姓名格式下拉框
        self.pumping_people_student_name_comboBox.addItems(["⌈张  三⌋", "⌈ 张三 ⌋"])
        self.pumping_people_student_name_comboBox.currentIndexChanged.connect(self.save_settings)
        self.pumping_people_student_name_comboBox.setFont(QFont(load_custom_font(), 12))

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

        # 显示格式
        self.pumping_people_display_format_comboBox = ComboBox()
        self.pumping_people_display_format_comboBox.addItems([
            "学号+姓名",
            "姓名",
            "学号"
        ])
        self.pumping_people_display_format_comboBox.setCurrentIndex(0)
        self.pumping_people_display_format_comboBox.currentIndexChanged.connect(self.save_settings)
        self.pumping_people_display_format_comboBox.setFont(QFont(load_custom_font(), 12))

        # 随机颜色
        self.pumping_people_student_name_color_comboBox = ComboBox()
        self.pumping_people_student_name_color_comboBox.addItems([
            "关闭",
            "随机颜色",
            "固定颜色"
        ])
        self.pumping_people_student_name_color_comboBox.setCurrentIndex(0)
        self.pumping_people_student_name_color_comboBox.currentIndexChanged.connect(self.save_settings)
        self.pumping_people_student_name_color_comboBox.setFont(QFont(load_custom_font(), 12))

        # 固定颜色按钮-动画
        self.pumping_people_animation_color_fixed_dialog_button = PushButton("动画固定颜色")
        self.pumping_people_animation_color_fixed_dialog_button.setFont(QFont(load_custom_font(), 12))
        self.pumping_people_animation_color_fixed_dialog_button.clicked.connect(lambda: self.on_color_animation_dialog())

        # 固定颜色按钮-结果
        self.pumping_people_result_color_fixed_dialog_button = PushButton("结果固定颜色")
        self.pumping_people_result_color_fixed_dialog_button.setFont(QFont(load_custom_font(), 12))
        self.pumping_people_result_color_fixed_dialog_button.clicked.connect(lambda: self.on_color_result_dialog())

        # 奖品图片开关
        self.pumping_people_show_image_switch = SwitchButton()
        self.pumping_people_show_image_switch.setOnText("开启")
        self.pumping_people_show_image_switch.setOffText("关闭")
        self.pumping_people_show_image_switch.checkedChanged.connect(self.save_settings)
        self.pumping_people_show_image_switch.setFont(QFont(load_custom_font(), 12))

        # 学生图片文件夹
        self.pumping_people_image_path_button = PushButton("学生图片文件夹")
        self.pumping_people_image_path_button.setFont(QFont(load_custom_font(), 12))
        self.pumping_people_image_path_button.clicked.connect(lambda: self.open_image_path())

        # 添加组件到分组中
        # 抽取模式设置
        self.addGroup(get_theme_icon("ic_fluent_arrow_sync_20_filled"), "抽取模式", "选择抽取模式", self.pumping_people_Draw_comboBox)
        self.addGroup(get_theme_icon("ic_fluent_arrow_sync_20_filled"), "清除抽取记录方式", "配置临时记录清理方式", self.pumping_people_Clear_comboBox)
        self.addGroup(get_theme_icon("ic_fluent_calendar_week_numbers_20_filled"), "半重复抽取次数", "一轮中抽取最大次数", self.Draw_pumping_SpinBox)
        self.addGroup(get_theme_icon("ic_fluent_timer_off_20_filled"), "抽取后定时清除", "抽取后是否自动清除临时记录", self.pumping_people_auto_clear_checkbox) 
        self.addGroup(get_theme_icon("ic_fluent_timer_off_20_filled"), "抽取后定时清除时间", "配置临时记录清理时间(1-86400)", self.pumping_people_auto_play_count_SpinBox)
        self.addGroup(get_theme_icon("ic_fluent_arrow_sync_20_filled"), "抽取方式", "选择具体的抽取执行方式", self.pumping_Draw_comboBox)
        
        # 显示格式设置
        self.addGroup(get_theme_icon("ic_fluent_text_font_size_20_filled"), "字体大小", "调整抽取结果显示的字体大小", self.pumping_people_font_size_SpinBox)
        self.addGroup(get_theme_icon("ic_fluent_number_symbol_square_20_filled"), "学号格式", "设置学号的显示格式规范", self.pumping_people_student_id_comboBox)
        self.addGroup(get_theme_icon("ic_fluent_rename_20_filled"), "姓名格式", "配置姓名的显示格式规范", self.pumping_people_student_name_comboBox)
        self.addGroup(get_theme_icon("ic_fluent_people_eye_20_filled"), "显示格式", "选择抽取结果的展示格式", self.pumping_people_display_format_comboBox)
        self.addGroup(get_theme_icon("ic_fluent_person_20_filled"), "显示随机组员", "抽取小组时是否同步显示组员信息", self.show_random_member_checkbox)
        self.addGroup(get_theme_icon("ic_fluent_people_eye_20_filled"), "组员显示格式", "配置随机组员信息的显示格式", self.random_member_format_comboBox)
        
        # 颜色设置
        self.addGroup(get_theme_icon("ic_fluent_people_eye_20_filled"), "动画/结果颜色", "配置动画和结果的字体颜色主题", self.pumping_people_student_name_color_comboBox)
        self.addGroup(get_theme_icon("ic_fluent_people_eye_20_filled"), "动画颜色", "自定义动画播放时的字体颜色", self.pumping_people_animation_color_fixed_dialog_button)
        self.addGroup(get_theme_icon("ic_fluent_people_eye_20_filled"), "结果颜色", "自定义抽取结果展示的字体颜色", self.pumping_people_result_color_fixed_dialog_button)
        
        # 图片显示设置
        self.addGroup(get_theme_icon("ic_fluent_people_eye_20_filled"), "学生图片", "是否在抽取时显示学生照片", self.pumping_people_show_image_switch)
        self.addGroup(get_theme_icon("ic_fluent_people_eye_20_filled"), "学生图片文件夹", "管理学生照片目录（图片名需与学生姓名对应）", self.pumping_people_image_path_button)
        
        # 动画设置
        self.addGroup(get_theme_icon("ic_fluent_calendar_video_20_filled"), "动画模式", "选择抽取过程的动画播放模式", self.pumping_people_Animation_comboBox)
        self.addGroup(get_theme_icon("ic_fluent_calendar_video_20_filled"), "动画间隔", "调整动画播放的速度间隔（适用于1、2号模式）", self.pumping_people_Animation_interval_SpinBox)
        self.addGroup(get_theme_icon("ic_fluent_calendar_video_20_filled"), "自动播放次数", "设置动画自动重复播放的次数（适用于2号模式）", self.pumping_people_Animation_auto_play_SpinBox)
        
        # 音乐设置
        self.addGroup(get_theme_icon("ic_fluent_music_note_2_20_filled"), "动画音乐", "启用抽取动画的背景音乐播放", self.pumping_people_Animation_music_switch)
        self.addGroup(get_theme_icon("ic_fluent_music_note_2_20_filled"), "结果音乐", "启用抽取结果的背景音乐播放", self.pumping_people_result_music_switch)
        self.addGroup(get_theme_icon("ic_fluent_music_note_2_20_filled"), "动画音乐文件夹", "管理动画背景音乐文件目录", self.pumping_people_Animation_music_path_button)
        self.addGroup(get_theme_icon("ic_fluent_music_note_2_20_filled"), "结果音乐文件夹", "管理结果背景音乐文件目录", self.pumping_people_result_music_path_button)
        self.addGroup(get_theme_icon("ic_fluent_music_note_2_20_filled"), "动画音乐音量", "调整动画背景音乐的播放音量", self.pumping_people_Animation_music_volume_SpinBox)
        self.addGroup(get_theme_icon("ic_fluent_music_note_2_20_filled"), "结果音乐音量", "调整结果背景音乐的播放音量", self.pumping_people_result_music_volume_SpinBox)
        self.addGroup(get_theme_icon("ic_fluent_music_note_2_20_filled"), "动画/结果音乐渐入时间", "设置音乐淡入效果的持续时间", self.pumping_people_music_fade_in_SpinBox)
        self.addGroup(get_theme_icon("ic_fluent_music_note_2_20_filled"), "动画/结果音乐渐出时间", "设置音乐淡出效果的持续时间", self.pumping_people_music_fade_out_SpinBox)

        self.load_settings()  # 加载设置
        self.save_settings()  # 保存设置

    def on_pumping_people_Voice_switch_changed(self, checked):
        self.save_settings()

    # 🌟 小鸟游星野：动画颜色选择器 ⭐
    def on_color_animation_dialog(self):
        # ✨ 星穹铁道白露：让颜色选择器在新窗口飞翔 ~
        color_type = "animation"
        self.load_color_settings()
        pumping_people_animation_color_fixed_dialog = ColorDialog(QColor(self.pumping_people_animation_color_fixed), "动画颜色", self, enableAlpha=False)
        pumping_people_animation_color_fixed_dialog.setModal(False)
        pumping_people_animation_color_fixed_dialog.colorChanged.connect(lambda color: self.save_color_settings(color.name(), color_type))
        pumping_people_animation_color_fixed_dialog.setFont(QFont(load_custom_font(), 12))
        pumping_people_animation_color_fixed_dialog.show()

    def on_color_result_dialog(self):
        # ✨ 星穹铁道白露：结果颜色选择器也需要自由 ~
        color_type = "result"
        self.load_color_settings()
        pumping_people_result_color_fixed_dialog = ColorDialog(QColor(self.pumping_people_result_color_fixed), "结果颜色", self, enableAlpha=False)
        pumping_people_result_color_fixed_dialog.setModal(False)
        pumping_people_result_color_fixed_dialog.colorChanged.connect(lambda color: self.save_color_settings(color.name(), color_type))
        pumping_people_result_color_fixed_dialog.setFont(QFont(load_custom_font(), 12))
        pumping_people_result_color_fixed_dialog.show()

    def open_music_path(self, button):
        bgm_animation_path = path_manager.get_resource_path('music/pumping_people', 'Animation_music')
        bgm_result_path = path_manager.get_resource_path('music/pumping_people', 'result_music')
        ensure_dir(bgm_animation_path)
        ensure_dir(bgm_result_path)
        # 星野引导：根据按钮选择打开对应的音乐文件夹 (๑•̀ㅂ•́)و✧
        if button == 'Animation_music':
            # 白露提示：确保路径是文件夹格式再打开哦～
            self.open_folder(str(bgm_animation_path))
        elif button == 'result_music':
            # 星野守护：用绝对路径确保文件夹正确打开～
            self.open_folder(str(bgm_result_path))

    def open_image_path(self):
        image_path = path_manager.get_resource_path('images', 'students')
        ensure_dir(image_path)
        # 星野守护：用绝对路径确保文件夹正确打开～
        self.open_folder(str(image_path))

    def open_folder(self, path):
        """跨平台打开文件夹的方法"""
        import subprocess
        import platform
        
        try:
            system = platform.system()
            if system == 'Windows':
                os.startfile(path)
            elif system == 'Darwin':  # macOS
                subprocess.run(['open', path], check=True)
            elif system == 'Linux':
                subprocess.run(['xdg-open', path], check=True)
            else:
                logger.warning(f"不支持的操作系统: {system}")
        except Exception as e:
            logger.error(f"打开文件夹失败: {e}")

    def apply_font_size(self):
        try:
            font_size_str = self.pumping_people_font_size_SpinBox.value()
            font_size = int(font_size_str)
            if 30 <= font_size <= 200:
                # 格式化保留一位小数
                self.pumping_people_font_size_SpinBox.setValue(font_size)
                self.save_settings()
                InfoBar.success(
                    title='设置成功',
                    content=f"设置字体大小为: {font_size}",
                    orient=Qt.Horizontal, parent=self, isClosable=True, duration=3000, position=InfoBarPosition.TOP
                )
            else:
                logger.warning(f"字体大小超出范围: {font_size}")
                InfoBar.warning(
                    title='字体大小超出范围',
                    content=f"字体大小超出范围，请输入30-200之间的数字: {font_size}",
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
            self.pumping_people_font_size_SpinBox.setValue("50")
        except FileNotFoundError as e:
            logger.error(f"加载设置时出错: {e}, 使用默认大小:50")
            self.pumping_people_font_size_SpinBox.setValue("50")
        except KeyError:
            logger.error(f"设置文件中缺少'foundation'键, 使用默认大小:50")
            self.pumping_people_font_size_SpinBox.setValue("50")
        self.save_settings()
        self.load_settings()
        
    def load_settings(self):
        try:
            if path_manager.file_exists(self.settings_file):
                with open_file(self.settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    pumping_people_settings = settings.get("pumping_people", {})

                    font_size = pumping_people_settings.get("font_size", self.default_settings["font_size"])
                    
                    # 直接使用索引值
                    draw_mode = pumping_people_settings.get("draw_mode", self.default_settings["draw_mode"])
                    if draw_mode < 0 or draw_mode >= self.pumping_people_Draw_comboBox.count():
                        logger.warning(f"无效的抽取模式索引: {draw_mode}")
                        draw_mode = self.default_settings["draw_mode"]
                        
                    clear_mode = pumping_people_settings.get("clear_mode", self.default_settings["clear_mode"])
                    if clear_mode < 0 or clear_mode >= self.pumping_people_Clear_comboBox.count():
                        logger.warning(f"无效的清除抽取记录方式索引: {clear_mode}")
                        clear_mode = self.default_settings["clear_mode"]
                        
                    draw_pumping = pumping_people_settings.get("draw_pumping", self.default_settings["draw_pumping"])
                    if draw_pumping < 0 or draw_pumping >= self.pumping_Draw_comboBox.count():
                        logger.warning(f"无效的抽取方式索引: {draw_pumping}")
                        draw_pumping = self.default_settings["draw_pumping"]
                        
                    animation_mode = pumping_people_settings.get("animation_mode", self.default_settings["animation_mode"])
                    if animation_mode < 0 or animation_mode >= self.pumping_people_Animation_comboBox.count():
                        logger.warning(f"无效的动画模式索引: {animation_mode}")
                        animation_mode = self.default_settings["animation_mode"]

                    student_id = pumping_people_settings.get("student_id", self.default_settings["student_id"])
                    if student_id < 0 or student_id >= self.pumping_people_student_id_comboBox.count():
                        logger.warning(f"无效的学号格式索引: {student_id}")
                        student_id = self.default_settings["student_id"]
                    
                    student_name = pumping_people_settings.get("student_name", self.default_settings["student_name"])
                    if student_name < 0 or student_name >= self.pumping_people_student_name_comboBox.count():
                        logger.warning(f"无效的姓名格式索引: {student_name}")
                        student_name = self.default_settings["student_name"]

                    # 加载随机组员显示设置
                    show_random_member = pumping_people_settings.get("show_random_member", self.default_settings["show_random_member"])
                    random_member_format = pumping_people_settings.get("random_member_format", self.default_settings["random_member_format"])

                    # 不重复抽取模式下的数字一个人的最多重复次数
                    Draw_pumping = pumping_people_settings.get("Draw_pumping", self.default_settings["Draw_pumping"])

                    # 最大抽取次数设置
                    max_draw_count = pumping_people_settings.get("max_draw_count", self.default_settings["max_draw_count"])

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

                    # 加载抽取结果显示格式
                    display_format = pumping_people_settings.get("display_format", self.default_settings["display_format"])
                    if display_format < 0 or display_format >= self.pumping_people_display_format_comboBox.count():
                        logger.warning(f"无效的抽取结果显示格式索引: {display_format}")
                        display_format = self.default_settings["display_format"]

                    # 动画/结果颜色
                    animation_color = pumping_people_settings.get("animation_color", self.default_settings["animation_color"])
                    if animation_color < 0 or animation_color >= self.pumping_people_student_name_color_comboBox.count():
                        logger.warning(f"无效的动画/结果颜色索引: {animation_color}")
                        animation_color = self.default_settings["animation_color"]

                    # 加载学生图片开关
                    show_student_image = pumping_people_settings.get("show_student_image", self.default_settings["show_student_image"])

                    self.pumping_people_Draw_comboBox.setCurrentIndex(draw_mode)
                    self.pumping_people_Clear_comboBox.setCurrentIndex(clear_mode)
                    self.pumping_people_auto_play_count_SpinBox.setValue(max_draw_count)
                    self.Draw_pumping_SpinBox.setValue(Draw_pumping)
                    self.pumping_Draw_comboBox.setCurrentIndex(draw_pumping)
                    self.pumping_people_font_size_SpinBox.setValue(font_size)
                    self.pumping_people_Animation_comboBox.setCurrentIndex(animation_mode)
                    self.pumping_people_student_id_comboBox.setCurrentIndex(student_id)
                    self.pumping_people_student_name_comboBox.setCurrentIndex(student_name)
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
                    self.pumping_people_display_format_comboBox.setCurrentIndex(display_format)
                    self.pumping_people_student_name_color_comboBox.setCurrentIndex(animation_color)
                    self.pumping_people_show_image_switch.setChecked(show_student_image)
                    
                    # 加载设置后应用抽取模式逻辑
                    self.on_draw_mode_changed()
            else:
                self.pumping_people_Draw_comboBox.setCurrentIndex(self.default_settings["draw_mode"])
                self.pumping_people_Clear_comboBox.setCurrentIndex(self.default_settings["clear_mode"])
                self.Draw_pumping_SpinBox.setValue(self.default_settings["Draw_pumping"])
                
                # 加载默认设置后应用抽取模式逻辑
                self.on_draw_mode_changed()
                
                self.pumping_people_auto_play_count_SpinBox.setValue(self.default_settings["max_draw_count"])
                self.pumping_Draw_comboBox.setCurrentIndex(self.default_settings["draw_pumping"])
                self.pumping_people_font_size_SpinBox.setValue(self.default_settings["font_size"])
                self.pumping_people_Animation_comboBox.setCurrentIndex(self.default_settings["animation_mode"])
                self.pumping_people_student_id_comboBox.setCurrentIndex(self.default_settings["student_id"])
                self.pumping_people_student_name_comboBox.setCurrentIndex(self.default_settings["student_name"])
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
                self.pumping_people_display_format_comboBox.setCurrentIndex(self.default_settings["display_format"])
                self.pumping_people_student_name_color_comboBox.setCurrentIndex(self.default_settings["animation_color"])
                self.pumping_people_show_image_switch.setChecked(self.default_settings["show_student_image"])
                self.save_settings()
        except Exception as e:
            logger.error(f"加载设置时出错: {e}")
            self.pumping_people_Draw_comboBox.setCurrentIndex(self.default_settings["draw_mode"])
            self.pumping_people_Clear_comboBox.setCurrentIndex(self.default_settings["clear_mode"])
            self.pumping_people_auto_play_count_SpinBox.setValue(self.default_settings["max_draw_count"])
            self.Draw_pumping_SpinBox.setValue(self.default_settings["Draw_pumping"])
            self.pumping_Draw_comboBox.setCurrentIndex(self.default_settings["draw_pumping"])
            self.pumping_people_font_size_SpinBox.setValue(self.default_settings["font_size"])
            self.pumping_people_Animation_comboBox.setCurrentIndex(self.default_settings["animation_mode"])
            self.pumping_people_student_id_comboBox.setCurrentIndex(self.default_settings["student_id"])
            self.pumping_people_student_name_comboBox.setCurrentIndex(self.default_settings["student_name"])
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
            self.pumping_people_display_format_comboBox.setCurrentIndex(self.default_settings["display_format"])
            self.pumping_people_student_name_color_comboBox.setCurrentIndex(self.default_settings["animation_color"])
            self.pumping_people_show_image_switch.setChecked(self.default_settings["show_student_image"])
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
        
        # 更新pumping_people部分的所有设置
        if "pumping_people" not in existing_settings:
            existing_settings["pumping_people"] = {}
            
        pumping_people_settings = existing_settings["pumping_people"]
        # 只保存索引值
        pumping_people_settings["draw_mode"] = self.pumping_people_Draw_comboBox.currentIndex()
        pumping_people_settings["clear_mode"] = self.pumping_people_Clear_comboBox.currentIndex()
        pumping_people_settings["max_draw_count"] = self.pumping_people_auto_play_count_SpinBox.value()
        pumping_people_settings["Draw_pumping"] = self.Draw_pumping_SpinBox.value()
        pumping_people_settings["draw_pumping"] = self.pumping_Draw_comboBox.currentIndex()
        pumping_people_settings["animation_mode"] = self.pumping_people_Animation_comboBox.currentIndex()
        pumping_people_settings["student_id"] = self.pumping_people_student_id_comboBox.currentIndex()
        pumping_people_settings["student_name"] = self.pumping_people_student_name_comboBox.currentIndex()
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
        pumping_people_settings["display_format"] = self.pumping_people_display_format_comboBox.currentIndex()
        pumping_people_settings["animation_color"] = self.pumping_people_student_name_color_comboBox.currentIndex()
        pumping_people_settings["show_student_image"] = self.pumping_people_show_image_switch.isChecked()

        # 保存字体大小
        try:
            font_size = int(self.pumping_people_font_size_SpinBox.value())
            if 30 <= font_size <= 200:
                pumping_people_settings["font_size"] = font_size
            # else:
            #     logger.warning(f"字体大小超出范围: {font_size}")
        except ValueError:
            # logger.warning(f"无效的字体大小输入: {self.pumping_people_font_size_edit.text()}")
            pass
        
        # 检查是否需要同步到instant_draw设置
        sync_to_instant_draw = False
        if "instant_draw" in existing_settings:
            instant_draw_settings = existing_settings["instant_draw"]
            # 检查是否开启了跟随点名设置
            if instant_draw_settings.get("follow_roll_call", False):
                sync_to_instant_draw = True
        
        # 如果需要同步，则更新instant_draw设置
        if sync_to_instant_draw:
            if "instant_draw" not in existing_settings:
                existing_settings["instant_draw"] = {}
                
            instant_draw_settings = existing_settings["instant_draw"]
            
            # 定义需要同步的键值映射
            sync_mapping = {
                "draw_mode": "draw_mode",
                "draw_pumping": "draw_pumping",
                "animation_mode": "animation_mode",
                "student_id": "student_id",
                "student_name": "student_name",
                "show_random_member": "show_random_member",
                "random_member_format": "random_member_format",
                "animation_interval": "animation_interval",
                "animation_auto_play": "animation_auto_play",
                "animation_music_enabled": "animation_music_enabled",
                "result_music_enabled": "result_music_enabled",
                "animation_music_volume": "animation_music_volume",
                "result_music_volume": "result_music_volume",
                "music_fade_in": "music_fade_in",
                "music_fade_out": "music_fade_out",
                "display_format": "display_format",
                "animation_color": "animation_color",
                "show_student_image": "show_student_image",
                "font_size": "font_size",
                "max_draw_count": "max_draw_count"
            }
            
            # 从pumping_people同步设置到instant_draw
            for pumping_key, instant_key in sync_mapping.items():
                if pumping_key in pumping_people_settings:
                    instant_draw_settings[instant_key] = pumping_people_settings[pumping_key]
        
        ensure_dir(Path(self.settings_file).parent)
        with open_file(self.settings_file, 'w', encoding='utf-8') as f:
            json.dump(existing_settings, f, indent=4)
            
        # 如果同步了设置到instant_draw，则触发信号通知刷新UI
        if sync_to_instant_draw:
            self.settings_updated.emit()

    def on_draw_mode_changed(self):
        """当抽取模式改变时的处理逻辑"""
        # 获取当前抽取模式索引
        draw_mode_index = self.pumping_people_Draw_comboBox.currentIndex()
        
        # 根据抽取模式设置不同的控制逻辑
        if draw_mode_index == 0:  # 重复抽取模式
            # 禁用清除抽取记录方式下拉框
            self.pumping_people_Clear_comboBox.setEnabled(False)
            # 清空当前选项
            self.pumping_people_Clear_comboBox.clear()
            self.pumping_people_Clear_comboBox.addItems(["重启后清除", "直到全部抽取完", "无需清除"])
            # 强制设置为"无需清除"（索引2）
            self.pumping_people_Clear_comboBox.setCurrentIndex(2)
            
            # 设置Draw_pumping_SpinBox为0并禁用
            self.Draw_pumping_SpinBox.setEnabled(False)
            self.Draw_pumping_SpinBox.setRange(0, 100)
            self.Draw_pumping_SpinBox.setValue(0)
            
        else:  # 不重复抽取模式或半重复抽取模式
            # 启用清除抽取记录方式下拉框
            self.pumping_people_Clear_comboBox.setEnabled(True)
            
            # 动态调整清除抽取记录方式下拉框的选项
            current_index = self.pumping_people_Clear_comboBox.currentIndex()
            
            # 清空当前选项
            self.pumping_people_Clear_comboBox.clear()
            
            # 添加前两个选项（不包含"无需清除"）
            self.pumping_people_Clear_comboBox.addItems(["重启后清除", "直到全部抽取完"])
            
            # 设置默认选择第一个选项
            self.pumping_people_Clear_comboBox.setCurrentIndex(0)
            
            # 根据具体模式设置Draw_pumping_SpinBox
            if draw_mode_index == 1:  # 不重复抽取模式
                # 设置Draw_pumping_SpinBox为1并禁用
                self.Draw_pumping_SpinBox.setEnabled(False)
                self.Draw_pumping_SpinBox.setRange(0, 100)
                self.Draw_pumping_SpinBox.setValue(1)
            else:  # 半重复抽取模式（索引2）
                # 设置Draw_pumping_SpinBox为2-100范围并启用
                self.Draw_pumping_SpinBox.setEnabled(True)
                self.Draw_pumping_SpinBox.setRange(2, 100)
                # 如果当前值小于2，则设置为2
                if self.Draw_pumping_SpinBox.value() < 2:
                    self.Draw_pumping_SpinBox.setValue(2)
        
        # 保存设置
        self.save_settings()

    # 读取颜色设置
    def load_color_settings(self):
        existing_settings = {}
        if path_manager.file_exists(self.settings_file):
            with open_file(self.settings_file, 'r', encoding='utf-8') as f:
                try:
                    existing_settings = json.load(f)
                except json.JSONDecodeError:
                    existing_settings = {}
        pumping_people_settings = existing_settings.get("pumping_people", {})
        self.pumping_people_animation_color_fixed = (pumping_people_settings.get("_animation_color", "#ffffff"))
        self.pumping_people_result_color_fixed = (pumping_people_settings.get("_result_color", "#ffffff"))

    def save_color_settings(self, color_name, color_type):
        # 先读取现有设置
        existing_settings = {}
        if path_manager.file_exists(self.settings_file):
            with open_file(self.settings_file, 'r', encoding='utf-8') as f:
                try:
                    existing_settings = json.load(f)
                except json.JSONDecodeError:
                    existing_settings = {}
        
        # 更新pumping_people部分的所有设置
        if "pumping_people" not in existing_settings:
            existing_settings["pumping_people"] = {}

        pumping_people_settings = existing_settings["pumping_people"]
        if color_type == "animation":
            pumping_people_settings["_animation_color"] = color_name
        elif color_type == "result":
            pumping_people_settings["_result_color"] = color_name
        
        ensure_dir(Path(self.settings_file).parent)
        with open_file(self.settings_file, 'w', encoding='utf-8') as f:
            json.dump(existing_settings, f, indent=4)