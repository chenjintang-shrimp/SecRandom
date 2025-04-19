from qfluentwidgets import *
from qfluentwidgets import FluentIcon as FIF
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

import os
from loguru import logger

from app.common.config import load_custom_font

class ClassInputDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("输入班级名称")
        self.setFixedSize(400, 300)
        self.saved = False
        
        self.text_label = BodyLabel('请输入班级名称，每行一个\n本班级的班级名称向前放\n注:用大写数字排序会乱')
        self.text_label.setFont(QFont(load_custom_font(), 14))

        # 读取主题设置
        try:
            with open('app/Settings/config.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
                theme_mode = config['QFluentWidgets']['ThemeMode']
        except Exception as e:
            logger.error(f"读取主题设置失败: {str(e)}")
            theme_mode = "Auto"
        
        # 根据主题模式设置样式
        if theme_mode == "Light":
            self.setStyleSheet("""
                QDialog, QDialog * {
                    color: black;
                    background-color: white;
                }
            """)
        elif theme_mode == "Dark":
            self.setStyleSheet("""
                QDialog, QDialog * {
                    color: white;
                    background-color: black;
                }
            """)
        else:  # Auto
            self.setStyleSheet("""
                QDialog, QDialog * {
                    background-color: white;
                }
            """)
            self.text_label.setFont(QFont(load_custom_font(), 14))
            self.text_label.setStyleSheet("color: black;")
        
        self.textEdit = PlainTextEdit()
        self.textEdit.setPlaceholderText("请输入班级名称，每行一个")
        self.textEdit.setFont(QFont(load_custom_font(), 14))
        
        # 统一设置对话框字体
        self.setFont(QFont(load_custom_font(), 14))
        
        # 尝试读取已保存的班级文件
        try:
            with open("app/resource/class/class.ini", 'r', encoding='utf-8') as f:
                self.textEdit.setPlainText(f.read())
        except FileNotFoundError:
            pass
        
        self.saveButton = PrimaryPushButton("保存")
        self.cancelButton = PushButton("取消")
        self.saveButton.clicked.connect(self.accept)
        self.cancelButton.clicked.connect(self.reject)
        self.saveButton.setFont(QFont(load_custom_font(), 14))
        self.cancelButton.setFont(QFont(load_custom_font(), 14))
        
        layout = QVBoxLayout()
        layout.addWidget(self.text_label)
        layout.addWidget(self.textEdit)
        
        buttonLayout = QHBoxLayout()
        buttonLayout.addStretch(1)
        buttonLayout.addWidget(self.cancelButton)
        buttonLayout.addWidget(self.saveButton)
        
        layout.addLayout(buttonLayout)
        self.setLayout(layout)
        
    def closeEvent(self, event):
        if self.textEdit.toPlainText() and not self.saved:
            w = Dialog('未保存内容', '有未保存的内容，确定要关闭吗？', self)
            w.setFont(QFont(load_custom_font(), 14))
            w.yesButton.setText("确定")
            w.cancelButton.setText("取消")
            w.yesButton = PrimaryPushButton('确定')
            w.cancelButton = PushButton('取消')
            
            if w.exec():
                self.reject
                return
            else:
                event.ignore()
                return
        event.accept()
    
    def getText(self):
        return self.textEdit.toPlainText()

class StudentInputDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("输入学生姓名")
        self.setFixedSize(400, 600)
        self.saved = False

        self.text_label = BodyLabel('请输入学生姓名，每行一个\n在输入已经不在当前班级的学生时\n请在姓名前后加上【】')
        self.text_label.setFont(QFont(load_custom_font(), 14))

        # 读取主题设置
        try:
            with open('app/Settings/config.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
                theme_mode = config['QFluentWidgets']['ThemeMode']
        except Exception as e:
            logger.error(f"读取主题设置失败: {str(e)}")
            theme_mode = "Auto"
        
        # 根据主题模式设置样式
        if theme_mode == "Light":
            self.setStyleSheet("""
                QDialog, QDialog * {
                    color: black;
                    background-color: white;
                }
            """)
        elif theme_mode == "Dark":
            self.setStyleSheet("""
                QDialog, QDialog * {
                    color: white;
                    background-color: black;
                }
            """)
        else:  # Auto
            self.setStyleSheet("""
                QDialog, QDialog * {
                    background-color: white;
                }
            """)
            self.text_label.setFont(QFont(load_custom_font(), 14))
            self.text_label.setStyleSheet("color: black;")
        
        self.textEdit = PlainTextEdit()
        self.textEdit.setPlaceholderText("请输入学生姓名，每行一个")
        self.textEdit.setFont(QFont(load_custom_font(), 14))
        
        # 统一设置对话框字体
        self.setFont(QFont(load_custom_font(), 14))
        
        # 尝试读取已保存的学生文件
        try:
            selected_class = self.parent().class_comboBox.currentText()
            if selected_class:
                with open(f"app/resource/students/{selected_class}.ini", 'r', encoding='utf-8') as f:
                    self.textEdit.setPlainText(f.read())
        except (FileNotFoundError, AttributeError):
            pass
        
        self.saveButton = PrimaryPushButton("保存")
        self.cancelButton = PushButton("取消")
        self.saveButton.clicked.connect(self.accept)
        self.cancelButton.clicked.connect(self.reject)
        
        layout = QVBoxLayout()
        layout.addWidget(self.text_label)
        layout.addWidget(self.textEdit)
        
        buttonLayout = QHBoxLayout()
        buttonLayout.addStretch(1)
        buttonLayout.addWidget(self.cancelButton)
        buttonLayout.addWidget(self.saveButton)
        
        layout.addLayout(buttonLayout)
        self.setLayout(layout)
        
    def closeEvent(self, event):
        if self.textEdit.toPlainText() and not self.saved:
            w = Dialog('未保存内容', '有未保存的内容，确定要关闭吗？', self)
            w.setFont(QFont(load_custom_font(), 14))
            w.yesButton.setText("确定")
            w.cancelButton.setText("取消")
            w.yesButton = PrimaryPushButton('确定')
            w.cancelButton = PushButton('取消')
            
            if w.exec():
                self.reject
            else:
                event.ignore()
                return
        event.accept()
    
    def getText(self):
        return self.textEdit.toPlainText()

class GroupInputDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("输入小组名单")
        self.setFixedSize(400, 400)
        self.saved = False

        self.text_label = BodyLabel('请输入小组名称，每行一个\尽量用小写数字来排序\n例:第1小组_[组名]\n注:用大写数字排序会乱')
        self.text_label.setFont(QFont(load_custom_font(), 14))

        # 读取主题设置
        try:
            with open('app/Settings/config.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
                theme_mode = config['QFluentWidgets']['ThemeMode']
        except Exception as e:
            logger.error(f"读取主题设置失败: {str(e)}")
            theme_mode = "Auto"
        
        # 根据主题模式设置样式
        if theme_mode == "Light":
            self.setStyleSheet("""
                QDialog, QDialog * {
                    color: black;
                    background-color: white;
                }
            """)
        elif theme_mode == "Dark":
            self.setStyleSheet("""
                QDialog, QDialog * {
                    color: white;
                    background-color: black;
                }
            """)
        else:  # Auto
            self.setStyleSheet("""
                QDialog, QDialog * {
                    background-color: white;
                }
            """)
            self.text_label.setFont(QFont(load_custom_font(), 14))
            self.text_label.setStyleSheet("color: black;")
        
        self.textEdit = PlainTextEdit()
        self.textEdit.setPlaceholderText("请输入小组名称，每行一个")
        self.textEdit.setFont(QFont(load_custom_font(), 14))
        
        # 统一设置对话框字体
        self.setFont(QFont(load_custom_font(), 14))
        
        class_name = self.parent().class_comboBox.currentText()
        # 尝试读取已保存的小组文件
        try:
            with open(f"app/resource/group/{class_name}_group.ini", 'r', encoding='utf-8') as f:
                self.textEdit.setPlainText(f.read())
        except FileNotFoundError:
            pass
        
        self.saveButton = PrimaryPushButton("保存")
        self.cancelButton = PushButton("取消")
        self.saveButton.clicked.connect(self.accept)
        self.cancelButton.clicked.connect(self.reject)
        
        layout = QVBoxLayout()
        layout.addWidget(self.text_label)
        layout.addWidget(self.textEdit)
        
        buttonLayout = QHBoxLayout()
        buttonLayout.addStretch(1)
        buttonLayout.addWidget(self.cancelButton)
        buttonLayout.addWidget(self.saveButton)
        
        layout.addLayout(buttonLayout)
        self.setLayout(layout)
        
    def closeEvent(self, event):
        if self.textEdit.toPlainText() and not self.saved:
            w = Dialog('未保存内容', '有未保存的内容，确定要关闭吗？', self)
            w.setFont(QFont(load_custom_font(), 14))
            w.yesButton.setText("确定")
            w.cancelButton.setText("取消")
            w.yesButton = PrimaryPushButton('确定')
            w.cancelButton = PushButton('取消')
            
            if w.exec():
                self.reject
                return
            else:
                event.ignore()
                return
        event.accept()
    
    def getText(self):
        return self.textEdit.toPlainText()

class GroupStudentInputDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("输入小组成员姓名")
        self.setFixedSize(400, 400)
        self.saved = False

        self.text_label = BodyLabel('请输入小组成员姓名，每行一个\n在输入已经不在当前班级的学生时\n请在姓名前后加上【】')
        self.text_label.setFont(QFont(load_custom_font(), 14))

        # 读取主题设置
        try:
            with open('app/Settings/config.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
                theme_mode = config['QFluentWidgets']['ThemeMode']
        except Exception as e:
            logger.error(f"读取主题设置失败: {str(e)}")
            theme_mode = "Auto"
        
        # 根据主题模式设置样式
        if theme_mode == "Light":
            self.setStyleSheet("""
                QDialog, QDialog * {
                    color: black;
                    background-color: white;
                }
            """)
        elif theme_mode == "Dark":
            self.setStyleSheet("""
                QDialog, QDialog * {
                    color: white;
                    background-color: black;
                }
            """)
        else:  # Auto
            self.setStyleSheet("""
                QDialog, QDialog * {
                    background-color: white;
                }
            """)
            self.text_label.setFont(QFont(load_custom_font(), 14))
            self.text_label.setStyleSheet("color: black;")
        
        self.textEdit = PlainTextEdit()
        self.textEdit.setPlaceholderText("请输入小组成员姓名，每行一个")
        self.textEdit.setFont(QFont(load_custom_font(), 14))
        
        # 统一设置对话框字体
        self.setFont(QFont(load_custom_font(), 14))
        
        # 尝试读取已保存的小组成员文件
        try:
            selected_group = self.parent().group_ComboBox.currentText()
            group_name = self.parent().class_comboBox.currentText()
            if selected_group:
                with open(f"app/resource/group/{group_name}_{selected_group}.ini", 'r', encoding='utf-8') as f:
                    self.textEdit.setPlainText(f.read())
        except (FileNotFoundError, AttributeError):
            pass
        
        self.saveButton = PrimaryPushButton("保存")
        self.cancelButton = PushButton("取消")
        self.saveButton.clicked.connect(self.accept)
        self.cancelButton.clicked.connect(self.reject)
        
        layout = QVBoxLayout()
        layout.addWidget(self.text_label)
        layout.addWidget(self.textEdit)
        
        buttonLayout = QHBoxLayout()
        buttonLayout.addStretch(1)
        buttonLayout.addWidget(self.cancelButton)
        buttonLayout.addWidget(self.saveButton)
        
        layout.addLayout(buttonLayout)
        self.setLayout(layout)
        
    def closeEvent(self, event):
        if self.textEdit.toPlainText() and not self.saved:
            w = Dialog('未保存内容', '有未保存的内容，确定要关闭吗？', self)
            w.setFont(QFont(load_custom_font(), 14))
            w.yesButton.setText("确定")
            w.cancelButton.setText("取消")
            w.yesButton = PrimaryPushButton('确定')
            w.cancelButton = PushButton('取消')
            
            if w.exec():
                self.reject
                return
            else:
                event.ignore()
                return
        event.accept()
    
    def getText(self):
        return self.textEdit.toPlainText()


class list_SettinsCard(GroupHeaderCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("名单设置")
        self.setBorderRadius(8)
        self.settings_file = "app/Settings/Settings.json"
        self.default_settings = {
            "player_people": 30,
            "use_lists": False
        }

        # 人数输入框
        self.player_people_edit = LineEdit()
        self.player_people_edit.setPlaceholderText("请输入人数 (最小值为1)")
        self.player_people_edit.setClearButtonEnabled(True)
        # 设置宽度和高度
        self.player_people_edit.setFixedWidth(320)
        self.player_people_edit.setFixedHeight(32)
        # 设置字体
        self.player_people_edit.setFont(QFont(load_custom_font(), 14))

        # 添加应用按钮
        apply_action = QAction(FluentIcon.SAVE.qicon(), "", triggered=self.apply_player_people)
        self.player_people_edit.addAction(apply_action, QLineEdit.TrailingPosition)

        # 是否使用名单按钮
        self.use_lists_switch = SwitchButton()
        self.use_lists_switch.setOnText("开启")
        self.use_lists_switch.setOffText("关闭")
        self.use_lists_switch.checkedChanged.connect(self.save_settings)
        self.use_lists_switch.setFont(QFont(load_custom_font(), 14))

        self.class_Button = PrimaryPushButton("设置班级")
        self.class_Button.clicked.connect(self.show_class_dialog)
        self.class_Button.setFont(QFont(load_custom_font(), 14))
        
        self.student_Button = PrimaryPushButton("设置班级名单")
        self.student_Button.clicked.connect(self.show_student_dialog)
        self.student_Button.setFont(QFont(load_custom_font(), 14))
        
        self.class_comboBox = ComboBox()
        self.class_comboBox.setFixedWidth(320)
        self.class_comboBox.setPlaceholderText("选择一个需要设置名单的班级")
        self.class_comboBox.addItems([])
        self.class_comboBox.setFont(QFont(load_custom_font(), 14))
        self.class_comboBox.currentIndexChanged.connect(self._show_group_dialog)

        self.group_Button = PrimaryPushButton("设置小组")
        self.group_Button.clicked.connect(self.show_group_dialog)
        self.group_Button.setFont(QFont(load_custom_font(), 14))

        self.group_ComboBox = ComboBox()
        self.group_ComboBox.setFixedWidth(320)
        self.group_ComboBox.setPlaceholderText("选择一个需要添加成员的小组")
        self.group_ComboBox.addItems([])
        self.group_ComboBox.setFont(QFont(load_custom_font(), 14))

        self.group_student_Button = PrimaryPushButton("设置小组成员")
        self.group_student_Button.clicked.connect(self.show_group_student_dialog)
        self.group_student_Button.setFont(QFont(load_custom_font(), 14))
        
        # 程序启动时自动加载班级名称
        try:
            if os.path.exists("app/resource/class/class.ini"):
                with open("app/resource/class/class.ini", 'r', encoding='utf-8') as f:
                    classes = [line.strip() for line in f.read().split('\n') if line.strip()]
                    self.class_comboBox.clear()
                    self.class_comboBox.addItems(classes)
        except Exception as e:
            logger.error(f"加载班级名称失败: {str(e)}")

        # 添加组件到分组中
        self.addGroup(FIF.LABEL, "仅学号名单", "是否使用只有学号的名单类型", self.use_lists_switch)
        self.addGroup(FIF.ADD_TO, "设置班级", "点击按钮设置班级名称", self.class_Button)
        self.addGroup(FIF.EDUCATION, "选择班级", "选择一个需要设置学生姓名的班级", self.class_comboBox)
        self.addGroup(FIF.PEOPLE, "设置班级仅学号的人数", "设置只用学号的名单类型时的人数", self.player_people_edit)
        self.addGroup(FIF.PEOPLE, "设置班级名单", "点击按钮设置学生姓名", self.student_Button)
        self.addGroup(FIF.ADD_TO, "设置小组", "点击按钮设置小组名单", self.group_Button)
        self.addGroup(FIF.TILES, "选择小组", "选择一个需要修改成员的小组", self.group_ComboBox)
        self.addGroup(FIF.PEOPLE, "设置小组成员", "点击按钮设置该小组成员的姓名", self.group_student_Button)

        self.load_settings()
        self.save_settings()

    def apply_player_people(self):
        class_name = self.class_comboBox.currentText()
        try:
            player_people = int(self.player_people_edit.text())
            if 1 <= player_people <= 200:
                self.player_people_edit.setText(str(player_people))
                self.save_settings()
                os.makedirs("app/resource/students", exist_ok=True)

                def write_people_ini():
                    with open(f"app/resource/students/people_{class_name}.ini", 'w', encoding='utf-8') as f:
                        f.writelines(f"{i}\n" for i in range(1, player_people + 1))
                    logger.info(f"设置人数: {player_people}")

                # 直接调用 write_people_ini 函数，不需要检查 use_lists 设置
                write_people_ini()

                InfoBar.success(
                    title='设置成功',
                    content=f"设置人数为: {player_people}",
                    orient=Qt.Horizontal,
                    parent=self,
                    isClosable=True,
                    duration=3000
                )
            else:
                logger.warning(f"人数超出范围: {player_people}")
                InfoBar.warning(
                    title='人数超出范围',
                    content=f"人数超出范围，请输入1-200之间的整数: {player_people}",
                    orient=Qt.Horizontal,
                    parent=self,
                    isClosable=True,
                    duration=3000
                )
        except ValueError:
            logger.warning(f"无效的人数输入: {self.player_people_edit.text()}")
            InfoBar.warning(
                title='无效的人数输入',
                content=f"无效的人数输入(需要是整数)：{self.player_people_edit.text()}",
                orient=Qt.Horizontal,
                parent=self,
                isClosable=True,
                duration=3000
            )

            
    def show_class_dialog(self):
        dialog = ClassInputDialog(self)
        if dialog.exec():
            class_text = dialog.getText()
            if class_text:
                try:
                    classes = [line.strip() for line in class_text.split('\n') if line.strip()]

                    # 确保class目录存在
                    os.makedirs("app/resource/class", exist_ok=True)
                    
                    # 保存到class.ini
                    class_file = "app/resource/class/class.ini"
                    with open(class_file, 'w', encoding='utf-8') as f:
                        f.write('\n'.join(classes))
                    
                    # 更新下拉框
                    self.class_comboBox.clear()
                    self.class_comboBox.addItems(classes)
                    logger.info("班级名单保存成功！\n某些显示可能需要刷新或重启软件才能生效")
                    Flyout.create(
                        icon=InfoBarIcon.SUCCESS,
                        title='保存成功',
                        content="班级名单已成功保存！\n某些显示可能需要刷新或重启软件才能生效",
                        target=self.class_Button,
                        parent=self,
                        isClosable=True,
                        aniType=FlyoutAnimationType.PULL_UP
                    )
                except Exception as e:
                    logger.error(f"保存失败: {str(e)}")
                    Flyout.create(
                        icon=InfoBarIcon.ERROR,
                        title='保存失败',
                        content=f'保存班级名单失败: {str(e)}',
                        target=self.class_Button,
                        parent=self,
                        isClosable=True,
                        aniType=FlyoutAnimationType.PULL_UP
                    )
    
    def show_student_dialog(self):
        dialog = StudentInputDialog(self)
        if dialog.exec():
            student_text = dialog.getText()
            selected_class = self.class_comboBox.currentText()
            if student_text and selected_class:
                try:
                    students = [line.strip() for line in student_text.split('\n') if line.strip()]
                    
                    # 确保students目录存在
                    os.makedirs("app/resource/students", exist_ok=True)
                    
                    # 保存到班级名称.ini
                    student_file = f"app/resource/students/{selected_class}.ini"
                    with open(student_file, 'w', encoding='utf-8') as f:
                        f.write('\n'.join(students))
                    
                    logger.info(f"学生名单保存成功！班级: {selected_class}\n某些显示可能需要刷新或重启软件才能生效")
                    Flyout.create(
                        icon=InfoBarIcon.SUCCESS,
                        title='保存成功',
                        content=f"{selected_class} ->学生名单已成功保存！\n某些显示可能需要刷新或重启软件才能生效",
                        target=self.student_Button,
                        parent=self,
                        isClosable=True,
                        aniType=FlyoutAnimationType.PULL_UP
                    )
                except Exception as e:
                    logger.error(f"保存失败: {str(e)}")
                    Flyout.create(
                        icon=InfoBarIcon.ERROR,
                        title='保存失败',
                        content=f'保存学生名单失败: {str(e)}',
                        target=self.student_Button,
                        parent=self,
                        isClosable=True,
                        aniType=FlyoutAnimationType.PULL_UP
                    )

    def _show_group_dialog(self):
        class_name = self.class_comboBox.currentText()
        try:
            if os.path.exists(f"app/resource/group/{class_name}_group.ini"):
                with open(f"app/resource/group/{class_name}_group.ini", 'r', encoding='utf-8') as f:
                    groups = [line.strip() for line in f.read().split('\n') if line.strip()]
                    self.group_ComboBox.clear()
                    self.group_ComboBox.addItems(groups)
        except Exception as e:
            logger.error(f"加载小组名称失败: {str(e)}")
                    
    def show_group_dialog(self):
        dialog = GroupInputDialog(self)
        if dialog.exec():
            group_text = dialog.getText()
            class_name = self.class_comboBox.currentText()
            if group_text:
                try:
                    groups = [line.strip() for line in group_text.split('\n') if line.strip()]
                    
                    # 确保group目录存在
                    os.makedirs("app/resource/group", exist_ok=True)
                        
                    # 保存到小组名称.ini
                    group_file = f"app/resource/group/{class_name}_group.ini"
                    with open(group_file, 'w', encoding='utf-8') as f:
                        f.write('\n'.join(groups))
                    
                    # 更新下拉框
                    self.group_ComboBox.clear()
                    self.group_ComboBox.addItems(groups)
                    logger.info(f"小组名单保存成功！\n某些显示可能需要刷新或重启软件才能生效")
                    Flyout.create(
                        icon=InfoBarIcon.SUCCESS,
                        title='保存成功',
                        content=f"小组名单已成功保存！\n某些显示可能需要刷新或重启软件才能生效",
                        target=self.group_Button,
                        parent=self,
                        isClosable=True,
                        aniType=FlyoutAnimationType.PULL_UP
                    )
                except Exception as e:
                    logger.error(f"保存失败: {str(e)}")
                    Flyout.create(
                        icon=InfoBarIcon.ERROR,
                        title='保存失败',
                        content=f'保存小组名单失败: {str(e)}',
                        target=self.group_Button,
                        parent=self,
                        isClosable=True,
                        aniType=FlyoutAnimationType.PULL_UP
                    )

    def show_group_student_dialog(self):
        selected_group = self.group_ComboBox.currentText()
        class_name = self.class_comboBox.currentText()
        if selected_group:
            dialog = GroupStudentInputDialog(self)
            dialog.setWindowTitle(f"设置{selected_group}的小组成员")
            if dialog.exec():
                student_text = dialog.getText()
                if student_text:
                    try:
                        group_students = [line.strip() for line in student_text.split('\n') if line.strip()]

                        # 确保group目录存在
                        os.makedirs("app/resource/group", exist_ok=True)
                        # 保存到小组名称.ini
                        group_file = f"app/resource/group/{class_name}_{selected_group}.ini"
                        with open(group_file, 'w', encoding='utf-8') as f:
                            f.write('\n'.join(group_students))

                        logger.info(f"{selected_group} ->小组成员名单保存成功！\n某些显示可能需要刷新或重启软件才能生效")
                        Flyout.create(
                            icon=InfoBarIcon.SUCCESS,
                            title='保存成功',
                            content=f"{selected_group} ->小组成员名单已成功保存！\n某些显示可能需要刷新或重启软件才能生效",
                            target=self.group_student_Button,
                            parent=self,
                            isClosable=True,
                            aniType=FlyoutAnimationType.PULL_UP 
                        )                
                    except Exception as e:
                        logger.error(f"保存失败: {str(e)}")
                        Flyout.create(
                            icon=InfoBarIcon.ERROR,
                            title='保存失败',
                            content=f'保存小组成员名单失败: {str(e)}',
                            target=self.group_student_Button,
                            parent=self,
                            isClosable=True,
                            aniType=FlyoutAnimationType.PULL_UP
                        )
                        
    def submit_data(self):
        # 处理班级数据
        class_text = self.classTextEdit.toPlainText()
        if class_text:
            try:
                classes = [line.strip() for line in class_text.split('\n') if line.strip()]
                
                # 保存到class.ini
                class_file = "app/resource/class/class.ini"
                with open(class_file, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(classes))
                
                # 更新下拉框
                self.class_comboBox.clear()
                self.class_comboBox.addItems(classes)
                logger.info("班级名单保存成功！")
            except Exception as e:
                logger.error(f"保存失败: {str(e)}")
        
        # 处理学生数据
        selected_class = self.class_comboBox.currentText()
        student_text = self.studentTextEdit.toPlainText()
        
        if not selected_class and student_text:
            logger.warning("请先选择一个班级")
            Flyout.create(
                icon=InfoBarIcon.WARNING,
                title='警告',
                content="请先选择一个班级！", 
                target=self.student_Button,
                parent=self,
                isClosable=True,
                aniType=FlyoutAnimationType.PULL_UP
            )
            return
            
        if student_text:
            try:
                students = [line.strip() for line in student_text.split('\n') if line.strip()]
                
                # 保存到班级名称.ini
                student_file = f"app/resource/students/{selected_class}.ini"
                with open(student_file, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(students))
                
                logger.info("学生名单保存成功！")
            except Exception as e:
                logger.error(f"保存失败: {str(e)}")

    def load_settings(self):
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    list_strings_settings = settings.get("list_strings", {})

                    player_people = list_strings_settings.get("player_people", self.default_settings["player_people"])

                    use_lists = list_strings_settings.get("use_lists", self.default_settings["use_lists"])

                    self.use_lists_switch.setChecked(use_lists)
                    self.player_people_edit.setText(str(player_people))
                    logger.info(f"加载名单设置设置完成")
            else:
                logger.warning(f"设置文件不存在: {self.settings_file}")
                self.player_people_edit.setText(str(self.default_settings["player_people"]))
                self.use_lists_switch.setChecked(self.default_settings["use_lists"])
                self.save_settings()
        except Exception as e:
            logger.error(f"加载设置时出错: {e}")
            self.player_people_edit.setText(str(self.default_settings["player_people"]))
            self.use_lists_switch.setChecked(self.default_settings["use_lists"])
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

        # 更新single_player部分的所有设置
        if "list_strings" not in existing_settings:
            existing_settings["list_strings"] = {}

        list_strings_settings = existing_settings["list_strings"]

        # 同时保存索引值
        list_strings_settings["use_lists"] = self.use_lists_switch.isChecked()

        try:
            player_people = int(list_strings_settings.get("player_people", self.default_settings["player_people"]))
            if 1 <= player_people <= 200:
                list_strings_settings["player_people"] = player_people
            else:
                logger.warning(f"人数超出范围: {player_people}")
                InfoBar.warning(
                    title='人数超出范围',
                    content=f"人数超出范围，请输入1-200之间的整数: {player_people}",
                    orient=Qt.Horizontal,
                    parent=self,
                    isClosable=True,
                    duration=3000
                )
        except ValueError:
            logger.warning(f"无效的人数输入: {self.player_people_edit.text()}")
            InfoBar.warning(
                title='无效的人数输入',
                content=f"无效的人数输入(需要是整数)：{self.player_people_edit.text()}",
                orient=Qt.Horizontal,
                parent=self,
                isClosable=True,
                duration=3000
            )

        os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
        with open(self.settings_file, 'w', encoding='utf-8') as f:
            json.dump(existing_settings, f, indent=4)