# ==================================================
# 导入库
# ==================================================

from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
from PySide6.QtNetwork import *
from qfluentwidgets import *

from app.tools.variable import *
from app.tools.path_utils import *
from app.tools.personalised import *
from app.tools.settings_default import *
from app.tools.settings_access import *
from app.Language.obtain_language import *
from app.tools.config import *
from app.page_building.security_window import (
    create_set_password_window,
    create_set_totp_window,
    create_bind_usb_window,
    create_unbind_usb_window,
)
from app.common.safety.usb import unbind, is_bound_connected
from app.common.safety.password import is_configured as password_is_configured
from app.common.safety.totp import is_configured as totp_is_configured


# ==================================================
# 安全设置
# ==================================================
class safety_settings(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # 创建垂直布局
        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout.setSpacing(10)

        # 添加验证方式设置组件
        self.verification_method_widget = basic_safety_verification_method(self)
        self.vBoxLayout.addWidget(self.verification_method_widget)

        # 添加验证流程设置组件
        self.verification_process_widget = basic_safety_verification_process(self)
        self.vBoxLayout.addWidget(self.verification_process_widget)

        # 添加安全操作设置组件
        self.security_operations_widget = basic_safety_security_operations(self)
        self.vBoxLayout.addWidget(self.security_operations_widget)


class basic_safety_verification_method(GroupHeaderCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(
            get_content_name_async("basic_safety_settings", "verification_method")
        )
        self.setBorderRadius(8)

        # 是否开启安全功能开关
        self.safety_switch = SwitchButton()
        self.safety_switch.setOffText(
            get_content_switchbutton_name_async(
                "basic_safety_settings", "safety_switch", "disable"
            )
        )
        self.safety_switch.setOnText(
            get_content_switchbutton_name_async(
                "basic_safety_settings", "safety_switch", "enable"
            )
        )
        self.safety_switch.setChecked(
            readme_settings_async("basic_safety_settings", "safety_switch")
        )
        if self.safety_switch.isChecked() and not password_is_configured():
            self.safety_switch.setChecked(False)
            update_settings("basic_safety_settings", "safety_switch", False)
        self.safety_switch.checkedChanged.connect(self.__on_safety_switch_changed)

        # 设置/修改密码按钮
        self.set_password_button = PushButton(
            get_content_name_async("basic_safety_settings", "set_password")
        )
        self.set_password_button.clicked.connect(lambda: self.set_password())

        # 是否启用TOTP开关
        self.totp_switch = SwitchButton()
        self.totp_switch.setOffText(
            get_content_switchbutton_name_async(
                "basic_safety_settings", "totp_switch", "disable"
            )
        )
        self.totp_switch.setOnText(
            get_content_switchbutton_name_async(
                "basic_safety_settings", "totp_switch", "enable"
            )
        )
        self.totp_switch.setChecked(
            readme_settings_async("basic_safety_settings", "totp_switch")
        )
        if self.totp_switch.isChecked() and not totp_is_configured():
            self.totp_switch.setChecked(False)
            update_settings("basic_safety_settings", "totp_switch", False)
        self.totp_switch.checkedChanged.connect(self.__on_totp_switch_changed)

        # 设置TOTP按钮
        self.set_totp_button = PushButton(
            get_content_name_async("basic_safety_settings", "set_totp")
        )
        self.set_totp_button.clicked.connect(lambda: self.set_totp())

        # 是否启用U盘验证开关
        self.usb_switch = SwitchButton()
        self.usb_switch.setOffText(
            get_content_switchbutton_name_async(
                "basic_safety_settings", "usb_switch", "disable"
            )
        )
        self.usb_switch.setOnText(
            get_content_switchbutton_name_async(
                "basic_safety_settings", "usb_switch", "enable"
            )
        )
        self.usb_switch.setChecked(
            readme_settings_async("basic_safety_settings", "usb_switch")
        )
        if self.usb_switch.isChecked() and not is_bound_connected():
            self.usb_switch.setChecked(False)
            update_settings("basic_safety_settings", "usb_switch", False)
        self.usb_switch.checkedChanged.connect(self.__on_usb_switch_changed)

        # 绑定U盘按钮
        self.bind_usb_button = PushButton(
            get_content_name_async("basic_safety_settings", "bind_usb")
        )
        self.bind_usb_button.clicked.connect(lambda: self.bind_usb())

        # 解绑U盘按钮
        self.unbind_usb_button = PushButton(
            get_content_name_async("basic_safety_settings", "unbind_usb")
        )
        self.unbind_usb_button.clicked.connect(lambda: self.unbind_usb())

        # 添加设置项到分组
        self.addGroup(
            get_theme_icon("ic_fluent_shield_keyhole_20_filled"),
            get_content_name_async("basic_safety_settings", "safety_switch"),
            get_content_description_async("basic_safety_settings", "safety_switch"),
            self.safety_switch,
        )
        self.addGroup(
            get_theme_icon("ic_fluent_laptop_shield_20_filled"),
            get_content_name_async("basic_safety_settings", "set_password"),
            get_content_description_async("basic_safety_settings", "set_password"),
            self.set_password_button,
        )
        self.addGroup(
            get_theme_icon("ic_fluent_puzzle_piece_shield_20_filled"),
            get_content_name_async("basic_safety_settings", "totp_switch"),
            get_content_description_async("basic_safety_settings", "totp_switch"),
            self.totp_switch,
        )
        self.addGroup(
            get_theme_icon("ic_fluent_laptop_shield_20_filled"),
            get_content_name_async("basic_safety_settings", "set_totp"),
            get_content_description_async("basic_safety_settings", "set_totp"),
            self.set_totp_button,
        )
        self.addGroup(
            get_theme_icon("ic_fluent_puzzle_piece_shield_20_filled"),
            get_content_name_async("basic_safety_settings", "usb_switch"),
            get_content_description_async("basic_safety_settings", "usb_switch"),
            self.usb_switch,
        )
        self.addGroup(
            get_theme_icon("ic_fluent_usb_stick_20_filled"),
            get_content_name_async("basic_safety_settings", "bind_usb"),
            get_content_description_async("basic_safety_settings", "bind_usb"),
            self.bind_usb_button,
        )
        self.addGroup(
            get_theme_icon("ic_fluent_usb_plug_20_filled"),
            get_content_name_async("basic_safety_settings", "unbind_usb"),
            get_content_description_async("basic_safety_settings", "unbind_usb"),
            self.unbind_usb_button,
        )

        if not password_is_configured():
            self.totp_switch.setEnabled(False)
            self.set_totp_button.setEnabled(False)
            self.usb_switch.setEnabled(False)
            self.bind_usb_button.setEnabled(False)
            self.unbind_usb_button.setEnabled(False)

        get_settings_signals().settingChanged.connect(self.__on_setting_changed)

    def set_password(self):
        create_set_password_window()

    def set_totp(self):
        if not password_is_configured():
            config = NotificationConfig(title=get_content_name_async("basic_safety_settings","error_title"), content=get_content_name_async("basic_safety_settings","error_set_password_first"), duration=3000)
            show_notification(NotificationType.ERROR, config, parent=self)
            return
        create_set_totp_window()

    def bind_usb(self):
        if not password_is_configured():
            config = NotificationConfig(title=get_content_name_async("basic_safety_settings","error_title"), content=get_content_name_async("basic_safety_settings","error_set_password_first"), duration=3000)
            show_notification(NotificationType.ERROR, config, parent=self)
            return
        create_bind_usb_window()

    def unbind_usb(self):
        if not password_is_configured():
            config = NotificationConfig(title=get_content_name_async("basic_safety_settings","error_title"), content=get_content_name_async("basic_safety_settings","error_set_password_first"), duration=3000)
            show_notification(NotificationType.ERROR, config, parent=self)
            return
        create_unbind_usb_window()

    def __on_safety_switch_changed(self):
        if self.safety_switch.isChecked() and not password_is_configured():
            self.safety_switch.setChecked(False)
            update_settings("basic_safety_settings", "safety_switch", False)
            config = NotificationConfig(title=get_content_name_async("basic_safety_settings","error_title"), content=get_content_name_async("basic_safety_settings","error_set_password_first"), duration=3000)
            show_notification(NotificationType.ERROR, config, parent=self)
            return
        update_settings(
            "basic_safety_settings",
            "safety_switch",
            self.safety_switch.isChecked(),
        )

    def __on_totp_switch_changed(self):
        if self.totp_switch.isChecked() and not totp_is_configured():
            self.totp_switch.setChecked(False)
            update_settings("basic_safety_settings", "totp_switch", False)
            config = NotificationConfig(title=get_content_name_async("basic_safety_settings","error_title"), content=get_content_name_async("basic_safety_settings","error_set_totp_first"), duration=3000)
            show_notification(NotificationType.ERROR, config, parent=self)
            return
        update_settings(
            "basic_safety_settings",
            "totp_switch",
            self.totp_switch.isChecked(),
        )

    def __on_usb_switch_changed(self):
        if self.usb_switch.isChecked() and not is_bound_connected():
            self.usb_switch.setChecked(False)
            update_settings("basic_safety_settings", "usb_switch", False)
            config = NotificationConfig(title=get_content_name_async("basic_safety_settings","error_title"), content=get_content_name_async("basic_safety_settings","error_bind_usb_first"), duration=3000)
            show_notification(NotificationType.ERROR, config, parent=self)
            return
        update_settings(
            "basic_safety_settings",
            "usb_switch",
            self.usb_switch.isChecked(),
        )

    def __on_setting_changed(self, first_level_key, second_level_key, value):
        if first_level_key != "basic_safety_settings":
            return
        if second_level_key == "safety_switch":
            self.safety_switch.setChecked(bool(value))
        elif second_level_key == "totp_switch":
            self.totp_switch.setChecked(bool(value))
        elif second_level_key == "usb_switch":
            self.usb_switch.setChecked(bool(value))
        enabled = password_is_configured()
        self.totp_switch.setEnabled(enabled)
        self.set_totp_button.setEnabled(enabled)
        self.usb_switch.setEnabled(enabled)
        self.bind_usb_button.setEnabled(enabled)
        self.unbind_usb_button.setEnabled(enabled)


class basic_safety_verification_process(GroupHeaderCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(
            get_content_name_async("basic_safety_settings", "verification_process")
        )
        self.setBorderRadius(8)

        # 选择验证流程下拉框
        self.verification_process_combo = ComboBox()
        self.verification_process_combo.addItems(
            get_content_combo_name_async(
                "basic_safety_settings", "verification_process"
            )
        )
        self.verification_process_combo.setCurrentIndex(
            readme_settings_async("basic_safety_settings", "verification_process")
        )
        self.verification_process_combo.currentIndexChanged.connect(
            lambda: update_settings(
                "basic_safety_settings",
                "verification_process",
                self.verification_process_combo.currentIndex(),
            )
        )

        # 添加设置项到分组
        self.addGroup(
            get_theme_icon("ic_fluent_calendar_shield_20_filled"),
            get_content_name_async("basic_safety_settings", "verification_process"),
            get_content_description_async(
                "basic_safety_settings", "verification_process"
            ),
            self.verification_process_combo,
        )


class basic_safety_security_operations(GroupHeaderCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(
            get_content_name_async("basic_safety_settings", "security_operations")
        )
        self.setBorderRadius(8)

        # 显隐浮窗需验证密码开关
        self.show_hide_floating_window_switch = SwitchButton()
        self.show_hide_floating_window_switch.setOffText(
            get_content_switchbutton_name_async(
                "basic_safety_settings", "show_hide_floating_window_switch", "disable"
            )
        )
        self.show_hide_floating_window_switch.setOnText(
            get_content_switchbutton_name_async(
                "basic_safety_settings", "show_hide_floating_window_switch", "enable"
            )
        )
        self.show_hide_floating_window_switch.setChecked(
            readme_settings_async(
                "basic_safety_settings", "show_hide_floating_window_switch"
            )
        )
        self.show_hide_floating_window_switch.checkedChanged.connect(
            lambda: update_settings(
                "basic_safety_settings",
                "show_hide_floating_window_switch",
                self.show_hide_floating_window_switch.isChecked(),
            )
        )

        # 重启软件需验证密码开关
        self.restart_switch = SwitchButton()
        self.restart_switch.setOffText(
            get_content_switchbutton_name_async(
                "basic_safety_settings", "restart_switch", "disable"
            )
        )
        self.restart_switch.setOnText(
            get_content_switchbutton_name_async(
                "basic_safety_settings", "restart_switch", "enable"
            )
        )
        self.restart_switch.setChecked(
            readme_settings_async("basic_safety_settings", "restart_switch")
        )
        self.restart_switch.checkedChanged.connect(
            lambda: update_settings(
                "basic_safety_settings",
                "restart_switch",
                self.restart_switch.isChecked(),
            )
        )

        # 退出软件需验证密码开关
        self.exit_switch = SwitchButton()
        self.exit_switch.setOffText(
            get_content_switchbutton_name_async(
                "basic_safety_settings", "exit_switch", "disable"
            )
        )
        self.exit_switch.setOnText(
            get_content_switchbutton_name_async(
                "basic_safety_settings", "exit_switch", "enable"
            )
        )
        self.exit_switch.setChecked(
            readme_settings_async("basic_safety_settings", "exit_switch")
        )
        self.exit_switch.checkedChanged.connect(
            lambda: update_settings(
                "basic_safety_settings", "exit_switch", self.exit_switch.isChecked()
            )
        )

        get_settings_signals().settingChanged.connect(self.__on_ops_setting_changed)

        # 添加设置项到分组
        self.addGroup(
            get_theme_icon("ic_fluent_window_ad_20_filled"),
            get_content_name_async(
                "basic_safety_settings", "show_hide_floating_window_switch"
            ),
            get_content_description_async(
                "basic_safety_settings", "show_hide_floating_window_switch"
            ),
            self.show_hide_floating_window_switch,
        )
        self.addGroup(
            get_theme_icon("ic_fluent_arrow_reset_20_filled"),
            get_content_name_async("basic_safety_settings", "restart_switch"),
            get_content_description_async("basic_safety_settings", "restart_switch"),
            self.restart_switch,
        )
        self.addGroup(
            get_theme_icon("ic_fluent_arrow_exit_20_filled"),
            get_content_name_async("basic_safety_settings", "exit_switch"),
            get_content_description_async("basic_safety_settings", "exit_switch"),
            self.exit_switch,
        )

    def __on_ops_setting_changed(self, first_level_key, second_level_key, value):
        if first_level_key != "basic_safety_settings":
            return
        if second_level_key == "show_hide_floating_window_switch":
            self.show_hide_floating_window_switch.setChecked(bool(value))
        elif second_level_key == "restart_switch":
            self.restart_switch.setChecked(bool(value))
        elif second_level_key == "exit_switch":
            self.exit_switch.setChecked(bool(value))
