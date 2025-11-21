# ==================================================
# 导入库
# ==================================================

from loguru import logger
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


# ==================================================
# 浮动窗口管理 - 主容器
# ==================================================
class floating_window_management(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # 创建垂直布局
        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout.setSpacing(10)

        # 使用占位与延迟创建以减少首次打开时的卡顿
        self._deferred_factories = {}

        def make_placeholder(attr_name: str):
            w = QWidget()
            w.setObjectName(attr_name)
            layout = QVBoxLayout(w)
            layout.setContentsMargins(0, 0, 0, 0)
            self.vBoxLayout.addWidget(w)
            return w

        # 创建占位并注册工厂
        self.basic_settings = make_placeholder("basic_settings")
        self._deferred_factories["basic_settings"] = (
            lambda: floating_window_basic_settings(self)
        )

        self.appearance_settings = make_placeholder("appearance_settings")
        self._deferred_factories["appearance_settings"] = (
            lambda: floating_window_appearance_settings(self)
        )

        self.edge_settings = make_placeholder("edge_settings")
        self._deferred_factories["edge_settings"] = (
            lambda: floating_window_edge_settings(self)
        )

        # 分批异步创建真实子组件，间隔以减少主线程瞬时负载
        try:
            for i, name in enumerate(list(self._deferred_factories.keys())):
                QTimer.singleShot(120 * i, lambda n=name: self._create_deferred(n))
        except Exception as e:
            logger = globals().get("logger")
            if logger:
                logger.error(f"调度延迟创建浮窗子组件失败: {e}")

    def _create_deferred(self, name: str):
        factories = getattr(self, "_deferred_factories", {})
        if name not in factories:
            return
        try:
            factory = factories.pop(name)
        except Exception:
            return

        try:
            real_widget = factory()
        except Exception as e:
            logger = globals().get("logger")
            if logger:
                logger.error(f"创建浮窗子组件 {name} 失败: {e}")
            return

        placeholder = getattr(self, name, None)
        if placeholder is None:
            try:
                self.vBoxLayout.addWidget(real_widget)
            except Exception:
                pass
            setattr(self, name, real_widget)
            return

        layout = None
        try:
            layout = placeholder.layout()
        except Exception:
            layout = None

        if layout is None:
            # 替换占位
            try:
                index = -1
                for i in range(self.vBoxLayout.count()):
                    item = self.vBoxLayout.itemAt(i)
                    if item and item.widget() is placeholder:
                        index = i
                        break
                if index >= 0:
                    try:
                        item = self.vBoxLayout.takeAt(index)
                        widget = item.widget() if item else None
                        if widget is not None:
                            widget.deleteLater()
                        self.vBoxLayout.insertWidget(index, real_widget)
                    except Exception:
                        self.vBoxLayout.addWidget(real_widget)
                else:
                    self.vBoxLayout.addWidget(real_widget)
            except Exception:
                try:
                    self.vBoxLayout.addWidget(real_widget)
                except Exception:
                    pass
            setattr(self, name, real_widget)
            return

        try:
            layout.addWidget(real_widget)
            setattr(self, name, real_widget)
        except Exception:
            try:
                self.vBoxLayout.addWidget(real_widget)
                setattr(self, name, real_widget)
            except Exception:
                pass


# ==================================================
# 浮动窗口管理 - 基础设置
# ==================================================
class floating_window_basic_settings(GroupHeaderCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(
            get_content_name_async("floating_window_management", "basic_settings")
        )
        self.setBorderRadius(8)

        # 软件启动时浮窗显示隐藏开关
        self.startup_display_floating_window_switch = SwitchButton()
        self.startup_display_floating_window_switch.setOffText(
            get_content_switchbutton_name_async(
                "floating_window_management",
                "startup_display_floating_window",
                "disable",
            )
        )
        self.startup_display_floating_window_switch.setOnText(
            get_content_switchbutton_name_async(
                "floating_window_management",
                "startup_display_floating_window",
                "enable",
            )
        )
        self.startup_display_floating_window_switch.setChecked(
            readme_settings_async(
                "floating_window_management", "startup_display_floating_window"
            )
        )
        self.startup_display_floating_window_switch.checkedChanged.connect(
            self.startup_display_floating_window_switch_changed
        )

        # 浮窗透明度
        self.floating_window_opacity_spinbox = SpinBox()
        self.floating_window_opacity_spinbox.setFixedWidth(WIDTH_SPINBOX)
        self.floating_window_opacity_spinbox.setRange(0, 100)
        self.floating_window_opacity_spinbox.setSuffix("%")
        self.floating_window_opacity_spinbox.setValue(
            readme_settings_async(
                "floating_window_management", "floating_window_opacity"
            )
            * 100
        )
        self.floating_window_opacity_spinbox.valueChanged.connect(
            self.floating_window_opacity_spinbox_changed
        )

        # 重置浮窗位置按钮
        self.reset_floating_window_position_button = PushButton(
            get_content_pushbutton_name_async(
                "floating_window_management", "reset_floating_window_position_button"
            )
        )
        self.reset_floating_window_position_button.setText(
            get_content_name_async(
                "floating_window_management", "reset_floating_window_position_button"
            )
        )
        self.reset_floating_window_position_button.clicked.connect(
            self.reset_floating_window_position_button_clicked
        )

        # 添加设置项到分组
        self.addGroup(
            get_theme_icon("ic_fluent_desktop_sync_20_filled"),
            get_content_name_async(
                "floating_window_management", "startup_display_floating_window"
            ),
            get_content_description_async(
                "floating_window_management", "startup_display_floating_window"
            ),
            self.startup_display_floating_window_switch,
        )
        self.addGroup(
            get_theme_icon("ic_fluent_brightness_high_20_filled"),
            get_content_name_async(
                "floating_window_management", "floating_window_opacity"
            ),
            get_content_description_async(
                "floating_window_management", "floating_window_opacity"
            ),
            self.floating_window_opacity_spinbox,
        )
        self.addGroup(
            get_theme_icon("ic_fluent_arrow_reset_20_filled"),
            get_content_name_async(
                "floating_window_management", "reset_floating_window_position_button"
            ),
            get_content_description_async(
                "floating_window_management", "reset_floating_window_position_button"
            ),
            self.reset_floating_window_position_button,
        )

    def startup_display_floating_window_switch_changed(self, checked):
        update_settings(
            "floating_window_management", "startup_display_floating_window", checked
        )

    def floating_window_opacity_spinbox_changed(self, value):
        update_settings(
            "floating_window_management", "floating_window_opacity", value / 100
        )

    def reset_floating_window_position_button_clicked(self):
        # 这里应该实现重置浮窗位置的逻辑
        logger.debug("重置浮窗位置按钮被点击")


# ==================================================
# 浮动窗口管理 - 外观设置
# ==================================================
class floating_window_appearance_settings(GroupHeaderCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(
            get_content_name_async("floating_window_management", "appearance_settings")
        )
        self.setBorderRadius(8)

        # 浮窗按钮控件配置下拉框
        self.floating_window_button_control_combo_box = ComboBox()
        self.floating_window_button_control_combo_box.addItems(
            get_content_combo_name_async(
                "floating_window_management", "floating_window_button_control"
            )
        )
        self.floating_window_button_control_combo_box.setCurrentIndex(
            readme_settings_async(
                "floating_window_management", "floating_window_button_control"
            )
        )
        self.floating_window_button_control_combo_box.currentIndexChanged.connect(
            self.floating_window_button_control_combo_box_changed
        )

        # 浮窗排列方式下拉框
        self.floating_window_placement_combo_box = ComboBox()
        self.floating_window_placement_combo_box.addItems(
            get_content_combo_name_async(
                "floating_window_management", "floating_window_placement"
            )
        )
        self.floating_window_placement_combo_box.setCurrentIndex(
            readme_settings_async(
                "floating_window_management", "floating_window_placement"
            )
        )
        self.floating_window_placement_combo_box.currentIndexChanged.connect(
            self.floating_window_placement_combo_box_changed
        )

        # 浮窗显示样式下拉框
        self.floating_window_display_style_combo_box = ComboBox()
        self.floating_window_display_style_combo_box.addItems(
            get_content_combo_name_async(
                "floating_window_management", "floating_window_display_style"
            )
        )
        self.floating_window_display_style_combo_box.setCurrentIndex(
            readme_settings_async(
                "floating_window_management", "floating_window_display_style"
            )
        )
        self.floating_window_display_style_combo_box.currentIndexChanged.connect(
            self.floating_window_display_style_combo_box_changed
        )

        # 添加设置项到分组
        self.addGroup(
            get_theme_icon("ic_fluent_button_20_filled"),
            get_content_name_async(
                "floating_window_management", "floating_window_button_control"
            ),
            get_content_description_async(
                "floating_window_management", "floating_window_button_control"
            ),
            self.floating_window_button_control_combo_box,
        )
        self.addGroup(
            get_theme_icon("ic_fluent_align_left_20_filled"),
            get_content_name_async(
                "floating_window_management", "floating_window_placement"
            ),
            get_content_description_async(
                "floating_window_management", "floating_window_placement"
            ),
            self.floating_window_placement_combo_box,
        )
        self.addGroup(
            get_theme_icon("ic_fluent_design_ideas_20_filled"),
            get_content_name_async(
                "floating_window_management", "floating_window_display_style"
            ),
            get_content_description_async(
                "floating_window_management", "floating_window_display_style"
            ),
            self.floating_window_display_style_combo_box,
        )

    def floating_window_button_control_combo_box_changed(self, index):
        update_settings(
            "floating_window_management", "floating_window_button_control", index
        )

    def floating_window_placement_combo_box_changed(self, index):
        update_settings(
            "floating_window_management", "floating_window_placement", index
        )

    def floating_window_display_style_combo_box_changed(self, index):
        update_settings(
            "floating_window_management", "floating_window_display_style", index
        )


# ==================================================
# 浮动窗口管理 - 贴边设置
# ==================================================
class floating_window_edge_settings(GroupHeaderCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(
            get_content_name_async("floating_window_management", "edge_settings")
        )
        self.setBorderRadius(8)

        # 浮窗贴边开关
        self.floating_window_stick_to_edge_switch = SwitchButton()
        self.floating_window_stick_to_edge_switch.setOffText(
            get_content_switchbutton_name_async(
                "floating_window_management", "floating_window_stick_to_edge", "disable"
            )
        )
        self.floating_window_stick_to_edge_switch.setOnText(
            get_content_switchbutton_name_async(
                "floating_window_management", "floating_window_stick_to_edge", "enable"
            )
        )
        self.floating_window_stick_to_edge_switch.setChecked(
            readme_settings_async(
                "floating_window_management", "floating_window_stick_to_edge"
            )
        )
        self.floating_window_stick_to_edge_switch.checkedChanged.connect(
            self.floating_window_stick_to_edge_switch_changed
        )

        # 浮窗贴边回收秒数
        self.floating_window_stick_to_edge_recover_seconds_spinbox = SpinBox()
        self.floating_window_stick_to_edge_recover_seconds_spinbox.setFixedWidth(
            WIDTH_SPINBOX
        )
        self.floating_window_stick_to_edge_recover_seconds_spinbox.setRange(0, 25600)
        self.floating_window_stick_to_edge_recover_seconds_spinbox.setSuffix("秒")
        self.floating_window_stick_to_edge_recover_seconds_spinbox.setValue(
            readme_settings_async(
                "floating_window_management",
                "floating_window_stick_to_edge_recover_seconds",
            )
        )
        self.floating_window_stick_to_edge_recover_seconds_spinbox.valueChanged.connect(
            self.floating_window_stick_to_edge_recover_seconds_spinbox_changed
        )

        # 浮窗贴边显示样式下拉框
        self.floating_window_stick_to_edge_display_style_combo_box = ComboBox()
        self.floating_window_stick_to_edge_display_style_combo_box.addItems(
            get_content_combo_name_async(
                "floating_window_management",
                "floating_window_stick_to_edge_display_style",
            )
        )
        self.floating_window_stick_to_edge_display_style_combo_box.setCurrentIndex(
            readme_settings_async(
                "floating_window_management",
                "floating_window_stick_to_edge_display_style",
            )
        )
        self.floating_window_stick_to_edge_display_style_combo_box.currentIndexChanged.connect(
            self.floating_window_stick_to_edge_display_style_combo_box_changed
        )

        # 添加设置项到分组
        self.addGroup(
            get_theme_icon("ic_fluent_pin_20_filled"),
            get_content_name_async(
                "floating_window_management", "floating_window_stick_to_edge"
            ),
            get_content_description_async(
                "floating_window_management", "floating_window_stick_to_edge"
            ),
            self.floating_window_stick_to_edge_switch,
        )
        self.addGroup(
            get_theme_icon("ic_fluent_timer_20_filled"),
            get_content_name_async(
                "floating_window_management",
                "floating_window_stick_to_edge_recover_seconds",
            ),
            get_content_description_async(
                "floating_window_management",
                "floating_window_stick_to_edge_recover_seconds",
            ),
            self.floating_window_stick_to_edge_recover_seconds_spinbox,
        )
        self.addGroup(
            get_theme_icon("ic_fluent_desktop_sync_20_filled"),
            get_content_name_async(
                "floating_window_management",
                "floating_window_stick_to_edge_display_style",
            ),
            get_content_description_async(
                "floating_window_management",
                "floating_window_stick_to_edge_display_style",
            ),
            self.floating_window_stick_to_edge_display_style_combo_box,
        )

    def floating_window_stick_to_edge_switch_changed(self, checked):
        update_settings(
            "floating_window_management", "floating_window_stick_to_edge", checked
        )

    def floating_window_stick_to_edge_recover_seconds_spinbox_changed(self, value):
        update_settings(
            "floating_window_management",
            "floating_window_stick_to_edge_recover_seconds",
            value,
        )

    def floating_window_stick_to_edge_display_style_combo_box_changed(self, index):
        update_settings(
            "floating_window_management",
            "floating_window_stick_to_edge_display_style",
            index,
        )
