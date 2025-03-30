from qfluentwidgets import *
from qfluentwidgets import FluentIcon as FIF
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget, QLabel, QPushButton, QComboBox, QLineEdit, QFileDialog, QMessageBox
import json
import os
from loguru import logger

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


class group_player_SettinsCard(GroupHeaderCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("抽小组设置")
        self.setBorderRadius(8)
        self.settings_file = os.path.join(os.path.dirname(__file__), "..", "Settings", "Settings.json")
        self.default_settings = {
            "draw_mode": 0,
            "animation_mode": 0,
            "voice_enabled": 0,
            "student_id": 0,
            "student_name": 0,
            "student_quantity_enabled": 0,
            "class_quantity_enabled": 0
        }

        self.group_player_Draw_comboBox = ComboBox()
        self.group_player_Animation_comboBox = ComboBox()
        self.group_player_Voice_comboBox = ComboBox()
        self.group_player_student_id_comboBox = ComboBox()
        self.group_player_student_name_comboBox = ComboBox()
        self.group_player_student_quantity_comboBox = ComboBox()
        self.group_player_class_quantity_comboBox = ComboBox()
        
        # 抽取模式下拉框
        self.group_player_Draw_comboBox.setFixedWidth(320) # 设置下拉框宽度为320像素
        self.group_player_Draw_comboBox.addItems(["跟随全局设置", "重复抽取", "不重复抽取(直到软件重启)", "不重复抽取(直到抽完全部人)"])
        self.group_player_Draw_comboBox.currentIndexChanged.connect(self.save_settings)

        # 语音播放按钮
        self.group_player_Voice_comboBox.setFixedWidth(320) # 设置下拉框宽度为320像素
        self.group_player_Voice_comboBox.addItems(["跟随全局设置", "开启", "关闭"])
        self.group_player_Voice_comboBox.currentIndexChanged.connect(self.save_settings)

        # 动画模式下拉框
        self.group_player_Animation_comboBox.setFixedWidth(320) # 设置下拉框宽度为320像素
        self.group_player_Animation_comboBox.addItems(["跟随全局设置", "手动停止动画", "自动播放完整动画", "直接显示结果"])
        self.group_player_Animation_comboBox.currentIndexChanged.connect(self.save_settings)

        # 学号格式下拉框
        self.group_player_student_id_comboBox.setFixedWidth(320) # 设置下拉框宽度为320像素
        self.group_player_student_id_comboBox.addItems(["跟随全局设置", "⌈01⌋", "⌈ 1 ⌋", "⌈  1⌋"])
        self.group_player_student_id_comboBox.currentIndexChanged.connect(self.save_settings)

        # 姓名格式下拉框
        self.group_player_student_name_comboBox.setFixedWidth(320) # 设置下拉框宽度为320像素
        self.group_player_student_name_comboBox.addItems(["跟随全局设置", "⌈张  三⌋", "⌈张三  ⌋", "⌈  张三⌋"])
        self.group_player_student_name_comboBox.currentIndexChanged.connect(self.save_settings)

        # 班级总人数下拉框
        self.group_player_student_quantity_comboBox.setFixedWidth(320) # 设置下拉框宽度为320像素
        self.group_player_student_quantity_comboBox.addItems(["跟随全局设置", "显示", "不显示"])
        self.group_player_student_quantity_comboBox.currentIndexChanged.connect(self.save_settings)

        # 便捷修改班级功能显示下拉框
        self.group_player_class_quantity_comboBox.setFixedWidth(320) # 设置下拉框宽度为320像素
        self.group_player_class_quantity_comboBox.addItems(["跟随全局设置", "显示", "不显示"])
        self.group_player_class_quantity_comboBox.currentIndexChanged.connect(self.save_settings)

        # 添加组件到分组中
        self.addGroup(FIF.SYNC, "抽取模式", "设置抽取模式", self.group_player_Draw_comboBox)
        self.addGroup(FIF.FEEDBACK, "语音播放", "设置结果公布时是否播放语音", self.group_player_Voice_comboBox)
        self.addGroup(FIF.VIDEO, "动画模式", "设置抽取时的动画播放方式", self.group_player_Animation_comboBox)
        self.addGroup(FIF.EDIT, "学号格式", "设置学号格式设置", self.group_player_student_id_comboBox)
        self.addGroup(FIF.EDIT, "姓名格式", "设置姓名格式设置", self.group_player_student_name_comboBox)
        self.addGroup(FIF.PEOPLE, "班级总人数", "设置班级总人数是否显示", self.group_player_student_quantity_comboBox)
        self.addGroup(FIF.EDUCATION, "便捷修改班级", "设置便捷修改班级功能是否显示", self.group_player_class_quantity_comboBox)

        self.load_settings()  # 加载设置
        self.save_settings()  # 保存设置
        
    def load_settings(self):
        try:
            if os.path.exists(self.settings_file):
                logger.info(f"加载设置文件: {self.settings_file}")  # 打印日志信息
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    group_player_settings = settings.get("group_player", {})
                    
                    # 优先使用保存的文字选项
                    draw_mode_text = group_player_settings.get("draw_mode_text", self.group_player_Draw_comboBox.itemText(self.default_settings["draw_mode"]))
                    draw_mode = self.group_player_Draw_comboBox.findText(draw_mode_text)
                    if draw_mode == -1:
                        # 如果文字选项无效，则使用索引值
                        logger.warning(f"无效的抽取模式文本: {draw_mode_text}")
                        draw_mode = group_player_settings.get("draw_mode", self.default_settings["draw_mode"])
                        if draw_mode < 0 or draw_mode >= self.group_player_Draw_comboBox.count():
                            # 如果索引值无效，则使用默认值  
                            logger.warning(f"无效的抽取模式索引: {draw_mode}")
                            draw_mode = self.default_settings["draw_mode"]
                        
                    animation_mode_text = group_player_settings.get("animation_mode_text", self.group_player_Animation_comboBox.itemText(self.default_settings["animation_mode"]))
                    animation_mode = self.group_player_Animation_comboBox.findText(animation_mode_text)
                    if animation_mode == -1:
                        # 如果文字选项无效，则使用索引值
                        logger.warning(f"无效的动画模式文本: {animation_mode_text}")
                        animation_mode = group_player_settings.get("animation_mode", self.default_settings["animation_mode"])
                        if animation_mode < 0 or animation_mode >= self.group_player_Animation_comboBox.count():
                            # 如果索引值无效，则使用默认值
                            logger.warning(f"无效的动画模式索引: {animation_mode}")
                            animation_mode = self.default_settings["animation_mode"]
                        
                    voice_enabled_text = group_player_settings.get("voice_enabled_text", self.group_player_Animation_comboBox.itemText(self.default_settings["voice_enabled"]))
                    voice_enabled = self.group_player_Animation_comboBox.findText(voice_enabled_text)
                    if voice_enabled == -1:
                        # 如果文字选项无效，则使用索引值
                        logger.warning(f"无效的语音播放设置文本: {voice_enabled_text}")
                        voice_enabled = group_player_settings.get("voice_enabled", self.default_settings["voice_enabled"])
                        if voice_enabled < 0 or voice_enabled >= self.group_player_Animation_comboBox.count():
                            # 如果索引值无效，则使用默认值
                            logger.warning(f"无效的语音播放设置索引: {voice_enabled}")
                            voice_enabled = self.default_settings["voice_enabled"]

                    student_id_text = group_player_settings.get("student_id_text", self.group_player_student_id_comboBox.itemText(self.default_settings["student_id"]))
                    student_id = self.group_player_student_id_comboBox.findText(student_id_text)
                    if student_id == -1:
                        # 如果文字选项无效，则使用索引值
                        logger.warning(f"无效的学号格式文本: {student_id_text}")
                        student_id = group_player_settings.get("student_id", self.default_settings["student_id"])
                        if student_id < 0 or student_id >= self.group_player_student_id_comboBox.count():
                            # 如果索引值无效，则使用默认值
                            logger.warning(f"无效的学号格式索引: {student_id}")
                            student_id = self.default_settings["student_id"]
                    
                    student_name_text = group_player_settings.get("student_name_text", self.group_player_student_name_comboBox.itemText(self.default_settings["student_name"]))
                    student_name = self.group_player_student_name_comboBox.findText(student_name_text)
                    if student_name == -1:
                        # 如果文字选项无效，则使用索引值
                        logger.warning(f"无效的姓名格式文本: {student_name_text}")
                        student_name = group_player_settings.get("student_name", self.default_settings["student_name"])
                        if student_name < 0 or student_name >= self.group_player_student_name_comboBox.count():
                            # 如果索引值无效，则使用默认值
                            logger.warning(f"无效的姓名格式索引: {student_name}")
                            student_name = self.default_settings["student_name"]

                    student_quantity_text = group_player_settings.get("student_quantity_text", self.group_player_student_quantity_comboBox.itemText(self.default_settings["student_quantity_enabled"]))
                    student_quantity = self.group_player_student_quantity_comboBox.findText(student_quantity_text)
                    if student_quantity == -1:
                        # 如果文字选项无效，则使用索引值
                        logger.warning(f"无效的班级总人数文本: {student_quantity_text}")
                        student_quantity = group_player_settings.get("student_quantity", self.default_settings["student_quantity_enabled"])
                        if student_quantity < 0 or student_quantity >= self.group_player_student_quantity_comboBox.count():
                            # 如果索引值无效，则使用默认值
                            logger.warning(f"无效的班级总人数索引: {student_quantity}")
                            student_quantity = self.default_settings["student_quantity_enabled"]

                    class_quantity_text = group_player_settings.get("class_quantity_text", self.group_player_class_quantity_comboBox.itemText(self.default_settings["class_quantity_enabled"]))
                    class_quantity = self.group_player_class_quantity_comboBox.findText(class_quantity_text)
                    if class_quantity == -1:
                        # 如果文字选项无效，则使用索引值
                        logger.warning(f"无效的便捷修改班级文本: {class_quantity_text}")
                        class_quantity = group_player_settings.get("class_quantity", self.default_settings["class_quantity_enabled"])
                        if class_quantity < 0 or class_quantity >= self.group_player_class_quantity_comboBox.count():
                            # 如果索引值无效，则使用默认值
                            logger.warning(f"无效的便捷修改班级索引: {class_quantity}")
                            class_quantity = self.default_settings["class_quantity_enabled"]

                    self.group_player_Draw_comboBox.setCurrentIndex(draw_mode)
                    self.group_player_Animation_comboBox.setCurrentIndex(animation_mode)
                    self.group_player_Voice_comboBox.setCurrentIndex(voice_enabled)
                    self.group_player_student_id_comboBox.setCurrentIndex(student_id)
                    self.group_player_student_name_comboBox.setCurrentIndex(student_name)
                    self.group_player_student_quantity_comboBox.setCurrentIndex(student_quantity)
                    self.group_player_class_quantity_comboBox.setCurrentIndex(class_quantity)  
                    logger.info(f"加载完成: draw_mode={draw_mode}, animation_mode={animation_mode}, voice_enabled={voice_enabled}, student_id={student_id}, student_name={student_name}, student_quantity={student_quantity}, class_quantity={class_quantity}")
            else:
                logger.warning(f"设置文件不存在: {self.settings_file}")
                self.group_player_Draw_comboBox.setCurrentIndex(self.default_settings["draw_mode"])
                self.group_player_Animation_comboBox.setCurrentIndex(self.default_settings["animation_mode"])
                self.group_player_Voice_comboBox.setCurrentIndex(self.default_settings["voice_enabled"])
                self.group_player_student_id_comboBox.setCurrentIndex(self.default_settings["student_id"])
                self.group_player_student_name_comboBox.setCurrentIndex(self.default_settings["student_name"])
                self.group_player_student_quantity_comboBox.setCurrentIndex(self.default_settings["student_quantity_enabled"])
                self.group_player_class_quantity_comboBox.setCurrentIndex(self.default_settings["class_quantity_enabled"])
                self.save_settings()
        except Exception as e:
            logger.error(f"加载设置时出错: {e}")
            self.group_player_Draw_comboBox.setCurrentIndex(self.default_settings["draw_mode"])
            self.group_player_Animation_comboBox.setCurrentIndex(self.default_settings["animation_mode"])
            self.group_player_Voice_comboBox.setCurrentIndex(self.default_settings["voice_enabled"])
            self.group_player_student_id_comboBox.setCurrentIndex(self.default_settings["student_id"])
            self.group_player_student_name_comboBox.setCurrentIndex(self.default_settings["student_name"])
            self.group_player_student_quantity_comboBox.setCurrentIndex(self.default_settings["student_quantity_enabled"])
            self.group_player_class_quantity_comboBox.setCurrentIndex(self.default_settings["class_quantity_enabled"])
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
        
        # 更新group_player部分的所有设置
        if "group_player" not in existing_settings:
            existing_settings["group_player"] = {}
            
        group_player_settings = existing_settings["group_player"]
        # 保存文字选项
        group_player_settings["draw_mode_text"] = self.group_player_Draw_comboBox.currentText()
        group_player_settings["animation_mode_text"] = self.group_player_Animation_comboBox.currentText()
        group_player_settings["voice_enabled_text"] = self.group_player_Voice_comboBox.currentText()
        group_player_settings["student_id_text"] = self.group_player_student_id_comboBox.currentText()
        group_player_settings["student_name_text"] = self.group_player_student_name_comboBox.currentText()
        group_player_settings["student_quantity_text"] = self.group_player_student_quantity_comboBox.currentText()
        group_player_settings["class_quantity_text"] = self.group_player_class_quantity_comboBox.currentText()
        # 同时保存索引值
        group_player_settings["draw_mode"] = self.group_player_Draw_comboBox.currentIndex()
        group_player_settings["animation_mode"] = self.group_player_Animation_comboBox.currentIndex()
        group_player_settings["voice_enabled"] = self.group_player_Voice_comboBox.currentIndex()
        group_player_settings["student_id"] = self.group_player_student_id_comboBox.currentIndex()
        group_player_settings["student_name"] = self.group_player_student_name_comboBox.currentIndex()
        group_player_settings["student_quantity"] = self.group_player_student_quantity_comboBox.currentIndex()
        group_player_settings["class_quantity"] = self.group_player_class_quantity_comboBox.currentIndex()
        
        os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
        with open(self.settings_file, 'w', encoding='utf-8') as f:
            json.dump(existing_settings, f, indent=4)