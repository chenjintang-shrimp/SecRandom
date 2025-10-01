from qfluentwidgets import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import hashlib
import json
import os
import pyotp
import os
from loguru import logger
from app.common.config import get_theme_icon, load_custom_font, is_dark_theme
from app.common.path_utils import path_manager, open_file
from app.common.password_settings import is_usb_bound, get_usb_drives

class PasswordDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        # 设置无边框窗口样式并解决屏幕设置冲突 
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window | Qt.Tool | Qt.WindowStaysOnTopHint)
        self.setWindowTitle("密码验证")
        self.setWindowIcon(QIcon(str(path_manager.get_resource_path('icon', 'SecRandom.png'))))
        self.setFixedSize(400, 300)

        self.dragging = False
        self.drag_position = None
        
        # 自动验证相关变量
        self.auto_verify_timer = QTimer()
        self.auto_verify_timer.setSingleShot(True)
        self.auto_verify_timer.timeout.connect(self.auto_verify)
        self.auto_verify_delay = 1000  # 1秒延迟，避免频繁验证
        
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

        self.update_theme_style()
        qconfig.themeChanged.connect(self.update_theme_style)

        screen = QApplication.primaryScreen()
        desktop = screen.availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)

        # 创建主布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 添加自定义标题栏
        layout.addWidget(self.title_bar)
        
        # 添加内容区域
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(20, 15, 20, 20)
        content_layout.setSpacing(10)
        layout.addLayout(content_layout)

        # 解锁方式选择 - 根据配置动态显示
        self.unlock_method = ComboBox()
        self.unlock_method.setFont(QFont(load_custom_font(), 12))
        
        # 根据配置文件动态添加解锁方式
        self.update_unlock_methods()
        content_layout.addWidget(self.unlock_method, 0, Qt.AlignCenter)

        # 密码输入框
        self.password_input = LineEdit()
        self.password_input.setPlaceholderText("请输入密码")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setFont(QFont(load_custom_font(), 12))
        # 回车确认
        self.password_input.returnPressed.connect(self.verify)
        content_layout.addWidget(self.password_input, 0, Qt.AlignCenter)

        # 密钥文件选择
        key_file_widget = QWidget()
        key_file_layout = QHBoxLayout(key_file_widget)
        key_file_layout.setContentsMargins(0, 0, 0, 0)
        key_file_layout.setSpacing(8)
        
        self.key_file_input = LineEdit()
        self.key_file_input.setPlaceholderText("请选择密钥文件")
        self.key_file_input.setFont(QFont(load_custom_font(), 12))
        self.key_file_btn = PushButton("选择文件")
        self.key_file_btn.setFont(QFont(load_custom_font(), 12))
        self.key_file_btn.clicked.connect(self.select_key_file)
        # 自动验证 - 密钥文件输入框
        self.key_file_input.textChanged.connect(self.start_auto_verify)
        
        key_file_layout.addWidget(self.key_file_input, 0, Qt.AlignCenter)
        key_file_layout.addStretch()
        key_file_layout.addWidget(self.key_file_btn, 0, Qt.AlignCenter)
        
        content_layout.addWidget(key_file_widget, 0, Qt.AlignCenter)

        # 用户名输入框（2FA验证时显示）
        self.username_input = LineEdit()
        self.username_input.setPlaceholderText("请输入用户名")
        self.username_input.setFont(QFont(load_custom_font(), 12))
        content_layout.addWidget(self.username_input, 0, Qt.AlignCenter)

        # 2FA验证码
        self.totp_input = LineEdit()
        self.totp_input.setPlaceholderText("请输入2FA验证码")
        self.totp_input.setFont(QFont(load_custom_font(), 12))
        # 回车确认
        self.totp_input.returnPressed.connect(self.verify)
        content_layout.addWidget(self.totp_input, 0, Qt.AlignCenter)

        # U盘状态显示
        self.usb_status_widget = QWidget()
        usb_status_layout = QVBoxLayout(self.usb_status_widget)
        usb_status_layout.setContentsMargins(0, 0, 0, 0)
        usb_status_layout.setSpacing(5)
        
        self.usb_status_label = BodyLabel("正在检测U盘...")
        self.usb_status_label.setFont(QFont(load_custom_font(), 12))
        self.usb_status_label.setAlignment(Qt.AlignCenter)
        usb_status_layout.addWidget(self.usb_status_label, 0, Qt.AlignCenter)
        
        self.usb_refresh_btn = PushButton("重新检测")
        self.usb_refresh_btn.setFont(QFont(load_custom_font(), 12))
        self.usb_refresh_btn.clicked.connect(self.check_usb_status)
        usb_status_layout.addWidget(self.usb_refresh_btn, alignment=Qt.AlignCenter)
        
        content_layout.addWidget(self.usb_status_widget, 0, Qt.AlignCenter)
        
        # 默认隐藏U盘状态组件
        self.usb_status_widget.hide()

        # 按钮
        self.verify_btn = PushButton("验证")
        self.verify_btn.clicked.connect(self.verify)
        self.verify_btn.setFont(QFont(load_custom_font(), 12))
        content_layout.addWidget(self.verify_btn, 0, Qt.AlignRight)

        # 根据选择显示不同控件
        self.unlock_method.currentIndexChanged.connect(self.update_ui)
        self.update_ui()
    
    def update_unlock_methods(self):
        """根据配置文件更新解锁方式选项"""
        try:
            # 清空现有选项
            self.unlock_method.clear()
            
            # 读取配置文件
            with open_file(path_manager.get_enc_set_path(), 'r', encoding='utf-8') as f:
                settings = json.load(f)
                
            hashed_set = settings.get('hashed_set', {})
            
            # 根据配置添加解锁方式
            unlock_methods = []
            
            # 密码解锁
            if hashed_set.get('start_password_enabled', False):
                unlock_methods.append("密码解锁")
            
            # 密钥文件解锁 - 如果有hashed_password则启用
            if hashed_set.get('hashed_password', ''):
                unlock_methods.append("密钥文件解锁")
            
            # 2FA验证
            if hashed_set.get('two_factor_auth', False):
                unlock_methods.append("2FA验证")
            
            # U盘解锁
            if settings.get('usb_auth_enabled', False):
                unlock_methods.append("U盘解锁")
            
            # 添加解锁方式到下拉框
            if unlock_methods:
                self.unlock_method.addItems(unlock_methods)
            else:
                # 如果没有启用的解锁方式，显示提示
                self.unlock_method.addItem("无可用解锁方式")
                self.unlock_method.setEnabled(False)
                
        except Exception as e:
            logger.error(f"读取解锁方式配置失败: {e}")
            # 读取失败时显示所有解锁方式作为备用
            self.unlock_method.addItems(["密码解锁", "密钥文件解锁", "2FA验证", "U盘解锁"])

    def mousePressEvent(self, event):
        # 窗口拖动功能
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
        # 主题样式更新
        is_dark = is_dark_theme(qconfig)
        title_bar_bg = '#2D2D30' if is_dark else '#F0F0F0'
        title_text_color = '#FFFFFF' if is_dark else '#000000'
        close_button_bg = '#3D3D40' if is_dark else '#E0E0E0'
        close_button_hover = '#ff4d4d'
        dialog_bg = '#111116' if is_dark else '#F5F5F5'
        text_color = '#F5F5F5' if is_dark else '#111116'
        line_edit_bg = '#3c3c3c' if is_dark else '#ffffff'
        line_edit_text = '#ffffff' if is_dark else '#000000'
        line_edit_border = '#555555' if is_dark else '#cccccc'
        push_button_bg = '#505050' if is_dark else '#f0f0f0'
        push_button_text = '#ffffff' if is_dark else '#000000'
        push_button_border = '#555555' if is_dark else '#cccccc'
        push_button_hover = '#606060' if is_dark else '#e0e0e0'
        combo_box_bg = '#3c3c3c' if is_dark else '#ffffff'
        combo_box_text = '#ffffff' if is_dark else '#000000'
        combo_box_border = '#555555' if is_dark else '#cccccc'

        self.setStyleSheet(f"""
            QDialog {{
                background-color: {dialog_bg};
                color: {text_color};
            }}
            #CustomTitleBar {{
                background-color: {title_bar_bg};
            }}
            #TitleLabel {{
                color: {title_text_color};
                font-weight: bold;
                padding: 5px;
            }}
            #CloseButton {{
                background-color: {close_button_bg};
                color: {title_text_color};
                border-radius: 4px;
                border: none;
                font-weight: bold;
            }}
            #CloseButton:hover {{
                background-color: {close_button_hover};
            }}
            QLineEdit {{
                background-color: {line_edit_bg};
                color: {line_edit_text};
                border: 1px solid {line_edit_border};
                border-radius: 4px;
                padding: 5px;
            }}
            QPushButton {{
                background-color: {push_button_bg};
                color: {push_button_text};
                border: 1px solid {push_button_border};
                border-radius: 4px;
                padding: 5px;
            }}
            QPushButton:hover {{
                background-color: {push_button_hover};
            }}
            QComboBox {{
                background-color: {combo_box_bg};
                color: {combo_box_text};
                border: 1px solid {combo_box_border};
                border-radius: 4px;
                padding: 5px;
            }}
        """)

        # 设置标题栏颜色以匹配背景色（仅Windows系统）
        if os.name == 'nt':
            try:
                import ctypes
                # 修复参数类型错误，将窗口ID转换为整数句柄
                hwnd = int(self.winId())  # 转换为整数句柄
                
                # 颜色格式要改成ARGB，添加透明度通道
                bg_color = title_bar_bg.lstrip('#')
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
                logger.warning(f"设置标题栏颜色失败: {str(e)}")

    def mousePressEvent(self, event):
        # 窗口拖动功能
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
        """窗口关闭时隐藏主界面"""
        self.hide()
        event.ignore()
        # 确保不会触发应用程序退出
        if QApplication.instance():
            QApplication.instance().setQuitOnLastWindowClosed(False)

    def update_ui(self):
        method = self.unlock_method.currentText()
        self.password_input.setVisible(method == "密码解锁")
        self.key_file_input.setVisible(method == "密钥文件解锁")
        self.key_file_btn.setVisible(method == "密钥文件解锁")
        self.username_input.setVisible(method == "2FA验证")
        self.totp_input.setVisible(method == "2FA验证")
        self.usb_status_widget.setVisible(method == "U盘解锁")
        
        # 如果切换到U盘解锁，立即检测U盘状态并尝试自动验证
        if method == "U盘解锁":
            self.check_usb_status()
            # 延迟一点时间让U盘检测完成，然后自动验证
            QTimer.singleShot(500, self.start_auto_verify)

    def select_key_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "选择密钥文件", "", "Key Files (*.key)")
        if file_path:
            self.key_file_input.setText(file_path)

    def verify(self):
        try:
            with open_file(path_manager.get_enc_set_path(), 'r', encoding='utf-8') as f:
                settings = json.load(f)
                hashed_set_settings = settings.get('hashed_set', {})

                method = self.unlock_method.currentText()

                if method == "密码解锁":
                    password = self.password_input.text()
                    salt = hashed_set_settings.get('password_salt', '')
                    stored_hash = hashed_set_settings.get('hashed_password', '')

                    if not password or not salt or not stored_hash:
                        w = MessageBox("错误", "密码验证失败: 未输入密码", self)
                        w.setFont(QFont(load_custom_font(), 14))
                        w.yesButton.setText("知道了")
                        w.cancelButton.hide()
                        w.buttonLayout.insertStretch(1)
                        w.exec_()
                        return

                    hashed = hashlib.md5((password + salt).encode()).hexdigest()
                    if hashed == stored_hash:
                        self.accept()
                    else:
                        w = MessageBox("错误", "密码错误", self)
                        w.setFont(QFont(load_custom_font(), 14))
                        w.yesButton.setText("知道了")
                        w.cancelButton.hide()
                        w.buttonLayout.insertStretch(1)
                        w.exec_()
                        return

                elif method == "密钥文件解锁":
                    key_file = self.key_file_input.text()
                    stored_key_hash = hashed_set_settings.get('hashed_password', '')

                    if not key_file or not stored_key_hash:
                        w = MessageBox("错误", "密钥文件验证失败: 未设置密钥文件", self)
                        w.setFont(QFont(load_custom_font(), 14))
                        w.yesButton.setText("知道了")
                        w.cancelButton.hide()
                        w.buttonLayout.insertStretch(1)
                        w.exec_()
                        return

                    try:
                        with open_file(key_file, 'rb') as f:
                            file_content = f.read()
                            file_content = file_content.decode().strip("b'").strip("'")

                        if file_content == stored_key_hash:
                            self.accept()
                        else:
                            w = MessageBox("错误", "密钥文件内容不匹配", self)
                            w.setFont(QFont(load_custom_font(), 14))
                            w.yesButton.setText("知道了")
                            w.cancelButton.hide()
                            w.buttonLayout.insertStretch(1)
                            w.exec_()
                    except Exception as e:
                        logger.error(f"读取密钥文件失败: {e}")
                        w = MessageBox("错误", f"读取密钥文件失败: {str(e)}", self)
                        w.setFont(QFont(load_custom_font(), 14))
                        w.yesButton.setText("知道了")
                        w.cancelButton.hide()
                        w.buttonLayout.insertStretch(1)
                        w.exec_()

                elif method == "2FA验证":
                    username = self.username_input.text()
                    if not username:
                        w = MessageBox("错误", "请输入用户名", self)
                        w.setFont(QFont(load_custom_font(), 14))
                        w.yesButton.setText("知道了")
                        w.cancelButton.hide()
                        w.buttonLayout.insertStretch(1)
                        w.exec_()
                        return

                    if not self.verify_2fa_code(self.totp_input.text(), username):
                        w = MessageBox("错误", "验证码/用户名不正确", self)
                        w.setFont(QFont(load_custom_font(), 14))
                        w.yesButton.setText("知道了")
                        w.cancelButton.hide()
                        w.buttonLayout.insertStretch(1)
                        w.exec_()
                        return

                    self.accept()

                elif method == "U盘解锁":
                    if self.verify_usb():
                        self.accept()
                        return
                    else:
                        w = MessageBox("错误", "U盘验证失败，请确保已插入正确的U盘", self)
                        w.setFont(QFont(load_custom_font(), 14))
                        w.yesButton.setText("知道了")
                        w.cancelButton.hide()
                        w.buttonLayout.insertStretch(1)
                        w.exec_()
                        return

        except Exception as e:
            logger.error(f"验证失败: {e}")
            w = MessageBox("错误", f"验证失败: {str(e)}", self)
            w.setFont(QFont(load_custom_font(), 14))
            w.yesButton.setText("知道了")
            w.cancelButton.hide()
            w.buttonLayout.insertStretch(1)
            w.exec_()
            

    def verify_2fa_code(self, code, username):
        try:
            # 从设置文件中读取2FA密钥和加密用户名
            with open_file(path_manager.get_enc_set_path(), 'r') as f:
                settings = json.load(f)
                secret = settings['hashed_set']['2fa_secret']
                stored_username = settings['hashed_set'].get('encrypted_username', '')

            # 对输入的用户名进行相同加密
            salt = 'SecRandomSalt'
            hashed_input = hashlib.md5((username + salt).encode()).hexdigest()

            # 验证用户名和2FA验证码
            totp = pyotp.TOTP(secret)
            return hashed_input == stored_username and totp.verify(code)
        except Exception as e:
            logger.error(f"2FA验证失败: {e}")
            return False
             
    def check_usb_status(self):
        """检查U盘状态并更新UI显示"""
        try:
            self.usb_status_label.setText("正在检测U盘...")
            
            # 获取当前插入的USB设备
            usb_drives = get_usb_drives()
            
            if not usb_drives:
                self.usb_status_label.setText("未检测到U盘设备")
                self.usb_status_label.setStyleSheet("color: #ff4d4d;")
                return
            
            # 检查是否有绑定的U盘
            if is_usb_bound():
                self.usb_status_label.setText(f"检测到 {len(usb_drives)} 个U盘设备，验证通过")
                self.usb_status_label.setStyleSheet("color: #4caf50;")
            else:
                self.usb_status_label.setText(f"检测到 {len(usb_drives)} 个U盘设备，但未通过验证")
                self.usb_status_label.setStyleSheet("color: #ff9800;")
                
        except Exception as e:
            logger.error(f"检查U盘状态失败: {e}")
            self.usb_status_label.setText("检测U盘状态时出错")
            self.usb_status_label.setStyleSheet("color: #ff4d4d;")
    
    def verify_usb(self):
        """验证U盘"""
        try:
            # 使用password_settings.py中的is_usb_bound函数进行验证
            return is_usb_bound()
        except Exception as e:
            logger.error(f"U盘验证失败: {e}")
            return False
    
    def start_auto_verify(self):
        """启动自动验证计时器"""
        # 重启计时器，实现防抖效果
        self.auto_verify_timer.start(self.auto_verify_delay)
    
    def auto_verify(self):
        """自动验证方法"""
        try:
            method = self.unlock_method.currentText()
            
            # 根据当前选择的验证方式检查是否满足自动验证条件
            if method == "密码解锁":
                password = self.password_input.text().strip()
                if password:  # 只有输入密码后才自动验证
                    self.verify()
                    
            elif method == "密钥文件解锁":
                key_file = self.key_file_input.text().strip()
                if key_file and os.path.exists(key_file):  # 只有选择了存在的密钥文件后才自动验证
                    self.verify()
                    
            elif method == "2FA验证":
                username = self.username_input.text().strip()
                totp_code = self.totp_input.text().strip()
                # 只有用户名和验证码都输入后才自动验证
                if username and totp_code and len(totp_code) >= 6:
                    self.verify()
                    
            elif method == "U盘解锁":
                # U盘解锁在检测到U盘时自动验证
                usb_drives = get_usb_drives()
                if usb_drives:  # 只有检测到U盘设备后才自动验证
                    self.verify()
                    
        except Exception as e:
            logger.error(f"自动验证失败: {e}")
            