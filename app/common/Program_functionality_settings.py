from shlex import join
from qfluentwidgets import *
from qfluentwidgets import FluentIcon as FIF
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

import json
import os
import sys
import platform
from pathlib import Path
from datetime import datetime, timedelta
from loguru import logger
import winreg
from app.common.config import get_theme_icon, load_custom_font, is_dark_theme, VERSION
from app.common.path_utils import path_manager
from app.common.path_utils import open_file, ensure_dir
from app.common.message_receiver import init_message_receiver

is_dark = is_dark_theme(qconfig)

class Program_functionality_settingsCard(GroupHeaderCardWidget):
    # 定义清理信号
    cleanup_signal = pyqtSignal()
    json_message_received = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("软件功能管理")
        self.setBorderRadius(8)
        self.settings_file = path_manager.get_settings_path('custom_settings.json')
        self.default_settings = {
            "instant_draw_disable": False,
            "clear_draw_records_switch": False,
            "use_cwci_confirm_switch": False,
            "clear_draw_records_time": 120,
        }

        # 是否在课间禁用抽取功能
        self.instant_draw_disable_switch = SwitchButton()
        self.instant_draw_disable_switch.setOnText("启用")
        self.instant_draw_disable_switch.setOffText("禁用")
        self.instant_draw_disable_switch.setFont(QFont(load_custom_font(), 12))
        self.instant_draw_disable_switch.checkedChanged.connect(self.save_settings)

        # 是否在上课前清空抽取记录
        self.clear_draw_records_switch = SwitchButton()
        self.clear_draw_records_switch.setOnText("启用")
        self.clear_draw_records_switch.setOffText("禁用")
        self.clear_draw_records_switch.setFont(QFont(load_custom_font(), 12))
        self.clear_draw_records_switch.checkedChanged.connect(self.save_settings)

        # 设置在上课几分钟前清空抽取记录
        self.clear_draw_records_time_SpinBox = SpinBox()
        self.clear_draw_records_time_SpinBox.setRange(1, 1800)
        self.clear_draw_records_time_SpinBox.setValue(self.default_settings["clear_draw_records_time"])
        self.clear_draw_records_time_SpinBox.setSingleStep(1)
        self.clear_draw_records_time_SpinBox.setSuffix("秒")
        self.clear_draw_records_time_SpinBox.valueChanged.connect(self.save_settings)
        self.clear_draw_records_time_SpinBox.setFont(QFont(load_custom_font(), 12))

        # 是否使用通过 插件确认上课时间
        self.use_cwci_confirm_switch = SwitchButton()
        self.use_cwci_confirm_switch.setOnText("启用")
        self.use_cwci_confirm_switch.setOffText("禁用")
        self.use_cwci_confirm_switch.setFont(QFont(load_custom_font(), 12))
        self.use_cwci_confirm_switch.checkedChanged.connect(self.save_settings)

        # 设置上课时间段按钮
        self.set_class_time_button = PushButton("设置上课时间段")
        self.set_class_time_button.clicked.connect(self.show_cleanup_dialog)
        self.set_class_time_button.setFont(QFont(load_custom_font(), 12))

        # 添加个性化设置组
        self.addGroup(get_theme_icon("ic_fluent_drawer_dismiss_20_filled"), "课间禁用", "在课间打开主页面需要安全验证", self.instant_draw_disable_switch)
        self.addGroup(get_theme_icon("ic_fluent_timer_off_20_filled"), "抽取记录清理开关", "启用或禁用上课前抽取记录自动清理功能", self.clear_draw_records_switch)
        self.addGroup(get_theme_icon("ic_fluent_timer_20_filled"), "抽取记录清理时间", "设置上课前多少秒自动清理抽取记录（1-1800秒）", self.clear_draw_records_time_SpinBox)
        self.addGroup(get_theme_icon("ic_fluent_plug_connected_checkmark_20_filled"), "通过 CI 插件确认上课时间", "启用后将使用 CI 传递的信息来确认上课时间", self.use_cwci_confirm_switch)
        self.addGroup(get_theme_icon("ic_fluent_time_picker_20_filled"), "上课时间段", "设置上课时间段", self.set_class_time_button)
        
        # 初始化计时器，设置为单次触发模式
        self.cleanup_timer = QTimer(self)
        self.cleanup_timer.timeout.connect(self.check_cleanup_time)
        self.cleanup_timer.setInterval(500)
        
        # 清理状态管理：记录每个上课时间段的清理状态
        self.cleanup_status = {}  # 格式: {时间段: 是否已清理}
        
        # 缓存时间设置，减少文件读取次数
        self.time_settings_cache = None
        self.time_settings_file = path_manager.get_settings_path('time_settings.json')
        
        # 存储从消息接收器获取的信息
        self.ci_info = {
            "current_subject": "",          # string 当前所处时间点的科目名称
            "next_subject": "",            # string 下一节课的科目名称
            "current_state": "",           # string 当前时间点状态的字符串表示
            "is_class_plan_enabled": False, # bool 是否启用课表
            "is_class_plan_loaded": False,  # bool 是否已加载课表
            "is_lesson_confirmed": False,   # bool 是否已确定当前时间点
            "on_class_left_time": 0,        # double 距离上课剩余时间（秒）
            "on_breaking_time_left": 0      # double 距下课剩余时间（秒）
        }
        
        # 加载设置
        self.load_settings()
        self.save_settings()

        # 优化：移除延迟初始化，直接初始化计时器和消息接收器连接
        self.connect_message_receiver()
        self._delayed_init()
    
    def _delayed_init(self):
        """初始化计时器和消息接收器连接"""
        # 根据设置状态启动或停止计时器
        if self.clear_draw_records_switch.isChecked():
            self.cleanup_timer.start()
            # logger.debug("已启动上课前清理抽取记录计时器")
        else:
            self.cleanup_timer.stop()
            # logger.debug("已停止上课前清理抽取记录计时器")
        
    def connect_message_receiver(self):
        # 连接消息接收器信号
        try:
            # 初始化消息接收器
            message_receiver = init_message_receiver()
            if message_receiver is not None:
                message_receiver.json_message_received.connect(self._handle_ci_message)
                # logger.debug("成功连接消息接收器信号")
            else:
                logger.error("消息接收器初始化失败")
        except Exception as e:
            logger.error(f"连接消息接收器信号失败: {e}")

    def load_settings(self):
        try:
            if path_manager.file_exists(self.settings_file):
                with open_file(self.settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    program_functionality_settings = settings.get("program_functionality", {})

                    self.instant_draw_disable_switch.setChecked(program_functionality_settings.get("instant_draw_disable", self.default_settings.get("instant_draw_disable", False)))
                    self.clear_draw_records_switch.setChecked(program_functionality_settings.get("clear_draw_records_switch", self.default_settings.get("clear_draw_records_switch", False)))
                    self.clear_draw_records_time_SpinBox.setValue(program_functionality_settings.get("clear_draw_records_time", self.default_settings.get("clear_draw_records_time", 120)))
                    self.use_cwci_confirm_switch.setChecked(program_functionality_settings.get("use_cwci_confirm_switch", self.default_settings.get("use_cwci_confirm_switch", False)))
            else:
                # logger.error(f"设置文件不存在: {self.settings_file}")
                self.instant_draw_disable_switch.setChecked(self.default_settings.get("instant_draw_disable", False))
                self.clear_draw_records_switch.setChecked(self.default_settings.get("clear_draw_records_switch", False))
                self.clear_draw_records_time_SpinBox.setValue(self.default_settings.get("clear_draw_records_time", 120))
                self.use_cwci_confirm_switch.setChecked(self.default_settings.get("use_cwci_confirm_switch", False))
                self.save_settings()
        except Exception as e:
            logger.error(f"加载设置时出错: {e}")
            self.instant_draw_disable_switch.setChecked(self.default_settings.get("instant_draw_disable", False))
            self.clear_draw_records_switch.setChecked(self.default_settings.get("clear_draw_records_switch", False))
            self.clear_draw_records_time_SpinBox.setValue(self.default_settings.get("clear_draw_records_time", 120))
            self.use_cwci_confirm_switch.setChecked(self.default_settings.get("use_cwci_confirm_switch", False))
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
        
        # 更新program_functionality部分的所有设置
        if "program_functionality" not in existing_settings:
            existing_settings["program_functionality"] = {}
            
        program_functionality_settings = existing_settings["program_functionality"]

        # 保存旧的状态，用于比较是否发生变化
        old_clear_draw_records_switch = program_functionality_settings.get("clear_draw_records_switch", False)
        old_use_cwci_confirm_switch = program_functionality_settings.get("use_cwci_confirm_switch", False)
        
        program_functionality_settings["instant_draw_disable"] = self.instant_draw_disable_switch.isChecked()
        program_functionality_settings["clear_draw_records_switch"] = self.clear_draw_records_switch.isChecked()
        program_functionality_settings["clear_draw_records_time"] = self.clear_draw_records_time_SpinBox.value()
        program_functionality_settings["use_cwci_confirm_switch"] = self.use_cwci_confirm_switch.isChecked()

        os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
        with open_file(self.settings_file, 'w', encoding='utf-8') as f:
            json.dump(existing_settings, f, indent=4)
        
        # 检查清理开关状态是否发生变化
        if old_clear_draw_records_switch != self.clear_draw_records_switch.isChecked():
            if self.clear_draw_records_switch.isChecked():
                # 开启计时器
                self.cleanup_timer.start()
                # logger.info("已启动上课前清理抽取记录计时器")
            else:
                # 停止计时器
                self.cleanup_timer.stop()
                # logger.info("已停止上课前清理抽取记录计时器")
        elif self.clear_draw_records_switch.isChecked() and not self.cleanup_timer.isActive():
            # 如果开关是开启状态但计时器未运行，启动计时器
            self.cleanup_timer.start()
            # logger.info("已启动上课前清理抽取记录计时器")
        
        # 检查 确认开关状态是否发生变化
        if old_use_cwci_confirm_switch != self.use_cwci_confirm_switch.isChecked():
            if self.use_cwci_confirm_switch.isChecked():
                # logger.info("已启用 插件确认上课时间")
                self.cleanup_status = {}
            else:
                # logger.info("已禁用 插件确认上课时间")
                # 重置清理状态，避免影响原有时间检测方式
                self.cleanup_status = {}


    def show_cleanup_dialog(self):
        dialog = TimeSettingsDialog(self)
        if dialog.exec():
            # 清除时间设置缓存，确保下次使用最新设置
            self.time_settings_cache = None
            time_settings = dialog.textEdit.toPlainText()
            try:
                # 确保Settings目录存在
                from app.common.path_utils import path_manager
                time_settings_file = path_manager.get_settings_path('time_settings.json')
                os.makedirs(os.path.dirname(time_settings_file), exist_ok=True)
                
                settings = {}
                if path_manager.file_exists(time_settings_file):
                    with open_file(time_settings_file, 'r', encoding='utf-8') as f:
                        settings = json.load(f)
                
                # 处理多个时间段输入
                time_list = [time.strip() for time in time_settings.split('\n') if time.strip()]
                
                # 清空现有设置
                if 'non_class_times' in settings:
                    settings['non_class_times'] = {}
                if 'class_times' in settings:
                    settings['class_times'] = []
                
                # 验证并收集所有有效时间段
                valid_class_times = []
                for time_str in time_list:
                    try:
                        # 验证时间段格式
                        time_str = time_str.replace('：', ':')  # 中文冒号转英文
                        
                        # 检查是否为时间段格式 (HH:MM-HH:MM)
                        if '-' in time_str:
                            parts = time_str.split('-')
                            if len(parts) != 2:
                                raise ValueError(f"时间段格式应为'开始时间-结束时间'，例如：08:00-08:40，当前输入: {time_str}")
                            
                            start_time, end_time = parts
                            
                            # 验证开始时间
                            start_parts = start_time.split(':')
                            if len(start_parts) == 2:
                                start_hours, start_minutes = start_parts
                                start_seconds = '00'
                                start_time = f"{start_hours}:{start_minutes}:{start_seconds}"
                            elif len(start_parts) == 3:
                                start_hours, start_minutes, start_seconds = start_parts
                            else:
                                raise ValueError(f"开始时间格式应为'HH:MM'或'HH:MM:SS'，当前输入: {start_time}")
                            
                            # 验证结束时间
                            end_parts = end_time.split(':')
                            if len(end_parts) == 2:
                                end_hours, end_minutes = end_parts
                                end_seconds = '00'
                                end_time = f"{end_hours}:{end_minutes}:{end_seconds}"
                            elif len(end_parts) == 3:
                                end_hours, end_minutes, end_seconds = end_parts
                            else:
                                raise ValueError(f"结束时间格式应为'HH:MM'或'HH:MM:SS'，当前输入: {end_time}")
                            
                            # 确保所有部分都存在
                            if not all([start_hours, start_minutes, start_seconds]):
                                raise ValueError(f"开始时间格式不完整，应为'HH:MM'或'HH:MM:SS'，当前输入: {start_time}")
                            if not all([end_hours, end_minutes, end_seconds]):
                                raise ValueError(f"结束时间格式不完整，应为'HH:MM'或'HH:MM:SS'，当前输入: {end_time}")
                                
                            start_hours = int(start_hours.strip())
                            start_minutes = int(start_minutes.strip())
                            start_seconds = int(start_seconds.strip())
                            
                            end_hours = int(end_hours.strip())
                            end_minutes = int(end_minutes.strip())
                            end_seconds = int(end_seconds.strip())
                            
                            if start_hours < 0 or start_hours > 23:
                                raise ValueError(f"开始小时数必须在0-23之间，当前输入: {start_hours}")
                            if start_minutes < 0 or start_minutes > 59:
                                raise ValueError(f"开始分钟数必须在0-59之间，当前输入: {start_minutes}")
                            if start_seconds < 0 or start_seconds > 59:
                                raise ValueError(f"开始秒数必须在0-59之间，当前输入: {start_seconds}")
                            
                            if end_hours < 0 or end_hours > 23:
                                raise ValueError(f"结束小时数必须在0-23之间，当前输入: {end_hours}")
                            if end_minutes < 0 or end_minutes > 59:
                                raise ValueError(f"结束分钟数必须在0-59之间，当前输入: {end_minutes}")
                            if end_seconds < 0 or end_seconds > 59:
                                raise ValueError(f"结束秒数必须在0-59之间，当前输入: {end_seconds}")
                            
                            # 验证开始时间是否早于结束时间
                            start_total_seconds = start_hours * 3600 + start_minutes * 60 + start_seconds
                            end_total_seconds = end_hours * 3600 + end_minutes * 60 + end_seconds
                            
                            if start_total_seconds >= end_total_seconds:
                                raise ValueError(f"开始时间必须早于结束时间，当前输入: {time_str}")
                            
                            valid_class_times.append({
                                'start': start_time,
                                'end': end_time,
                                'raw': time_str
                            })
                        else:
                            # 如果不是时间段格式，则作为错误处理
                            raise ValueError(f"请输入时间段格式，例如：08:00-08:40，当前输入: {time_str}")
                    except Exception as e:
                        logger.error(f"时间段格式验证失败: {str(e)}")
                        continue
                
                # 按开始时间排序
                valid_class_times.sort(key=lambda x: tuple(map(int, x['start'].split(':'))))
                
                # 保存上课时间段
                settings['class_times'] = [time_info['raw'] for time_info in valid_class_times]
                
                # 生成非上课时间段（用于清理）
                non_class_times_list = []
                current_time = 0  # 从0点开始
                
                for class_time in valid_class_times:
                    start_time = class_time['start']
                    end_time = class_time['end']
                    
                    # 计算开始和结束时间的总秒数
                    start_parts = list(map(int, start_time.split(':')))
                    end_parts = list(map(int, end_time.split(':')))
                    
                    start_total_seconds = start_parts[0] * 3600 + start_parts[1] * 60 + start_parts[2]
                    end_total_seconds = end_parts[0] * 3600 + end_parts[1] * 60 + end_parts[2]
                    
                    # 如果当前时间早于上课开始时间，则添加当前时间到上课开始时间的清理时间段
                    if current_time < start_total_seconds:
                        non_class_times_list.append(self._seconds_to_time_string(current_time) + '-' + start_time)
                    
                    # 更新当前时间为上课结束时间
                    current_time = end_total_seconds
                
                # 如果最后一段不是到24点，则添加最后一段清理时间段
                if current_time < 24 * 3600:
                    non_class_times_list.append(self._seconds_to_time_string(current_time) + '-24:00:00')
                
                # 保存清理时间段
                for idx, time_str in enumerate(non_class_times_list, 1):
                    settings.setdefault('non_class_times', {})[str(idx)] = time_str
                
                with open_file(time_settings_file, 'w', encoding='utf-8') as f:
                    json.dump(settings, f, ensure_ascii=False, indent=4)
                    # 更新缓存
                    self.time_settings_cache = settings
                    logger.info(f"成功保存{len(time_list)}个上课时间段设置，生成了{len(non_class_times_list)}个清理时间段")
                    InfoBar.success(
                        title='设置成功',
                        content=f"成功保存{len(time_list)}个上课时间段，生成了{len(non_class_times_list)}个清理时间段!",
                        orient=Qt.Horizontal,
                        isClosable=True,
                        position=InfoBarPosition.TOP,
                        duration=3000,
                        parent=self
                    )
            except Exception as e:
                logger.error(f"保存上课时间段失败: {str(e)}")
                InfoBar.error(
                    title='设置失败',
                    content=f"保存上课时间段失败: {str(e)}",
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=3000,
                    parent=self
                )
    
    def check_cleanup_time(self):
        """检查当前时间是否需要清理抽取记录"""
        try:
            # 获取设置的时间（秒）
            cleanup_seconds = self.clear_draw_records_time_SpinBox.value()
            
            # 检查是否使用 插件确认上课时间
            if self.use_cwci_confirm_switch.isChecked():
                # 使用 插件信息进行检测
                self._check_cleanup_time_with_ci(cleanup_seconds)
            else:
                # 使用原有的时间检测方式
                self._check_cleanup_time_with_timer(cleanup_seconds)
        except Exception as e:
            logger.error(f"检查清理时间时出错: {e}")
    
    def _check_cleanup_time_with_ci(self, cleanup_seconds: int):
        """使用 插件信息检查是否需要清理抽取记录"""
        try:
            # 检查是否启用课表、已加载课表、已确定当前时间点
            if not (self.ci_info["is_class_plan_enabled"] and 
                    self.ci_info["is_class_plan_loaded"] and 
                    self.ci_info["is_lesson_confirmed"]):
                # 如果 信息不完整，不进行清理
                return
            
            # 检查当前状态是否为课间
            if self.ci_info["current_state"] != "Breaking":
                # 如果不是课间，不进行清理
                return
            
            # 检查距离上课剩余时间
            on_class_left_time = self.ci_info["on_class_left_time"]
            
            # 如果距离上课时间在设定范围内，则清理抽取记录
            if 0 < on_class_left_time <= cleanup_seconds:
                # 生成唯一的时间键，避免重复清理
                time_key = f"ci_{self.ci_info['next_subject']}"
                
                # 检查是否已经清理过这个时间段
                if not self.cleanup_status.get(time_key, False):
                    self._cleanup_draw_records()
                    self.cleanup_status[time_key] = True  # 标记为已清理
                    logger.info(f"信息检测：距离上课还有{int(on_class_left_time)}秒，已清理抽取记录（下一节课: {self.ci_info['next_subject']}）")
            else:
                # 如果时间差不在清理范围内，重置清理状态
                time_key = f"ci_{self.ci_info['next_subject']}_{on_class_left_time}"
                if self.cleanup_status.get(time_key, False):
                    self.cleanup_status[time_key] = False  # 重置清理状态
                    logger.info(f"信息检测：重置清理状态: {self.ci_info['next_subject']}")
        except Exception as e:
            logger.error(f"信息检查清理时间时出错: {e}")
    
    def _check_cleanup_time_with_timer(self, cleanup_seconds: int):
        """使用原有的时间检测方式检查是否需要清理抽取记录"""
        try:
            # 获取当前时间
            current_time = datetime.now().time()
            current_time_str = current_time.strftime("%H:%M:%S")
            
            # 使用缓存的时间设置，减少文件读取次数
            if self.time_settings_cache is None:
                if not path_manager.file_exists(self.time_settings_file):
                    return
                    
                with open_file(self.time_settings_file, 'r', encoding='utf-8') as f:
                    self.time_settings_cache = json.load(f)
            
            time_settings = self.time_settings_cache
                
            # 检查是否有非上课时间段设置
            if "non_class_times" not in time_settings or not time_settings["non_class_times"]:
                return
                
            # 检查当前时间是否在非上课时间段内
            # non_class_times 是一个字典，需要遍历其值而不是键值对
            for self._time_range_value, time_range_value in time_settings["non_class_times"].items():
                # 确保时间范围格式正确
                if "-" not in time_range_value:
                    logger.error(f"时间范围格式不正确，缺少'-'分隔符: {time_range_value}")
                    continue
                    
                time_parts = time_range_value.split("-")
                if len(time_parts) != 2:
                    logger.error(f"时间范围格式不正确，应该包含开始和结束时间: {time_range_value}")
                    continue
                    
                start_time_str, end_time_str = time_parts
                
                # 优化时间比较：直接比较字符串，避免频繁的时间转换
                if start_time_str <= current_time_str <= end_time_str:
                    # 当前时间在非上课时间段内，检查是否需要清理
                    # 计算距离上课开始的时间
                    self._class_start_time_str = end_time_str  # 非上课时间结束就是上课时间开始
                    
                    # 处理特殊情况：24:00:00 应该视为 00:00:00（午夜）
                    if self._class_start_time_str == "24:00:00":
                        self._class_start_time_str = "00:00:00"
                    
                    # 优化时间差计算：只在需要时才转换为datetime对象
                    now = datetime.now()
                    class_start_time = datetime.strptime(self._class_start_time_str, "%H:%M:%S").time()
                    
                    # 处理跨天情况
                    class_start_datetime = datetime.combine(now.date(), class_start_time)
                    if class_start_time < current_time:
                        # 如果上课时间是第二天，加一天
                        class_start_datetime = datetime.combine((now.date() + timedelta(days=1)), class_start_time)
                    
                    time_diff = (class_start_datetime - now).total_seconds()
                    
                    # 如果时间差小于等于设置的时间，则清理抽取记录
                    if 0 < time_diff <= cleanup_seconds:
                        # 检查是否已经清理过这个时间段
                        time_key = f"{self._class_start_time_str}_{self._time_range_value}"
                        if not self.cleanup_status.get(time_key, False):
                            self._cleanup_draw_records()
                            self.cleanup_status[time_key] = True  # 标记为已清理
                            # logger.info(f"距离上课还有{int(time_diff)}秒，已清理抽取记录（时间段: {self._time_range_value}）")
                        break
                    else:
                        # 如果时间差不在清理范围内，重置清理状态
                        time_key = f"{self._class_start_time_str}_{self._time_range_value}"
                        if self.cleanup_status.get(time_key, False):
                            self.cleanup_status[time_key] = False  # 重置清理状态
                            # logger.debug(f"重置清理状态: {self._time_range_value}")
        except Exception as e:
            logger.error(f"检查清理时间时出错: {e}")
    
    def _handle_ci_message(self, data: dict):
        """处理来自 插件的消息"""
        try:
            # 检查消息类型
            message_type = data.get("type", "")
            
            if message_type == "class_status":
                # 更新 信息
                ci_data = data.get("data", {})
                self.ci_info["current_subject"] = ci_data.get("current_subject", "")
                self.ci_info["next_subject"] = ci_data.get("next_subject", "")
                self.ci_info["current_state"] = ci_data.get("current_state", "")
                self.ci_info["is_class_plan_enabled"] = ci_data.get("is_class_plan_enabled", False)
                self.ci_info["is_class_plan_loaded"] = ci_data.get("is_class_plan_loaded", False)
                self.ci_info["is_lesson_confirmed"] = ci_data.get("is_lesson_confirmed", False)
                self.ci_info["on_class_left_time"] = ci_data.get("on_class_left_time", 0)
                self.ci_info["on_breaking_time_left"] = ci_data.get("on_breaking_time_left", 0)
        except Exception as e:
            logger.error(f"处理 消息失败: {e}")

    def _get_main_window(self):
        """获取主窗口实例"""
        try:
            for widget in QApplication.topLevelWidgets():
                # 通过特征识别主窗口
                if hasattr(widget, 'cleanup_signal'):
                    return widget
            return None
        except Exception as e:
            logger.error(f"获取主窗口失败: {str(e)}")
            return None

    def _cleanup_draw_records(self):
        """清理抽取记录"""
        try:
            settings_path = path_manager.get_settings_path('Settings.json')
            with open_file(settings_path, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                max_draw_times_per_person = settings['pumping_people']['Draw_pumping']
                pumping_people_draw_mode = settings['pumping_people']['draw_mode']
                logger.info(f"抽选模式为{max_draw_times_per_person}，准备执行对应清理方案～ ")

        except Exception as e:
            pumping_people_draw_mode = 1
            max_draw_times_per_person = 1
            logger.error(f"加载抽选模式设置失败了喵～ {e}, 使用默认:{max_draw_times_per_person}次模式")

        import glob
        temp_dir = path_manager.get_temp_path('')
        ensure_dir(temp_dir)

        if max_draw_times_per_person != 0 and pumping_people_draw_mode not in [0,2]:  # 不重复抽取(直到软件重启)
            if path_manager.file_exists(temp_dir):
                for file in glob.glob(f"{temp_dir}/*.json"):
                    try:
                        os.remove(file)
                        logger.info(f"已删除临时抽取记录文件: {file}")
                    except Exception as e:
                        logger.error(f"删除临时文件出错喵～ {e}")
        
        # 通过主窗口发送清理信号，通知抽奖和点名界面清除标签
        main_window = self._get_main_window()
        if main_window:
            main_window.cleanup_signal.emit()
            logger.info("已通过主窗口发送清理信号，通知抽奖和点名界面清除标签～")
        else:
            logger.error("未找到主窗口实例，无法发送清理信号～")
    
    def _seconds_to_time_string(self, seconds):
        """将秒数转换为HH:MM:SS格式的时间字符串"""
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def _is_non_class_time_with_ci(self):
        """使用 插件信息判断是否为非上课时间"""
        try:
            # 读取程序功能设置
            instant_draw_disable = program_functionality.get("instant_draw_disable", False)
            
            if not instant_draw_disable:
                return False
                
            # 检查信息是否可用
            if not hasattr(self, 'ci_info') or not self.ci_info:
                # 如果信息不可用，回退到原有的时间检测方式
                logger.error("信息不可用，回退到原有时间检测方式")
                return self._is_non_class_time_with_timer()
                
            # 检查是否启用课表、已加载课表、已确定当前时间点
            if not (self.ci_info.get("is_class_plan_enabled", False) and 
                    self.ci_info.get("is_class_plan_loaded", False) and 
                    self.ci_info.get("is_lesson_confirmed", False)):
                # 如果 信息不完整，回退到原有的时间检测方式
                logger.error("信息不完整，回退到原有时间检测方式")
                return self._is_non_class_time_with_timer()
            
            # 检查当前状态是否为课间
            current_state = self.ci_info.get("current_state", "")
            if current_state == "Breaking":
                # 如果是课间，返回True（表示是非上课时间）
                return True
            elif current_state in ["BeforeClass", "InClass", "AfterClass"]:
                # 如果是上课前、上课中或下课后，返回False（表示不是非上课时间）
                return False
            else:
                # 如果状态未知，回退到原有的时间检测方式
                logger.error(f"未知的状态: {current_state}，回退到原有时间检测方式")
                return self._is_non_class_time_with_timer()
                
        except Exception as e:
            logger.error(f"使用插件检测非上课时间失败: {e}")
            # 如果插件检测失败，回退到原有的时间检测方式
            logger.error("插件检测失败，回退到原有时间检测方式")
            return self._is_non_class_time_with_timer()

    def _is_non_class_time_with_timer(self):
        """使用原有的时间检测方式判断是否为非上课时间"""
        try:
            # 读取程序功能设置
            settings_path = path_manager.get_settings_path('custom_settings.json')
            if not path_manager.file_exists(settings_path):
                return False
                
            with open_file(settings_path, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                
            # 检查课间禁用开关是否启用
            program_functionality = settings.get("program_functionality", {})
            instant_draw_disable = program_functionality.get("instant_draw_disable", False)
            
            if not instant_draw_disable:
                return False
                
            # 读取上课时间段设置
            time_settings_path = path_manager.get_settings_path('time_settings.json')
            if not path_manager.file_exists(time_settings_path):
                return False
                
            with open_file(time_settings_path, 'r', encoding='utf-8') as f:
                time_settings = json.load(f)
                
            # 获取非上课时间段
            non_class_times = time_settings.get('non_class_times', {})
            if not non_class_times:
                return False
                
            # 获取当前时间
            current_time = QDateTime.currentDateTime()
            current_hour = current_time.time().hour()
            current_minute = current_time.time().minute()
            current_second = current_time.time().second()
            
            # 将当前时间转换为总秒数
            current_total_seconds = current_hour * 3600 + current_minute * 60 + current_second
            
            # 检查当前时间是否在任何非上课时间段内
            for time_range in non_class_times.values():
                try:
                    start_end = time_range.split('-')
                    if len(start_end) != 2:
                        continue
                        
                    start_time_str, end_time_str = start_end
                    
                    # 解析开始时间
                    start_parts = list(map(int, start_time_str.split(':')))
                    start_total_seconds = start_parts[0] * 3600 + start_parts[1] * 60 + (start_parts[2] if len(start_parts) > 2 else 0)
                    
                    # 解析结束时间
                    end_parts = list(map(int, end_time_str.split(':')))
                    end_total_seconds = end_parts[0] * 3600 + end_parts[1] * 60 + (end_parts[2] if len(end_parts) > 2 else 0)
                    
                    # 检查当前时间是否在该非上课时间段内
                    if start_total_seconds <= current_total_seconds < end_total_seconds:
                        return True
                        
                except Exception as e:
                    logger.error(f"解析非上课时间段失败: {e}")
                    continue
                    
            return False
            
        except Exception as e:
            logger.error(f"检测非上课时间失败: {e}")
            return False

    def is_non_class_time(self):
        """检测当前时间是否在非上课时间段
        当'课间禁用'开关启用时，用于判断是否需要安全验证"""
        try:
            # 检查是否使用 插件确认上课时间
            if hasattr(self, 'use_cwci_confirm_switch') and self.use_cwci_confirm_switch.isChecked():
                # 使用 插件信息进行检测
                return self._is_non_class_time_with_ci()
            else:
                # 使用原有的时间检测方式
                return self._is_non_class_time_with_timer()
        except Exception as e:
            logger.error(f"检测非上课时间失败: {e}")
            return False



class TimeSettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self.setWindowTitle("上课时间段设置")
        self.setMinimumSize(400, 335)  # 设置最小大小而不是固定大小
        self.saved = False
        self.dragging = False
        self.drag_position = None
        
        # 确保不设置子窗口的屏幕属性
        if parent is not None:
            self.setParent(parent)
        
        self.title_bar = QWidget()
        self.title_bar.setObjectName("CustomTitleBar")
        self.title_bar.setFixedHeight(35)
        
        # 标题栏布局
        title_layout = QHBoxLayout(self.title_bar)
        title_layout.setContentsMargins(10, 0, 10, 0)
        
        # 窗口标题
        self.title_label = BodyLabel("上课时间段设置")
        self.title_label.setObjectName("TitleLabel")
        self.title_label.setFont(QFont(load_custom_font(), 12))
        
        # 窗口控制按钮
        self.close_btn = QPushButton("✕")
        self.close_btn.setObjectName("CloseButton")
        self.close_btn.setFixedSize(25, 25)
        self.close_btn.clicked.connect(self.reject)
        
        # 添加组件到标题栏
        title_layout.addWidget(self.title_label)
        title_layout.addStretch()
        title_layout.addWidget(self.close_btn)
        
        self.text_label = BodyLabel('请每行输入一个上课时间段，格式为 开始时间-结束时间\n示例：08:00-08:40\n系统会自动计算非上课时间段，用于清理抽取记录和禁用抽取功能')
        self.text_label.setFont(QFont(load_custom_font(), 12))

        self.update_theme_style()
        qconfig.themeChanged.connect(self.update_theme_style)
        
        self.textEdit = PlainTextEdit()
        self.textEdit.setPlaceholderText("示例：\n08:00-08:40\n09:00-09:40\n10:00-10:40")
        self.textEdit.setFont(QFont(load_custom_font(), 12))
        
        self.setFont(QFont(load_custom_font(), 12))

        try:
            time_settings_file = path_manager.get_settings_path('time_settings.json')
            if path_manager.file_exists(time_settings_file):
                with open_file(time_settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    
                    # 获取所有上课时间段并格式化为字符串
                    class_times = settings.get('class_times', [])
                    if class_times:
                        self.textEdit.setPlainText('\n'.join(class_times))
                    else:
                        pass
        except Exception as e:
            logger.error(f"加载上课时间段设置失败: {str(e)}")

        self.saveButton = PrimaryPushButton("保存")
        self.cancelButton = PushButton("取消")
        self.saveButton.clicked.connect(self.accept)
        self.cancelButton.clicked.connect(self.reject)
        self.saveButton.setFont(QFont(load_custom_font(), 12))
        self.cancelButton.setFont(QFont(load_custom_font(), 12))
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        # 添加自定义标题栏
        layout.addWidget(self.title_bar)
        # 添加内容区域
        content_layout = QVBoxLayout()
        content_layout.setSpacing(10)
        content_layout.addWidget(self.text_label)
        content_layout.addWidget(self.textEdit)
        
        buttonLayout = QHBoxLayout()
        buttonLayout.addStretch(1)
        buttonLayout.addWidget(self.cancelButton)
        buttonLayout.addWidget(self.saveButton)
        
        content_layout.addLayout(buttonLayout)
        content_layout.setContentsMargins(20, 10, 20, 20)
        layout.addLayout(content_layout)
        self.setLayout(layout)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.title_bar.underMouse():
            self.dragging = True
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.dragging and event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        self.dragging = False

    def update_theme_style(self):
        
        colors = {'text': '#F5F5F5', 'bg': '#111116', 'title_bg': '#2D2D2D'} if is_dark else {'text': '#111116', 'bg': '#F5F5F5', 'title_bg': '#E0E0E0'}
        self.setStyleSheet(f"""
            QDialog {{ background-color: {colors['bg']}; border-radius: 5px; }}
            #CustomTitleBar {{ background-color: {colors['title_bg']}; }}
            #TitleLabel {{ color: {colors['text']}; font-weight: bold; padding: 5px; }}
            #CloseButton {{ 
                background-color: transparent; 
                color: {colors['text']}; 
                border-radius: 4px; 
                font-weight: bold; 
            }}
            #CloseButton:hover {{ background-color: #ff4d4d; color: white; }}
            BodyLabel, QPushButton, QTextEdit {{ color: {colors['text']}; }}
        """)
        
        # 设置标题栏颜色以匹配背景色（仅Windows系统）
        if os.name == 'nt':
            try:
                import ctypes
                hwnd = int(self.winId())  # 转换为整数句柄
                
                bg_color = colors['bg'].lstrip('#')
                # 转换为ARGB格式（添加不透明通道）
                rgb_color = int(f'FF{bg_color}', 16) if len(bg_color) == 6 else int(bg_color, 16)
                
                # 设置窗口标题栏颜色
                ctypes.windll.dwmapi.DwmSetWindowAttribute(
                    ctypes.c_int(hwnd),  # 窗口句柄（整数类型）
                    35,  # DWMWA_CAPTION_COLOR
                    ctypes.byref(ctypes.c_uint(rgb_color)),  # 颜色值指针
                    ctypes.sizeof(ctypes.c_uint)  # 数据大小
                )
            except Exception as e:
                logger.error(f"设置标题栏颜色失败: {str(e)}")

    def accept(self):
        """保存上课时间段设置"""
        time_settings = self.textEdit.toPlainText()
        try:
            # 确保Settings目录存在
            from app.common.path_utils import path_manager
            time_settings_file = path_manager.get_settings_path('time_settings.json')
            os.makedirs(os.path.dirname(time_settings_file), exist_ok=True)
            
            settings = {}
            if path_manager.file_exists(time_settings_file):
                with open_file(time_settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
            
            # 处理多个时间段输入
            time_list = [time.strip() for time in time_settings.split('\n') if time.strip()]
            
            # 清空现有设置
            if 'non_class_times' in settings:
                settings['non_class_times'] = {}
            if 'class_times' in settings:
                settings['class_times'] = []
            
            # 验证并收集所有有效时间段
            valid_class_times = []
            for time_str in time_list:
                try:
                    # 验证时间段格式
                    time_str = time_str.replace('：', ':')  # 中文冒号转英文
                    
                    # 检查是否为时间段格式 (HH:MM-HH:MM)
                    if '-' in time_str:
                        parts = time_str.split('-')
                        if len(parts) != 2:
                            raise ValueError(f"时间段格式应为'开始时间-结束时间'，例如：08:00-08:40，当前输入: {time_str}")
                        
                        start_time, end_time = parts
                        
                        # 验证开始时间
                        start_parts = start_time.split(':')
                        if len(start_parts) == 2:
                            start_hours, start_minutes = start_parts
                            start_seconds = '00'
                            start_time = f"{start_hours}:{start_minutes}:{start_seconds}"
                        elif len(start_parts) == 3:
                            start_hours, start_minutes, start_seconds = start_parts
                        else:
                            raise ValueError(f"开始时间格式应为'HH:MM'或'HH:MM:SS'，当前输入: {start_time}")
                        
                        # 验证结束时间
                        end_parts = end_time.split(':')
                        if len(end_parts) == 2:
                            end_hours, end_minutes = end_parts
                            end_seconds = '00'
                            end_time = f"{end_hours}:{end_minutes}:{end_seconds}"
                        elif len(end_parts) == 3:
                            end_hours, end_minutes, end_seconds = end_parts
                        else:
                            raise ValueError(f"结束时间格式应为'HH:MM'或'HH:MM:SS'，当前输入: {end_time}")
                        
                        # 确保所有部分都存在
                        if not all([start_hours, start_minutes, start_seconds]):
                            raise ValueError(f"开始时间格式不完整，应为'HH:MM'或'HH:MM:SS'，当前输入: {start_time}")
                        if not all([end_hours, end_minutes, end_seconds]):
                            raise ValueError(f"结束时间格式不完整，应为'HH:MM'或'HH:MM:SS'，当前输入: {end_time}")
                            
                        start_hours = int(start_hours.strip())
                        start_minutes = int(start_minutes.strip())
                        start_seconds = int(start_seconds.strip())
                        
                        end_hours = int(end_hours.strip())
                        end_minutes = int(end_minutes.strip())
                        end_seconds = int(end_seconds.strip())
                        
                        if start_hours < 0 or start_hours > 23:
                            raise ValueError(f"开始小时数必须在0-23之间，当前输入: {start_hours}")
                        if start_minutes < 0 or start_minutes > 59:
                            raise ValueError(f"开始分钟数必须在0-59之间，当前输入: {start_minutes}")
                        if start_seconds < 0 or start_seconds > 59:
                            raise ValueError(f"开始秒数必须在0-59之间，当前输入: {start_seconds}")
                        
                        if end_hours < 0 or end_hours > 23:
                            raise ValueError(f"结束小时数必须在0-23之间，当前输入: {end_hours}")
                        if end_minutes < 0 or end_minutes > 59:
                            raise ValueError(f"结束分钟数必须在0-59之间，当前输入: {end_minutes}")
                        if end_seconds < 0 or end_seconds > 59:
                            raise ValueError(f"结束秒数必须在0-59之间，当前输入: {end_seconds}")
                        
                        # 验证开始时间是否早于结束时间
                        start_total_seconds = start_hours * 3600 + start_minutes * 60 + start_seconds
                        end_total_seconds = end_hours * 3600 + end_minutes * 60 + end_seconds
                        
                        if start_total_seconds >= end_total_seconds:
                            raise ValueError(f"开始时间必须早于结束时间，当前输入: {time_str}")
                        
                        valid_class_times.append({
                            'start': start_time,
                            'end': end_time,
                            'raw': time_str
                        })
                    else:
                        # 如果不是时间段格式，则作为错误处理
                        raise ValueError(f"请输入时间段格式，例如：08:00-08:40，当前输入: {time_str}")
                except Exception as e:
                    logger.error(f"时间段格式验证失败: {str(e)}")
                    continue
            
            # 按开始时间排序
            valid_class_times.sort(key=lambda x: tuple(map(int, x['start'].split(':'))))
            
            # 保存上课时间段
            settings['class_times'] = [time_info['raw'] for time_info in valid_class_times]
            
            # 生成非上课时间段（用于清理）
            non_class_times_list = []
            current_time = 0  # 从0点开始
            
            for class_time in valid_class_times:
                start_time = class_time['start']
                end_time = class_time['end']
                
                # 计算开始和结束时间的总秒数
                start_parts = list(map(int, start_time.split(':')))
                end_parts = list(map(int, end_time.split(':')))
                
                start_total_seconds = start_parts[0] * 3600 + start_parts[1] * 60 + start_parts[2]
                end_total_seconds = end_parts[0] * 3600 + end_parts[1] * 60 + end_parts[2]
                
                # 如果当前时间早于上课开始时间，则添加当前时间到上课开始时间的清理时间段
                if current_time < start_total_seconds:
                    non_class_times_list.append(self._seconds_to_time_string(current_time) + '-' + start_time)
                
                # 更新当前时间为上课结束时间
                current_time = end_total_seconds
            
            # 如果最后一段不是到24点，则添加最后一段清理时间段
            if current_time < 24 * 3600:
                non_class_times_list.append(self._seconds_to_time_string(current_time) + '-24:00:00')
            
            # 保存清理时间段
            for idx, time_str in enumerate(non_class_times_list, 1):
                settings.setdefault('non_class_times', {})[str(idx)] = time_str
            
            with open_file(time_settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=4)
                logger.info(f"成功保存{len(time_list)}个上课时间段设置，生成了{len(non_class_times_list)}个清理时间段")
                InfoBar.success(
                    title='设置成功',
                    content=f"成功保存{len(time_list)}个上课时间段，生成了{len(non_class_times_list)}个清理时间段!",
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=3000,
                    parent=self
                )
                self.saved = True
                super().accept()
        except Exception as e:
            logger.error(f"保存上课时间段失败: {str(e)}")
            InfoBar.error(
                title='设置失败',
                content=f"保存上课时间段失败: {str(e)}",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )
    
    def _seconds_to_time_string(self, total_seconds):
        """将总秒数转换为时间字符串(HH:MM:SS格式)"""
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
