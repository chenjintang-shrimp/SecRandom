from math import e
from qfluentwidgets import *
from qfluentwidgets import FluentIcon as FIF
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

import os
import json
from loguru import logger

from app.common.config import get_theme_icon, load_custom_font, is_dark_theme

is_dark = not is_dark_theme(qconfig)

class list_SettinsCard(GroupHeaderCardWidget):
    refresh_signal = pyqtSignal()
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("抽人名单")
        self.setBorderRadius(8)
        self.settings_file = "app/Settings/Settings.json"

        self.class_Button = PushButton("设置班级名称")
        self.class_Button.clicked.connect(self.show_class_dialog)
        self.class_Button.setFont(QFont(load_custom_font(), 12))
        
        self.class_comboBox = ComboBox()
        self.class_comboBox.setFixedWidth(250)
        self.class_comboBox.setPlaceholderText("选择一个需要设置名单的班级")
        self.class_comboBox.addItems([])
        self.class_comboBox.setFont(QFont(load_custom_font(), 12))
        self.class_comboBox.currentIndexChanged.connect(lambda: self.refresh_signal.emit())

        self.student_Button = PushButton("设置班级名单")
        self.student_Button.clicked.connect(self.show_student_dialog)
        self.student_Button.setFont(QFont(load_custom_font(), 12))

        self.gender_Button = PushButton("设置学生性别")
        self.gender_Button.clicked.connect(self.show_gender_dialog)
        self.gender_Button.setFont(QFont(load_custom_font(), 12))

        self.group_Button = PushButton("设置学生小组")
        self.group_Button.clicked.connect(self.show_group_dialog)
        self.group_Button.setFont(QFont(load_custom_font(), 12))
        
        try:
            list_folder = "app/resource/list"
            if os.path.exists(list_folder) and os.path.isdir(list_folder):
                files = os.listdir(list_folder)
                classes = []
                for file in files:
                    if file.endswith('.json'):
                        class_name = os.path.splitext(file)[0]
                        classes.append(class_name)
                
                self.class_comboBox.clear()
                self.class_comboBox.addItems(classes)
        except Exception as e:
            logger.error(f"加载班级名称失败: {str(e)}")

        # 添加组件到分组中
        self.addGroup(get_theme_icon("ic_fluent_class_20_filled"), "设置班级", "点击按钮设置班级名称", self.class_Button)
        self.addGroup(get_theme_icon("ic_fluent_multiselect_ltr_20_filled"), "选择班级", "选择一个需要设置学生姓名的班级", self.class_comboBox)
        self.addGroup(get_theme_icon("ic_fluent_people_list_20_filled"), "设置班级名单", "点击按钮设置学生姓名", self.student_Button)
        self.addGroup(get_theme_icon("ic_fluent_person_pill_20_filled"), "设置学生性别", "点击按钮设置学生性别", self.gender_Button)
        self.addGroup(get_theme_icon("ic_fluent_group_20_filled"), "设置小组", "点击按钮设置小组名单", self.group_Button)

        # 创建表格
        self.table = TableWidget(self)
        self.table.setBorderVisible(True)
        self.table.setBorderRadius(8)
        self.table.setWordWrap(False)
        self.table.setColumnCount(4)
        self.table.setEditTriggers(TableWidget.NoEditTriggers)
        self.table.setSortingEnabled(True)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.verticalHeader().hide()
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setHorizontalHeaderLabels(['学号', '姓名', '性别', '所处小组'])
        self.show_table()
        self.refresh_signal.connect(self.show_table)
        # 布局
        self.layout().addWidget(self.table)

    def show_table(self):
        class_name = self.class_comboBox.currentText()
        # 获取是否存在学生
        if os.path.exists(f"app/resource/list/{class_name}.json"):
            with open(f"app/resource/list/{class_name}.json", 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            data = []

        if not class_name:
            self.student_Button.setEnabled(False)
            self.gender_Button.setEnabled(False)
            self.group_Button.setEnabled(False)
            self.class_comboBox.setPlaceholderText("选择一个需要设置名单的班级")
        elif not data:
            self.student_Button.setEnabled(True)
            self.gender_Button.setEnabled(False)
            self.group_Button.setEnabled(False)
        else:
            self.student_Button.setEnabled(True)
            self.gender_Button.setEnabled(True)
            self.group_Button.setEnabled(True)

        if class_name and (not data):
            self.table.setRowCount(0)
            self.table.setHorizontalHeaderLabels([])
            return

        if class_name:
            try:
                with open(f"app/resource/list/{class_name}.json", 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.table.setRowCount(len(data))
                self.table.clearContents()
                
                # 计算最大ID位数
                max_digits = max(len(str(info['id'])) for info in data.values())
                
                self.table.setSortingEnabled(False)
                for i, (name, info) in enumerate(data.items()):
                    self.table.setItem(i, 0, QTableWidgetItem(str(info['id']).zfill(max_digits)))
                    self.table.setItem(i, 1, QTableWidgetItem(name.replace('【', '').replace('】', '')))
                    self.table.setItem(i, 2, QTableWidgetItem(info['gender']))
                    self.table.setItem(i, 3, QTableWidgetItem(info['group']))
                    for j in range(4):
                        item = self.table.item(i, j)
                        if item:
                            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                            item.setFont(QFont(load_custom_font(), 12))
                self.table.setHorizontalHeaderLabels(['学号', '姓名', '性别', '所处小组'])
                self.table.setSortingEnabled(True)
            except FileNotFoundError:
                self.table.setRowCount(0)
                self.table.setHorizontalHeaderLabels([])
                logger.error(f"班级文件 '{class_name}.json' 不存在")
            except json.JSONDecodeError:
                self.table.setRowCount(0)
                self.table.setHorizontalHeaderLabels([])
                logger.error(f"班级文件 '{class_name}.json' 格式错误")
            except Exception as e:
                self.table.setRowCount(0)
                self.table.setHorizontalHeaderLabels([])
                logger.error(f"显示表格时出错: {str(e)}")
        else:
            self.table.setRowCount(0)
            self.table.setHorizontalHeaderLabels([])
            logger.error("未选择班级")
            
    def show_class_dialog(self):
        dialog = ClassInputDialog(self)
        if dialog.exec():
            class_text = dialog.getText()
            try:
                classes = [line.strip() for line in class_text.split('\n') if line.strip()]
                
                # 获取当前所有班级文件
                list_folder = "app/resource/list"
                existing_classes = []
                if os.path.exists(list_folder):
                    existing_classes = [f.split('.')[0] for f in os.listdir(list_folder) if f.endswith('.json')]
                
                # 删除不再需要的班级文件
                for existing_class in existing_classes:
                    if existing_class not in classes:
                        class_file = f"app/resource/list/{existing_class}.json"
                        history_file = f"app/resource/history/{existing_class}.json"
                        try:
                            os.remove(class_file)
                            logger.info(f"已删除班级文件: {class_file}")
                            # 删除对应的历史记录文件
                            if os.path.exists(f"app/resource/history/{existing_class}.json"):
                                os.remove(history_file)
                                logger.info(f"已删除历史记录文件: {history_file}")
                        except Exception as e:
                            logger.error(f"删除文件失败: {class_file}或{history_file}, 错误: {str(e)}")

                os.makedirs("app/resource/list", exist_ok=True)
                
                for class_name in classes:
                    class_file = f"app/resource/list/{class_name}.json"
                    if not os.path.exists(class_file):
                        with open(class_file, 'w', encoding='utf-8') as f:
                            basic_structure = {
                                "示例学生": {
                                    "id": 1,
                                    "gender": "男",
                                    "group": "第一小组",
                                    "exist": True
                                }
                            }
                            json.dump(basic_structure, f, ensure_ascii=False, indent=4)

                self.class_comboBox.clear()
                self.class_comboBox.addItems(classes)
                self.refresh_signal.emit()
                logger.info("班级名单保存成功！")
            except Exception as e:
                logger.error(f"保存失败: {str(e)}")
    
    def show_student_dialog(self):
        dialog = StudentInputDialog(self)
        if dialog.exec():
            student_text = dialog.getText()
            selected_class = self.class_comboBox.currentText()
            if selected_class:
                try:
                    students = [line.strip() for line in student_text.split('\n') if line.strip()]
                    
                    os.makedirs("app/resource/list", exist_ok=True)
                    
                    student_file = f"app/resource/list/{selected_class}.json"
                    student_data = {}
                    
                    if os.path.exists(student_file):
                        with open(student_file, 'r', encoding='utf-8') as f:
                            student_data = json.load(f)
                    
                    # 先删除不在新名单中的学生
                    existing_students = {name.replace('【', '').replace('】', '') for name in student_data.keys()}
                    new_students = {student.strip().replace('【', '').replace('】', '') for student in students if student.strip()}
                    for student_to_remove in existing_students - new_students:
                        del student_data[student_to_remove]
                    
                    # 更新或添加新学生
                    # 重新生成学生顺序，确保按输入顺序存储
                    new_student_data = {}
                    for idx, student in enumerate(students, start=1):
                        student_name = student.strip()
                        exist_status = False if '【' in student_name and '】' in student_name else True
                        # 确保保留原有的性别和小组信息
                        cleaned_name = student_name.replace('【', '').replace('】', '')
                        if cleaned_name in {k.replace('【', '').replace('】', '') for k in student_data.keys()}: 
                            original_info = next((student_data[k] for k in student_data if k.replace('【', '').replace('】', '') == cleaned_name), {})
                        else:
                            original_info = {}
                        new_student_data[student_name] = {
                            "id": idx,
                            "exist": exist_status,
                            "gender": original_info.get("gender", ""),
                            "group": original_info.get("group", "")
                        }
                    student_data = new_student_data
                    
                    with open(student_file, 'w', encoding='utf-8') as f:
                        json.dump(student_data, f, ensure_ascii=False, indent=4)
                    
                    self.refresh_signal.emit()
                    logger.info(f"学生名单保存成功！")
                except Exception as e:
                    logger.error(f"保存失败: {str(e)}")

    def show_gender_dialog(self):
        dialog = GenderInputDialog(self)
        if dialog.exec():
            gender_text = dialog.getText()
            class_name = self.class_comboBox.currentText()
            if class_name:
                try:
                    genders = [line.strip() for line in gender_text.split('\n') if line.strip()]
                    
                    os.makedirs("app/resource/list", exist_ok=True)

                    student_file = f"app/resource/list/{class_name}.json"
                    student_data = {}
                    
                    if os.path.exists(student_file):
                        with open(student_file, 'r', encoding='utf-8') as f:
                            
                            student_data = json.load(f)
                    
                    for idx, gender_name in enumerate(genders, start=1):
                        gender_name = gender_name.strip()
                        for student_name in student_data:
                            if student_data[student_name]["id"] == idx:
                                student_data[student_name]["gender"] = gender_name
                    
                    with open(student_file, 'w', encoding='utf-8') as f:
                        json.dump(student_data, f, ensure_ascii=False, indent=4)
                    
                    self.refresh_signal.emit()
                    logger.info(f"学生对应的性别已成功保存！")
                except Exception as e:
                    logger.error(f"保存失败: {str(e)}")
                    
    def show_group_dialog(self):
        dialog = GroupInputDialog(self)
        if dialog.exec():
            group_text = dialog.getText()
            class_name = self.class_comboBox.currentText()
            if class_name:
                try:
                    groups = [line.strip() for line in group_text.split('\n') if line.strip()]
                    
                    os.makedirs("app/resource/list", exist_ok=True)

                    student_file = f"app/resource/list/{class_name}.json"
                    student_data = {}
                    
                    if os.path.exists(student_file):
                        with open(student_file, 'r', encoding='utf-8') as f:
                            student_data = json.load(f)
                    
                    for idx, group_name in enumerate(groups, start=1):
                        group_name = group_name.strip()
                        for student_name in student_data:
                            if student_data[student_name]["id"] == idx:
                                student_data[student_name]["group"] = group_name
                    
                    with open(student_file, 'w', encoding='utf-8') as f:
                        json.dump(student_data, f, ensure_ascii=False, indent=4)
                    
                    self.refresh_signal.emit()
                    logger.info(f"学生对应的小组名单已成功保存！")
                except Exception as e:
                    logger.error(f"保存失败: {str(e)}")



class ClassInputDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("输入班级名称")
        self.setFixedSize(400, 300)
        self.saved = False
        
        self.text_label = BodyLabel('请输入班级名称，每行一个')
        self.text_label.setFont(QFont(load_custom_font(), 12))

        self.update_theme_style()
        qconfig.themeChanged.connect(self.update_theme_style)
        
        self.textEdit = PlainTextEdit()
        self.textEdit.setPlaceholderText("请输入班级名称，每行一个")
        self.textEdit.setFont(QFont(load_custom_font(), 12))
        
        self.setFont(QFont(load_custom_font(), 12))

        try:
            list_folder = "app/resource/list"
            if os.path.exists(list_folder) and os.path.isdir(list_folder):
                files = os.listdir(list_folder)
                classes = []
                for file in files:
                    if file.endswith('.json'):
                        class_name = os.path.splitext(file)[0]
                        classes.append(class_name)
                
                self.textEdit.setPlainText("\n".join(classes))
        except Exception as e:
            logger.error(f"加载班级名称失败: {str(e)}")

        self.saveButton = PrimaryPushButton("保存")
        self.cancelButton = PushButton("取消")
        self.saveButton.clicked.connect(self.accept)
        self.cancelButton.clicked.connect(self.reject)
        self.saveButton.setFont(QFont(load_custom_font(), 12))
        self.cancelButton.setFont(QFont(load_custom_font(), 12))
        
        layout = QVBoxLayout()
        layout.addWidget(self.text_label)
        layout.addWidget(self.textEdit)
        
        buttonLayout = QHBoxLayout()
        buttonLayout.addStretch(1)
        buttonLayout.addWidget(self.cancelButton)
        buttonLayout.addWidget(self.saveButton)
        
        layout.addLayout(buttonLayout)
        self.setLayout(layout)
    
    def update_theme_style(self):
        if is_dark:
            self.setStyleSheet("""
                QDialog, QDialog * {
                    color: black;
                    background-color: white;
                }
            """)
        else:
            self.setStyleSheet("""
                QDialog, QDialog * {
                    color: white;
                    background-color: black;
                }
            """)
        
    def closeEvent(self, event):
        if not self.saved:
            w = Dialog('未保存内容', '确定要关闭吗？', self)
            w.setFont(QFont(load_custom_font(), 12))
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
        self.text_label.setFont(QFont(load_custom_font(), 12))

        self.update_theme_style()
        qconfig.themeChanged.connect(self.update_theme_style)
        
        self.textEdit = PlainTextEdit()
        self.textEdit.setPlaceholderText("请输入学生姓名，每行一个")
        self.textEdit.setFont(QFont(load_custom_font(), 12))
        
        self.setFont(QFont(load_custom_font(), 12))
        
        class_name = self.parent().class_comboBox.currentText()
        try:
            with open(f"app/resource/list/{class_name}.json", 'r', encoding='utf-8') as f:
                file_content = f.read()
                if not file_content.strip():
                    # 处理空文件情况
                    logger.warning(f"JSON文件为空: app/resource/list/{class_name}.json")
                    return
                
                try:
                    data = json.loads(file_content)
                    if not isinstance(data, dict):
                        raise ValueError("JSON格式不正确，应为字典类型")
                    
                    name_list = []
                    for student_name in data:
                        name_list.append(student_name)
                    self.textEdit.setPlainText("\n".join(name_list))
                except json.JSONDecodeError as e:
                    logger.error(f"JSON解析错误: {str(e)}")
                except ValueError as e:
                    logger.error(f"数据格式错误: {str(e)}")
        except FileNotFoundError:
            logger.error(f"文件未找到: app/resource/list/{class_name}.json")
        except json.JSONDecodeError:
            logger.error("JSON文件格式错误，请检查文件内容")
        
        self.saveButton = PrimaryPushButton("保存")
        self.cancelButton = PushButton("取消")
        self.saveButton.clicked.connect(self.accept)
        self.cancelButton.clicked.connect(self.reject)
        self.saveButton.setFont(QFont(load_custom_font(), 12))
        self.cancelButton.setFont(QFont(load_custom_font(), 12))
        
        layout = QVBoxLayout()
        layout.addWidget(self.text_label)
        layout.addWidget(self.textEdit)
        
        buttonLayout = QHBoxLayout()
        buttonLayout.addStretch(1)
        buttonLayout.addWidget(self.cancelButton)
        buttonLayout.addWidget(self.saveButton)
        
        layout.addLayout(buttonLayout)
        self.setLayout(layout)

    def update_theme_style(self):
        if is_dark:
            self.setStyleSheet("""
                QDialog, QDialog * {
                    color: black;
                    background-color: white;
                }
            """)
        else:
            self.setStyleSheet("""
                QDialog, QDialog * {
                    color: white;
                    background-color: black;
                }
            """)
        
    def closeEvent(self, event):
        if not self.saved:
            w = Dialog('未保存内容', '确定要关闭吗？', self)
            w.setFont(QFont(load_custom_font(), 12))
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

class GenderInputDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("输入每个人对应的性别")
        self.setFixedSize(400, 400)
        self.saved = False

        self.text_label = BodyLabel('请输入每个人对应的性别，每行一个\n例:男 或 女(其它的?自己试一试吧)\n注:尽量在表格中复制后直接粘贴')
        self.text_label.setFont(QFont(load_custom_font(), 12))

        self.update_theme_style()
        qconfig.themeChanged.connect(self.update_theme_style)

        self.textEdit = PlainTextEdit()
        self.textEdit.setPlaceholderText("请输入每个人对应的性别，每行一个")
        self.textEdit.setFont(QFont(load_custom_font(), 12))
        
        # 统一设置对话框字体
        self.setFont(QFont(load_custom_font(), 12))
        
        class_name = self.parent().class_comboBox.currentText()
        # 尝试读取已保存的性别值
        try:
            with open(f"app/resource/list/{class_name}.json", 'r', encoding='utf-8') as f:
                file_content = f.read()
                if not file_content.strip():
                    logger.warning(f"JSON文件为空: app/resource/list/{class_name}.json")
                    return
                data = json.loads(file_content)
                if isinstance(data, dict):
                    gender_list = []
                    # 按id排序后从id为1开始读取
                    sorted_students = sorted(data.values(), key=lambda x: x.get("id", 0))
                    for student in sorted_students:
                        if student.get("id", 0) >= 1:
                            gender_list.append(student.get("gender", ""))
                    self.textEdit.setPlainText("\n".join(gender_list))

        except FileNotFoundError:
            pass
        except json.JSONDecodeError:
            logger.error(f"JSON文件解析错误: {str(e)}")
        
        self.saveButton = PrimaryPushButton("保存")
        self.cancelButton = PushButton("取消")
        self.saveButton.clicked.connect(self.accept)
        self.cancelButton.clicked.connect(self.reject)
        self.saveButton.setFont(QFont(load_custom_font(), 12))
        self.cancelButton.setFont(QFont(load_custom_font(), 12))
        
        layout = QVBoxLayout()
        layout.addWidget(self.text_label)
        layout.addWidget(self.textEdit)
        
        buttonLayout = QHBoxLayout()
        buttonLayout.addStretch(1)
        buttonLayout.addWidget(self.cancelButton)
        buttonLayout.addWidget(self.saveButton)
        
        layout.addLayout(buttonLayout)
        self.setLayout(layout)

    def update_theme_style(self):
        if is_dark:
            self.setStyleSheet("""
                QDialog, QDialog * {
                    color: black;
                    background-color: white;
                }
            """)
        else:
            self.setStyleSheet("""
                QDialog, QDialog * {
                    color: white;
                    background-color: black;
                }
            """)
        
    def closeEvent(self, event):
        if not self.saved:
            w = Dialog('未保存内容', '确定要关闭吗？', self)
            w.setFont(QFont(load_custom_font(), 12))
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

class GroupInputDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("输入每个人对应的小组名称")
        self.setFixedSize(400, 400)
        self.saved = False

        self.text_label = BodyLabel('请输入每个人对应的小组名称，每行一个\n例:第1小组 或 第一小组\n注:尽量在表格中复制后直接粘贴')
        self.text_label.setFont(QFont(load_custom_font(), 12))

        self.update_theme_style()
        qconfig.themeChanged.connect(self.update_theme_style)

        self.textEdit = PlainTextEdit()
        self.textEdit.setPlaceholderText("请输入小组名称，每行一个")
        self.textEdit.setFont(QFont(load_custom_font(), 12))
        
        # 统一设置对话框字体
        self.setFont(QFont(load_custom_font(), 12))
        
        class_name = self.parent().class_comboBox.currentText()
        # 尝试读取已保存的小组值
        try:
            with open(f"app/resource/list/{class_name}.json", 'r', encoding='utf-8') as f:
                file_content = f.read()
                if not file_content.strip():
                    logger.warning(f"JSON文件为空: app/resource/list/{class_name}.json")
                    return
                data = json.loads(file_content)
                if isinstance(data, dict):
                    group_list = []
                    # 按id排序后从id为1开始读取
                    sorted_students = sorted(data.values(), key=lambda x: x.get("id", 0))
                    for student in sorted_students:
                        if student.get("id", 0) >= 1:
                            group_list.append(student.get("group", ""))
                    self.textEdit.setPlainText("\n".join(group_list))

        except FileNotFoundError:
            pass
        except json.JSONDecodeError:
            logger.error("JSON文件格式错误，请检查文件内容")
        
        self.saveButton = PrimaryPushButton("保存")
        self.cancelButton = PushButton("取消")
        self.saveButton.clicked.connect(self.accept)
        self.cancelButton.clicked.connect(self.reject)
        self.saveButton.setFont(QFont(load_custom_font(), 12))
        self.cancelButton.setFont(QFont(load_custom_font(), 12))
        
        layout = QVBoxLayout()
        layout.addWidget(self.text_label)
        layout.addWidget(self.textEdit)
        
        buttonLayout = QHBoxLayout()
        buttonLayout.addStretch(1)
        buttonLayout.addWidget(self.cancelButton)
        buttonLayout.addWidget(self.saveButton)
        
        layout.addLayout(buttonLayout)
        self.setLayout(layout)

    def update_theme_style(self):
        if is_dark:
            self.setStyleSheet("""
                QDialog, QDialog * {
                    color: black;
                    background-color: white;
                }
            """)
        else:
            self.setStyleSheet("""
                QDialog, QDialog * {
                    color: white;
                    background-color: black;
                }
            """)
        
    def closeEvent(self, event):
        if not self.saved:
            w = Dialog('未保存内容', '确定要关闭吗？', self)
            w.setFont(QFont(load_custom_font(), 12))
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
