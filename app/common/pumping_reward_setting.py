from re import S
from qfluentwidgets import *
from qfluentwidgets import FluentIcon as FIF
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

import json
import os
from loguru import logger

from app.common.config import get_theme_icon, load_custom_font

class pumping_reward_SettinsCard(GroupHeaderCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("抽奖设置")
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
            "reward_theme": 0,
            "list_refresh_button": True,
            "prize_pools_quantity": True,
            "refresh_button": True,
            "voice_volume": 100,
            "voice_speed": 100,
            "animation_interval": 100,
            "animation_auto_play": 5,
        }

        self.pumping_reward_Draw_comboBox = ComboBox()
        self.pumping_reward_mode_Draw_comboBox = ComboBox()
        self.pumping_reward_Animation_comboBox = ComboBox()
        self.pumping_reward_theme_comboBox = ComboBox()
        self.pumping_reward_Voice_switch = SwitchButton()
        self.pumping_reward_voice_volume_SpinBox = SpinBox()
        self.pumping_reward_voice_speed_SpinBox = SpinBox()
        self.pumping_reward_font_size_SpinBox = DoubleSpinBox()
        self.pumping_reward_system_volume_switch = SwitchButton()
        self.pumping_reward_system_volume_SpinBox = SpinBox()
        self.pumping_reward_animation_interval_SpinBox = SpinBox()
        self.pumping_reward_animation_auto_play_SpinBox = SpinBox()
        
        # 抽取模式下拉框
        self.pumping_reward_Draw_comboBox.setFixedWidth(250)
        self.pumping_reward_Draw_comboBox.addItems(["重复抽取", "不重复抽取(直到软件重启)", "不重复抽取(直到抽完全部奖项)"])
        self.pumping_reward_Draw_comboBox.currentIndexChanged.connect(self.save_settings)
        self.pumping_reward_Draw_comboBox.setFont(QFont(load_custom_font(), 12))

        # 抽取方式下拉框
        self.pumping_reward_mode_Draw_comboBox.setFixedWidth(250)
        self.pumping_reward_mode_Draw_comboBox.addItems(["可预测抽取", "不可预测抽取"])
        self.pumping_reward_mode_Draw_comboBox.currentIndexChanged.connect(self.save_settings)
        self.pumping_reward_mode_Draw_comboBox.setFont(QFont(load_custom_font(), 12))

        # 字体大小
        self.pumping_reward_font_size_SpinBox.setRange(30.0, 200.0)
        self.pumping_reward_font_size_SpinBox.setValue(50.0)
        self.pumping_reward_font_size_SpinBox.setSingleStep(0.5)
        self.pumping_reward_font_size_SpinBox.setDecimals(1)
        self.pumping_reward_font_size_SpinBox.valueChanged.connect(self.save_settings)
        self.pumping_reward_font_size_SpinBox.setFont(QFont(load_custom_font(), 12))

        # 语音播放按钮
        self.pumping_reward_Voice_switch.setOnText("开启")
        self.pumping_reward_Voice_switch.setOffText("关闭")
        self.pumping_reward_Voice_switch.checkedChanged.connect(self.on_pumping_reward_Voice_switch_changed)
        self.pumping_reward_Voice_switch.setFont(QFont(load_custom_font(), 12))

        # 动画模式下拉框
        self.pumping_reward_Animation_comboBox.setFixedWidth(250)
        self.pumping_reward_Animation_comboBox.addItems(["手动停止动画", "自动播放完整动画", "直接显示结果"])
        self.pumping_reward_Animation_comboBox.currentIndexChanged.connect(lambda: self.save_settings())
        self.pumping_reward_Animation_comboBox.setFont(QFont(load_custom_font(), 12))

        # 动画间隔
        self.pumping_reward_animation_interval_SpinBox.setRange(100, 1000)
        self.pumping_reward_animation_interval_SpinBox.setValue(100)
        self.pumping_reward_animation_interval_SpinBox.setSingleStep(10)
        self.pumping_reward_animation_interval_SpinBox.setSuffix("ms")
        self.pumping_reward_animation_interval_SpinBox.valueChanged.connect(self.save_settings)
        self.pumping_reward_animation_interval_SpinBox.setFont(QFont(load_custom_font(), 12))

        # 自动播放次数
        self.pumping_reward_animation_auto_play_SpinBox.setRange(1, 50)
        self.pumping_reward_animation_auto_play_SpinBox.setValue(5)
        self.pumping_reward_animation_auto_play_SpinBox.setSingleStep(1)
        self.pumping_reward_animation_auto_play_SpinBox.setSuffix("次")
        self.pumping_reward_animation_auto_play_SpinBox.valueChanged.connect(self.save_settings)
        self.pumping_reward_animation_auto_play_SpinBox.setFont(QFont(load_custom_font(), 12))

        # 奖品量样式下拉框
        self.pumping_reward_theme_comboBox.setFixedWidth(150)
        self.pumping_reward_theme_comboBox.addItems(["总数 | 剩余", "总数", "剩余"])
        self.pumping_reward_theme_comboBox.currentIndexChanged.connect(self.save_settings)
        self.pumping_reward_theme_comboBox.setFont(QFont(load_custom_font(), 12))

        # 音量
        self.pumping_reward_voice_volume_SpinBox.setRange(0, 100)
        self.pumping_reward_voice_volume_SpinBox.setValue(100)
        self.pumping_reward_voice_volume_SpinBox.valueChanged.connect(self.save_settings)
        self.pumping_reward_voice_volume_SpinBox.setFont(QFont(load_custom_font(), 12))

        # 语速
        self.pumping_reward_voice_speed_SpinBox.setRange(1, 500)
        self.pumping_reward_voice_speed_SpinBox.setValue(100)
        self.pumping_reward_voice_speed_SpinBox.valueChanged.connect(self.save_settings)
        self.pumping_reward_voice_speed_SpinBox.setFont(QFont(load_custom_font(), 12))

        # 系统音量控制开关
        self.pumping_reward_system_volume_switch.setOnText("开启")
        self.pumping_reward_system_volume_switch.setOffText("关闭")
        self.pumping_reward_system_volume_switch.checkedChanged.connect(self.save_settings)
        self.pumping_reward_system_volume_switch.setFont(QFont(load_custom_font(), 12))

        # 系统音量
        self.pumping_reward_system_volume_SpinBox.setRange(0, 100)
        self.pumping_reward_system_volume_SpinBox.setValue(100)
        self.pumping_reward_system_volume_SpinBox.valueChanged.connect(self.save_settings)
        self.pumping_reward_system_volume_SpinBox.setFont(QFont(load_custom_font(), 12))

        # 添加组件到分组中
        self.addGroup(get_theme_icon("ic_fluent_arrow_sync_20_filled"), "抽取模式", "设置抽取模式", self.pumping_reward_Draw_comboBox)
        self.addGroup(get_theme_icon("ic_fluent_arrow_sync_20_filled"), "抽取方式", "设置抽取方式", self.pumping_reward_mode_Draw_comboBox)
        self.addGroup(get_theme_icon("ic_fluent_text_font_size_20_filled"), "字体大小", "设置抽取结果的字体大小(支持小数)", self.pumping_reward_font_size_SpinBox)
        self.addGroup(get_theme_icon("ic_fluent_person_feedback_20_filled"), "语音播放", "设置结果公布时是否播放语音", self.pumping_reward_Voice_switch)
        self.addGroup(get_theme_icon("ic_fluent_music_note_2_20_filled"), "音量大小", "调节播报音量 (0-100)", self.pumping_reward_voice_volume_SpinBox)
        self.addGroup(get_theme_icon("ic_fluent_person_feedback_20_filled"), "语速调节", "调节播报语速 (1%-500%)", self.pumping_reward_voice_speed_SpinBox)
        self.addGroup(get_theme_icon("ic_fluent_person_voice_20_filled"), "系统音量控制", "抽取完成后自动设置系统音量", self.pumping_reward_system_volume_switch)
        self.addGroup(get_theme_icon("ic_fluent_music_note_2_20_filled"), "系统音量大小", "设置抽取完成后的系统音量 (0-100)", self.pumping_reward_system_volume_SpinBox)
        self.addGroup(get_theme_icon("ic_fluent_calendar_video_20_filled"), "动画模式", "设置抽取时的动画播放方式", self.pumping_reward_Animation_comboBox)
        self.addGroup(get_theme_icon("ic_fluent_calendar_video_20_filled"), "动画间隔", "设置抽取时的动画播放间隔(10-2000)(<1,2号动画模式>适用)", self.pumping_reward_animation_interval_SpinBox)
        self.addGroup(get_theme_icon("ic_fluent_calendar_video_20_filled"), "自动播放次数", "设置抽取时的自动播放次数(1-50)(<2号动画模式>适用)", self.pumping_reward_animation_auto_play_SpinBox)
        self.addGroup(get_theme_icon("ic_fluent_people_eye_20_filled"), "奖品量", "设置该功能的显示格式", self.pumping_reward_theme_comboBox)

        self.load_settings()  # 加载设置
        self.save_settings()  # 保存设置

    def on_pumping_reward_Voice_switch_changed(self, checked):
        self.save_settings()

    def apply_font_size(self):
        try:
            font_size_str = self.pumping_reward_font_size_SpinBox.value()
            # 检查是否为一位小数
            if '.' in font_size_str:
                integer_part, decimal_part = font_size_str.split('.', 1)
                if len(decimal_part) > 1:
                    raise ValueError("最多只能输入一位小数")
            font_size = float(font_size_str)
            if 30.0 <= font_size <= 200.0:
                # 格式化保留一位小数
                self.pumping_reward_font_size_SpinBox.setValue(font_size)
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
            logger.warning(f"无效的字体大小输入: {self.pumping_reward_font_size_SpinBox.value()}")
            InfoBar.warning(
                title='无效的字体大小输入',
                content=f"无效的字体大小输入: {e}",
                orient=Qt.Horizontal, parent=self, isClosable=True, duration=3000, position=InfoBarPosition.TOP
            )

    def reset_font_size(self):
        try:
            self.pumping_reward_font_size_SpinBox.setValue("50.0")
        except FileNotFoundError as e:
            logger.error(f"加载设置时出错: {e}, 使用默认大小:50.0")
            self.pumping_reward_font_size_SpinBox.setValue("50.0")
        except KeyError:
            logger.error(f"设置文件中缺少'foundation'键, 使用默认大小:50.0")
            self.pumping_reward_font_size_SpinBox.setValue("50.0")
        self.save_settings()
        self.load_settings()
        
    def load_settings(self):
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    pumping_reward_settings = settings.get("pumping_reward", {})

                    font_size = pumping_reward_settings.get("font_size", self.default_settings["font_size"])
                    
                    # 直接使用索引值
                    draw_mode = pumping_reward_settings.get("draw_mode", self.default_settings["draw_mode"])
                    if draw_mode < 0 or draw_mode >= self.pumping_reward_Draw_comboBox.count():
                        logger.warning(f"无效的抽取模式索引: {draw_mode}")
                        draw_mode = self.default_settings["draw_mode"]

                    draw_pumping = pumping_reward_settings.get("draw_pumping", self.default_settings["draw_pumping"])
                    if draw_pumping < 0 or draw_pumping >= self.pumping_reward_mode_Draw_comboBox.count():
                        logger.warning(f"无效的抽取方式索引: {draw_pumping}")
                        draw_pumping = self.default_settings["draw_pumping"]
                        
                    animation_mode = pumping_reward_settings.get("animation_mode", self.default_settings["animation_mode"])
                    if animation_mode < 0 or animation_mode >= self.pumping_reward_Animation_comboBox.count():
                        logger.warning(f"无效的动画模式索引: {animation_mode}")
                        animation_mode = self.default_settings["animation_mode"]
                        
                    voice_enabled = pumping_reward_settings.get("voice_enabled", self.default_settings["voice_enabled"])

                    reward_theme = pumping_reward_settings.get("reward_theme", self.default_settings["reward_theme"])
                    if reward_theme < 0 or reward_theme >= self.pumping_reward_theme_comboBox.count():
                        logger.warning(f"无效的人数/组数样式索引: {reward_theme}")
                        reward_theme = self.default_settings["reward_theme"]

                    # 加载语音设置
                    voice_volume = pumping_reward_settings.get("voice_volume", self.default_settings["voice_volume"])
                    if voice_volume < 0 or voice_volume > 100:
                        logger.warning(f"无效的音量值: {voice_volume}")
                        voice_volume = self.default_settings["voice_volume"]

                    voice_speed = pumping_reward_settings.get("voice_speed", self.default_settings["voice_speed"])
                    if voice_speed < 1 or voice_speed > 500:
                        logger.warning(f"无效的语速值: {voice_speed}")
                        voice_speed = self.default_settings["voice_speed"]

                    # 加载系统音量设置
                    system_volume_enabled = pumping_reward_settings.get("system_volume_enabled", self.default_settings["system_volume_enabled"])
                    system_volume_value = pumping_reward_settings.get("system_volume_value", self.default_settings["system_volume_value"])

                    animation_interval = pumping_reward_settings.get("animation_interval", self.default_settings["animation_interval"])
                    animation_auto_play = pumping_reward_settings.get("animation_auto_play", self.default_settings["animation_auto_play"])
                    
                    self.pumping_reward_Draw_comboBox.setCurrentIndex(draw_mode)
                    self.pumping_reward_mode_Draw_comboBox.setCurrentIndex(draw_pumping)
                    self.pumping_reward_font_size_SpinBox.setValue(font_size)
                    self.pumping_reward_Animation_comboBox.setCurrentIndex(animation_mode)
                    self.pumping_reward_Voice_switch.setChecked(voice_enabled)
                    self.pumping_reward_theme_comboBox.setCurrentIndex(reward_theme)
                    self.pumping_reward_voice_volume_SpinBox.setValue(voice_volume)
                    self.pumping_reward_voice_speed_SpinBox.setValue(voice_speed)
                    self.pumping_reward_system_volume_switch.setChecked(system_volume_enabled)
                    self.pumping_reward_system_volume_SpinBox.setValue(system_volume_value)
                    self.pumping_reward_animation_interval_SpinBox.setValue(animation_interval)
                    self.pumping_reward_animation_auto_play_SpinBox.setValue(animation_auto_play)
            else:
                self.pumping_reward_Draw_comboBox.setCurrentIndex(self.default_settings["draw_mode"])
                self.pumping_reward_mode_Draw_comboBox.setCurrentIndex(self.default_settings["draw_pumping"])
                self.pumping_reward_font_size_SpinBox.setValue(self.default_settings["font_size"])
                self.pumping_reward_Animation_comboBox.setCurrentIndex(self.default_settings["animation_mode"])
                self.pumping_reward_Voice_switch.setChecked(self.default_settings["voice_enabled"])
                self.pumping_reward_theme_comboBox.setCurrentIndex(self.default_settings["reward_theme"])
                self.pumping_reward_voice_volume_SpinBox.setValue(self.default_settings["voice_volume"])
                self.pumping_reward_voice_speed_SpinBox.setValue(self.default_settings["voice_speed"])
                self.pumping_reward_system_volume_switch.setChecked(self.default_settings["system_volume_enabled"])
                self.pumping_reward_system_volume_SpinBox.setValue(self.default_settings["system_volume_value"])
                self.pumping_reward_animation_interval_SpinBox.setValue(self.default_settings["animation_interval"])
                self.pumping_reward_animation_auto_play_SpinBox.setValue(self.default_settings["animation_auto_play"])

                self.save_settings()
        except Exception as e:
            logger.error(f"加载设置时出错: {e}")
            self.pumping_reward_Draw_comboBox.setCurrentIndex(self.default_settings["draw_mode"])
            self.pumping_reward_mode_Draw_comboBox.setCurrentIndex(self.default_settings["draw_pumping"])
            self.pumping_reward_font_size_SpinBox.setValue(self.default_settings["font_size"])
            self.pumping_reward_Animation_comboBox.setCurrentIndex(self.default_settings["animation_mode"])
            self.pumping_reward_Voice_switch.setChecked(self.default_settings["voice_enabled"])
            self.pumping_reward_theme_comboBox.setCurrentIndex(self.default_settings["reward_theme"])
            self.pumping_reward_voice_volume_SpinBox.setValue(self.default_settings["voice_volume"])
            self.pumping_reward_voice_speed_SpinBox.setValue(self.default_settings["voice_speed"])
            self.pumping_reward_system_volume_switch.setChecked(self.default_settings["system_volume_enabled"])
            self.pumping_reward_system_volume_SpinBox.setValue(self.default_settings["system_volume_value"])
            self.pumping_reward_animation_interval_SpinBox.setValue(self.default_settings["animation_interval"])
            self.pumping_reward_animation_auto_play_SpinBox.setValue(self.default_settings["animation_auto_play"])

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
        
        # 更新pumping_reward部分的所有设置
        if "pumping_reward" not in existing_settings:
            existing_settings["pumping_reward"] = {}
            
        pumping_reward_settings = existing_settings["pumping_reward"]
        # 只保存索引值
        pumping_reward_settings["draw_mode"] = self.pumping_reward_Draw_comboBox.currentIndex()
        pumping_reward_settings["draw_pumping"] = self.pumping_reward_mode_Draw_comboBox.currentIndex()
        pumping_reward_settings["animation_mode"] = self.pumping_reward_Animation_comboBox.currentIndex()
        pumping_reward_settings["voice_enabled"] = self.pumping_reward_Voice_switch.isChecked()
        pumping_reward_settings["reward_theme"] = self.pumping_reward_theme_comboBox.currentIndex()
        pumping_reward_settings["voice_volume"] = self.pumping_reward_voice_volume_SpinBox.value()
        pumping_reward_settings["voice_speed"] = self.pumping_reward_voice_speed_SpinBox.value()
        pumping_reward_settings["system_volume_enabled"] = self.pumping_reward_system_volume_switch.isChecked()
        pumping_reward_settings["system_volume_value"] = self.pumping_reward_system_volume_SpinBox.value()
        pumping_reward_settings["animation_interval"] = self.pumping_reward_animation_interval_SpinBox.value()
        pumping_reward_settings["animation_auto_play"] = self.pumping_reward_animation_auto_play_SpinBox.value()

        # 保存字体大小
        try:
            font_size = float(self.pumping_reward_font_size_SpinBox.value())
            if 30.0 <= font_size <= 200.0:
                pumping_reward_settings["font_size"] = font_size
            # else:
            #     logger.warning(f"字体大小超出范围: {font_size}")
        except ValueError:
            # logger.warning(f"无效的字体大小输入: {self.pumping_reward_font_size_edit.text()}")
            pass
        
        os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
        with open(self.settings_file, 'w', encoding='utf-8') as f:
            json.dump(existing_settings, f, indent=4)
