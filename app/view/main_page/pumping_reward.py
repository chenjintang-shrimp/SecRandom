from pickle import NONE
from qfluentwidgets import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtMultimedia import *

import os
import glob
import json
import random
import datetime
from loguru import logger
from random import SystemRandom
system_random = SystemRandom()
from app.common.path_utils import path_manager, open_file, remove_file


# 音乐文件路径定义 ~(≧▽≦)/~ 星野最喜欢的动画BGM存放地
BGM_ANIMATION_PATH = path_manager.get_resource_path("music/pumping_reward/Animation_music")
BGM_RESULT_PATH = path_manager.get_resource_path("music/pumping_reward/result_music")

from app.common.config import load_custom_font, restore_volume
from app.common.voice import TTSHandler

class pumping_reward(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # 设置对象名称，用于快捷键功能识别
        self.setObjectName("RewardInterface")
        # 定义变量
        self.is_animating = False
        self.draw_mode = "random"
        self.animation_timer = None
        # 音乐播放器初始化 ✧(◍˃̶ᗜ˂̶◍)✩ 感谢白露提供的播放器
        self.music_player = QMediaPlayer()
        self.initUI()
        
        # 连接清理信号
        self._connect_cleanup_signal()
    
    def start_draw(self):
        """开始抽选奖品"""
        # 获取抽选模式和动画模式设置
        try:
            with open_file(path_manager.get_settings_path(), 'r', encoding='utf-8') as f:
                settings = json.load(f)
                pumping_reward_draw_mode = settings['pumping_reward']['draw_mode']
                pumping_reward_animation_mode = settings['pumping_reward']['animation_mode']
                self.interval = settings['pumping_reward']['animation_interval']
                self.auto_play = settings['pumping_reward']['animation_auto_play']
                self.animation_music_enabled = settings['pumping_reward']['animation_music_enabled']
                self.result_music_enabled = settings['pumping_reward']['result_music_enabled']
                self.animation_music_volume = settings['pumping_reward']['animation_music_volume']
                self.result_music_volume = settings['pumping_reward']['result_music_volume']
                self.music_fade_in = settings['pumping_reward']['music_fade_in']
                self.music_fade_out = settings['pumping_reward']['music_fade_out']
                
        except Exception as e:
            pumping_reward_draw_mode = 0
            pumping_reward_animation_mode = 0
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
        if pumping_reward_draw_mode == 0:  # 重复随机
            self.draw_mode = "random"
        elif pumping_reward_draw_mode == 1:  # 不重复抽取(直到软件重启)
            self.draw_mode = "until_reboot"
        elif pumping_reward_draw_mode == 2:  # 不重复抽取(直到抽完全部奖)
            self.draw_mode = "until_all"
            
        # 根据动画模式执行不同逻辑
        if pumping_reward_animation_mode == 0:  # 手动停止动画
            self.start_button.setText("停止")
            self.is_animating = True
            self.animation_timer = QTimer()
            self.animation_timer.timeout.connect(self._show_random_reward)
            self.animation_timer.start(self.interval)
            if self.animation_music_enabled:
                self._play_animation_music()
            self.start_button.clicked.disconnect()
            self.start_button.clicked.connect(self._stop_animation)
            
        elif pumping_reward_animation_mode == 1:  # 自动播放完整动画
            self._play_full_animation()
            
        elif pumping_reward_animation_mode == 2:  # 直接显示结果
            self._show_result_directly()
        
    def _show_random_reward(self):
        """显示随机奖品（用于动画效果）"""
        reward_name = self.reward_combo.currentText()

        if reward_name and reward_name not in ["你暂未添加奖池", "加载奖池列表失败"]:
            reward_file = path_manager.get_resource_path("reward", f"{reward_name}.json")

            if self.draw_mode == "until_reboot":
                draw_record_file = path_manager.get_temp_path(f"until_the_reboot_{reward_name}.json")
            elif self.draw_mode == "until_all":
                draw_record_file = path_manager.get_temp_path(f"until_all_draw_{reward_name}.json")
            
            if self.draw_mode in ["until_reboot", "until_all"]:
                # 创建Temp目录如果不存在
                os.makedirs(os.path.dirname(draw_record_file), exist_ok=True)
                
                # 初始化抽取记录文件
                if not path_manager.file_exists(draw_record_file):
                    with open_file(draw_record_file, 'w', encoding='utf-8') as f:
                        json.dump([], f, ensure_ascii=False, indent=4)
                
                # 读取已抽取记录
                drawn_rewards = []
                with open_file(draw_record_file, 'r', encoding='utf-8') as f:
                    try:
                        drawn_rewards = json.load(f)
                    except json.JSONDecodeError:
                        drawn_rewards = []
            else:
                drawn_rewards = []

            if path_manager.file_exists(reward_file):
                with open_file(reward_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    cleaned_data = []
                    # 获取奖品列表
                    for reward_name, reward_info in data.items():
                        if isinstance(reward_info, dict) and 'id' in reward_info:
                            id = reward_info.get('id', '')
                            name = reward_name
                            probability = reward_info.get('probability', '1.0')
                            cleaned_data.append((id, name, probability))

                    # 如果所有奖品都已抽取过，则使用全部奖品名单
                    rewards = [s for s in cleaned_data if s[1].replace(' ', '') not in [x.replace(' ', '') for x in drawn_rewards]] or cleaned_data

                    if rewards:
                        # 从self.current_count获取抽取奖数
                        draw_count = self.current_count
                        
                        # 根据设置选项选择随机方法
                        use_system_random = self.get_random_method_setting()
                        
                        if use_system_random == 1:  # 使用SystemRandom的方式-不可预测抽取
                            if len(rewards) <= draw_count:
                                selected_rewards = rewards
                            else:
                                if self.draw_mode == "random":
                                    # 允许重复抽取
                                    weights = [float(reward[2]) for reward in rewards]
                                    selected_rewards = system_random.choices(
                                        rewards,
                                        weights=weights,
                                        k=draw_count
                                    )
                                else:
                                    # 不重复抽取
                                    weights = [float(reward[2]) for reward in rewards]
                                    selected_rewards = []
                                    temp_rewards = rewards.copy()
                                    temp_weights = weights.copy()
                                    for _ in range(draw_count):
                                        if not temp_rewards:
                                            break
                                        chosen = system_random.choices(
                                            temp_rewards,
                                            weights=temp_weights,
                                            k=1
                                        )[0]
                                        selected_rewards.append(chosen)
                                        index = temp_rewards.index(chosen)
                                        temp_rewards.pop(index)
                                        temp_weights.pop(index)

                        else:  # 默认使用random的方式-可预测抽取
                            if len(rewards) <= draw_count:
                                selected_rewards = rewards
                            else:
                                if self.draw_mode == "random":
                                    # 允许重复抽取
                                    weights = [float(reward[2]) for reward in rewards]
                                    selected_rewards = random.choices(
                                        rewards,
                                        weights=weights,
                                        k=draw_count
                                    )
                                else:
                                    # 不重复抽取
                                    weights = [float(reward[2]) for reward in rewards]
                                    selected_rewards = []
                                    temp_rewards = rewards.copy()
                                    temp_weights = weights.copy()
                                    for _ in range(draw_count):
                                        if not temp_rewards:
                                            break
                                        chosen = random.choices(
                                            temp_rewards,
                                            weights=temp_weights,
                                            k=1
                                        )[0]
                                        selected_rewards.append(chosen)
                                        index = temp_rewards.index(chosen)
                                        temp_rewards.pop(index)
                                        temp_weights.pop(index)

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

                        if hasattr(self, 'reward_labels'):
                            for label in self.reward_labels:
                                try:
                                    if label:
                                        label.deleteLater()
                                except RuntimeError:
                                    pass
                            self.reward_labels = []

                        # 删除布局中的所有内容
                        while self.result_grid.count(): 
                            item = self.result_grid.takeAt(0)
                            widget = item.widget()
                            if widget:
                                try:
                                    widget.deleteLater()
                                except RuntimeError:
                                    pass

                        try:
                            with open_file(path_manager.get_settings_path(), 'r', encoding='utf-8') as f:
                                settings = json.load(f)
                                font_size = settings['pumping_reward']['font_size']
                                display_format = settings['pumping_reward']['display_format']
                                animation_color = settings['pumping_reward']['animation_color']
                                _animation_color = settings['pumping_reward'].get('_animation_color', '#ffffff')
                                show_reward_image = settings['pumping_reward']['show_reward_image']
                        except Exception as e:
                            font_size = 50
                            display_format = 0
                            animation_color = 0
                            _animation_color = "#ffffff"
                            show_reward_image = False

                        # 创建新标签列表
                        self.reward_labels = []
                        for num, name, probability in selected_rewards:
                            # 为每个奖励单独查找对应的图片文件
                            current_image_path = None
                            if show_reward_image:
                                # 支持多种图片格式：png、jpg、jpeg、svg
                                image_extensions = ['.png', '.jpg', '.jpeg', '.svg']
                                
                                # 遍历所有支持的图片格式，查找存在的图片文件
                                for ext in image_extensions:
                                    temp_path = path_manager.get_resource_path("images", f"rewards/{name}{ext}")
                                    if path_manager.file_exists(temp_path):
                                        current_image_path = str(temp_path)
                                        break
                                    else:
                                        current_image_path = None
                                        continue
                            
                            # 为每个标签创建独立的容器和布局
                            h_layout = QHBoxLayout()
                            h_layout.setSpacing(8)
                            h_layout.setContentsMargins(0, 0, 0, 0)
                            # 创建容器widget来包含水平布局
                            __container = QWidget()
                            __container.setLayout(h_layout)
                            reward_id_str = f"{num:02}"
                            if display_format == 1:
                                self.result_grid.setAlignment(Qt.AlignCenter)
                                if draw_count == 1:
                                    if show_reward_image:
                                        if current_image_path != None:
                                            avatar = AvatarWidget(current_image_path)
                                        else:
                                            avatar = AvatarWidget()
                                            avatar.setText(name)
                                        avatar.setRadius(font_size*2)
                                        text_label = BodyLabel(f"{name}")
                                        h_layout.addWidget(avatar)
                                        h_layout.addWidget(text_label)
                                        
                                        # 使用容器作为标签
                                        label = __container
                                    else:
                                        label = BodyLabel(f"{name}")
                                else:
                                    self.result_grid.setAlignment(Qt.AlignTop | Qt.AlignCenter)
                                    if show_reward_image:
                                        if current_image_path != None:
                                            avatar = AvatarWidget(current_image_path)
                                        else:
                                            avatar = AvatarWidget()
                                            avatar.setText(name)
                                        avatar.setRadius(font_size//2)
                                        text_label = BodyLabel(f"{name}")
                                        h_layout.addWidget(avatar)
                                        h_layout.addWidget(text_label)
                                        
                                        # 使用容器作为标签
                                        label = __container
                                    else:
                                        label = BodyLabel(f"{name}")
                            elif display_format == 2:
                                self.result_grid.setAlignment(Qt.AlignCenter)
                                if draw_count == 1:
                                    if show_reward_image:
                                        if current_image_path != None:
                                            avatar = AvatarWidget(current_image_path)
                                        else:
                                            avatar = AvatarWidget()
                                            avatar.setText(name)
                                        avatar.setRadius(font_size*2)
                                        text_label = BodyLabel(f"{reward_id_str}")
                                        h_layout.addWidget(avatar)
                                        h_layout.addWidget(text_label)
                                        
                                        # 使用容器作为标签
                                        label = __container
                                    else:
                                        label = BodyLabel(f"{reward_id_str}")
                                else:
                                    self.result_grid.setAlignment(Qt.AlignTop | Qt.AlignCenter)
                                    if show_reward_image:
                                        if current_image_path != None:
                                            avatar = AvatarWidget(current_image_path)
                                        else:
                                            avatar = AvatarWidget()
                                            avatar.setText(name)
                                        avatar.setRadius(font_size//2)
                                        if current_image_path == None:
                                            avatar.setText(name)
                                        text_label = BodyLabel(f"{reward_id_str}")
                                        h_layout.addWidget(avatar)
                                        h_layout.addWidget(text_label)
                                        
                                        # 使用容器作为标签
                                        label = __container
                                    else:
                                        label = BodyLabel(f"{reward_id_str}")
                            else:
                                if draw_count == 1:
                                    self.result_grid.setAlignment(Qt.AlignCenter)
                                    if show_reward_image:
                                        if current_image_path != None:
                                            avatar = AvatarWidget(current_image_path)
                                        else:
                                            avatar = AvatarWidget()
                                            avatar.setText(name)
                                        avatar.setRadius(font_size*2)
                                        text_label = BodyLabel(f"{reward_id_str}\n{name}")
                                        h_layout.addWidget(avatar)
                                        h_layout.addWidget(text_label)
                                        
                                        # 使用容器作为标签
                                        label = __container
                                    else:
                                        label = BodyLabel(f"{reward_id_str}\n{name}")
                                else:
                                    self.result_grid.setAlignment(Qt.AlignTop | Qt.AlignCenter)
                                    if show_reward_image:
                                        if current_image_path != None:
                                            avatar = AvatarWidget(current_image_path)
                                        else:
                                            avatar = AvatarWidget()
                                            avatar.setText(name)
                                        avatar.setRadius(font_size//2)
                                        if current_image_path == None:
                                            avatar.setText(name)
                                        text_label = BodyLabel(f"{reward_id_str} {name}")
                                        h_layout.addWidget(avatar)
                                        h_layout.addWidget(text_label)
                                        
                                        # 使用容器作为标签
                                        label = __container
                                    else:
                                        label = BodyLabel(f"{reward_id_str} {name}")

                            # 根据label类型应用不同的样式设置
                            widget = None  # 初始化widget变量
                            if isinstance(label, QWidget) and hasattr(label, 'layout') and label.layout() is not None:
                                # 如果是容器类型，对容器内的文本标签应用样式
                                layout = label.layout()
                                if layout:
                                    for i in range(layout.count()):
                                        item = layout.itemAt(i)
                                        widget = item.widget()
                                        if isinstance(widget, BodyLabel):
                                            widget.setAlignment(Qt.AlignCenter)
                                            if animation_color == 1:
                                                widget.setStyleSheet(f"color: {self._generate_vibrant_color()};")
                                            elif animation_color == 2:
                                                widget.setStyleSheet(f"color: {_animation_color};")
                            else:
                                # 如果是普通的BodyLabel，直接应用样式
                                label.setAlignment(Qt.AlignCenter)
                                if animation_color == 1:
                                    label.setStyleSheet(f"color: {self._generate_vibrant_color()};")
                                elif animation_color == 2:
                                    label.setStyleSheet(f"color: {_animation_color};")

                            # 为widget设置字体（如果widget存在）
                            if widget is not None:
                                widget.setFont(QFont(load_custom_font(), font_size))
                            # 为label设置字体
                            label.setFont(QFont(load_custom_font(), font_size))
                            self.reward_labels.append(label)

                        # 计算所有标签的宽度之和，并考虑间距和边距
                        if self.reward_labels:
                            total_width = sum(label.sizeHint().width() for label in self.reward_labels) + \
                                          len(self.reward_labels) * 180
                            available_width = self.width() - 20
                            
                            # 如果总宽度超过可用宽度，则计算每行最多能放几个标签
                            if total_width > available_width:
                                avg_label_width = total_width / len(self.reward_labels)
                                max_columns = max(1, int(available_width // avg_label_width))
                            else:
                                max_columns = len(self.reward_labels)  # 一行显示所有标签
                        else:
                            max_columns = 1
                        
                        # 复用 container 和 vbox_layout
                        if not hasattr(self, 'container'):
                            self.container = QWidget()
                            self.vbox_layout = QGridLayout()
                            # 设置标签之间的水平和垂直间距
                            self.vbox_layout.setSpacing(15)  # 设置统一的间距
                            self.vbox_layout.setHorizontalSpacing(20)  # 设置水平间距
                            self.vbox_layout.setVerticalSpacing(10)   # 设置垂直间距
                            self.container.setLayout(self.vbox_layout)
                        else:
                            # 清空旧标签
                            for i in reversed(range(self.vbox_layout.count())):
                                item = self.vbox_layout.itemAt(i)
                                if item.widget():
                                    item.widget().setParent(None)

                        for i, label in enumerate(self.reward_labels):
                            row = i // max_columns
                            col = i % max_columns
                            self.vbox_layout.addWidget(label, row, col)
                        
                        self.result_grid.addWidget(self.container)
                        
                        return
        
        else:
            self.clear_layout(self.result_grid)
            if hasattr(self, 'container'):
                self.container.deleteLater()
                del self.container
            if hasattr(self, 'reward_labels'):
                for label in self.reward_labels:
                    label.deleteLater()
            
            # 创建错误标签
            error_label = BodyLabel("-- 抽选失败")
            error_label.setAlignment(Qt.AlignCenter)
            try:
                with open_file(path_manager.get_settings_path(), 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    font_size = settings['pumping_reward']['font_size']
            except Exception as e:
                font_size = 50
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
    
    # 播放完整动画
    def _play_full_animation(self):
        """播放完整动画（快速显示n个随机奖品后显示最终结果）"""
        self.is_animating = True
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self._show_random_reward)
        self.animation_timer.start(self.interval)
        if self.animation_music_enabled:
            self._play_animation_music()
        self.start_button.setEnabled(False)  # 禁用按钮
        
        # n次随机后停止
        QTimer.singleShot(self.auto_play * self.interval, lambda: [
            self.animation_timer.stop(),
            self._stop_animation(),
            self.start_button.setEnabled(True)  # 恢复按钮
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
            # 检查音乐目录是否存在
            if not path_manager.file_exists(BGM_RESULT_PATH):
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
            self.music_player.setVolume(0)  # 初始音量设为0
            self.music_player.play()
            
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
            # 检查音乐目录是否存在
            if not path_manager.file_exists(BGM_ANIMATION_PATH):
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
            self.music_player.setVolume(0)  # 初始音量设为0
            self.music_player.play()
            
            # 创建音量渐入动画 ～(￣▽￣)～* 星野的魔法音量调节
            self.fade_in_animation = QPropertyAnimation(self.music_player, b"volume")
            self.fade_in_animation.setDuration(self.music_fade_in)
            self.fade_in_animation.setStartValue(0)
            self.fade_in_animation.setEndValue(self.animation_music_volume)
            self.fade_in_animation.setEasingCurve(QEasingCurve.InOutQuad)
            self.fade_in_animation.start()
        except Exception as e:
            logger.error(f"播放音乐时出错: {e}")

    def voice_play(self):
        """语音播报部分"""
        try:
            with open_file(path_manager.get_voice_engine_path(), 'r', encoding='utf-8') as f:
                voice_config = json.load(f)
                voice_engine = voice_config['voice_engine']['voice_engine']
                edge_tts_voice_name = voice_config['voice_engine'] ['edge_tts_voice_name']
                voice_enabled = voice_config['voice_engine']['voice_enabled']
                system_volume_enabled = voice_config['voice_engine']['system_volume_enabled']
                voice_volume = voice_config['voice_engine'].get('voice_volume', 100) / 100.0
                voice_speed = voice_config['voice_engine'].get('voice_speed', 100)
                volume_value = voice_config['voice_engine'].get('system_volume_value', 50)

                if voice_enabled == True:  # 开启语音
                    if system_volume_enabled == True: # 开启系统音量
                        restore_volume(volume_value)
                    tts_handler = TTSHandler()
                    config = {
                        'voice_enabled': voice_enabled,
                        'voice_volume': voice_volume,
                        'voice_speed': voice_speed,
                        'system_voice_name': edge_tts_voice_name,
                    }
                    students_name = []
                    for label in self.reward_labels:
                        # 检查label是否是QWidget容器类型
                        if isinstance(label, QWidget) and hasattr(label, 'layout'):
                            # 如果是容器类型，从容器中获取文本标签的文本
                            layout = label.layout()
                            text = ""
                            if layout:
                                for i in range(layout.count()):
                                    item = layout.itemAt(i)
                                    widget = item.widget()
                                    if isinstance(widget, BodyLabel):
                                        text = widget.text()
                                        break
                        else:
                            # 如果是普通的BodyLabel，直接获取文本
                            text = label.text()
                        
                        # 处理文本内容
                        parts = text.split()
                        if len(parts) >= 2 and len(parts[-1]) == 1 and len(parts[-2]) == 1:
                            name = parts[-2] + parts[-1]
                        else:
                            name = parts[-1]
                        name = name.replace(' ', '')
                        students_name.append(name)
                    tts_handler.voice_play(config, students_name, voice_engine, edge_tts_voice_name)
        except Exception as e:
            logger.error(f"语音播报出错: {e}")
    
    # 根据抽取模式抽选奖品
    def random(self):
        """根据抽取模式抽选奖品"""
        reward_name = self.reward_combo.currentText()
        
        if reward_name and reward_name not in ["你暂未添加奖池", "加载奖池列表失败"]:
            reward_file = path_manager.get_resource_path("reward", f"{reward_name}.json")

            if self.draw_mode == "until_reboot":
                draw_record_file = path_manager.get_temp_path(f"until_the_reboot_{reward_name}.json")
            elif self.draw_mode == "until_all":
                draw_record_file = path_manager.get_temp_path(f"until_all_draw_{reward_name}.json")
            
            if self.draw_mode in ["until_reboot", "until_all"]:
                # 创建Temp目录如果不存在
                os.makedirs(os.path.dirname(draw_record_file), exist_ok=True)
                
                # 初始化抽取记录文件
                if not path_manager.file_exists(draw_record_file):
                    with open_file(draw_record_file, 'w', encoding='utf-8') as f:
                        json.dump([], f, ensure_ascii=False, indent=4)
                
                # 读取已抽取记录
                drawn_rewards = []
                with open_file(draw_record_file, 'r', encoding='utf-8') as f:
                    try:
                        drawn_rewards = json.load(f)
                    except json.JSONDecodeError:
                        drawn_rewards = []
            else:
                drawn_rewards = []
            
            if path_manager.file_exists(reward_file):
                with open_file(reward_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    cleaned_data = []
                    
                    # 获取奖品列表
                    for prize_pools, reward_info in data.items():
                        if isinstance(reward_info, dict) and 'id' in reward_info:
                            id = reward_info.get('id', '')
                            name = prize_pools
                            probability = reward_info.get('probability', '1.0')
                            cleaned_data.append((id, name, probability))

                    if self.draw_mode == "random":
                        available_rewards = cleaned_data
                    elif self.draw_mode == "until_reboot" or self.draw_mode == "until_all":
                        available_rewards = [s for s in cleaned_data if s[1].replace(' ', '') not in [x.replace(' ', '') for x in drawn_rewards]]

                    if available_rewards:
                        # 从self.current_count获取抽取奖数
                        draw_count = self.current_count
                        
                        # 根据设置选项选择随机方法
                        use_system_random = self.get_random_method_setting()
                        
                        if use_system_random == 1:  # 使用SystemRandom的方式-不可预测抽取
                            if len(available_rewards) <= draw_count:
                                selected_rewards = available_rewards
                            else:
                                if self.draw_mode == "random":
                                    # 允许重复抽取
                                    weights = [float(reward[2]) for reward in available_rewards]
                                    selected_rewards = system_random.choices(
                                        available_rewards,
                                        weights=weights,
                                        k=draw_count
                                    )
                                else:
                                    # 不重复抽取
                                    weights = [float(reward[2]) for reward in available_rewards]
                                    selected_rewards = []
                                    temp_rewards = available_rewards.copy()
                                    temp_weights = weights.copy()
                                    for _ in range(draw_count):
                                        if not temp_rewards:
                                            break
                                        chosen = system_random.choices(
                                            temp_rewards,
                                            weights=temp_weights,
                                            k=1
                                        )[0]
                                        selected_rewards.append(chosen)
                                        index = temp_rewards.index(chosen)
                                        temp_rewards.pop(index)
                                        temp_weights.pop(index)

                        else:  # 默认使用random的方式-可预测抽取
                            if len(available_rewards) <= draw_count:
                                selected_rewards = available_rewards
                            else:
                                if self.draw_mode == "random":
                                    # 允许重复抽取
                                    weights = [float(reward[2]) for reward in available_rewards]
                                    selected_rewards = random.choices(
                                        available_rewards,
                                        weights=weights,
                                        k=draw_count
                                    )
                                else:
                                    # 不重复抽取
                                    weights = [float(reward[2]) for reward in available_rewards]
                                    selected_rewards = []
                                    temp_rewards = available_rewards.copy()
                                    temp_weights = weights.copy()
                                    for _ in range(draw_count):
                                        if not temp_rewards:
                                            break
                                        chosen = random.choices(
                                            temp_rewards,
                                            weights=temp_weights,
                                            k=1
                                        )[0]
                                        selected_rewards.append(chosen)
                                        index = temp_rewards.index(chosen)
                                        temp_rewards.pop(index)
                                        temp_weights.pop(index)

                        # 更新历史记录
                        self._update_history(reward_name, selected_rewards)
                        
                        # 显示结果
                        if hasattr(self, 'container'):
                            self.container.deleteLater()
                            del self.container
                        if hasattr(self, 'reward_labels'):
                            for label in self.reward_labels:
                                label.deleteLater()

                        while self.result_grid.count(): 
                            item = self.result_grid.takeAt(0)
                            widget = item.widget()
                            if widget:
                                widget.deleteLater()
                        try:
                            with open_file(path_manager.get_settings_path(), 'r', encoding='utf-8') as f:
                                settings = json.load(f)
                                font_size = settings['pumping_reward']['font_size']
                                display_format = settings['pumping_reward']['display_format']
                                animation_color = settings['pumping_reward']['animation_color']
                                _result_color = settings['pumping_reward'].get('_result_color', '#ffffff')
                                show_reward_image = settings['pumping_reward']['show_reward_image']
                        except Exception as e:
                            font_size = 50
                            display_format = 0
                            animation_color = 0
                            _animation_color = "#ffffff"
                            show_reward_image = False

                        # 创建新标签列表
                        self.reward_labels = []
                        for num, name, probability in selected_rewards:
                            # 为每个奖励单独查找对应的图片文件
                            current_image_path = None
                            if show_reward_image:
                                # 支持多种图片格式：png、jpg、jpeg、svg
                                image_extensions = ['.png', '.jpg', '.jpeg', '.svg']
                                
                                # 遍历所有支持的图片格式，查找存在的图片文件
                                for ext in image_extensions:
                                    temp_path = path_manager.get_resource_path("images/rewards", f"{name}{ext}")
                                    if os.path.isfile(temp_path):
                                        current_image_path = str(temp_path)
                                        break
                                    else:
                                        current_image_path = None
                                        continue

                            # 为每个标签创建独立的容器和布局
                            h_layout = QHBoxLayout()
                            h_layout.setSpacing(8)
                            h_layout.setContentsMargins(0, 0, 0, 0)
                            # 创建容器widget来包含水平布局
                            __container = QWidget()
                            __container.setLayout(h_layout)
                            reward_id_str = f"{num:02}"
                            if display_format == 1:
                                self.result_grid.setAlignment(Qt.AlignCenter)
                                if draw_count == 1:
                                    if show_reward_image:
                                        if current_image_path != None:
                                            avatar = AvatarWidget(current_image_path)
                                        else:
                                            avatar = AvatarWidget()
                                            avatar.setText(name)
                                        avatar.setRadius(font_size*2)
                                        if current_image_path == None:
                                            avatar.setText(name)
                                        text_label = BodyLabel(f"{name}")
                                        h_layout.addWidget(avatar)
                                        h_layout.addWidget(text_label)
                                        
                                        # 使用容器作为标签
                                        label = __container
                                    else:
                                        label = BodyLabel(f"{name}")
                                else:
                                    self.result_grid.setAlignment(Qt.AlignTop | Qt.AlignCenter)
                                    if show_reward_image:
                                        if current_image_path != None:
                                            avatar = AvatarWidget(current_image_path)
                                        else:
                                            avatar = AvatarWidget()
                                            avatar.setText(name)
                                        avatar.setRadius(font_size//2)
                                        if current_image_path == None:
                                            avatar.setText(name)
                                        text_label = BodyLabel(f"{name}")
                                        h_layout.addWidget(avatar)
                                        h_layout.addWidget(text_label)
                                        
                                        # 使用容器作为标签
                                        label = __container
                                    else:
                                        label = BodyLabel(f"{name}")
                            elif display_format == 2:
                                self.result_grid.setAlignment(Qt.AlignCenter)
                                if draw_count == 1:
                                    if show_reward_image:
                                        if current_image_path != None:
                                            avatar = AvatarWidget(current_image_path)
                                        else:
                                            avatar = AvatarWidget()
                                            avatar.setText(name)
                                        avatar.setRadius(font_size*2)
                                        if current_image_path == None:
                                            avatar.setText(name)
                                        text_label = BodyLabel(f"{reward_id_str}")
                                        h_layout.addWidget(avatar)
                                        h_layout.addWidget(text_label)
                                        
                                        # 使用容器作为标签
                                        label = __container
                                    else:
                                        label = BodyLabel(f"{reward_id_str}")
                                else:
                                    self.result_grid.setAlignment(Qt.AlignTop | Qt.AlignCenter)
                                    if show_reward_image:
                                        if current_image_path != None:
                                            avatar = AvatarWidget(current_image_path)
                                        else:
                                            avatar = AvatarWidget()
                                            avatar.setText(name)
                                        avatar.setRadius(font_size//2)
                                        if current_image_path == None:
                                            avatar.setText(name)
                                        text_label = BodyLabel(f"{reward_id_str}")
                                        h_layout.addWidget(avatar)
                                        h_layout.addWidget(text_label)
                                        
                                        # 使用容器作为标签
                                        label = __container
                                    else:
                                        label = BodyLabel(f"{reward_id_str}")
                            else:
                                self.result_grid.setAlignment(Qt.AlignCenter)
                                if draw_count == 1:
                                    if show_reward_image:
                                        if current_image_path != None:
                                            avatar = AvatarWidget(current_image_path)
                                        else:
                                            avatar = AvatarWidget()
                                            avatar.setText(name)
                                        avatar.setRadius(font_size*2)
                                        text_label = BodyLabel(f"{reward_id_str}\n{name}")
                                        h_layout.addWidget(avatar)
                                        h_layout.addWidget(text_label)
                                        
                                        # 使用容器作为标签
                                        label = __container
                                    else:
                                        label = BodyLabel(f"{reward_id_str}\n{name}")
                                else:
                                    self.result_grid.setAlignment(Qt.AlignTop | Qt.AlignCenter)
                                    if show_reward_image:
                                        if current_image_path != None:
                                            avatar = AvatarWidget(current_image_path)
                                        else:
                                            avatar = AvatarWidget()
                                            avatar.setText(name)
                                        avatar.setRadius(font_size//2)
                                        if current_image_path == None:
                                            avatar.setText(name)
                                        text_label = BodyLabel(f"{reward_id_str} {name}")
                                        h_layout.addWidget(avatar)
                                        h_layout.addWidget(text_label)
                                        
                                        # 使用容器作为标签
                                        label = __container
                                    else:
                                        label = BodyLabel(f"{reward_id_str} {name}")

                            widget = None  # 初始化widget变量
                            # 根据label类型应用不同的样式设置
                            if isinstance(label, QWidget) and hasattr(label, 'layout') and label.layout() is not None:
                                # 如果是容器类型，对容器内的文本标签应用样式
                                layout = label.layout()
                                if layout:
                                    for i in range(layout.count()):
                                        item = layout.itemAt(i)
                                        widget = item.widget()
                                        if isinstance(widget, BodyLabel):
                                            widget.setAlignment(Qt.AlignCenter)
                                            if animation_color == 1:
                                                widget.setStyleSheet(f"color: {self._generate_vibrant_color()};")
                                            elif animation_color == 2:
                                                widget.setStyleSheet(f"color: {_result_color};")
                            else:
                                label.setAlignment(Qt.AlignCenter)
                                if animation_color == 1:
                                    label.setStyleSheet(f"color: {self._generate_vibrant_color()};")
                                elif animation_color == 2:
                                    label.setStyleSheet(f"color: {_result_color};")

                            # 为widget设置字体（如果widget存在）
                            if widget is not None:
                                widget.setFont(QFont(load_custom_font(), font_size))
                            # 为label设置字体
                            label.setFont(QFont(load_custom_font(), font_size))
                            self.reward_labels.append(label)

                        # 计算所有标签的宽度之和，并考虑间距和边距
                        if self.reward_labels:
                            total_width = sum(label.sizeHint().width() for label in self.reward_labels) + \
                                          len(self.reward_labels) * 180
                            available_width = self.width() - 20
                            
                            # 如果总宽度超过可用宽度，则计算每行最多能放几个标签
                            if total_width > available_width:
                                avg_label_width = total_width / len(self.reward_labels)
                                max_columns = max(1, int(available_width // avg_label_width))
                            else:
                                max_columns = len(self.reward_labels)  # 一行显示所有标签
                        else:
                            max_columns = 1
                        
                        # 复用 container 和 vbox_layout
                        if not hasattr(self, 'container'):
                            self.container = QWidget()
                            self.vbox_layout = QGridLayout()
                            # 设置标签之间的水平和垂直间距
                            self.vbox_layout.setSpacing(15)  # 设置统一的间距
                            self.vbox_layout.setHorizontalSpacing(20)  # 设置水平间距
                            self.vbox_layout.setVerticalSpacing(10)   # 设置垂直间距
                            self.container.setLayout(self.vbox_layout)
                        else:
                            # 清空旧标签
                            for i in reversed(range(self.vbox_layout.count())):
                                item = self.vbox_layout.itemAt(i)
                                if item.widget():
                                    item.widget().setParent(None)

                        for i, label in enumerate(self.reward_labels):
                            row = i // max_columns
                            col = i % max_columns
                            self.vbox_layout.addWidget(label, row, col)
                        
                        self.result_grid.addWidget(self.container)
                        
                        if self.draw_mode in ["until_reboot", "until_all"]:
                            # 更新抽取记录
                            drawn_rewards.extend([s[1].replace(' ', '') for s in selected_rewards])
                            with open_file(draw_record_file, 'w', encoding='utf-8') as f:
                                json.dump(drawn_rewards, f, ensure_ascii=False, indent=4)

                        self.update_total_count()
                        return
                    else:
                        if self.draw_mode in ["until_reboot", "until_all"]:
                            # 删除临时文件
                            if path_manager.file_exists(draw_record_file):
                                os.remove(draw_record_file)

                        self.random()
                        return

        else:
            self.clear_layout(self.result_grid)
            if hasattr(self, 'container'):
                self.container.deleteLater()
                del self.container
            if hasattr(self, 'reward_labels'):
                for label in self.reward_labels:
                    label.deleteLater()
            
            # 创建错误标签
            error_label = BodyLabel("-- 抽选失败")
            error_label.setAlignment(Qt.AlignCenter)
            
            # 获取字体大小设置
            try:
                with open_file(path_manager.get_settings_path(), 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    font_size = settings['pumping_reward']['font_size']
            except Exception as e:
                font_size = 50
                logger.error(f"加载字体设置时出错: {e}, 使用默认设置")
            error_label.setFont(QFont(load_custom_font(), font_size))
            self.result_grid.addWidget(error_label)

    def _generate_vibrant_color(self):
        """生成鲜艳的随机颜色
        使用HSV色彩空间生成高饱和度和适中亮度的颜色，确保颜色鲜艳直观
        返回格式为"rgb(r,g,b)"的字符串
        """
        import colorsys
        # 随机生成色调 (0-1)
        h = random.random()
        # 高饱和度 (0.7-1.0) 确保颜色鲜艳
        s = random.uniform(0.7, 1.0)
        # 适中亮度 (0.7-1.0) 避免过暗或过亮
        v = random.uniform(0.7, 1.0)
        
        # 将HSV转换为RGB
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        # 转换为0-255范围的整数
        r, g, b = int(r * 255), int(g * 255), int(b * 255)
        
        return f"rgb({r},{g},{b})"

    # 清除旧布局和标签
    def clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
    
    def _connect_cleanup_signal(self):
        """连接清理信号"""
        try:
            # 查找主窗口实例
            parent = self.parent()
            while parent is not None:
                if hasattr(parent, 'cleanup_signal'):
                    # 连接主窗口的清理信号
                    parent.cleanup_signal.connect(self._on_cleanup_signal)
                    logger.info("星野连接: 抽奖界面已连接到主窗口清理信号～")
                    return
                parent = parent.parent()
            
            # 如果没找到，尝试通过应用程序查找主窗口
            for widget in QApplication.topLevelWidgets():
                if hasattr(widget, 'cleanup_signal'):
                    widget.cleanup_signal.connect(self._on_cleanup_signal)
                    logger.info("星野连接: 已通过应用程序查找连接主窗口清理信号～")
                    return
            
            logger.warning("星野警告: 未找到主窗口实例，清理信号连接失败～")
        except Exception as e:
            logger.error(f"星野连接失败: 连接清理信号时出错喵～ {e}")
    
    def _on_cleanup_signal(self):
        """处理清理信号，清除标签"""
        try:
            # 清除结果区域的标签
            self.clear_layout(self.result_grid)
            # 更新总奖数显示
            self.update_total_count()
            logger.info("星野清理: 抽奖界面已清除所有标签～")
        except Exception as e:
            logger.error(f"星野清理失败: 清除抽奖界面标签时出错喵～ {e}")

    # 获取随机抽取方法的设置
    def get_random_method_setting(self):
        """获取随机抽取方法的设置"""
        try:
            with open_file(path_manager.get_settings_path(), 'r', encoding='utf-8') as f:
                settings = json.load(f)
                random_method = settings['pumping_reward']['draw_pumping']
                return random_method
        except Exception as e:
            logger.error(f"加载随机抽取方法设置时出错: {e}, 使用默认设置")
            return 0

    # 更新历史记录
    def _update_history(self, reward_name, selected_rewards):
        """更新历史记录"""
        try:
            with open_file(path_manager.get_settings_path(), 'r', encoding='utf-8') as f:
                settings = json.load(f)
                reward_history_enabled = settings['history']['reward_history_enabled']
        except Exception as e:
            reward_history_enabled = False
            logger.error(f"加载历史记录设置时出错: {e}, 使用默认设置")
        
        if not reward_history_enabled:
            logger.info("历史记录功能已被禁用。")
            return
        
        history_file = path_manager.get_resource_path("reward/history", f"{reward_name}.json")
        os.makedirs(os.path.dirname(history_file), exist_ok=True)
        
        history_data = {}
        if path_manager.file_exists(history_file):
            with open_file(history_file, 'r', encoding='utf-8') as f:
                try:
                    history_data = json.load(f)
                except json.JSONDecodeError:
                    history_data = {}
        
        # 初始化数据结构
        if "pumping_reward" not in history_data:
            history_data["pumping_reward"] = {}
        if "total_rounds" not in history_data:
            history_data["total_rounds"] = 0
        
        # 更新总轮次
        history_data["total_rounds"] += 1

        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 更新被选中奖品的记录
        for reward_id, reward_name, probability in selected_rewards:
            # 获取奖品信息
            if reward_name not in history_data["pumping_reward"]:
                history_data["pumping_reward"][reward_name] = {
                    "total_number_of_times": 1,
                    "last_drawn_time": current_time,
                    "rounds_missed": 0,
                    "time": [{
                        "draw_method": self.draw_mode,
                        "draw_time": current_time,
                        "draw_reward_numbers": self.current_count
                    }]
                }
            else:
                history_data["pumping_reward"][reward_name]["total_number_of_times"] += 1
                history_data["pumping_reward"][reward_name]["last_drawn_time"] = current_time
                history_data["pumping_reward"][reward_name]["rounds_missed"] = 0
                history_data["pumping_reward"][reward_name]["time"].append({
                    "draw_method": self.draw_mode,
                    "draw_time": current_time,
                    "draw_reward_numbers": self.current_count
                })
        
        # 更新未被选中奖品的rounds_missed
        all_rewards = set()
        reward_file = path_manager.get_resource_path("reward", f"{reward_name}.json")
        if path_manager.file_exists(reward_file):
            with open_file(reward_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for reward_name, reward_info in data.items():
                    if isinstance(reward_info, dict) and 'id' in reward_info:
                        name = reward_name
                        all_rewards.add(name)
        
        selected_names = {s[1] for s in selected_rewards}
        for reward_name in all_rewards:
            if reward_name in history_data["pumping_reward"] and reward_name not in selected_names:
                history_data["pumping_reward"][reward_name]["rounds_missed"] += 1
        
        # 保存历史记录
        with open_file(history_file, 'w', encoding='utf-8') as f:
            json.dump(history_data, f, ensure_ascii=False, indent=4)

    # 更新总奖数显示   
    def update_total_count(self):
        """根据选择的奖池更新总奖数显示"""
        reward_name = self.reward_combo.currentText()

        try:
            with open_file(path_manager.get_settings_path("custom_settings.json"), 'r', encoding='utf-8') as f:
                settings = json.load(f)
                pumping_reward_reward_quantity = settings['reward']['reward_theme']
        except Exception:
            pumping_reward_reward_quantity = 0

        if reward_name and reward_name not in ["你暂未添加奖池", "加载奖池列表失败"] and pumping_reward_reward_quantity != 3:
            reward_file = path_manager.get_resource_path("reward", f"{reward_name}.json")
            if path_manager.file_exists(reward_file):
                cleaned_data = self._get_cleaned_data(reward_file)
                drawn_count = self._get_drawn_count(reward_name)
                _count = len(cleaned_data) - drawn_count
                count = len(cleaned_data)
                if _count <= 0:
                    _count = count
                    InfoBar.success(
                        title='抽取完成',
                        content="抽取完了所有奖品了！记录已清除!",
                        orient=Qt.Horizontal,
                        parent=self,
                        isClosable=True,
                        duration=3000,
                        position=InfoBarPosition.TOP
                    )
                if pumping_reward_reward_quantity == 1:
                    self.total_label.setText(f'总奖数: {count}')
                elif pumping_reward_reward_quantity == 2:
                    self.total_label.setText(f'剩余奖数: {_count}')
                else:
                    self.total_label.setText(f'总奖数: {count} | 剩余奖数: {_count}')
                self.max_count = count
                self._update_count_display()
            else:
                self._set_default_count(pumping_reward_reward_quantity)
        else:
            self._set_default_count(pumping_reward_reward_quantity)

    # 对用户的选择进行返回奖品数量数量
    def _get_cleaned_data(self, reward_file):
        with open_file(reward_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # 初始化不同情况的列表
            cleaned_data = []
            for reward_name, reward_info in data.items():
                if isinstance(reward_info, dict) and 'id' in reward_info:
                    id = reward_info.get('id', '')
                    name = reward_name
                    probability = float(reward_info.get('probability', 1.0))
                    cleaned_data.append((id, name, probability))

            return cleaned_data

    # 获取已抽取奖数
    def _get_drawn_count(self, reward_name):
        if self.draw_mode in ["until_reboot", "until_all"]:
            if self.draw_mode == "until_reboot":
                draw_record_file = path_manager.get_temp_path(f"until_the_reboot_{reward_name}.json")
            elif self.draw_mode == "until_all":
                draw_record_file = path_manager.get_temp_path(f"until_all_draw_{reward_name}.json")
            if path_manager.file_exists(draw_record_file):
                try:
                    with open_file(draw_record_file, 'r', encoding='utf-8') as f:
                        return len(json.load(f))
                except Exception as e:
                    # 处理加载文件出错的情况，返回 0
                    logger.error(f"加载抽取记录文件 {draw_record_file} 出错: {e}")
                    return 0
            else:
                return 0
        else:
            return 0

    # 设置默认总奖数显示
    def _set_default_count(self, pumping_reward_reward_quantity):
        if pumping_reward_reward_quantity != 3:
            if pumping_reward_reward_quantity == 1:
                self.total_label.setText('总奖数: 0')
            elif pumping_reward_reward_quantity == 2:
                self.total_label.setText('剩余奖数: 0')
            else:
                self.total_label.setText('总奖数: 0 | 剩余奖数: 0')
            self.max_count = 0
            self._update_count_display()
    
    # 增加抽取奖数
    def _increase_count(self):
        """增加抽取奖数"""
        if self.current_count < self.max_count:
            self.current_count += 1
            self._update_count_display()

    # 减少抽取奖数        
    def _decrease_count(self):
        """减少抽取奖数"""
        if self.current_count > 1:
            self.current_count -= 1
            self._update_count_display()

    # 更新奖数显示        
    def _update_count_display(self):
        """更新奖数显示"""
        self.count_label.setText(str(self.current_count))
        
        # 根据当前奖数启用/禁用按钮
        self.plus_button.setEnabled(self.current_count < self.max_count)
        self.minus_button.setEnabled(self.current_count > 1)

        if not self.is_animating:
            self.start_button.setEnabled(self.current_count <= self.max_count and self.current_count > 0)
    
    # 刷新奖池列表         
    def refresh_reward_list(self):
        """刷新奖池下拉框选项"""
        self.reward_combo.clear()
        try:
            list_folder = path_manager.get_resource_path("reward")
            if path_manager.file_exists(list_folder) and os.path.isdir(list_folder):
                files = os.listdir(list_folder)
                classes = []
                for file in files:
                    if file.endswith('.json'):
                        reward_name = os.path.splitext(file)[0]
                        classes.append(reward_name)
                
                self.reward_combo.clear()
                if classes:
                    self.reward_combo.addItems(classes)
                else:
                    logger.error("你暂未添加奖池")
                    self.reward_combo.addItem("你暂未添加奖池")
            else:
                logger.error("你暂未添加奖池")
                self.reward_combo.addItem("你暂未添加奖池")
        except Exception as e:
            logger.error(f"加载奖池名称失败: {str(e)}")

        self.update_total_count()

        InfoBar.success(
            title='奖池列表',
            content="奖池列表更新成功！",
            orient=Qt.Horizontal,
            parent=self,
            isClosable=True,
            duration=3000,
            position=InfoBarPosition.TOP
        )
    
    # 恢复初始状态
    def _reset_to_initial_state(self):
        """恢复初始状态"""
        self._clean_temp_files()
        self.current_count = 1
        self.update_total_count()
        self.clear_layout(self.result_grid)

    # 清理临时文件
    def _clean_temp_files(self):
        import glob
        temp_dir = path_manager.get_temp_path()
        if path_manager.file_exists(temp_dir):
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
            with open_file(path_manager.get_settings_path("custom_settings.json"), 'r', encoding='utf-8') as f:
                settings = json.load(f)
                main_window_control_Switch = settings['reward']['pumping_reward_control_Switch']
                show_reset_button = settings['reward']['show_reset_button']
                show_refresh_button = settings['reward']['show_refresh_button']
                show_quantity_control = settings['reward']['show_quantity_control']
                show_start_button = settings['reward']['show_start_button']
                show_list_toggle = settings['reward']['show_list_toggle']
                pumping_reward_reward_quantity = settings['reward']['reward_theme']
        except Exception as e:
            logger.error(f"加载设置时出错: {e}, 使用默认设置")
            show_reset_button = True
            show_refresh_button = True
            show_quantity_control = True
            show_list_toggle = True
            show_start_button = True
            main_window_control_Switch = True
            pumping_reward_reward_quantity = 0

        # 主布局
        scroll_area = SingleDirectionScrollArea()
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
        """)
        # 启用触屏滚动
        QScroller.grabGesture(scroll_area.viewport(), QScroller.LeftMouseButtonGesture)
        
        # 创建主容器和布局
        container = QWidget(scroll_area)
        scroll_area_container = QVBoxLayout(container)
        
        # 控制面板
        control_panel = QVBoxLayout()
        control_panel.setContentsMargins(10, 10, 10, 10)

        # 刷新按钮
        if show_reset_button:
            self.refresh_button = PushButton('重置已抽取名单')
            self.refresh_button.setFixedSize(180, 50)
            self.refresh_button.setFont(QFont(load_custom_font(), 13))
            self.refresh_button.clicked.connect(self._reset_to_initial_state)
            self.refresh_button.clicked.connect(self.update_total_count)
            control_panel.addWidget(self.refresh_button, 0, Qt.AlignVCenter)

        # 刷新按钮
        if show_refresh_button:
            self.refresh_button = PushButton('刷新奖品列表')
            self.refresh_button.setFixedSize(180, 50)
            self.refresh_button.setFont(QFont(load_custom_font(), 13))
            self.refresh_button.clicked.connect(self.refresh_reward_list)
            self.refresh_button.clicked.connect(self.update_total_count)
            control_panel.addWidget(self.refresh_button, 0, Qt.AlignVCenter)

        # 创建一个水平布局
        horizontal_layout = QHBoxLayout()

        # 减号按钮
        self.minus_button = PushButton('-')
        self.minus_button.setFixedSize(50, 50)
        self.minus_button.setFont(QFont(load_custom_font(), 25))
        self.minus_button.clicked.connect(self._decrease_count)
        horizontal_layout.addWidget(self.minus_button, 0, Qt.AlignLeft)

        # 奖数显示
        self.count_label = BodyLabel('1')
        self.count_label.setAlignment(Qt.AlignCenter)
        self.count_label.setFont(QFont(load_custom_font(), 25))
        self.count_label.setFixedWidth(65)
        horizontal_layout.addWidget(self.count_label, 0, Qt.AlignLeft)

        # 加号按钮
        self.plus_button = PushButton('+')
        self.plus_button.setFixedSize(50, 50)
        self.plus_button.setFont(QFont(load_custom_font(), 25))
        self.plus_button.clicked.connect(self._increase_count)
        horizontal_layout.addWidget(self.plus_button, 0, Qt.AlignLeft)

        # 奖数控制开关
        if show_quantity_control:
            control_panel.addLayout(horizontal_layout)

        # 开始按钮
        if show_start_button:
            self.start_button = PrimaryPushButton('开始')
            self.start_button.setObjectName("rewardButton")
            self.start_button.setFixedSize(180, 50)
            self.start_button.setFont(QFont(load_custom_font(), 15))
            self.start_button.clicked.connect(self.start_draw)
            control_panel.addWidget(self.start_button, 0, Qt.AlignVCenter)
        
        # 奖池下拉框
        self.reward_combo = ComboBox()
        self.reward_combo.setFixedSize(180, 50)
        self.reward_combo.setFont(QFont(load_custom_font(), 13))
        
        # 加载奖池列表
        try:
            list_folder = path_manager.get_resource_path("reward")
            if path_manager.file_exists(list_folder) and os.path.isdir(list_folder):
                files = os.listdir(list_folder)
                classes = []
                for file in files:
                    if file.endswith('.json'):
                        reward_name = os.path.splitext(file)[0]
                        classes.append(reward_name)
                
                self.reward_combo.clear()
                if classes:
                    self.reward_combo.addItems(classes)
                else:
                    logger.error("你暂未添加奖池")
                    self.reward_combo.addItem("你暂未添加奖池")
            else:
                logger.error("你暂未添加奖池")
                self.reward_combo.addItem("你暂未添加奖池")
        except Exception as e:
            logger.error(f"加载奖池列表失败: {str(e)}")
            self.reward_combo.addItem("加载奖池列表失败")
        
        # 奖池选择开关
        if show_list_toggle:
            control_panel.addWidget(self.reward_combo)
        
        # 总奖数和剩余奖数显示
        if pumping_reward_reward_quantity != 3:
            if pumping_reward_reward_quantity == 1:
                self.total_label = BodyLabel('总奖数: 0')
            elif pumping_reward_reward_quantity == 2:
                self.total_label = BodyLabel('剩余奖数: 0')
            else:
                self.total_label = BodyLabel('总奖数: 0 | 剩余奖数: 0')
            self.total_label.setFont(QFont(load_custom_font(), 11))
            self.total_label.setAlignment(Qt.AlignCenter)
            self.total_label.setFixedWidth(180)
            control_panel.addWidget(self.total_label, 0, Qt.AlignLeft)
        
        control_panel.addStretch(1)
        
        # 结果区域布局
        self.result_grid = QGridLayout()
        self.result_grid.setSpacing(10)

        scroll_area_container.addLayout(self.result_grid)
        
        # 奖池选择变化时更新总奖数
        self.reward_combo.currentTextChanged.connect(self.update_total_count)
        
        # 初始化抽取奖数
        self.current_count = 1
        self.max_count = 0
        
        # 初始化总奖数显示
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
        if main_window_control_Switch:
            main_layout.addWidget(scroll_area)
            main_layout.addWidget(control_button_widget)
        else:
            main_layout.addWidget(control_button_widget)
            main_layout.addWidget(scroll_area)

        # 显示主布局
        self.setLayout(main_layout)