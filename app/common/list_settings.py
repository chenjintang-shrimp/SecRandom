from math import e
from qfluentwidgets import *
from qfluentwidgets import FluentIcon as FIF
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

import os
import json
from collections import OrderedDict
from pathlib import Path
from loguru import logger
import pandas as pd
from app.common.path_utils import path_manager
from app.common.path_utils import open_file, ensure_dir

from app.common.config import get_theme_icon, load_custom_font, is_dark_theme

is_dark = is_dark_theme(qconfig)

class list_SettinsCard(GroupHeaderCardWidget):
    refresh_signal = pyqtSignal()
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("点名名单")
        self.setBorderRadius(8)
        # 获取应用根目录并构建设置文件路径
        self.settings_file = path_manager.get_settings_path()

        self.class_Button = PushButton("设置班级名称")
        self.class_Button.clicked.connect(self.show_class_dialog)
        self.class_Button.setFont(QFont(load_custom_font(), 12))
        
        self.class_comboBox = ComboBox()
        self.class_comboBox.setPlaceholderText("选择一个需要设置名单的班级")
        self.class_comboBox.addItems([])
        self.class_comboBox.setFont(QFont(load_custom_font(), 12))
        self.class_comboBox.currentIndexChanged.connect(lambda: self.refresh_signal.emit())

        # 快速导入学生名单
        self.import_Button = PushButton("导入学生名单")
        self.import_Button.clicked.connect(self.import_student_list)
        self.import_Button.setFont(QFont(load_custom_font(), 12))

        self.student_Button = PushButton("姓名设置")
        self.student_Button.clicked.connect(self.show_student_dialog)
        self.student_Button.setFont(QFont(load_custom_font(), 12))

        self.gender_Button = PushButton("性别设置")
        self.gender_Button.clicked.connect(self.show_gender_dialog)
        self.gender_Button.setFont(QFont(load_custom_font(), 12))

        self.group_Button = PushButton("小组设置")
        self.group_Button.clicked.connect(self.show_group_dialog)
        self.group_Button.setFont(QFont(load_custom_font(), 12))

        # 导出学生名单
        self.export_Button = PushButton("导出学生名单")
        self.export_Button.clicked.connect(self.export_student_list)
        self.export_Button.setFont(QFont(load_custom_font(), 12))
        
        try:
            # 获取应用根目录并构建列表文件夹路径
            list_folder = path_manager.get_resource_path("list")
            if list_folder.exists() and list_folder.is_dir():
                files = list_folder.iterdir()
                classes = []
                for file in files:
                    if file.suffix == '.json':
                        class_name = file.stem
                        classes.append(class_name)
                
                self.class_comboBox.clear()
                self.class_comboBox.addItems(classes)
        except Exception as e:
            logger.error(f"加载班级名称失败: {str(e)}")

        # 班级管理设置
        self.addGroup(get_theme_icon("ic_fluent_class_20_filled"), "设置班级", "创建或编辑班级名称信息", self.class_Button)
        self.addGroup(get_theme_icon("ic_fluent_multiselect_ltr_20_filled"), "选择班级", "选择要管理学生信息的班级", self.class_comboBox)
        
        # 数据导入设置
        self.addGroup(get_theme_icon("ic_fluent_people_list_20_filled"), "导入学生名单", "从文件批量导入学生信息(将覆盖现有数据)", self.import_Button)
        
        # 学生信息设置
        self.addGroup(get_theme_icon("ic_fluent_people_list_20_filled"), "设置学生姓名", "编辑或添加学生姓名信息", self.student_Button)
        self.addGroup(get_theme_icon("ic_fluent_person_pill_20_filled"), "设置学生性别", "配置学生性别信息", self.gender_Button)
        
        # 小组管理设置
        self.addGroup(get_theme_icon("ic_fluent_group_20_filled"), "设置小组", "创建和管理学生小组分配", self.group_Button)
        
        # 数据导出设置
        self.addGroup(get_theme_icon("ic_fluent_people_list_20_filled"), "导出学生名单", "将当前班级学生信息导出为文件", self.export_Button)

        # 创建表格
        self.table = TableWidget(self)
        self.table.setBorderVisible(True)
        self.table.setBorderRadius(8)
        self.table.setWordWrap(False)
        self.table.setColumnCount(5)
        self.table.setEditTriggers(TableWidget.DoubleClicked)
        self.table.setSortingEnabled(True)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.verticalHeader().hide()
        # 设置表格列宽模式
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)    # 在班级列固定且不可调整
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)  # 学号列拉伸
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)  # 姓名列拉伸
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)  # 性别列拉伸
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)  # 所处小组列拉伸
        # 设置"在班级"列的宽度为较小值
        self.table.horizontalHeader().resizeSection(0, 80)  # 第1列（索引0）宽度设为80
        # 设置表格拉伸最后一列后的剩余空间
        self.table.horizontalHeader().setStretchLastSection(False)
        self.table.setHorizontalHeaderLabels(['在班级', '学号', '姓名', '性别', '所处小组'])
        # 设置第一列表头居中对齐
        self.table.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)
        self.show_table()
        self.refresh_signal.connect(self.show_table)
        self.table.itemChanged.connect(self.save_table_data)
        self.layout().addWidget(self.table)

    # 学生名单导入功能
    def import_student_list(self):
        # 创建导入对话框
        dialog = ImportStudentDialog(self)
        if dialog.exec():
            # 直接获取对话框处理好的数据
            student_data, class_name = dialog.get_processed_data()
            if not class_name or not student_data:
                return

            try:
                # 确保目录存在并写入数据
                student_file = path_manager.get_resource_path('list', f'{class_name}.json')
                ensure_dir(os.path.dirname(student_file))
                with open_file(student_file, 'w', encoding='utf-8') as f:
                    json.dump(student_data, f, ensure_ascii=False, indent=4)

                self.refresh_signal.emit()
                logger.info(f"学生名单导入成功，共导入 {len(student_data)} 条记录")
            except Exception as e:
                logger.error(f"导入失败: {str(e)}")

    # 学生名单导出功能
    def export_student_list(self):
        class_name = self.class_comboBox.currentText()
        if not class_name:
            InfoBar.warning(
                title='导出失败',
                content='请先选择要导出的班级',
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )
            return

        try:
            # 构建学生文件路径
            student_file = path_manager.get_resource_path('list', f'{class_name}.json')
            # 读取学生数据
            with open_file(student_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if not data:
                InfoBar.warning(
                    title='导出失败',
                    content='当前班级没有学生数据',
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=3000,
                    parent=self
                )
                return

            # 转换为DataFrame
            export_data = []
            for name, info in data.items():
                export_data.append({
                    '学号': info['id'],
                    '姓名': name.replace('【', '').replace('】', ''),
                    '性别': info['gender'],
                    '所处小组': info['group']
                })
            
            df = pd.DataFrame(export_data)
            
            # 打开文件保存对话框
            file_path, selected_filter = QFileDialog.getSaveFileName(
                self,
                "保存学生名单",
                f"{class_name}_学生名单",
                "Excel 文件 (*.xlsx);;CSV 文件 (*.csv);;TXT 文件（仅姓名） (*.txt)"
            )
            
            if file_path:
                # 根据选择的格式处理文件扩展名和保存方式
                if "Excel 文件 (*.xlsx)" in selected_filter:
                    if not file_path.endswith('.xlsx'):
                        file_path += '.xlsx'
                    # 保存为xlsx文件
                    df.to_excel(file_path, index=False, engine='openpyxl')
                elif "CSV 文件 (*.csv)" in selected_filter:
                    if not file_path.endswith('.csv'):
                        file_path += '.csv'
                    # 保存为CSV文件
                    df.to_csv(file_path, index=False, encoding='utf-8-sig')
                else:  # TXT格式（仅姓名）
                    if not file_path.endswith('.txt'):
                        file_path += '.txt'
                    # 提取姓名并保存为TXT文件，每行一个姓名
                    with open_file(file_path, 'w', encoding='utf-8') as f:
                        for name in data.keys():
                            # 去除【】符号后写入
                            clean_name = name.replace('【', '').replace('】', '')
                            f.write(f"{clean_name}\n")
                
                InfoBar.success(
                    title='导出成功',
                    content=f'学生名单已导出到: {file_path}',
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=5000,
                    parent=self
                )
                logger.info(f"学生名单导出成功: {file_path}")
                
        except FileNotFoundError:
            logger.error(f"班级文件 '{class_name}.json' 不存在")
            InfoBar.error(
                title='导出失败',
                content='班级文件不存在',
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )
        except json.JSONDecodeError:
            logger.error(f"班级文件 '{class_name}.json' 格式错误")
            InfoBar.error(
                title='导出失败',
                content='班级文件格式错误',
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )
        except Exception as e:
            logger.error(f"导出学生名单时出错: {str(e)}")
            InfoBar.error(
                title='导出失败',
                content=f'导出时出错: {str(e)}',
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )

    def show_table(self):
        class_name = self.class_comboBox.currentText()
        # 获取是否存在学生
        student_file = path_manager.get_resource_path('list', f'{class_name}.json')
        if path_manager.file_exists(student_file):
            with open_file(student_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            data = []

        if not class_name:
            self.student_Button.setEnabled(False)
            self.gender_Button.setEnabled(False)
            self.group_Button.setEnabled(False)
            self.import_Button.setEnabled(False)
            self.export_Button.setEnabled(False)
            self.class_comboBox.setPlaceholderText("选择一个需要设置名单的班级")
        elif not data:
            self.student_Button.setEnabled(True)
            self.gender_Button.setEnabled(False)
            self.group_Button.setEnabled(False)
            self.import_Button.setEnabled(True)
            self.export_Button.setEnabled(False)
        else:
            self.student_Button.setEnabled(True)
            self.gender_Button.setEnabled(True)
            self.group_Button.setEnabled(True)
            self.import_Button.setEnabled(True)
            self.export_Button.setEnabled(True)

        if class_name and (not data):
            self.table.setRowCount(0)
            self.table.setHorizontalHeaderLabels([])
            return

        if class_name:
            try:
                with open_file(student_file, 'r', encoding='utf-8') as f:
                    data = json.load(f, object_pairs_hook=OrderedDict)
                self.table.setRowCount(len(data))
                self.table.clearContents()
                
                # 计算最大ID位数
                max_digits = max(len(str(info['id'])) for info in data.values())
                
                self.table.setSortingEnabled(False)
                self.table.blockSignals(True)
                for i, (name, info) in enumerate(data.items()):
                    # 添加"在班级"勾选框到第一列
                    checkbox = QTableWidgetItem()
                    checkbox.setFlags(checkbox.flags() | Qt.ItemIsUserCheckable)
                    if info.get('exist', True):  # 默认为True，如果不存在exist字段
                        checkbox.setCheckState(Qt.Checked)
                    else:
                        checkbox.setCheckState(Qt.Unchecked)
                    # 设置勾选框居中对齐
                    checkbox.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.table.setItem(i, 0, checkbox)
                    # 设置单元格的勾选框居中
                    self.table.item(i, 0).setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    
                    # 设置其他列数据
                    self.table.setItem(i, 1, QTableWidgetItem(str(info['id']).zfill(max_digits)))
                    self.table.setItem(i, 2, QTableWidgetItem(name.replace('【', '').replace('】', '')))
                    self.table.setItem(i, 3, QTableWidgetItem(info['gender']))
                    self.table.setItem(i, 4, QTableWidgetItem(info['group']))
                    
                    for j in range(5):
                        item = self.table.item(i, j)
                        if item:
                            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                            item.setFont(QFont(load_custom_font(), 12))
                            # 学号列不可编辑，姓名列可编辑
                            if j == 1:  # 学号列(现在在索引1)不可编辑
                                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.table.setHorizontalHeaderLabels(['在班级', '学号', '姓名', '性别', '所处小组'])
                self.table.blockSignals(False)
                self.table.setSortingEnabled(True)
                # 重新设置列宽模式，保持第1列固定宽度，其他列拉伸
                self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)    # 在班级列固定且不可调整
                self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)  # 学号列拉伸
                self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)  # 姓名列拉伸
                self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)  # 性别列拉伸
                self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)  # 所处小组列拉伸
                # 重新设置"在班级"列的宽度
                self.table.horizontalHeader().resizeSection(0, 80)  # 第1列（索引0）宽度设为80
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
                list_folder = path_manager.get_resource_path('list', '')
                existing_classes = []
                if path_manager.file_exists(list_folder):
                    existing_classes = [os.path.splitext(f)[0] for f in os.listdir(list_folder) if f.endswith('.json')]
                
                # 删除不再需要的班级文件
                for existing_class in existing_classes:
                    if existing_class not in classes:
                        class_file = path_manager.get_resource_path('list', f'{existing_class}.json')
                        history_file = path_manager.get_resource_path('history', f'{existing_class}.json')
                        try:
                            class_file.unlink()
                            logger.info(f"已删除班级文件: {class_file}")
                            # 删除对应的历史记录文件
                            if history_file.exists():
                                history_file.unlink()
                                logger.info(f"已删除历史记录文件: {history_file}")
                        except Exception as e:
                            logger.error(f"删除文件失败: {class_file}或{history_file}, 错误: {str(e)}")

                ensure_dir(list_folder)
                
                for class_name in classes:
                    class_file = path_manager.get_resource_path('list', f'{class_name}.json')
                    if not path_manager.file_exists(class_file):
                        with open_file(class_file, 'w', encoding='utf-8') as f:
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
                    
                    list_folder = path_manager.get_resource_path('list', '')
                    ensure_dir(list_folder)
                    
                    student_file = path_manager.get_resource_path('list', f'{selected_class}.json')
                    student_data = OrderedDict()
                    
                    if path_manager.file_exists(student_file):
                        with open_file(student_file, 'r', encoding='utf-8') as f:
                            student_data = json.load(f, object_pairs_hook=OrderedDict)
                    
                    # 先删除不在新名单中的学生
                    # 保留原始键名处理特殊字符
                    existing_students = {name for name in student_data.keys()}
                    new_students_cleaned = {student.strip().replace('【', '').replace('】', '') for student in students if student.strip()}
                    
                    # 找出需要删除的学生（原始键名）
                    students_to_remove = []
                    for name in existing_students:
                        cleaned_name = name.replace('【', '').replace('】', '')
                        if cleaned_name not in new_students_cleaned:
                            students_to_remove.append(name)
                    
                    for student_to_remove in students_to_remove:
                        del student_data[student_to_remove]
                    
                    # 更新或添加新学生，保持原有学号和顺序
                    # 创建一个临时有序字典来存储所有学生信息
                    temp_student_data = OrderedDict()
                    
                    # 首先，将所有现有学生添加到临时字典
                    for name, info in student_data.items():
                        temp_student_data[name] = info
                    
                    # 处理新输入的学生
                    for idx, student in enumerate(students, start=1):
                        student_name = student.strip()
                        # 去掉输入中的【】符号（如果用户输入了）
                        clean_name = student_name.replace('【', '').replace('】', '')
                        
                        # 检查学生是否已存在
                        existing_key = None
                        for key in temp_student_data.keys():
                            if key.replace('【', '').replace('】', '') == clean_name:
                                existing_key = key
                                break
                        
                        if existing_key:
                            # 学生已存在，保留原有信息（包括学号）
                            original_info = temp_student_data[existing_key]
                            exist_status = original_info.get("exist", True)
                            original_key = existing_key
                        else:
                            # 新学生，找到最小的可用学号
                            used_ids = {info['id'] for info in temp_student_data.values()}
                            new_id = 1
                            while new_id in used_ids:
                                new_id += 1
                            
                            original_info = {"id": new_id}
                            exist_status = True
                            original_key = ""
                        
                        # 根据 exist 状态决定是否在名称两侧加上【】符号
                        # 检查原本的名称是否已经包含【】符号
                        original_has_brackets = '【' in original_key and '】' in original_key if original_key else False
                        # 只有当 exist 状态与括号状态不一致时才更改
                        if not exist_status and not original_has_brackets:
                            # 不是否在班级但名称没有括号，添加括号
                            display_name = f"【{clean_name}】"
                        elif exist_status and original_has_brackets:
                            # 是否在班级但名称有括号，移除括号
                            display_name = clean_name
                        else:
                            # 状态一致，保持原有名称
                            display_name = original_key if original_key else clean_name
                        
                        # 如果键名发生变化，需要更新字典
                        if display_name != original_key and original_key:
                            # 删除旧键
                            del temp_student_data[original_key]
                        
                        # 更新学生信息
                        temp_student_data[display_name] = {
                            "id": original_info.get("id", idx),
                            "exist": exist_status,
                            "gender": original_info.get("gender", ""),
                            "group": original_info.get("group", "")
                        }
                    
                    # 根据学号排序学生
                    sorted_students = sorted(temp_student_data.items(), key=lambda x: x[1]['id'])
                    
                    # 创建排序后的学生数据有序字典
                    student_data = OrderedDict()
                    for name, info in sorted_students:
                        student_data[name] = info
                    
                    with open_file(student_file, 'w', encoding='utf-8') as f:
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
                    
                    list_folder = path_manager.get_resource_path('list', '')
                    ensure_dir(list_folder)

                    student_file = path_manager.get_resource_path('list', f'{class_name}.json')
                    student_data = OrderedDict()
                    
                    if path_manager.file_exists(student_file):
                        with open_file(student_file, 'r', encoding='utf-8') as f:
                            student_data = json.load(f, object_pairs_hook=OrderedDict)
                    
                    for idx, gender_name in enumerate(genders, start=1):
                        gender_name = gender_name.strip()
                        for student_name in student_data:
                            if student_data[student_name]["id"] == idx:
                                student_data[student_name]["gender"] = gender_name
                    
                    with open_file(student_file, 'w', encoding='utf-8') as f:
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
                    
                    list_folder = path_manager.get_resource_path('list', '')
                    ensure_dir(list_folder)

                    student_file = path_manager.get_resource_path('list', f'{class_name}.json')
                    student_data = OrderedDict()
                    
                    if path_manager.file_exists(student_file):
                        with open_file(student_file, 'r', encoding='utf-8') as f:
                            student_data = json.load(f, object_pairs_hook=OrderedDict)
                    
                    for idx, group_name in enumerate(groups, start=1):
                        group_name = group_name.strip()
                        for student_name in student_data:
                            if student_data[student_name]["id"] == idx:
                                student_data[student_name]["group"] = group_name
                    
                    with open_file(student_file, 'w', encoding='utf-8') as f:
                        json.dump(student_data, f, ensure_ascii=False, indent=4)
                    
                    self.refresh_signal.emit()
                    logger.info(f"学生对应的小组名单已成功保存！")
                except Exception as e:
                    logger.error(f"保存失败: {str(e)}")
                    
    # 保存表格编辑的数据
    def save_table_data(self, item):
        # 获取当前选中的班级
        class_name = self.class_comboBox.currentText()
        if not class_name:
            return
        
        row = item.row()
        col = item.column()
        
        # 获取当前行的学号（索引1）和姓名（索引2）
        id_item = self.table.item(row, 1)
        name_item = self.table.item(row, 2)
        if not id_item or not name_item:
            return
        student_id = id_item.text()
        student_name = name_item.text()
        
        # 加载当前班级的学生数据
        student_file = path_manager.get_resource_path('list', f'{class_name}.json')
        try:
            with open_file(student_file, 'r', encoding='utf-8') as f:
                student_data = json.load(f, object_pairs_hook=OrderedDict)
        except Exception as e:
            logger.error(f"加载学生数据失败: {str(e)}")
            return
        
        # 通过学号找到对应的学生键
        matched_key = None
        for key, value in student_data.items():
            # 确保学号比较时类型一致，处理字符串和整数类型的比较，并去除前导零
            stored_id = value.get('id')
            # 去除前导零后比较
            if str(stored_id).lstrip('0') == str(student_id).lstrip('0') or str(stored_id) == str(student_id):
                matched_key = key
                break
        if not matched_key:
            logger.error(f"未找到学号为 {student_id} 的学生，学生姓名: {student_name}")
            return
        
        # 根据列索引更新相应的字段
        new_value = item.text()
        if col == 2:  # 姓名列
            # 获取当前学生的exist状态
            exist_status = student_data[matched_key].get('exist', True)
            
            # 检查原始键名中是否包含【】符号
            has_brackets = '【' in matched_key and '】' in matched_key
            
            # 获取原始姓名（不包含【】符号）
            original_name = matched_key.replace('【', '').replace('】', '')
            
            # 根据exist状态决定是否在名称两侧加上【】符号
            if not exist_status:
                # 不在班级，名称加上【】符号
                new_key = f"【{new_value}】"
            else:
                # 在班级，名称不加【】符号
                new_key = new_value
            
            # 如果只是姓名内容没有变化，不需要更新
            if new_key.replace('【', '').replace('】', '') == original_name:
                return
            
            # 只有当键名需要改变时才执行
            if new_key != matched_key:
                # 创建一个新的有序字典来保持原始顺序
                new_student_data = OrderedDict()
                
                # 遍历原始数据，保持顺序
                for key, value in student_data.items():
                    if key == matched_key:
                        # 使用新键而不是旧键
                        new_student_data[new_key] = value
                    else:
                        # 保持其他键不变
                        new_student_data[key] = value
                
                # 更新原始数据
                student_data = new_student_data
        elif col == 3:  # 性别列
            student_data[matched_key]['gender'] = new_value
        elif col == 4:  # 小组列
            student_data[matched_key]['group'] = new_value
        elif col == 0:  # "是否在班级"勾选框列
            # 获取勾选框状态
            checkbox_item = self.table.item(row, 0)
            if checkbox_item:
                is_checked = checkbox_item.checkState() == Qt.Checked
                student_data[matched_key]['exist'] = is_checked
                
                # 如果 exist 状态改变，需要更新键名（添加或移除【】符号）
                clean_name = matched_key.replace('【', '').replace('】', '')
                new_key = f"【{clean_name}】" if not is_checked else clean_name
                
                # 只有当键名需要改变时才执行
                if new_key != matched_key:
                    # 创建一个新的有序字典来保持原始顺序
                    new_student_data = OrderedDict()
                    
                    # 遍历原始数据，保持顺序
                    for key, value in student_data.items():
                        if key == matched_key:
                            # 使用新键而不是旧键
                            new_student_data[new_key] = value
                        else:
                            # 保持其他键不变
                            new_student_data[key] = value
                    
                    # 更新原始数据
                    student_data = new_student_data
        # 学号列（col=1）不可编辑，所以不需要处理
        
        # 保存更新后的数据
        try:
            with open_file(student_file, 'w', encoding='utf-8') as f:
                json.dump(student_data, f, ensure_ascii=False, indent=4)
            logger.info(f"学生数据更新成功: {student_name}")
            # 保存成功后设置后4列拉伸铺满表格宽度
            self.table.blockSignals(True)
            for i in range(1, 5):
                self.table.horizontalHeader().setSectionResizeMode(i, QHeaderView.Stretch)
            self.table.blockSignals(False)
        except Exception as e:
            logger.error(f"保存学生数据失败: {str(e)}")
            # 如果保存失败，恢复原来的值
            if col == 2:  # 姓名列
                # 恢复原始姓名（保持原始的【】符号状态）
                item.setText(str(matched_key) if matched_key else student_name)
            else:
                original_value = ""
                if matched_key:
                    original_value = student_data[matched_key]['gender'] if col == 3 else student_data[matched_key]['group'] if col == 4 else ""
                item.setText(str(original_value))

class ImportStudentDialog(QDialog):
    # 学生名单导入对话框
    def __init__(self, parent=None):
        super().__init__(parent)
        # 设置无边框但可调整大小的窗口样式并解决屏幕设置冲突 
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self.setWindowTitle("导入学生名单")
        self.setMinimumSize(600, 535)  # 设置最小大小而不是固定大小
        self.saved = False
        self.dragging = False
        self.drag_position = None
        
        # 确保不设置子窗口的屏幕属性
        if parent is not None:
            self.setParent(parent)
        
        # 创建自定义标题栏
        self.title_bar = QWidget()
        self.title_bar.setObjectName("CustomTitleBar")
        self.title_bar.setFixedHeight(35)
        
        # 标题栏布局
        title_layout = QHBoxLayout(self.title_bar)
        title_layout.setContentsMargins(10, 0, 10, 0)
        
        # 窗口标题
        self.title_label = QLabel("导入学生名单")
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

        
        self.dragging = False
        self.drag_position = None

        # 确保不设置子窗口的屏幕属性
        if parent is not None:
            self.setParent(parent)
        
        # 创建自定义标题栏
        self.title_bar = QWidget()
        self.title_bar.setObjectName("CustomTitleBar")
        self.title_bar.setFixedHeight(35)
        
        # 标题栏布局
        title_layout = QHBoxLayout(self.title_bar)
        title_layout.setContentsMargins(10, 0, 10, 0)
        
        # 窗口标题
        self.title_label = QLabel("密码验证")
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

        self.file_path = None
        self.file_type = 'excel'
        self.column_mapping = {'学号': -1, '姓名': -1, '性别': -1, '小组': -1}
        self.include_columns = {'性别': True, '小组': True}
        # 初始化处理后的数据和班级名称
        self.processed_data = None
        self.class_name = None

        self.update_theme_style()
        qconfig.themeChanged.connect(self.update_theme_style)
        self.init_ui()

    def mousePressEvent(self, event):
        # 窗口拖动功能，按住标题栏就能移动
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
        # 主题样式更新，现在包含自定义标题栏
        colors = {'text': '#F5F5F5', 'bg': '#111116', 'title_bg': '#2D2D2D'} if is_dark else {'text': '#111116', 'bg': '#F5F5F5', 'title_bg': '#E0E0E0'}
        self.setStyleSheet(f"""
            QDialog, QDialog * {{
                color: {colors['text']};
                background-color: {colors['bg']};
            }}
            #CustomTitleBar {{
                background-color: {colors['title_bg']};
            }}
            #TitleLabel {{
                color: {colors['text']};
                font-weight: bold; padding: 5px;
                background-color: transparent;
            }}
            #CloseButton {{ 
                background-color: transparent; 
                color: {colors['text']}; 
                border-radius: 4px; 
                font-weight: bold; 
            }}
            #CloseButton:hover {{
                background-color: #ff4d4d;
                color: white;
            }}
        """)

        # 设置标题栏颜色以匹配背景色（仅Windows系统）
        if os.name == 'nt':
            try:
                import ctypes
                # 修复参数类型错误，现在要把窗口ID转成整数才行
                hwnd = int(self.winId())  # 转换为整数句柄
                
                # 颜色格式要改成ARGB才行，添加透明度通道
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

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 添加自定义标题栏
        layout.addWidget(self.title_bar)

        # 创建内容区域布局
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(10, 10, 10, 10)
        content_layout.setSpacing(10)

        # 文件选择区域
        file_layout = QHBoxLayout()
        self.file_path_edit = LineEdit()
        self.file_path_edit.setReadOnly(True)
        browse_btn = PrimaryPushButton("浏览文件")
        browse_btn.setFont(QFont(load_custom_font(), 12))
        browse_btn.clicked.connect(self.browse_file)
        file_layout.addWidget(self.file_path_edit)
        file_layout.addWidget(browse_btn)
        content_layout.addLayout(file_layout)

        # 文件类型选择
        type_layout = QHBoxLayout()
        type_label = BodyLabel("文件类型：")
        type_label.setFont(QFont(load_custom_font(), 12))
        self.type_combo = ComboBox()
        self.type_combo.setFont(QFont(load_custom_font(), 12))
        self.type_combo.addItems(["Excel文件 (*.xlsx)", "CSV文件 (*.csv)", "NamePicker < 软件版本3.0 格式 CSV 文件 (*.csv)"])
        self.type_combo.currentIndexChanged.connect(self.change_file_type)
        type_layout.addWidget(type_label)
        type_layout.addWidget(self.type_combo)
        content_layout.addLayout(type_layout)

        # 列映射区域
        mapping_group = QGroupBox("") 
        mapping_group.setFont(QFont(load_custom_font(), 12))
        mapping_layout = QFormLayout()

        # 创建列选择控件
        self._create_combo_row(mapping_layout, 'id_combo', '学号列：')
        self._create_combo_row(mapping_layout, 'name_combo', '姓名列：')
        self._create_checkable_combo_row(mapping_layout, 'gender_combo', 'gender_check', '性别列：', '性别')
        self._create_checkable_combo_row(mapping_layout, 'group_combo', 'group_check', '小组列：', '小组')

        mapping_group.setLayout(mapping_layout)
        content_layout.addWidget(mapping_group)

        # 按钮区域
        btn_layout = QHBoxLayout()
        cancel_btn = PushButton("取消")
        cancel_btn.setFont(QFont(load_custom_font(), 12))
        ok_btn = PrimaryPushButton("导入")
        ok_btn.setFont(QFont(load_custom_font(), 12))
        cancel_btn.clicked.connect(self.reject)
        ok_btn.clicked.connect(self.accept)
        btn_layout.addStretch(1)
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(ok_btn)
        content_layout.addLayout(btn_layout)

        # 添加内容区域到主布局
        layout.addLayout(content_layout)
        self.setLayout(layout)

    def _create_combo_box(self):
        # 创建下拉框
        combo = ComboBox()
        combo.setFont(QFont(load_custom_font(), 12))
        combo.addItem('请选择')
        return combo

    def _create_combo_row(self, layout, combo_attr, label_text):
        # 创建下拉框行
        row_layout = QHBoxLayout()
        combo = self._create_combo_box()
        setattr(self, combo_attr, combo)
        row_layout.addWidget(combo)
        layout.addRow(label_text, row_layout)

    def _create_checkable_combo_row(self, layout, combo_attr, check_attr, label_text, column_name):
        # 创建带复选框的下拉框行
        row_layout = QHBoxLayout()
        combo = self._create_combo_box()
        setattr(self, combo_attr, combo)

        check_box = CheckBox("包含")
        check_box.setFont(QFont(load_custom_font(), 12))
        check_box.setChecked(True)
        check_box.stateChanged.connect(lambda: self.toggle_column(column_name))
        setattr(self, check_attr, check_box)

        row_layout.addWidget(combo)
        row_layout.addWidget(check_box)
        layout.addRow(label_text, row_layout)

    def change_file_type(self, index):
        # 切换文件类型并更新UI状态
        types = ['excel', 'csv', 'namepicker']
        self.file_type = types[index]
        
        # 清除并重新加载列数据
        self.file_path_edit.clear()
        self.file_path = None
        self.clear_columns()

    def browse_file(self):
        filters = {
            # 仅支持xlsx格式的Excel文件
            'excel': "Excel 文件 (*.xlsx)",
            'csv': "CSV 文件 (*.csv)",
            'namepicker': "NamePicker < 软件版本3.0 格式 CSV 文件 (*.csv)"
        }
        self.file_path, _ = QFileDialog.getOpenFileName(
            self, "选择文件", "", filters[self.file_type]
        )
        if self.file_path:
            self.file_path_edit.setText(self.file_path)
            self.load_columns()

    def clear_columns(self):
        # 清空列选择控件
        for combo in [self.id_combo, self.name_combo, self.gender_combo, self.group_combo]:
            combo.clear()
            combo.addItem('请选择')
        self.update_mapping()

    def load_columns(self):
        # 加载文件列名
        try:
            if self.file_type == 'excel':
                self._load_excel_columns()
            elif self.file_type == 'csv' or self.file_type == 'namepicker':
                self._load_csv_columns()
        except Warning as w:
            # 处理提示性警告，不清除文件路径
            logger.error(f"列选择提示: {str(w)}")
            msg_box = MessageBox("列选择提示", str(w), self)
            msg_box.yesButton.setText("确定")
            msg_box.cancelButton.hide()
            msg_box.buttonLayout.insertStretch(1)
            msg_box.exec_()
        except Exception as e:
            logger.error(f"加载文件列失败: {str(e)}")
            # 文件加载失败提示
            w = MessageBox("加载失败", f"无法读取文件: {str(e)}", self)
            w.yesButton.setText("确定")
            w.cancelButton.hide()
            w.buttonLayout.insertStretch(1)
            w.exec_()
            self.file_path = None
            self.file_path_edit.clear()

    def _init_combo_boxes(self, columns):
        # 初始化所有下拉框
        column_items = ['请选择'] + [str(col) for col in columns]
        for combo in [self.id_combo, self.name_combo, self.gender_combo, self.group_combo]:
            combo.clear()
            combo.addItems(column_items)
            combo.setVisible(True)
        self.update_mapping()

    def _auto_select_columns(self, columns):
        # 智能列匹配
        fields = [
            (self.id_combo, ['id', '学号', 'studentid', 'no', 'number'], True, '学号'),
            (self.name_combo, ['name', '姓名', 'studentname', 'nickname'], True, '姓名'),
            (self.gender_combo, ['gender', '性别', 'sex'], False, '性别'),
            (self.group_combo, ['group', '小组', 'team'], False, '小组')
        ]

        # 检查是否为数字列名（如CSV文件没有标题行的情况）
        is_numeric_columns = all(str(col).isdigit() for col in columns)
        
        if is_numeric_columns and len(columns) >= 2:
            # 如果列名都是数字，默认第一列作为学号，第二列作为姓名
            self.id_combo.setCurrentIndex(1)  # 第一列
            self.name_combo.setCurrentIndex(2)  # 第二列
            # 可选列不自动选择
            self.gender_check.setChecked(False)
            self.group_check.setChecked(False)
        else:
            # 正常的列名匹配逻辑
            for combo, keywords, is_required, field_name in fields:
                # 自动选择匹配项
                auto_selected = False
                for i, col in enumerate(columns):
                    if any(key in str(col).lower() for key in keywords):
                        combo.setCurrentIndex(i + 1)  # +1是因为第一个选项是"请选择"
                        auto_selected = True
                        break

                # 必选列验证
                self._validate_required_column(combo, is_required, field_name, columns)

                # 可选列未找到匹配时取消勾选
                if not is_required and not auto_selected:
                    if field_name == '性别':
                        self.gender_check.setChecked(False)
                    elif field_name == '小组':
                        self.group_check.setChecked(False)

        self.update_mapping()
        self._validate_mandatory_columns()

    def _validate_required_column(self, combo, is_required, field_name, columns):
        # 必选列验证
        if is_required and combo.currentIndex() == 0:  # 0表示"请选择"
            if columns:
                combo.setCurrentIndex(1)  # 选择第一列数据
                raise Warning(f"已自动选择第一列作为{field_name}列，请确认是否正确")
            else:
                raise Exception(f"必须选择{field_name}对应的列")

    def _validate_mandatory_columns(self):
        # 验证用户选择
        if self.column_mapping['学号'] == -1:
            raise Exception("必须选择学号对应的列")
        if self.column_mapping['姓名'] == -1:
            raise Exception("必须选择姓名对应的列")

    def _load_excel_columns(self):
        # 加载Excel列并智能匹配
        df = pd.read_excel(self.file_path)
        columns = list(df.columns)
        self._init_combo_boxes(columns)
        self._auto_select_columns(columns)

    def _load_csv_columns(self):
        # 加载CSV列并智能匹配
        df = self._read_csv_file(self.file_path)
        columns = list(df.columns)
        self._init_combo_boxes(columns)
        self._auto_select_columns(columns)

    def update_mapping(self):
        # 更新列映射，确保索引正确计算
        self.column_mapping['学号'] = self.id_combo.currentIndex() - 1 if self.id_combo.currentIndex() > 0 else -1
        self.column_mapping['姓名'] = self.name_combo.currentIndex() - 1 if self.name_combo.currentIndex() > 0 else -1
        self.column_mapping['性别'] = self.gender_combo.currentIndex() - 1 if (self.gender_check.isChecked() and self.gender_combo.currentIndex() > 0) else -1
        self.column_mapping['小组'] = self.group_combo.currentIndex() - 1 if (self.group_check.isChecked() and self.group_combo.currentIndex() > 0) else -1

    def toggle_column(self, column):
        self.include_columns[column] = not self.include_columns[column]
        self.update_mapping()

    def accept(self):
        # 检查必要条件是否满足并执行导入
        self.update_mapping()
        if not self.file_path:
            self._show_error_message("文件未选择", "请先选择导入文件！")
            return

        # 根据文件类型执行不同的验证逻辑
        validation_methods = {
            'excel': self._validate_excel,
            'csv': self._validate_csv_json
        }

        validator = validation_methods.get(self.file_type)
        if validator and not validator():
            return

        try:
            # 获取班级名称并验证
            if not hasattr(self.parent(), 'class_comboBox'):
                raise Exception("无法获取班级信息，请确保主界面已正确加载")
            self.class_name = self.parent().class_comboBox.currentText()
            
            # 传递最新列映射给导入方法
            self.processed_data = self._import_data()
            self._show_success_message("导入成功", f"学生名单导入成功！\n共导入 {len(self.processed_data)} 条记录")
            super().accept()
        except Exception as e:
            logger.error(f"导入失败: {str(e)}")
            self._show_error_message("导入失败", f"导入过程中出错: {str(e)}")

    def _read_csv_file(self, file_path):
        # 智能读取CSV文件的专用方法
        encodings = ['utf-8', 'gbk', 'gb2312', 'latin-1', 'iso-8859-1', 'cp936']
        found_encoding = None
        found_sep = None
        df = None
        
        # 尝试不同编码和分隔符组合
        for encoding in encodings:
            try:
                for sep in [',', ';', '\t']:
                    df = pd.read_csv(file_path, encoding=encoding, sep=sep, nrows=10)
                    if len(df.columns) > 1:
                        found_encoding = encoding
                        found_sep = sep
                        break
                if found_encoding:
                    break
            except:
                continue
        
        # 验证是否找到合适的解析方式
        if df is None:
            raise Exception("无法解析CSV文件，请检查文件格式是否正确")
        
        # 使用找到的参数读取完整文件
        return pd.read_csv(file_path, encoding=found_encoding, sep=found_sep)

    def _import_data(self):
        # 执行学生数据导入并返回处理后的数据
        # 根据文件类型选择合适的读取方式
        file_ext = os.path.splitext(self.file_path)[1].lower()
        
        # 根据扩展名选择读取方法
        if file_ext in ['.xlsx', '.xls']:
            df = pd.read_excel(self.file_path)
        elif file_ext == '.csv':
            df = self._read_csv_file(self.file_path)
        else:
            raise Exception(f"不支持的文件类型: {file_ext}，请使用Excel或CSV文件")

        # 获取列映射
        id_col = self.column_mapping['学号']
        name_col = self.column_mapping['姓名']
        gender_col = self.column_mapping['性别']
        group_col = self.column_mapping['小组']

        # 处理学生数据
        student_data = {}
        for index, row in df.iterrows():
            # 获取学号和姓名（必选字段）
            # 提取并清理学号和姓名（去除空白字符）
            student_id = str(row.iloc[id_col]).strip()
            student_name = str(row.iloc[name_col]).strip()

            # 验证必填字段（确保不为空）
            if not student_id or not student_name:
                continue

            # 创建学生信息字典
            # 处理性别字段转换（针对NamePicker格式）
            gender_value = str(row.iloc[gender_col]) if gender_col != -1 and not pd.isna(row.iloc[gender_col]) else ""
            if self.file_type == 'namepicker' and gender_value.isdigit():
                gender_map = {'0': '男', '1': '女', '2': '非二元'}
                gender_value = gender_map.get(gender_value, gender_value)
            
            student_data[student_name] = {
                'id': int(student_id) if student_id.isdigit() else index + 1,
                'gender': gender_value,
                'group': str(row.iloc[group_col]) if group_col != -1 and not pd.isna(row.iloc[group_col]) else '',
                # 根据名字是否包含【】判断学生是否存在
                'exist': False if '【' in student_name or '】' in student_name else True
            }

        return student_data

    def _show_error_message(self, title, message):
        # 统一错误提示对话框
        w = MessageBox(title, message, self)
        w.yesButton.setText("确定")
        w.cancelButton.hide()
        w.buttonLayout.insertStretch(1)
        w.exec_()

    def _show_success_message(self, title, message):
        # 统一成功提示对话框
        w = MessageBox(title, message, self)
        w.yesButton.setText("确定")
        w.cancelButton.hide()
        w.buttonLayout.insertStretch(1)
        w.exec_()

    def _validate_excel(self):
        # Excel文件验证
        if self.id_combo.currentIndex() <= 0:
            self._show_error_message("学号列未选择", "请选择有效的学号列！")
            return False

        if self.name_combo.currentIndex() <= 0:
            self._show_error_message("姓名列未选择", "请选择有效的姓名列！")
            return False

        # 可选列未选择时自动取消勾选
        if self.gender_check.isChecked() and self.gender_combo.currentIndex() <= 0:
            self.gender_check.setChecked(False)
        if self.group_check.isChecked() and self.group_combo.currentIndex() <= 0:
            self.group_check.setChecked(False)

        # 验证列选择唯一性
        selected_columns = []
        if self.id_combo.currentIndex() > 0:
            selected_columns.append(self.id_combo.currentIndex() - 1)
        if self.name_combo.currentIndex() > 0:
            selected_columns.append(self.name_combo.currentIndex() - 1)
        if self.gender_check.isChecked() and self.gender_combo.currentIndex() > 0:
            selected_columns.append(self.gender_combo.currentIndex() - 1)
        if self.group_check.isChecked() and self.group_combo.currentIndex() > 0:
            selected_columns.append(self.group_combo.currentIndex() - 1)

        # 检查重复选择
        if len(selected_columns) != len(set(selected_columns)):
            self._show_error_message("列选择错误", "不能选择重复的列！请确保所有选中的列都是唯一的。")
            return False

        return True

    def _validate_csv_json(self):
        # CSV/JSON文件验证
        if self.id_combo.currentIndex() <= 0:
            self._show_error_message("验证失败", "文件缺少必要的学号列！")
            return False

        if self.name_combo.currentIndex() <= 0:
            self._show_error_message("验证失败", "文件缺少必要的姓名列！")
            return False

        # 可选列未选择时自动取消勾选
        if self.gender_check.isChecked() and self.gender_combo.currentIndex() <= 0:
            self.gender_check.setChecked(False)
        if self.group_check.isChecked() and self.group_combo.currentIndex() <= 0:
            self.group_check.setChecked(False)

        # 验证列选择唯一性
        selected_columns = []
        if self.id_combo.currentIndex() > 0:
            selected_columns.append(self.id_combo.currentIndex() - 1)
        if self.name_combo.currentIndex() > 0:
            selected_columns.append(self.name_combo.currentIndex() - 1)
        if self.gender_check.isChecked() and self.gender_combo.currentIndex() > 0:
            selected_columns.append(self.gender_combo.currentIndex() - 1)
        if self.group_check.isChecked() and self.group_combo.currentIndex() > 0:
            selected_columns.append(self.group_combo.currentIndex() - 1)

        # 检查重复选择
        if len(selected_columns) != len(set(selected_columns)):
            self._show_error_message("列选择错误", "不能选择重复的列！请确保所有选中的列都是唯一的。")
            return False

        return True

    def get_processed_data(self):
        # 返回处理后的学生数据和班级名称
        return self.processed_data, self.class_name

    def get_result(self):
        return self.file_path, self.file_type, self.column_mapping

class ClassInputDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("输入班级名称")
        self.setMinimumSize(400, 335)  # 设置最小大小而不是固定大小
        self.saved = False
        self.dragging = False
        
        # 设置无边框窗口
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        # 创建标题栏
        self.title_bar = QWidget()
        self.title_bar.setObjectName("CustomTitleBar")
        self.title_bar.setFixedHeight(35)
        # 标题栏布局
        title_layout = QHBoxLayout(self.title_bar)
        title_layout.setContentsMargins(10, 0, 10, 0)
        # 标题标签
        self.title_label = QLabel("输入班级名称")
        self.title_label.setObjectName("TitleLabel")
        self.title_label.setFont(QFont(load_custom_font(), 12, QFont.Bold))
        # 关闭按钮
        self.close_button = QPushButton("✕")
        self.close_button.setObjectName("CloseButton")
        self.close_button.setFixedSize(25, 25)
        self.close_button.clicked.connect(self.close)
        # 添加到布局
        title_layout.addWidget(self.title_label)
        title_layout.addStretch(1)
        title_layout.addWidget(self.close_button)
        
        self.text_label = BodyLabel('请输入班级名称，每行一个')
        self.text_label.setFont(QFont(load_custom_font(), 12))

        self.update_theme_style()
        qconfig.themeChanged.connect(self.update_theme_style)
        
        self.textEdit = PlainTextEdit()
        self.textEdit.setPlaceholderText("请输入班级名称，每行一个")
        self.textEdit.setFont(QFont(load_custom_font(), 12))
        
        self.setFont(QFont(load_custom_font(), 12))

        try:
            list_folder = path_manager.get_resource_path('list', '')
            if path_manager.file_exists(list_folder) and os.path.isdir(list_folder):
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
        
        # 创建主布局
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 添加标题栏到主布局
        layout.addWidget(self.title_bar)
        
        # 创建内容区域布局
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(10, 10, 10, 10)
        content_layout.setSpacing(10)
        
        # 添加UI元素到内容布局
        content_layout.addWidget(self.text_label)
        content_layout.addWidget(self.textEdit)
        
        # 创建按钮布局
        buttonLayout = QHBoxLayout()
        buttonLayout.addStretch(1)
        buttonLayout.addWidget(self.cancelButton)
        buttonLayout.addWidget(self.saveButton)
        
        # 将按钮布局添加到内容布局
        content_layout.addLayout(buttonLayout)
        
        # 将内容布局添加到主布局
        layout.addLayout(content_layout)
        
        # 设置主布局
        self.setLayout(layout)
    
    def update_theme_style(self):
        # 主题样式更新，现在包含自定义标题栏
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
            QLabel, QPushButton, QTextEdit {{ color: {colors['text']}; }}
        """)
        
        # 设置标题栏颜色以匹配背景色（仅Windows系统）
        if os.name == 'nt':
            try:
                import ctypes
                # 修复参数类型错误，现在要把窗口ID转成整数才行
                hwnd = int(self.winId())  # 转换为整数句柄
                
                # 颜色格式要改成ARGB才行，添加透明度通道
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

    def mousePressEvent(self, event):
        # 标题栏拖动
        if event.button() == Qt.LeftButton and self.title_bar.geometry().contains(event.pos()):
            self.dragging = True
            self.drag_start_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        # 窗口拖动
        if self.dragging and event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_start_position)
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        # 结束拖动
        if self.dragging and event.button() == Qt.LeftButton:
            self.dragging = False
            event.accept()
        else:
            super().mouseReleaseEvent(event)
        
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
        self.setMinimumSize(400, 635)  # 设置最小大小而不是固定大小
        self.saved = False
        self.dragging = False
        
        # 设置无边框窗口
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        # 创建标题栏
        self.title_bar = QWidget()
        self.title_bar.setObjectName("CustomTitleBar")
        self.title_bar.setFixedHeight(35)
        # 标题栏布局
        title_layout = QHBoxLayout(self.title_bar)
        title_layout.setContentsMargins(10, 0, 10, 0)
        # 标题标签
        self.title_label = QLabel("输入学生姓名")
        self.title_label.setObjectName("TitleLabel")
        self.title_label.setFont(QFont(load_custom_font(), 12, QFont.Bold))
        # 关闭按钮
        self.close_button = QPushButton("✕")
        self.close_button.setObjectName("CloseButton")
        self.close_button.setFixedSize(25, 25)
        self.close_button.clicked.connect(self.close)
        # 添加到布局
        title_layout.addWidget(self.title_label)
        title_layout.addStretch(1)
        title_layout.addWidget(self.close_button)

        self.text_label = BodyLabel('请输入学生姓名，每行一个\n已经不在当前班级的学生会被标记为不是否在班级')
        self.text_label.setFont(QFont(load_custom_font(), 12))

        self.update_theme_style()
        qconfig.themeChanged.connect(self.update_theme_style)
        
        self.textEdit = PlainTextEdit()
        self.textEdit.setPlaceholderText("请输入学生姓名，每行一个")
        self.textEdit.setFont(QFont(load_custom_font(), 12))
        
        self.setFont(QFont(load_custom_font(), 12))
        
        class_name = self.parent().class_comboBox.currentText()
        try:
            student_file = path_manager.get_resource_path('list', f'{class_name}.json')
            with open_file(student_file, 'r', encoding='utf-8') as f:
                file_content = f.read()
                if not file_content.strip():
                    # 处理空文件情况
                    logger.error(f"JSON文件为空: {student_file}")
                    return
                
                try:
                    data = json.loads(file_content)
                    if not isinstance(data, dict):
                        raise ValueError("JSON格式不正确，应为字典类型")
                    
                    name_list = []
                    for student_name in data:
                        # 去掉显示时的【】符号
                        clean_name = student_name.replace('【', '').replace('】', '')
                        name_list.append(clean_name)
                    self.textEdit.setPlainText("\n".join(name_list))
                except json.JSONDecodeError as e:
                    logger.error(f"JSON解析错误: {str(e)}")
                except ValueError as e:
                    logger.error(f"数据格式错误: {str(e)}")
        except FileNotFoundError:
            logger.error(f"文件未找到: {student_file}")
        except json.JSONDecodeError:
            logger.error("JSON文件格式错误，请检查文件内容")
        
        self.saveButton = PrimaryPushButton("保存")
        self.cancelButton = PushButton("取消")
        self.saveButton.clicked.connect(self.accept)
        self.cancelButton.clicked.connect(self.reject)
        self.saveButton.setFont(QFont(load_custom_font(), 12))
        self.cancelButton.setFont(QFont(load_custom_font(), 12))
        

        # 创建主布局
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 添加标题栏到主布局
        layout.addWidget(self.title_bar)
        
        # 创建内容区域布局
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(10, 10, 10, 10)
        content_layout.setSpacing(10)
        
        # 添加UI元素到内容布局
        content_layout.addWidget(self.text_label)
        content_layout.addWidget(self.textEdit)
        
        # 创建按钮布局
        buttonLayout = QHBoxLayout()
        buttonLayout.addStretch(1)
        buttonLayout.addWidget(self.cancelButton)
        buttonLayout.addWidget(self.saveButton)
        
        # 将按钮布局添加到内容布局
        content_layout.addLayout(buttonLayout)
        
        # 将内容布局添加到主布局
        layout.addLayout(content_layout)
        
        # 设置主布局
        self.setLayout(layout)

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
            QLabel, QPushButton, QTextEdit {{ color: {colors['text']}; }}
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

    def mousePressEvent(self, event):
        # 标题栏拖动
        if event.button() == Qt.LeftButton and self.title_bar.geometry().contains(event.pos()):
            self.dragging = True
            self.drag_start_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        # 窗口拖动
        if self.dragging and event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_start_position)
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        # 结束拖动
        if self.dragging and event.button() == Qt.LeftButton:
            self.dragging = False
            event.accept()
        else:
            super().mouseReleaseEvent(event)
        
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
        self.setWindowTitle("输入每个学生对应的性别")
        self.setMinimumSize(400, 435)  # 设置最小大小而不是固定大小
        self.saved = False
        self.dragging = False
        
        # 设置无边框窗口
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        # 创建标题栏
        self.title_bar = QWidget()
        self.title_bar.setObjectName("CustomTitleBar")
        self.title_bar.setFixedHeight(35)
        # 标题栏布局
        title_layout = QHBoxLayout(self.title_bar)
        title_layout.setContentsMargins(10, 0, 10, 0)
        # 标题标签
        self.title_label = QLabel("输入每个学生对应的性别")
        self.title_label.setObjectName("TitleLabel")
        self.title_label.setFont(QFont(load_custom_font(), 12, QFont.Bold))
        # 关闭按钮
        self.close_button = QPushButton("✕")
        self.close_button.setObjectName("CloseButton")
        self.close_button.setFixedSize(25, 25)
        self.close_button.clicked.connect(self.close)
        # 添加到布局
        title_layout.addWidget(self.title_label)
        title_layout.addStretch(1)
        title_layout.addWidget(self.close_button)

        self.text_label = BodyLabel('请输入每个学生对应的性别，每行一个\n例:男 或 女（其它的？自己试一试吧）\n注：尽量在表格中复制后直接粘贴')
        self.text_label.setFont(QFont(load_custom_font(), 12))

        self.update_theme_style()
        qconfig.themeChanged.connect(self.update_theme_style)

        self.textEdit = PlainTextEdit()
        self.textEdit.setPlaceholderText("请输入每个学生对应的性别，每行一个")
        self.textEdit.setFont(QFont(load_custom_font(), 12))
        
        # 统一设置对话框字体
        self.setFont(QFont(load_custom_font(), 12))
        
        class_name = self.parent().class_comboBox.currentText()
        # 尝试读取已保存的性别值
        try:
            student_file = path_manager.get_resource_path('list', f'{class_name}.json')
            with open_file(student_file, 'r', encoding='utf-8') as f:
                file_content = f.read()
                if not file_content.strip():
                    logger.error(f"JSON文件为空: {student_file}")
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
            logger.error(f"JSON文件解析错误：{str(e)}")
        
        self.saveButton = PrimaryPushButton("保存")
        self.cancelButton = PushButton("取消")
        self.saveButton.clicked.connect(self.accept)
        self.cancelButton.clicked.connect(self.reject)
        self.saveButton.setFont(QFont(load_custom_font(), 12))
        self.cancelButton.setFont(QFont(load_custom_font(), 12))
        
        # 创建主布局
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 添加标题栏到主布局
        layout.addWidget(self.title_bar)
        
        # 创建内容区域布局
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(10, 10, 10, 10)
        content_layout.setSpacing(10)
        
        # 添加UI元素到内容布局
        content_layout.addWidget(self.text_label)
        content_layout.addWidget(self.textEdit)
        
        # 创建按钮布局
        buttonLayout = QHBoxLayout()
        buttonLayout.addStretch(1)
        buttonLayout.addWidget(self.cancelButton)
        buttonLayout.addWidget(self.saveButton)
        
        # 将按钮布局添加到内容布局
        content_layout.addLayout(buttonLayout)
        
        # 将内容布局添加到主布局
        layout.addLayout(content_layout)
        
        # 设置主布局
        self.setLayout(layout)

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
            QLabel, QPushButton, QTextEdit {{ color: {colors['text']}; }}
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

    def mousePressEvent(self, event):
        # 标题栏拖动
        if event.button() == Qt.LeftButton and self.title_bar.geometry().contains(event.pos()):
            self.dragging = True
            self.drag_start_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        # 窗口拖动
        if self.dragging and event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_start_position)
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        # 结束拖动
        if self.dragging and event.button() == Qt.LeftButton:
            self.dragging = False
            event.accept()
        else:
            super().mouseReleaseEvent(event)
        
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
        self.setWindowTitle("输入每个学生对应的小组名称")
        self.setMinimumSize(400, 435)  # 增加高度以适应标题栏
        self.saved = False
        self.dragging = False
        
        # 设置无边框窗口
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        # 创建标题栏
        self.title_bar = QWidget()
        self.title_bar.setObjectName("CustomTitleBar")
        self.title_bar.setFixedHeight(35)
        # 标题栏布局
        title_layout = QHBoxLayout(self.title_bar)
        title_layout.setContentsMargins(10, 0, 10, 0)
        # 标题标签
        self.title_label = QLabel("输入每个学生对应的小组名称")
        self.title_label.setObjectName("TitleLabel")
        self.title_label.setFont(QFont(load_custom_font(), 12, QFont.Bold))
        # 关闭按钮
        self.close_button = QPushButton("✕")
        self.close_button.setObjectName("CloseButton")
        self.close_button.setFixedSize(25, 25)
        self.close_button.clicked.connect(self.close)
        # 添加到布局
        title_layout.addWidget(self.title_label)
        title_layout.addStretch(1)
        title_layout.addWidget(self.close_button)

        self.text_label = BodyLabel('请输入每个学生对应的小组名称，每行一个\n例:第1小组 或 第一小组\n注:尽量在表格中复制后直接粘贴')
        self.text_label.setFont(QFont(load_custom_font(), 12))

        self.update_theme_style()
        qconfig.themeChanged.connect(self.update_theme_style)

        self.textEdit = PlainTextEdit()
        self.textEdit.setPlaceholderText("请输入每个学生对应的小组名称，每行一个")
        self.textEdit.setFont(QFont(load_custom_font(), 12))
        
        # 统一设置对话框字体
        self.setFont(QFont(load_custom_font(), 12))
        
        class_name = self.parent().class_comboBox.currentText()
        # 尝试读取已保存的小组值
        try:
            student_file = path_manager.get_resource_path('list', f'{class_name}.json')
            with open_file(student_file, 'r', encoding='utf-8') as f:
                file_content = f.read()
                if not file_content.strip():
                    logger.error(f"JSON文件为空: {student_file}")
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
        
        # 创建主布局
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 添加标题栏到主布局
        layout.addWidget(self.title_bar)
        
        # 创建内容区域布局
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(10, 10, 10, 10)
        content_layout.setSpacing(10)
        
        # 添加UI元素到内容布局
        content_layout.addWidget(self.text_label)
        content_layout.addWidget(self.textEdit)
        
        # 创建按钮布局
        buttonLayout = QHBoxLayout()
        buttonLayout.addStretch(1)
        buttonLayout.addWidget(self.cancelButton)
        buttonLayout.addWidget(self.saveButton)
        
        # 将按钮布局添加到内容布局
        content_layout.addLayout(buttonLayout)
        
        # 将内容布局添加到主布局
        layout.addLayout(content_layout)
        
        # 设置主布局
        self.setLayout(layout)

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
            QLabel, QPushButton, QTextEdit {{ color: {colors['text']}; }}
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

    def mousePressEvent(self, event):
        # 标题栏拖动
        if event.button() == Qt.LeftButton and self.title_bar.geometry().contains(event.pos()):
            self.dragging = True
            self.drag_start_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        # 窗口拖动
        if self.dragging and event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_start_position)
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        # 结束拖动
        if self.dragging and event.button() == Qt.LeftButton:
            self.dragging = False
            event.accept()
        else:
            super().mouseReleaseEvent(event)
        
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
