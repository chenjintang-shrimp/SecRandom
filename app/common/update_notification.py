from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from qfluentwidgets import *
import webbrowser
import os
import json
import requests
import subprocess
import sys
import tempfile
import threading
from pathlib import Path

from app.common.config import get_theme_icon, load_custom_font, check_for_updates, VERSION
from app.common.path_utils import path_manager, open_file

def show_update_notification(latest_version):
    """显示更新通知窗口"""
    if hasattr(QApplication.instance(), 'update_notification_window'):
        # 如果窗口已存在则激活它
        notification_window = QApplication.instance().update_notification_window
        if notification_window.isHidden():
            notification_window.show()
        notification_window.raise_()
        notification_window.activateWindow()
        return

    # 创建新的通知窗口
    notification_window = UpdateNotification(latest_version)
    QApplication.instance().update_notification_window = notification_window
    notification_window.show()

class UpdateNotification(QDialog):
    """自定义更新通知窗口"""
    def __init__(self, latest_version):
        # 🐦 小鸟游星野：添加Qt.Tool标志隐藏任务栏图标~ (๑•̀ㅂ•́)و✧
        super().__init__(parent=None, flags=Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.latest_version = latest_version
        self.duration = 15000  # 默认显示15秒
        self.init_ui()
        self.init_animation()
        self.start_auto_close_timer()

    def init_ui(self):
        """初始化UI界面"""
        cursor_pos = QCursor.pos()
        for screen in QGuiApplication.screens():
            if screen.geometry().contains(cursor_pos):
                target_screen = screen
                break
        else:
            target_screen = QGuiApplication.primaryScreen()
        screen_geometry = target_screen.availableGeometry()
        max_width = min(int(screen_geometry.width() * 0.3), 500)  # 最大宽度为屏幕30%或500px取较小值
        self.setMaximumWidth(max_width)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        # 🌟 星穹铁道白露：更新窗口标志，确保任务栏不显示图标~ 
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setStyleSheet("""
            QDialog {
                background-color: rgba(235, 238, 242, 0.5);
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 5px;
                opacity: 0;
            }
        """)

        # 创建主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(20)

        # 标题栏（包含图标和标题）
        title_layout = QHBoxLayout()
        title_layout.setSpacing(10)

        # 更新图标
        icon_label = QLabel()
        icon_path = path_manager.get_resource_path('icon', 'SecRandom.png')
        icon_label.setPixmap(QIcon(icon_path).pixmap(55, 55))
        icon_label.setStyleSheet("background: transparent; border: none;")

        # 标题文本
        title_label = BodyLabel("SecRandom 有新版本可用")
        title_label.setFont(QFont(load_custom_font(), 14, QFont.Bold))
        title_label.setStyleSheet("color: #1a1a1a; border: none; background: transparent;")

        # 版本信息
        version_label = BodyLabel(f"📌 当前版本: {VERSION}\n🎉 发现新版本 {self.latest_version}\n✨ 包含多项功能优化和体验改进")
        version_label.setFont(QFont(load_custom_font(), 12))
        version_label.setStyleSheet("color: #2d3436; border: none; background: transparent;")
        version_label.setAlignment(Qt.AlignCenter)

        # 关闭按钮
        close_btn = PushButton("")
        close_icon_path = path_manager.get_asset_path('dark', 'ic_fluent_arrow_exit_20_filled_dark', '.svg')
        close_btn.setIcon(QIcon(close_icon_path))
        close_btn.setStyleSheet("background: transparent; border: none;")
        close_btn.clicked.connect(self.close_with_animation)

        # 添加到标题布局
        title_layout.addWidget(icon_label)
        title_layout.addWidget(title_label)
        title_layout.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))
        title_layout.addWidget(close_btn)

        # 按钮布局
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        # 官网
        manual_update_btn = PushButton("     官网 下载更新")
        manual_update_btn.setIcon(QIcon(icon_path))
        manual_update_btn.setStyleSheet(""
            "QPushButton {background-color: #4a6cf7; color: white; border-radius: 8px; padding: 8px 16px; font-weight: 500; border: none;}"
            "QPushButton:hover {background-color: #3a5bdb;}"

        )
        manual_update_btn.setFont(QFont(load_custom_font(), 12))
        manual_update_btn.clicked.connect(self.on_manual_update_clicked)

        # 添加到按钮布局
        btn_layout.addWidget(manual_update_btn)

        # 添加所有组件到主布局
        main_layout.addLayout(title_layout)
        main_layout.addWidget(version_label)
        main_layout.addLayout(btn_layout)

        self.move_to_bottom_right()

    def init_animation(self):
        """初始化动画效果"""
        # 获取屏幕几何信息
        screen_geometry = QApplication.desktop().availableGeometry()
        # 设置初始位置在屏幕右侧外
        self.move(screen_geometry.width(), self.y())
        
        # 创建位置动画
        self.pos_animation = QPropertyAnimation(self, b"pos")
        self.pos_animation.setDuration(600)
        self.pos_animation.setEasingCurve(QEasingCurve.OutCubic)
        self.pos_animation.setStartValue(QPoint(screen_geometry.width(), self.y()))
        self.pos_animation.setEndValue(QPoint(screen_geometry.width() - self.width() - 20, self.y()))
        
        # 创建透明度动画
        self.opacity_animation = QPropertyAnimation(self, b"windowOpacity")
        self.opacity_animation.setDuration(400)
        self.opacity_animation.setEasingCurve(QEasingCurve.InOutQuad)
        self.opacity_animation.setStartValue(0.0)
        self.opacity_animation.setEndValue(1.0)
        
        # 并行运行所有动画
        self.group_animation = QParallelAnimationGroup(self)
        self.group_animation.addAnimation(self.pos_animation)
        self.group_animation.addAnimation(self.opacity_animation)
        self.group_animation.start()

    def start_auto_close_timer(self):
        """启动自动关闭定时器"""
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.close_with_animation)
        self.timer.start(self.duration)

    def showEvent(self, event):
        super().showEvent(event)
        # 确保窗口尺寸已确定后再计算位置
        QTimer.singleShot(100, self.move_to_bottom_right)

    def move_to_bottom_right(self):
        """将窗口移动到屏幕右下角"""
        screen_geometry = QGuiApplication.primaryScreen().availableGeometry()
        # 重新获取窗口尺寸确保准确性
        self.adjustSize()
        x = max(0, screen_geometry.width() - self.width() - 20)
        y = max(0, screen_geometry.height() - self.height() - 20)
        self.move(x, y)

    def on_manual_update_clicked(self):
        """官网手动更新按钮点击事件"""
        webbrowser.open("https://secrandom.netlify.app//download")
        self.close_with_animation()

    def is_installer_package(self):
        """检查是否为安装包版本"""
        marker_path = path_manager.get_guide_complete_path('installer_marker.json')
        if marker_path.exists():
            try:
                with open_file(marker_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('installer_package', False)
            except:
                pass
        return False

    def show_auto_update_dialog(self):
        """显示自动更新对话框"""
        dialog = AutoUpdateDialog(self.latest_version)
        dialog.exec_()

    def close_with_animation(self):
        """带动画效果关闭窗口"""
        # 获取屏幕几何信息
        screen_geometry = QApplication.desktop().availableGeometry()
        
        # 创建位置动画到屏幕右侧外
        self.pos_animation = QPropertyAnimation(self, b"pos")
        self.pos_animation.setEasingCurve(QEasingCurve.InCubic)
        self.pos_animation.setDuration(600)
        self.pos_animation.setStartValue(self.pos())
        self.pos_animation.setEndValue(QPoint(screen_geometry.width(), self.y()))
        
        # 创建透明度动画
        self.opacity_animation = QPropertyAnimation(self, b"windowOpacity")
        self.opacity_animation.setEasingCurve(QEasingCurve.InOutQuad)
        self.opacity_animation.setDuration(400)
        self.opacity_animation.setStartValue(1.0)
        self.opacity_animation.setEndValue(0.0)
        
        # 并行运行所有动画
        self.group_animation = QParallelAnimationGroup(self)
        self.group_animation.addAnimation(self.pos_animation)
        self.group_animation.addAnimation(self.opacity_animation)
        self.group_animation.finished.connect(self.close)
        self.group_animation.start()

    def mousePressEvent(self, event):
        """鼠标按下事件 - 重置自动关闭定时器"""
        if event.button() == Qt.LeftButton:
            self.timer.start(self.duration)
        super().mousePressEvent(event)

    def showEvent(self, event):
        """显示事件 - 确保窗口在最前面"""
        self.raise_()
        super().showEvent(event)

    def closeEvent(self, event):
        if hasattr(QApplication.instance(), 'update_notification_window'):
            del QApplication.instance().update_notification_window
        super().closeEvent(event)


class AutoUpdateDialog(QDialog):
    """自动更新对话框"""
    def __init__(self, latest_version):
        super().__init__()
        self.latest_version = latest_version
        self.download_thread = None
        self.init_ui()
        self.setWindowFlags(Qt.Window | Qt.WindowCloseButtonHint)
        self.setWindowTitle("自动更新")
        self.setFixedSize(400, 300)

    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)

        # 标题
        title = QLabel("发现新版本")
        title.setFont(QFont(load_custom_font(), 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # 版本信息
        version_info = QLabel(f"当前版本: {VERSION}\n新版本: {self.latest_version}")
        version_info.setFont(QFont(load_custom_font(), 12))
        version_info.setAlignment(Qt.AlignCenter)
        layout.addWidget(version_info)

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # 状态标签
        self.status_label = QLabel("准备下载...")
        self.status_label.setFont(QFont(load_custom_font(), 11))
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

        # 按钮布局
        button_layout = QHBoxLayout()
        
        self.update_button = PushButton("自动更新")
        self.update_button.clicked.connect(self.start_auto_update)
        
        self.cancel_button = PushButton("取消")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.update_button)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)

    def start_auto_update(self):
        """开始自动更新"""
        self.update_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.status_label.setText("正在检查更新...")
        
        self.download_thread = DownloadThread(self.latest_version)
        self.download_thread.progress_updated.connect(self.update_progress)
        self.download_thread.status_updated.connect(self.update_status)
        self.download_thread.download_finished.connect(self.on_download_finished)
        self.download_thread.download_error.connect(self.on_download_error)
        self.download_thread.start()

    def update_progress(self, value):
        """更新进度条"""
        self.progress_bar.setValue(value)

    def update_status(self, message):
        """更新状态文本"""
        self.status_label.setText(message)

    def on_download_finished(self, file_path):
        """下载完成"""
        self.status_label.setText("下载完成，正在安装...")
        self.install_update(file_path)

    def on_download_error(self, error_message):
        """下载错误"""
        QMessageBox.warning(self, "下载错误", f"下载失败: {error_message}")
        self.update_button.setEnabled(True)
        self.progress_bar.setVisible(False)

    def install_update(self, file_path):
        """安装更新"""
        try:
            # 启动安装程序
            subprocess.Popen([file_path, '/silent'])
            
            # 关闭当前应用
            QApplication.quit()
            
        except Exception as e:
            QMessageBox.warning(self, "安装错误", f"启动安装程序失败: {str(e)}")


class DownloadThread(QThread):
    """下载线程"""
    progress_updated = pyqtSignal(int)
    status_updated = pyqtSignal(str)
    download_finished = pyqtSignal(str)
    download_error = pyqtSignal(str)

    def __init__(self, version):
        super().__init__()
        self.version = version

    def run(self):
        """执行下载"""
        try:
            # 构建下载URL
            download_url = f"https://github.com/SECTL/SecRandom/releases/download/{self.version}/SecRandom-Setup-{self.version}.exe"
            
            # 创建临时文件
            temp_dir = tempfile.gettempdir()
            file_name = f"SecRandom-Setup-{self.version}.exe"
            file_path = os.path.join(temp_dir, file_name)
            
            self.status_updated.emit("正在连接服务器...")
            
            # 下载文件
            response = requests.get(download_url, stream=True)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            progress = int((downloaded / total_size) * 100)
                            self.progress_updated.emit(progress)
                            self.status_updated.emit(f"已下载 {progress}%")
            
            self.download_finished.emit(file_path)
            
        except requests.exceptions.RequestException as e:
            self.download_error.emit(f"网络错误: {str(e)}")
        except Exception as e:
            self.download_error.emit(str(e))