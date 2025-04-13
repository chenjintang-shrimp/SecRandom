from qfluentwidgets import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import os
import json
import random
import pyttsx3
from loguru import logger

from ..common.config import load_custom_font

# 配置日志记录
log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

logger.add(
    os.path.join(log_dir, "SecRandom_{time:YYYY-MM-DD}.log"),
    rotation="1 MB",
    encoding="utf-8",
    retention="30 days",
    format="{time:YYYY-MM-DD HH:mm:ss:SSS} | {level} | {name}:{function}:{line} - {message}"
)

class single(QWidget):
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
                single_player_animation_mode = settings['single_player']['animation_mode']
                global_draw_mode = settings['global']['draw_mode']
                if single_player_animation_mode == 0:
                    global_animation_mode = settings['global']['animation_mode']
        except Exception as e:
            # single_player_draw_mode = 1
            single_player_animation_mode = 1
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
        if single_player_animation_mode == 0 and global_animation_mode == 0:  # 手动停止动画
            self.start_button.setText("停止")
            self.is_animating = True
            self.animation_timer = QTimer()
            self.animation_timer.timeout.connect(self._show_random_student)
            self.animation_timer.start(100)
            self.start_button.clicked.disconnect()
            self.start_button.clicked.connect(self._stop_animation)
            
        elif single_player_animation_mode == 0 and global_animation_mode == 1:  # 自动播放完整动画
            self._play_full_animation()
            
        elif single_player_animation_mode == 0 and global_animation_mode == 2:  # 直接显示结果
            self._show_result_directly()
            
        # 跟随单抽动画设置
        elif single_player_animation_mode == 1:  # 手动停止动画
            self.start_button.setText("停止")
            self.is_animating = True
            self.animation_timer = QTimer()
            self.animation_timer.timeout.connect(self._show_random_student)
            self.animation_timer.start(100)
            self.start_button.clicked.disconnect()
            self.start_button.clicked.connect(self._stop_animation)
            
        elif single_player_animation_mode == 2:  # 自动播放完整动画
            self._play_full_animation()
            
        elif single_player_animation_mode == 3:  # 直接显示结果
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
                    if list_strings_settings == False:
                        student_file = f"app/resource/students/{class_name}.ini"
                    else:
                        student_file = f"app/resource/students/people.ini"
            except FileNotFoundError as e:
                logger.error(f"加载设置时出错: {e}, 使用默认显示仅学号显示")
                student_file = f"app/resource/students/people.ini"
            except KeyError:
                logger.error(f"设置文件中缺少'foundation'键, 使用默认仅学号显示")
                student_file = f"app/resource/students/people.ini"

            if os.path.exists(student_file):
                with open(student_file, 'r', encoding='utf-8') as f:
                    students = [(i+1, line.strip().replace(' ', '')) for i, line in enumerate(f) if line.strip() and not line.strip().startswith('【') and not line.strip().endswith('】')]
                    if students:
                        line_num, selected = random.choice(students)
                        
                        # 根据设置格式化学号显示
                        try:
                            with open('app/Settings/Settings.json', 'r', encoding='utf-8') as f:
                                settings = json.load(f)

                                single_player_student_id = settings['single_player']['student_id']
                                if single_player_student_id == 0:
                                    global_student_id = settings['global']['student_id']
                        except Exception as e:
                            single_player_student_id = 1
                            logger.error(f"加载设置时出错: {e}, 使用默认设置")

                        try:
                            with open('app/Settings/Settings.json', 'r', encoding='utf-8') as f:
                                settings = json.load(f)
                                single_player_student_name = settings['single_player']['student_name']
                                if single_player_student_name == 0:
                                    global_student_name = settings['global']['student_name']
                        except Exception as e:
                            single_player_student_name = 0
                            global_student_name = 0
                            logger.error(f"加载姓名格式设置时出错: {e}, 使用默认设置")
                        
                        # 处理两字姓名
                        if single_player_student_name == 0 and global_student_name == 0:
                            if len(selected) == 2:
                                selected = f"{selected[0]}    {selected[1]}"
                        elif single_player_student_name == 1:
                            if len(selected) == 2:
                                selected = f"{selected[0]}    {selected[1]}"

                        try:
                            with open('app/Settings/Settings.json', 'r', encoding='utf-8') as f:
                                settings = json.load(f)
                                list_strings_set = settings.get('list_strings', {})
                                list_strings_settings = list_strings_set.get('use_lists', False)
                                if list_strings_settings == False:
                                    # 根据学号格式执行不同逻辑
                                    if single_player_student_id == 0 and global_student_id == 0:  # 补零
                                        self.main_text.setText(f"{line_num:02}")
                                    elif single_player_student_id == 0 and global_student_id == 1:  # 居中显示
                                        self.main_text.setText(f"{line_num:^5}")

                                    elif single_player_student_id == 1:  # 补零
                                        self.main_text.setText(f"{line_num:02}")
                                    elif single_player_student_id == 2:  # 居中显示
                                        self.main_text.setText(f"{line_num:^5}")
                                    self.sub_text.setText(selected)
                                else:
                                    # 根据学号格式执行不同逻辑
                                    if single_player_student_id == 0 and global_student_id == 0:  # 补零
                                        self.main_text.setText(f"{line_num:02}")
                                    elif single_player_student_id == 0 and global_student_id == 1:  # 居中显示
                                        self.main_text.setText(f"{line_num:^5}")

                                    elif single_player_student_id == 1:  # 补零
                                        self.main_text.setText(f"{line_num:02}")
                                    elif single_player_student_id == 2:  # 居中显示
                                        self.main_text.setText(f"{line_num:^5}")
                        except FileNotFoundError as e:
                            logger.error(f"加载设置时出错: {e}, 使用默认显示仅学号显示")
                            # 根据学号格式执行不同逻辑
                            if single_player_student_id == 0 and global_student_id == 0:  # 补零
                                self.main_text.setText(f"{line_num:02}")
                            elif single_player_student_id == 0 and global_student_id == 1:  # 居中显示
                                self.main_text.setText(f"{line_num:^5}")

                            elif single_player_student_id == 1:  # 补零
                                self.main_text.setText(f"{line_num:02}")
                            elif single_player_student_id == 2:  # 居中显示
                                self.main_text.setText(f"{line_num:^5}")
                        except KeyError:
                            logger.error(f"设置文件中缺少'foundation'键, 使用默认仅学号显示")
                            # 根据学号格式执行不同逻辑
                            if single_player_student_id == 0 and global_student_id == 0:  # 补零
                                self.main_text.setText(f"{line_num:02}")
                            elif single_player_student_id == 0 and global_student_id == 1:  # 居中显示
                                self.main_text.setText(f"{line_num:^5}")

                            elif single_player_student_id == 1:  # 补零
                                self.main_text.setText(f"{line_num:02}")
                            elif single_player_student_id == 2:  # 居中显示
                                self.main_text.setText(f"{line_num:^5}")

                        # 读取设置中的font_size值
                        try:
                            with open('app/Settings/Settings.json', 'r', encoding='utf-8') as f:
                                settings = json.load(f)
                                font_size = settings['single_player']['font_size']
                                if font_size < 30:
                                    font_size = 100
                        except Exception as e:
                            font_size = 100
                            logger.error(f"加载字体设置时出错: {e}, 使用默认设置")
                        # 根据设置调整字体大小
                        if font_size < 30:
                            self.main_text.setFont(QFont(load_custom_font(), 100))
                        else:
                            self.main_text.setFont(QFont(load_custom_font(), font_size))

                        # 读取设置中的font_size值
                        try:
                            with open('app/Settings/Settings.json', 'r', encoding='utf-8') as f:
                                settings = json.load(f)
                                font_size = settings['single_player']['font_size']
                                if font_size < 30:
                                    font_size = 100
                        except Exception as e:
                            font_size = 100
                            logger.error(f"加载字体设置时出错: {e}, 使用默认设置")
                        # 根据设置调整字体大小
                        if font_size < 30:
                            self.sub_text.setFont(QFont(load_custom_font(), 100))
                        else:
                            self.sub_text.setFont(QFont(load_custom_font(), font_size))

                        return
        
        self.main_text.setText("--")
        self.sub_text.setText("抽选失败")
    
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
                voice_enabled = settings['single_player']['voice_enabled']
                if voice_enabled == 0:
                    voice_enabled = settings['global']['voice_enabled']
                
                if voice_enabled == 1 or voice_enabled == True:  # 开启语音
                    selected = self.sub_text.text()
                    if selected != "抽选失败":
                        self.voice_engine.say(f"{selected}")
                        self.voice_engine.iterate()
        except Exception as e:
            logger.error(f"语音播报出错: {e}")
    
    def _play_full_animation(self):
        """播放完整动画（快速显示5个随机学生后显示最终结果）"""
        self.is_animating = True
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self._show_random_student)
        self.animation_timer.start(100)
        self.start_button.setEnabled(False)  # 恢复按钮状态
        
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

        # 结束后进行语音播报
        try:
            with open('app/Settings/Settings.json', 'r', encoding='utf-8') as f:
                settings = json.load(f)
                voice_enabled = settings['single_player']['voice_enabled']
                if voice_enabled == 0:
                    voice_enabled = settings['global']['voice_enabled']
                
                if voice_enabled == 1 or voice_enabled == True:  # 开启语音
                    selected = self.sub_text.text()
                    if selected != "抽选失败":
                        self.voice_engine.say(f"{selected}")
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
                    if list_strings_settings == False:
                        student_file = f"app/resource/students/{class_name}.ini"
                    else:
                        student_file = f"app/resource/students/people.ini"
            except FileNotFoundError as e:
                logger.error(f"加载设置时出错: {e}, 使用默认显示仅学号显示")
                student_file = f"app/resource/students/people.ini"
            except KeyError:
                logger.error(f"设置文件中缺少'foundation'键, 使用默认仅学号显示")
                student_file = f"app/resource/students/people.ini"

            if os.path.exists(student_file):
                with open(student_file, 'r', encoding='utf-8') as f:
                    students = [(i+1, line.strip().replace(' ', '')) for i, line in enumerate(f) if line.strip() and not line.strip().startswith('【') and not line.strip().endswith('】')]
                    if students:
                        import random
                        line_num, selected = random.choice(students)

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
                            history_file = f"app/resource/history/{class_name}.json"
                            os.makedirs(os.path.dirname(history_file), exist_ok=True)
                            
                            history_data = {}
                            if os.path.exists(history_file):
                                with open(history_file, 'r', encoding='utf-8') as f:
                                    try:
                                        history_data = json.load(f)
                                    except json.JSONDecodeError:
                                        logger.error(f"历史记录文件 {history_file} 格式错误，已重置为空。")
                                        history_data = {}

                            if "single" not in history_data:
                                history_data["single"] = {}

                            import datetime

                            if selected not in history_data["single"]:
                                history_data["single"][selected] = {
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
                                history_data["single"][selected]["total_number_of_times"] += 1
                                history_data["single"][selected]["time"].append({
                                    "draw_method": {
                                        self.draw_mode: datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                    }
                                })
                            
                            with open(history_file, 'w', encoding='utf-8') as f:
                                json.dump(history_data, f, ensure_ascii=False, indent=4)

                        else:
                            logger.info("历史记录功能已被禁用。")
                        
                        # 根据设置格式化学号显示
                        try:
                            with open('app/Settings/Settings.json', 'r', encoding='utf-8') as f:
                                settings = json.load(f)

                                single_player_student_id = settings['single_player']['student_id']
                                if single_player_student_id == 0:
                                    global_student_id = settings['global']['student_id']
                        except Exception as e:
                            single_player_student_id = 1
                            logger.error(f"加载设置时出错: {e}, 使用默认设置")

                        try:
                            with open('app/Settings/Settings.json', 'r', encoding='utf-8') as f:
                                settings = json.load(f)
                                single_player_student_name = settings['single_player']['student_name']
                                if single_player_student_name == 0:
                                    global_student_name = settings['global']['student_name']
                        except Exception as e:
                            single_player_student_name = 0
                            global_student_name = 0
                            logger.error(f"加载姓名格式设置时出错: {e}, 使用默认设置")
                        
                        # 处理两字姓名
                        if single_player_student_name == 0 and global_student_name == 0:
                            if len(selected) == 2:
                                selected = f"{selected[0]}    {selected[1]}"
                        elif single_player_student_name == 1:
                            if len(selected) == 2:
                                selected = f"{selected[0]}    {selected[1]}"
                        
                        try:
                            with open('app/Settings/Settings.json', 'r', encoding='utf-8') as f:
                                settings = json.load(f)
                                list_strings_set = settings.get('list_strings', {})
                                list_strings_settings = list_strings_set.get('use_lists', False)
                                if list_strings_settings == False:
                                    # 根据学号格式执行不同逻辑
                                    if single_player_student_id == 0 and global_student_id == 0:  # 补零
                                        self.main_text.setText(f"{line_num:02}")
                                    elif single_player_student_id == 0 and global_student_id == 1:  # 居中显示
                                        self.main_text.setText(f"{line_num:^5}")

                                    elif single_player_student_id == 1:  # 补零
                                        self.main_text.setText(f"{line_num:02}")
                                    elif single_player_student_id == 2:  # 居中显示
                                        self.main_text.setText(f"{line_num:^5}")
                                    self.sub_text.setText(selected)
                                else:
                                    # 根据学号格式执行不同逻辑
                                    if single_player_student_id == 0 and global_student_id == 0:  # 补零
                                        self.main_text.setText(f"{line_num:02}")
                                    elif single_player_student_id == 0 and global_student_id == 1:  # 居中显示
                                        self.main_text.setText(f"{line_num:^5}")

                                    elif single_player_student_id == 1:  # 补零
                                        self.main_text.setText(f"{line_num:02}")
                                    elif single_player_student_id == 2:  # 居中显示
                                        self.main_text.setText(f"{line_num:^5}")
                        except FileNotFoundError as e:
                            logger.error(f"加载设置时出错: {e}, 使用默认显示仅学号显示")
                            # 根据学号格式执行不同逻辑
                            if single_player_student_id == 0 and global_student_id == 0:  # 补零
                                self.main_text.setText(f"{line_num:02}")
                            elif single_player_student_id == 0 and global_student_id == 1:  # 居中显示
                                self.main_text.setText(f"{line_num:^5}")

                            elif single_player_student_id == 1:  # 补零
                                self.main_text.setText(f"{line_num:02}")
                            elif single_player_student_id == 2:  # 居中显示
                                self.main_text.setText(f"{line_num:^5}")
                        except KeyError:
                            logger.error(f"设置文件中缺少'foundation'键, 使用默认仅学号显示")
                            # 根据学号格式执行不同逻辑
                            if single_player_student_id == 0 and global_student_id == 0:  # 补零
                                self.main_text.setText(f"{line_num:02}")
                            elif single_player_student_id == 0 and global_student_id == 1:  # 居中显示
                                self.main_text.setText(f"{line_num:^5}")

                            elif single_player_student_id == 1:  # 补零
                                self.main_text.setText(f"{line_num:02}")
                            elif single_player_student_id == 2:  # 居中显示
                                self.main_text.setText(f"{line_num:^5}")

                        # 读取设置中的font_size值
                        try:
                            with open('app/Settings/Settings.json', 'r', encoding='utf-8') as f:
                                settings = json.load(f)
                                font_size = settings['single_player']['font_size']
                                if font_size < 30:
                                    font_size = 100
                        except Exception as e:
                            font_size = 100
                            logger.error(f"加载字体设置时出错: {e}, 使用默认设置")
                        # 根据设置调整字体大小
                        if font_size < 30:
                            self.main_text.setFont(QFont(load_custom_font(), 100))
                        else:
                            self.main_text.setFont(QFont(load_custom_font(), font_size))

                        # 读取设置中的font_size值
                        try:
                            with open('app/Settings/Settings.json', 'r', encoding='utf-8') as f:
                                settings = json.load(f)
                                font_size = settings['single_player']['font_size']
                                if font_size < 30:
                                    font_size = 100
                        except Exception as e:
                            font_size = 100
                            logger.error(f"加载字体设置时出错: {e}, 使用默认设置")
                        # 根据设置调整字体大小
                        if font_size < 30:
                            self.sub_text.setFont(QFont(load_custom_font(), 100))
                        else:
                            self.sub_text.setFont(QFont(load_custom_font(), font_size))

                        return
        
        self.main_text.setText("--")
        self.sub_text.setText("抽选失败")
        
    def until_the_reboot_draw(self):
        """不重复抽取(直到软件重启)"""
        class_name = self.class_combo.currentText()
        if class_name and class_name not in ["你暂未添加班级", "加载班级列表失败"]:
            try:
                with open('app/Settings/Settings.json', 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    list_strings_set = settings.get('list_strings', {})
                    list_strings_settings = list_strings_set.get('use_lists', False)
                    if list_strings_settings == False:
                        student_file = f"app/resource/students/{class_name}.ini"
                    else:
                        student_file = f"app/resource/students/people.ini"
            except FileNotFoundError as e:
                logger.error(f"加载设置时出错: {e}, 使用默认显示仅学号显示")
                student_file = f"app/resource/students/people.ini"
            except KeyError:
                logger.error(f"设置文件中缺少'foundation'键, 使用默认仅学号显示")
                student_file = f"app/resource/students/people.ini"

            # 根据抽取作用范围模式确定记录文件名
            with open('app/Settings/Settings.json', 'r', encoding='utf-8') as f:
                settings = json.load(f)
                extraction_scope = settings['global']['extraction_scope']
            
            if extraction_scope == 1:  # 隔离模式
                draw_record_file = f"app/resource/Temp/until_the_reboot_scope_{class_name}_single.json"
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
                    students = [(i+1, line.strip().replace(' ', '')) for i, line in enumerate(f) if line.strip() and not line.strip().startswith('【') and not line.strip().endswith('】')]     
                    available_students = [s for s in students if s[1].replace(' ', '') not in [x.replace(' ', '') for x in drawn_students]]
                    
                    if available_students:
                        import random
                        line_num, selected = random.choice(available_students)

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
                            history_file = f"app/resource/history/{class_name}.json"
                            os.makedirs(os.path.dirname(history_file), exist_ok=True)
                            
                            history_data = {}
                            if os.path.exists(history_file):
                                with open(history_file, 'r', encoding='utf-8') as f:
                                    try:
                                        history_data = json.load(f)
                                    except json.JSONDecodeError:
                                        history_data = {}
                            
                            if "single" not in history_data:
                                history_data["single"] = {}

                            import datetime

                            if selected not in history_data["single"]:
                                history_data["single"][selected] = {
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
                                history_data["single"][selected]["total_number_of_times"] += 1
                                history_data["single"][selected]["time"].append({
                                    "draw_method": {
                                        self.draw_mode: datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                    }
                                })
                            
                            with open(history_file, 'w', encoding='utf-8') as f:
                                json.dump(history_data, f, ensure_ascii=False, indent=4)

                        else:
                            logger.info("历史记录功能已被禁用。")

                        # 根据设置格式化学号显示
                        try:
                            with open('app/Settings/Settings.json', 'r', encoding='utf-8') as f:
                                settings = json.load(f)

                                single_player_student_id = settings['single_player']['student_id']
                                if single_player_student_id == 0:
                                    global_student_id = settings['global']['student_id']
                        except Exception as e:
                            single_player_student_id = 1
                            logger.error(f"加载设置时出错: {e}, 使用默认设置")

                        try:
                            with open('app/Settings/Settings.json', 'r', encoding='utf-8') as f:
                                settings = json.load(f)
                                single_player_student_name = settings['single_player']['student_name']
                                if single_player_student_name == 0:
                                    global_student_name = settings['global']['student_name']
                        except Exception as e:
                            single_player_student_name = 0
                            global_student_name = 0
                            logger.error(f"加载姓名格式设置时出错: {e}, 使用默认设置")
                        
                        # 处理两字姓名
                        if single_player_student_name == 0 and global_student_name == 0:
                            if len(selected) == 2:
                                selected = f"{selected[0]}    {selected[1]}"
                        elif single_player_student_name == 1:
                            if len(selected) == 2:
                                selected = f"{selected[0]}    {selected[1]}"
                        
                        try:
                            with open('app/Settings/Settings.json', 'r', encoding='utf-8') as f:
                                settings = json.load(f)
                                list_strings_set = settings.get('list_strings', {})
                                list_strings_settings = list_strings_set.get('use_lists', False)
                                if list_strings_settings == False:
                                    # 根据学号格式执行不同逻辑
                                    if single_player_student_id == 0 and global_student_id == 0:  # 补零
                                        self.main_text.setText(f"{line_num:02}")
                                    elif single_player_student_id == 0 and global_student_id == 1:  # 居中显示
                                        self.main_text.setText(f"{line_num:^5}")

                                    elif single_player_student_id == 1:  # 补零
                                        self.main_text.setText(f"{line_num:02}")
                                    elif single_player_student_id == 2:  # 居中显示
                                        self.main_text.setText(f"{line_num:^5}")
                                    self.sub_text.setText(selected)
                                else:
                                    # 根据学号格式执行不同逻辑
                                    if single_player_student_id == 0 and global_student_id == 0:  # 补零
                                        self.main_text.setText(f"{line_num:02}")
                                    elif single_player_student_id == 0 and global_student_id == 1:  # 居中显示
                                        self.main_text.setText(f"{line_num:^5}")

                                    elif single_player_student_id == 1:  # 补零
                                        self.main_text.setText(f"{line_num:02}")
                                    elif single_player_student_id == 2:  # 居中显示
                                        self.main_text.setText(f"{line_num:^5}")
                        except FileNotFoundError as e:
                            logger.error(f"加载设置时出错: {e}, 使用默认显示仅学号显示")
                            # 根据学号格式执行不同逻辑
                            if single_player_student_id == 0 and global_student_id == 0:  # 补零
                                self.main_text.setText(f"{line_num:02}")
                            elif single_player_student_id == 0 and global_student_id == 1:  # 居中显示
                                self.main_text.setText(f"{line_num:^5}")

                            elif single_player_student_id == 1:  # 补零
                                self.main_text.setText(f"{line_num:02}")
                            elif single_player_student_id == 2:  # 居中显示
                                self.main_text.setText(f"{line_num:^5}")
                        except KeyError:
                            logger.error(f"设置文件中缺少'foundation'键, 使用默认仅学号显示")
                            # 根据学号格式执行不同逻辑
                            if single_player_student_id == 0 and global_student_id == 0:  # 补零
                                self.main_text.setText(f"{line_num:02}")
                            elif single_player_student_id == 0 and global_student_id == 1:  # 居中显示
                                self.main_text.setText(f"{line_num:^5}")

                            elif single_player_student_id == 1:  # 补零
                                self.main_text.setText(f"{line_num:02}")
                            elif single_player_student_id == 2:  # 居中显示
                                self.main_text.setText(f"{line_num:^5}")

                        # 读取设置中的font_size值
                        try:
                            with open('app/Settings/Settings.json', 'r', encoding='utf-8') as f:
                                settings = json.load(f)
                                font_size = settings['single_player']['font_size']
                                if font_size < 30:
                                    font_size = 100
                        except Exception as e:
                            font_size = 100
                            logger.error(f"加载字体设置时出错: {e}, 使用默认设置")
                        # 根据设置调整字体大小
                        if font_size < 30:
                            self.main_text.setFont(QFont(load_custom_font(), 100))
                        else:
                            self.main_text.setFont(QFont(load_custom_font(), font_size))

                        # 读取设置中的font_size值
                        try:
                            with open('app/Settings/Settings.json', 'r', encoding='utf-8') as f:
                                settings = json.load(f)
                                font_size = settings['single_player']['font_size']
                                if font_size < 30:
                                    font_size = 100
                        except Exception as e:
                            font_size = 100
                            logger.error(f"加载字体设置时出错: {e}, 使用默认设置")
                        # 根据设置调整字体大小
                        if font_size < 30:
                            self.sub_text.setFont(QFont(load_custom_font(), 100))
                        else:
                            self.sub_text.setFont(QFont(load_custom_font(), font_size))

                        # 更新抽取记录
                        drawn_students.append(selected.replace(' ', ''))
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
        
        self.main_text.setText("--")
        self.sub_text.setText("抽选失败")
        
    def until_all_draw_mode(self):
        """不重复抽取(直到抽完全部人)"""
        class_name = self.class_combo.currentText()
        if class_name and class_name not in ["你暂未添加班级", "加载班级列表失败"]:
            try:
                with open('app/Settings/Settings.json', 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    list_strings_set = settings.get('list_strings', {})
                    list_strings_settings = list_strings_set.get('use_lists', False)
                    if list_strings_settings == False:
                        student_file = f"app/resource/students/{class_name}.ini"
                    else:
                        student_file = f"app/resource/students/people.ini"
            except FileNotFoundError as e:
                logger.error(f"加载设置时出错: {e}, 使用默认显示仅学号显示")
                student_file = f"app/resource/students/people.ini"
            except KeyError:
                logger.error(f"设置文件中缺少'foundation'键, 使用默认仅学号显示")
                student_file = f"app/resource/students/people.ini"

            # 根据抽取作用范围模式确定记录文件名
            with open('app/Settings/Settings.json', 'r', encoding='utf-8') as f:
                settings = json.load(f)
                extraction_scope = settings['global']['extraction_scope']
            
            if extraction_scope == 1:  # 隔离模式
                draw_record_file = f"app/resource/Temp/until_all_scope_{class_name}_single.json"
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
                    students = [(i+1, line.strip().replace(' ', '')) for i, line in enumerate(f) if line.strip() and not line.strip().startswith('【') and not line.strip().endswith('】')]
                    
                    # 确保draw_record_file存在
                    if not os.path.exists(draw_record_file):
                        drawn_students = []
                        
                    available_students = [s for s in students if s[1].replace(' ', '') not in [x.replace(' ', '') for x in drawn_students]]
                    
                    if available_students:
                        import random
                        line_num, selected = random.choice(available_students)
                        
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
                            history_file = f"app/resource/history/{class_name}.json"
                            os.makedirs(os.path.dirname(history_file), exist_ok=True)
                            
                            history_data = {}
                            if os.path.exists(history_file):
                                with open(history_file, 'r', encoding='utf-8') as f:
                                    try:
                                        history_data = json.load(f)
                                    except json.JSONDecodeError:
                                        history_data = {}
                            
                            if "single" not in history_data:
                                history_data["single"] = {}

                            import datetime

                            if selected not in history_data["single"]:
                                history_data["single"][selected] = {
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
                                history_data["single"][selected]["total_number_of_times"] += 1
                                history_data["single"][selected]["time"].append({
                                    "draw_method": {
                                        self.draw_mode: datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                    }
                                })
                            
                            with open(history_file, 'w', encoding='utf-8') as f:
                                json.dump(history_data, f, ensure_ascii=False, indent=4)

                        else:
                            logger.info("历史记录功能已被禁用。")

                        # 根据设置格式化学号显示
                        try:
                            with open('app/Settings/Settings.json', 'r', encoding='utf-8') as f:
                                settings = json.load(f)

                                single_player_student_id = settings['single_player']['student_id']
                                if single_player_student_id == 0:
                                    global_student_id = settings['global']['student_id']
                        except Exception as e:
                            single_player_student_id = 1
                            logger.error(f"加载设置时出错: {e}, 使用默认设置")
                            
                        try:
                            with open('app/Settings/Settings.json', 'r', encoding='utf-8') as f:
                                settings = json.load(f)
                                single_player_student_name = settings['single_player']['student_name']
                                if single_player_student_name == 0:
                                    global_student_name = settings['global']['student_name']
                        except Exception as e:
                            single_player_student_name = 0
                            global_student_name = 0
                            logger.error(f"加载姓名格式设置时出错: {e}, 使用默认设置")
                        
                        # 处理两字姓名
                        if single_player_student_name == 0 and global_student_name == 0:
                            if len(selected) == 2:
                                selected = f"{selected[0]}    {selected[1]}"
                        elif single_player_student_name == 1:
                            if len(selected) == 2:
                                selected = f"{selected[0]}    {selected[1]}"
                        
                        try:
                            with open('app/Settings/Settings.json', 'r', encoding='utf-8') as f:
                                settings = json.load(f)
                                list_strings_set = settings.get('list_strings', {})
                                list_strings_settings = list_strings_set.get('use_lists', False)
                                if list_strings_settings == False:
                                    # 根据学号格式执行不同逻辑
                                    if single_player_student_id == 0 and global_student_id == 0:  # 补零
                                        self.main_text.setText(f"{line_num:02}")
                                    elif single_player_student_id == 0 and global_student_id == 1:  # 居中显示
                                        self.main_text.setText(f"{line_num:^5}")

                                    elif single_player_student_id == 1:  # 补零
                                        self.main_text.setText(f"{line_num:02}")
                                    elif single_player_student_id == 2:  # 居中显示
                                        self.main_text.setText(f"{line_num:^5}")
                                    self.sub_text.setText(selected)
                                else:
                                    # 根据学号格式执行不同逻辑
                                    if single_player_student_id == 0 and global_student_id == 0:  # 补零
                                        self.main_text.setText(f"{line_num:02}")
                                    elif single_player_student_id == 0 and global_student_id == 1:  # 居中显示
                                        self.main_text.setText(f"{line_num:^5}")

                                    elif single_player_student_id == 1:  # 补零
                                        self.main_text.setText(f"{line_num:02}")
                                    elif single_player_student_id == 2:  # 居中显示
                                        self.main_text.setText(f"{line_num:^5}")
                        except FileNotFoundError as e:
                            logger.error(f"加载设置时出错: {e}, 使用默认显示仅学号显示")
                            # 根据学号格式执行不同逻辑
                            if single_player_student_id == 0 and global_student_id == 0:  # 补零
                                self.main_text.setText(f"{line_num:02}")
                            elif single_player_student_id == 0 and global_student_id == 1:  # 居中显示
                                self.main_text.setText(f"{line_num:^5}")

                            elif single_player_student_id == 1:  # 补零
                                self.main_text.setText(f"{line_num:02}")
                            elif single_player_student_id == 2:  # 居中显示
                                self.main_text.setText(f"{line_num:^5}")
                        except KeyError:
                            logger.error(f"设置文件中缺少'foundation'键, 使用默认仅学号显示")
                            # 根据学号格式执行不同逻辑
                            if single_player_student_id == 0 and global_student_id == 0:  # 补零
                                self.main_text.setText(f"{line_num:02}")
                            elif single_player_student_id == 0 and global_student_id == 1:  # 居中显示
                                self.main_text.setText(f"{line_num:^5}")

                            elif single_player_student_id == 1:  # 补零
                                self.main_text.setText(f"{line_num:02}")
                            elif single_player_student_id == 2:  # 居中显示
                                self.main_text.setText(f"{line_num:^5}")

                        # 读取设置中的font_size值
                        try:
                            with open('app/Settings/Settings.json', 'r', encoding='utf-8') as f:
                                settings = json.load(f)
                                font_size = settings['single_player']['font_size']
                                if font_size < 30:
                                    font_size = 100
                        except Exception as e:
                            font_size = 100
                            logger.error(f"加载字体设置时出错: {e}, 使用默认设置")
                        # 根据设置调整字体大小
                        if font_size < 30:
                            self.main_text.setFont(QFont(load_custom_font(), 100))
                        else:
                            self.main_text.setFont(QFont(load_custom_font(), font_size))

                        # 读取设置中的font_size值
                        try:
                            with open('app/Settings/Settings.json', 'r', encoding='utf-8') as f:
                                settings = json.load(f)
                                font_size = settings['single_player']['font_size']
                                if font_size < 30:
                                    font_size = 100
                        except Exception as e:
                            font_size = 100
                            logger.error(f"加载字体设置时出错: {e}, 使用默认设置")
                        # 根据设置调整字体大小
                        if font_size < 30:
                            self.sub_text.setFont(QFont(load_custom_font(), 100))
                        else:
                            self.sub_text.setFont(QFont(load_custom_font(), font_size))
                        
                        # 更新抽取记录
                        drawn_students.append(selected.replace(' ', ''))
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
                        
                        # 重新开始新一轮抽选
                        self.until_all_draw_mode()
                        return
        
        self.main_text.setText("--")
        self.sub_text.setText("抽选失败")
        
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

        InfoBar.success(
            title='班级列表',
            content="班级列表更新，临时记录已被清除",
            orient=Qt.Horizontal,
            parent=self,
            isClosable=True,
            duration=3000
        )

        if class_name and class_name not in ["你暂未添加班级", "加载班级列表失败"]:
            try:
                with open('app/Settings/Settings.json', 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    list_strings_set = settings.get('list_strings', {})
                    list_strings_settings = list_strings_set.get('use_lists', False)
                    if list_strings_settings == False:
                        student_file = f"app/resource/students/{class_name}.ini"
                    else:
                        student_file = f"app/resource/students/people.ini"
            except FileNotFoundError as e:
                logger.error(f"加载设置时出错: {e}, 使用默认显示仅学号显示")
                student_file = f"app/resource/students/people.ini"
            except KeyError:
                logger.error(f"设置文件中缺少'foundation'键, 使用默认仅学号显示")
                student_file = f"app/resource/students/people.ini"

            if os.path.exists(student_file):
                with open(student_file, 'r', encoding='utf-8') as f:
                    count = len([line.strip() for line in f if line.strip() and not line.strip().startswith('【') and not line.strip().endswith('】')])
                    self.total_label.setText(f'总人数: {count}')
            else:
                self.total_label.setText('总人数: 0')
        else:
            self.total_label.setText('总人数: 0')
            
    def refresh_class_list(self):
        """刷新班级下拉框选项"""
        self.class_combo.clear()
        try:
            class_file = "app/resource/class/class.ini"
            if os.path.exists(class_file):
                with open(class_file, 'r', encoding='utf-8') as f:
                    classes = [line.strip() for line in f.read().split('\n') if line.strip()]
                    if classes:
                        self.class_combo.addItems(classes)
                        logger.info("加载班级列表成功！")
                    else:
                        logger.error(f"你暂未添加班级")
                        self.class_combo.addItem("你暂未添加班级")
            else:
                logger.error(f"你暂未添加班级")
                self.class_combo.addItem("你暂未添加班级")
        except Exception as e:
            logger.error(f"加载班级列表失败: {str(e)}")
        self.update_total_count()
        
    def initUI(self):
        # 加载设置
        try:
            with open('app/Settings/Settings.json', 'r', encoding='utf-8') as f:
                settings = json.load(f)
                single_player_student_quantity = settings['single_player']['student_quantity']
                single_player_class_quantity = settings['single_player']['class_quantity']
                if single_player_student_quantity == 0:
                    global_student_quantity = f"{settings['global']['student_quantity']}"
                if single_player_class_quantity == 0:
                    global_class_quantity = f"{settings['global']['class_quantity']}"
        except Exception as e:
            logger.error(f"加载设置时出错: {e}, 使用默认设置")
            global_student_quantity = True
            global_class_quantity = True
            single_player_student_quantity = 1
            single_player_class_quantity = 1
            
        # 根据设置控制UI元素显示状态
        if single_player_student_quantity == 0:
            show_student_quantity = global_student_quantity
            if show_student_quantity == 'True':
                show_student_quantity = True
            else:
                show_student_quantity = False
        elif single_player_student_quantity == 1:
            show_student_quantity = True
        else:
            show_student_quantity = False
            
        if single_player_class_quantity == 0:
            show_class_quantity = global_class_quantity
            if show_class_quantity == 'True':
                show_class_quantity = True
            else:
                show_class_quantity = False
        elif single_player_class_quantity == 1:
            show_class_quantity = True
        else:
            show_class_quantity = False
        
        if single_player_student_quantity == 1 or single_player_class_quantity == 1 or global_student_quantity == 'True' or global_class_quantity == 'True':
            show_refresh_button = True
        else:
            show_refresh_button = False
            
        # 主布局
        main_layout = QVBoxLayout()
        
        # 按钮布局
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(50, 0, 0, 0)  # 左边距20像素
        
        # 开始按钮
        self.start_button = PrimaryPushButton('开始')
        self.start_button.setFixedSize(150, 50)
        self.start_button.setFont(QFont(load_custom_font(), 20))
        self.start_button.clicked.connect(self.start_draw)
        button_layout.addWidget(self.start_button, 0, Qt.AlignVCenter | Qt.AlignLeft)
        
        # 上部布局（按钮和文本）
        top_layout = QHBoxLayout()
        top_layout.addLayout(button_layout)
        
        # 文本区域
        text_layout = QVBoxLayout()
        text_layout.setAlignment(Qt.AlignCenter | Qt.AlignCenter)

        self.main_text = BodyLabel('--')
        self.main_text.setAlignment(Qt.AlignCenter | Qt.AlignCenter)
        # 读取设置中的font_size值
        try:
            with open('app/Settings/Settings.json', 'r', encoding='utf-8') as f:
                settings = json.load(f)
                font_size = settings['single_player']['font_size']
                if font_size < 30:
                    font_size = 100
        except Exception as e:
            font_size = 100
            logger.error(f"加载字体设置时出错: {e}, 使用默认设置")
        # 根据设置调整字体大小
        if font_size < 30:
            self.main_text.setFont(QFont(load_custom_font(), 100))
        else:
            self.main_text.setFont(QFont(load_custom_font(), font_size))
        
        self.sub_text = BodyLabel('别紧张')
        self.sub_text.setAlignment(Qt.AlignCenter | Qt.AlignCenter)
        # 读取设置中的font_size值
        try:
            with open('app/Settings/Settings.json', 'r', encoding='utf-8') as f:
                settings = json.load(f)
                font_size = settings['single_player']['font_size']
                if font_size < 30:
                    font_size = 100
        except Exception as e:
            font_size = 100
            logger.error(f"加载字体设置时出错: {e}, 使用默认设置")
        # 根据设置调整字体大小
        if font_size < 30:
            self.sub_text.setFont(QFont(load_custom_font(), 100))
        else:
            self.sub_text.setFont(QFont(load_custom_font(), font_size))
        
        text_layout.addWidget(self.main_text)
        text_layout.addWidget(self.sub_text)
        
        main_layout.addStretch(1)
        main_layout.addLayout(text_layout)
        main_layout.addStretch(1)
        main_layout.addLayout(top_layout)
        
        # 底部信息栏
        bottom_layout = QHBoxLayout()
        bottom_layout.setContentsMargins(50, 0, 0, 20)  # 左边距50像素，底部边距20像素

        # 刷新按钮
        self.refresh_button = PushButton('刷新班级列表')
        self.refresh_button.setFixedSize(150, 50)
        self.refresh_button.setFont(QFont(load_custom_font(), 15))
        self.refresh_button.clicked.connect(self.refresh_class_list)
        self.refresh_button.setVisible(show_refresh_button)

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
        
        # 总人数显示
        self.total_label = BodyLabel('总人数: 0')
        self.total_label.setFont(QFont(load_custom_font(), 14))
        self.total_label.setFixedWidth(200)
        self.total_label.setVisible(show_student_quantity)

        bottom_layout.addWidget(self.refresh_button)
        bottom_layout.addWidget(self.class_combo)
        bottom_layout.addWidget(self.total_label)
        bottom_layout.addStretch(6)  # 添加弹性空间
        
        # 班级选择变化时更新总人数
        self.class_combo.currentTextChanged.connect(self.update_total_count)
        
        # 初始化总人数显示
        self.update_total_count()

        main_layout.addLayout(bottom_layout)

        
        # 设置主布局
        self.setLayout(main_layout)