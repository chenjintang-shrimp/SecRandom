from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
from qfluentwidgets import *

from app.tools.config import *
from app.Language.obtain_language import *
from app.tools.personalised import *
from app.common.safety.password import verify_password, is_configured as password_is_configured
from app.common.safety.totp import is_configured as totp_is_configured, verify as verify_totp
from app.common.safety.usb import is_bound_connected
from app.tools.settings_access import readme_settings_async


class VerifyPasswordWindow(QWidget):
    verified = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.__connect_signals()

    def init_ui(self):
        self.setWindowTitle(get_content_name_async("basic_safety_settings", "safety_switch"))
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(15)

        self.title_label = TitleLabel(get_content_name_async("basic_safety_settings", "safety_switch"))
        self.main_layout.addWidget(self.title_label)

        card = CardWidget()
        layout = QVBoxLayout(card)

        self.password_label = BodyLabel(get_content_name_async("basic_safety_settings", "current_password"))
        self.password_edit = PasswordLineEdit()
        self.totp_label = BodyLabel(get_content_name_async("basic_safety_settings", "verify_totp_code"))
        self.totp_edit = LineEdit()
        self.totp_edit.setPlaceholderText(get_content_name_async("basic_safety_settings", "totp_input_placeholder"))
        self.usb_status_label = BodyLabel("")
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_edit)
        layout.addWidget(self.totp_label)
        layout.addWidget(self.totp_edit)
        layout.addWidget(self.usb_status_label)

        self.main_layout.addWidget(card)

        btns = QHBoxLayout()
        btns.addStretch(1)
        self.ok_button = PrimaryPushButton(get_content_name_async("basic_safety_settings", "save_button"))
        self.cancel_button = PushButton(get_content_name_async("basic_safety_settings", "cancel_button"))
        btns.addWidget(self.ok_button)
        btns.addWidget(self.cancel_button)
        self.main_layout.addLayout(btns)
        self.main_layout.addStretch(1)

        self._configure_methods()

    def __connect_signals(self):
        self.ok_button.clicked.connect(self.__on_ok)
        self.cancel_button.clicked.connect(self.__cancel)

    def _configure_methods(self):
        mode = int(readme_settings_async("basic_safety_settings", "verification_process") or 0)
        totp_enabled = bool(readme_settings_async("basic_safety_settings", "totp_switch")) and totp_is_configured()
        usb_enabled = bool(readme_settings_async("basic_safety_settings", "usb_switch")) and is_bound_connected()
        pwd_enabled = password_is_configured()

        self._required = []
        if mode == 0:
            available = []
            if pwd_enabled:
                available.append("password")
            if totp_enabled:
                available.append("totp")
            if usb_enabled:
                available.append("usb")
            if not available:
                available = ["password"]
            self._required = available
            self._any_one = True
        elif mode == 1:
            self._required = ["password"]
            self._any_one = False
        elif mode == 2:
            self._required = ["totp"] if totp_enabled else ["password"]
            self._any_one = False
        elif mode == 3:
            self._required = ["usb"] if usb_enabled else ["password"]
            self._any_one = False
        elif mode == 4:
            r = ["password", "totp" if totp_enabled else "password"]
            self._required = list(dict.fromkeys(r))
            self._any_one = False
        elif mode == 5:
            r = ["password", "usb" if usb_enabled else "password"]
            self._required = list(dict.fromkeys(r))
            self._any_one = False
        elif mode == 6:
            r = ["totp" if totp_enabled else "password", "usb" if usb_enabled else "password"]
            self._required = list(dict.fromkeys(r))
            self._any_one = False
        else:
            r = ["password", "totp" if totp_enabled else "password", "usb" if usb_enabled else "password"]
            self._required = list(dict.fromkeys(r))
            self._any_one = False

        self.password_label.setVisible("password" in self._required)
        self.password_edit.setVisible("password" in self._required)
        self.totp_label.setVisible("totp" in self._required)
        self.totp_edit.setVisible("totp" in self._required)
        if "usb" in self._required:
            self.usb_status_label.setVisible(True)
            self.usb_status_label.setText(
                get_content_name_async("basic_safety_settings", "usb_status_connected")
                if is_bound_connected()
                else get_content_name_async("basic_safety_settings", "usb_status_disconnected")
            )
        else:
            self.usb_status_label.setVisible(False)

    def __on_ok(self):
        results = {}
        if "password" in self._required:
            plain = self.password_edit.text() or ""
            results["password"] = bool(plain and verify_password(plain))
        if "totp" in self._required:
            code = self.totp_edit.text() or ""
            results["totp"] = bool(code and verify_totp(code))
        if "usb" in self._required:
            results["usb"] = bool(is_bound_connected())

        passed = False
        if self._any_one:
            passed = any(results.get(k, False) for k in self._required)
        else:
            passed = all(results.get(k, False) for k in self._required)

        if not passed:
            # 显示综合错误信息
            config = NotificationConfig(
                title=get_content_name_async("basic_safety_settings","error_title"),
                content=get_content_name_async("basic_safety_settings","error_set_password_first"),
                duration=3000,
            )
            show_notification(NotificationType.ERROR, config, parent=self)
            return
        self.verified.emit()
        self.__cancel()

    def __cancel(self):
        parent = self.parent()
        while parent:
            if hasattr(parent, "windowClosed") and hasattr(parent, "close"):
                parent.close()
                break
            parent = parent.parent()
