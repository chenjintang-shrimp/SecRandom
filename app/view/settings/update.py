# ==================================================
# 导入库
# ==================================================

from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
from qfluentwidgets import *

from app.tools.variable import *
from app.tools.path_utils import *
from app.tools.personalised import *
from app.tools.settings_default import *
from app.tools.settings_access import *
from app.Language.obtain_language import *


# ==================================================
# 更新页面
# ==================================================
class update(QWidget):
    """创建更新页面"""
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 创建主布局
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(15)
        self.main_layout.setAlignment(Qt.AlignTop)
        
        # 设置标题
        self.titleLabel = BodyLabel(get_content_name_async("update", "secrandom_update_text"))
        self.titleLabel.setFont(QFont(load_custom_font(), 20))

        # 创建顶部信息区域
        self.setup_header_info()
        
        # 创建更新设置区域
        self.setup_update_settings()
        
        # 添加到主界面
        self.main_layout.addWidget(self.titleLabel)
        self.main_layout.addLayout(self.header_layout)
        self.main_layout.addWidget(self.update_settings_card)
        
        # 设置窗口布局
        self.setLayout(self.main_layout)
        
    def setup_header_info(self):
        """设置头部信息区域"""
        # 创建水平布局用于放置图标和状态信息
        self.header_layout = QHBoxLayout()
        self.header_layout.setSpacing(15)
        self.header_layout.setAlignment(Qt.AlignLeft)
        
        # 添加软件图标
        self.icon_label = BodyLabel()
        icon_pixmap = QPixmap(str(get_resources_path("assets/icon", "secrandom-icon-paper.png")))
        self.icon_label.setPixmap(icon_pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        
        # 创建垂直布局用于放置图标和进度条
        icon_progress_layout = QVBoxLayout()
        icon_progress_layout.setAlignment(Qt.AlignCenter)
        icon_progress_layout.addWidget(self.icon_label)
        
        # 添加进度条
        self.progress_bar = ProgressBar()
        self.progress_bar.setVisible(False)  # 默认隐藏
        icon_progress_layout.addWidget(self.progress_bar)
        
        # 创建状态信息布局
        status_layout = QVBoxLayout()
        status_layout.setSpacing(5)
        status_layout.setAlignment(Qt.AlignLeft)
        
        # 当前状态标签
        self.status_label = BodyLabel(get_content_name_async("update", "checking_update"))
        self.status_label.setFont(QFont(load_custom_font(), 16))

        # 版本信息标签
        self.version_label = BodyLabel(f"{get_content_name_async('update', 'current_version')}: {VERSION}")
        self.version_label.setFont(QFont(load_custom_font(), 12))

        status_layout.addWidget(self.status_label)
        status_layout.addWidget(self.version_label)
        
        self.header_layout.addLayout(icon_progress_layout)
        self.header_layout.addLayout(status_layout)
        self.header_layout.addStretch()
        
    def setup_update_settings(self):
        """设置更新设置区域"""
        self.update_settings_card = GroupHeaderCardWidget()
        self.update_settings_card.setTitle(get_content_name_async("update", "title"))
        self.update_settings_card.setBorderRadius(8)
        
        # 更新方式设置
        self.update_method_combo = ComboBox()
        self.update_method_combo.addItems(
            get_content_combo_name_async("update", "update_method")
        )
        update_method = readme_settings("update", "update_method")
        self.update_method_combo.setCurrentIndex(update_method)
        self.update_method_combo.currentIndexChanged.connect(
            lambda: update_settings("update", "update_method", self.update_method_combo.currentIndex())
        )
        
        # 更新通道选择
        self.update_channel_combo = ComboBox()
        self.update_channel_combo.addItems(
            get_content_combo_name_async("update", "update_channel")
        )
        update_channel = readme_settings("update", "update_channel")
        self.update_channel_combo.setCurrentIndex(update_channel)
        self.update_channel_combo.currentIndexChanged.connect(
            lambda: update_settings("update", "update_channel", self.update_channel_combo.currentIndex())
        )
        
        # 更新源选择
        self.update_source_combo = ComboBox()
        self.update_source_combo.addItems(
            get_content_combo_name_async("update", "update_source")
        )
        update_source = readme_settings("update", "update_source")
        self.update_source_combo.setCurrentIndex(update_source)
        self.update_source_combo.currentIndexChanged.connect(
            lambda: update_settings("update", "update_source", self.update_source_combo.currentIndex())
        )
        
        # 添加设置项到卡片
        self.update_settings_card.addGroup(
            get_theme_icon("ic_fluent_arrow_sync_20_filled"),
            get_content_name_async("update", "update_method"),
            get_content_description_async("update", "update_method"),
            self.update_method_combo,
        )
        
        self.update_settings_card.addGroup(
            get_theme_icon("ic_fluent_channel_20_filled"),
            get_content_name_async("update", "update_channel"),
            get_content_description_async("update", "update_channel"),
            self.update_channel_combo,
        )
        
        self.update_settings_card.addGroup(
            get_theme_icon("ic_fluent_cloud_arrow_down_20_filled"),
            get_content_name_async("update", "update_source"),
            get_content_description_async("update", "update_source"),
            self.update_source_combo,
        )