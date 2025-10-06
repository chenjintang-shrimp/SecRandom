from qfluentwidgets import *
from qfluentwidgets import FluentIcon as FIF
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

import os
import json
import pyttsx3
import asyncio
import edge_tts
from loguru import logger

from app.common.config import get_theme_icon, load_custom_font, is_dark_theme
from app.common.path_utils import path_manager, ensure_dir, open_file

class VoiceEngine_SettingsCard(GroupHeaderCardWidget):
    # 定义信号
    updateVoiceComboBox = pyqtSignal(list, str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("语音引擎")
        self.setBorderRadius(8)
        self.settings_file = path_manager.get_voice_engine_path()
        self.default_settings = {
            "voice_engine": 0,
            "edge_tts_voice_name": "zh-CN-XiaoxiaoNeural",
            "voice_enabled": False,
            "voice_volume": 100,
            "voice_speed": 100,
            "system_volume_enabled": False,
            "system_volume_value": 50
        }

        # 连接信号和槽
        self.updateVoiceComboBox.connect(self._update_voice_combo_box)
        
        # 添加标志，避免重复更新语音列表
        self._is_updating_voices = False

        # 选择语音引擎
        self.voice_engine_comboBox = ComboBox()
        self.voice_engine_comboBox.setPlaceholderText("选择语音引擎")
        self.voice_engine_comboBox.addItems(["系统TTS", "Edge TTS"])
        self.voice_engine_comboBox.setCurrentIndex(self.default_settings["voice_engine"])
        self.voice_engine_comboBox.currentIndexChanged.connect(self.save_settings)
        self.voice_engine_comboBox.currentIndexChanged.connect(self.on_voice_engine_changed)
        self.voice_engine_comboBox.setFont(QFont(load_custom_font(), 12))

        # 选择Edge TTS的语音名称
        self.edge_tts_voiceComboBox = ComboBox()
        # 使用默认语音列表初始化，避免在构造函数中使用asyncio.run
        default_voices = [
            "zh-CN-XiaoxiaoNeural",
            "zh-CN-YunxiNeural", 
            "zh-CN-XiaoyiNeural",
            "en-US-JennyNeural",
            "en-US-GuyNeural"
        ]
        self.edge_tts_voiceComboBox.addItems(default_voices)
        self.edge_tts_voiceComboBox.currentTextChanged.connect(self.save_settings)
        self.edge_tts_voiceComboBox.setFont(QFont(load_custom_font(), 10))
        self.edge_tts_voiceComboBox.setEnabled((self.voice_engine_comboBox.currentIndex() == 1))

        # 语音播放按钮
        self.pumping_people_Voice_switch = SwitchButton()
        self.pumping_people_Voice_switch.setOnText("开启")
        self.pumping_people_Voice_switch.setOffText("关闭")
        self.pumping_people_Voice_switch.checkedChanged.connect(self.save_settings)
        self.pumping_people_Voice_switch.setFont(QFont(load_custom_font(), 12))

        # 音量
        self.pumping_people_voice_volume_SpinBox = SpinBox()
        self.pumping_people_voice_volume_SpinBox.setRange(0, 100)
        self.pumping_people_voice_volume_SpinBox.setValue(100)
        self.pumping_people_voice_volume_SpinBox.setSingleStep(5)
        self.pumping_people_voice_volume_SpinBox.setSuffix("%")
        self.pumping_people_voice_volume_SpinBox.valueChanged.connect(self.save_settings)
        self.pumping_people_voice_volume_SpinBox.setFont(QFont(load_custom_font(), 12))

        # 语速
        self.pumping_people_voice_speed_SpinBox = SpinBox()
        self.pumping_people_voice_speed_SpinBox.setRange(1, 500)
        self.pumping_people_voice_speed_SpinBox.setValue(100)
        self.pumping_people_voice_speed_SpinBox.setSingleStep(10)
        self.pumping_people_voice_speed_SpinBox.setSuffix("wpm")
        self.pumping_people_voice_speed_SpinBox.valueChanged.connect(self.save_settings)
        self.pumping_people_voice_speed_SpinBox.setFont(QFont(load_custom_font(), 12))

        # 系统音量控制开关
        self.pumping_people_system_volume_switch = SwitchButton()
        self.pumping_people_system_volume_switch.setOnText("开启")
        self.pumping_people_system_volume_switch.setOffText("关闭")
        self.pumping_people_system_volume_switch.checkedChanged.connect(self.save_settings)
        self.pumping_people_system_volume_switch.setFont(QFont(load_custom_font(), 12))

        # 系统音量
        self.pumping_people_system_volume_SpinBox = SpinBox()
        self.pumping_people_system_volume_SpinBox.setRange(0, 100)
        self.pumping_people_system_volume_SpinBox.setValue(100)
        self.pumping_people_system_volume_SpinBox.setSingleStep(5)
        self.pumping_people_system_volume_SpinBox.setSuffix("%")
        self.pumping_people_system_volume_SpinBox.valueChanged.connect(self.save_settings)
        self.pumping_people_system_volume_SpinBox.setFont(QFont(load_custom_font(), 12))

        # ===== 语音引擎选择 =====
        self.addGroup(get_theme_icon("ic_fluent_person_voice_20_filled"), "语音引擎", "配置语音播报的引擎类型", self.voice_engine_comboBox)
        self.addGroup(get_theme_icon("ic_fluent_person_feedback_20_filled"), "Edge TTS-语音名称", "选择Edge TTS的具体语音角色", self.edge_tts_voiceComboBox)
        
        # ===== 语音播放控制 =====
        self.addGroup(get_theme_icon("ic_fluent_person_feedback_20_filled"), "语音播放", "开启或关闭抽取结果的语音播报", self.pumping_people_Voice_switch)
        
        # ===== 语音参数调节 =====
        self.addGroup(get_theme_icon("ic_fluent_music_note_2_20_filled"), "音量大小", "调整语音播报的音量大小(0-100)", self.pumping_people_voice_volume_SpinBox)
        self.addGroup(get_theme_icon("ic_fluent_person_feedback_20_filled"), "语速调节", "调整语音播报的语速快慢(1-500wpm)", self.pumping_people_voice_speed_SpinBox)
        
        # ===== 系统音量控制 =====
        self.addGroup(get_theme_icon("ic_fluent_person_voice_20_filled"), "系统音量控制", "抽取完成后自动调整系统音量", self.pumping_people_system_volume_switch)
        self.addGroup(get_theme_icon("ic_fluent_music_note_2_20_filled"), "系统音量大小", "设置抽取完成后的系统音量值(0-100)", self.pumping_people_system_volume_SpinBox)

        self.load_settings()
        # 移除构造函数中的save_settings调用，避免不必要的文件写入

    def on_voice_engine_changed(self, index):
        self.edge_tts_voiceComboBox.setEnabled(index == 1)
        # 当切换到Edge TTS时，延迟异步更新语音列表，避免频繁触发网络请求
        if index == 1:
            # 使用QTimer延迟执行，给UI一些响应时间
            QTimer.singleShot(500, self._async_update_edge_tts_voices)
    
    def _async_update_edge_tts_voices(self):
        """异步更新Edge TTS语音列表"""
        # 如果正在更新，则不再重复请求
        if self._is_updating_voices:
            return
            
        self._is_updating_voices = True
        try:
            # 获取当前事件循环
            loop = asyncio.get_event_loop()
            # 创建任务但不等待，让它在后台运行
            loop.create_task(self._update_edge_tts_voices_task())
        except Exception as e:
            logger.error(f"创建Edge TTS语音更新任务失败: {e}")
            self._is_updating_voices = False
    
    async def _update_edge_tts_voices_task(self):
        """异步更新Edge TTS语音列表的任务"""
        try:
            # 获取最新的语音列表
            voices = await self._get_edge_tts_voices()
            # 获取当前选中的语音
            current_voice = self.edge_tts_voiceComboBox.currentText()
            
            # 使用信号槽机制在主线程中更新UI
            self.updateVoiceComboBox.emit(voices, current_voice)
        except Exception as e:
            logger.error(f"更新Edge TTS语音列表失败: {e}")
        finally:
            # 无论成功或失败，都要重置更新标志
            self._is_updating_voices = False
    
    @pyqtSlot(list, str)
    def _update_voice_combo_box(self, voices, current_voice):
        """在主线程中更新语音列表下拉框"""
        try:
            # 清空当前列表
            self.edge_tts_voiceComboBox.clear()
            # 添加新的语音列表
            self.edge_tts_voiceComboBox.addItems([v['id'] for v in voices])
            # 尝试恢复之前选中的语音
            index = self.edge_tts_voiceComboBox.findText(current_voice)
            if index >= 0:
                self.edge_tts_voiceComboBox.setCurrentIndex(index)
            else:
                # 如果找不到之前选中的语音，使用默认语音
                self.edge_tts_voiceComboBox.setCurrentText("zh-CN-XiaoxiaoNeural")
            
            logger.info(f"Edge TTS语音列表已更新，共{len(voices)}个语音")
        except Exception as e:
            logger.error(f"更新语音列表下拉框失败: {e}")

    async def _get_edge_tts_voices(self):
        import aiohttp
        max_retries = 3
        retry_delay = 2  # 秒
        
        for attempt in range(max_retries):
            try:
                voices = await edge_tts.list_voices()
                filtered_voices = [{
                    "name": v['FriendlyName'],
                    "id": v['ShortName'] if not v['Locale'].startswith('zh-CN') else f"zh-CN-{v['FriendlyName'].split()[1]}Neural",
                    "languages": v['Locale'].replace('_', '-'),
                    "full_info": f"{v['Gender']} | {v['Locale']} | Type: {v.get('VoiceType', 'Unknown')}"
                } for v in voices if v['Locale'].startswith(('zh-CN', 'en-', 'ja-JP', 'ko-KR'))]
                return filtered_voices
            except (aiohttp.ClientError, aiohttp.ClientResponseError) as e:
                if attempt < max_retries - 1:
                    logger.error(f"Edge TTS服务连接失败，第{attempt + 1}次重试中... 错误: {str(e)!r}")
                    await asyncio.sleep(retry_delay)
                    continue
                else:
                    logger.error(f"Edge TTS服务连接失败，已重试{max_retries}次: {str(e)!r}")
            except KeyError as e:
                logger.error(f"Edge TTS语音解析失败: {str(e)!r}")
                break
            except Exception as e:
                if attempt < max_retries - 1:
                    logger.error(f"Edge TTS语音获取失败，第{attempt + 1}次重试中... 错误: {str(e)!r}")
                    await asyncio.sleep(retry_delay)
                    continue
                else:
                    logger.error(f"Edge TTS语音解析失败: {str(e)!r}")
        
        # 所有尝试都失败后，返回默认语音列表
        default_voices = [
            {"name": "Xiaoxiao", "id": "zh-CN-XiaoxiaoNeural", "languages": "zh-CN", "full_info": "Female | zh-CN | Type: Neural"},
            {"name": "Yunxi", "id": "zh-CN-YunxiNeural", "languages": "zh-CN", "full_info": "Male | zh-CN | Type: Neural"},
            {"name": "Xiaoyi", "id": "zh-CN-XiaoyiNeural", "languages": "zh-CN", "full_info": "Female | zh-CN | Type: Neural"},
            {"name": "Jenny", "id": "en-US-JennyNeural", "languages": "en-US", "full_info": "Female | en-US | Type: Neural"},
            {"name": "Guy", "id": "en-US-GuyNeural", "languages": "en-US", "full_info": "Male | en-US | Type: Neural"}
        ]
        logger.info("Edge TTS服务不可用，使用默认语音列表")
        return default_voices

    def load_settings(self):
        try:
            if path_manager.file_exists(self.settings_file):
                with open_file(self.settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    # 确保 voice_engine_settings 是一个字典
                    if isinstance(settings.get("voice_engine"), dict):
                        voice_engine_settings = settings.get("voice_engine", {})
                    else:
                        # 如果 voice_engine 不是字典，则创建一个新的字典
                        voice_engine_settings = {}
                        # 如果 voice_engine 是一个整数，则将其作为 voice_engine 键的值
                        if isinstance(settings.get("voice_engine"), int):
                            voice_engine_settings["voice_engine"] = settings.get("voice_engine")

                    voice_engine = voice_engine_settings.get("voice_engine", self.default_settings["voice_engine"])
                    edge_tts_voice_name = voice_engine_settings.get("edge_tts_voice_name", self.default_settings["edge_tts_voice_name"])
                    voice_enabled = voice_engine_settings.get("voice_enabled", self.default_settings["voice_enabled"])
                    voice_volume = voice_engine_settings.get("voice_volume", self.default_settings["voice_volume"])
                    voice_speed = voice_engine_settings.get("voice_speed", self.default_settings["voice_speed"])
                    system_volume_enabled = voice_engine_settings.get("system_volume_enabled", self.default_settings["system_volume_enabled"])
                    system_volume_value = voice_engine_settings.get("system_volume_value", self.default_settings["system_volume_value"])

                    self.voice_engine_comboBox.setCurrentIndex(voice_engine)
                    self.edge_tts_voiceComboBox.setCurrentText(edge_tts_voice_name)
                    self.pumping_people_Voice_switch.setChecked(voice_enabled)
                    self.pumping_people_voice_volume_SpinBox.setValue(voice_volume)
                    self.pumping_people_voice_speed_SpinBox.setValue(voice_speed)
                    self.pumping_people_system_volume_switch.setChecked(system_volume_enabled)
                    self.pumping_people_system_volume_SpinBox.setValue(system_volume_value)
            else:
                self.voice_engine_comboBox.setCurrentIndex(self.default_settings["voice_engine"])
                self.edge_tts_voiceComboBox.setCurrentText(self.default_settings["edge_tts_voice_name"])
                self.pumping_people_Voice_switch.setChecked(self.default_settings["voice_enabled"])
                self.pumping_people_voice_volume_SpinBox.setValue(self.default_settings["voice_volume"])
                self.pumping_people_voice_speed_SpinBox.setValue(self.default_settings["voice_speed"])
                self.pumping_people_system_volume_switch.setChecked(self.default_settings["system_volume_enabled"])
                self.pumping_people_system_volume_SpinBox.setValue(self.default_settings["system_volume_value"])
                self.save_settings()
        except Exception as e:
            logger.error(f"加载设置时出错: {e}")
            self.voice_engine_comboBox.setCurrentIndex(self.default_settings["voice_engine"])
            self.edge_tts_voiceComboBox.setCurrentText(self.default_settings["edge_tts_voice_name"])
            self.pumping_people_Voice_switch.setChecked(self.default_settings["voice_enabled"])
            self.pumping_people_voice_volume_SpinBox.setValue(self.default_settings["voice_volume"])
            self.pumping_people_voice_speed_SpinBox.setValue(self.default_settings["voice_speed"])
            self.pumping_people_system_volume_switch.setChecked(self.default_settings["system_volume_enabled"])
            self.pumping_people_system_volume_SpinBox.setValue(self.default_settings["system_volume_value"])
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
        
        # 确保 voice_engine 是一个字典
        if "voice_engine" not in existing_settings or not isinstance(existing_settings["voice_engine"], dict):
            existing_settings["voice_engine"] = {}
            # 如果原来的 voice_engine 是一个整数，则将其作为 voice_engine 键的值
            if isinstance(existing_settings.get("voice_engine"), int):
                existing_settings["voice_engine"]["voice_engine"] = existing_settings.get("voice_engine")
            
        voice_engine_settings = existing_settings["voice_engine"]
        
        # 检查设置是否有变化，如果没有变化则不写入文件
        settings_changed = (
            voice_engine_settings.get("voice_engine") != self.voice_engine_comboBox.currentIndex() or
            voice_engine_settings.get("edge_tts_voice_name") != self.edge_tts_voiceComboBox.currentText() or
            voice_engine_settings.get("voice_enabled") != self.pumping_people_Voice_switch.isChecked() or
            voice_engine_settings.get("voice_volume") != self.pumping_people_voice_volume_SpinBox.value() or
            voice_engine_settings.get("voice_speed") != self.pumping_people_voice_speed_SpinBox.value() or
            voice_engine_settings.get("system_volume_enabled") != self.pumping_people_system_volume_switch.isChecked() or
            voice_engine_settings.get("system_volume_value") != self.pumping_people_system_volume_SpinBox.value()
        )
        
        if not settings_changed:
            return  # 设置没有变化，不写入文件
        
        # 更新设置
        voice_engine_settings["voice_engine"] = self.voice_engine_comboBox.currentIndex()
        voice_engine_settings["edge_tts_voice_name"] = self.edge_tts_voiceComboBox.currentText()
        voice_engine_settings["voice_enabled"] = self.pumping_people_Voice_switch.isChecked()
        voice_engine_settings["voice_volume"] = self.pumping_people_voice_volume_SpinBox.value()
        voice_engine_settings["voice_speed"] = self.pumping_people_voice_speed_SpinBox.value()
        voice_engine_settings["system_volume_enabled"] = self.pumping_people_system_volume_switch.isChecked()
        voice_engine_settings["system_volume_value"] = self.pumping_people_system_volume_SpinBox.value()

        ensure_dir(Path(self.settings_file).parent)
        with open_file(self.settings_file, 'w', encoding='utf-8') as f:
            json.dump(existing_settings, f, indent=4)
