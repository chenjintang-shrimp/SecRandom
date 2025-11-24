from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
from qfluentwidgets import *

from app.tools.config import *
from app.Language.obtain_language import *
from app.tools.personalised import *
from app.common.safety.usb import get_bound_serials, is_serial_connected, unbind


class UnbindUsbWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.__connect_signals()

    def init_ui(self):
        self.setWindowTitle(get_content_name_async("basic_safety_settings", "unbind_usb"))
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(15)

        self.title_label = TitleLabel(get_content_name_async("basic_safety_settings", "unbind_usb"))
        self.main_layout.addWidget(self.title_label)

        self.description_label = BodyLabel(get_content_description_async("basic_safety_settings", "unbind_usb"))
        self.description_label.setWordWrap(True)
        self.main_layout.addWidget(self.description_label)

        card = CardWidget()
        layout = QVBoxLayout(card)

        list_title = SubtitleLabel(get_content_name_async("basic_safety_settings", "usb_bound_devices"))
        layout.addWidget(list_title)

        self.bound_list = ListWidget()
        layout.addWidget(self.bound_list)

        btns = QHBoxLayout()
        self.refresh_button = PushButton(get_content_name_async("basic_safety_settings", "usb_refresh"))
        self.unbind_selected_button = PrimaryPushButton(get_content_name_async("basic_safety_settings", "usb_unbind_selected"))
        self.unbind_all_button = PushButton(get_content_name_async("basic_safety_settings", "usb_unbind_all"))
        btns.addWidget(self.refresh_button)
        btns.addWidget(self.unbind_selected_button)
        btns.addWidget(self.unbind_all_button)
        layout.addLayout(btns)

        self.main_layout.addWidget(card)

        footer = QHBoxLayout()
        footer.addStretch(1)
        self.close_button = PushButton(get_content_name_async("basic_safety_settings", "cancel_button"))
        footer.addWidget(self.close_button)
        self.main_layout.addLayout(footer)
        self.main_layout.addStretch(1)

        self.__refresh()

    def __connect_signals(self):
        self.refresh_button.clicked.connect(self.__refresh)
        self.unbind_selected_button.clicked.connect(self.__unbind_selected)
        self.unbind_all_button.clicked.connect(self.__unbind_all)
        self.close_button.clicked.connect(self.__cancel)

    def __refresh(self):
        self.bound_list.clear()
        try:
            serials = get_bound_serials()
            for s in serials:
                connected = is_serial_connected(s)
                suffix = " (Connected)" if connected else " (Disconnected)"
                item = QListWidgetItem(f"{s}{suffix}")
                self.bound_list.addItem(item)
        except Exception as e:
            config = NotificationConfig(title=get_content_name_async("basic_safety_settings","title"), content=str(e), duration=3000)
            show_notification(NotificationType.ERROR, config, parent=self)

    def __unbind_selected(self):
        item = self.bound_list.currentItem()
        if item is None:
            config = NotificationConfig(title=get_content_name_async("basic_safety_settings","title"), content=get_content_name_async("basic_safety_settings","usb_select_bound_hint"), duration=3000)
            show_notification(NotificationType.ERROR, config, parent=self)
            return
        text = item.text()
        serial = text.split(" ")[0]
        try:
            unbind(serial)
            config = NotificationConfig(title=get_content_name_async("basic_safety_settings","title"), content=get_content_name_async("basic_safety_settings","usb_unbind_selected_success"), duration=3000)
            show_notification(NotificationType.SUCCESS, config, parent=self)
            self.__refresh()
        except Exception as e:
            config = NotificationConfig(title=get_content_name_async("basic_safety_settings","title"), content=str(e), duration=3000)
            show_notification(NotificationType.ERROR, config, parent=self)

    def __unbind_all(self):
        try:
            unbind(None)
            config = NotificationConfig(title=get_content_name_async("basic_safety_settings","title"), content=get_content_name_async("basic_safety_settings","usb_unbind_all_success"), duration=3000)
            show_notification(NotificationType.SUCCESS, config, parent=self)
            self.__refresh()
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

