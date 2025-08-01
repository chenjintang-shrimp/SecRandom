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

class PasswordDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        # 🌟 星穹铁道白露：设置无边框窗口样式并解决屏幕设置冲突~ 
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self.setWindowTitle("密码验证")
        self.setWindowIcon(QIcon('./app/resource/icon/SecRandom.png'))
        self.setFixedSize(400, 300)

        self.dragging = False
        self.drag_position = None

        # 确保不设置子窗口的屏幕属性
        if parent is not None:
            self.setParent(parent)
        
        # 🐦 小鸟游星野：创建自定义标题栏啦~ (≧∇≦)ﾉ
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
        content_layout.setContentsMargins(20, 10, 20, 20)
        layout.addLayout(content_layout)

        # 解锁方式选择
        self.unlock_method = ComboBox()
        self.unlock_method.addItems(["密码解锁", "密钥文件解锁", "2FA验证"])
        self.unlock_method.setFont(QFont(load_custom_font(), 14))
        content_layout.addWidget(self.unlock_method)

        # 密码输入框
        self.password_input = LineEdit()
        self.password_input.setPlaceholderText("请输入密码")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setFont(QFont(load_custom_font(), 14))
        # 回车确认
        self.password_input.returnPressed.connect(self.verify)
        content_layout.addWidget(self.password_input)

        # 密钥文件选择
        self.key_file_input = LineEdit()
        self.key_file_input.setPlaceholderText("请选择密钥文件")
        self.key_file_input.setFont(QFont(load_custom_font(), 14))
        self.key_file_btn = PushButton("选择文件")
        self.key_file_btn.setFont(QFont(load_custom_font(), 14))
        self.key_file_btn.clicked.connect(self.select_key_file)

        key_file_layout = QHBoxLayout()
        key_file_layout.addWidget(self.key_file_input)
        key_file_layout.addWidget(self.key_file_btn)

        content_layout.addLayout(key_file_layout)

        # 用户名输入框（2FA验证时显示）
        self.username_input = LineEdit()
        self.username_input.setPlaceholderText("请输入用户名")
        self.username_input.setFont(QFont(load_custom_font(), 14))
        content_layout.addWidget(self.username_input)

        # 2FA验证码
        self.totp_input = LineEdit()
        self.totp_input.setPlaceholderText("请输入2FA验证码")
        self.totp_input.setFont(QFont(load_custom_font(), 14))
        # 回车确认
        self.totp_input.returnPressed.connect(self.verify)
        content_layout.addWidget(self.totp_input)

        # 按钮
        self.verify_btn = PushButton("验证")
        self.verify_btn.clicked.connect(self.verify)
        self.verify_btn.setFont(QFont(load_custom_font(), 14))
        content_layout.addWidget(self.verify_btn)

        # 根据选择显示不同控件
        self.unlock_method.currentIndexChanged.connect(self.update_ui)
        self.update_ui()

    def mousePressEvent(self, event):
        # 🐦 小鸟游星野：窗口拖动功能~ 按住标题栏就能移动啦 (๑•̀ㅂ•́)و✧
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
        # 🌟 星穹铁道白露：主题样式更新 ~ 现在包含自定义标题栏啦！
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
                # 🌟 星穹铁道白露：修复参数类型错误~ 现在要把窗口ID转成整数才行哦！
                hwnd = int(self.winId())  # 转换为整数句柄
                
                # 🐦 小鸟游星野：颜色格式要改成ARGB才行呢~ 添加透明度通道(๑•̀ㅂ•́)و✧
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
        # 🐦 小鸟游星野：窗口拖动功能~ 按住标题栏就能移动啦 (๑•̀ㅂ•́)و✧
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

    def update_ui(self):
        method = self.unlock_method.currentText()
        self.password_input.setVisible(method == "密码解锁")
        self.key_file_input.setVisible(method == "密钥文件解锁")
        self.key_file_btn.setVisible(method == "密钥文件解锁")
        self.username_input.setVisible(method == "2FA验证")
        self.totp_input.setVisible(method == "2FA验证")

    def select_key_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "选择密钥文件", "", "Key Files (*.key)")
        if file_path:
            self.key_file_input.setText(file_path)

    def verify(self):
        try:
            with open('app/SecRandom/enc_set.json', 'r', encoding='utf-8') as f:
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
                        with open(key_file, 'rb') as f:
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
            with open('app/SecRandom/enc_set.json', 'r') as f:
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