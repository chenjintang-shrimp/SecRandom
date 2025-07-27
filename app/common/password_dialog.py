from qfluentwidgets import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import hashlib
import json
import pyotp
from loguru import logger
from app.common.config import get_theme_icon, load_custom_font, is_dark_theme

class PasswordDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("密码验证")
        self.setWindowIcon(QIcon('./app/resource/icon/SecRandom.png'))
        self.setFixedSize(400, 300)

        self.update_theme_style()
        qconfig.themeChanged.connect(self.update_theme_style)

        screen = QApplication.primaryScreen()
        desktop = screen.availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)

        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # 解锁方式选择
        self.unlock_method = ComboBox()
        self.unlock_method.addItems(["密码解锁", "密钥文件解锁", "2FA验证"])
        self.unlock_method.setFont(QFont(load_custom_font(), 14))
        layout.addWidget(self.unlock_method)

        # 密码输入框
        self.password_input = LineEdit()
        self.password_input.setPlaceholderText("请输入密码")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setFont(QFont(load_custom_font(), 14))
        # 回车确认
        self.password_input.returnPressed.connect(self.verify)
        layout.addWidget(self.password_input)

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

        layout.addLayout(key_file_layout)

        # 用户名输入框（2FA验证时显示）
        self.username_input = LineEdit()
        self.username_input.setPlaceholderText("请输入用户名")
        self.username_input.setFont(QFont(load_custom_font(), 14))
        layout.addWidget(self.username_input)

        # 2FA验证码
        self.totp_input = LineEdit()
        self.totp_input.setPlaceholderText("请输入2FA验证码")
        self.totp_input.setFont(QFont(load_custom_font(), 14))
        # 回车确认
        self.totp_input.returnPressed.connect(self.verify)
        layout.addWidget(self.totp_input)

        # 按钮
        self.verify_btn = PushButton("验证")
        self.verify_btn.clicked.connect(self.verify)
        self.verify_btn.setFont(QFont(load_custom_font(), 14))
        layout.addWidget(self.verify_btn)

        # 根据选择显示不同控件
        self.unlock_method.currentIndexChanged.connect(self.update_ui)
        self.update_ui()

    def update_theme_style(self):
        """根据当前主题更新样式"""
        is_dark = is_dark_theme(qconfig)
        if is_dark:
            self.setStyleSheet("""
                QDialog {
                    background-color: #111116;
                    color: #F5F5F5;
                }
                QLineEdit {
                    background-color: #3c3c3c;
                    color: #ffffff;
                    border: 1px solid #555555;
                    border-radius: 4px;
                    padding: 5px;
                }
                QPushButton {
                    background-color: #505050;
                    color: #ffffff;
                    border: 1px solid #555555;
                    border-radius: 4px;
                    padding: 5px;
                }
                QPushButton:hover {
                    background-color: #606060;
                }
                QComboBox {
                    background-color: #3c3c3c;
                    color: #ffffff;
                    border: 1px solid #555555;
                    border-radius: 4px;
                    padding: 5px;
                }
            """)
        else:
            self.setStyleSheet("""
                QDialog {
                    background-color: #111116;
                    color: #F5F5F5;
                }
                QLineEdit {
                    background-color: #ffffff;
                    color: #000000;
                    border: 1px solid #cccccc;
                    border-radius: 4px;
                    padding: 5px;
                }
                QPushButton {
                    background-color: #f0f0f0;
                    color: #000000;
                    border: 1px solid #cccccc;
                    border-radius: 4px;
                    padding: 5px;
                }
                QPushButton:hover {
                    background-color: #e0e0e0;
                }
                QComboBox {
                    background-color: #ffffff;
                    color: #000000;
                    border: 1px solid #cccccc;
                    border-radius: 4px;
                    padding: 5px;
                }
            """)

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
                        w = MessageBox("错误", "密码验证失败: 未设置密码", self)
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