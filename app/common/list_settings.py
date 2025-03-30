from qfluentwidgets import *
from qfluentwidgets import FluentIcon as FIF
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (QHBoxLayout, QVBoxLayout, QWidget, QLabel, QPushButton, 
                            QComboBox, QLineEdit, QFileDialog, QMessageBox, QDialog, 
                            QDialogButtonBox)

import os
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

class ClassInputDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("输入班级名称")
        self.setFixedSize(400, 300)
        self.setStyleSheet("background-color: white;")
        self.saved = False
        
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
            w.yesButton.setText("保存")
            w.cancelButton.setText("取消")
            w.yesButton = PrimaryPushButton('保存')
            w.cancelButton = PushButton('取消')
            
            if w.exec(): 
                self.accept()
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
        self.setStyleSheet("background-color: white;")
        self.saved = False
        
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
            w.yesButton.setText("保存")
            w.cancelButton.setText("取消")
            w.yesButton = PrimaryPushButton('保存')
            w.cancelButton = PushButton('取消')
            
            if w.exec():
                self.accept()
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
        self.setStyleSheet("background-color: white;")
        self.saved = False
        
        self.textEdit = PlainTextEdit()
        self.textEdit.setPlaceholderText("请输入小组名称，每行一个")
        self.textEdit.setFont(QFont(load_custom_font(), 14))
        
        # 统一设置对话框字体
        self.setFont(QFont(load_custom_font(), 14))
        
        # 尝试读取已保存的小组文件
        try:
            with open("app/resource/class/group.ini", 'r', encoding='utf-8') as f:
                self.textEdit.setPlainText(f.read())
        except FileNotFoundError:
            pass
        
        self.saveButton = PrimaryPushButton("保存")
        self.cancelButton = PushButton("取消")
        self.saveButton.clicked.connect(self.accept)
        self.cancelButton.clicked.connect(self.reject)
        
        layout = QVBoxLayout()
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
            w.yesButton.setText("保存")
            w.cancelButton.setText("取消")
            w.yesButton = PrimaryPushButton('保存')
            w.cancelButton = PushButton('取消')
            
            if w.exec():
                self.accept()
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
        self.setStyleSheet("background-color: white;")
        self.saved = False
        
        self.textEdit = PlainTextEdit()
        self.textEdit.setPlaceholderText("请输入小组成员姓名，每行一个")
        self.textEdit.setFont(QFont(load_custom_font(), 14))
        
        # 统一设置对话框字体
        self.setFont(QFont(load_custom_font(), 14))
        
        # 尝试读取已保存的小组成员文件
        try:
            selected_group = self.parent().group_ComboBox.currentText()
            if selected_group:
                with open(f"app/resource/group/{selected_group}.ini", 'r', encoding='utf-8') as f:
                    self.textEdit.setPlainText(f.read())
        except (FileNotFoundError, AttributeError):
            pass
        
        self.saveButton = PrimaryPushButton("保存")
        self.cancelButton = PushButton("取消")
        self.saveButton.clicked.connect(self.accept)
        self.cancelButton.clicked.connect(self.reject)
        
        layout = QVBoxLayout()
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
            w.yesButton.setText("保存")
            w.cancelButton.setText("取消")
            w.yesButton = PrimaryPushButton('保存')
            w.cancelButton = PushButton('取消')
            
            if w.exec():
                self.accept()
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
        self.addGroup(FIF.ADD_TO, "设置班级", "点击按钮设置班级名称", self.class_Button)
        self.addGroup(FIF.EDUCATION, "选择班级", "选择一个需要设置学生姓名的班级", self.class_comboBox)
        self.addGroup(FIF.PEOPLE, "设置班级名单", "点击按钮设置学生姓名", self.student_Button)
        self.addGroup(FIF.PEOPLE, "设置小组", "点击按钮设置小组名单", self.group_Button)
        self.addGroup(FIF.EDUCATION, "选择小组", "选择一个需要修改成员的小组", self.group_ComboBox)
        self.addGroup(FIF.EDUCATION, "设置小组成员", "点击按钮设置该小组成员的姓名", self.group_student_Button)
        
        # 程序启动时自动加载小组名称
        try:
            if os.path.exists("app/resource/class/group.ini"):
                with open("app/resource/class/group.ini", 'r', encoding='utf-8') as f:
                    groups = [line.strip() for line in f.read().split('\n') if line.strip()]
                    self.group_ComboBox.clear()
                    self.group_ComboBox.addItems(groups)
        except Exception as e:
            logger.error(f"加载小组名称失败: {str(e)}")
            
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
                    logger.info("班级名单保存成功！")
                    Flyout.create(
                        icon=InfoBarIcon.SUCCESS,
                        title='保存成功',
                        content="班级名单已成功保存！",
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
                    
                    logger.info(f"学生名单保存成功！班级: {selected_class}")
                    Flyout.create(
                        icon=InfoBarIcon.SUCCESS,
                        title='保存成功',
                        content=f"{selected_class} ->学生名单已成功保存！",
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
                    
    def show_group_dialog(self):
        dialog = GroupInputDialog(self)
        if dialog.exec():
            group_text = dialog.getText()
            if group_text:
                try:
                    groups = [line.strip() for line in group_text.split('\n') if line.strip()]
                    
                    # 确保group目录存在
                    os.makedirs("app/resource/class", exist_ok=True)
                        
                    # 保存到小组名称.ini
                    group_file = f"app/resource/class/group.ini"
                    with open(group_file, 'w', encoding='utf-8') as f:
                        f.write('\n'.join(groups))
                    
                    # 更新下拉框
                    self.group_ComboBox.clear()
                    self.group_ComboBox.addItems(groups)
                    logger.info(f"小组名单保存成功！")
                    Flyout.create(
                        icon=InfoBarIcon.SUCCESS,
                        title='保存成功',
                        content=f"小组名单已成功保存！",
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
                        group_file = f"app/resource/group/{selected_group}.ini"
                        with open(group_file, 'w', encoding='utf-8') as f:
                            f.write('\n'.join(group_students))

                        logger.info(f"{selected_group} ->小组成员名单保存成功！")
                        Flyout.create(
                            icon=InfoBarIcon.SUCCESS,
                            title='保存成功',
                            content=f"{selected_group} ->小组成员名单已成功保存！",
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