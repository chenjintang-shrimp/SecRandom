import os
from loguru import logger

from qfluentwidgets import * # type: ignore
from qfluentwidgets import FluentIcon as fIcon # type: ignore
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from ..common.config import load_custom_font

class single(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
    
    def start_draw(self):
        """开始抽选学生"""
        import json
        
        # 获取抽选模式设置
        try:
            with open('app/Settings/Settings.json', 'r', encoding='utf-8') as f:
                settings = json.load(f)
                single_player_draw_mode = settings['single_player']['draw_mode']
                if single_player_draw_mode == 0:
                    global_draw_mode = settings['global']['draw_mode']
        except Exception as e:
            single_player_draw_mode = 1
            logger.error(f"加载抽选模式设置时出错: {e}, 使用默认:不重复抽取(直到软件重启)模式")
            
        # 根据抽选模式执行不同逻辑
        # 跟随全局设置
        if global_draw_mode == 0  and single_player_draw_mode == 0:  # 重复随机
            self.random_draw()
        elif global_draw_mode == 1  and single_player_draw_mode == 0:  # 不重复抽取(直到软件重启)
            self.until_the_reboot_draw()
        elif global_draw_mode == 2  and single_player_draw_mode == 0:  # 不重复抽取(直到抽完全部人)
            self.until_all_draw_mode()
        # 跟随单抽设置
        elif single_player_draw_mode == 1:  # 重复随机
            self.random_draw()
        elif single_player_draw_mode == 2:  # 不重复抽取(直到软件重启)
            self.until_the_reboot_draw()
        elif single_player_draw_mode == 3:  # 不重复抽取(直到抽完全部人)
            self.until_all_draw_mode()
            
    def random_draw(self):
        """重复随机抽选学生"""
        class_name = self.class_combo.currentText()
        if class_name and class_name not in ["你暂未添加班级,请到设置进行添加", "加载班级列表失败"]:
            student_file = f"app/resource/students/{class_name}.ini"
            if os.path.exists(student_file):
                with open(student_file, 'r', encoding='utf-8') as f:
                    students = [(i+1, line.strip()) for i, line in enumerate(f) if line.strip()]
                    if students:
                        import random
                        line_num, selected = random.choice(students)
                        self.main_text.setText(f"{line_num}")
                        self.sub_text.setText(selected)
                        return
        
        self.main_text.setText("--")
        self.sub_text.setText("抽选失败")
        
    def until_the_reboot_draw(self):
        """不重复抽取(直到软件重启)"""
        class_name = self.class_combo.currentText()
        if class_name and class_name not in ["你暂未添加班级,请到设置进行添加", "加载班级列表失败"]:
            student_file = f"app/resource/students/{class_name}.ini"
            draw_record_file = f"app/resource/Temp/until_the_reboot_draw_{class_name}.json"
            
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
                    students = [(i+1, line.strip()) for i, line in enumerate(f) if line.strip()]
                    available_students = [s for s in students if s[1] not in drawn_students]
                    
                    if available_students:
                        import random
                        line_num, selected = random.choice(available_students)
                        self.main_text.setText(f"{line_num}")
                        self.sub_text.setText(selected)
                        
                        # 更新抽取记录
                        drawn_students.append(selected)
                        with open(draw_record_file, 'w', encoding='utf-8') as f:
                            json.dump(drawn_students, f, ensure_ascii=False, indent=4)
                        return
                    else:
                        # 删除临时文件
                        if os.path.exists(draw_record_file):
                            os.remove(draw_record_file)

                        Flyout.create(
                            icon=InfoBarIcon.SUCCESS,
                            title='抽选完成',
                            content="所有学生都已被抽选完毕，临时记录已清除\n显示的结果为新一轮抽选的结果,您可继续抽取",
                            target=self.start_button,
                            parent=self,
                            isClosable=True,
                            aniType=FlyoutAnimationType.PULL_UP
                        )

                        self.until_the_reboot_draw()
                        return
        
        self.main_text.setText("--")
        self.sub_text.setText("抽选失败")
        
    def until_all_draw_mode(self):
        """不重复抽取(直到抽完全部人)"""
        class_name = self.class_combo.currentText()
        if class_name and class_name not in ["你暂未添加班级,请到设置进行添加", "加载班级列表失败"]:
            student_file = f"app/resource/students/{class_name}.ini"
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
                    students = [(i+1, line.strip()) for i, line in enumerate(f) if line.strip()]
                    available_students = [s for s in students if s[1] not in drawn_students]
                    
                    if available_students:
                        import random
                        line_num, selected = random.choice(available_students)
                        self.main_text.setText(f"{line_num}")
                        self.sub_text.setText(selected)
                        
                        # 更新抽取记录
                        drawn_students.append(selected)
                        with open(draw_record_file, 'w', encoding='utf-8') as f:
                            json.dump(drawn_students, f, ensure_ascii=False, indent=4)
                        return
                    else:
                        # 删除临时文件
                        if os.path.exists(draw_record_file):
                            os.remove(draw_record_file)

                        Flyout.create(
                            icon=InfoBarIcon.SUCCESS,
                            title='抽选完成',
                            content="所有学生都已被抽选完毕，记录已清除\n显示的结果为新一轮抽选的结果, 您可继续抽取",
                            target=self.start_button,
                            parent=self,
                            isClosable=True,
                            aniType=FlyoutAnimationType.PULL_UP
                        )
                        
                        # 重新开始新一轮抽选
                        self.until_all_draw_mode()
                        return
        
        self.main_text.setText("--")
        self.sub_text.setText("抽选失败")
        
    def update_total_count(self):
        """根据选择的班级更新总人数显示"""
        class_name = self.class_combo.currentText()
        if class_name and class_name not in ["你暂未添加班级,请到设置进行添加", "加载班级列表失败"]:
            student_file = f"app/resource/students/{class_name}.ini"
            if os.path.exists(student_file):
                with open(student_file, 'r', encoding='utf-8') as f:
                    count = len([line.strip() for line in f if line.strip()])
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
                        Flyout.create(
                            icon=InfoBarIcon.SUCCESS,
                            title='加载成功',
                            content="加载班级列表成功！",
                            target=self.refresh_button,
                            parent=self,
                            isClosable=True,
                            aniType=FlyoutAnimationType.PULL_UP
                        )
                    else:
                        logger.error(f"你暂未添加班级,请到设置进行添加")
                        Flyout.create(
                            icon=InfoBarIcon.ERROR,
                            title='加载失败',
                            content=f'加载班级列表失败: 你暂未添加班级,请到设置进行添加',
                            target=self.refresh_button,
                            parent=self,
                            isClosable=True,
                            aniType=FlyoutAnimationType.PULL_UP
                        )
            else:
                logger.error(f"你暂未添加班级,请到设置进行添加")
                Flyout.create(
                    icon=InfoBarIcon.ERROR,
                    title='加载失败',
                    content=f'加载班级列表失败: 你暂未添加班级,请到设置进行添加',
                    target=self.refresh_button,
                    parent=self,
                    isClosable=True,
                    aniType=FlyoutAnimationType.PULL_UP
                )
        except Exception as e:
            logger.error(f"加载班级列表失败: {str(e)}")
            Flyout.create(
                icon=InfoBarIcon.ERROR,
                title='加载失败',
                content=f'加载班级列表失败: {str(e)}',
                target=self.refresh_button,
                parent=self,
                isClosable=True,
                aniType=FlyoutAnimationType.PULL_UP
            )
        self.update_total_count()
        
    def initUI(self):
        # 主布局
        main_layout = QVBoxLayout()
        
        # 按钮布局
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(50, 0, 0, 0)  # 左边距20像素
        
        # 开始按钮
        self.start_button = PrimaryPushButton('开始')
        self.start_button.setFixedSize(100, 50)
        self.start_button.setFont(QFont(load_custom_font(), 20))
        self.start_button.clicked.connect(self.start_draw)
        button_layout.addWidget(self.start_button, 0, Qt.AlignVCenter | Qt.AlignLeft)
        
        # 上部布局（按钮和文本）
        top_layout = QHBoxLayout()
        top_layout.addLayout(button_layout)
        
        # 文本区域
        text_layout = QVBoxLayout()
        self.main_text = QLabel('--')
        self.main_text.setAlignment(Qt.AlignCenter | Qt.AlignTop)
        self.main_text.setFont(QFont(load_custom_font(), 88))
        
        self.sub_text = QLabel('别紧张')
        self.sub_text.setAlignment(Qt.AlignCenter | Qt.AlignTop)
        self.sub_text.setFont(QFont(load_custom_font(), 88))
        
        text_layout.addWidget(self.main_text)
        text_layout.setSpacing(30)  # 减小垂直间距
        text_layout.addWidget(self.sub_text)
        
        main_layout.addLayout(text_layout)
        main_layout.addStretch(1)
        main_layout.addLayout(top_layout)
        
        # 底部信息栏
        bottom_layout = QHBoxLayout()
        bottom_layout.setContentsMargins(50, 0, 0, 20)  # 左边距50像素，底部边距20像素

        # 刷新按钮
        self.refresh_button = QPushButton('刷新')
        self.refresh_button.setFixedSize(100, 40)
        self.refresh_button.setFont(QFont(load_custom_font(), 14))
        self.refresh_button.clicked.connect(self.refresh_class_list)
        bottom_layout.addWidget(self.refresh_button)

        # 班级下拉框
        self.class_combo = ComboBox()
        self.class_combo.setFixedWidth(200)
        self.class_combo.setFont(QFont(load_custom_font(), 14))
        
        # 加载班级列表
        try:
            class_file = "app/resource/class/class.ini"
            if os.path.exists(class_file):
                with open(class_file, 'r', encoding='utf-8') as f:
                    classes = [line.strip() for line in f.read().split('\n') if line.strip()]
                    if classes:
                        self.class_combo.addItems(classes)
                    else:
                        self.class_combo.addItem("你暂未添加班级,请到设置进行添加")
            else:
                self.class_combo.addItem("你暂未添加班级,请到设置进行添加")
        except Exception as e:
            logger.error(f"加载班级列表失败: {str(e)}")
            self.class_combo.addItem("加载班级列表失败")
        
        bottom_layout.addWidget(self.class_combo)

        # 总人数显示
        self.total_label = QLabel('总人数: 0')
        self.total_label.setFont(QFont(load_custom_font(), 14))
        self.total_label.setFixedWidth(200)
        bottom_layout.addWidget(self.total_label, 0, Qt.AlignLeft)
        
        # 班级选择变化时更新总人数
        self.class_combo.currentTextChanged.connect(self.update_total_count)
        
        # 初始化总人数显示
        self.update_total_count()
        
        main_layout.addStretch(1)  # 添加弹性空间
        main_layout.addLayout(bottom_layout)
        
        self.setLayout(main_layout)