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

class reward_SettinsCard(GroupHeaderCardWidget):
    refresh_signal = pyqtSignal()
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("抽奖名单")
        self.setBorderRadius(8)
        self.settings_file = "app/Settings/Settings.json"

        self.prize_pools_Button = PushButton("设置奖池名称")
        self.prize_pools_Button.clicked.connect(self.show_prize_pools_dialog)
        self.prize_pools_Button.setFont(QFont(load_custom_font(), 12))
        
        self.prize_pools_comboBox = ComboBox()
        self.prize_pools_comboBox.setFixedWidth(250)
        self.prize_pools_comboBox.setPlaceholderText("选择一个需要设置奖品的奖池")
        self.prize_pools_comboBox.addItems([])
        self.prize_pools_comboBox.setFont(QFont(load_custom_font(), 12))
        self.prize_pools_comboBox.currentIndexChanged.connect(lambda: self.refresh_signal.emit())

        self.prize_Button = PushButton("设置奖池奖品")
        self.prize_Button.clicked.connect(self.show_prize_dialog)
        self.prize_Button.setFont(QFont(load_custom_font(), 12))

        self.probability_Button = PushButton("设置奖品权重")
        self.probability_Button.clicked.connect(self.show_probability_dialog)
        self.probability_Button.setFont(QFont(load_custom_font(), 12))
        
        try:
            list_folder = "app/resource/reward"
            if os.path.exists(list_folder) and os.path.isdir(list_folder):
                files = os.listdir(list_folder)
                prizes = []
                for file in files:
                    if file.endswith('.json'):
                        prize_pools_name = os.path.splitext(file)[0]
                        prizes.append(prize_pools_name)
                
                self.prize_pools_comboBox.clear()
                self.prize_pools_comboBox.addItems(prizes)
        except Exception as e:
            logger.error(f"加载奖品名称失败: {str(e)}")

        # 添加组件到分组中
        self.addGroup(get_theme_icon("ic_fluent_class_20_filled"), "设置奖池", "设置奖池名称", self.prize_pools_Button)
        self.addGroup(get_theme_icon("ic_fluent_multiselect_ltr_20_filled"), "选择奖池", "选择一个需要设置奖品的奖池", self.prize_pools_comboBox)
        self.addGroup(get_theme_icon("ic_fluent_people_list_20_filled"), "设置奖池奖品", "设置该奖池的奖品", self.prize_Button)
        self.addGroup(get_theme_icon("ic_fluent_person_pill_20_filled"), "设置奖品权重", "设置奖品权重", self.probability_Button)

        # 创建表格
        self.table = TableWidget(self)
        self.table.setBorderVisible(True)
        self.table.setBorderRadius(8)
        self.table.setWordWrap(False)
        self.table.setColumnCount(3)
        self.table.setEditTriggers(TableWidget.NoEditTriggers)
        self.table.setSortingEnabled(True)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.verticalHeader().hide()
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setHorizontalHeaderLabels(['序号', '奖品', '权重'])
        self.show_table()
        self.refresh_signal.connect(self.show_table)
        # 布局
        self.layout().addWidget(self.table)

    def show_table(self):
        prize_pools_name = self.prize_pools_comboBox.currentText()
        # 获取是否存在奖品
        if os.path.exists(f"app/resource/reward/{prize_pools_name}.json"):
            with open(f"app/resource/reward/{prize_pools_name}.json", 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            data = []

        if not prize_pools_name:
            self.prize_Button.setEnabled(False)
            self.probability_Button.setEnabled(False)
            self.prize_pools_comboBox.setPlaceholderText("选择一个需要设置奖品的奖池")
        elif not data:
            self.prize_Button.setEnabled(True)
            self.probability_Button.setEnabled(False)
        else:
            self.prize_Button.setEnabled(True)
            self.probability_Button.setEnabled(True)

        if prize_pools_name and (not data):
            self.table.setRowCount(0)
            self.table.setHorizontalHeaderLabels([])
            return
            
        if prize_pools_name:
            try:
                with open(f"app/resource/reward/{prize_pools_name}.json", 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.table.setRowCount(len(data))
                self.table.clearContents()
                
                # 计算最大ID位数
                max_digits = max(len(str(info['id'])) for info in data.values())
                
                self.table.setSortingEnabled(False)
                for i, (name, info) in enumerate(data.items()):
                    self.table.setItem(i, 0, QTableWidgetItem(str(info['id']).zfill(max_digits)))
                    self.table.setItem(i, 1, QTableWidgetItem(name))
                    self.table.setItem(i, 2, QTableWidgetItem(info['probability']))
                    for j in range(3):
                        item = self.table.item(i, j)
                        if item:
                            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                            item.setFont(QFont(load_custom_font(), 12))
                self.table.setHorizontalHeaderLabels(['序号', '奖品', '权重'])
                self.table.setSortingEnabled(True)
            except FileNotFoundError:
                self.table.setRowCount(0)
                self.table.setHorizontalHeaderLabels([])
                logger.error(f"奖池文件 '{prize_pools_name}.json' 不存在")
            except json.JSONDecodeError:
                self.table.setRowCount(0)
                self.table.setHorizontalHeaderLabels([])
                logger.error(f"奖池文件 '{prize_pools_name}.json' 格式错误")
            except Exception as e:
                self.table.setRowCount(0)
                self.table.setHorizontalHeaderLabels([])
                logger.error(f"显示表格时出错: {str(e)}")
        else:
            self.table.setRowCount(0)
            self.table.setHorizontalHeaderLabels([])
            logger.error("未选择奖池")
            
    def show_prize_pools_dialog(self):
        dialog = Prize_pools_InputDialog(self)
        if dialog.exec():
            prize_pools_text = dialog.getText()
            try:
                prize_poolss = [line.strip() for line in prize_pools_text.split('\n') if line.strip()]
                
                # 获取当前所有奖池文件
                list_folder = "app/resource/reward"
                existing_prize_poolss = []
                if os.path.exists(list_folder):
                    existing_prize_poolss = [f.split('.')[0] for f in os.listdir(list_folder) if f.endswith('.json')]
                
                # 删除不再需要的奖池文件
                for existing_prize in existing_prize_poolss:
                    if existing_prize not in prize_poolss:
                        prize_pools_file = f"app/resource/reward/{existing_prize}.json"
                        history_file = f"app/resource/reward/history/{existing_prize}.json"
                        try:
                            os.remove(prize_pools_file)
                            logger.info(f"已删除奖池文件: {prize_pools_file}")
                            # 删除对应的历史记录文件
                            if os.path.exists(f"app/resource/reward/history/{existing_prize}.json"):
                                os.remove(history_file)
                                logger.info(f"已删除历史记录文件: {history_file}")
                        except Exception as e:
                            logger.error(f"删除文件失败: {prize_pools_file}或{history_file}, 错误: {str(e)}")

                os.makedirs("app/resource/reward", exist_ok=True)
                
                for prize_pools_name in prize_poolss:
                    prize_pools_file = f"app/resource/reward/{prize_pools_name}.json"
                    if not os.path.exists(prize_pools_file):
                        with open(prize_pools_file, 'w', encoding='utf-8') as f:
                            basic_structure = {
                                "示例奖品": {
                                    "id": 1,
                                    "probability": "1",
                                }
                            }
                            json.dump(basic_structure, f, ensure_ascii=False, indent=4)

                self.prize_pools_comboBox.clear()
                self.prize_pools_comboBox.addItems(prize_poolss)
                self.refresh_signal.emit()
                logger.info("奖池名单保存成功！")
            except Exception as e:
                logger.error(f"保存失败: {str(e)}")
    
    def show_prize_dialog(self):
        dialog = PrizeInputDialog(self)
        if dialog.exec():
            prize_text = dialog.getText()
            selected_prize = self.prize_pools_comboBox.currentText()
            if selected_prize:
                try:
                    students = [line.strip() for line in prize_text.split('\n') if line.strip()]
                    
                    os.makedirs("app/resource/reward", exist_ok=True)
                    
                    prize_file = f"app/resource/reward/{selected_prize}.json"
                    prize_data = {}
                    
                    if os.path.exists(prize_file):
                        with open(prize_file, 'r', encoding='utf-8') as f:
                            prize_data = json.load(f)
                    
                    existing_students = {name for name in prize_data.keys()}
                    new_students = {student for student in students if student.strip()}
                    for prize_to_remove in existing_students - new_students:
                        del prize_data[prize_to_remove]
                    
                    new_prize_data = {}
                    for idx, student in enumerate(students, start=1):
                        prize_name = student.strip()
                        if prize_name in {k for k in prize_data.keys()}: 
                            original_info = next((prize_data[k] for k in prize_data if k == prize_name), {})
                        else:
                            original_info = {}
                        new_prize_data[prize_name] = {
                            "id": idx,
                            "probability": original_info.get("probability", "1")
                        }
                    prize_data = new_prize_data
                    
                    with open(prize_file, 'w', encoding='utf-8') as f:
                        json.dump(prize_data, f, ensure_ascii=False, indent=4)
                    
                    self.refresh_signal.emit()
                    logger.info(f"奖品名单保存成功！")
                except Exception as e:
                    logger.error(f"保存失败: {str(e)}")

    def show_probability_dialog(self):
        dialog = ProbabilityInputDialog(self)
        if dialog.exec():
            probability_text = dialog.getText()
            prize_pools_name = self.prize_pools_comboBox.currentText()
            # 获取是否存在奖品
            if os.path.exists(f"app/resource/reward/{prize_pools_name}.json"):
                with open(f"app/resource/reward/{prize_pools_name}.json", 'r', encoding='utf-8') as f:
                    data = json.load(f)
            if not data:
                self.table.setRowCount(0)
                self.table.setHorizontalHeaderLabels([])
                return
            if prize_pools_name:
                try:
                    probabilitys = [line.strip() for line in probability_text.split('\n') if line.strip()]
                    
                    os.makedirs("app/resource/reward", exist_ok=True)

                    prize_file = f"app/resource/reward/{prize_pools_name}.json"
                    prize_data = {}
                    
                    if os.path.exists(prize_file):
                        with open(prize_file, 'r', encoding='utf-8') as f:
                            
                            prize_data = json.load(f)
                    
                    for idx, probability_name in enumerate(probabilitys, start=1):
                        probability_name = probability_name.strip()
                        for prize_name in prize_data:
                            if prize_data[prize_name]["id"] == idx:
                                prize_data[prize_name]["probability"] = probability_name
                    
                    with open(prize_file, 'w', encoding='utf-8') as f:
                        json.dump(prize_data, f, ensure_ascii=False, indent=4)
                    
                    self.refresh_signal.emit()
                    logger.info(f"奖品对应的权重已成功保存！")
                except Exception as e:
                    logger.error(f"保存失败: {str(e)}")



class Prize_pools_InputDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("输入奖池名称")
        self.setFixedSize(400, 300)
        self.saved = False
        
        self.text_label = BodyLabel('请输入奖池名称，每行一个')
        self.text_label.setFont(QFont(load_custom_font(), 12))

        self.update_theme_style()
        qconfig.themeChanged.connect(self.update_theme_style)
        
        self.textEdit = PlainTextEdit()
        self.textEdit.setPlaceholderText("请输入奖池名称，每行一个")
        self.textEdit.setFont(QFont(load_custom_font(), 12))
        
        self.setFont(QFont(load_custom_font(), 12))

        try:
            list_folder = "app/resource/reward"
            if os.path.exists(list_folder) and os.path.isdir(list_folder):
                files = os.listdir(list_folder)
                prizes = []
                for file in files:
                    if file.endswith('.json'):
                        prize_pools_name = os.path.splitext(file)[0]
                        prizes.append(prize_pools_name)
                
                self.textEdit.setPlainText("\n".join(prizes))
        except Exception as e:
            logger.error(f"加载奖池名称失败: {str(e)}")

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
        # 🌟 星穹铁道白露：主题样式更新 ~ (๑•̀ㅂ•́)و✧
        colors = {'text': '#111116', 'bg': '#F5F5F5'} if is_dark else {'text': '#F5F5F5', 'bg': '#111116'}
        self.setStyleSheet(f"""
            QDialog, QDialog * {{
                color: {colors['text']};
                background-color: {colors['bg']};
            }}
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

class PrizeInputDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("输入奖品名称")
        self.setFixedSize(400, 600)
        self.saved = False

        self.text_label = BodyLabel('请输入奖品名称，每行一个')
        self.text_label.setFont(QFont(load_custom_font(), 12))

        self.update_theme_style()
        qconfig.themeChanged.connect(self.update_theme_style)
        
        self.textEdit = PlainTextEdit()
        self.textEdit.setPlaceholderText("请输入奖品名称，每行一个")
        self.textEdit.setFont(QFont(load_custom_font(), 12))
        
        self.setFont(QFont(load_custom_font(), 12))
        
        prize_pools_name = self.parent().prize_pools_comboBox.currentText()
        try:
            with open(f"app/resource/reward/{prize_pools_name}.json", 'r', encoding='utf-8') as f:
                file_content = f.read()
                if not file_content.strip():
                    # 处理空文件情况
                    logger.warning(f"JSON文件为空: app/resource/reward/{prize_pools_name}.json")
                    return
                
                try:
                    data = json.loads(file_content)
                    if not isinstance(data, dict):
                        raise ValueError("JSON格式不正确，应为字典类型")
                    
                    name_list = []
                    for prize_name in data:
                        name_list.append(prize_name)
                    self.textEdit.setPlainText("\n".join(name_list))
                except json.JSONDecodeError as e:
                    logger.error(f"JSON解析错误: {str(e)}")
                except ValueError as e:
                    logger.error(f"数据格式错误: {str(e)}")
        except FileNotFoundError:
            logger.error(f"文件未找到: app/resource/reward/{prize_pools_name}.json")
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
        # 🌟 星穹铁道白露：主题样式更新 ~ (๑•̀ㅂ•́)و✧
        colors = {'text': '#111116', 'bg': '#F5F5F5'} if is_dark else {'text': '#F5F5F5', 'bg': '#111116'}
        self.setStyleSheet(f"""
            QDialog, QDialog * {{
                color: {colors['text']};
                background-color: {colors['bg']};
            }}
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

class ProbabilityInputDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("输入每项奖品对应的权重")
        self.setFixedSize(400, 400)
        self.saved = False

        self.text_label = BodyLabel('请输入每项奖品对应的权重，每行一个\n例:1 或 5\n注:尽量在表格中复制后直接粘贴')
        self.text_label.setFont(QFont(load_custom_font(), 12))

        self.update_theme_style()
        qconfig.themeChanged.connect(self.update_theme_style)

        self.textEdit = PlainTextEdit()
        self.textEdit.setPlaceholderText("请输入每项奖品对应的权重，每行一个")
        self.textEdit.setFont(QFont(load_custom_font(), 12))
        
        # 统一设置对话框字体
        self.setFont(QFont(load_custom_font(), 12))
        
        prize_pools_name = self.parent().prize_pools_comboBox.currentText()
        try:
            with open(f"app/resource/reward/{prize_pools_name}.json", 'r', encoding='utf-8') as f:
                file_content = f.read()
                if not file_content.strip():
                    logger.warning(f"JSON文件为空: app/resource/reward/{prize_pools_name}.json")
                    return
                data = json.loads(file_content)
                if isinstance(data, dict):
                    probability_list = []
                    sorted_students = sorted(data.values(), key=lambda x: x.get("id", 0))
                    for student in sorted_students:
                        if student.get("id", 0) >= 1:
                            probability_list.append(student.get("probability", ""))
                    self.textEdit.setPlainText("\n".join(probability_list))

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
        # 🌟 星穹铁道白露：主题样式更新 ~ (๑•̀ㅂ•́)و✧
        colors = {'text': '#111116', 'bg': '#F5F5F5'} if is_dark else {'text': '#F5F5F5', 'bg': '#111116'}
        self.setStyleSheet(f"""
            QDialog, QDialog * {{
                color: {colors['text']};
                background-color: {colors['bg']};
            }}
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