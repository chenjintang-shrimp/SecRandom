from math import e
from qfluentwidgets import *
from qfluentwidgets import FluentIcon as FIF
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

import os
import json
from pathlib import Path
from loguru import logger
import pandas as pd

from app.common.config import get_theme_icon, load_custom_font, is_dark_theme
from app.common.path_utils import path_manager, open_file, ensure_dir

is_dark = is_dark_theme(qconfig)

class reward_SettinsCard(GroupHeaderCardWidget):
    refresh_signal = pyqtSignal()
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("抽奖名单")
        self.setBorderRadius(8)
        self.settings_file = path_manager.get_settings_path()

        self.prize_pools_Button = PushButton("设置奖池名称")
        self.prize_pools_Button.clicked.connect(self.show_prize_pools_dialog)
        self.prize_pools_Button.setFont(QFont(load_custom_font(), 12))
        
        self.prize_pools_comboBox = ComboBox()
        self.prize_pools_comboBox.setPlaceholderText("选择一个需要设置奖品的奖池")
        self.prize_pools_comboBox.addItems([])
        self.prize_pools_comboBox.setFont(QFont(load_custom_font(), 12))
        self.prize_pools_comboBox.currentIndexChanged.connect(lambda: self.refresh_signal.emit())

        # 快速导入奖品名单
        self.import_Button = PushButton("导入奖品名单")
        self.import_Button.clicked.connect(self.import_prize_list)
        self.import_Button.setFont(QFont(load_custom_font(), 12))

        self.prize_Button = PushButton("奖品设置")
        self.prize_Button.clicked.connect(self.show_prize_dialog)
        self.prize_Button.setFont(QFont(load_custom_font(), 12))

        self.probability_Button = PushButton("权重设置")
        self.probability_Button.clicked.connect(self.show_probability_dialog)
        self.probability_Button.setFont(QFont(load_custom_font(), 12))
        
        # 导出奖品名单
        self.export_Button = PushButton("名单导出")
        self.export_Button.clicked.connect(self.export_prize_list)
        self.export_Button.setFont(QFont(load_custom_font(), 12))

        try:
            list_folder = path_manager.get_resource_path('reward')
            if list_folder.exists() and list_folder.is_dir():
                files = list(list_folder.iterdir())
                prizes = []
                for file in files:
                    if file.suffix == '.json':
                        prize_pools_name = file.stem
                        prizes.append(prize_pools_name)
                
                self.prize_pools_comboBox.clear()
                self.prize_pools_comboBox.addItems(prizes)
        except Exception as e:
            logger.error(f"加载奖品名称失败: {str(e)}")

        # 添加组件到分组中
        # 奖池管理设置
        self.addGroup(get_theme_icon("ic_fluent_class_20_filled"), "设置奖池", "创建或修改奖池名称信息", self.prize_pools_Button)
        self.addGroup(get_theme_icon("ic_fluent_multiselect_ltr_20_filled"), "选择奖池", "选择要配置奖品的奖池", self.prize_pools_comboBox)
        
        # 数据导入设置
        self.addGroup(get_theme_icon("ic_fluent_people_list_20_filled"), "导入奖品名单", "批量导入奖品数据（将覆盖现有数据）", self.import_Button)
        
        # 奖品设置
        self.addGroup(get_theme_icon("ic_fluent_people_list_20_filled"), "设置奖品名称", "配置奖池中的奖品项目", self.prize_Button)
        self.addGroup(get_theme_icon("ic_fluent_person_pill_20_filled"), "设置奖品权重", "调整奖品的中奖概率权重", self.probability_Button)
        
        # 数据导出设置
        self.addGroup(get_theme_icon("ic_fluent_people_list_20_filled"), "导出奖品名单", "导出当前奖池奖品数据到文件", self.export_Button)

        # 创建表格
        self.table = TableWidget(self)
        self.table.setBorderVisible(True)
        self.table.setBorderRadius(8)
        self.table.setWordWrap(False)
        self.table.setColumnCount(3)
        self.table.setEditTriggers(TableWidget.DoubleClicked)
        self.table.setSortingEnabled(True)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.verticalHeader().hide()
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setHorizontalHeaderLabels(['序号', '奖品', '权重'])
        self.show_table()
        self.table.itemChanged.connect(self.save_table_data)
        self.refresh_signal.connect(self.show_table)
        # 布局
        self.layout().addWidget(self.table)

    def import_prize_list(self):
        # 创建导入对话框
        dialog = ImportPrizeDialog(self)
        if dialog.exec():
            prize_data, prize_pools_name = dialog.get_processed_data()
            if not prize_pools_name or not prize_data:
                return

            try:
                reward_dir = path_manager.get_resource_path('reward')
                ensure_dir(reward_dir)
                with open_file(reward_dir / f'{prize_pools_name}.json', 'w', encoding='utf-8') as f:
                    json.dump(prize_data, f, ensure_ascii=False, indent=4)

                self.refresh_signal.emit()
                logger.info(f"奖品名单导入成功，共导入 {len(prize_data)} 条记录")
            except Exception as e:
                logger.error(f"导入失败: {str(e)}")

    def export_prize_list(self):
        prize_pools_name = self.prize_pools_comboBox.currentText()
        if not prize_pools_name:
            InfoBar.warning(
                title='导出失败',
                content='请先选择要导出的奖池',
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )
            return

        try:
            # 读取奖品数据
            reward_dir = path_manager.get_resource_path('reward')
            with open_file(reward_dir / f'{prize_pools_name}.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if not data:
                InfoBar.warning(
                    title='导出失败',
                    content='当前奖池没有奖品数据',
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
                    '序号': info['id'],
                    '奖品名称': name,
                    '权重': info['probability']
                })
            
            df = pd.DataFrame(export_data)
            
            # 打开文件保存对话框
            file_path, selected_filter = QFileDialog.getSaveFileName(
                self,
                "保存奖品名单",
                f"{prize_pools_name}_奖品名单",
                "Excel 文件 (*.xlsx);;CSV 文件 (*.csv);;TXT 文件（仅名称） (*.txt)"
            )
            
            if file_path:
                # 根据选择的文件类型确定扩展名和保存格式
                if selected_filter == "Excel 文件 (*.xlsx)":
                    if not file_path.endswith('.xlsx'):
                        file_path += '.xlsx'
                    df.to_excel(file_path, index=False, engine='openpyxl')
                elif selected_filter == "CSV 文件 (*.csv)":
                    if not file_path.endswith('.csv'):
                        file_path += '.csv'
                    df.to_csv(file_path, index=False, encoding='utf-8-sig')
                else:  # TXT文件（仅名称）
                    if not file_path.endswith('.txt'):
                        file_path += '.txt'
                    # 仅导出奖品名称，每行一个名称
                    with open_file(file_path, 'w', encoding='utf-8') as f:
                        for name in data.keys():
                            f.write(f"{name}\n")
                
                InfoBar.success(
                    title='导出成功',
                    content=f'奖品名单已导出到: {file_path}',
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=5000,
                    parent=self
                )
                logger.info(f"奖品名单导出成功: {file_path}")
                
        except FileNotFoundError:
            logger.error(f"奖池文件 '{prize_pools_name}.json' 不存在")
            InfoBar.error(
                title='导出失败',
                content='奖池文件不存在',
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )
        except json.JSONDecodeError:
            logger.error(f"奖池文件 '{prize_pools_name}.json' 格式错误")
            InfoBar.error(
                title='导出失败',
                content='奖池文件格式错误',
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )
        except Exception as e:
            logger.error(f"导出奖品名单时出错: {str(e)}")
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
        prize_pools_name = self.prize_pools_comboBox.currentText()
        # 获取是否存在奖品
        prize_file = path_manager.get_resource_path('reward', f'{prize_pools_name}.json')
        if prize_file.exists():
            with open_file(prize_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            data = []

        if not prize_pools_name:
            self.prize_Button.setEnabled(False)
            self.probability_Button.setEnabled(False)
            self.import_Button.setEnabled(False)
            self.export_Button.setEnabled(False)
            self.prize_pools_comboBox.setPlaceholderText("选择一个需要设置奖品的奖池")
        elif not data:
            self.prize_Button.setEnabled(True)
            self.import_Button.setEnabled(True)
            self.export_Button.setEnabled(False)
            self.probability_Button.setEnabled(False)
        else:
            self.prize_Button.setEnabled(True)
            self.probability_Button.setEnabled(True)
            self.import_Button.setEnabled(True)
            self.export_Button.setEnabled(True)

        if prize_pools_name and (not data):
            self.table.setRowCount(0)
            self.table.setHorizontalHeaderLabels([])
            return
            
        if prize_pools_name:
            try:
                reward_dir = path_manager.get_resource_path('reward')
                with open_file(reward_dir / f'{prize_pools_name}.json', 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.table.setRowCount(len(data))
                self.table.clearContents()
                
                # 计算最大ID位数
                max_digits = max(len(str(info['id'])) for info in data.values())
                
                self.table.setSortingEnabled(False)
                self.table.blockSignals(True)
                table_data = []
                for name, info in data.items():
                    table_data.append([
                        str(info['id']).zfill(max_digits),
                        name,
                        f"{float(info['probability'])}".rstrip('0').rstrip('.')
                    ])
                
                for i, row in enumerate(table_data):
                    for j in range(3):
                        self.table.setItem(i, j, QTableWidgetItem(row[j]))
                        item = self.table.item(i, j)
                        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                        item.setFont(QFont(load_custom_font(), 12))
                        if j == 0:
                            item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.table.setHorizontalHeaderLabels(['序号', '奖品', '权重'])
                self.table.blockSignals(False)
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
                reward_dir = path_manager.get_resource_path('reward')
                existing_prize_poolss = []
                if reward_dir.exists():
                    existing_prize_poolss = [f.stem for f in reward_dir.iterdir() if f.suffix == '.json']
                
                # 删除不再需要的奖池文件
                for existing_prize in existing_prize_poolss:
                    if existing_prize not in prize_poolss:
                        prize_pools_file = reward_dir / f'{existing_prize}.json'
                        history_file = reward_dir / 'history' / f'{existing_prize}.json'
                        try:
                            prize_pools_file.unlink()
                            logger.info(f"已删除奖池文件: {prize_pools_file}")
                            # 删除对应的历史记录文件
                            if history_file.exists():
                                history_file.unlink()
                                logger.info(f"已删除历史记录文件: {history_file}")
                        except Exception as e:
                            logger.error(f"删除文件失败: {prize_pools_file}或{history_file}, 错误: {str(e)}")

                list_folder = path_manager.get_resource_path('reward')
                ensure_dir(list_folder)
                
                for prize_pools_name in prize_poolss:
                    prize_pools_file = list_folder / f'{prize_pools_name}.json'
                    if not prize_pools_file.exists():
                        with open_file(prize_pools_file, 'w', encoding='utf-8') as f:
                            basic_structure = {
                                "示例奖品": {
                                    "id": 1,
                                    "probability": "1.0",
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
                    
                    reward_dir = path_manager.get_resource_path('reward')
                    ensure_dir(reward_dir)
                    
                    prize_file = reward_dir / f'{selected_prize}.json'
                    prize_data = {}
                    
                    if path_manager.file_exists(prize_file):
                        with open_file(prize_file, 'r', encoding='utf-8') as f:
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
                            "probability": original_info.get("probability", "1.0")
                        }
                    prize_data = new_prize_data
                    
                    with open_file(prize_file, 'w', encoding='utf-8') as f:
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
        reward_dir = path_manager.get_resource_path('reward')
        prize_file = reward_dir / f'{prize_pools_name}.json'
        if prize_file.exists():
            with open_file(prize_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if not data:
                self.table.setRowCount(0)
                self.table.setHorizontalHeaderLabels([])
                return
            if prize_pools_name:
                try:
                    probabilitys = [line.strip() for line in probability_text.split('\n') if line.strip()]
                    
                    reward_dir = path_manager.get_resource_path('reward')
                    ensure_dir(reward_dir)

                    prize_file = reward_dir / f'{prize_pools_name}.json'
                    prize_data = {}
                    
                    if path_manager.file_exists(prize_file):
                        with open_file(prize_file, 'r', encoding='utf-8') as f:
                            
                            prize_data = json.load(f)
                    
                    for idx, probability_name in enumerate(probabilitys, start=1):
                        probability_name = probability_name.strip()
                        for prize_name in prize_data:
                            if prize_data[prize_name]["id"] == idx:
                                prize_data[prize_name]["probability"] = probability_name
                    
                    with open_file(prize_file, 'w', encoding='utf-8') as f:
                        json.dump(prize_data, f, ensure_ascii=False, indent=4)
                    
                    self.refresh_signal.emit()
                    logger.info(f"奖品对应的权重已成功保存！")
                except Exception as e:
                    logger.error(f"保存失败: {str(e)}")


    def save_table_data(self, item):
        # 获取当前选中的奖池
        prize_pool = self.prize_pools_comboBox.currentText()
        if not prize_pool:
            return
        
        row = item.row()
        col = item.column()
        
        # 获取当前行的奖品名称（索引1）
        name_item = self.table.item(row, 1)
        if not name_item:
            return
        prize_name = name_item.text()
        
        # 加载当前奖池的奖品数据
        reward_dir = path_manager.get_resource_path('reward')
        prize_file = reward_dir / f'{prize_pool}.json'
        try:
            with open_file(prize_file, 'r', encoding='utf-8') as f:
                prize_data = json.load(f)
        except Exception as e:
            logger.error(f"加载奖品数据失败: {str(e)}")
            return
        
        # 找到对应的奖品键
        matched_key = None
        for key in prize_data.keys():
            if key == prize_name:
                matched_key = key
                break
        if not matched_key:
            logger.error(f"未找到奖品: {prize_name}")
            return
        
        # 根据列索引更新相应的字段
        new_value = item.text()
        if col == 1:  # 奖品名称列
            # 修改名称需要重命名键
            old_key = matched_key
            new_key = new_value
            if old_key != new_key:
                prize_data[new_key] = prize_data.pop(old_key)
        if col == 2:  # 权重列
            prize_data[matched_key]['probability'] = float(new_value)
        
        # 保存更新后的数据
        try:
            with open_file(prize_file, 'w', encoding='utf-8') as f:
                json.dump(prize_data, f, ensure_ascii=False, indent=4)
            logger.info(f"奖品数据更新成功: {prize_name}")
        except Exception as e:
            logger.error(f"保存奖品数据失败: {str(e)}")
            # 如果保存失败，恢复原来的值
            original_value = prize_data[matched_key]['probability'] if col == 2 else "1.0"
            item.setText(str(original_value))


class ImportPrizeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        # 设置无边框但可调整大小的窗口样式
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self.setWindowTitle("导入奖品名单")
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
        self.title_label = QLabel("导入奖品名单")
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
        self.column_mapping = {'序号': -1, '奖品': -1, '权重': -1, '小组': -1}
        self.include_columns = {'权重': True, '小组': True}
        self.processed_data = None
        self.prize_pool_name = None

        self.update_theme_style()
        qconfig.themeChanged.connect(self.update_theme_style)
        self.init_ui()

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
            QLabel, QPushButton, QTextEdit, QLineEdit, QComboBox, QCheckBox {{ color: {colors['text']}; }}
        """)
        
        # 设置标题栏颜色以匹配背景色（仅Windows系统）
        if os.name == 'nt':
            try:
                import ctypes
                # 转换为整数句柄
                hwnd = int(self.winId())
                
                # 颜色格式要改成ARGB才行呢~ 添加透明度通道
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
        # 窗口拖动功能~ 按住标题栏就能移动啦
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

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        # 添加自定义标题栏
        layout.addWidget(self.title_bar)
        # 添加内容区域
        content_layout = QVBoxLayout()
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
        self.type_combo.addItems(["Excel 文件 (*.xlsx)", "CSV 文件 (*.csv)"])
        self.type_combo.currentIndexChanged.connect(self.change_file_type)
        type_layout.addWidget(type_label)
        type_layout.addWidget(self.type_combo)
        content_layout.addLayout(type_layout)

        # 列映射区域
        mapping_group = QGroupBox("") 
        mapping_group.setFont(QFont(load_custom_font(), 12))
        mapping_layout = QFormLayout()

        # 创建列选择控件
        self._create_combo_row(mapping_layout, 'id_combo', '序号列：')
        self._create_combo_row(mapping_layout, 'reward_combo', '奖品列：')
        self._create_checkable_combo_row(mapping_layout, 'probability_combo', 'probability_check', '权重列：', '权重')

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

        # 设置内容区域边距
        content_layout.setContentsMargins(20, 10, 20, 20)
        # 添加内容区域到主布局
        layout.addLayout(content_layout)
        self.setLayout(layout)

    def _create_combo_box(self):
        combo = ComboBox()
        combo.setFont(QFont(load_custom_font(), 12))
        combo.addItem('请选择')
        return combo

    def _create_combo_row(self, layout, combo_attr, label_text):
        row_layout = QHBoxLayout()
        combo = self._create_combo_box()
        setattr(self, combo_attr, combo)
        row_layout.addWidget(combo)
        layout.addRow(label_text, row_layout)

    def _create_checkable_combo_row(self, layout, combo_attr, check_attr, label_text, column_name):
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
        types = ['excel', 'csv']
        self.file_type = types[index]
        
        # 清除并重新加载列数据
        self.file_path_edit.clear()
        self.file_path = None
        self.clear_columns()

    def browse_file(self):
        filters = {
            'excel': "Excel 文件 (*.xlsx)",
            'csv': "CSV 文件 (*.csv)"
        }
        self.file_path, _ = QFileDialog.getOpenFileName(
            self, "选择文件", "", filters[self.file_type]
        )
        if self.file_path:
            self.file_path_edit.setText(self.file_path)
            self.load_columns()

    def clear_columns(self):
        for combo in [self.id_combo, self.reward_combo, self.probability_combo]:
            combo.clear()
            combo.addItem('请选择')
        self.update_mapping()

    def load_columns(self):
        try:
            if self.file_type == 'excel':
                self._load_excel_columns()
            elif self.file_type == 'csv':
                self._load_csv_columns()
        except Warning as w:
            logger.error(f"列选择提示: {str(w)}")
            msg_box = MessageBox("列选择提示", str(w), self)
            msg_box.yesButton.setText("确定")
            msg_box.cancelButton.hide()
            msg_box.buttonLayout.insertStretch(1)
            msg_box.exec_()
        except Exception as e:
            logger.error(f"加载文件列失败: {str(e)}")
            w = MessageBox("加载失败", f"无法读取文件: {str(e)}", self)
            w.yesButton.setText("确定")
            w.cancelButton.hide()
            w.buttonLayout.insertStretch(1)
            w.exec_()
            self.file_path = None
            self.file_path_edit.clear()

    def _init_combo_boxes(self, columns):
        column_items = ['请选择'] + [str(col) for col in columns]
        for combo in [self.id_combo, self.reward_combo, self.probability_combo]:
            combo.clear()
            combo.addItems(column_items)
            combo.setVisible(True)
        self.update_mapping()

    def _auto_select_columns(self, columns):
        fields = [
            (self.id_combo, ['id', '序号', 'rewardid', 'no', 'number', 'prizeid'], True, '序号'),
            (self.reward_combo, ['name', '奖品', 'rewardname', 'prize'], True, '奖品'),
            (self.probability_combo, ['probability', '权重', 'weight'], False, '权重')
        ]

        # 检查是否为数字列名（如CSV文件没有标题行的情况）
        is_numeric_columns = all(str(col).isdigit() for col in columns)
        
        if is_numeric_columns and len(columns) >= 2:
            # 如果列名都是数字，默认第一列作为学号，第二列作为姓名
            self.id_combo.setCurrentIndex(1)  # 第一列
            self.reward_combo.setCurrentIndex(2)  # 第二列
            # 可选列不自动选择
            self.probability_check.setChecked(False)
        else:
            for combo, keywords, is_required, field_name in fields:
                # 自动选择匹配项
                auto_selected = False
                for i, col in enumerate(columns):
                    if any(key in col.lower() for key in keywords):
                        combo.setCurrentIndex(i + 1)  # +1是因为第一个选项是"请选择"
                        auto_selected = True
                        break

                # 必选列验证
                self._validate_required_column(combo, is_required, field_name, columns)

                # 可选列未找到匹配时取消勾选
                if not is_required and not auto_selected:
                    if field_name == '权重':
                        self.probability_check.setChecked(False)

        self.update_mapping()
        self._validate_mandatory_columns()

    def _validate_required_column(self, combo, is_required, field_name, columns):
        if is_required and combo.currentIndex() == 0:  # 0表示"请选择"
            if columns:
                combo.setCurrentIndex(1)  # 选择第一列数据
                raise Warning(f"已自动选择第一列作为{field_name}列，请确认是否正确")
            else:
                raise Exception(f"必须选择{field_name}对应的列")

    def _validate_mandatory_columns(self):
        if self.column_mapping['序号'] == -1:
            raise Exception("必须选择序号对应的列")
        if self.column_mapping['奖品'] == -1:
            raise Exception("必须选择奖品对应的列")

    def _load_excel_columns(self):
        df = pd.read_excel(self.file_path)
        columns = list(df.columns)
        self._init_combo_boxes(columns)
        self._auto_select_columns(columns)

    def _load_csv_columns(self):
        df = self._read_csv_file(self.file_path)
        columns = list(df.columns)
        self._init_combo_boxes(columns)
        self._auto_select_columns(columns)

    def update_mapping(self):
        self.column_mapping['序号'] = self.id_combo.currentIndex() - 1 if self.id_combo.currentIndex() > 0 else -1
        self.column_mapping['奖品'] = self.reward_combo.currentIndex() - 1 if self.reward_combo.currentIndex() > 0 else -1
        self.column_mapping['权重'] = self.probability_combo.currentIndex() - 1 if (self.probability_check.isChecked() and self.probability_combo.currentIndex() > 0) else -1

    def toggle_column(self, column):
        self.include_columns[column] = not self.include_columns[column]
        self.update_mapping()

    def accept(self):
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
            if not hasattr(self.parent(), 'prize_pools_comboBox'):
                raise Exception("无法获取班级信息，请确保主界面已正确加载")
            self.prize_pool_name = self.parent().prize_pools_comboBox.currentText()
            
            self.processed_data = self._import_data()
            self._show_success_message("导入成功", f"奖品名单导入成功！\n共导入 {len(self.processed_data)} 条记录")
            super().accept()
        except Exception as e:
            logger.error(f"导入失败: {str(e)}")
            self._show_error_message("导入失败", f"导入过程中出错: {str(e)}")

    def _read_csv_file(self, file_path):
        encodings = ['gbk', 'gb2312', 'utf-8', 'latin-1', 'iso-8859-1', 'cp936']
        found_encoding = None
        found_sep = None
        df = None
        
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
        file_ext = os.path.splitext(self.file_path)[1].lower()
        
        # 根据扩展名选择读取方法
        if file_ext in ['.xlsx', '.xls']:
            df = pd.read_excel(self.file_path)
        elif file_ext == '.csv':
            df = self._read_csv_file(self.file_path)
        else:
            raise Exception(f"不支持的文件类型: {file_ext}，请使用Excel或CSV文件")

        # 获取列映射
        id_col = self.column_mapping['序号']
        reward_col = self.column_mapping['奖品']
        probability_col = self.column_mapping['权重']

        # 处理学生数据
        reward_data = {}
        for index, row in df.iterrows():
            # 获取序号和奖品（必选字段）
            # 提取并清理序号和奖品（去除空白字符）
            reward_id = str(row.iloc[id_col]).strip()
            reward_name = str(row.iloc[reward_col]).strip()

            # 验证必填字段（确保不为空）
            if not reward_id or not reward_name:
                continue

            # 创建学生信息字典
            # 处理权重字段转换（针对NamePicker格式）
            probability_value = str(row.iloc[probability_col]) if probability_col != -1 and not pd.isna(row.iloc[probability_col]) else ""
            
            reward_data[reward_name] = {
                'id': int(reward_id) if reward_id.isdigit() else index + 1,
                'probability': probability_value,
            }

        return reward_data

    def _show_error_message(self, title, message):
        w = MessageBox(title, message, self)
        w.yesButton.setText("确定")
        w.cancelButton.hide()
        w.buttonLayout.insertStretch(1)
        w.exec_()

    def _show_success_message(self, title, message):
        w = MessageBox(title, message, self)
        w.yesButton.setText("确定")
        w.cancelButton.hide()
        w.buttonLayout.insertStretch(1)
        w.exec_()

    def _validate_excel(self):
        if self.id_combo.currentIndex() <= 0:
            self._show_error_message("序号列未选择", "请选择有效的序号列！")
            return False

        if self.reward_combo.currentIndex() <= 0:
            self._show_error_message("奖品列未选择", "请选择有效的奖品列！")
            return False

        # 可选列未选择时自动取消勾选
        if self.probability_check.isChecked() and self.probability_combo.currentIndex() <= 0:
            self.probability_check.setChecked(False)

        # 验证列选择唯一性
        selected_columns = []
        if self.id_combo.currentIndex() > 0:
            selected_columns.append(self.id_combo.currentIndex() - 1)
        if self.reward_combo.currentIndex() > 0:
            selected_columns.append(self.reward_combo.currentIndex() - 1)
        if self.probability_check.isChecked() and self.probability_combo.currentIndex() > 0:
            selected_columns.append(self.probability_combo.currentIndex() - 1)

        # 检查重复选择
        if len(selected_columns) != len(set(selected_columns)):
            self._show_error_message("列选择错误", "不能选择重复的列！请确保所有选中的列都是唯一的。")
            return False

        return True

    def _validate_csv_json(self):
        if self.id_combo.currentIndex() <= 0:
            self._show_error_message("序号列未选择", "请选择有效的序号列！")
            return False

        if self.reward_combo.currentIndex() <= 0:
            self._show_error_message("奖品列未选择", "请选择有效的奖品列！")
            return False

        # 可选列未选择时自动取消勾选
        if self.probability_check.isChecked() and self.probability_combo.currentIndex() <= 0:
            self.probability_check.setChecked(False)

        # 验证列选择唯一性
        selected_columns = []
        if self.id_combo.currentIndex() > 0:
            selected_columns.append(self.id_combo.currentIndex() - 1)
        if self.reward_combo.currentIndex() > 0:
            selected_columns.append(self.reward_combo.currentIndex() - 1)
        if self.probability_check.isChecked() and self.probability_combo.currentIndex() > 0:
            selected_columns.append(self.probability_combo.currentIndex() - 1)

        # 检查重复选择
        if len(selected_columns) != len(set(selected_columns)):
            self._show_error_message("列选择错误", "不能选择重复的列！请确保所有选中的列都是唯一的。")
            return False

        return True

    def get_processed_data(self):
        return self.processed_data, self.prize_pool_name

    def get_result(self):
        return self.file_path, self.file_type, self.column_mapping


class Prize_pools_InputDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("输入奖池名称")
        # 设置无边框但可调整大小的窗口样式
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self.setMinimumSize(400, 335)  # 设置最小大小而不是固定大小
        self.saved = False
        
        # 创建自定义标题栏
        self.title_bar = QWidget()
        self.title_bar.setObjectName("CustomTitleBar")
        self.title_bar.setFixedHeight(35)
        title_layout = QHBoxLayout(self.title_bar)
        title_layout.setContentsMargins(10, 0, 10, 0)
        title_layout.setSpacing(0)
        
        # 标题标签
        self.title_label = QLabel("输入奖池名称")
        self.title_label.setObjectName("TitleLabel")
        self.title_label.setFont(QFont(load_custom_font(), 12, QFont.Bold))
        
        # 关闭按钮
        self.close_button = QPushButton("×")
        self.close_button.setObjectName("CloseButton")
        self.close_button.setFixedSize(25, 25)
        self.close_button.clicked.connect(self.reject)
        
        # 添加到标题栏布局
        title_layout.addWidget(self.title_label)
        title_layout.addStretch(1)
        title_layout.addWidget(self.close_button)
        
        # 窗口拖动属性
        self.dragging = False
        self.drag_position = QPoint()
        
        self.text_label = BodyLabel('请输入奖池名称，每行一个')
        self.text_label.setFont(QFont(load_custom_font(), 12))

        self.update_theme_style()
        qconfig.themeChanged.connect(self.update_theme_style)
        
        self.textEdit = PlainTextEdit()
        self.textEdit.setPlaceholderText("请输入奖池名称，每行一个")
        self.textEdit.setFont(QFont(load_custom_font(), 12))
        
        self.setFont(QFont(load_custom_font(), 12))

        try:
            app_dir = path_manager._app_root
            list_folder = app_dir / 'app' / 'resource' / 'reward'
            if list_folder.exists() and list_folder.is_dir():
                files = list(list_folder.iterdir())
                prizes = []
                for file in files:
                    if file.suffix == '.json':
                        prize_pools_name = file.stem
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
        
        # 创建主布局
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 添加自定义标题栏
        layout.addWidget(self.title_bar)
        
        # 创建内容区域布局
        content_layout = QVBoxLayout()
        content_layout.setSpacing(10)
        content_layout.addWidget(self.text_label)
        content_layout.addWidget(self.textEdit)
        
        # 按钮区域
        buttonLayout = QHBoxLayout()
        buttonLayout.addStretch(1)
        buttonLayout.addWidget(self.cancelButton)
        buttonLayout.addWidget(self.saveButton)
        
        content_layout.addLayout(buttonLayout)
        
        # 设置内容区域边距
        content_layout.setContentsMargins(20, 10, 20, 20)
        
        # 添加内容区域到主布局
        layout.addLayout(content_layout)
        
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
            QLabel, QPushButton, QTextEdit, QLineEdit, QComboBox, QCheckBox {{ color: {colors['text']}; }}
        """)
        
        # 设置标题栏颜色以匹配背景色（仅Windows系统）
        if os.name == 'nt':
            try:
                import ctypes
                # 转换为整数句柄
                hwnd = int(self.winId())
                
                # 颜色格式要改成ARGB才行呢~ 添加透明度通道
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
                logger.error(f"设置标题栏颜色失败：{str(e)}")
        
    def mousePressEvent(self, event):
        # 窗口拖动功能~ 按住标题栏就能移动啦
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
        # 设置无边框但可调整大小的窗口样式
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self.setMinimumSize(400, 635)  # 设置最小大小而不是固定大小
        self.saved = False
        
        # 创建自定义标题栏
        self.title_bar = QWidget()
        self.title_bar.setObjectName("CustomTitleBar")
        self.title_bar.setFixedHeight(35)
        title_layout = QHBoxLayout(self.title_bar)
        title_layout.setContentsMargins(10, 0, 10, 0)
        title_layout.setSpacing(0)
        
        # 标题标签
        self.title_label = QLabel("输入奖品名称")
        self.title_label.setObjectName("TitleLabel")
        self.title_label.setFont(QFont(load_custom_font(), 12, QFont.Bold))
        
        # 关闭按钮
        self.close_button = QPushButton("×")
        self.close_button.setObjectName("CloseButton")
        self.close_button.setFixedSize(25, 25)
        self.close_button.clicked.connect(self.reject)
        
        # 添加到标题栏布局
        title_layout.addWidget(self.title_label)
        title_layout.addStretch(1)
        title_layout.addWidget(self.close_button)
        
        # 窗口拖动属性
        self.dragging = False
        self.drag_position = QPoint()

        # 创建主布局
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # 添加标题栏到主布局
        self.main_layout.addWidget(self.title_bar)
        
        # 创建内容区域布局
        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(20, 10, 20, 20)
        self.content_layout.setSpacing(10)
        
        # 内容区域组件
        self.text_label = BodyLabel('请输入奖品名称，每行一个')
        self.text_label.setFont(QFont(load_custom_font(), 12))

        self.update_theme_style()
        qconfig.themeChanged.connect(self.update_theme_style)
        
        self.textEdit = PlainTextEdit()
        self.textEdit.setPlaceholderText("请输入奖品名称，每行一个")
        self.textEdit.setFont(QFont(load_custom_font(), 12))
        
        self.setFont(QFont(load_custom_font(), 12))
        
        prize_pools_name = self.parent().prize_pools_comboBox.currentText()
        reward_dir = path_manager.get_resource_path('reward')
        prize_file = reward_dir / f'{prize_pools_name}.json'
        try:
            with open_file(prize_file, 'r', encoding='utf-8') as f:
                file_content = f.read()
                if not file_content.strip():
                    # 处理空文件情况
                    logger.error(f"JSON文件为空: {prize_file}")
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
            logger.error(f"文件未找到: {prize_file}")
        except json.JSONDecodeError:
            logger.error("JSON文件格式错误，请检查文件内容")
        
        self.saveButton = PrimaryPushButton("保存")
        self.cancelButton = PushButton("取消")
        self.saveButton.clicked.connect(self.accept)
        self.cancelButton.clicked.connect(self.reject)
        self.saveButton.setFont(QFont(load_custom_font(), 12))
        self.cancelButton.setFont(QFont(load_custom_font(), 12))
        
        # 添加组件到内容区域布局
        self.content_layout.addWidget(self.text_label)
        self.content_layout.addWidget(self.textEdit)
        
        buttonLayout = QHBoxLayout()
        buttonLayout.addStretch(1)
        buttonLayout.addWidget(self.cancelButton)
        buttonLayout.addWidget(self.saveButton)
        
        self.content_layout.addLayout(buttonLayout)
        
        # 添加内容区域布局到主布局
        self.main_layout.addLayout(self.content_layout)
        
        # 设置主布局
        self.setLayout(self.main_layout)

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
            QLabel, QPushButton, QTextEdit, QLineEdit, QComboBox, QCheckBox {{ color: {colors['text']}; }}
        """)
        
        # 设置标题栏颜色以匹配背景色（仅Windows系统）
        if os.name == 'nt':
            try:
                import ctypes
                # 转换为整数句柄
                hwnd = int(self.winId())
                
                # 颜色格式要改成ARGB才行呢~ 添加透明度通道
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
        # 设置无边框但可调整大小的窗口样式
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self.setMinimumSize(400, 435)  # 设置最小大小而不是固定大小
        self.saved = False
        
        # 创建自定义标题栏
        self.title_bar = QWidget()
        self.title_bar.setObjectName("CustomTitleBar")
        self.title_bar.setFixedHeight(35)
        title_layout = QHBoxLayout(self.title_bar)
        title_layout.setContentsMargins(10, 0, 10, 0)
        title_layout.setSpacing(0)
        
        # 标题标签
        self.title_label = QLabel("输入每项奖品对应的权重")
        self.title_label.setObjectName("TitleLabel")
        self.title_label.setFont(QFont(load_custom_font(), 12, QFont.Bold))
        
        # 关闭按钮
        self.close_button = QPushButton("×")
        self.close_button.setObjectName("CloseButton")
        self.close_button.setFixedSize(25, 25)
        self.close_button.clicked.connect(self.reject)
        
        # 添加到标题栏布局
        title_layout.addWidget(self.title_label)
        title_layout.addStretch(1)
        title_layout.addWidget(self.close_button)
        
        # 窗口拖动属性
        self.dragging = False
        self.drag_position = QPoint()

        # 创建主布局
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # 添加标题栏到主布局
        self.main_layout.addWidget(self.title_bar)
        
        # 创建内容区域布局
        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(20, 10, 20, 20)
        self.content_layout.setSpacing(10)
        
        # 内容区域组件
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
        reward_dir = path_manager.get_resource_path('reward')
        prize_file = reward_dir / f'{prize_pools_name}.json'
        try:
            with open_file(prize_file, 'r', encoding='utf-8') as f:
                file_content = f.read()
                if not file_content.strip():
                    logger.error(f"JSON文件为空: {prize_file}")
                    return
                data = json.loads(file_content)
                if isinstance(data, dict):
                    probability_list = []
                    sorted_students = sorted(data.values(), key=lambda x: x.get("id", 0))
                    for student in sorted_students:
                        if student.get("id", 0) >= 1:
                            probability_list.append(student.get("probability", "1.0"))
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
        
        # 添加组件到内容区域布局
        self.content_layout.addWidget(self.text_label)
        self.content_layout.addWidget(self.textEdit)
        
        buttonLayout = QHBoxLayout()
        buttonLayout.addStretch(1)
        buttonLayout.addWidget(self.cancelButton)
        buttonLayout.addWidget(self.saveButton)
        
        self.content_layout.addLayout(buttonLayout)
        
        # 添加内容区域布局到主布局
        self.main_layout.addLayout(self.content_layout)
        
        # 设置主布局
        self.setLayout(self.main_layout)

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
            QLabel, QPushButton, QTextEdit, QLineEdit, QComboBox, QCheckBox {{ color: {colors['text']}; }}
        """)
        
        # 设置标题栏颜色以匹配背景色（仅Windows系统）
        if os.name == 'nt':
            try:
                import ctypes
                # 转换为整数句柄
                hwnd = int(self.winId())
                
                # 颜色格式要改成ARGB才行呢~ 添加透明度通道
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