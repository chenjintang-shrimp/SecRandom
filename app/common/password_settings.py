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
import pyqrcode
import re
import secrets
import ctypes

from app.common.config import get_theme_icon, load_custom_font
from app.common.path_utils import path_manager, open_file

def create_hidden_folder(path):
    """创建隐藏文件夹"""
    try:
        if not path_manager.file_exists(path):
            os.makedirs(path)
            if os.name == 'nt':
                ctypes.windll.kernel32.SetFileAttributesW(path, 2)
            return
        return
    except Exception as e:
        logger.error(f"创建隐藏文件夹失败: {e}")
        return

# 获取应用根目录并构建SecRandom文件夹路径
secrandom_dir = path_manager._get_app_root()
create_hidden_folder(secrandom_dir)

def generate_qr_code(secret, username):
    """生成二维码"""
    try:
        totp = pyotp.TOTP(secret)
        uri = totp.provisioning_uri(
            name=username,
            issuer_name="SecRandom"
        )
        qr = pyqrcode.create(uri, error='L', version=5, mode='binary')
        buffer = BytesIO()
        qr.png(buffer, scale=10, module_color=[0, 0, 0, 255], background=[255, 255, 255, 255])
        pixmap = QPixmap()
        pixmap.loadFromData(buffer.getvalue())
        pixmap = pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        return pixmap
    except Exception as e:
        logger.error(f"生成二维码失败: {e}")
        return None

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
        """ 验证TOTP码 """
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
        self.titleLabel = SubtitleLabel('2FA验证', self)
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
        
        # 从设置文件中获取2FA密钥和用户名
        settings_file = path_manager.get_enc_set_path()
        if settings_file.exists():
            with open_file(settings_file, 'r', encoding='utf-8') as f:
                try:
                    settings = json.load(f)
                    secret = settings.get("hashed_set", {}).get("2fa_secret")
                    encrypted_username = settings.get("hashed_set", {}).get("encrypted_username")
                    
                    # 检查用户名是否存在
                    if not encrypted_username:
                        self.warningLabel.setText("2FA用户名未设置，请先设置用户名")
                        self.warningLabel.setHidden(False)
                        return False
                    
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
        self.titleLabel = SubtitleLabel('输入密码')
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
        settings_file = path_manager.get_enc_set_path()
        if path_manager.file_exists(settings_file):
            with open_file(settings_file, 'r', encoding='utf-8') as f:
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

class ChangePasswordDialog(MessageBoxBase):
    """ 修改密码对话框 """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.titleLabel = SubtitleLabel('修改密码')
        self.titleLabel.setFont(QFont(load_custom_font(), 12))
        
        # 当前密码输入框
        self.currentPasswordLabel = BodyLabel('当前密码:')
        self.currentPasswordLabel.setFont(QFont(load_custom_font(), 12))
        self.currentPasswordLineEdit = LineEdit(self)
        self.currentPasswordLineEdit.setEchoMode(QLineEdit.Password)
        self.currentPasswordLineEdit.setPlaceholderText("请输入当前密码")
        self.currentPasswordLineEdit.setClearButtonEnabled(True)
        self.currentPasswordLineEdit.setFont(QFont(load_custom_font(), 12))
        
        # 新密码输入框
        self.newPasswordLabel = BodyLabel('新密码:')
        self.newPasswordLabel.setFont(QFont(load_custom_font(), 12))
        self.newPasswordLineEdit = LineEdit(self)
        self.newPasswordLineEdit.setEchoMode(QLineEdit.Password)
        self.newPasswordLineEdit.setPlaceholderText("请输入新密码")
        self.newPasswordLineEdit.setClearButtonEnabled(True)
        self.newPasswordLineEdit.setFont(QFont(load_custom_font(), 12))
        
        # 确认新密码输入框
        self.confirmPasswordLabel = BodyLabel('确认新密码:')
        self.confirmPasswordLabel.setFont(QFont(load_custom_font(), 12))
        self.confirmPasswordLineEdit = LineEdit(self)
        self.confirmPasswordLineEdit.setEchoMode(QLineEdit.Password)
        self.confirmPasswordLineEdit.setPlaceholderText("请确认新密码")
        self.confirmPasswordLineEdit.setClearButtonEnabled(True)
        self.confirmPasswordLineEdit.setFont(QFont(load_custom_font(), 12))
        
        self.warningLabel = CaptionLabel("")
        self.warningLabel.setTextColor("#cf1010", QColor(255, 28, 32))

        # 设置输入框回车键切换焦点
        self.currentPasswordLineEdit.returnPressed.connect(self.newPasswordLineEdit.setFocus)
        self.newPasswordLineEdit.returnPressed.connect(self.confirmPasswordLineEdit.setFocus)
        self.confirmPasswordLineEdit.returnPressed.connect(self.accept)

        # 添加组件到布局
        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(self.currentPasswordLabel)
        self.viewLayout.addWidget(self.currentPasswordLineEdit)
        self.viewLayout.addWidget(self.newPasswordLabel)
        self.viewLayout.addWidget(self.newPasswordLineEdit)
        self.viewLayout.addWidget(self.confirmPasswordLabel)
        self.viewLayout.addWidget(self.confirmPasswordLineEdit)
        self.viewLayout.addWidget(self.warningLabel)
        self.warningLabel.hide()

        # 设置对话框最小宽度
        self.widget.setMinimumWidth(400)

    def validate(self):
        """ 验证密码修改 """
        current_password = self.currentPasswordLineEdit.text()
        new_password = self.newPasswordLineEdit.text()
        confirm_password = self.confirmPasswordLineEdit.text()
        
        # 检查新密码和确认密码是否一致
        if new_password != confirm_password:
            self.warningLabel.setText("两次输入的新密码不一致")
            self.warningLabel.show()
            return False
        
        # 检查新密码是否为空
        if not new_password:
            self.warningLabel.setText("新密码不能为空")
            self.warningLabel.show()
            return False
        
        # 检查新密码是否与当前密码相同
        if new_password == current_password:
            self.warningLabel.setText("新密码不能与当前密码相同")
            self.warningLabel.show()
            return False
        
        # 验证当前密码是否正确
        settings_file = path_manager.get_enc_set_path()
        if path_manager.file_exists(settings_file):
            with open_file(settings_file, 'r', encoding='utf-8') as f:
                try:
                    settings = json.load(f)
                    hashed_password = settings.get("hashed_set", {}).get("hashed_password")
                    salt = settings.get("hashed_set", {}).get("password_salt")
                    if hashed_password and salt:
                        is_current_valid = hashed_password == hashlib.md5((current_password + salt).encode()).hexdigest()
                        if not is_current_valid:
                            self.warningLabel.setText("当前密码错误")
                            self.warningLabel.show()
                            return False
                except json.JSONDecodeError:
                    self.warningLabel.setText("设置文件损坏")
                    self.warningLabel.show()
                    return False
        
        self.warningLabel.hide()
        return True

class ChangeUsernameDialog(MessageBoxBase):
    """ 修改2FA用户名对话框 """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.titleLabel = SubtitleLabel('修改2FA用户名')
        self.titleLabel.setFont(QFont(load_custom_font(), 12))
        
        # 当前用户名显示
        self.currentUsernameLabel = BodyLabel('当前用户名:')
        self.currentUsernameLabel.setFont(QFont(load_custom_font(), 12))
        self.currentUsernameValue = BodyLabel('')
        self.currentUsernameValue.setFont(QFont(load_custom_font(), 12))
        
        # 新用户名输入框
        self.newUsernameLabel = BodyLabel('新用户名:')
        self.newUsernameLabel.setFont(QFont(load_custom_font(), 12))
        self.newUsernameLineEdit = LineEdit(self)
        self.newUsernameLineEdit.setPlaceholderText('请输入新的2FA用户名(仅限英文大小写字母和数字)')
        self.newUsernameLineEdit.setClearButtonEnabled(True)
        self.newUsernameLineEdit.setFont(QFont(load_custom_font(), 12))
        self.newUsernameLineEdit.returnPressed.connect(self.accept)
        
        # 设置输入验证器，只允许英文大小写字母
        regex = QRegExp("[A-Za-z0-9]+")
        validator = QRegExpValidator(regex, self.newUsernameLineEdit)
        self.newUsernameLineEdit.setValidator(validator)
        
        self.warningLabel = CaptionLabel("用户名只能包含英文大小写字母、数字且不能为空")
        self.warningLabel.setTextColor("#cf1010", QColor(255, 28, 32))

        # 添加组件到布局
        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(self.currentUsernameLabel)
        self.viewLayout.addWidget(self.currentUsernameValue)
        self.viewLayout.addWidget(self.newUsernameLabel)
        self.viewLayout.addWidget(self.newUsernameLineEdit)
        self.viewLayout.addWidget(self.warningLabel)
        self.warningLabel.hide()

        # 设置对话框最小宽度
        self.widget.setMinimumWidth(500)
        
        # 加载当前用户名
        self._load_current_username()
    
    def _load_current_username(self):
        """加载当前用户名"""
        settings_file = path_manager.get_enc_set_path()
        if path_manager.file_exists(settings_file):
            try:
                with open_file(settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    encrypted_username = settings.get("hashed_set", {}).get("encrypted_username")
                    if encrypted_username:
                        salt = 'SecRandomSalt'
                        # 这里无法直接解密，因为MD5是单向哈希
                        # 显示为已加密状态
                        self.currentUsernameValue.setText("[已加密存储]")
                    else:
                        self.currentUsernameValue.setText("[未设置]")
            except json.JSONDecodeError:
                self.currentUsernameValue.setText("[设置文件损坏]")
        else:
            self.currentUsernameValue.setText("[设置文件不存在]")

    def validate(self):
        """ 验证用户名修改 """
        new_username = self.newUsernameLineEdit.text()
        
        # 检查用户名格式
        isValid = bool(re.match(r'^[A-Za-z0-9]+$', new_username))
        if not isValid:
            self.warningLabel.setText("用户名只能包含英文大小写字母、数字且不能为空")
            self.warningLabel.show()
            return False
        
        self.warningLabel.hide()
        return True

class password_SettingsCard(GroupHeaderCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("密码设置")
        self.setBorderRadius(8)
        self.settings_file = path_manager.get_enc_set_path()
        self.secret_dir = secrandom_dir
        self.default_settings = {
            "start_password_enabled": False,
            "encrypt_setting_enabled": False,
            "two_factor_auth": False,
            "exit_verification_enabled": False,
            "restart_verification_enabled": False,
            "show_hide_verification_enabled": False,
            "usb_auth_enabled": False
        }

        # 密码功能开关
        self.start_password_switch = SwitchButton()
        self.start_password_switch.setOnText("开启")
        self.start_password_switch.setOffText("关闭")
        self.start_password_switch.checkedChanged.connect(self.start_password_switch_checked)
        self.start_password_switch.setFont(QFont(load_custom_font(), 12))

        # 设置是否启用加密相关设置/名单文件开关
        self.encrypt_setting_switch = SwitchButton()
        self.encrypt_setting_switch.setOnText("开启")
        self.encrypt_setting_switch.setOffText("关闭")
        self.encrypt_setting_switch.checkedChanged.connect(lambda: self.verify_password_for_action('加密设置', 'encrypt'))
        self.encrypt_setting_switch.setFont(QFont(load_custom_font(), 12))

        # 设置2FA开关
        self.two_factor_switch = SwitchButton()
        self.two_factor_switch.setOnText("启用")
        self.two_factor_switch.setOffText("关闭")
        self.two_factor_switch.checkedChanged.connect(self.on_2fa_changed)
        self.two_factor_switch.setFont(QFont(load_custom_font(), 12))

        # 导出密钥按钮
        self.export_key_button = PushButton('导出密钥')
        self.export_key_button.setFont(QFont(load_custom_font(), 12))
        self.export_key_button.clicked.connect(self.export_key_file)

        # 设置密码按钮
        self.set_password_button = PushButton('设置密码')
        self.set_password_button.setFont(QFont(load_custom_font(), 12))
        self.set_password_button.clicked.connect(self.show_password_dialog)
        
        # 修改密码按钮
        self.change_password_button = PushButton('修改密码')
        self.change_password_button.setFont(QFont(load_custom_font(), 12))
        self.change_password_button.clicked.connect(self.show_change_password_dialog)
        
        # 修改2FA用户名按钮
        self.change_username_button = PushButton('修改2FA用户名')
        self.change_username_button.setFont(QFont(load_custom_font(), 12))
        self.change_username_button.clicked.connect(self.show_change_username_dialog)

        # 退出软件是否需要验证密码开关
        self.exit_verification_switch = SwitchButton()
        self.exit_verification_switch.setOnText("开启")
        self.exit_verification_switch.setOffText("关闭")
        self.exit_verification_switch.checkedChanged.connect(lambda: self.verify_password_for_action('退出软件需要密码', 'exit'))
        self.exit_verification_switch.setFont(QFont(load_custom_font(), 12))

        # 重启软件是否需要验证密码开关
        self.restart_verification_switch = SwitchButton()
        self.restart_verification_switch.setOnText("开启")
        self.restart_verification_switch.setOffText("关闭")
        self.restart_verification_switch.checkedChanged.connect(lambda: self.verify_password_for_action('重启软件需要密码', 'restart'))
        self.restart_verification_switch.setFont(QFont(load_custom_font(), 12))

        # 暂时显示/隐藏悬浮窗是否需要验证密码开关
        self.show_hide_verification_switch = SwitchButton()
        self.show_hide_verification_switch.setOnText("开启")
        self.show_hide_verification_switch.setOffText("关闭")
        self.show_hide_verification_switch.checkedChanged.connect(lambda: self.verify_password_for_action('显示/隐藏悬浮窗需要密码', 'show_hide'))
        self.show_hide_verification_switch.setFont(QFont(load_custom_font(), 12))

        # 添加组件到分组中
        self.addGroup(get_theme_icon("ic_fluent_person_passkey_20_filled"), "密码功能", "启用后将启用该设置卡的所有功能", self.start_password_switch)
        self.addGroup(get_theme_icon("ic_fluent_password_20_filled"), "设置密码", "设置管理员账号密码", self.set_password_button)
        self.addGroup(get_theme_icon("ic_fluent_password_20_filled"), "修改密码", "修改管理员账号密码", self.change_password_button)
        self.addGroup(get_theme_icon("ic_fluent_document_key_20_filled"), '密钥导出', '导出密钥文件', self.export_key_button)
        self.addGroup(get_theme_icon("ic_fluent_certificate_20_filled"), "双重认证", "启用2FA验证", self.two_factor_switch)
        self.addGroup(get_theme_icon("ic_fluent_person_20_filled"), "修改2FA用户名", "修改双因素认证的用户名", self.change_username_button)
        # self.addGroup(FIF.VPN, "数据加密", "加密设置和名单文件", self.encrypt_setting_switch)
        if path_manager.file_exists('_internal'):
            self.addGroup(get_theme_icon("ic_fluent_arrow_reset_20_filled"), "重启软件验证", "重启软件时需要验证密码", self.restart_verification_switch)
        self.addGroup(get_theme_icon("ic_fluent_arrow_exit_20_filled"), "退出软件验证", "退出软件时需要验证密码", self.exit_verification_switch)
        self.addGroup(get_theme_icon("ic_fluent_window_ad_20_filled"), "暂时显示/隐藏悬浮窗验证", "暂时显示/隐藏悬浮窗时需要验证密码", self.show_hide_verification_switch)


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

    def verify_password_for_action(self, action_type, type):
        """验证密码和2FA"""
        if not path_manager.file_exists(self.settings_file):
            return False

        try:
            with open_file(self.settings_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                hashed_set = settings.get("hashed_set", {})
                if hashed_set.get("verification_start") == True:
                    if not hashed_set.get("hashed_password") or not hashed_set.get("password_salt"):
                        self.show_info_bar('error', '错误', '请先设置密码', 3000, self)
                        # 阻止开关状态改变，恢复到原始状态
                        if type == 'exit':
                            self.exit_verification_switch.blockSignals(True)
                            self.exit_verification_switch.setChecked(False)
                            self.exit_verification_switch.blockSignals(False)
                        elif type == 'restart':
                            self.restart_verification_switch.blockSignals(True)
                            self.restart_verification_switch.setChecked(False)
                            self.restart_verification_switch.blockSignals(False)
                        elif type == 'show_hide':
                            self.show_hide_verification_switch.blockSignals(True)
                            self.show_hide_verification_switch.setChecked(False)
                            self.show_hide_verification_switch.blockSignals(False)
                        elif type == 'encrypt':
                            self.encrypt_setting_switch.blockSignals(True)
                            self.encrypt_setting_switch.setChecked(False)
                            self.encrypt_setting_switch.blockSignals(False)
                        return False

                    dialog = PasswordDialog(self)
                    dialog.yesButton.setText("确认")
                    dialog.cancelButton.setText("取消")
                    if dialog.exec_() != QDialog.Accepted:
                        # 用户取消密码验证，恢复到原始状态
                        if type == 'exit':
                            original_state = hashed_set.get("exit_verification_enabled", False)
                            self.exit_verification_switch.blockSignals(True)
                            self.exit_verification_switch.setChecked(original_state)
                            self.exit_verification_switch.blockSignals(False)
                            self.show_info_bar('warning', '警告', f'{action_type}功能设置已取消', 3000, self)
                        elif type == 'restart':
                            original_state = hashed_set.get("restart_verification_enabled", False)
                            self.restart_verification_switch.blockSignals(True)
                            self.restart_verification_switch.setChecked(original_state)
                            self.restart_verification_switch.blockSignals(False)
                            self.show_info_bar('warning', '警告', f'{action_type}功能设置已取消', 3000, self)
                        elif type == 'show_hide':
                            original_state = hashed_set.get("show_hide_verification_enabled", False)
                            self.show_hide_verification_switch.blockSignals(True)
                            self.show_hide_verification_switch.setChecked(original_state)
                            self.show_hide_verification_switch.blockSignals(False)
                            self.show_info_bar('warning', '警告', f'{action_type}功能设置已取消', 3000, self)
                        elif type == 'encrypt':
                            original_state = hashed_set.get("encrypt_setting_enabled", False)
                            self.encrypt_setting_switch.blockSignals(True)
                            self.encrypt_setting_switch.setChecked(original_state)
                            self.encrypt_setting_switch.blockSignals(False)
                            self.show_info_bar('warning', '警告', f'{action_type}功能设置已取消', 3000, self)
                        return False

                    if hashed_set.get("two_factor_auth", False):
                        dialog = SimpleTwoFactorAuthDialog(self)
                        dialog.yesButton.setText("确认")
                        dialog.cancelButton.setText("取消")
                        if dialog.exec_() != QDialog.Accepted:
                            # 用户取消2FA验证，恢复到原始状态
                            if type == 'exit':
                                original_state = hashed_set.get("exit_verification_enabled", False)
                                self.exit_verification_switch.blockSignals(True)
                                self.exit_verification_switch.setChecked(original_state)
                                self.exit_verification_switch.blockSignals(False)
                                self.show_info_bar('warning', '警告', f'{action_type}功能设置已取消', 3000, self)
                            elif type == 'restart':
                                original_state = hashed_set.get("restart_verification_enabled", False)
                                self.restart_verification_switch.blockSignals(True)
                                self.restart_verification_switch.setChecked(original_state)
                                self.restart_verification_switch.blockSignals(False)
                                self.show_info_bar('warning', '警告', f'{action_type}功能设置已取消', 3000, self)
                            elif type == 'show_hide':
                                original_state = hashed_set.get("show_hide_verification_enabled", False)
                                self.show_hide_verification_switch.blockSignals(True)
                                self.show_hide_verification_switch.setChecked(original_state)
                                self.show_hide_verification_switch.blockSignals(False)
                                self.show_info_bar('warning', '警告', f'{action_type}功能设置已取消', 3000, self)
                            elif type == 'encrypt':
                                original_state = hashed_set.get("encrypt_setting_enabled", False)
                                self.encrypt_setting_switch.blockSignals(True)
                                self.encrypt_setting_switch.setChecked(original_state)
                                self.encrypt_setting_switch.blockSignals(False)
                                self.show_info_bar('warning', '警告', f'{action_type}功能设置已取消', 3000, self)
                            return False

                    # 验证成功，更新对应的开关状态
                    if type == 'exit':
                        hashed_set['exit_verification_enabled'] = True
                    elif type == 'restart':
                        hashed_set['restart_verification_enabled'] = True
                    elif type == 'show_hide':
                        hashed_set['show_hide_verification_enabled'] = True
                    elif type == 'encrypt':
                        hashed_set['encrypt_setting_enabled'] = True
                    
                    # 保存更新后的设置
                    with open_file(self.settings_file, 'w', encoding='utf-8') as f:
                        json.dump(settings, f, indent=4)
                    
                    self.show_info_bar('success', '功能设置成功', f'{action_type}功能设置成功', 3000, self)
                    return True

        except Exception as e:
            logger.error(f"验证失败: {e}")
            return False

    def show_password_dialog(self):
        if not path_manager.file_exists(self.settings_file):
            self.show_info_bar('error', '错误', '设置文件不存在', 3000, self)
            return

        try:
            with open_file(self.settings_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                hashed_set = settings.get("hashed_set", {})
                if hashed_set.get("verification_start") == True:
                    with open_file(self.settings_file, 'r', encoding='utf-8') as f:
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

    def show_change_password_dialog(self):
        """显示修改密码对话框"""
        if not path_manager.file_exists(self.settings_file):
            self.show_info_bar('error', '错误', '设置文件不存在', 3000, self)
            return

        try:
            with open_file(self.settings_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                hashed_set = settings.get("hashed_set", {})
                
                # 检查是否已设置密码
                if not hashed_set.get("hashed_password") or not hashed_set.get("password_salt"):
                    self.show_info_bar('warning', '警告', '请先设置密码', 3000, self)
                    return
                
                # 检查密码功能是否启用
                if hashed_set.get("verification_start") == True:
                    # 如果启用了2FA，需要先验证2FA
                    if hashed_set.get("two_factor_auth") == True:
                        dialog = SimpleTwoFactorAuthDialog(self)
                        dialog.yesButton.setText("确认")
                        dialog.cancelButton.setText("取消")
                        if dialog.exec_() != QDialog.Accepted:
                            self.show_info_bar('warning', '警告', '修改密码已取消', 3000, self)
                            return
                    
                    # 显示修改密码对话框
                    dialog = ChangePasswordDialog(self)
                    dialog.yesButton.setText("确认")
                    dialog.cancelButton.setText("取消")
                    if dialog.exec():
                        self.update_password(dialog, dialog.newPasswordLineEdit)
                    else:
                        self.show_info_bar('warning', '警告', '修改密码已取消', 3000, self)
                else:
                    self.show_info_bar('warning', '警告', '请先启用密码功能', 3000, self)
                    return
        except json.JSONDecodeError as e:
            self.show_info_bar('error', '错误', '设置文件损坏', 3000, self)
            return

    def update_password(self, dialog, new_password_input):
        """更新密码"""
        new_password = new_password_input.text()
        
        if not new_password:
            self.show_info_bar('error', '错误', '新密码不能为空', 3000, self)
            return
        
        # 生成新的随机盐值
        new_salt = secrets.token_hex(16)
        new_hashed_password = hashlib.md5((new_password + new_salt).encode()).hexdigest()
        
        # 更新设置文件中的密码和盐值
        try:
            with open_file(self.settings_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)
            
            if "hashed_set" not in settings:
                settings["hashed_set"] = {}
            
            settings["hashed_set"]["hashed_password"] = new_hashed_password
            settings["hashed_set"]["password_salt"] = new_salt
            
            with open_file(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=4)
            
            logger.info("密码修改成功")
            self.show_info_bar('success', '成功', "密码修改成功", 3000, self)
            dialog.accept()
            
        except Exception as e:
            logger.error(f"密码修改失败: {e}")
            self.show_info_bar('error', '错误', f"密码修改失败: {str(e)}", 3000, self)

    def show_change_username_dialog(self):
        """显示修改2FA用户名对话框"""
        if not path_manager.file_exists(self.settings_file):
            self.show_info_bar('error', '错误', '设置文件不存在', 3000, self)
            return

        try:
            with open_file(self.settings_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                hashed_set = settings.get("hashed_set", {})

            # 检查是否启用了密码功能
            if hashed_set.get("verification_start") != True:
                self.show_info_bar('warning', '提示', '请先启用密码功能', 3000, self)
                return

            # 检查是否启用了2FA
            if not hashed_set.get("two_factor_auth", False):
                self.show_info_bar('warning', '提示', '请先启用2FA功能', 3000, self)
                return

            # 验证当前密码
            dialog = PasswordDialog(self)
            dialog.yesButton.setText("确认")
            dialog.cancelButton.setText("取消")
            if dialog.exec_() != QDialog.Accepted:
                return

            # 验证2FA
            dialog = SimpleTwoFactorAuthDialog(self)
            dialog.yesButton.setText("确认")
            dialog.cancelButton.setText("取消")
            if dialog.exec_() != QDialog.Accepted:
                return

            # 显示修改用户名对话框
            dialog = ChangeUsernameDialog(self)
            dialog.yesButton.setText("确认")
            dialog.cancelButton.setText("取消")
            if dialog.exec():
                if dialog.validate():
                    new_username = dialog.usernameLineEdit.text().strip()
                    if self.update_username(new_username):
                        self.show_info_bar('success', '用户名修改成功', '2FA用户名已成功修改', 3000, self)
                    else:
                        self.show_info_bar('error', '用户名修改失败', '2FA用户名修改失败', 3000, self)

        except Exception as e:
            logger.error(f"修改用户名对话框显示失败: {e}")
            self.show_info_bar('error', '错误', f'修改用户名对话框显示失败: {str(e)}', 3000, self)

    def update_username(self, new_username):
        """更新2FA用户名"""
        if not path_manager.file_exists(self.settings_file):
            self.show_info_bar('error', '错误', '设置文件不存在', 3000, self)
            return False

        try:
            with open_file(self.settings_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                hashed_set = settings.get("hashed_set", {})

            # 生成新的用户名哈希（使用固定盐值）
            username_salt = 'SecRandomSalt'
            hashed_username = hashlib.md5((new_username + username_salt).encode('utf-8')).hexdigest()

            # 更新设置
            hashed_set['encrypted_username'] = hashed_username

            settings['hashed_set'] = hashed_set

            with open_file(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=4)

            return True

        except Exception as e:
            logger.error(f"用户名修改失败: {e}")
            return False

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
        if path_manager.file_exists(self.settings_file):
            try:
                with open_file(self.settings_file, 'r', encoding='utf-8') as f:
                    existing_settings = json.load(f)
            except json.JSONDecodeError:
                existing_settings = {}

        if "hashed_set" not in existing_settings:
            existing_settings["hashed_set"] = {}
        existing_settings["hashed_set"]["hashed_password"] = hashed_password
        existing_settings["hashed_set"]["password_salt"] = salt

        with open_file(self.settings_file, 'w', encoding='utf-8') as f:
            json.dump(existing_settings, f, indent=4)

        logger.info("密码设置成功")
        self.show_info_bar('success', '成功', "密码设置成功", 3000, self)
        dialog.accept()

    def start_password_switch_checked(self):
        if not path_manager.file_exists(self.settings_file):
            self.show_info_bar('error', '错误', '设置文件不存在', 3000, self)
            self.start_password_switch.setChecked(False)
            return

        try:
            with open_file(self.settings_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                hashed_set = settings.get("hashed_set", {})
                if hashed_set.get("verification_start") == True:
                    with open_file(self.settings_file, 'r', encoding='utf-8') as f:
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
                                        # 用户取消2FA验证，恢复开关状态
                                        original_state = hashed_set.get("start_password_enabled", False)
                                        self.start_password_switch.blockSignals(True)
                                        self.start_password_switch.setChecked(original_state)
                                        self.start_password_switch.blockSignals(False)
                                        self.show_info_bar('warning', '警告', '启动设置需密码已取消', 3000, self)
                                        return
                                else:
                                    self.save_settings()
                                    return
                            else:
                                # 用户取消密码验证，恢复开关状态
                                original_state = hashed_set.get("start_password_enabled", False)
                                self.start_password_switch.blockSignals(True)
                                self.start_password_switch.setChecked(original_state)
                                self.start_password_switch.blockSignals(False)
                                self.show_info_bar('warning', '警告', '启动设置需密码已取消', 3000, self)
                                return
        except json.JSONDecodeError as e:
            self.show_info_bar('error', '错误', '设置文件损坏', 3000, self)
            self.start_password_switch.setChecked(False)
            return

    def on_2fa_changed(self):
        if not path_manager.file_exists(self.settings_file):
            self.show_info_bar('error', '错误', '设置文件不存在', 3000, self)
            self.two_factor_switch.blockSignals(True)
            self.two_factor_switch.setChecked(False)
            self.two_factor_switch.blockSignals(False)
            return

        try:
            with open_file(self.settings_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                hashed_set = settings.get("hashed_set", {})
                if hashed_set.get("verification_start") == True:
                    if not hashed_set.get("hashed_password") or not hashed_set.get("password_salt"):
                        self.show_info_bar('warning', '警告', '请先设置密码', 3000, self)
                        self.two_factor_switch.blockSignals(True)
                        self.two_factor_switch.setChecked(False)
                        self.two_factor_switch.blockSignals(False)
                        self.save_settings()
                        return
                    elif hashed_set.get("hashed_password") and hashed_set.get("password_salt"):
                        dialog = PasswordDialog(self)
                        dialog.yesButton.setText("确认")
                        dialog.cancelButton.setText("取消")
                        if dialog.exec_() == QDialog.Accepted:
                            if hashed_set.get("two_factor_auth") == True:
                                # 关闭2FA
                                dialog = SimpleTwoFactorAuthDialog(self)
                                dialog.yesButton.setText("确认")
                                dialog.cancelButton.setText("取消")
                                if dialog.exec_() == QDialog.Accepted:
                                    # 验证成功，删除2FA相关设置
                                    existing_settings = {}
                                    try:
                                        with open_file(self.settings_file, 'r', encoding='utf-8') as f:
                                            existing_settings = json.load(f)
                                    except json.JSONDecodeError:
                                        existing_settings = {}
                                    
                                    if "hashed_set" in existing_settings:
                                        existing_settings["hashed_set"].pop("encrypted_username", None)
                                        existing_settings["hashed_set"].pop("2fa_secret", None)
                                    
                                    with open_file(self.settings_file, 'w', encoding='utf-8') as f:
                                        json.dump(existing_settings, f, indent=4)
                                    
                                    self.save_settings()
                                    self.show_info_bar('success', '成功', '2FA已关闭', 3000, self)
                                else:
                                    # 用户取消验证，恢复开关状态
                                    original_state = hashed_set.get("two_factor_auth", False)
                                    self.two_factor_switch.blockSignals(True)
                                    self.two_factor_switch.setChecked(original_state)
                                    self.two_factor_switch.blockSignals(False)
                                    self.show_info_bar('warning', '警告', '2FA关闭已取消', 3000, self)
                                    return
                            else:
                                # 开启2FA
                                existing_settings = {}
                                try:
                                    with open_file(self.settings_file, 'r', encoding='utf-8') as f:
                                        existing_settings = json.load(f)
                                except json.JSONDecodeError:
                                    existing_settings = {}
                                
                                if "hashed_set" not in existing_settings or "2fa_secret" not in existing_settings["hashed_set"]:
                                    self.setup_2fa()
                                    # setup_2fa方法中已经处理了保存和状态设置
                                else:
                                    self.save_settings()
                                return
                        else:
                            # 用户取消密码验证，恢复开关状态
                            original_state = hashed_set.get("two_factor_auth", False)
                            self.two_factor_switch.blockSignals(True)
                            self.two_factor_switch.setChecked(original_state)
                            self.two_factor_switch.blockSignals(False)
                            self.show_info_bar('warning', '警告', '2FA设置已取消', 3000, self)
                            return
        except json.JSONDecodeError as e:
            self.show_info_bar('error', '错误', '设置文件损坏', 3000, self)
            self.two_factor_switch.blockSignals(True)
            self.two_factor_switch.setChecked(False)
            self.two_factor_switch.blockSignals(False)
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
                    self.show_info_bar('warning', '警告', '用户名不能为空', 3000, self)
                    self.two_factor_switch.blockSignals(True)
                    self.two_factor_switch.setChecked(False)
                    self.two_factor_switch.blockSignals(False)
                    return
            else:
                # 用户取消用户名输入，重置开关状态
                self.show_info_bar('warning', '警告', '2FA设置已取消', 3000, self)
                self.two_factor_switch.blockSignals(True)
                self.two_factor_switch.setChecked(False)
                self.two_factor_switch.blockSignals(False)
                return

            salt = 'SecRandomSalt'
            hashed_username = hashlib.md5((username + salt).encode()).hexdigest()

            os.makedirs(self.secret_dir, exist_ok=True)

            existing_settings = {}
            try:
                with open_file(self.settings_file, 'r', encoding='utf-8') as f:
                    existing_settings = json.load(f)
            except json.JSONDecodeError:
                existing_settings = {}

            if "hashed_set" not in existing_settings:
                existing_settings["hashed_set"] = {}
            existing_settings["hashed_set"]["encrypted_username"] = hashed_username

            with open_file(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(existing_settings, f, indent=4)

            # 生成密钥但暂不保存，等待用户验证成功后再保存
            self.secret = pyotp.random_base32()
            pixmap = generate_qr_code(self.secret, username)
            
            if pixmap:
                # 创建自定义2FA对话框
                dialog = TwoFactorAuthDialog(self, pixmap, self.secret)
                dialog.yesButton.setText("确认")
                dialog.cancelButton.setText("取消")
                if dialog.exec():
                    # 用户验证成功，才保存密钥到设置文件
                    try:
                        with open_file(self.settings_file, 'r', encoding='utf-8') as f:
                            existing_settings = json.load(f)
                        
                        if "hashed_set" not in existing_settings:
                            existing_settings["hashed_set"] = {}
                        existing_settings["hashed_set"]["2fa_secret"] = self.secret

                        with open_file(self.settings_file, 'w', encoding='utf-8') as f:
                            json.dump(existing_settings, f, indent=4)
                            
                        self.show_info_bar('success', '成功', '2FA设置成功', 3000, self)
                    except Exception as e:
                        logger.error(f"保存2FA密钥失败: {e}")
                        self.show_info_bar('error', '错误', '2FA密钥保存失败', 3000, self)
                        self.two_factor_switch.setChecked(False)
                else:
                    # 用户取消验证，不保存密钥，重置开关状态
                    self.show_info_bar('warning', '警告', '2FA设置已取消', 3000, self)
                    self.two_factor_switch.blockSignals(True)
                    self.two_factor_switch.setChecked(False)
                    self.two_factor_switch.blockSignals(False)
            else:
                self.show_info_bar('error', '错误', "2FA设置失败", 3000, self)
                self.two_factor_switch.blockSignals(True)
                self.two_factor_switch.setChecked(False)
                self.two_factor_switch.blockSignals(False)
        except Exception as e:
            self.show_info_bar('error', '错误', f"2FA设置失败: {str(e)}", 3000, self)
            self.two_factor_switch.blockSignals(True)
            self.two_factor_switch.setChecked(False)
            self.two_factor_switch.blockSignals(False)
            return

    def export_key_file(self):
        if not path_manager.file_exists(self.settings_file):
            self.show_info_bar('error', '错误', '设置文件不存在', 3000, self)
            return

        try:
            with open_file(self.settings_file, 'r', encoding='utf-8') as f:
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
            with open_file(path, 'w') as f:
                f.write(hashed_password)
        except Exception as e:
            self.show_info_bar('error', '错误', f"密钥导出失败: {str(e)}", 3000, self)

    def load_settings(self):
        try:
            if path_manager.file_exists(self.settings_file):
                with open_file(self.settings_file, 'r', encoding='utf-8') as f:
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
                    self.exit_verification_switch.setChecked(
                        hashed_set_settings.get("exit_verification_enabled", self.default_settings["exit_verification_enabled"])
                    )
                    self.restart_verification_switch.setChecked(
                        hashed_set_settings.get("restart_verification_enabled", self.default_settings["restart_verification_enabled"])
                    )
                    self.show_hide_verification_switch.setChecked(
                        hashed_set_settings.get("show_hide_verification_enabled", self.default_settings["show_hide_verification_enabled"])
                    )
                    self.usb_auth_switch.setChecked(
                        settings.get("usb_auth_enabled", self.default_settings["usb_auth_enabled"])
                    )
                    logger.info("安全设置加载完成")
                    
                    # 如果U盘认证已启用，启动监控线程
                    if settings.get("usb_auth_enabled", False):
                        self.start_usb_monitoring()
            else:
                logger.warning(f"设置文件不存在: {self.settings_file}")
                self.start_password_switch.setChecked(self.default_settings["start_password_enabled"])
                self.encrypt_setting_switch.setChecked(self.default_settings["encrypt_setting_enabled"])
                self.two_factor_switch.setChecked(self.default_settings["two_factor_auth"])
                self.exit_verification_switch.setChecked(self.default_settings["exit_verification_enabled"])
                self.restart_verification_switch.setChecked(self.default_settings["restart_verification_enabled"])
                self.show_hide_verification_switch.setChecked(self.default_settings["show_hide_verification_enabled"])
                self.usb_auth_switch.setChecked(self.default_settings["usb_auth_enabled"])
        except Exception as e:
            logger.error(f"加载设置时出错: {e}")
            self.start_password_switch.setChecked(self.default_settings["start_password_enabled"])
            self.encrypt_setting_switch.setChecked(self.default_settings["encrypt_setting_enabled"])
            self.two_factor_switch.setChecked(self.default_settings["two_factor_auth"])
            self.exit_verification_switch.setChecked(self.default_settings["exit_verification_enabled"])
            self.restart_verification_switch.setChecked(self.default_settings["restart_verification_enabled"])
            self.show_hide_verification_switch.setChecked(self.default_settings["show_hide_verification_enabled"])
            self.usb_auth_switch.setChecked(self.default_settings["usb_auth_enabled"])

    def save_settings(self):
        # 先读取现有设置
        _existing_settings = {}
        try:
            if path_manager.file_exists(self.settings_file):
                with open_file(self.settings_file, 'r', encoding='utf-8') as f:
                    _existing_settings = json.load(f)
        except json.JSONDecodeError:
            _existing_settings = {}

        # 更新hashed_set部分的所有设置
        if "hashed_set" not in _existing_settings:
            _existing_settings["hashed_set"] = {}

        # 移除自动重置开关状态的逻辑，让各个方法自行管理开关状态
        # 这样可以避免与已经正确实现的blockSignals机制产生冲突

        _existing_settings["hashed_set"].update({
            "start_password_enabled": self.start_password_switch.isChecked(),
            "encrypt_setting_enabled": self.encrypt_setting_switch.isChecked(),
            "two_factor_auth": self.two_factor_switch.isChecked(),
            "exit_verification_enabled": self.exit_verification_switch.isChecked(),
            "restart_verification_enabled": self.restart_verification_switch.isChecked(),
            "show_hide_verification_enabled": self.show_hide_verification_switch.isChecked()
        })
        
        # 更新U盘认证设置（存储在根级别，不在hashed_set中）
        _existing_settings["usb_auth_enabled"] = self.usb_auth_switch.isChecked()

        os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)

        with open_file(self.settings_file, 'w', encoding='utf-8') as f:
            json.dump(_existing_settings, f, indent=4)