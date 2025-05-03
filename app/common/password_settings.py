from qfluentwidgets import *
from qfluentwidgets import FluentIcon as FIF
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

import json
import os
from loguru import logger
import hashlib
import pyotp
from io import BytesIO
import re
import secrets
import ctypes

from app.common.config import load_custom_font

def create_hidden_folder(path):
    """创建隐藏文件夹"""
    try:
        if not os.path.exists(path):
            os.makedirs(path)
            if os.name == 'nt':
                ctypes.windll.kernel32.SetFileAttributesW(path, 2)
            return
        return
    except Exception as e:
        logger.error(f"创建隐藏文件夹失败: {e}")
        return

create_hidden_folder("app/SecRandom")

class UsernameInputDialog(MessageBoxBase):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.titleLabel = SubtitleLabel('输入用户名')
        self.titleLabel.setFont(QFont(load_custom_font(), 12))
        self.usernameLineEdit = LineEdit()

        self.usernameLineEdit.setPlaceholderText('请输入用于2FA的用户名(仅限英文大小写字母和数字)')
        self.usernameLineEdit.setClearButtonEnabled(True)
        self.usernameLineEdit.setFont(QFont(load_custom_font(), 12))
        self.usernameLineEdit.returnPressed.connect(self.accept)

        # 设置输入验证器，只允许英文大小写字母
        regex = QRegExp("[A-Za-z0-9]+")
        validator = QRegExpValidator(regex, self.usernameLineEdit)
        self.usernameLineEdit.setValidator(validator)

        self.warningLabel = CaptionLabel("用户名只能包含英文大小写字母、数字且不能为空")
        self.warningLabel.setTextColor("#cf1010", QColor(255, 28, 32))

        # 将组件添加到布局中
        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(self.usernameLineEdit)
        self.viewLayout.addWidget(self.warningLabel)
        self.warningLabel.hide()

        self.widget.setMinimumWidth(500)

    def validate(self):
        """ 重写验证表单数据的方法 """
        isValid = bool(re.match(r'^[A-Za-z0-9]+$', self.usernameLineEdit.text()))
        self.warningLabel.setHidden(isValid)
        return isValid

class TwoFactorAuthDialog(MessageBoxBase):
    """ 2FA设置对话框 """
    def __init__(self, parent=None, pixmap=None, secret=None):
        super().__init__(parent)
        self.secret = secret

        # 添加说明文本
        self.titleLabel = SubtitleLabel("请扫描二维码或输入密钥到Authenticator应用程序中", self)
        self.titleLabel.setAlignment(Qt.AlignCenter)
        self.titleLabel.setFont(QFont(load_custom_font(), 12))
        self.viewLayout.addWidget(self.titleLabel)

        # 创建水平布局容器
        hLayout = QHBoxLayout()
        hLayout.setSpacing(5)
        hLayout.setContentsMargins(0, 0, 0, 0)
        
        # 添加二维码图像
        self.qrLabel = ImageLabel()
        self.qrLabel.setFixedSize(150, 150)
        if pixmap and not pixmap.isNull():
            self.qrLabel.setPixmap(pixmap)
        else:
            logger.error('生成二维码图片失败，无法设置到标签上')
            raise ValueError('生成二维码图片失败')
        self.qrLabel.setAlignment(Qt.AlignCenter)
        hLayout.addWidget(self.qrLabel)

        # 创建垂直布局容器，用于放置密钥文本和验证码输入框
        vLayout = QVBoxLayout()
        vLayout.setSpacing(5)
        vLayout.setContentsMargins(0, 0, 0, 0)

        # 添加密钥文本
        self.secretLabel = BodyLabel(f"密钥: {self.secret}", self)
        self.secretLabel.setAlignment(Qt.AlignLeft)
        self.secretLabel.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.secretLabel.setFont(QFont(load_custom_font(), 12))
        # 允许文本自动换行
        self.secretLabel.setWordWrap(True)
        vLayout.addWidget(self.secretLabel)

        # 添加验证码输入框
        self.otpInput = LineEdit(self)
        self.otpInput.setFixedSize(200, 40)
        self.otpInput.setPlaceholderText("请输入验证码")
        self.otpInput.setFont(QFont(load_custom_font(), 12))
        self.otpInput.returnPressed.connect(self.accept)
        vLayout.addWidget(self.otpInput)

        # 将垂直布局添加到水平布局中
        hLayout.addLayout(vLayout)
        hLayout.addStretch(1)

        # 将水平布局添加到主布局
        container = QWidget()
        container.setLayout(hLayout)
        self.viewLayout.addWidget(container)

        # 使用MessageBoxBase的确认按钮
        self.yesButton.setText("验证")
        self.yesButton.clicked.disconnect()
        self.yesButton.clicked.connect(self.verify_otp)
        self.cancelButton.hide()
        self.buttonLayout.insertStretch(1)

    def verify_otp(self):
        """ 验证OTP码 """
        otp = self.otpInput.text()
        totp = pyotp.TOTP(self.secret)
        if totp.verify(otp):
            self.accept()
        else:
            InfoBar.warning(
                title="警告",
                content="验证码错误，请重新输入",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )
            self.otpInput.setFocus()

    def validate(self):
        """ 重写验证方法 """
        return True

class SimpleTwoFactorAuthDialog(MessageBoxBase):
    """ 2FA验证对话框 """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.titleLabel = SubtitleLabel('2FA验证(注:如是开关请确认是开还是关,有些BUG,见谅)', self)
        self.titleLabel.setFont(QFont(load_custom_font(), 12))
        self.codeLineEdit = LineEdit(self)
        self.warningLabel = CaptionLabel("验证码错误")
        self.warningLabel.setTextColor("#cf1010", QColor(255, 28, 32))

        # 设置输入框属性
        self.codeLineEdit.setPlaceholderText("请输入验证码")
        self.codeLineEdit.setClearButtonEnabled(True)
        self.codeLineEdit.setFont(QFont(load_custom_font(), 12))
        self.codeLineEdit.returnPressed.connect(self.accept)

        # 添加组件到布局
        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(self.codeLineEdit)
        self.viewLayout.addWidget(self.warningLabel)
        self.warningLabel.hide()

        # 设置对话框最小宽度
        self.widget.setMinimumWidth(350)

    def validate(self):
        """ 验证验证码 """
        code = self.codeLineEdit.text()
        
        # 从设置文件中获取2FA密钥
        settings_file = "app/SecRandom/enc_set.json"
        if os.path.exists(settings_file):
            with open(settings_file, 'r', encoding='utf-8') as f:
                try:
                    settings = json.load(f)
                    secret = settings.get("hashed_set", {}).get("2fa_secret")
                    if secret:
                        totp = pyotp.TOTP(secret)
                        isValid = totp.verify(code)
                        self.warningLabel.setHidden(isValid)
                        return isValid
                except json.JSONDecodeError:
                    pass
        
        self.warningLabel.setHidden(False)
        return False

class PasswordInputDialog(MessageBoxBase):
    """ 密码输入对话框 """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.titleLabel = SubtitleLabel('设置密码', self)
        self.titleLabel.setFont(QFont(load_custom_font(), 12))
        self.passwordLineEdit = LineEdit(self)
        self.confirmLineEdit = LineEdit(self)
        self.warningLabel = CaptionLabel("两次密码不一致")
        self.warningLabel.setTextColor("#cf1010", QColor(255, 28, 32))

        # 设置输入框属性
        self.passwordLineEdit.setEchoMode(QLineEdit.Password)
        self.passwordLineEdit.setPlaceholderText("请输入密码")
        self.passwordLineEdit.setClearButtonEnabled(True)
        self.passwordLineEdit.setFont(QFont(load_custom_font(), 12))
        self.passwordLineEdit.returnPressed.connect(self.confirmLineEdit.setFocus)
        
        self.confirmLineEdit.setEchoMode(QLineEdit.Password)
        self.confirmLineEdit.setPlaceholderText("请确认密码")
        self.confirmLineEdit.setClearButtonEnabled(True)
        self.confirmLineEdit.setFont(QFont(load_custom_font(), 12))
        self.confirmLineEdit.returnPressed.connect(self.accept)

        # 添加组件到布局
        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(self.passwordLineEdit)
        self.viewLayout.addWidget(self.confirmLineEdit)
        self.viewLayout.addWidget(self.warningLabel)
        self.warningLabel.hide()

        # 设置对话框最小宽度
        self.widget.setMinimumWidth(350)

    def validate(self):
        """ 验证密码是否一致 """
        password = self.passwordLineEdit.text()
        confirm = self.confirmLineEdit.text()
        
        isValid = password == confirm
        self.warningLabel.setHidden(isValid)
        return isValid

class PasswordDialog(MessageBoxBase):
    """ 密码对话框 """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.titleLabel = SubtitleLabel('输入密码(注:如是开关请确认是开还是关,有些BUG,见谅)')
        self.titleLabel.setFont(QFont(load_custom_font(), 12))
        self.passwordLineEdit = LineEdit(self)
        self.warningLabel = CaptionLabel("密码错误")
        self.warningLabel.setTextColor("#cf1010", QColor(255, 28, 32))

        # 设置输入框属性
        self.passwordLineEdit.setEchoMode(QLineEdit.Password)
        self.passwordLineEdit.setPlaceholderText("请输入密码")
        self.passwordLineEdit.setClearButtonEnabled(True)
        self.passwordLineEdit.setFont(QFont(load_custom_font(), 12))
        self.passwordLineEdit.returnPressed.connect(self.accept)

        # 添加组件到布局
        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(self.passwordLineEdit)
        self.viewLayout.addWidget(self.warningLabel)
        self.warningLabel.hide()

        # 设置对话框最小宽度
        self.widget.setMinimumWidth(350)

    def validate(self):
        """ 验证密码 """
        # 从设置文件中获取密码
        settings_file = "app/SecRandom/enc_set.json"
        if os.path.exists(settings_file):
            with open(settings_file, 'r', encoding='utf-8') as f:
                try:
                    settings = json.load(f)
                    hashed_password = settings.get("hashed_set", {}).get("hashed_password")
                    salt = settings.get("hashed_set", {}).get("password_salt")
                    if hashed_password and salt:
                        password = self.passwordLineEdit.text()
                        isValid = hashed_password == hashlib.md5((password + salt).encode()).hexdigest()
                        self.warningLabel.setHidden(isValid)
                        return isValid
                except json.JSONDecodeError:
                    pass
        
        self.warningLabel.setHidden(False)
        return False

class password_SettingsCard(GroupHeaderCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("密码设置")
        self.setBorderRadius(8)
        self.settings_file = "app/SecRandom/enc_set.json"
        self.secret_dir = "app/SecRandom"
        self.default_settings = {
            "start_password_enabled": False,
            "encrypt_setting_enabled": False,
            "two_factor_auth": False
        }

        self.start_password_switch = SwitchButton()
        self.encrypt_setting_switch = SwitchButton()
        self.two_factor_switch = SwitchButton()
        self.export_key_button = PushButton('导出密钥')
        self.set_password_button = PushButton('设置密码')

        self.export_key_button.setFont(QFont(load_custom_font(), 14))
        self.export_key_button.clicked.connect(self.export_key_file)

        # 密码功能开关
        self.start_password_switch.setOnText("开启")
        self.start_password_switch.setOffText("关闭")
        self.start_password_switch.checkedChanged.connect(self.start_password_switch_checked)
        self.start_password_switch.setFont(QFont(load_custom_font(), 14))

        # 设置是否启用加密相关设置/名单文件开关
        self.encrypt_setting_switch.setOnText("开启")
        self.encrypt_setting_switch.setOffText("关闭")
        self.encrypt_setting_switch.checkedChanged.connect(self.save_settings)
        self.encrypt_setting_switch.setFont(QFont(load_custom_font(), 14))

        # 设置2FA开关
        self.two_factor_switch.setOnText("启用")
        self.two_factor_switch.setOffText("关闭")
        self.two_factor_switch.checkedChanged.connect(self.on_2fa_changed)
        self.two_factor_switch.setFont(QFont(load_custom_font(), 14))

        # 设置密码按钮
        self.set_password_button.setFont(QFont(load_custom_font(), 14))
        self.set_password_button.clicked.connect(self.show_password_dialog)

        # 添加组件到分组中
        self.addGroup(FIF.VPN, "密码功能", "启用后将启用该设置卡的所有功能", self.start_password_switch)
        self.addGroup(FIF.VPN, "设置密码", "设置管理员账号密码", self.set_password_button)
        self.addGroup(FIF.DOWNLOAD, '密钥导出', '导出密钥文件', self.export_key_button)
        self.addGroup(FIF.CERTIFICATE, "双重认证", "启用2FA验证", self.two_factor_switch)
        # self.addGroup(FIF.VPN, "数据加密", "加密设置和名单文件", self.encrypt_setting_switch)

        self.load_settings()
        self.save_settings()

    def show_info_bar(self, status, title, content, duration=3000, parent=None):
        """
        :param status: 状态类型，'success'或'warning'或'error'
        :param title: 标题
        :param content: 内容
        :param duration: 显示时长(毫秒)
        :param parent: 父窗口
        """
        if status == 'success':
            InfoBar.success(
                title=title,
                content=content,
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=duration,
                parent=parent or self
            )
        elif status == 'error':
            InfoBar.error(
                title=title,
                content=content,
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=duration,
                parent=parent or self
            )
        elif status == 'warning':
            InfoBar.warning(
                title=title,
                content=content,
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=duration,
                parent=parent or self
            )

    def show_password_dialog(self):
        if not os.path.exists(self.settings_file):
            self.show_info_bar('error', '错误', '设置文件不存在', 3000, self)

            return

        try:
            with open(self.settings_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                hashed_set = settings.get("hashed_set", {})
                if hashed_set.get("verification_start") == True:
                    with open(self.settings_file, 'r', encoding='utf-8') as f:
                        settings = json.load(f)
                        hashed_set = settings.get("hashed_set", {})
                        if not hashed_set.get("hashed_password") or not hashed_set.get("password_salt"):
                            dialog = PasswordInputDialog(self)
                            dialog.yesButton.setText("确认")
                            dialog.cancelButton.setText("取消")
                            if dialog.exec():
                                self.validate_and_save_password(dialog, dialog.passwordLineEdit, dialog.confirmLineEdit)
                        elif hashed_set.get("hashed_password") and hashed_set.get("password_salt"):
                            dialog = PasswordDialog(self)
                            dialog.yesButton.setText("确认")
                            dialog.cancelButton.setText("取消")
                            if dialog.exec_() == QDialog.Accepted:
                                if hashed_set.get("two_factor_auth") == True:
                                    dialog = SimpleTwoFactorAuthDialog(self)
                                    dialog.yesButton.setText("确认")
                                    dialog.cancelButton.setText("取消")
                                    if dialog.exec_() == QDialog.Accepted:
                                        dialog = PasswordInputDialog(self)
                                        dialog.yesButton.setText("确认")
                                        dialog.cancelButton.setText("取消")
                                        if dialog.exec():
                                            self.validate_and_save_password(dialog, dialog.passwordLineEdit, dialog.confirmLineEdit)
                                        return
                                    else:
                                        self.show_info_bar('warning', '警告', '密码设置已取消', 3000, self)
                                        return
                                else:
                                    dialog = PasswordInputDialog(self)
                                    dialog.yesButton.setText("确认")
                                    dialog.cancelButton.setText("取消")
                                    if dialog.exec():
                                        self.validate_and_save_password(dialog, dialog.passwordLineEdit, dialog.confirmLineEdit)
                                    return
                            else:
                                self.show_info_bar('warning', '警告', '密码设置已取消', 3000, self)
                                return
        except json.JSONDecodeError as e:
            self.show_info_bar('error', '错误', '设置文件损坏', 3000, self)
            return

    def validate_and_save_password(self, dialog, password_input, confirm_password_input):
        password = password_input.text()
        confirm_password = confirm_password_input.text()

        if password != confirm_password:
            self.show_info_bar('error', '错误', "两次输入的密码不一致", 3000, self)
            return

        # 生成随机盐值
        salt = secrets.token_hex(16)
        hashed_password = hashlib.md5((password + salt).encode()).hexdigest()

        # 保存密码和盐值到设置文件
        existing_settings = {}
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    existing_settings = json.load(f)
            except json.JSONDecodeError:
                existing_settings = {}

        if "hashed_set" not in existing_settings:
            existing_settings["hashed_set"] = {}
        existing_settings["hashed_set"]["hashed_password"] = hashed_password
        existing_settings["hashed_set"]["password_salt"] = salt

        with open(self.settings_file, 'w', encoding='utf-8') as f:
            json.dump(existing_settings, f, indent=4)

        logger.info("密码设置成功")
        self.show_info_bar('success', '成功', "密码设置成功", 3000, self)
        dialog.accept()

    def start_password_switch_checked(self):
        if not os.path.exists(self.settings_file):
            self.show_info_bar('error', '错误', '设置文件不存在', 3000, self)
            self.start_password_switch.setChecked(False)
            return

        try:
            with open(self.settings_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                hashed_set = settings.get("hashed_set", {})
                if hashed_set.get("verification_start") == True:
                    with open(self.settings_file, 'r', encoding='utf-8') as f:
                        settings = json.load(f)
                        hashed_set = settings.get("hashed_set", {})
                        if not hashed_set.get("hashed_password") or not hashed_set.get("password_salt"):
                            self.show_info_bar('warning', '警告', '请先设置密码', 3000, self)
                            self.start_password_switch.setChecked(False)
                            return
                        elif hashed_set.get("hashed_password") and hashed_set.get("password_salt"):
                            dialog = PasswordDialog(self)
                            dialog.yesButton.setText("确认")
                            dialog.cancelButton.setText("取消")
                            if dialog.exec_() == QDialog.Accepted:
                                if hashed_set.get("two_factor_auth") == True:
                                    dialog = SimpleTwoFactorAuthDialog(self)
                                    dialog.yesButton.setText("确认")
                                    dialog.cancelButton.setText("取消")
                                    if dialog.exec_() == QDialog.Accepted:
                                        self.save_settings()
                                        return
                                    else:
                                        if hashed_set.get("start_password_enabled") == True:
                                            self.show_info_bar('warning', '警告', '启动设置需密码已取消', 3000, self)
                                            self.start_password_switch.setChecked(True)
                                            self.save_settings()
                                        else:
                                            self.show_info_bar('warning', '警告', '启动设置需密码已取消', 3000, self)
                                            self.start_password_switch.setChecked(False)
                                            self.save_settings()
                                        return
                                else:
                                    self.save_settings()
                                    return
                            else:
                                if hashed_set.get("start_password_enabled") == True:
                                    self.show_info_bar('warning', '警告', '启动设置需密码已取消', 3000, self)
                                    self.start_password_switch.setChecked(True)
                                    self.save_settings()
                                else:
                                    self.show_info_bar('warning', '警告', '启动设置需密码已取消', 3000, self)
                                    self.start_password_switch.setChecked(False)
                                    self.save_settings()
                                return
        except json.JSONDecodeError as e:
            self.show_info_bar('error', '错误', '设置文件损坏', 3000, self)
            self.start_password_switch.setChecked(False)
            return

    def on_2fa_changed(self):
        if not os.path.exists(self.settings_file):
            self.show_info_bar('error', '错误', '设置文件不存在', 3000, self)
            self.two_factor_switch.setChecked(False)
            return

        try:
            with open(self.settings_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                hashed_set = settings.get("hashed_set", {})
                if hashed_set.get("verification_start") == True:
                    with open(self.settings_file, 'r', encoding='utf-8') as f:
                        settings = json.load(f)
                        hashed_set = settings.get("hashed_set", {})
                        if not hashed_set.get("hashed_password") or not hashed_set.get("password_salt"):
                            self.show_info_bar('warning', '警告', '请先设置密码', 3000, self)
                            self.two_factor_switch.setChecked(False)
                            self.save_settings()
                            return
                        elif hashed_set.get("hashed_password") and hashed_set.get("password_salt"):
                            dialog = PasswordDialog(self)
                            dialog.yesButton.setText("确认")
                            dialog.cancelButton.setText("取消")
                            if dialog.exec_() == QDialog.Accepted:
                                if hashed_set.get("two_factor_auth") == True:
                                    dialog = SimpleTwoFactorAuthDialog(self)
                                    dialog.yesButton.setText("确认")
                                    dialog.cancelButton.setText("取消")
                                    if dialog.exec_() == QDialog.Accepted:
                                        existing_settings = {}
                                        try:
                                            with open(self.settings_file, 'r', encoding='utf-8') as f:
                                                existing_settings = json.load(f)
                                        except json.JSONDecodeError:
                                            existing_settings = {}
                                        if "hashed_set" not in existing_settings or "2fa_secret" not in existing_settings["hashed_set"]:
                                            self.save_settings()
                                        else:
                                            existing_settings["hashed_set"].pop("encrypted_username", None)
                                            existing_settings["hashed_set"].pop("2fa_secret", None)
                                            with open(self.settings_file, 'w', encoding='utf-8') as f:
                                                json.dump(existing_settings, f, indent=4)
                                            self.save_settings()
                                    else:
                                        if hashed_set.get("two_factor_auth") == True:
                                            self.show_info_bar('warning', '警告', '2FA验证已取消', 3000, self)
                                            self.two_factor_switch.setChecked(True)
                                            self.save_settings()
                                        else:
                                            self.show_info_bar('warning', '警告', '2FA验证已取消', 3000, self)
                                            self.two_factor_switch.setChecked(False)
                                            self.save_settings()
                                        return
                                else:
                                    existing_settings = {}
                                    try:
                                        with open(self.settings_file, 'r', encoding='utf-8') as f:
                                            existing_settings = json.load(f)
                                    except json.JSONDecodeError:
                                        existing_settings = {}
                                    if "hashed_set" not in existing_settings or "2fa_secret" not in existing_settings["hashed_set"]:
                                        self.setup_2fa()
                                        self.save_settings()
                                    else:
                                        self.save_settings()
                                    return
                            else:
                                if hashed_set.get("two_factor_auth") == True:
                                    self.show_info_bar('warning', '警告', '2FA验证已取消', 3000, self)
                                    self.two_factor_switch.setChecked(True)
                                    self.save_settings()
                                else:
                                    self.show_info_bar('warning', '警告', '2FA验证已取消', 3000, self)
                                    self.two_factor_switch.setChecked(False)
                                    self.save_settings()
                                return
        except json.JSONDecodeError as e:
            self.show_info_bar('error', '错误', '设置文件损坏', 3000, self)
            self.two_factor_switch.setChecked(False)
            return

    def setup_2fa(self):
        """初始化2FA设置"""
        global username
        try:
            dialog = UsernameInputDialog(self)
            dialog.yesButton.setText("确认")
            dialog.cancelButton.setText("取消")
            if dialog.exec():
                username = dialog.usernameLineEdit.text()
                if not username:
                    return

            # 对用户名进行MD5加盐加密
            salt = 'SecRandomSalt'
            hashed_username = hashlib.md5((username + salt).encode()).hexdigest()

            # 从enc_set.json读取或生成2FA密钥
            os.makedirs(self.secret_dir, exist_ok=True)

            # 读取现有设置
            existing_settings = {}
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    existing_settings = json.load(f)
            except json.JSONDecodeError:
                existing_settings = {}

            # 将加密后的用户名存储到enc_set.json中
            if "hashed_set" not in existing_settings:
                existing_settings["hashed_set"] = {}
            existing_settings["hashed_set"]["encrypted_username"] = hashed_username

            # 保存设置
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(existing_settings, f, indent=4)

            # 获取或生成密钥
            if "hashed_set" not in existing_settings or "2fa_secret" not in existing_settings["hashed_set"]:
                self.secret = pyotp.random_base32()
                if "hashed_set" not in existing_settings:
                    existing_settings["hashed_set"] = {}
                existing_settings["hashed_set"]["2fa_secret"] = self.secret

                # 保存设置
                with open(self.settings_file, 'w', encoding='utf-8') as f:
                    json.dump(existing_settings, f, indent=4)
            else:
                self.secret = existing_settings["hashed_set"]["2fa_secret"]

            # 生成二维码URI
            totp = pyotp.TOTP(self.secret)
            uri = totp.provisioning_uri(
                name=username,
                issuer_name="SecRandom"
            )

            import qrcode

            # 创建二维码对象
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(uri)
            qr.make(fit=True)

            # 生成二维码图片
            img = qr.make_image(fill_color="black", back_color="white")

            # 转换为QPixmap
            byte_array = BytesIO()
            img.save(byte_array, 'PNG')
            pixmap = QPixmap()
            pixmap.loadFromData(byte_array.getvalue())
            pixmap = pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)

            # 创建自定义2FA对话框
            dialog = TwoFactorAuthDialog(self, pixmap, self.secret)
            dialog.yesButton.setText("确认")
            dialog.cancelButton.setText("取消")
            if not dialog.exec():
                self.two_factor_switch.setChecked(False)

        except Exception as e:
            self.show_info_bar('error', '错误', f"2FA设置失败: {str(e)}", 3000, self)
            return

    def export_key_file(self):
        if not os.path.exists(self.settings_file):
            self.show_info_bar('error', '错误', '设置文件不存在', 3000, self)
            return

        try:
            with open(self.settings_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                hashed_set = settings.get("hashed_set", {})
                if not hashed_set.get("hashed_password") or not hashed_set.get("password_salt"):
                    self.show_info_bar('warning', '警告', '请先设置密码', 3000, self)
                    return
                elif hashed_set.get("hashed_password") and hashed_set.get("password_salt"):
                    dialog = PasswordDialog(self)
                    dialog.yesButton.setText("确认")
                    dialog.cancelButton.setText("取消")
                    if dialog.exec_() == QDialog.Accepted:
                        if hashed_set.get("two_factor_auth") == True:
                            dialog = SimpleTwoFactorAuthDialog(self)
                            dialog.yesButton.setText("确认")
                            dialog.cancelButton.setText("取消")
                            if dialog.exec_() == QDialog.Accepted:
                                path = QFileDialog.getSaveFileName(self, '保存密钥文件', 'SecRandom', 'Key Files (*.key)')[0]
                                if path:
                                    hashed_password = settings.get("hashed_set", {}).get("hashed_password")
                                    if hashed_password:
                                        self._save_key_file(path, hashed_password)
                                    else:
                                        self.show_info_bar('error', '错误', '未找到密码', 3000, self)
                            else:
                                self.show_info_bar('warning', '警告', '导出密钥已取消', 3000, self)
                                return
                        else:
                            path = QFileDialog.getSaveFileName(self, '保存密钥文件', 'SecRandom', 'Key Files (*.key)')[0]
                            if path:
                                hashed_password = settings.get("hashed_set", {}).get("hashed_password")
                                if hashed_password:
                                    self._save_key_file(path, hashed_password)
                                else:
                                    self.show_info_bar('error', '错误', '未找到密码', 3000, self)
                        return
                    else:
                        return
        except json.JSONDecodeError as e:
            self.show_info_bar('error', '错误', f'设置文件损坏: {e}', 3000, self)
            return

    def _save_key_file(self, path, hashed_password):
        try:
            with open(path, 'w') as f:
                f.write(hashed_password)
        except Exception as e:
            self.show_info_bar('error', '错误', f"密钥导出失败: {str(e)}", 3000, self)

    def load_settings(self):
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    hashed_set_settings = settings.get("hashed_set", {})

                    self.start_password_switch.setChecked(
                        hashed_set_settings.get("start_password_enabled", self.default_settings["start_password_enabled"])
                    )
                    self.encrypt_setting_switch.setChecked(
                        hashed_set_settings.get("encrypt_setting_enabled", self.default_settings["encrypt_setting_enabled"])
                    )
                    self.two_factor_switch.setChecked(
                        hashed_set_settings.get("two_factor_auth", self.default_settings["two_factor_auth"])
                    )
                    logger.info("安全设置加载完成")
            else:
                logger.warning(f"设置文件不存在: {self.settings_file}")
                self.start_password_switch.setChecked(self.default_settings["start_password_enabled"])
                self.encrypt_setting_switch.setChecked(self.default_settings["encrypt_setting_enabled"])
                self.two_factor_switch.setChecked(self.default_settings["two_factor_auth"])
        except Exception as e:
            logger.error(f"加载设置时出错: {e}")
            self.start_password_switch.setChecked(self.default_settings["start_password_enabled"])
            self.encrypt_setting_switch.setChecked(self.default_settings["encrypt_setting_enabled"])
            self.two_factor_switch.setChecked(self.default_settings["two_factor_auth"])

    def save_settings(self):
        # 先读取现有设置
        _existing_settings = {}
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    _existing_settings = json.load(f)
        except json.JSONDecodeError:
            _existing_settings = {}

        # 更新hashed_set部分的所有设置
        if "hashed_set" not in _existing_settings:
            _existing_settings["hashed_set"] = {}

        if "hashed_set" in _existing_settings and "2fa_secret" not in _existing_settings["hashed_set"]:
            self.two_factor_switch.setChecked(False)
        if "hashed_set" in _existing_settings and ("hashed_password" not in _existing_settings["hashed_set"] or "password_salt" not in _existing_settings["hashed_set"]):
            self.start_password_switch.setChecked(False)
        if _existing_settings["hashed_set"].get("two_factor_auth") == True:
            if "hashed_set" in _existing_settings and "2fa_secret" not in _existing_settings["hashed_set"]:
                self.two_factor_switch.setChecked(False)

        _existing_settings["hashed_set"].update({
            "start_password_enabled": self.start_password_switch.isChecked(),
            "encrypt_setting_enabled": self.encrypt_setting_switch.isChecked(),
            "two_factor_auth": self.two_factor_switch.isChecked()
        })

        os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)

        with open(self.settings_file, 'w', encoding='utf-8') as f:
            json.dump(_existing_settings, f, indent=4)