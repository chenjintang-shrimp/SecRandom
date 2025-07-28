from qfluentwidgets import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtMultimedia import *

import os
import glob
import sys
import json
import random
import pyttsx3
import platform
import re
import datetime
import math
from loguru import logger
from random import SystemRandom
system_random = SystemRandom()

from app.common.config import get_theme_icon, load_custom_font, restore_volume

class pumping_people(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # 定义变量
        self.is_animating = False
        self.draw_mode = "random"
        self.animation_timer = None
        # 音乐播放器初始化 ✧(◍˃̶ᗜ˂̶◍)✩ 感谢白露提供的播放器
        self.music_player = QMediaPlayer()
        # 使用全局语音引擎单例
        # 检查系统版本是否为Windows 10及以上且非x86架构
        if sys.platform == 'win32' and sys.getwindowsversion().major >= 10 and platform.machine() != 'x86':
            if not hasattr(QApplication.instance(), 'pumping_reward_voice_engine'):
                QApplication.instance().pumping_reward_voice_engine = pyttsx3.init()
                QApplication.instance().pumping_reward_voice_engine.startLoop(False)
            self.voice_engine = QApplication.instance().pumping_reward_voice_engine
        else:
            logger.warning("语音功能仅在Windows 10及以上系统且非x86架构可用")
        self.initUI()
    
    def start_draw(self):
        """开始抽选学生"""
        # 获取抽选模式和动画模式设置
        try:
            with open('app/Settings/Settings.json', 'r', encoding='utf-8') as f:
                settings = json.load(f)
                pumping_people_draw_mode = settings['pumping_people']['draw_mode']
                pumping_people_animation_mode = settings['pumping_people']['animation_mode']
                self.interval = settings['pumping_people']['animation_interval']
                self.auto_play = settings['pumping_people']['animation_auto_play']
                self.animation_music_enabled = settings['pumping_people']['animation_music_enabled']
                self.result_music_enabled = settings['pumping_people']['result_music_enabled']
                self.animation_music_volume = settings['pumping_people']['animation_music_volume']
                self.result_music_volume = settings['pumping_people']['result_music_volume']
                self.music_fade_in = settings['pumping_people']['music_fade_in']
                self.music_fade_out = settings['pumping_people']['music_fade_out']
                
        except Exception as e:
            pumping_people_draw_mode = 0
            pumping_people_animation_mode = 0
            self.interval = 100
            self.auto_play = 5
            self.animation_music_enabled = False
            self.result_music_enabled = False
            self.animation_music_volume = 5
            self.result_music_volume = 5
            self.music_fade_in = 300
            self.music_fade_out = 300
            logger.error(f"加载设置时出错: {e}, 使用默认设置")

        # 根据抽选模式执行不同逻辑
        # 跟随全局设置
        if pumping_people_draw_mode == 0:  # 重复随机
            self.draw_mode = "random"
        elif pumping_people_draw_mode == 1:  # 不重复抽取(直到软件重启)
            self.draw_mode = "until_reboot"
        elif pumping_people_draw_mode == 2:  # 不重复抽取(直到抽完全部人)
            self.draw_mode = "until_all"
            
        # 根据动画模式执行不同逻辑
        if pumping_people_animation_mode == 0:  # 手动停止动画
            self.start_button.setText("停止")
            if self.animation_music_enabled:
                self._play_animation_music()
            self.is_animating = True
            self.animation_timer = QTimer()
            self.animation_timer.timeout.connect(self._show_random_student)
            self.animation_timer.start(self.interval)
            self.start_button.clicked.disconnect()
            self.start_button.clicked.connect(self._stop_animation)
            
        elif pumping_people_animation_mode == 1:  # 自动播放完整动画
            self._play_full_animation()
            
        elif pumping_people_animation_mode == 2:  # 直接显示结果
            self._show_result_directly()
        
    def _show_random_student(self):
        """显示随机学生（用于动画效果）"""
        class_name = self.class_combo.currentText()
        group_name = self.group_combo.currentText()
        genders = self.gender_combo.currentText()

        if class_name and class_name not in ["你暂未添加班级", "加载班级列表失败", "你暂未添加小组", "加载小组列表失败"] and group_name and group_name not in ["你暂未添加小组", "加载小组列表失败"]:
            student_file = f"app/resource/list/{class_name}.json"

            if self.draw_mode == "until_reboot":
                if group_name == '抽取全班学生':
                    draw_record_file = f"app/resource/Temp/until_the_reboot_{class_name}_{group_name}_{genders}.json"
                elif group_name == '抽取小组组号':
                    draw_record_file = f"app/resource/Temp/until_the_reboot_{class_name}_{group_name}.json"
                else:
                    draw_record_file = f"app/resource/Temp/until_the_reboot_{class_name}_{group_name}_{genders}.json"
            elif self.draw_mode == "until_all":
                if group_name == '抽取全班学生':
                    draw_record_file = f"app/resource/Temp/until_all_draw_{class_name}_{group_name}_{genders}.json"
                elif group_name == '抽取小组组号':
                    draw_record_file = f"app/resource/Temp/until_all_draw_{class_name}_{group_name}.json"
                else:
                    draw_record_file = f"app/resource/Temp/until_all_draw_{class_name}_{group_name}_{genders}.json"
            
            if self.draw_mode in ["until_reboot", "until_all"]:
                # 创建Temp目录如果不存在
                os.makedirs(os.path.dirname(draw_record_file), exist_ok=True)
                
                # 初始化抽取记录文件
                if not os.path.exists(draw_record_file):
                    with open(draw_record_file, 'w', encoding='utf-8') as f:
                        json.dump([], f, ensure_ascii=False, indent=4)
                
                # 读取已抽取记录
                drawn_students = []
                with open(draw_record_file, 'r', encoding='utf-8') as f:
                    try:
                        drawn_students = json.load(f)
                    except json.JSONDecodeError:
                        drawn_students = []
            else:
                drawn_students = []

            if os.path.exists(student_file):
                with open(student_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    cleaned_data = []
                    # 获取学生列表
                    if group_name == '抽取全班学生':
                        if genders == '抽取所有性别':
                            for student_name, student_info in data.items():
                                if isinstance(student_info, dict) and 'id' in student_info:
                                    id = student_info.get('id', '')
                                    name = student_name.replace('【', '').replace('】', '')
                                    gender = student_info.get('gender', '')
                                    group = student_info.get('group', '')
                                    exist = student_info.get('exist', True)
                                    cleaned_data.append((id, name, exist))
                        else:
                            for student_name, student_info in data.items():
                                if isinstance(student_info, dict) and 'id' in student_info:
                                    id = student_info.get('id', '')
                                    name = student_name.replace('【', '').replace('】', '')
                                    gender = student_info.get('gender', '')
                                    group = student_info.get('group', '')
                                    exist = student_info.get('exist', True)
                                    if gender == genders:
                                        cleaned_data.append((id, name, exist))
                    elif group_name == '抽取小组组号':
                        groups = set()
                        for student_name, student_info in data.items():
                            if isinstance(student_info, dict) and 'id' in student_info:
                                id = student_info.get('id', '')
                                name = student_name.replace('【', '').replace('】', '')
                                gender = student_info.get('gender', '')
                                group = student_info.get('group', '')
                                exist = student_info.get('exist', True)
                                if group:  # 只添加非空小组
                                    groups.add((id, group, exist))
                        cleaned_data = sorted(list(groups), key=lambda x: self.sort_key(str(x)))
                    else:
                        if genders == '抽取所有性别':
                            for student_name, student_info in data.items():
                                if isinstance(student_info, dict) and 'id' in student_info:
                                    id = student_info.get('id', '')
                                    name = student_name.replace('【', '').replace('】', '')
                                    gender = student_info.get('gender', '')
                                    group = student_info.get('group', '')
                                    exist = student_info.get('exist', True)
                                    if group == group_name:
                                        cleaned_data.append((id, name, exist))
                        else:
                            for student_name, student_info in data.items():
                                if isinstance(student_info, dict) and 'id' in student_info:
                                    id = student_info.get('id', '')
                                    name = student_name.replace('【', '').replace('】', '')
                                    gender = student_info.get('gender', '')
                                    group = student_info.get('group', '')
                                    exist = student_info.get('exist', True)
                                    if gender == genders and group == group_name:
                                        cleaned_data.append((id, name, exist))

                    # 过滤学生信息的exist为False的学生
                    cleaned_data = list(filter(lambda x: x[2], cleaned_data))

                    # 如果所有学生都已抽取过，则使用全部学生名单
                    students = [s for s in cleaned_data if s[1].replace(' ', '') not in [x.replace(' ', '') for x in drawn_students]] or cleaned_data

                    if students:
                        # 从self.current_count获取抽取人数
                        draw_count = self.current_count
                        
                        # 抽取多个学生
                        selected_students = random.sample(students, min(draw_count, len(students)))
                        
                        # 清除旧布局和标签
                        if hasattr(self, 'container') and isinstance(self.container, list):
                            for label in self.container:
                                label.deleteLater()
                            self.container = []
                        elif hasattr(self, 'container') and isinstance(self.container, QWidget):
                            try:
                                if self.container:
                                    self.container.deleteLater()
                            except RuntimeError:
                                pass
                            del self.container

                        if hasattr(self, 'student_labels'):
                            for label in self.student_labels:
                                try:
                                    if label:
                                        label.deleteLater()
                                except RuntimeError:
                                    pass
                            self.student_labels = []
                            
                        # 删除布局中的所有内容
                        while self.result_grid.count(): 
                            item = self.result_grid.takeAt(0)
                            widget = item.widget()
                            if widget:
                                try:
                                    widget.deleteLater()
                                except RuntimeError:
                                    pass
                        
                        # 根据设置格式化学号显示
                        try:
                            with open('app/Settings/Settings.json', 'r', encoding='utf-8') as f:
                                settings = json.load(f)
                                pumping_people_student_id = settings['pumping_people']['student_id']
                                pumping_people_student_name = settings['pumping_people']['student_name']
                        except Exception as e:
                            pumping_people_student_id = 0
                            pumping_people_student_name = 0
                            logger.error(f"加载设置时出错: {e}, 使用默认设置")

                        # 创建新布局
                        vbox_layout = QGridLayout()
                        # 创建新标签列表
                        self.student_labels = []
                        for num, selected, exist in selected_students:
                            # 整合学号格式和姓名处理逻辑
                            student_id_format = pumping_people_student_id
                            student_name_format = pumping_people_student_name
                            
                            # 根据学号格式生成标签文本
                            if student_id_format == 0:  # 补零
                                student_id_str = f"{num:02}"
                            elif student_id_format == 1:  # 居中显示
                                student_id_str = f"{num:^5}"
                            else:
                                student_id_str = f"{num:02}"
                            
                            # 处理两字姓名
                            if student_name_format == 0 and len(selected) == 2:
                                name = f"{selected[0]}    {selected[1]}"
                            else:
                                name = selected

                            if group_name == '抽取小组组号':
                                # 定义格式常量
                                FORMAT_GROUP_RANDOM_MEMBER = 0
                                FORMAT_GROUP_RANDOM = 1
                                FORMAT_GROUP_SIMPLE = 2
                                FORMAT_GROUP_ARROW = 3
                                FORMAT_GROUP_ARROW_BRACKET = 4

                                # 格式映射字典
                                FORMAT_MAPPINGS = {
                                    FORMAT_GROUP_RANDOM_MEMBER: f"{{selected}}-随机组员:{{random_member}}",
                                    FORMAT_GROUP_RANDOM: f"{{selected}}-随机:{{random_member}}",
                                    FORMAT_GROUP_SIMPLE: f"{{selected}}-{{random_member}}",
                                    FORMAT_GROUP_ARROW: f"{{selected}}>{{random_member}}",
                                    FORMAT_GROUP_ARROW_BRACKET: f"{{selected}}>{{random_member}}<"
                                }

                                # 构建学生数据文件路径
                                student_file = os.path.join("app", "resource", "list", f"{self.class_combo.currentText()}.json")
                                members = []

                                # 加载学生数据和筛选组成员
                                if os.path.exists(student_file):
                                    try:
                                        with open(student_file, 'r', encoding='utf-8') as f:
                                            data = json.load(f)
                                            members = [
                                                name.replace('【', '').replace('】', '') 
                                                for name, info in data.items()
                                                if isinstance(info, dict) and info.get('group') == selected and info.get('exist', True)
                                            ]
                                    except (json.JSONDecodeError, IOError) as e:
                                        # 记录具体错误但不中断程序
                                        print(f"加载学生数据失败: {str(e)}")

                                # 随机选择成员
                                random_member = random.choice(members) if members else ''
                                display_text = selected  # 默认显示组号

                                # 加载显示设置
                                try:
                                    with open('app/Settings/Settings.json', 'r', encoding='utf-8') as f:
                                        settings = json.load(f)
                                        show_random = settings['pumping_people'].get('show_random_member', False)
                                        format_str = settings['pumping_people'].get('random_member_format', FORMAT_GROUP_SIMPLE)
                                except (json.JSONDecodeError, IOError, KeyError) as e:
                                    show_random = False
                                    format_str = FORMAT_GROUP_SIMPLE
                                    print(f"加载设置失败: {str(e)}")

                                # 应用格式设置
                                if show_random and random_member and format_str in FORMAT_MAPPINGS:
                                    display_text = FORMAT_MAPPINGS[format_str].format(
                                        selected=selected, 
                                        random_member=random_member
                                    )

                                label = BodyLabel(display_text)
                            else:
                                label = BodyLabel(f"{student_id_str} {name}")

                            label.setAlignment(Qt.AlignCenter)
                            # 读取设置中的font_size值
                            try:
                                with open('app/Settings/Settings.json', 'r', encoding='utf-8') as f:
                                    settings = json.load(f)
                                    font_size = settings['pumping_people']['font_size']
                                    if font_size < 30:
                                        font_size = 85
                            except Exception as e:
                                font_size = 85
                                logger.error(f"加载字体设置时出错: {e}, 使用默认设置")
                            # 根据设置调整字体大小
                            if font_size < 30:
                                label.setFont(QFont(load_custom_font(), 85))
                            else:
                                label.setFont(QFont(load_custom_font(), font_size))
                            self.student_labels.append(label)
                            vbox_layout.addWidget(label)

                        # 计算所有标签的宽度之和，并考虑间距和边距
                        if self.student_labels:
                            total_width = sum(label.sizeHint().width() for label in self.student_labels) + \
                                          len(self.student_labels) * 180
                            available_width = self.width() - 20
                            
                            # 如果总宽度超过可用宽度，则计算每行最多能放几个标签
                            if total_width > available_width:
                                avg_label_width = total_width / len(self.student_labels)
                                max_columns = max(1, int(available_width // avg_label_width))
                            else:
                                max_columns = len(self.student_labels)  # 一行显示所有标签
                        else:
                            max_columns = 1
                        
                        # 复用 container 和 vbox_layout
                        if not hasattr(self, 'container'):
                            self.container = QWidget()
                            self.vbox_layout = QGridLayout()
                            self.container.setLayout(self.vbox_layout)
                        else:
                            # 清空旧标签
                            for i in reversed(range(self.vbox_layout.count())):
                                item = self.vbox_layout.itemAt(i)
                                if item.widget():
                                    item.widget().setParent(None)

                        for i, label in enumerate(self.student_labels):
                            row = i // max_columns
                            col = i % max_columns
                            self.vbox_layout.addWidget(label, row, col)
                        
                        self.result_grid.addWidget(self.container)
                        
                        return
                    else:
                        return

        
        else:
            self.clear_layout(self.result_grid)
            if hasattr(self, 'container'):
                self.container.deleteLater()
                del self.container
            if hasattr(self, 'student_labels'):
                for label in self.student_labels:
                    label.deleteLater()
            
            # 创建错误标签
            error_label = BodyLabel("-- 抽选失败")
            error_label.setAlignment(Qt.AlignCenter)
            
            # 获取字体大小设置
            font_size = 85
            try:
                with open('app/Settings/Settings.json', 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    font_size = max(settings['pumping_people']['font_size'], 30)
            except Exception as e:
                logger.error(f"加载字体设置时出错: {e}, 使用默认设置")
            
            error_label.setFont(QFont(load_custom_font(), font_size))
            self.result_grid.addWidget(error_label)
    
    # 停止动画并显示最终结果
    def _stop_animation(self):
        """停止动画并显示最终结果"""
        self.animation_timer.stop()
        if self.animation_music_enabled:
            # 创建音量渐出动画 ～(￣▽￣)～* 白露负责温柔收尾
            self.fade_out_animation = QPropertyAnimation(self.music_player, b"volume")
            self.fade_out_animation.setDuration(self.music_fade_out)
            self.fade_out_animation.setStartValue(self.music_player.volume())
            self.fade_out_animation.setEndValue(0)
            self.fade_out_animation.setEasingCurve(QEasingCurve.InOutQuad)
        
            # 动画结束后停止播放
            def stop_after_fade():
                self.music_player.stop()
                self.music_player.setVolume(100)  # 重置音量为最大，准备下次播放
            
            self.fade_out_animation.finished.connect(stop_after_fade)
            self.fade_out_animation.start()
        if self.result_music_enabled:
            self._play_result_music()
        self.is_animating = False
        self.start_button.setText("开始")
        self.start_button.clicked.disconnect()
        self.start_button.clicked.connect(self.start_draw)
        
        # 显示最终结果
        self.random()
        self.voice_play()
    
    def _play_full_animation(self):
        """播放完整动画（快速显示n个随机学生后显示最终结果）
        星野：动画开始啦~ 让我们看看谁是幸运儿！🎡
        白露：背景音乐和动画会同步播放哦~ 🎵"""
        self.is_animating = True
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self._show_random_student)
        self.animation_timer.start(self.interval)
        if self.animation_music_enabled:
            self._play_animation_music()
        self.start_button.setEnabled(False)  # 禁用按钮（星野：抽奖中不能重复点击哦~）
        
        # n次随机后停止
        QTimer.singleShot(self.auto_play * self.interval, lambda: [
            self.animation_timer.stop(),
            self._stop_animation(),
            self.start_button.setEnabled(True)  # 白露：按钮恢复啦~ 可以再次抽奖哦！😊
          ])
    
    # 直接显示结果（无动画效果）
    def _show_result_directly(self):
        """直接显示结果（无动画效果）"""
        if self.result_music_enabled:
            self._play_result_music()
        self.random()
        self.voice_play()

    def _play_result_music(self):
        """播放结果音乐
        星野：恭喜你抽中啦！🎉 来听听胜利的音乐吧~
        白露：结果音乐和动画音乐是分开的呢~ 真有趣！"""
        try:
            BGM_RESULT_PATH = os.path.abspath('./app/resource/music/pumping_people/result_music')
            # 检查音乐目录是否存在
            if not os.path.exists(BGM_RESULT_PATH):
                logger.warning(f"结果音乐目录不存在: {BGM_RESULT_PATH}")
                return

            # 获取所有支持的音乐文件 (｡･ω･｡)ﾉ♡
            music_extensions = ['*.mp3', '*.wav', '*.ogg', '*.flac']
            music_files = []
            for ext in music_extensions:
                music_files.extend(glob.glob(os.path.join(BGM_RESULT_PATH, ext)))

            if not music_files:
                logger.warning(f"结果音乐目录中没有找到音乐文件: {BGM_RESULT_PATH}")
                return

            # 随机选择一首音乐 ♪(^∇^*)
            selected_music = random.choice(music_files)
            logger.info(f"正在播放结果音乐: {selected_music}")

            # 设置并播放音乐，准备渐入效果 ✧*｡٩(ˊᗜˋ*)و✧*｡
            self.music_player.setMedia(QMediaContent(QUrl.fromLocalFile(selected_music)))
            if self.music_player.mediaStatus() == QMediaPlayer.InvalidMedia:
                logger.error(f"无效的媒体文件: {selected_music}")
                return
            self.music_player.setVolume(0)  # 初始音量设为0
            self.music_player.play()
            # 连接错误信号
            self.music_player.error.connect(self.handle_media_error)
            
            # 创建音量渐入动画 ～(￣▽￣)～* 星野的魔法音量调节
            self.fade_in_animation = QPropertyAnimation(self.music_player, b"volume")
            self.fade_in_animation.setDuration(self.music_fade_in)
            self.fade_in_animation.setStartValue(0)
            self.fade_in_animation.setEndValue(self.result_music_volume)
            self.fade_in_animation.setEasingCurve(QEasingCurve.InOutQuad)
            self.fade_in_animation.start()

            if self.music_player.state() == QMediaPlayer.PlayingState:
                # 创建音量渐出动画
                fade_out_animation = QPropertyAnimation(self.music_player, b"volume")
                fade_out_animation.setDuration(self.music_fade_out)
                fade_out_animation.setStartValue(self.music_player.volume())
                fade_out_animation.setEndValue(0)
                fade_out_animation.setEasingCurve(QEasingCurve.InOutQuad)

                # 动画结束后停止播放并重置音量
                def final_stop():
                    self.music_player.stop()
                    self.music_player.setVolume(self.result_music_volume)

                fade_out_animation.finished.connect(final_stop)
                fade_out_animation.start()

        except Exception as e:
            logger.error(f"播放结果音乐时出错: {e}")

    def _play_animation_music(self):
        """播放动画背景音乐 ～(￣▽￣)～* 星野和白露的音乐时间"""
        try:
            BGM_ANIMATION_PATH = os.path.abspath('./app/resource/music/pumping_people/Animation_music')
            # 检查音乐目录是否存在
            if not os.path.exists(BGM_ANIMATION_PATH):
                logger.warning(f"音乐目录不存在: {BGM_ANIMATION_PATH}")
                return

            # 获取所有支持的音乐文件 (｡･ω･｡)ﾉ♡
            music_extensions = ['*.mp3', '*.wav', '*.ogg', '*.flac']
            music_files = []
            for ext in music_extensions:
                music_files.extend(glob.glob(os.path.join(BGM_ANIMATION_PATH, ext)))

            if not music_files:
                logger.warning(f"音乐目录中没有找到音乐文件: {BGM_ANIMATION_PATH}")
                return

            # 随机选择一首音乐 ♪(^∇^*)
            selected_music = random.choice(music_files)
            logger.info(f"正在播放音乐: {selected_music}")

            # 设置并播放音乐，准备渐入效果 ✧*｡٩(ˊᗜˋ*)و✧*｡
            self.music_player.setMedia(QMediaContent(QUrl.fromLocalFile(selected_music)))
            if self.music_player.mediaStatus() == QMediaPlayer.InvalidMedia:
                logger.error(f"无效的媒体文件: {selected_music}")
                return
            self.music_player.setVolume(0)  # 初始音量设为0
            self.music_player.play()
            # 连接错误信号
            self.music_player.error.connect(self.handle_media_error)
            
            # 创建音量渐入动画 ～(￣▽￣)～* 星野的魔法音量调节
            self.fade_in_animation = QPropertyAnimation(self.music_player, b"volume")
            self.fade_in_animation.setDuration(self.music_fade_in)
            self.fade_in_animation.setStartValue(0)
            self.fade_in_animation.setEndValue(self.animation_music_volume)
            self.fade_in_animation.setEasingCurve(QEasingCurve.InOutQuad)
            self.fade_in_animation.start()
        except Exception as e:
            logger.error(f"播放音乐时出错: {e}")

    def handle_media_error(self, error):
        """处理媒体播放错误 ～(T_T)～ 星野的音乐播放失败了"""
        error_str = self.music_player.errorString()
        logger.error(f"媒体播放错误: {error_str} (错误代码: {error})")
        self.music_player.stop()

    def voice_play(self):
        """语音播报部分"""
        try:
            with open('app/Settings/Settings.json', 'r', encoding='utf-8') as f:
                settings = json.load(f)
                voice_enabled = settings['pumping_people']['voice_enabled']
                system_volume_enabled = settings['pumping_people']['system_volume_enabled']
                voice_volume = settings['pumping_people'].get('voice_volume', 100) / 100.0
                voice_speed = settings['pumping_people'].get('voice_speed', 100)
                volume_value = settings['pumping_people'].get('system_volume_value', 50)
                
                if voice_enabled == True:  # 开启语音
                    if system_volume_enabled == True: # 开启系统音量
                        # 设置系统音量
                        restore_volume(volume_value)
                    # 设置音量
                    self.voice_engine.setProperty('volume', voice_volume)
                    # 设置语速
                    self.voice_engine.setProperty('rate', int(200 * (voice_speed / 100)))
                    if hasattr(self, 'student_labels'):
                        for label in self.student_labels:
                            parts = label.text().split()
                            if len(parts) >= 2 and len(parts[-1]) == 1 and len(parts[-2]) == 1:
                                name = parts[-2] + parts[-1]
                            else:
                                name = parts[-1]
                            name = name.replace(' ', '')
                            self.voice_engine.say(f"{name}")
                            self.voice_engine.iterate()
        except Exception as e:
            logger.error(f"语音播报出错: {e}")
    
    # 根据抽取模式抽选学生
    def random(self):
        """根据抽取模式抽选学生"""
        class_name = self.class_combo.currentText()
        group_name = self.group_combo.currentText()
        genders = self.gender_combo.currentText()
        
        if class_name and class_name not in ["你暂未添加班级", "加载班级列表失败", "你暂未添加小组", "加载小组列表失败"] and group_name and group_name not in ["你暂未添加小组", "加载小组列表失败"]:
            student_file = f"app/resource/list/{class_name}.json"

            if self.draw_mode == "until_reboot":
                if group_name == '抽取全班学生':
                    draw_record_file = f"app/resource/Temp/until_the_reboot_{class_name}_{group_name}_{genders}.json"
                elif group_name == '抽取小组组号':
                    draw_record_file = f"app/resource/Temp/until_the_reboot_{class_name}_{group_name}.json"
                else:
                    draw_record_file = f"app/resource/Temp/until_the_reboot_{class_name}_{group_name}_{genders}.json"
            elif self.draw_mode == "until_all":
                if group_name == '抽取全班学生':
                    draw_record_file = f"app/resource/Temp/until_all_draw_{class_name}_{group_name}_{genders}.json"
                elif group_name == '抽取小组组号':
                    draw_record_file = f"app/resource/Temp/until_all_draw_{class_name}_{group_name}.json"
                else:
                    draw_record_file = f"app/resource/Temp/until_all_draw_{class_name}_{group_name}_{genders}.json"
            
            if self.draw_mode in ["until_reboot", "until_all"]:
                # 创建Temp目录如果不存在
                os.makedirs(os.path.dirname(draw_record_file), exist_ok=True)
                
                # 初始化抽取记录文件
                if not os.path.exists(draw_record_file):
                    with open(draw_record_file, 'w', encoding='utf-8') as f:
                        json.dump([], f, ensure_ascii=False, indent=4)
                
                # 读取已抽取记录
                drawn_students = []
                with open(draw_record_file, 'r', encoding='utf-8') as f:
                    try:
                        drawn_students = json.load(f)
                    except json.JSONDecodeError:
                        drawn_students = []
            else:
                drawn_students = []
            
            if os.path.exists(student_file):
                with open(student_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    cleaned_data = []
                    __cleaned_data = []
                    
                    # 获取学生列表
                    if group_name == '抽取全班学生':
                        if genders == '抽取所有性别':
                            for student_name, student_info in data.items():
                                if isinstance(student_info, dict) and 'id' in student_info:
                                    id = student_info.get('id', '')
                                    name = student_name.replace('【', '').replace('】', '')
                                    gender = student_info.get('gender', '')
                                    group = student_info.get('group', '')
                                    exist = student_info.get('exist', True)
                                    cleaned_data.append((id, name, exist))
                                    __cleaned_data.append((id, name, gender, group, exist))
                        else:
                            for student_name, student_info in data.items():
                                if isinstance(student_info, dict) and 'id' in student_info:
                                    id = student_info.get('id', '')
                                    name = student_name.replace('【', '').replace('】', '')
                                    gender = student_info.get('gender', '')
                                    group = student_info.get('group', '')
                                    exist = student_info.get('exist', True)
                                    if gender == genders:
                                        cleaned_data.append((id, name, exist))
                                        __cleaned_data.append((id, name, gender, group, exist))
                    elif group_name == '抽取小组组号':
                        groups = set()
                        for student_name, student_info in data.items():
                            if isinstance(student_info, dict) and 'id' in student_info:
                                id = student_info.get('id', '')
                                name = student_name.replace('【', '').replace('】', '')
                                gender = student_info.get('gender', '')
                                group = student_info.get('group', '')
                                exist = student_info.get('exist', True)
                                if group:  # 只添加非空小组
                                    groups.add((id, group, exist))
                                    __cleaned_data.append((id, name, gender, group, exist))
                        cleaned_data = sorted(list(groups), key=lambda x: self.sort_key(str(x)))
                    else:
                        if genders == '抽取所有性别':
                            for student_name, student_info in data.items():
                                if isinstance(student_info, dict) and 'id' in student_info:
                                    id = student_info.get('id', '')
                                    name = student_name.replace('【', '').replace('】', '')
                                    gender = student_info.get('gender', '')
                                    group = student_info.get('group', '')
                                    exist = student_info.get('exist', True)
                                    if group == group_name:
                                        cleaned_data.append((id, name, exist))
                                        __cleaned_data.append((id, name, gender, group, exist))
                        else:
                            for student_name, student_info in data.items():
                                if isinstance(student_info, dict) and 'id' in student_info:
                                    id = student_info.get('id', '')
                                    name = student_name.replace('【', '').replace('】', '')
                                    gender = student_info.get('gender', '')
                                    group = student_info.get('group', '')
                                    exist = student_info.get('exist', True)
                                    if gender == genders and group == group_name:
                                        cleaned_data.append((id, name, exist))
                                        __cleaned_data.append((id, name, gender, group, exist))

                    # 过滤学生信息的exist为False的学生
                    cleaned_data = list(filter(lambda x: x[2], cleaned_data))
                    __cleaned_data = list(filter(lambda x: x[4], __cleaned_data))

                    if self.draw_mode == "random":
                        available_students = cleaned_data
                    elif self.draw_mode == "until_reboot" or self.draw_mode == "until_all":
                        available_students = [s for s in cleaned_data if s[1].replace(' ', '') not in [x.replace(' ', '') for x in drawn_students]]

                    if available_students:
                        # 从self.current_count获取抽取人数
                        draw_count = self.current_count
                        
                        # 根据设置选项选择随机方法
                        use_system_random = self.get_random_method_setting()
                        
                        if use_system_random == 1:  # 使用SystemRandom的方式-不可预测抽取
                            if len(available_students) <= draw_count:
                                selected_students = available_students
                            else:
                                selected_students = system_random.sample(available_students, draw_count)

                        elif use_system_random == 2 or use_system_random == 3:  # 动态权重调整抽取系统
                            # 加载历史记录
                            history_file = f"app/resource/history/{class_name}.json"
                            history_data = {}
                            if os.path.exists(history_file):
                                with open(history_file, 'r', encoding='utf-8') as f:
                                    try:
                                        history_data = json.load(f)
                                    except json.JSONDecodeError:
                                        history_data = {}
                            
                            # 初始化权重数据
                            weights = {}
                            
                            for student_id, student_name, exist in available_students:
                                # 获取学生历史记录
                                student_history = history_data.get("pumping_people", {}).get(student_name, {
                                    "total_number_of_times": 0,
                                    "last_drawn_time": None,
                                    "rounds_missed": 0,
                                    "time": []
                                })
                                
                                # 基础参数配置
                                COLD_START_ROUNDS = 10       # 冷启动轮次
                                BASE_WEIGHT = 1.0            # 基础权重

                                # 计算各权重因子
                                # 因子1: 抽取频率惩罚（被抽中次数越多权重越低）
                                frequency_factor = 1.0 / math.sqrt(student_history["total_number_of_times"] * 2 + 1)

                                # 因子2: 小组平衡（仅当有足够数据时生效）
                                group_factor = 1.0
                                # 获取有效小组统计数量（值>0的条目）
                                valid_groups = [v for v in history_data.get("group_stats", {}).values() if v > 0]
                                if len(valid_groups) > 3:  # 有效小组数量达标
                                    for student in __cleaned_data:
                                        if student[1] == student_name:
                                            current_student_group = student[3]
                                            break
                                    else:
                                        current_student_group = ''
                                    group_history = max(history_data["group_stats"].get(current_student_group, 0), 0)
                                    group_factor = 1.0 / (group_history * 0.2 + 1)

                                # 因子3: 性别平衡（仅当两种性别都有数据时生效）
                                gender_factor = 1.0
                                # 获取有效性别统计数量（值>0的条目）
                                valid_gender = [v for v in history_data.get("gender_stats", {}).values() if v > 0]
                                if len(valid_gender) > 3:  # 有效性别数量达标
                                    for student in __cleaned_data:
                                        if student[1] == student_name:
                                            current_student_gender = student[2]
                                            break
                                    else:
                                        current_student_gender = ''
                                    gender_history = max(history_data["gender_stats"].get(current_student_gender, 0), 0)
                                    gender_factor = 1.0 / (gender_history * 0.2 + 1)

                                # 冷启动特殊处理
                                current_round = history_data.get("total_rounds", 0)
                                if current_round < COLD_START_ROUNDS:
                                    frequency_factor = min(0.8, frequency_factor)  # 防止新学生权重过低

                                # 综合权重计算
                                student_weights = {
                                    'base': BASE_WEIGHT * 0.2,                    # 基础权重
                                    'frequency': frequency_factor * 3.0,          # 频率惩罚
                                    'group': group_factor * 0.8,                  # 小组平衡
                                    'gender': gender_factor * 0.8                 # 性别平衡
                                }

                                if self.draw_mode in ['until_reboot', 'until_all'] and student_name in drawn_students:
                                    # 如果是不重复抽取模式，且该学生已被抽中，则权重为0
                                    comprehensive_weight = 0
                                else:
                                    comprehensive_weight = sum(student_weights.values())

                                # 5. 最终调整与限制
                                # 确保权重在合理范围内 (0.5~5.0)
                                final_weight = max(0.5, min(comprehensive_weight, 5.0))
                                weights[(student_id, student_name, exist)] = final_weight
                            
                            # 根据权重抽取学生
                            selected_students = []
                            remaining_students = available_students.copy()

                            use_system_random = self.get_random_method_setting()
                            if use_system_random == 3:
                                random_module = system_random
                            elif use_system_random == 2:
                                random_module = random
                            else:
                                random_module = random
                            
                            for _ in range(min(draw_count, len(available_students))):
                                total_weight = sum(weights[s] for s in remaining_students)
                                r = random_module.uniform(0, total_weight)
                                accumulator = 0
                                
                                for student in remaining_students:
                                    accumulator += weights[student]
                                    if accumulator >= r:
                                        selected_students.append(student)
                                        remaining_students.remove(student)
                                        break

                        else:  # 默认使用random的方式-可预测抽取
                            if len(available_students) <= draw_count:
                                selected_students = available_students
                            else:
                                selected_students = random.sample(available_students, draw_count)

                        # 更新历史记录
                        self._update_history(class_name, group_name, genders, selected_students)
                        
                        # 显示结果
                        if hasattr(self, 'container'):
                            self.container.deleteLater()
                            del self.container
                        if hasattr(self, 'student_labels'):
                            for label in self.student_labels:
                                label.deleteLater()

                        while self.result_grid.count(): 
                            item = self.result_grid.takeAt(0)
                            widget = item.widget()
                            if widget:
                                widget.deleteLater()
                        
                        try:
                            with open('app/Settings/Settings.json', 'r', encoding='utf-8') as f:
                                settings = json.load(f)
                                pumping_people_student_id = settings['pumping_people']['student_id']
                                pumping_people_student_name = settings['pumping_people']['student_name']
                        except Exception as e:
                            pumping_people_student_id = 0
                            pumping_people_student_name = 0
                            logger.error(f"加载设置时出错: {e}, 使用默认设置")

                        self.student_labels = []
                        for num, selected, exist in selected_students:
                            student_id_format = pumping_people_student_id
                            student_name_format = pumping_people_student_name
                            
                            if student_id_format == 0:
                                student_id_str = f"{num:02}"
                            elif student_id_format == 1:
                                student_id_str = f"{num:^5}"
                            else:
                                student_id_str = f"{num:02}"
                            
                            if student_name_format == 0 and len(selected) == 2:
                                name = f"{selected[0]}    {selected[1]}"
                            else:
                                name = selected

                            if group_name == '抽取小组组号':
                                # 定义格式常量
                                FORMAT_GROUP_RANDOM_MEMBER = 0
                                FORMAT_GROUP_RANDOM = 1
                                FORMAT_GROUP_SIMPLE = 2
                                FORMAT_GROUP_ARROW = 3
                                FORMAT_GROUP_ARROW_BRACKET = 4

                                # 格式映射字典
                                FORMAT_MAPPINGS = {
                                    FORMAT_GROUP_RANDOM_MEMBER: f"{{selected}}-随机组员:{{random_member}}",
                                    FORMAT_GROUP_RANDOM: f"{{selected}}-随机:{{random_member}}",
                                    FORMAT_GROUP_SIMPLE: f"{{selected}}-{{random_member}}",
                                    FORMAT_GROUP_ARROW: f"{{selected}}>{{random_member}}",
                                    FORMAT_GROUP_ARROW_BRACKET: f"{{selected}}>{{random_member}}<"
                                }

                                # 构建学生数据文件路径
                                student_file = os.path.join("app", "resource", "list", f"{self.class_combo.currentText()}.json")
                                members = []

                                # 加载学生数据和筛选组成员
                                if os.path.exists(student_file):
                                    try:
                                        with open(student_file, 'r', encoding='utf-8') as f:
                                            data = json.load(f)
                                            members = [
                                                name.replace('【', '').replace('】', '') 
                                                for name, info in data.items()
                                                if isinstance(info, dict) and info.get('group') == selected and info.get('exist', True)
                                            ]
                                    except (json.JSONDecodeError, IOError) as e:
                                        # 记录具体错误但不中断程序
                                        print(f"加载学生数据失败: {str(e)}")

                                # 随机选择成员
                                random_member = random.choice(members) if members else ''
                                display_text = selected  # 默认显示组号

                                # 加载显示设置
                                try:
                                    with open('app/Settings/Settings.json', 'r', encoding='utf-8') as f:
                                        settings = json.load(f)
                                        show_random = settings['pumping_people'].get('show_random_member', False)
                                        format_str = settings['pumping_people'].get('random_member_format', FORMAT_GROUP_SIMPLE)
                                except (json.JSONDecodeError, IOError, KeyError) as e:
                                    show_random = False
                                    format_str = FORMAT_GROUP_SIMPLE
                                    print(f"加载设置失败: {str(e)}")

                                # 应用格式设置
                                if show_random and random_member and format_str in FORMAT_MAPPINGS:
                                    display_text = FORMAT_MAPPINGS[format_str].format(
                                        selected=selected, 
                                        random_member=random_member
                                    )

                                label = BodyLabel(display_text)
                            else:
                                label = BodyLabel(f"{student_id_str} {name}")

                            label.setAlignment(Qt.AlignCenter)
                            try:
                                with open('app/Settings/Settings.json', 'r', encoding='utf-8') as f:
                                    settings = json.load(f)
                                    font_size = settings['pumping_people']['font_size']
                                    if font_size < 30:
                                        font_size = 85
                            except Exception as e:
                                font_size = 85
                                logger.error(f"加载字体设置时出错: {e}, 使用默认设置")
                            
                            if font_size < 30:
                                label.setFont(QFont(load_custom_font(), 85))
                            else:
                                label.setFont(QFont(load_custom_font(), font_size))
                            
                            self.student_labels.append(label)

                        # 计算所有标签的宽度之和，并考虑间距和边距
                        if self.student_labels:
                            total_width = sum(label.sizeHint().width() for label in self.student_labels) + \
                                          len(self.student_labels) * 180
                            available_width = self.width() - 20
                            
                            # 如果总宽度超过可用宽度，则计算每行最多能放几个标签
                            if total_width > available_width:
                                avg_label_width = total_width / len(self.student_labels)
                                max_columns = max(1, int(available_width // avg_label_width))
                            else:
                                max_columns = len(self.student_labels)  # 一行显示所有标签
                        else:
                            max_columns = 1
                        
                        # 复用 container 和 vbox_layout
                        if not hasattr(self, 'container'):
                            self.container = QWidget()
                            self.vbox_layout = QGridLayout()
                            self.container.setLayout(self.vbox_layout)
                        else:
                            # 清空旧标签
                            for i in reversed(range(self.vbox_layout.count())):
                                item = self.vbox_layout.itemAt(i)
                                if item.widget():
                                    item.widget().setParent(None)

                        for i, label in enumerate(self.student_labels):
                            row = i // max_columns
                            col = i % max_columns
                            self.vbox_layout.addWidget(label, row, col)
                        
                        self.result_grid.addWidget(self.container)
                        
                        if self.draw_mode in ["until_reboot", "until_all"]:
                            # 更新抽取记录
                            drawn_students.extend([s[1].replace(' ', '') for s in selected_students])
                            with open(draw_record_file, 'w', encoding='utf-8') as f:
                                json.dump(drawn_students, f, ensure_ascii=False, indent=4)

                        self.update_total_count()
                        return
                    else:
                        if self.draw_mode in ["until_reboot", "until_all"]:
                            # 删除临时文件
                            if os.path.exists(draw_record_file):
                                os.remove(draw_record_file)

                        return

        else:
            self.clear_layout(self.result_grid)
            if hasattr(self, 'container'):
                self.container.deleteLater()
                del self.container
            if hasattr(self, 'student_labels'):
                for label in self.student_labels:
                    label.deleteLater()
            
            # 创建错误标签
            error_label = BodyLabel("-- 抽选失败")
            error_label.setAlignment(Qt.AlignCenter)
            
            # 获取字体大小设置
            font_size = 85
            try:
                with open('app/Settings/Settings.json', 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    font_size = max(settings['pumping_people']['font_size'], 30)
            except Exception as e:
                logger.error(f"加载字体设置时出错: {e}, 使用默认设置")
            
            error_label.setFont(QFont(load_custom_font(), font_size))
            self.result_grid.addWidget(error_label)

    # 清除旧布局和标签
    def clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    # 获取随机抽取方法的设置
    def get_random_method_setting(self):
        """获取随机抽取方法的设置"""
        try:
            with open('app/Settings/Settings.json', 'r', encoding='utf-8') as f:
                settings = json.load(f)
                random_method = settings['pumping_people']['draw_pumping']
                return random_method
        except Exception as e:
            logger.error(f"加载随机抽取方法设置时出错: {e}, 使用默认设置")
            return 0

    # 更新历史记录
    def _update_history(self, class_name, group_name, genders, selected_students):
        """更新历史记录"""
        try:
            with open('app/Settings/Settings.json', 'r', encoding='utf-8') as f:
                settings = json.load(f)
                history_enabled = settings['history']['history_enabled']
        except Exception as e:
            history_enabled = False
            logger.error(f"加载历史记录设置时出错: {e}, 使用默认设置")
        
        if not history_enabled:
            logger.info("历史记录功能已被禁用。")
            return
        
        history_file = f"app/resource/history/{class_name}.json"
        os.makedirs(os.path.dirname(history_file), exist_ok=True)
        
        history_data = {}
        if os.path.exists(history_file):
            with open(history_file, 'r', encoding='utf-8') as f:
                try:
                    history_data = json.load(f)
                except json.JSONDecodeError:
                    history_data = {}
        
        # 初始化数据结构
        if "pumping_people" not in history_data:
            history_data["pumping_people"] = {}
        if "pumping_group" not in history_data:
            history_data["pumping_group"] = {}
        if "group_stats" not in history_data:
            history_data["group_stats"] = {}
        if "gender_stats" not in history_data:
            history_data["gender_stats"] = {}
        # 初始化统计数据字段
        for field in ["total_rounds", "total_stats"]:
            if field not in history_data:
                history_data[field] = 0

        # 加载学生数据以获取小组和性别信息
        student_info_map = {}
        student_file = f"app/resource/list/{class_name}.json"
        if os.path.exists(student_file):
            with open(student_file, 'r', encoding='utf-8') as f:
                student_data = json.load(f)
                for name, info in student_data.items():
                    if isinstance(info, dict) and 'id' in info:
                        student_name = name.replace('【', '').replace('】', '')
                        student_info_map[student_name] = {
                            'group': info.get('group', ''),
                            'gender': info.get('gender', '')
                        }
        
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 更新被选中学生的记录
        for student_id, student_name, exist in selected_students:
            # 获取学生信息
            student_info = student_info_map.get(student_name, {'group': '', 'gender': ''})
            student_group = student_info['group']
            student_gender = student_info['gender']

            if student_group not in history_data["group_stats"]:
                history_data["group_stats"][student_group] = 0
            if student_gender not in history_data["gender_stats"]:
                history_data["gender_stats"][student_gender] = 0

            history_data["total_rounds"] += 1

            if (not genders or '抽取所有性别' in genders) and group_name == '抽取全班学生':
                if "total_stats" not in history_data:
                    history_data["total_stats"] = 0
                history_data["total_stats"] += 1
                history_data["gender_stats"][student_gender] += 1
                history_data["group_stats"][student_group] += 1
                
            if group_name == '抽取小组组号':
                if student_name not in history_data["pumping_group"]:
                    history_data["pumping_group"][student_name] = {
                        "total_number_of_times": 1,
                        "last_drawn_time": current_time,
                        "rounds_missed": 0,
                        "time": [{
                            "draw_method": self.draw_mode,
                            "draw_time": current_time,
                            "draw_people_numbers": self.current_count
                        }]
                    }
                else:
                    history_data["pumping_group"][student_name]["total_number_of_times"] += 1
                    history_data["pumping_group"][student_name]["last_drawn_time"] = current_time
                    history_data["pumping_group"][student_name]["rounds_missed"] = 0
                    history_data["pumping_group"][student_name]["time"].append({
                        "draw_method": self.draw_mode,
                        "draw_time": current_time,
                        "draw_people_numbers": self.current_count
                    })
            else:
                if student_name not in history_data["pumping_people"]:
                    if not genders or '抽取所有性别' in genders:
                        history_data["pumping_people"][student_name] = {
                            "total_number_of_times": 1,
                            "total_number_auxiliary": 0,
                            "last_drawn_time": current_time,
                            "rounds_missed": 0,
                            "time": [{
                                "draw_method": self.draw_mode,
                                "draw_time": current_time,
                                "draw_people_numbers": self.current_count,
                                "draw_group": group_name,
                                "draw_gender": genders
                            }]
                        }
                    else:
                        history_data["pumping_people"][student_name] = {
                            "total_number_of_times": 0,
                            "total_number_auxiliary": 1,
                            "last_drawn_time": current_time,
                            "rounds_missed": 0,
                            "time": [{
                                "draw_method": self.draw_mode,
                                "draw_time": current_time,
                                "draw_people_numbers": self.current_count,
                                "draw_group": group_name,
                                "draw_gender": genders
                            }]
                        }
                else:
                    if not genders or '抽取所有性别' in genders: 
                        history_data["pumping_people"][student_name]["total_number_of_times"] += 1
                    else:
                        history_data["pumping_people"][student_name]["total_number_auxiliary"] += 1
                    history_data["pumping_people"][student_name]["last_drawn_time"] = current_time
                    history_data["pumping_people"][student_name]["rounds_missed"] = 0
                    history_data["pumping_people"][student_name]["time"].append({
                        "draw_method": self.draw_mode,
                        "draw_time": current_time,
                        "draw_people_numbers": self.current_count,
                        "draw_group": group_name,
                        "draw_gender": genders
                    })
        
        # 更新未被选中学生的rounds_missed
        all_students = set()
        student_file = f"app/resource/list/{class_name}.json"
        if os.path.exists(student_file):
            with open(student_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for student_name, student_info in data.items():
                    if isinstance(student_info, dict) and 'id' in student_info:
                        name = student_name.replace('【', '').replace('】', '')
                        all_students.add(name)
        
        selected_names = {s[1] for s in selected_students}
        for student_name in all_students:
            if student_name in history_data["pumping_people"] and student_name not in selected_names:
                history_data["pumping_people"][student_name]["rounds_missed"] += 1
        
        # 保存历史记录
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(history_data, f, ensure_ascii=False, indent=4)

    # 将小组名称转换为排序键
    def sort_key(self, group):
        # 尝试匹配 '第X小组' 或 '第X组' 格式
        match = re.match(r'第\s*(\d+|一|二|三|四|五|六|七|八|九|十)\s*(小组|组)', group)
        if match:
            num = match.group(1)
            num_map = {'一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9, '十': 10}
            if num in num_map:
                return (1, num_map[num])  # 类型1: 中文数字组
            else:
                return (1, int(num))       # 类型1: 阿拉伯数字组
        
        # 尝试匹配仅数字格式
        try:
            return (2, int(group))         # 类型2: 纯数字组
        except ValueError:
            pass
        
        # 🌟 星穹铁道白露：自定义组名直接使用中文排序啦~
        return (3, group) # ✨ 小鸟游星野：类型3: 其他名称组，保持排序功能不变

    # 更新总人数显示   
    def update_total_count(self):
        """根据选择的班级更新总人数显示"""
        group_name = self.group_combo.currentText()
        class_name = self.class_combo.currentText()
        genders = self.gender_combo.currentText()

        try:
            with open('app/Settings/Settings.json', 'r', encoding='utf-8') as f:
                settings = json.load(f)
                pumping_people_student_quantity = f"{settings['pumping_people']['people_theme']}"
        except Exception:
            pumping_people_student_quantity = 0

        if class_name and class_name not in ["你暂未添加班级", "加载班级列表失败"]:
            student_file = f"app/resource/list/{class_name}.json"
            if os.path.exists(student_file):
                cleaned_data = self._get_cleaned_data(student_file, group_name, genders)
                drawn_count = self._get_drawn_count(class_name, group_name, genders)
                if group_name == '抽取全班学生':
                    _count = len(cleaned_data) - drawn_count
                elif group_name == '抽取小组组号':
                    _count = len(set(group for _, group, _ in cleaned_data)) - drawn_count
                else:
                    _count = len(cleaned_data) - drawn_count
                count = len(cleaned_data)
                if _count <= 0:
                    _count = count
                    InfoBar.success(
                        title='抽取完成',
                        content="抽取完了所有学生了！记录已清除!",
                        orient=Qt.Horizontal,
                        parent=self,
                        isClosable=True,
                        duration=3000,
                        position=InfoBarPosition.TOP
                    )
                entity_type = '组数' if group_name == '抽取小组组号' else '人数'
                if pumping_people_student_quantity == 1:
                    self.total_label = BodyLabel('总人数: 0')
                    self.total_label.setText(f'总{entity_type}: {count}')
                if pumping_people_student_quantity == 2:
                    self.total_label = BodyLabel('剩余人数: 0')
                    self.total_label.setText(f'剩余{entity_type}: {_count}')
                else:
                    self.total_label.setText(f'总{entity_type}: {count} | 剩余{entity_type}: {_count}')
                self.max_count = count
                self._update_count_display()
            else:
                self._set_default_count(pumping_people_student_quantity)
        else:
            self._set_default_count(pumping_people_student_quantity)

    # 对用户的选择进行返回学生数量或小组数量
    def _get_cleaned_data(self, student_file, group_name, genders):
        with open(student_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # 初始化不同情况的列表
            group_data = []
            student_data = []
            for student_name, student_info in data.items():
                if isinstance(student_info, dict) and 'id' in student_info:
                    id = student_info.get('id', '')
                    name = student_name.replace('【', '').replace('】', '')
                    gender = student_info.get('gender', '')
                    group = student_info.get('group', '')
                    exist = student_info.get('exist', True)
                    if group_name == '抽取小组组号':
                        group_data.append((id, group, exist))
                    elif group_name == group:
                        if (not genders) or (genders and gender in genders) or (genders == '抽取所有性别'):
                            student_data.append((id, name, exist))
                    elif group_name == '抽取全班学生':
                        if (not genders) or (genders and gender in genders) or (genders == '抽取所有性别'):
                            student_data.append((id, name, exist))
                        
            if group_name == '抽取小组组号':
                valid_groups = set()
                group_exist_map = {}
                for _, group, exist in group_data:
                    if group not in group_exist_map:
                        group_exist_map[group] = exist
                    else:
                        group_exist_map[group] = group_exist_map[group] or exist
                for group, has_exist in group_exist_map.items():
                    if has_exist:
                        valid_groups.add(group)
                unique_groups = sorted(valid_groups, key=self.sort_key)
                cleaned_data = [(group_id, group, True) for group_id, group in enumerate(sorted(unique_groups, key=self.sort_key), start=1)]
            else:
                cleaned_data = [data for data in student_data if data[2]]
            return cleaned_data

    # 获取已抽取人数
    def _get_drawn_count(self, class_name, group_name, genders):
        if self.draw_mode in ["until_reboot", "until_all"]:
            if self.draw_mode == "until_reboot":
                if group_name == '抽取全班学生':
                    draw_record_file = f"app/resource/Temp/until_the_reboot_{class_name}_{group_name}_{genders}.json"
                elif group_name == '抽取小组组号':
                    draw_record_file = f"app/resource/Temp/until_the_reboot_{class_name}_{group_name}.json"
                else:
                    draw_record_file = f"app/resource/Temp/until_the_reboot_{class_name}_{group_name}_{genders}.json"
            elif self.draw_mode == "until_all":
                if group_name == '抽取全班学生':
                    draw_record_file = f"app/resource/Temp/until_all_draw_{class_name}_{group_name}_{genders}.json"
                elif group_name == '抽取小组组号':
                    draw_record_file = f"app/resource/Temp/until_all_draw_{class_name}_{group_name}.json"
                else:
                    draw_record_file = f"app/resource/Temp/until_all_draw_{class_name}_{group_name}_{genders}.json"
            if os.path.exists(draw_record_file):
                try:
                    with open(draw_record_file, 'r', encoding='utf-8') as f:
                        return len(json.load(f))
                except Exception as e:
                    # 处理加载文件出错的情况，返回 0
                    logger.error(f"加载抽取记录文件 {draw_record_file} 出错: {e}")
                    return 0
            else:
                return 0
        else:
            return 0

    # 设置默认总人数显示
    def _set_default_count(self, pumping_people_student_quantity):
        if pumping_people_student_quantity == 1:
            self.total_label = BodyLabel('总人数: 0')
        if pumping_people_student_quantity == 2:
            self.total_label = BodyLabel('剩余人数: 0')
        else:
            self.total_label = BodyLabel('总人数: 0 | 剩余人数: 0')
        self.max_count = 0
        self._update_count_display()
    
    # 增加抽取人数
    def _increase_count(self):
        """增加抽取人数"""
        if self.current_count < self.max_count:
            self.current_count += 1
            self._update_count_display()

    # 减少抽取人数        
    def _decrease_count(self):
        """减少抽取人数"""
        if self.current_count > 1:
            self.current_count -= 1
            self._update_count_display()

    # 更新人数显示        
    def _update_count_display(self):
        """更新人数显示"""
        self.count_label.setText(str(self.current_count))
        
        # 根据当前人数启用/禁用按钮
        self.plus_button.setEnabled(self.current_count < self.max_count)
        self.minus_button.setEnabled(self.current_count > 1)
        self.start_button.setEnabled(self.current_count <= self.max_count and self.current_count > 0)
    
    # 刷新班级列表         
    def refresh_class_list(self):
        """刷新班级下拉框选项"""
        self.class_combo.clear()
        try:
            list_folder = "app/resource/list"
            if os.path.exists(list_folder) and os.path.isdir(list_folder):
                files = os.listdir(list_folder)
                classes = []
                for file in files:
                    if file.endswith('.json'):
                        class_name = os.path.splitext(file)[0]
                        classes.append(class_name)
                
                self.class_combo.clear()
                if classes:
                    self.class_combo.addItems(classes)
                else:
                    logger.error("你暂未添加班级")
                    self.class_combo.addItem("你暂未添加班级")
            else:
                logger.error("你暂未添加班级")
                self.class_combo.addItem("你暂未添加班级")
        except Exception as e:
            logger.error(f"加载班级名称失败: {str(e)}")

        self.update_total_count()

        InfoBar.success(
            title='班级列表',
            content="班级列表更新成功！",
            orient=Qt.Horizontal,
            parent=self,
            isClosable=True,
            duration=3000,
            position=InfoBarPosition.TOP
        )

    # 刷新小组列表
    def refresh_group_list(self):
        """刷新小组下拉框选项"""
        class_name = self.class_combo.currentText()

        self.current_count = 1
        self._update_count_display()

        if class_name not in ["你暂未添加班级", "加载班级列表失败", "你暂未添加小组", "加载小组列表失败"]:
            pumping_people_file = f'app/resource/list/{class_name}.json'
            try:
                if os.path.exists(pumping_people_file):
                    with open(pumping_people_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        groups = set()
                        for student_name, student_info in data.items():
                            if isinstance(student_info, dict) and 'id' in student_info:
                                id = student_info.get('id', '')
                                name = student_name.replace('【', '').replace('】', '')
                                gender = student_info.get('gender', '')
                                group = student_info.get('group', '')
                                if group:  # 只添加非空小组
                                    groups.add(group)
                        cleaned_data = sorted(list(groups), key=lambda x: self.sort_key(str(x)))
                        self.group_combo.clear()
                        self.group_combo.addItem('抽取全班学生')
                        if groups:
                            self.group_combo.addItem('抽取小组组号')
                            self.group_combo.addItems(cleaned_data)
                        else:
                            logger.error("你暂未添加小组")
                            self.group_combo.addItem("你暂未添加小组")
                else:
                    logger.error("你暂未添加小组")
                    self.group_combo.addItem("你暂未添加小组")
            except Exception as e:
                logger.error(f"加载小组列表失败: {str(e)}")
                self.group_combo.addItem("加载小组列表失败")
        else:
            logger.error("请先选择有效的班级")

    # 刷新性别列表
    def refresh_gender_list(self):
        """刷新性别下拉框选项"""
        class_name = self.class_combo.currentText()

        self.current_count = 1
        self._update_count_display()

        if class_name not in ["你暂未添加班级", "加载班级列表失败", "你暂未添加性别", "加载性别列表失败"]:
            pumping_people_file = f'app/resource/list/{class_name}.json'
            try:
                if os.path.exists(pumping_people_file):
                    with open(pumping_people_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        genders = set()
                        for student_name, student_info in data.items():
                            if isinstance(student_info, dict) and 'id' in student_info:
                                id = student_info.get('id', '')
                                name = student_name.replace('【', '').replace('】', '')
                                gender = student_info.get('gender', '')
                                group = student_info.get('group', '')
                                if gender:  # 只添加非空小组
                                    genders.add(gender)
                        cleaned_data = sorted(list(genders), key=lambda x: self.sort_key(str(x)))
                        self.gender_combo.clear()
                        if genders:
                            self.gender_combo.addItem('抽取所有性别')
                            self.gender_combo.addItems(cleaned_data)
                        else:
                            logger.error("你暂未添加性别")
                            self.gender_combo.addItem('抽取所有性别')
                            self.gender_combo.addItem("你暂未添加性别")
                else:
                    logger.error("你暂未添加性别")
                    self.gender_combo.addItem("你暂未添加性别")
            except Exception as e:
                logger.error(f"加载性别列表失败: {str(e)}")
                self.gender_combo.addItem("加载性别列表失败")
        else:
            logger.error("请先选择有效的班级")
    
    # 恢复初始状态
    def _reset_to_initial_state(self):
        """恢复初始状态"""
        self._clean_temp_files()
        self.current_count = 1
        self.update_total_count()
        self.refresh_class_list()
        self.clear_layout(self.result_grid)

    # 清理临时文件
    def _clean_temp_files(self):
        import glob
        temp_dir = "app/resource/Temp"
        if os.path.exists(temp_dir):
            for file in glob.glob(f"{temp_dir}/until_the_reboot_*.json"):
                try:
                    os.remove(file)
                    logger.info(f"已清理临时抽取记录文件: {file}")
                except Exception as e:
                    logger.error(f"清理临时抽取记录文件失败: {e}")

    # 初始化UI
    def initUI(self):
        # 加载设置
        try:
            with open('app/Settings/Settings.json', 'r', encoding='utf-8') as f:
                settings = json.load(f)
                pumping_people_student_quantity = f"{settings['pumping_people']['people_theme']}"
        except Exception as e:
            logger.error(f"加载设置时出错: {e}, 使用默认设置")
            pumping_people_student_quantity = 0
            
        # 主布局
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        # 设置滚动条样式
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollArea QWidget {
                border: none;
                background-color: transparent;
            }
            /* 垂直滚动条整体 */
            QScrollBar:vertical {
                background-color: #E5DDF8;   /* 背景透明 */
                width: 8px;                    /* 宽度 */
                margin: 0px;                   /* 外边距 */
            }
            /* 垂直滚动条的滑块 */
            QScrollBar::handle:vertical {
                background-color: rgba(0, 0, 0, 0.3);    /* 半透明滑块 */
                border-radius: 4px;                      /* 圆角 */
                min-height: 20px;                        /* 最小高度 */
            }
            /* 鼠标悬停在滑块上 */
            QScrollBar::handle:vertical:hover {
                background-color: rgba(0, 0, 0, 0.5);
            }
            /* 滚动条的上下按钮和顶部、底部区域 */
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical,
            QScrollBar::up-arrow:vertical,
            QScrollBar::down-arrow:vertical {
                height: 0px;
            }
        
            /* 水平滚动条整体 */
            QScrollBar:horizontal {
                background-color: #E5DDF8;   /* 背景透明 */
                height: 8px;
                margin: 0px;
            }
            /* 水平滚动条的滑块 */
            QScrollBar::handle:horizontal {
                background-color: rgba(0, 0, 0, 0.3);
                border-radius: 4px;
                min-width: 20px;
            }
            /* 鼠标悬停在滑块上 */
            QScrollBar::handle:horizontal:hover {
                background-color: rgba(0, 0, 0, 0.5);
            }
            /* 滚动条的左右按钮和左侧、右侧区域 */
            QScrollBar::add-line:horizontal,
            QScrollBar::sub-line:horizontal,
            QScrollBar::left-arrow:horizontal,
            QScrollBar::right-arrow:horizontal {
                width: 0px;
            }
        """)
        # 启用触屏滚动
        QScroller.grabGesture(scroll_area.viewport(), QScroller.LeftMouseButtonGesture)
        
        # 创建主容器和布局
        container = QWidget(scroll_area)
        scroll_area_container = QVBoxLayout(container)
        
        # 控制面板
        control_panel = QVBoxLayout()
        control_panel.setContentsMargins(10, 10, 50, 10)

        # 刷新按钮
        self.refresh_button = PushButton('重置已抽取名单')
        self.refresh_button.setFixedSize(200, 50)
        self.refresh_button.setFont(QFont(load_custom_font(), 15))
        self.refresh_button.clicked.connect(self._reset_to_initial_state)
        control_panel.addWidget(self.refresh_button, 0, Qt.AlignVCenter)

        # 刷新按钮
        self.refresh_button = PushButton('刷新学生列表')
        self.refresh_button.setFixedSize(200, 50)
        self.refresh_button.setFont(QFont(load_custom_font(), 15))
        self.refresh_button.clicked.connect(self.refresh_class_list)
        control_panel.addWidget(self.refresh_button, 0, Qt.AlignVCenter)

        # 创建一个水平布局
        horizontal_layout = QHBoxLayout()

        # 减号按钮
        self.minus_button = PushButton('-')
        self.minus_button.setFixedSize(60, 50)
        self.minus_button.setFont(QFont(load_custom_font(), 30))
        self.minus_button.clicked.connect(self._decrease_count)
        horizontal_layout.addWidget(self.minus_button, 0, Qt.AlignLeft)

        # 人数显示
        self.count_label = BodyLabel('1')
        self.count_label.setAlignment(Qt.AlignCenter)
        self.count_label.setFont(QFont(load_custom_font(), 30))
        self.count_label.setFixedWidth(65)
        horizontal_layout.addWidget(self.count_label, 0, Qt.AlignLeft)

        # 加号按钮
        self.plus_button = PushButton('+')
        self.plus_button.setFixedSize(60, 50)
        self.plus_button.setFont(QFont(load_custom_font(), 30))
        self.plus_button.clicked.connect(self._increase_count)
        horizontal_layout.addWidget(self.plus_button, 0, Qt.AlignLeft)

        # 将水平布局添加到控制面板
        control_panel.addLayout(horizontal_layout)

        # 开始按钮
        self.start_button = PrimaryPushButton('开始')
        self.start_button.setFixedSize(200, 50)
        self.start_button.setFont(QFont(load_custom_font(), 20))
        self.start_button.clicked.connect(self.start_draw)
        control_panel.addWidget(self.start_button, 0, Qt.AlignVCenter)
        
        # 班级下拉框
        self.class_combo = ComboBox()
        self.class_combo.setFixedSize(200, 50)
        self.class_combo.setFont(QFont(load_custom_font(), 15))
        
        # 加载班级列表
        try:
            list_folder = "app/resource/list"
            if os.path.exists(list_folder) and os.path.isdir(list_folder):
                files = os.listdir(list_folder)
                classes = []
                for file in files:
                    if file.endswith('.json'):
                        class_name = os.path.splitext(file)[0]
                        classes.append(class_name)
                
                self.class_combo.clear()
                if classes:
                    self.class_combo.addItems(classes)
                else:
                    logger.error("你暂未添加班级")
                    self.class_combo.addItem("你暂未添加班级")
            else:
                logger.error("你暂未添加班级")
                self.class_combo.addItem("你暂未添加班级")
        except Exception as e:
            logger.error(f"加载班级列表失败: {str(e)}")
            self.class_combo.addItem("加载班级列表失败")
        
        control_panel.addWidget(self.class_combo)

        # 小组下拉框
        self.group_combo = ComboBox()
        self.group_combo.setFixedSize(200, 50)
        self.group_combo.setFont(QFont(load_custom_font(), 15))
        self.group_combo.addItem('抽取全班学生')
        self.group_combo.currentIndexChanged.connect(self.update_total_count)
        self.class_combo.currentIndexChanged.connect(self.refresh_group_list)

        class_name = self.class_combo.currentText()
        pumping_people_file = f'app/resource/list/{class_name}.json'
        try:
            if os.path.exists(pumping_people_file):
                with open(pumping_people_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    groups = set()
                    for student_name, student_info in data.items():
                        if isinstance(student_info, dict) and 'id' in student_info:
                            id = student_info.get('id', '')
                            name = student_name.replace('【', '').replace('】', '')
                            gender = student_info.get('gender', '')
                            group = student_info.get('group', '')
                            if group:  # 只添加非空小组
                                groups.add(group)
                    cleaned_data = sorted(list(groups), key=lambda x: self.sort_key(str(x)))
                    if groups:
                        self.group_combo.addItem('抽取小组组号')
                        self.group_combo.addItems(cleaned_data)
                    else:
                        logger.error("你暂未添加小组")
                        self.group_combo.addItem("你暂未添加小组")
            else:
                logger.error("你暂未添加小组")
                self.group_combo.addItem("你暂未添加小组")
        except Exception as e:
            logger.error(f"加载小组列表失败: {str(e)}")
            self.group_combo.addItem("加载小组列表失败")
        
        control_panel.addWidget(self.group_combo)

        # 性别下拉框
        self.gender_combo = ComboBox()
        self.gender_combo.setFixedSize(200, 50)
        self.gender_combo.setFont(QFont(load_custom_font(), 15))
        self.gender_combo.addItem('抽取所有性别')
        self.gender_combo.currentIndexChanged.connect(self.update_total_count)
        self.class_combo.currentIndexChanged.connect(self.refresh_gender_list)
        self.group_combo.currentIndexChanged.connect(self.refresh_gender_list)

        class_name = self.class_combo.currentText()
        pumping_people_file = f'app/resource/list/{class_name}.json'
        try:
            if os.path.exists(pumping_people_file):
                with open(pumping_people_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    genders = set()
                    for student_name, student_info in data.items():
                        if isinstance(student_info, dict) and 'id' in student_info:
                            id = student_info.get('id', '')
                            name = student_name.replace('【', '').replace('】', '')
                            gender = student_info.get('gender', '')
                            group = student_info.get('group', '')
                            if gender:  # 只添加非空小组
                                genders.add(gender)
                    cleaned_data = sorted(list(genders), key=lambda x: self.sort_key(str(x)))
                    if genders:
                        self.gender_combo.addItems(cleaned_data)
                    else:
                        logger.error("你暂未添加性别")
                        self.gender_combo.addItem("你暂未添加性别")
            else:
                logger.error("你暂未添加性别")
                self.gender_combo.addItem("你暂未添加性别")
        except Exception as e:
            logger.error(f"加载性别列表失败: {str(e)}")
            self.gender_combo.addItem("加载性别列表失败")
        
        control_panel.addWidget(self.gender_combo)
        
        # 总人数和剩余人数显示
        if pumping_people_student_quantity == 1:
            self.total_label = BodyLabel('总人数: 0')
        if pumping_people_student_quantity == 2:
            self.total_label = BodyLabel('剩余人数: 0')
        else:
            self.total_label = BodyLabel('总人数: 0 | 剩余人数: 0')
        self.total_label.setFont(QFont(load_custom_font(), 12))
        self.total_label.setAlignment(Qt.AlignCenter)
        self.total_label.setFixedWidth(200)
        control_panel.addWidget(self.total_label, 0, Qt.AlignLeft)
        
        control_panel.addStretch(1)
        
        # 结果区域布局
        self.result_grid = QGridLayout()
        self.result_grid.setSpacing(10)
        self.result_grid.setAlignment(Qt.AlignTop)

        scroll_area_container.addLayout(self.result_grid)
        
        # 班级选择变化时更新总人数
        self.class_combo.currentTextChanged.connect(self.update_total_count)
        
        # 初始化抽取人数
        self.current_count = 1
        self.max_count = 0
        
        # 初始化总人数显示
        self.update_total_count()
        
        # 设置容器并应用布局
        main_layout = QHBoxLayout(self)

        control_button_layout = QVBoxLayout()

        control_button_layout.addStretch(5)
        
        # 将control_panel布局包裹在QWidget中
        control_panel_widget = QWidget()
        control_panel_widget.setLayout(control_panel)
        control_button_layout.addWidget(control_panel_widget, 0, Qt.AlignBottom)

        # 将scroll_area添加到主布局中
        scroll_area.setWidget(container)
        # 创建一个QWidget来包含control_button_layout
        control_button_widget = QWidget()
        control_button_widget.setLayout(control_button_layout)
        # 将control_button_widget添加到主布局中
        main_layout.addWidget(control_button_widget)
        main_layout.addWidget(scroll_area)

        # 显示主布局
        self.setLayout(main_layout)
