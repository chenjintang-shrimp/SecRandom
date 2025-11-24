from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
from qfluentwidgets import *

from app.tools.config import *
from app.Language.obtain_language import *
from app.tools.personalised import *
from app.common.safety.usb import list_removable_drives, get_volume_serial, bind


class BindUsbWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.saved = False
        self.init_ui()
        self.__connect_signals()

    def init_ui(self):
        self.setWindowTitle(get_content_name_async("basic_safety_settings", "bind_usb"))
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(15)

        self.title_label = TitleLabel(get_content_name_async("basic_safety_settings", "bind_usb"))
        self.main_layout.addWidget(self.title_label)

        self.description_label = BodyLabel(get_content_description_async("basic_safety_settings", "bind_usb"))
        self.description_label.setWordWrap(True)
        self.main_layout.addWidget(self.description_label)

        card = CardWidget()
        layout = QVBoxLayout(card)

        self.drive_combo = ComboBox()
        self.refresh_button = PushButton(get_content_name_async("basic_safety_settings","usb_refresh"))
        self.bind_button = PrimaryPushButton(get_content_name_async("basic_safety_settings","usb_bind"))

        layout.addWidget(self.drive_combo)
        layout.addWidget(self.refresh_button)
        layout.addWidget(self.bind_button)

        self.main_layout.addWidget(card)

        btns = QHBoxLayout()
        btns.addStretch(1)
        self.close_button = PushButton(get_content_name_async("basic_safety_settings", "cancel_button"))
        btns.addWidget(self.close_button)
        self.main_layout.addLayout(btns)
        self.main_layout.addStretch(1)

        self.__refresh()

    def __connect_signals(self):
        self.refresh_button.clicked.connect(self.__refresh)
        self.bind_button.clicked.connect(self.__bind)
        self.close_button.clicked.connect(self.__cancel)

    def __refresh(self):
        self.drive_combo.clear()
        try:
            letters = list_removable_drives()
            for lt in letters:
                self.drive_combo.addItem(f"{lt}:")
            if not letters:
                self.drive_combo.setCurrentIndex(-1)
                self.drive_combo.setPlaceholderText(
                    get_content_name_async("basic_safety_settings", "usb_no_removable")
                )
        except Exception as e:
            config = NotificationConfig(title=get_content_name_async("basic_safety_settings","title"), content=str(e), duration=3000)
            show_notification(NotificationType.ERROR, config, parent=self)

    def __bind(self):
        idx = self.drive_combo.currentIndex()
        if idx < 0:
            config = NotificationConfig(title=get_content_name_async("basic_safety_settings","title"), content=get_content_name_async("basic_safety_settings","usb_no_removable"), duration=3000)
            show_notification(NotificationType.ERROR, config, parent=self)
            return
        text = self.drive_combo.currentText()
        letter = text[:1]
        try:
            serial = get_volume_serial(letter)
            bind(serial)
            config = NotificationConfig(title=get_content_name_async("basic_safety_settings","title"), content=f"{get_content_name_async('basic_safety_settings','usb_bind_success')}: {text}", duration=3000)
            show_notification(NotificationType.SUCCESS, config, parent=self)
        except Exception as e:
            config = NotificationConfig(title=get_content_name_async("basic_safety_settings","title"), content=str(e), duration=3000)
            show_notification(NotificationType.ERROR, config, parent=self)


    def __cancel(self):
        parent = self.parent()
        while parent:
            if hasattr(parent, "windowClosed") and hasattr(parent, "close"):
                parent.close()
                break
            parent = parent.parent()

    def closeEvent(self, event):
        event.accept()
