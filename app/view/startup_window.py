# ==================================================
# 启动窗口模块
# ==================================================

# ==================================================
# 系统工具导入
# ==================================================
import os
import sys
import multiprocessing

# ==================================================
# 第三方库导入
# ==================================================
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from qfluentwidgets import *
from loguru import logger

# ==================================================
# 内部模块导入
# ==================================================
from app.common.config import cfg, VERSION, load_custom_font
from app.common.path_utils import path_manager
from qfluentwidgets import qconfig, Theme

# ==================================================
# 启动窗口类
# ==================================================
class StartupWindow(QDialog):
    """启动窗口，展示软件启动进度"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SecRandom 正在启动...")
        self.setFixedSize(300, 150)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool | Qt.NoFocus | Qt.Popup)
        
        # 移除透明背景属性，使窗口不透明
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # 移除透明化效果
        # self.opacity_effect = QGraphicsOpacityEffect()
        # self.opacity_effect.setOpacity(0.8)
        # self.setGraphicsEffect(self.opacity_effect)

        # 创建主布局
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建背景容器
        self.background_widget = QWidget()
        self.background_widget.setObjectName("backgroundWidget")
        
        # 根据主题设置背景颜色
        self.update_background_theme()
        
        # 创建内容布局
        content_layout = QVBoxLayout(self.background_widget)
        content_layout.setSpacing(15)
        content_layout.setContentsMargins(20, 20, 20, 20)
        
        # 创建顶部水平布局，用于放置图标和标题
        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(0, 0, 0, 10)
        top_layout.setSpacing(10)  # 设置图标和标题之间的间距为10像素
        
        # 添加软件图标到左上角
        try:
            icon_path = str(path_manager.get_resource_path('icon', 'secrandom-icon-paper.png'))
            if os.path.exists(icon_path):
                icon_label = QLabel()
                pixmap = QPixmap(icon_path)
                # 缩放图标到合适大小
                scaled_pixmap = pixmap.scaled(52, 52, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                icon_label.setPixmap(scaled_pixmap)
                icon_label.setFixedSize(52, 52)
                top_layout.addWidget(icon_label)
            else:
                logger.error(f"软件图标文件不存在: {icon_path}")
        except Exception as e:
            logger.error(f"加载软件图标失败: {e}")
        
        # 创建垂直布局容器，用于放置标题和版本号
        title_version_layout = QVBoxLayout()
        title_version_layout.setSpacing(2)  # 设置标题和版本号之间的间距
        title_version_layout.setContentsMargins(0, 0, 0, 0)
        
        # 添加标题标签
        self.title_label = BodyLabel("SecRandom")
        self.title_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.title_label.setFont(QFont(load_custom_font(), 16))
        title_version_layout.addWidget(self.title_label)
        
        # 添加版本号标签到标题下方
        self.version_label = BodyLabel(f"{VERSION}")
        self.version_label.setAlignment(Qt.AlignLeft)
        self.version_label.setFont(QFont(load_custom_font(), 10))
        title_version_layout.addWidget(self.version_label)
        
        # 将标题和版本号布局添加到水平布局
        top_layout.addLayout(title_version_layout)
        
        # 添加弹性空间，使图标和标题靠左对齐
        top_layout.addStretch(1)
        
        # 添加顶部布局到内容布局
        content_layout.addLayout(top_layout)

        # 创建详细信息标签
        self.detail_label = BodyLabel("正在初始化，请稍候...")
        self.detail_label.setAlignment(Qt.AlignCenter)
        self.detail_label.setFont(QFont(load_custom_font(), 9))
        content_layout.addWidget(self.detail_label)
        
        # 添加弹性空间，使进度条能够贴底显示
        content_layout.addStretch(1)
        
        # 创建进度条
        self.progress_bar = ProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("%p%")
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: none;
                background-color: #F0F0F0;
                border-radius: 5px;
                text-align: center;
                color: #333333;
            }
            QProgressBar::chunk {
                background-color: #0078D7;
                border-radius: 5px;
            }
        """)
        content_layout.addWidget(self.progress_bar)
        
        # 将背景容器添加到主布局
        main_layout.addWidget(self.background_widget)
        
        # 启动步骤和进度
        self.startup_steps = [
            ("初始化应用程序环境", 10),
            ("配置日志系统", 20),
            ("检查单实例运行", 30),
            ("加载配置文件", 40),
            ("清理过期历史记录", 50),
            ("注册URL协议", 60),
            ("创建主窗口", 70),
            ("初始化界面组件", 80),
            ("处理URL命令", 90),
            ("启动完成", 100)
        ]
        
        self.current_step = 0
        
    def update_progress(self, step_name=None, progress=None, detail=None):
        """更新启动进度"""
        if progress is not None:
            self.progress_bar.setValue(progress)
        
        if detail:
            self.detail_label.setText(detail)
            
        # 确保界面更新
        QApplication.processEvents()
        
    def next_step(self, detail=None):
        """进入下一个启动步骤"""
        if self.current_step < len(self.startup_steps):
            step_name, progress = self.startup_steps[self.current_step]
            self.update_progress(step_name, progress, detail)
            self.current_step += 1
            return True
        return False
    
    def set_step(self, step_index, detail=None):
        """设置到指定步骤"""
        if 0 <= step_index < len(self.startup_steps):
            step_name, progress = self.startup_steps[step_index]
            self.update_progress(step_name, progress, detail)
            self.current_step = step_index + 1
            return True
        return False
    
    def update_background_theme(self):
        """根据当前主题更新背景颜色"""
        # 检测当前主题
        if qconfig.theme == Theme.AUTO:
            lightness = QApplication.palette().color(QPalette.Window).lightness()
            is_dark = lightness <= 127
        else:
            is_dark = qconfig.theme == Theme.DARK
        
        # 根据主题设置颜色
        if is_dark:
            # 深色主题
            bg_color = "#111116"
            border_color = "#3E3E42"
            text_color = "#F5F5F5"
            progress_bg = "#2D2D30"
            progress_text = "#F5F5F5"
        else:
            # 浅色主题
            bg_color = "#F5F5F5"
            border_color = "#CCCCCC"
            text_color = "#111116"
            progress_bg = "#F0F0F0"
            progress_text = "#333333"
        
        # 设置背景容器样式
        self.background_widget.setStyleSheet(f"""
            #backgroundWidget {{
                background-color: {bg_color};
                border-radius: 15px;
                border: 1px solid {border_color};
            }}
        """)
        
    def close_startup(self):
        """关闭启动窗口"""
        self.close()