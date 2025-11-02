# ==================================================
# 导入库
# ==================================================

from loguru import logger
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtNetwork import *
from qfluentwidgets import *

from app.tools.variable import *
from app.tools.path_utils import *
from app.tools.personalised import *
from app.tools.settings_default import *
from app.tools.settings_access import *
from app.Language.obtain_language import *
from app.tools.history import *

# ==================================================
# 点名历史记录表格
# ==================================================


class roll_call_history_table(GroupHeaderCardWidget):
    """点名历史记录表格卡片"""

    refresh_signal = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setTitle(get_content_name_async("roll_call_history_table", "title"))
        self.setBorderRadius(8)
        # 创建班级选择区域
        QTimer.singleShot(APPLY_DELAY, self.create_class_selection)

        # 创建表格区域
        QTimer.singleShot(APPLY_DELAY, self.create_table)

        # 创建按钮区域
        QTimer.singleShot(APPLY_DELAY, self.create_buttons)

        # 初始化班级列表
        QTimer.singleShot(APPLY_DELAY, self.refresh_class_history)

        # 设置文件系统监视器
        QTimer.singleShot(APPLY_DELAY, self.setup_file_watcher)

        # 初始化数据
        QTimer.singleShot(APPLY_DELAY, self.refresh_data)

        # 连接信号
        self.refresh_signal.connect(self.refresh_data)

    def create_class_selection(self):
        """创建班级选择区域"""
        self.class_comboBox = ComboBox()
        self.class_comboBox.setCurrentIndex(
            readme_settings_async("roll_call_history_table", "select_class_name")
        )
        if not get_class_name_history():
            self.class_comboBox.setCurrentIndex(-1)
            self.class_comboBox.setPlaceholderText(
                get_content_name_async("roll_call_history_table", "select_class_name")
            )
        self.class_comboBox.currentIndexChanged.connect(self.on_class_changed)
        self.class_comboBox.currentTextChanged.connect(
            lambda: self.on_class_changed(-1)
        )

        # 选择查看模式
        self.mode_comboBox = ComboBox()
        self.mode_comboBox.addItems(
            get_content_combo_name_async("roll_call_history_table", "select_mode")
        )
        self.mode_comboBox.setCurrentIndex(
            readme_settings_async("roll_call_history_table", "select_mode")
        )
        self.mode_comboBox.currentIndexChanged.connect(
            lambda: update_settings(
                "roll_call_history_table",
                "select_mode",
                self.mode_comboBox.currentIndex(),
            )
        )
        self.mode_comboBox.currentTextChanged.connect(self.refresh_data)

        self.addGroup(
            get_theme_icon("ic_fluent_class_20_filled"),
            get_content_name_async("roll_call_history_table", "select_class_name"),
            get_content_description_async(
                "roll_call_history_table", "select_class_name"
            ),
            self.class_comboBox,
        )
        self.addGroup(
            get_theme_icon("ic_fluent_reading_mode_mobile_20_filled"),
            get_content_name_async("roll_call_history_table", "select_mode"),
            get_content_description_async("roll_call_history_table", "select_mode"),
            self.mode_comboBox,
        )

    def create_buttons(self):
        """创建按钮区域"""
        # 创建清除历史记录按钮
        self.clear_button = PushButton(
            get_content_name_async("roll_call_history_table", "clear_history")
        )
        self.clear_button.clicked.connect(self.clear_history)
        self.clear_button.setEnabled(False)

        # 添加按钮到布局
        self.addGroup(
            get_theme_icon("ic_fluent_delete_20_filled"),
            get_content_name_async("roll_call_history_table", "clear_history"),
            get_content_description_async("roll_call_history_table", "clear_history"),
            self.clear_button,
        )

    def clear_history(self):
        """清除当前班级的历史记录"""
        class_name = self.class_comboBox.currentText()
        if not class_name:
            return

        # 确认对话框
        reply = QMessageBox.question(
            self,
            get_content_name_async("roll_call_history_table", "confirm_clear_title"),
            get_content_name_async(
                "roll_call_history_table", "confirm_clear_message"
            ).format(class_name=class_name),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            # 调用清除历史记录函数
            from app.tools.history import clear_roll_call_history

            success = clear_roll_call_history(class_name)

            if success:
                # 显示成功消息
                QMessageBox.information(
                    self,
                    get_content_name_async(
                        "roll_call_history_table", "clear_success_title"
                    ),
                    get_content_name_async(
                        "roll_call_history_table", "clear_success_message"
                    ).format(class_name=class_name),
                )
                # 刷新数据
                self.refresh_class_history()
            else:
                # 显示错误消息
                QMessageBox.critical(
                    self,
                    get_content_name_async(
                        "roll_call_history_table", "clear_error_title"
                    ),
                    get_content_name_async(
                        "roll_call_history_table", "clear_error_message"
                    ).format(class_name=class_name),
                )

    def create_table(self):
        """创建表格区域"""
        # 创建表格
        self.table = TableWidget()
        self.table.setBorderVisible(True)
        self.table.setBorderRadius(8)
        self.table.setWordWrap(False)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSortingEnabled(True)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.verticalHeader().hide()

        # 根据当前选择的模式设置表格头
        self.update_table_headers()

        # 设置表格属性
        for i in range(self.table.columnCount()):
            self.table.horizontalHeader().setSectionResizeMode(
                i, QHeaderView.ResizeMode.Stretch
            )
            self.table.horizontalHeader().setDefaultAlignment(
                Qt.AlignmentFlag.AlignCenter
            )
        self.layout().addWidget(self.table)

    def update_table_headers(self):
        """根据选择的模式更新表格头"""
        # 检查mode_comboBox是否存在
        if not hasattr(self, "mode_comboBox"):
            # 如果mode_comboBox不存在，使用默认模式
            headers = get_content_name_async(
                "roll_call_history_table", "HeaderLabels_all_not_weight"
            )
            self.table.setColumnCount(len(headers))
            self.table.setHorizontalHeaderLabels(headers)
            return

        # 获取当前选择的模式
        mode_index = self.mode_comboBox.currentIndex()
        mode_items = get_content_combo_name_async(
            "roll_call_history_table", "select_mode"
        )

        if mode_index >= 0 and mode_index < len(mode_items):
            mode = mode_items[mode_index]

            # 根据模式设置表格头和列数
            if mode == "全部":
                # 默认显示不包含权重的全部信息
                headers = get_content_name_async(
                    "roll_call_history_table", "HeaderLabels_all_not_weight"
                )
                self.table.setColumnCount(len(headers))
                self.table.setHorizontalHeaderLabels(headers)
            elif mode == "时间":
                # 显示时间模式
                headers = get_content_name_async(
                    "roll_call_history_table", "HeaderLabels_time"
                )
                self.table.setColumnCount(len(headers))
                self.table.setHorizontalHeaderLabels(headers)
            elif mode == "个人":
                # 显示个人统计模式
                headers = get_content_name_async(
                    "roll_call_history_table", "HeaderLabels_Individual"
                )
                self.table.setColumnCount(len(headers))
                self.table.setHorizontalHeaderLabels(headers)
            else:
                # 默认使用不包含权重的全部信息
                headers = get_content_name_async(
                    "roll_call_history_table", "HeaderLabels_all_not_weight"
                )
                self.table.setColumnCount(len(headers))
                self.table.setHorizontalHeaderLabels(headers)
        else:
            # 默认使用不包含权重的全部信息
            headers = get_content_name_async(
                "roll_call_history_table", "HeaderLabels_all_not_weight"
            )
            self.table.setColumnCount(len(headers))
            self.table.setHorizontalHeaderLabels(headers)

    def setup_file_watcher(self):
        """设置文件系统监视器，监控班级历史记录文件夹的变化"""
        # 获取班级历史记录文件夹路径
        roll_call_history_dir = get_path("app/resources/history/roll_call_history")

        # 确保目录存在
        if not roll_call_history_dir.exists():
            logger.warning(f"班级历史记录文件夹不存在: {roll_call_history_dir}")
            return

        # 创建文件系统监视器
        self.file_watcher = QFileSystemWatcher()

        # 监视目录
        self.file_watcher.addPath(str(roll_call_history_dir))

        # 连接信号
        self.file_watcher.directoryChanged.connect(self.on_directory_changed)
        # logger.debug(f"已设置文件监视器，监控目录: {roll_call_history_dir}")

    def on_directory_changed(self, path):
        """当目录内容发生变化时调用此方法

        Args:
            path: 发生变化的目录路径
        """
        # logger.debug(f"检测到目录变化: {path}")
        # 延迟刷新，避免文件操作未完成
        QTimer.singleShot(1000, self.refresh_class_history)

    def refresh_class_history(self):
        """刷新班级下拉框列表"""
        # 检查class_comboBox是否存在
        if not hasattr(self, "class_comboBox"):
            return

        # 保存当前选中的班级名称
        current_class_name = self.class_comboBox.currentText()

        # 获取最新的班级列表
        class_history = get_class_name_history()

        # 清空并重新添加班级列表
        self.class_comboBox.clear()
        self.class_comboBox.addItems(class_history)

        # 尝试恢复之前选中的班级
        if current_class_name and current_class_name in class_history:
            index = class_history.index(current_class_name)
            self.class_comboBox.setCurrentIndex(index)
        elif not class_history:
            self.class_comboBox.setCurrentIndex(-1)
            self.class_comboBox.setPlaceholderText(
                get_content_name_async("roll_call_history_table", "select_class_name")
            )

        # 启用或禁用清除按钮
        if hasattr(self, "clear_button"):
            self.clear_button.setEnabled(bool(current_class_name))

    def on_class_changed(self, index):
        """班级选择变化时刷新表格数据"""
        # 检查class_comboBox是否存在
        if not hasattr(self, "class_comboBox"):
            return

        # 更新设置（当index有效时）
        if index >= 0:
            update_settings("roll_call_history_table", "select_class_name", index)

        # 更新清除按钮状态
        if hasattr(self, "clear_button"):
            self.clear_button.setEnabled(self.class_comboBox.currentIndex() >= 0)

        # 刷新表格数据
        self.refresh_data()

        # logger.debug(f"班级列表已刷新，共 {len(class_history)} 个班级")
        # 只有在表格已经创建时才刷新数据
        if hasattr(self, "table"):
            self.refresh_data()

    def refresh_data(self):
        """刷新表格数据"""
        # 确保表格已经创建
        if not hasattr(self, "table"):
            return

        # 检查class_comboBox是否存在
        if not hasattr(self, "class_comboBox"):
            return

        class_name = self.class_comboBox.currentText()
        if not class_name:
            self.table.setRowCount(0)
            return

        # 更新表格头
        self.update_table_headers()

        # 临时阻止信号，避免初始化时触发保存操作
        self.table.blockSignals(True)

        try:
            # 检查mode_comboBox是否存在
            if not hasattr(self, "mode_comboBox"):
                # 如果mode_comboBox不存在，使用默认模式
                self.fill_all_students_data(class_name)
                return

            # 获取当前选择的模式
            mode_index = self.mode_comboBox.currentIndex()
            mode_items = get_content_combo_name_async(
                "roll_call_history_table", "select_mode"
            )

            if mode_index >= 0 and mode_index < len(mode_items):
                mode = mode_items[mode_index]

                # 根据模式获取不同的数据
                if mode == "全部":
                    # 获取学生数据
                    self.fill_all_students_data(class_name)
                elif mode == "时间":
                    # 获取时间模式数据
                    self.fill_time_mode_data(class_name)
                elif mode == "个人":
                    # 获取个人统计模式数据
                    self.fill_individual_mode_data(class_name)
                else:
                    # 默认使用全部模式
                    self.fill_all_students_data(class_name)
            else:
                # 默认使用全部模式
                self.fill_all_students_data(class_name)

            # 调整列宽
            for i in range(self.table.columnCount()):
                self.table.horizontalHeader().setSectionResizeMode(
                    i, QHeaderView.ResizeMode.Stretch
                )
                self.table.horizontalHeader().setDefaultAlignment(
                    Qt.AlignmentFlag.AlignCenter
                )

        except Exception as e:
            logger.error(f"刷新表格数据失败: {str(e)}")
        finally:
            # 恢复信号
            self.table.blockSignals(False)

    def fill_all_students_data(self, class_name: str):
        """填充全部学生数据

        Args:
            class_name: 班级名称
        """
        # 获取学生数据
        students = get_student_history(class_name)
        if not students:
            self.table.setRowCount(0)
            return

        # 设置表格行数
        self.table.setRowCount(len(students))

        # 填充表格数据
        for row, student in enumerate(students):
            # 学号
            id_item = QTableWidgetItem(
                str(student.get("student_id", student.get("id", row + 1)))
            )
            id_item.setFlags(
                id_item.flags() & ~Qt.ItemFlag.ItemIsEditable
            )  # 学号不可编辑
            id_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 0, id_item)

            # 姓名
            name_item = QTableWidgetItem(student.get("name", ""))
            name_item.setFlags(
                name_item.flags() & ~Qt.ItemFlag.ItemIsEditable
            )  # 姓名不可编辑
            name_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 1, name_item)

            # 性别
            gender_item = QTableWidgetItem(student.get("gender", ""))
            gender_item.setFlags(
                gender_item.flags() & ~Qt.ItemFlag.ItemIsEditable
            )  # 性别不可编辑
            gender_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 2, gender_item)

            # 小组
            group_item = QTableWidgetItem(student.get("group", ""))
            group_item.setFlags(
                group_item.flags() & ~Qt.ItemFlag.ItemIsEditable
            )  # 小组不可编辑
            group_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 3, group_item)

            # 总次数
            total_count_item = QTableWidgetItem(str(student.get("total_count", 0)))
            total_count_item.setFlags(
                total_count_item.flags() & ~Qt.ItemFlag.ItemIsEditable
            )  # 总次数不可编辑
            total_count_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 4, total_count_item)

    def fill_time_mode_data(self, class_name: str):
        """填充时间模式数据

        Args:
            class_name: 班级名称
        """
        # 获取抽取会话数据
        sessions = get_draw_sessions_history(class_name)
        if not sessions:
            self.table.setRowCount(0)
            return

        # 设置表格行数
        self.table.setRowCount(len(sessions))

        # 填充表格数据
        for row, session in enumerate(sessions):
            # 时间
            time_item = QTableWidgetItem(session.get("timestamp", ""))
            time_item.setFlags(
                time_item.flags() & ~Qt.ItemFlag.ItemIsEditable
            )  # 时间不可编辑
            time_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 0, time_item)

            # 学号
            selected_students = session.get("selected_students", [])
            student_ids = []
            for student in selected_students:
                student_ids.append(str(student.get("student_id", "")))

            id_item = QTableWidgetItem(", ".join(student_ids))
            id_item.setFlags(
                id_item.flags() & ~Qt.ItemFlag.ItemIsEditable
            )  # 学号不可编辑
            id_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 1, id_item)

            # 姓名（显示选中学生的姓名列表）
            names = [student.get("name", "") for student in selected_students]
            name_item = QTableWidgetItem(", ".join(names))
            name_item.setFlags(
                name_item.flags() & ~Qt.ItemFlag.ItemIsEditable
            )  # 姓名不可编辑
            name_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 2, name_item)

            # 性别
            gender = session.get("parameters", {}).get("gender", "全部")
            gender_item = QTableWidgetItem(str(gender) if gender else "全部")
            gender_item.setFlags(
                gender_item.flags() & ~Qt.ItemFlag.ItemIsEditable
            )  # 性别不可编辑
            gender_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 3, gender_item)

            # 小组
            group = session.get("parameters", {}).get("group", "全部")
            group_item = QTableWidgetItem(str(group) if group else "全部")
            group_item.setFlags(
                group_item.flags() & ~Qt.ItemFlag.ItemIsEditable
            )  # 小组不可编辑
            group_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 4, group_item)

    def fill_individual_mode_data(self, class_name: str):
        """填充个人统计模式数据

        Args:
            class_name: 班级名称
        """
        # 获取个人统计数据
        stats = get_individual_statistics(class_name)
        if not stats:
            self.table.setRowCount(0)
            return

        # 设置表格行数
        self.table.setRowCount(len(stats))

        # 填充表格数据
        for row, stat in enumerate(stats):
            # 时间
            time_item = QTableWidgetItem(stat.get("time", ""))
            time_item.setFlags(
                time_item.flags() & ~Qt.ItemFlag.ItemIsEditable
            )  # 时间不可编辑
            time_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 0, time_item)

            # 模式
            mode_item = QTableWidgetItem(stat.get("mode", ""))
            mode_item.setFlags(
                mode_item.flags() & ~Qt.ItemFlag.ItemIsEditable
            )  # 模式不可编辑
            mode_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 1, mode_item)

            # 人数
            people_count_item = QTableWidgetItem(str(stat.get("count", 0)))
            people_count_item.setFlags(
                people_count_item.flags() & ~Qt.ItemFlag.ItemIsEditable
            )  # 人数不可编辑
            people_count_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 2, people_count_item)

            # 性别
            gender = stat.get("parameters", {}).get("gender", "全部")
            gender_item = QTableWidgetItem(str(gender) if gender else "全部")
            gender_item.setFlags(
                gender_item.flags() & ~Qt.ItemFlag.ItemIsEditable
            )  # 性别不可编辑
            gender_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 3, gender_item)

            # 小组
            group = stat.get("parameters", {}).get("group", "全部")
            group_item = QTableWidgetItem(str(group) if group else "全部")
            group_item.setFlags(
                group_item.flags() & ~Qt.ItemFlag.ItemIsEditable
            )  # 小组不可编辑
            group_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 4, group_item)
