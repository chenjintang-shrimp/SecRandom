from qfluentwidgets import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from app.common.config import load_custom_font


class VocabularyPKSettingsDialog(QDialog):
    """单词PK设置对话框"""
    
    def __init__(self, parent=None, settings=None):
        super().__init__(parent)
        self.settings = settings or {}
        self.initUI()
        
    def initUI(self):
        # 设置对话框属性
        self.setWindowTitle("单词PK设置")
        self.setFixedSize(700, 700)  # 增加对话框尺寸以容纳美化后的布局
        self.setWindowModality(Qt.ApplicationModal)  # 设置为模态对话框
        
        # 创建主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(20)
        
        # 创建标题区域
        title_widget = QWidget()
        title_layout = QHBoxLayout(title_widget)
        title_layout.setContentsMargins(0, 0, 0, 0)
        
        # 添加图标
        title_icon = IconWidget(FluentIcon.SETTING)
        title_icon.setFixedSize(24, 24)
        title_layout.addWidget(title_icon)
        
        # 创建标题
        title_label = TitleLabel("单词PK设置")
        title_label.setAlignment(Qt.AlignLeft)
        title_label.setFont(QFont(load_custom_font(), 18, QFont.Bold))
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        
        main_layout.addWidget(title_widget)
        
        # 创建设置区域卡片
        settings_card = CardWidget()
        settings_card_layout = QVBoxLayout(settings_card)
        settings_card_layout.setContentsMargins(20, 20, 20, 20)
        settings_card_layout.setSpacing(16)
        
        # 导入词汇表按钮区域
        import_button_layout = QHBoxLayout()
        import_button_layout.addStretch()
        
        self.import_button = PrimaryPushButton("导入词汇表")
        self.import_button.setFont(QFont(load_custom_font(), 12))
        self.import_button.setFixedWidth(160)
        self.import_button.setIcon(FluentIcon.ADD_TO)
        self.import_button.clicked.connect(self.on_import_vocabulary_clicked)
        import_button_layout.addWidget(self.import_button)
        
        # 添加删除词汇表按钮
        self.delete_button = PushButton("删除该词汇表")
        self.delete_button.setFont(QFont(load_custom_font(), 12))
        self.delete_button.setFixedWidth(160)
        self.delete_button.setIcon(FluentIcon.DELETE)
        self.delete_button.clicked.connect(self.on_delete_vocabulary_clicked)
        import_button_layout.addWidget(self.delete_button)
        
        import_button_layout.addStretch()
        settings_card_layout.addLayout(import_button_layout)
        
        # 添加分割线
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        settings_card_layout.addWidget(line)
        
        # 基础设置区域
        basic_group = QGroupBox("基础设置")
        basic_group.setFont(QFont(load_custom_font(), 12))
        basic_layout = QFormLayout(basic_group)
        basic_layout.setLabelAlignment(Qt.AlignRight)
        basic_layout.setFormAlignment(Qt.AlignLeft)
        basic_layout.setSpacing(15)

        basic_group.setStyleSheet("QGroupBox { border: 1px solid #cccccc; border-radius: 6px; margin-top: 12px; } "
                                 "QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 3px 0 3px; }")   
        
        # 词汇表选择
        vocabulary_label = BodyLabel("词汇表:")
        vocabulary_label.setFont(QFont(load_custom_font(), 12))
        self.vocabulary_combo = ComboBox()
        # 获取可用的词汇文件列表
        available_vocabularies = self.settings.get('available_vocabularies', ["未添加词库"])
        if available_vocabularies:
            self.vocabulary_combo.addItems(available_vocabularies)
            self.vocabulary_combo.setCurrentText(self.settings.get('current_vocabulary', available_vocabularies[0]))
        else:
            # 如果没有可用的词汇文件，添加默认选项
            self.vocabulary_combo.addItems(["未添加词库"])
            self.vocabulary_combo.setCurrentText("未添加词库")
        self.vocabulary_combo.setFont(QFont(load_custom_font(), 12))
        basic_layout.addRow(vocabulary_label, self.vocabulary_combo)

        # 学习模式设置
        repeat_label = BodyLabel("学习模式:")
        repeat_label.setFont(QFont(load_custom_font(), 12))
        self.repeat_mode_combo = ComboBox()
        self.repeat_mode_combo.addItems(["重复模式", "不重复模式"])
        self.repeat_mode_combo.setCurrentText(self.settings.get('repeat_mode', "不重复模式"))
        self.repeat_mode_combo.setFont(QFont(load_custom_font(), 12))
        basic_layout.addRow(repeat_label, self.repeat_mode_combo)

        # 学习顺序设置
        mode_label = BodyLabel("学习顺序:")
        mode_label.setFont(QFont(load_custom_font(), 12))
        self.mode_combo = ComboBox()
        self.mode_combo.addItems(["顺序学习", "随机学习"])
        self.mode_combo.setCurrentText(self.settings.get('mode', "随机学习"))
        self.mode_combo.setFont(QFont(load_custom_font(), 12))
        basic_layout.addRow(mode_label, self.mode_combo)
        
        # 玩家模式设置
        player_mode_label = BodyLabel("玩家模式:")
        player_mode_label.setFont(QFont(load_custom_font(), 12))
        self.player_mode_combo = ComboBox()
        self.player_mode_combo.addItems(["单人模式", "双人模式"])
        self.player_mode_combo.setCurrentText(self.settings.get('player_mode', "单人模式"))
        self.player_mode_combo.setFont(QFont(load_custom_font(), 12))
        basic_layout.addRow(player_mode_label, self.player_mode_combo)
        
        settings_card_layout.addWidget(basic_group)
        
        # 高级设置区域
        advanced_group = QGroupBox("高级设置")
        advanced_group.setFont(QFont(load_custom_font(), 12))
        advanced_layout = QFormLayout(advanced_group)
        advanced_layout.setLabelAlignment(Qt.AlignRight)
        advanced_layout.setFormAlignment(Qt.AlignLeft)
        advanced_layout.setSpacing(15)

        advanced_group.setStyleSheet("QGroupBox { border: 1px solid #cccccc; border-radius: 6px; margin-top: 12px; } "
                         "QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 3px 0 3px; }")
        
        # 练习模式选择
        learning_mode_label = BodyLabel("练习模式:")
        learning_mode_label.setFont(QFont(load_custom_font(), 12))
        self.learning_mode_combo = ComboBox()
        self.learning_mode_combo.addItems(["无尽模式", "总题数模式", "倒计时模式"])
        self.learning_mode_combo.setCurrentText(self.settings.get('learning_mode', "无尽模式"))
        self.learning_mode_combo.setFont(QFont(load_custom_font(), 12))
        advanced_layout.addRow(learning_mode_label, self.learning_mode_combo)
        
        # 干扰词汇数量设置
        distractor_label = BodyLabel("干扰词汇数量:")
        distractor_label.setFont(QFont(load_custom_font(), 12))
        self.distractor_count_spin = SpinBox()
        self.distractor_count_spin.setRange(0, 5)
        self.distractor_count_spin.setValue(self.settings.get('distractor_count', 3))
        self.distractor_count_spin.setFont(QFont(load_custom_font(), 12))
        advanced_layout.addRow(distractor_label, self.distractor_count_spin)
        
        # 总题数设置
        self.total_questions_widget = QWidget()
        total_questions_layout = QHBoxLayout(self.total_questions_widget)
        total_questions_layout.setContentsMargins(0, 0, 0, 0)
        total_questions_layout.setSpacing(5)
        
        total_questions_label = BodyLabel("总题数:")
        total_questions_label.setFont(QFont(load_custom_font(), 12))
        
        self.total_questions_spin = SpinBox()
        self.total_questions_spin.setRange(1, 50000)
        self.total_questions_spin.setValue(self.settings.get('total_questions', 20))
        self.total_questions_spin.setFont(QFont(load_custom_font(), 12))
        total_questions_layout.addWidget(self.total_questions_spin)
        
        advanced_layout.addRow(total_questions_label, self.total_questions_widget)
        
        # 倒计时设置
        self.countdown_widget = QWidget()
        countdown_layout = QHBoxLayout(self.countdown_widget)
        countdown_layout.setContentsMargins(0, 0, 0, 0)
        countdown_layout.setSpacing(5)

        countdown_label = BodyLabel("倒计时:")
        countdown_label.setFont(QFont(load_custom_font(), 12))
        
        self.countdown_hours_spin = SpinBox()
        self.countdown_hours_spin.setRange(0, 23)
        self.countdown_hours_spin.setValue(self.settings.get('countdown_hours', 0))
        self.countdown_hours_spin.setFont(QFont(load_custom_font(), 12))
        countdown_layout.addWidget(self.countdown_hours_spin)
        
        hours_label = BodyLabel("时")
        hours_label.setFont(QFont(load_custom_font(), 12))
        countdown_layout.addWidget(hours_label)
        
        self.countdown_minutes_spin = SpinBox()
        self.countdown_minutes_spin.setRange(0, 59)
        self.countdown_minutes_spin.setValue(self.settings.get('countdown_minutes', 30))
        self.countdown_minutes_spin.setFont(QFont(load_custom_font(), 12))
        countdown_layout.addWidget(self.countdown_minutes_spin)
        
        minutes_label = BodyLabel("分")
        minutes_label.setFont(QFont(load_custom_font(), 12))
        countdown_layout.addWidget(minutes_label)
        
        self.countdown_seconds_spin = SpinBox()
        self.countdown_seconds_spin.setRange(0, 59)
        self.countdown_seconds_spin.setValue(self.settings.get('countdown_seconds', 0))
        self.countdown_seconds_spin.setFont(QFont(load_custom_font(), 12))
        countdown_layout.addWidget(self.countdown_seconds_spin)
        
        seconds_label = BodyLabel("秒")
        seconds_label.setFont(QFont(load_custom_font(), 12))
        countdown_layout.addWidget(seconds_label)
        
        advanced_layout.addRow(countdown_label, self.countdown_widget)
        
        settings_card_layout.addWidget(advanced_group)
        
        main_layout.addWidget(settings_card)
        
        # 添加弹性空间
        main_layout.addStretch()
        
        # 创建按钮区域
        button_widget = QWidget()
        button_layout = QHBoxLayout(button_widget)
        button_layout.setContentsMargins(0, 0, 0, 0)
        
        # 添加弹性空间
        button_layout.addStretch()
        
        # 取消按钮
        self.cancel_button = PushButton("取消")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        # 确定按钮
        self.ok_button = PrimaryPushButton("确定")
        self.ok_button.clicked.connect(self.accept)
        button_layout.addWidget(self.ok_button)
        
        main_layout.addWidget(button_widget)
    
    def on_delete_vocabulary_clicked(self):
        """删除当前选择的词汇表"""
        # 获取当前选择的词汇表名称
        current_vocabulary = self.vocabulary_combo.currentText()
        
        # 检查是否为默认选项
        if current_vocabulary == "未添加词库":
            InfoBar.warning(
                title="警告",
                content="没有选择可删除的词汇表",
                duration=3000,
                parent=self
            ).show()
            return
        
        # 确认删除
        from qfluentwidgets import Dialog, FluentIcon
        
        confirm_dialog = Dialog(
            "确认删除",
            f"确定要删除词汇表 '{current_vocabulary}' 吗？\n删除后将无法恢复，请确认操作。",
            self
        )
        confirm_dialog.yesButton.setText("确定")
        confirm_dialog.cancelButton.setText("取消")
        
        if confirm_dialog.exec_():
            # 获取父窗口（主界面）
            parent = self.parent()
            
            # 如果父窗口存在，调用父窗口的删除词汇表方法
            if parent and hasattr(parent, 'delete_vocabulary'):
                success = parent.delete_vocabulary(current_vocabulary)
                
                if success:
                    # 删除成功后，刷新词汇表下拉框
                    if hasattr(parent, 'get_available_vocabularies'):
                        available_vocabularies = parent.get_available_vocabularies()
                        
                        # 清空下拉框
                        self.vocabulary_combo.clear()
                        
                        if available_vocabularies:
                            # 添加新的词汇文件列表
                            self.vocabulary_combo.addItems(available_vocabularies)
                            # 选中第一个词库
                            self.vocabulary_combo.setCurrentText(available_vocabularies[0])
                        else:
                            # 如果没有可用的词汇文件，添加默认选项
                            self.vocabulary_combo.addItems(["未添加词库"])
                            self.vocabulary_combo.setCurrentText("未添加词库")
                    
                    # 显示删除成功的提示
                    InfoBar.success(
                        title="删除成功",
                        content=f"已成功删除词汇表: {current_vocabulary}",
                        duration=3000,
                        parent=self
                    ).show()
                else:
                    # 显示删除失败的提示
                    InfoBar.error(
                        title="删除失败",
                        content=f"删除词汇表 '{current_vocabulary}' 失败，请重试",
                        duration=3000,
                        parent=self
                    ).show()
            else:
                # 如果父窗口不存在或没有删除词汇表方法，显示错误提示
                InfoBar.error(
                    title="错误",
                    content="无法删除词汇表，请重试",
                    duration=3000,
                    parent=self
                ).show()
    
    def on_import_vocabulary_clicked(self):
        """导入词汇表按钮点击事件处理函数"""
        # 获取父窗口（主界面）
        parent = self.parent()
        
        # 如果父窗口存在，调用父窗口的导入词汇表方法
        if parent and hasattr(parent, 'import_vocabulary'):
            parent.import_vocabulary()
            
            # 导入成功后，刷新词汇表下拉框
            if hasattr(parent, 'get_available_vocabularies'):
                available_vocabularies = parent.get_available_vocabularies()
                
                # 保存当前选中的词库
                current_vocabulary = self.vocabulary_combo.currentText()
                
                # 清空下拉框
                self.vocabulary_combo.clear()
                
                if available_vocabularies:
                    # 添加新的词汇文件列表
                    self.vocabulary_combo.addItems(available_vocabularies)
                    
                    # 如果之前选中的词库仍然存在，则保持选中状态
                    if current_vocabulary in available_vocabularies:
                        self.vocabulary_combo.setCurrentText(current_vocabulary)
                    else:
                        # 否则选中第一个词库
                        self.vocabulary_combo.setCurrentText(available_vocabularies[0])
                else:
                    # 如果没有可用的词汇文件，添加默认选项
                    self.vocabulary_combo.addItems(["未添加词库"])
                    self.vocabulary_combo.setCurrentText("未添加词库")
        else:
            # 如果父窗口不存在或没有导入词汇表方法，显示错误提示
            from qfluentwidgets import InfoBar
            InfoBar.error(
                title="错误",
                content="无法导入词汇表，请重试",
                duration=3000,
                parent=self
            ).show()
    
    def get_settings(self):
        """获取设置值"""
        return {
            'distractor_count': self.distractor_count_spin.value(),
            'repeat_mode': self.repeat_mode_combo.currentText(),
            'learning_mode': self.learning_mode_combo.currentText(),
            'total_questions': self.total_questions_spin.value(),
            'countdown_hours': self.countdown_hours_spin.value(),
            'countdown_minutes': self.countdown_minutes_spin.value(),
            'countdown_seconds': self.countdown_seconds_spin.value(),
            'current_vocabulary': self.vocabulary_combo.currentText(),
            'mode': self.mode_combo.currentText(),
            'player_mode': self.player_mode_combo.currentText()
        }