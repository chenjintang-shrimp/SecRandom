from qfluentwidgets import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import os
import json
import random
import pyttsx3
from loguru import logger

from app.common.config import load_custom_font

class pumping_people(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # 定义变量
        self.is_animating = False
        self.draw_mode = "random"
        self.animation_timer = None
        # 使用全局语音引擎单例
        if not hasattr(QApplication.instance(), 'global_voice_engine'):
            QApplication.instance().global_voice_engine = pyttsx3.init()
            QApplication.instance().global_voice_engine.startLoop(False)
        self.voice_engine = QApplication.instance().global_voice_engine
        self.initUI()
    
    def start_draw(self):
        """开始抽选学生"""
        # 获取抽选模式和动画模式设置
        try:
            with open('app/Settings/Settings.json', 'r', encoding='utf-8') as f:
                settings = json.load(f)
                multi_player_animation_mode = settings['multi_player']['animation_mode']
                global_draw_mode = settings['global']['draw_mode']
                if multi_player_animation_mode == 0:
                    global_animation_mode = settings['global']['animation_mode']
        except Exception as e:
            multi_player_animation_mode = 1
            logger.error(f"加载设置时出错: {e}, 使用默认设置")

        # 根据抽选模式执行不同逻辑
        # 跟随全局设置
        if global_draw_mode == 0:  # 重复随机
            self.draw_mode = "random"
        elif global_draw_mode == 1:  # 不重复抽取(直到软件重启)
            self.draw_mode = "until_reboot"
        elif global_draw_mode == 2:  # 不重复抽取(直到抽完全部人)
            self.draw_mode = "until_all"
            
        # 根据动画模式执行不同逻辑
        if multi_player_animation_mode == 0 and global_animation_mode == 0:  # 手动停止动画
            self.start_button.setText("停止")
            self.is_animating = True
            self.animation_timer = QTimer()
            self.animation_timer.timeout.connect(self._show_random_student)
            self.animation_timer.start(100)
            self.start_button.clicked.disconnect()
            self.start_button.clicked.connect(self._stop_animation)
            
        elif multi_player_animation_mode == 0 and global_animation_mode == 1:  # 自动播放完整动画
            self._play_full_animation()
            
        elif multi_player_animation_mode == 0 and global_animation_mode == 2:  # 直接显示结果
            self._show_result_directly()
            
        # 跟随单抽动画设置
        elif multi_player_animation_mode == 1:  # 手动停止动画
            self.start_button.setText("停止")
            self.is_animating = True
            self.animation_timer = QTimer()
            self.animation_timer.timeout.connect(self._show_random_student)
            self.animation_timer.start(100)
            self.start_button.clicked.disconnect()
            self.start_button.clicked.connect(self._stop_animation)
            
        elif multi_player_animation_mode == 2:  # 自动播放完整动画
            self._play_full_animation()
            
        elif multi_player_animation_mode == 3:  # 直接显示结果
            self._show_result_directly()
        
    def _show_random_student(self):
        """显示随机学生（用于动画效果）"""
        class_name = self.class_combo.currentText()
        if class_name and class_name not in ["你暂未添加班级", "加载班级列表失败"]:
            try:
                with open('app/Settings/Settings.json', 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    list_strings_set = settings.get('list_strings', {})
                    list_strings_settings = list_strings_set.get('use_lists', False)
                    if not list_strings_settings:
                        student_file = f"app/resource/students/{class_name}.ini"
                    else:
                        student_file = f"app/resource/students/people_{class_name}.ini"
            except FileNotFoundError as e:
                logger.error(f"加载设置时出错: {e}, 使用默认显示仅学号显示")
                student_file = f"app/resource/students/people_{class_name}.ini"
            except KeyError:
                logger.error(f"设置文件中缺少foundation键, 使用默认仅学号显示")
                student_file = f"app/resource/students/people_{class_name}.ini"

            if os.path.exists(student_file):
                with open(student_file, 'r', encoding='utf-8') as f:
                    students = [(i+1, line.strip().replace(' ', '')) for i, line in enumerate(f) if line.strip() and '【' not in line.strip() and '】' not in line.strip()]
                    if students:
                        # 从self.current_count获取抽取人数
                        draw_count = self.current_count
                        
                        # 抽取多个学生
                        selected_students = random.sample(students, min(draw_count, len(students)))
                        
                        # 清除旧布局和标签
                        if hasattr(self, 'container'):
                            self.container.deleteLater()
                            del self.container

                        if hasattr(self, 'student_labels'):
                            for label in self.student_labels:
                                label.deleteLater()

                        # 删除布局中的所有内容
                        while self.result_layout.count(): 
                            item = self.result_layout.takeAt(0)
                            widget = item.widget()
                            if widget:
                                widget.deleteLater()
                        
                        # 根据设置格式化学号显示
                        try:
                            with open('app/Settings/Settings.json', 'r', encoding='utf-8') as f:
                                settings = json.load(f)

                                multi_player_student_id = settings['multi_player']['student_id']
                                multi_player_student_name = settings['multi_player']['student_name']
                                if multi_player_student_id == 0:
                                    global_student_id = settings['global']['student_id']
                                if multi_player_student_name == 0:
                                    global_student_name = settings['global']['student_name']
                        except Exception as e:
                            multi_player_student_id = 1
                            multi_player_student_name = 0
                            global_student_id = 0
                            global_student_name = 0
                            logger.error(f"加载设置时出错: {e}, 使用默认设置")

                        # 创建新布局
                        vbox_layout = QVBoxLayout()
                        # 创建新标签列表
                        self.student_labels = []
                        for num, name in selected_students:
                            # 整合学号格式和姓名处理逻辑
                            student_id_format = multi_player_student_id if multi_player_student_id != 0 else global_student_id
                            student_name_format = multi_player_student_name if multi_player_student_name != 0 else global_student_name
                            
                            # 根据学号格式生成标签文本
                            if student_id_format == 0:  # 补零
                                student_id_str = f"{num:02}"
                            elif student_id_format == 1:  # 居中显示
                                student_id_str = f"{num:^5}"
                            else:
                                student_id_str = f"{num:02}"
                            
                            # 处理两字姓名
                            if student_name_format == 0 and len(name) == 2:
                                name = f"{name[0]}    {name[1]}"

                            try:
                                with open('app/Settings/Settings.json', 'r', encoding='utf-8') as f:
                                    settings = json.load(f)
                                    list_strings_set = settings.get('list_strings', {})
                                    list_strings_settings = list_strings_set.get('use_lists', False)
                                    if not list_strings_settings:
                                        label = BodyLabel(f"{student_id_str} {name}")
                                    else:
                                        label = BodyLabel(f"{student_id_str}")
                            except FileNotFoundError as e:
                                logger.error(f"加载设置时出错: {e}, 使用默认显示仅学号显示")
                                label = BodyLabel(f"{student_id_str}")
                            except KeyError:
                                logger.error(f"设置文件中缺少foundation键, 使用默认仅学号显示")
                                label = BodyLabel(f"{student_id_str}")

                            label.setAlignment(Qt.AlignCenter)
                            # 读取设置中的font_size值
                            try:
                                with open('app/Settings/Settings.json', 'r', encoding='utf-8') as f:
                                    settings = json.load(f)
                                    font_size = settings['multi_player']['font_size']
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
                        # 创建容器并添加到布局
                        container = QWidget()
                        container.setLayout(vbox_layout)
                        self.result_layout.addWidget(container)
                        
                        return
        
        else:
            # 清除旧布局和标签
            if hasattr(self, 'container'):
                self.container.deleteLater()
                del self.container
            if hasattr(self, 'student_labels'):
                for label in self.student_labels:
                    label.deleteLater()

            # 删除布局中的所有内容
            while self.result_layout.count(): 
                item = self.result_layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
                    
            error_label = BodyLabel("-- 抽选失败")
            error_label.setAlignment(Qt.AlignCenter)
            # 读取设置中的font_size值
            try:
                with open('app/Settings/Settings.json', 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    font_size = settings['multi_player']['font_size']
                    if font_size < 30:
                        font_size = 85
            except Exception as e:
                font_size = 85
                logger.error(f"加载字体设置时出错: {e}, 使用默认设置")
            # 根据设置调整字体大小
            if font_size < 30:
                error_label.setFont(QFont(load_custom_font(), 85))
            else:
                error_label.setFont(QFont(load_custom_font(), font_size))
            self.result_layout.addWidget(error_label)
    
    def _stop_animation(self):
        """停止动画并显示最终结果"""
        self.animation_timer.stop()
        self.is_animating = False
        self.start_button.setText("开始")
        self.start_button.clicked.disconnect()
        self.start_button.clicked.connect(self.start_draw)
        
        # 根据抽选模式显示最终结果
        if self.draw_mode == "random":
            self.random_draw()
        elif self.draw_mode == "until_reboot":
            self.until_the_reboot_draw()
        elif self.draw_mode == "until_all":
            self.until_all_draw_mode()
            
        # 动画结束后进行语音播报
        try:
            with open('app/Settings/Settings.json', 'r', encoding='utf-8') as f:
                settings = json.load(f)
                voice_enabled = settings['multi_player']['voice_enabled']
                if voice_enabled == 0:
                    voice_enabled = settings['global']['voice_enabled']
                
                if voice_enabled == 1 or voice_enabled == True:  # 开启语音
                    if hasattr(self, 'student_labels'):
                        for label in self.student_labels:
                            parts = label.text().split()
                            if len(parts) >= 2 and len(parts[-1]) == 1 and len(parts[-2]) == 1:
                                name = parts[-2] + parts[-1]
                            else:
                                name = parts[-1]
                            name = name.replace(' ', '')
                            try:
                                with open('app/Settings/Settings.json', 'r', encoding='utf-8') as f:
                                    settings = json.load(f)
                                    list_strings_set = settings.get('list_strings', {})
                                    list_strings_settings = list_strings_set.get('use_lists', False)
                                    if not list_strings_settings:
                                        self.voice_engine.say(f"{name}")
                                        self.voice_engine.iterate()
                                    else:
                                        self.voice_engine.say(f"{name}号")
                                        self.voice_engine.iterate()
                            except FileNotFoundError as e:
                                logger.error(f"加载设置时出错: {e}, 使用默认显示仅学号朗读")
                                self.voice_engine.say(f"{name}号")
                                self.voice_engine.iterate()
                            except KeyError:
                                logger.error(f"设置文件中缺少foundation'键, 使用默认仅学号朗读")
                                self.voice_engine.say(f"{name}号")
                                self.voice_engine.iterate()
        except Exception as e:
            logger.error(f"语音播报出错: {e}")
    
    def _play_full_animation(self):
        """播放完整动画（快速显示5个随机学生后显示最终结果）"""
        self.is_animating = True
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self._show_random_student)
        self.animation_timer.start(100)
        self.start_button.setEnabled(False)  # 禁用按钮
        
        # 5次随机后停止
        QTimer.singleShot(500, lambda: [
            self.animation_timer.stop(),
            self._stop_animation(),
            self.start_button.setEnabled(True)  # 恢复按钮
          ])
    
    def _show_result_directly(self):
        """直接显示结果（无动画效果）"""
        if self.draw_mode == "random":
            self.random_draw()
        elif self.draw_mode == "until_reboot":
            self.until_the_reboot_draw()
        elif self.draw_mode == "until_all":
            self.until_all_draw_mode()

        # 动画结束后进行语音播报
        try:
            with open('app/Settings/Settings.json', 'r', encoding='utf-8') as f:
                settings = json.load(f)
                voice_enabled = settings['multi_player']['voice_enabled']
                if voice_enabled == 0:
                    voice_enabled = settings['global']['voice_enabled']
                
                if voice_enabled == 1 or voice_enabled == True:  # 开启语音
                    if hasattr(self, 'student_labels'):
                        for label in self.student_labels:
                            parts = label.text().split()
                            if len(parts) >= 2 and len(parts[-1]) == 1 and len(parts[-2]) == 1:
                                name = parts[-2] + parts[-1]
                            else:
                                name = parts[-1]
                            name = name.replace(' ', '')
                            try:
                                with open('app/Settings/Settings.json', 'r', encoding='utf-8') as f:
                                    settings = json.load(f)
                                    list_strings_set = settings.get('list_strings', {})
                                    list_strings_settings = list_strings_set.get('use_lists', False)
                                    if not list_strings_settings:
                                        self.voice_engine.say(f"{name}")
                                        self.voice_engine.iterate()
                                    else:
                                        self.voice_engine.say(f"{name}号")
                                        self.voice_engine.iterate()
                            except FileNotFoundError as e:
                                logger.error(f"加载设置时出错: {e}, 使用默认显示仅学号朗读")
                                self.voice_engine.say(f"{name}号")
                                self.voice_engine.iterate()
                            except KeyError:
                                logger.error(f"设置文件中缺少foundation'键, 使用默认仅学号朗读")
                                self.voice_engine.say(f"{name}号")
                                self.voice_engine.iterate()
        except Exception as e:
            logger.error(f"语音播报出错: {e}")
            
    def random_draw(self):
        """重复随机抽选学生"""
        class_name = self.class_combo.currentText()
        if class_name and class_name not in ["你暂未添加班级", "加载班级列表失败"]:
            try:
                with open('app/Settings/Settings.json', 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    list_strings_set = settings.get('list_strings', {})
                    list_strings_settings = list_strings_set.get('use_lists', False)
                    if not list_strings_settings:
                        student_file = f"app/resource/students/{class_name}.ini"
                    else:
                        student_file = f"app/resource/students/people_{class_name}.ini"
            except FileNotFoundError as e:
                logger.error(f"加载设置时出错: {e}, 使用默认显示仅学号显示")
                student_file = f"app/resource/students/people_{class_name}.ini"
            except KeyError:
                logger.error(f"设置文件中缺少foundation键, 使用默认仅学号显示")
                student_file = f"app/resource/students/people_{class_name}.ini"

            if os.path.exists(student_file):
                with open(student_file, 'r', encoding='utf-8') as f:
                    students = [(i+1, line.strip().replace(' ', '')) for i, line in enumerate(f) if line.strip() and '【' not in line.strip() and '】' not in line.strip()]     
                    available_students = [s for s in students if s[1].replace(' ', '')]
                    
                    if available_students:
                        # 从self.current_count获取抽取人数
                        draw_count = self.current_count
                        
                        # 抽取多个学生
                        selected_students = random.sample(available_students, min(draw_count, len(available_students)))
                        
                        # 清除旧布局和标签
                        if hasattr(self, 'container'):
                            self.container.deleteLater()
                            del self.container
                        if hasattr(self, 'student_labels'):
                            for label in self.student_labels:
                                label.deleteLater()

                        # 删除布局中的所有内容
                        while self.result_layout.count(): 
                            item = self.result_layout.takeAt(0)
                            widget = item.widget()
                            if widget:
                                widget.deleteLater()
                        
                        # 根据设置格式化学号显示
                        try:
                            with open('app/Settings/Settings.json', 'r', encoding='utf-8') as f:
                                settings = json.load(f)

                                multi_player_student_id = settings['multi_player']['student_id']
                                multi_player_student_name = settings['multi_player']['student_name']
                                if multi_player_student_id == 0:
                                    global_student_id = settings['global']['student_id']
                                if multi_player_student_name == 0:
                                    global_student_name = settings['global']['student_name']
                        except Exception as e:
                            multi_player_student_id = 1
                            multi_player_student_name = 0
                            global_student_id = 0
                            global_student_name = 0
                            logger.error(f"加载设置时出错: {e}, 使用默认设置")

                        # 创建新布局
                        vbox_layout = QVBoxLayout()
                        # 创建新标签列表
                        self.student_labels = []
                        for num, selected in selected_students:
                            # 整合学号格式和姓名处理逻辑
                            student_id_format = multi_player_student_id if multi_player_student_id != 0 else global_student_id
                            student_name_format = multi_player_student_name if multi_player_student_name != 0 else global_student_name
                            
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

                            # 读取设置中的history_enabled
                            try:
                                with open('app/Settings/Settings.json', 'r', encoding='utf-8') as f:
                                    settings = json.load(f)
                                    history_enabled = settings['history']['history_enabled']
                            except Exception as e:
                                history_enabled = False
                                logger.error(f"加载历史记录设置时出错: {e}, 使用默认设置")

                            if history_enabled:
                                # 记录抽选历史
                                try:
                                    with open('app/Settings/Settings.json', 'r', encoding='utf-8') as f:
                                        settings = json.load(f)
                                        list_strings_set = settings.get('list_strings', {})
                                        list_strings_settings = list_strings_set.get('use_lists', False)
                                        if not list_strings_settings:
                                            history_file = f"app/resource/history/{class_name}.json"
                                        else:
                                            history_file = f"app/resource/history/people_{class_name}.json"
                                except FileNotFoundError as e:
                                    logger.error(f"加载设置时出错: {e}, 使用默认显示仅学号记录历史")
                                    history_file = f"app/resource/history/people_{class_name}.json"
                                except KeyError:
                                    logger.error(f"设置文件中缺少foundation键, 使用默认仅学号记录历史")
                                    history_file = f"app/resource/history/people_{class_name}.json"

                                os.makedirs(os.path.dirname(history_file), exist_ok=True)
                                
                                history_data = {}
                                if os.path.exists(history_file):
                                    with open(history_file, 'r', encoding='utf-8') as f:
                                        try:
                                            history_data = json.load(f)
                                        except json.JSONDecodeError:
                                            history_data = {}
                                
                                if "multi" not in history_data:
                                    history_data["multi"] = {}

                                import datetime

                                if selected not in history_data["multi"]:
                                    history_data["multi"][selected] = {
                                        "total_number_of_times": 1,
                                        "time": [
                                            {
                                                "draw_method": {
                                                    self.draw_mode: datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                                }
                                            }
                                        ]
                                    }
                                else:
                                    history_data["multi"][selected]["total_number_of_times"] += 1
                                    history_data["multi"][selected]["time"].append({
                                        "draw_method": {
                                            self.draw_mode: datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                        }
                                    })
                                
                                with open(history_file, 'w', encoding='utf-8') as f:
                                    json.dump(history_data, f, ensure_ascii=False, indent=4)

                            else:
                                logger.info("历史记录功能已被禁用。")

                            try:
                                with open('app/Settings/Settings.json', 'r', encoding='utf-8') as f:
                                    settings = json.load(f)
                                    list_strings_set = settings.get('list_strings', {})
                                    list_strings_settings = list_strings_set.get('use_lists', False)
                                    if not list_strings_settings:
                                        label = BodyLabel(f"{student_id_str} {name}")
                                    else:
                                        label = BodyLabel(f"{student_id_str}")
                            except FileNotFoundError as e:
                                logger.error(f"加载设置时出错: {e}, 使用默认显示仅学号显示")
                                label = BodyLabel(f"{student_id_str}")
                            except KeyError:
                                logger.error(f"设置文件中缺少foundation键, 使用默认仅学号显示")
                                label = BodyLabel(f"{student_id_str}")

                            label.setAlignment(Qt.AlignCenter)
                            # 读取设置中的font_size值
                            try:
                                with open('app/Settings/Settings.json', 'r', encoding='utf-8') as f:
                                    settings = json.load(f)
                                    font_size = settings['multi_player']['font_size']
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
                        # 创建容器并添加到布局
                        container = QWidget()
                        container.setLayout(vbox_layout)
                        self.result_layout.addWidget(container)

                        return
            
        else:
            # 清除旧布局和标签
            if hasattr(self, 'container'):
                self.container.deleteLater()
                del self.container
            if hasattr(self, 'student_labels'):
                for label in self.student_labels:
                    label.deleteLater()

            # 删除布局中的所有内容
            while self.result_layout.count(): 
                item = self.result_layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()

            error_label = BodyLabel("-- 抽选失败")
            error_label.setAlignment(Qt.AlignCenter)
            # 读取设置中的font_size值
            try:
                with open('app/Settings/Settings.json', 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    font_size = settings['multi_player']['font_size']
                    if font_size < 30:
                        font_size = 85
            except Exception as e:
                font_size = 85
                logger.error(f"加载字体设置时出错: {e}, 使用默认设置")
            # 根据设置调整字体大小
            if font_size < 30:
                error_label.setFont(QFont(load_custom_font(), 85))
            else:
                error_label.setFont(QFont(load_custom_font(), font_size))
            self.result_layout.addWidget(error_label)
    
        
    def until_the_reboot_draw(self):
        """不重复抽取(直到软件重启)"""
        class_name = self.class_combo.currentText()
        if class_name and class_name not in ["你暂未添加班级", "加载班级列表失败"]:
            try:
                with open('app/Settings/Settings.json', 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    list_strings_set = settings.get('list_strings', {})
                    list_strings_settings = list_strings_set.get('use_lists', False)
                    if not list_strings_settings:
                        student_file = f"app/resource/students/{class_name}.ini"
                    else:
                        student_file = f"app/resource/students/people_{class_name}.ini"
            except FileNotFoundError as e:
                logger.error(f"加载设置时出错: {e}, 使用默认显示仅学号显示")
                student_file = f"app/resource/students/people_{class_name}.ini"
            except KeyError:
                logger.error(f"设置文件中缺少foundation键, 使用默认仅学号显示")
                student_file = f"app/resource/students/people_{class_name}.ini"

            # 根据抽取作用范围模式确定记录文件名
            with open('app/Settings/Settings.json', 'r', encoding='utf-8') as f:
                settings = json.load(f)
                extraction_scope = settings['global']['extraction_scope']
            
            if extraction_scope == 1:  # 隔离模式
                draw_record_file = f"app/resource/Temp/until_the_reboot_scope_{class_name}_multi.json"
            else:  # 共享模式
                draw_record_file = f"app/resource/Temp/until_the_reboot_draw_{class_name}.json"
            
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
            
            if os.path.exists(student_file):
                with open(student_file, 'r', encoding='utf-8') as f:
                    students = [(i+1, line.strip().replace(' ', '')) for i, line in enumerate(f) if line.strip() and '【' not in line.strip() and '】' not in line.strip()]     
                    available_students = [s for s in students if s[1].replace(' ', '') not in [x.replace(' ', '') for x in drawn_students]]
                    
                    if available_students:
                        # 从self.current_count获取抽取人数
                        draw_count = self.current_count
                        
                        # 抽取多个学生
                        selected_students = random.sample(available_students, min(draw_count, len(available_students)))
                        
                        # 清除旧布局和标签
                        if hasattr(self, 'container'):
                            self.container.deleteLater()
                            del self.container
                        if hasattr(self, 'student_labels'):
                            for label in self.student_labels:
                                label.deleteLater()

                        # 删除布局中的所有内容
                        while self.result_layout.count(): 
                            item = self.result_layout.takeAt(0)
                            widget = item.widget()
                            if widget:
                                widget.deleteLater()
                        
                        # 根据设置格式化学号显示
                        try:
                            with open('app/Settings/Settings.json', 'r', encoding='utf-8') as f:
                                settings = json.load(f)

                                multi_player_student_id = settings['multi_player']['student_id']
                                multi_player_student_name = settings['multi_player']['student_name']
                                if multi_player_student_id == 0:
                                    global_student_id = settings['global']['student_id']
                                if multi_player_student_name == 0:
                                    global_student_name = settings['global']['student_name']
                        except Exception as e:
                            multi_player_student_id = 1
                            multi_player_student_name = 0
                            global_student_id = 0
                            global_student_name = 0
                            logger.error(f"加载设置时出错: {e}, 使用默认设置")

                        # 创建新布局
                        vbox_layout = QVBoxLayout()
                        # 创建新标签列表
                        self.student_labels = []
                        for num, selected in selected_students:
                            # 整合学号格式和姓名处理逻辑
                            student_id_format = multi_player_student_id if multi_player_student_id != 0 else global_student_id
                            student_name_format = multi_player_student_name if multi_player_student_name != 0 else global_student_name
                            
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

                            # 读取设置中的history_enabled
                            try:
                                with open('app/Settings/Settings.json', 'r', encoding='utf-8') as f:
                                    settings = json.load(f)
                                    history_enabled = settings['history']['history_enabled']
                            except Exception as e:
                                history_enabled = False
                                logger.error(f"加载历史记录设置时出错: {e}, 使用默认设置")

                            if history_enabled:
                                # 记录抽选历史
                                try:
                                    with open('app/Settings/Settings.json', 'r', encoding='utf-8') as f:
                                        settings = json.load(f)
                                        list_strings_set = settings.get('list_strings', {})
                                        list_strings_settings = list_strings_set.get('use_lists', False)
                                        if not list_strings_settings:
                                            history_file = f"app/resource/history/{class_name}.json"
                                        else:
                                            history_file = f"app/resource/history/people_{class_name}.json"
                                except FileNotFoundError as e:
                                    logger.error(f"加载设置时出错: {e}, 使用默认显示仅学号记录历史")
                                    history_file = f"app/resource/history/people_{class_name}.json"
                                except KeyError:
                                    logger.error(f"设置文件中缺少foundation键, 使用默认仅学号记录历史")
                                    history_file = f"app/resource/history/people_{class_name}.json"

                                os.makedirs(os.path.dirname(history_file), exist_ok=True)
                                
                                history_data = {}
                                if os.path.exists(history_file):
                                    with open(history_file, 'r', encoding='utf-8') as f:
                                        try:
                                            history_data = json.load(f)
                                        except json.JSONDecodeError:
                                            history_data = {}
                                
                                if "multi" not in history_data:
                                    history_data["multi"] = {}

                                import datetime

                                if selected not in history_data["multi"]:
                                    history_data["multi"][selected] = {
                                        "total_number_of_times": 1,
                                        "time": [
                                            {
                                                "draw_method": {
                                                    self.draw_mode: datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                                }
                                            }
                                        ]
                                    }
                                else:
                                    history_data["multi"][selected]["total_number_of_times"] += 1
                                    history_data["multi"][selected]["time"].append({
                                        "draw_method": {
                                            self.draw_mode: datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                        }
                                    })
                                
                                with open(history_file, 'w', encoding='utf-8') as f:
                                    json.dump(history_data, f, ensure_ascii=False, indent=4)

                            else:
                                logger.info("历史记录功能已被禁用。")

                            try:
                                with open('app/Settings/Settings.json', 'r', encoding='utf-8') as f:
                                    settings = json.load(f)
                                    list_strings_set = settings.get('list_strings', {})
                                    list_strings_settings = list_strings_set.get('use_lists', False)
                                    if not list_strings_settings:
                                        label = BodyLabel(f"{student_id_str} {name}")
                                    else:
                                        label = BodyLabel(f"{student_id_str}")
                            except FileNotFoundError as e:
                                logger.error(f"加载设置时出错: {e}, 使用默认显示仅学号显示")
                                label = BodyLabel(f"{student_id_str}")
                            except KeyError:
                                logger.error(f"设置文件中缺少foundation键, 使用默认仅学号显示")
                                label = BodyLabel(f"{student_id_str}")

                            label.setAlignment(Qt.AlignCenter)
                            # 读取设置中的font_size值
                            try:
                                with open('app/Settings/Settings.json', 'r', encoding='utf-8') as f:
                                    settings = json.load(f)
                                    font_size = settings['multi_player']['font_size']
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
                        # 创建容器并添加到布局
                        container = QWidget()
                        container.setLayout(vbox_layout)
                        self.result_layout.addWidget(container)
                        
                        # 更新抽取记录
                        drawn_students.extend([s[1].replace(' ', '') for s in selected_students])
                        with open(draw_record_file, 'w', encoding='utf-8') as f:
                            json.dump(drawn_students, f, ensure_ascii=False, indent=4)
                        return
                    else:
                        # 删除临时文件
                        if os.path.exists(draw_record_file):
                            os.remove(draw_record_file)

                        InfoBar.success(
                            title='抽选完成',
                            content="所有学生都已被抽选完毕，临时记录已清除\n显示的结果为新一轮抽选的结果,您可继续抽取",
                            orient=Qt.Horizontal,
                            parent=self,
                            isClosable=True,
                            duration=3000
                        )

                        self.until_the_reboot_draw()
                        return

        else:
            # 清除旧布局和标签
            if hasattr(self, 'container'):
                self.container.deleteLater()
                del self.container
            if hasattr(self, 'student_labels'):
                for label in self.student_labels:
                    label.deleteLater()

            # 删除布局中的所有内容
            while self.result_layout.count(): 
                item = self.result_layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()

            error_label = BodyLabel("-- 抽选失败")
            error_label.setAlignment(Qt.AlignCenter)
            # 读取设置中的font_size值
            try:
                with open('app/Settings/Settings.json', 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    font_size = settings['multi_player']['font_size']
                    if font_size < 30:
                        font_size = 85
            except Exception as e:
                font_size = 85
                logger.error(f"加载字体设置时出错: {e}, 使用默认设置")
            # 根据设置调整字体大小
            if font_size < 30:
                error_label.setFont(QFont(load_custom_font(), 85))
            else:
                error_label.setFont(QFont(load_custom_font(), font_size))
            self.result_layout.addWidget(error_label)
        
    def until_all_draw_mode(self):
        """不重复抽取(直到抽完全部人)"""
        class_name = self.class_combo.currentText()
        if class_name and class_name not in ["你暂未添加班级", "加载班级列表失败"]:
            try:
                with open('app/Settings/Settings.json', 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    list_strings_set = settings.get('list_strings', {})
                    list_strings_settings = list_strings_set.get('use_lists', False)
                    if not list_strings_settings:
                        student_file = f"app/resource/students/{class_name}.ini"
                    else:
                        student_file = f"app/resource/students/people_{class_name}.ini"
            except FileNotFoundError as e:
                logger.error(f"加载设置时出错: {e}, 使用默认显示仅学号显示")
                student_file = f"app/resource/students/people_{class_name}.ini"
            except KeyError:
                logger.error(f"设置文件中缺少foundation键, 使用默认仅学号显示")
                student_file = f"app/resource/students/people_{class_name}.ini"

            # 根据抽取作用范围模式确定记录文件名
            with open('app/Settings/Settings.json', 'r', encoding='utf-8') as f:
                settings = json.load(f)
                extraction_scope = settings['global']['extraction_scope']
            
            if extraction_scope == 1:  # 隔离模式
                draw_record_file = f"app/resource/Temp/until_all_scope_{class_name}_multi.json"
            else:  # 共享模式
                draw_record_file = f"app/resource/Temp/until_all_draw_{class_name}.json"
            
            # 创建Temp目录如果不存在
            os.makedirs(os.path.dirname(draw_record_file), exist_ok=True)
            
            # 读取已抽取记录
            drawn_students = []
            if os.path.exists(draw_record_file):
                with open(draw_record_file, 'r', encoding='utf-8') as f:
                    try:
                        drawn_students = json.load(f)
                    except json.JSONDecodeError:
                        drawn_students = []
            
            if os.path.exists(student_file):
                with open(student_file, 'r', encoding='utf-8') as f:
                    students = [(i+1, line.strip().replace(' ', '')) for i, line in enumerate(f) if line.strip() and '【' not in line.strip() and '】' not in line.strip()]
                    
                    # 确保draw_record_file存在
                    if not os.path.exists(draw_record_file):
                        drawn_students = []
                        
                    available_students = [s for s in students if s[1].replace(' ', '') not in [x.replace(' ', '') for x in drawn_students]]
                    
                    if available_students:
                        # 从self.current_count获取抽取人数
                        draw_count = self.current_count
                        
                        # 抽取多个学生
                        selected_students = random.sample(available_students, min(draw_count, len(available_students)))
                        
                        # 清除旧布局和标签
                        if hasattr(self, 'container'):
                            self.container.deleteLater()
                            del self.container
                        if hasattr(self, 'student_labels'):
                            for label in self.student_labels:
                                label.deleteLater()

                        # 删除布局中的所有内容
                        while self.result_layout.count(): 
                            item = self.result_layout.takeAt(0)
                            widget = item.widget()
                            if widget:
                                widget.deleteLater()

                        # 根据设置格式化学号显示
                        try:
                            with open('app/Settings/Settings.json', 'r', encoding='utf-8') as f:
                                settings = json.load(f)

                                multi_player_student_id = settings['multi_player']['student_id']
                                if multi_player_student_id == 0:
                                    global_student_id = settings['global']['student_id']
                        except Exception as e:
                            multi_player_student_id = 1
                            logger.error(f"加载设置时出错: {e}, 使用默认设置")

                        try:
                            with open('app/Settings/Settings.json', 'r', encoding='utf-8') as f:
                                settings = json.load(f)
                                multi_player_student_name = settings['multi_player']['student_name']
                                if multi_player_student_name == 0:
                                    global_student_name = settings['global']['student_name']
                        except Exception as e:
                            multi_player_student_name = 0
                            global_student_name = 0
                            logger.error(f"加载姓名格式设置时出错: {e}, 使用默认设置")

                        # 创建新布局
                        vbox_layout = QVBoxLayout()
                        # 创建新标签列表
                        self.student_labels = []
                        for num, selected in selected_students:
                            # 整合学号格式和姓名处理逻辑
                            student_id_format = multi_player_student_id if multi_player_student_id != 0 else global_student_id
                            student_name_format = multi_player_student_name if multi_player_student_name != 0 else global_student_name
                            
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

                            # 读取设置中的history_enabled
                            try:
                                with open('app/Settings/Settings.json', 'r', encoding='utf-8') as f:
                                    settings = json.load(f)
                                    history_enabled = settings['history']['history_enabled']
                            except Exception as e:
                                history_enabled = False
                                logger.error(f"加载历史记录设置时出错: {e}, 使用默认设置")

                            if history_enabled:
                                # 记录抽选历史
                                try:
                                    with open('app/Settings/Settings.json', 'r', encoding='utf-8') as f:
                                        settings = json.load(f)
                                        list_strings_set = settings.get('list_strings', {})
                                        list_strings_settings = list_strings_set.get('use_lists', False)
                                        if not list_strings_settings:
                                            history_file = f"app/resource/history/{class_name}.json"
                                        else:
                                            history_file = f"app/resource/history/people_{class_name}.json"
                                except FileNotFoundError as e:
                                    logger.error(f"加载设置时出错: {e}, 使用默认显示仅学号记录历史")
                                    history_file = f"app/resource/history/people_{class_name}.json"
                                except KeyError:
                                    logger.error(f"设置文件中缺少foundation键, 使用默认仅学号记录历史")
                                    history_file = f"app/resource/history/people_{class_name}.json"

                                os.makedirs(os.path.dirname(history_file), exist_ok=True)
                                
                                history_data = {}
                                if os.path.exists(history_file):
                                    with open(history_file, 'r', encoding='utf-8') as f:
                                        try:
                                            history_data = json.load(f)
                                        except json.JSONDecodeError:
                                            history_data = {}
                                
                                if "multi" not in history_data:
                                    history_data["multi"] = {}

                                import datetime

                                if selected not in history_data["multi"]:
                                    history_data["multi"][selected] = {
                                        "total_number_of_times": 1,
                                        "time": [
                                            {
                                                "draw_method": {
                                                    self.draw_mode: datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                                }
                                            }
                                        ]
                                    }
                                else:
                                    history_data["multi"][selected]["total_number_of_times"] += 1
                                    history_data["multi"][selected]["time"].append({
                                        "draw_method": {
                                            self.draw_mode: datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                        }
                                    })
                                
                                with open(history_file, 'w', encoding='utf-8') as f:
                                    json.dump(history_data, f, ensure_ascii=False, indent=4)

                            else:
                                logger.info("历史记录功能已被禁用。")

                            try:
                                with open('app/Settings/Settings.json', 'r', encoding='utf-8') as f:
                                    settings = json.load(f)
                                    list_strings_set = settings.get('list_strings', {})
                                    list_strings_settings = list_strings_set.get('use_lists', False)
                                    if not list_strings_settings:
                                        label = BodyLabel(f"{student_id_str} {name}")
                                    else:
                                        label = BodyLabel(f"{student_id_str}")
                            except FileNotFoundError as e:
                                logger.error(f"加载设置时出错: {e}, 使用默认显示仅学号显示")
                                label = BodyLabel(f"{student_id_str}")
                            except KeyError:
                                logger.error(f"设置文件中缺少foundation键, 使用默认仅学号显示")
                                label = BodyLabel(f"{student_id_str}")

                            label.setAlignment(Qt.AlignCenter)
                            # 读取设置中的font_size值
                            try:
                                with open('app/Settings/Settings.json', 'r', encoding='utf-8') as f:
                                    settings = json.load(f)
                                    font_size = settings['multi_player']['font_size']
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

                        # 创建容器并添加到布局
                        container = QWidget()
                        container.setLayout(vbox_layout)
                        self.result_layout.addWidget(container)
                        
                        # 更新抽取记录
                        drawn_students.extend([s[1].replace(' ', '') for s in selected_students])
                        with open(draw_record_file, 'w', encoding='utf-8') as f:
                            json.dump(drawn_students, f, ensure_ascii=False, indent=4)
                        return
                    else:
                        # 删除临时文件
                        if os.path.exists(draw_record_file):
                            os.remove(draw_record_file)

                        InfoBar.success(
                            title='抽选完成',
                            content="所有学生都已被抽选完毕，记录已清除\n显示的结果为新一轮抽选的结果, 您可继续抽取",
                            orient=Qt.Horizontal,
                            parent=self,
                            isClosable=True,
                            duration=3000
                        )
                        
                        # 重新开始新一轮抽选
                        self.until_all_draw_mode()
                        return

        else:
            # 清除旧布局和标签
            if hasattr(self, 'container'):
                self.container.deleteLater()
                del self.container
            if hasattr(self, 'student_labels'):
                for label in self.student_labels:
                    label.deleteLater()

            # 删除布局中的所有内容
            while self.result_layout.count(): 
                item = self.result_layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()

            error_label = BodyLabel("-- 抽选失败")
            error_label.setAlignment(Qt.AlignCenter)
            # 读取设置中的font_size值
            try:
                with open('app/Settings/Settings.json', 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    font_size = settings['multi_player']['font_size']
                    if font_size < 30:
                        font_size = 85
            except Exception as e:
                font_size = 85
                logger.error(f"加载字体设置时出错: {e}, 使用默认设置")
            # 根据设置调整字体大小
            if font_size < 30:
                error_label.setFont(QFont(load_custom_font(), 85))
            else:
                error_label.setFont(QFont(load_custom_font(), font_size))
            self.result_layout.addWidget(error_label)
        
    def update_total_count(self):
        """根据选择的班级更新总人数显示"""
        class_name = self.class_combo.currentText()

        try:
            # 根据抽取作用范围模式确定记录文件名
            with open('app/Settings/Settings.json', 'r', encoding='utf-8') as f:
                settings = json.load(f)
                extraction_scope = settings['global']['extraction_scope']
            if extraction_scope == 1:  # 隔离模式
                draw_record_file = f"app/resource/Temp/until_the_reboot_scope_{class_name}_multi.json"
            else:  # 共享模式
                draw_record_file = f"app/resource/Temp/until_the_reboot_draw_{class_name}.json"
        except Exception as e:
            logger.error(f"加载设置时出错: {e}, 使用默认设置")
            draw_record_file = f"app/resource/Temp/until_the_reboot_draw_{class_name}.json"

        # 删除临时文件
        if os.path.exists(draw_record_file):
            os.remove(draw_record_file)
        
        self.current_count = 1
        self._update_count_display()

        if class_name and class_name not in ["你暂未添加班级", "加载班级列表失败"]:
            try:
                with open('app/Settings/Settings.json', 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    list_strings_set = settings.get('list_strings', {})
                    list_strings_settings = list_strings_set.get('use_lists', False)
                    if not list_strings_settings:
                        student_file = f"app/resource/students/{class_name}.ini"
                    else:
                        student_file = f"app/resource/students/people_{class_name}.ini"
            except FileNotFoundError as e:
                logger.error(f"加载设置时出错: {e}, 使用默认显示仅学号显示")
                student_file = f"app/resource/students/people_{class_name}.ini"
            except KeyError:
                logger.error(f"设置文件中缺少foundation键, 使用默认仅学号显示")
                student_file = f"app/resource/students/people_{class_name}.ini"

            if os.path.exists(student_file):
                with open(student_file, 'r', encoding='utf-8') as f:
                    count = len([line.strip() for line in f if line.strip() and not line.strip().startswith('【') and not line.strip().endswith('】')])
                    self.total_label.setText(f'总人数: {count}')
                    self.max_count = count
                    self._update_count_display()
            else:
                self.total_label.setText('总人数: 0')
                self.max_count = 0
        else:
            self.total_label.setText('总人数: 0')
            self.max_count = 0
            
    def _increase_count(self):
        """增加抽取人数"""
        if self.current_count < self.max_count:
            self.current_count += 1
            self._update_count_display()
            
    def _decrease_count(self):
        """减少抽取人数"""
        if self.current_count > 1:
            self.current_count -= 1
            self._update_count_display()
            
    def _update_count_display(self):
        """更新人数显示"""
        self.count_label.setText(str(self.current_count))
        
        # 根据当前人数启用/禁用按钮
        self.plus_button.setEnabled(self.current_count < self.max_count)
        self.minus_button.setEnabled(self.current_count > 1)
            
    def refresh_class_list(self):
        """刷新班级下拉框选项"""
        self.class_combo.clear()
        try:
            class_file = "app/resource/class/class.ini"
            if os.path.exists(class_file):
                with open(class_file, 'r', encoding='utf-8') as f:
                    classes = [line.strip() for line in f if line.strip()]
                    if classes:
                        self.class_combo.addItems(classes)
                        logger.info("加载班级列表成功！")
                    else:
                        logger.error("你暂未添加班级")
                        self.class_combo.addItem("你暂未添加班级")
            else:
                logger.error("你暂未添加班级")
                self.class_combo.addItem("你暂未添加班级")
        except Exception as e:
            logger.error(f"加载班级列表失败: {str(e)}")

        self.update_total_count()

        InfoBar.success(
            title='班级列表',
            content="班级列表更新，临时记录已被清除\n选取人数已重置为1",
            orient=Qt.Horizontal,
            parent=self,
            isClosable=True,
            duration=3000
        )

    
    def initUI(self):
        # 加载设置
        try:
            with open('app/Settings/Settings.json', 'r', encoding='utf-8') as f:
                settings = json.load(f)
                multi_player_student_quantity = settings['multi_player']['student_quantity']
                multi_player_class_quantity = settings['multi_player']['class_quantity']
                if multi_player_student_quantity == 0:
                    global_student_quantity = f"{settings['global']['student_quantity']}"
                if multi_player_class_quantity == 0:
                    global_class_quantity = f"{settings['global']['class_quantity']}"
        except Exception as e:
            logger.error(f"加载设置时出错: {e}, 使用默认设置")
            global_student_quantity = True
            global_class_quantity = True
            multi_player_student_quantity = 1
            multi_player_class_quantity = 1
            
        # 根据设置控制UI元素显示状态
        if multi_player_student_quantity == 0:
            show_student_quantity = global_student_quantity
            if show_student_quantity == 'True':
                show_student_quantity = True
            else:
                show_student_quantity = False
        elif multi_player_student_quantity == 1:
            show_student_quantity = True
        else:
            show_student_quantity = False
            
        if multi_player_class_quantity == 0:
            show_class_quantity = global_class_quantity
            if show_class_quantity == 'True':
                show_class_quantity = True
            else:
                show_class_quantity = False
        elif multi_player_class_quantity == 1:
            show_class_quantity = True
        else:
            show_class_quantity = False
        
        if multi_player_student_quantity == 1 or multi_player_class_quantity == 1 or global_student_quantity == 'True' or global_class_quantity == 'True':
            show_refresh_button = True
        else:
            show_refresh_button = False
            
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
        control_panel.setContentsMargins(50, 20, 50, 20)

        # 加号按钮
        self.plus_button = PushButton('+')
        self.plus_button.setFixedSize(200, 50)
        self.plus_button.setFont(QFont(load_custom_font(), 30))
        self.plus_button.clicked.connect(self._increase_count)
        control_panel.addWidget(self.plus_button)
        
        # 人数显示
        self.count_label = BodyLabel('1')
        self.count_label.setAlignment(Qt.AlignCenter)
        self.count_label.setFont(QFont(load_custom_font(), 30))
        self.count_label.setFixedWidth(200)
        control_panel.addWidget(self.count_label)

        # 减号按钮
        self.minus_button = PushButton('-')
        self.minus_button.setFixedSize(200, 50)
        self.minus_button.setFont(QFont(load_custom_font(), 30))
        self.minus_button.clicked.connect(self._decrease_count)
        control_panel.addWidget(self.minus_button)

        # 开始按钮
        self.start_button = PrimaryPushButton('开始')
        self.start_button.setFixedSize(200, 50)
        self.start_button.setFont(QFont(load_custom_font(), 20))
        self.start_button.clicked.connect(self.start_draw)
        control_panel.addWidget(self.start_button, 0, Qt.AlignVCenter)
        
        # 刷新按钮
        self.refresh_button = PushButton('刷新班级列表')
        self.refresh_button.setFixedSize(200, 50)
        self.refresh_button.setFont(QFont(load_custom_font(), 15))
        self.refresh_button.clicked.connect(self.refresh_class_list)
        self.refresh_button.setVisible(show_refresh_button)
        control_panel.addWidget(self.refresh_button, 0, Qt.AlignVCenter)
        
        # 班级下拉框
        self.class_combo = ComboBox()
        self.class_combo.setFixedSize(200, 50)
        self.class_combo.setFont(QFont(load_custom_font(), 15))
        self.class_combo.setVisible(show_class_quantity)
        
        # 加载班级列表
        try:
            class_file = "app/resource/class/class.ini"
            if os.path.exists(class_file):
                with open(class_file, 'r', encoding='utf-8') as f:
                    classes = [line.strip() for line in f.read().split('\n') if line.strip()]
                    if classes:
                        self.class_combo.addItems(classes)
                    else:
                        logger.error(f"你暂未添加班级")
                        self.class_combo.addItem("你暂未添加班级")
            else:
                logger.error(f"你暂未添加班级")
                self.class_combo.addItem("你暂未添加班级")
        except Exception as e:
            logger.error(f"加载班级列表失败: {str(e)}")
            self.class_combo.addItem("加载班级列表失败")
        
        control_panel.addWidget(self.class_combo)
        
        # 总人数显示
        self.total_label = BodyLabel('总人数: 0')
        self.total_label.setFont(QFont(load_custom_font(), 14))
        self.total_label.setAlignment(Qt.AlignCenter)
        self.total_label.setFixedWidth(200)
        self.total_label.setVisible(show_student_quantity)
        control_panel.addWidget(self.total_label)
        
        control_panel.addStretch(1)
        
        # 结果区域布局
        self.result_layout = QVBoxLayout()
        
        scroll_area_container.addLayout(self.result_layout)
        
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