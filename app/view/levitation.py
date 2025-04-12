from qfluentwidgets import *
from qfluentwidgets import FluentIcon as fIcon
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import json

from ..common.config import load_custom_font

class LevitationWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.load_position()

    def initUI(self):
        layout = QHBoxLayout()

        # 创建容器按钮
        self.container_button = QWidget()
        button_layout = QHBoxLayout(self.container_button)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(0)
        
        # 左侧 MENU 图标
        self.menu_button = ToolButton(fIcon.MENU, self.container_button)
        # 设置图标大小
        self.menu_button.setIconSize(QSize(20, 20))
        # 设置透明度
        self.menu_button.setStyleSheet('opacity: 0;')
        # 添加长按拖动功能
        self.menu_button.pressed.connect(self.start_drag) 
        self.menu_button.released.connect(self.stop_drag)
        # 设置按钮的尺寸
        self.menu_button.setFixedSize(40, 50)
        button_layout.addWidget(self.menu_button)
        # 添加字体
        self.menu_button.setFont(QFont(load_custom_font(), 12))

        # 右侧 PEOPLE 图标
        self.people_button = ToolButton(self.container_button)
        self.people_button.setIcon(QIcon("app\\resource\\icon\\SecRandom_floating.png"))
        # 设置图标大小
        self.people_button.setIconSize(QSize(40, 40))
        # 设置透明度
        self.people_button.setStyleSheet('opacity: 0;')
        # 设置按钮的尺寸
        self.people_button.setFixedSize(60, 50)
        # 鼠标放上去会变成手型
        self.people_button.setCursor(Qt.PointingHandCursor)
        button_layout.addWidget(self.people_button)
        # 添加字体
        self.people_button.setFont(QFont(load_custom_font(), 12))
        
        # 将容器按钮添加到主布局
        layout.addWidget(self.container_button)

        self.setLayout(layout)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool | Qt.X11BypassWindowManagerHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet('border-radius: 5px; background-color: rgba(65, 66, 66, 0.5);')
        self.setProperty("radius", 5)

        self.people_button.clicked.connect(self.on_people_clicked)

    def on_people_clicked(self):
        if hasattr(self, 'pumping_floating_Interface') and self.pumping_floating_Interface.isVisible():
            self.pumping_floating_Interface.activateWindow()
            self.pumping_floating_Interface.raise_()
            return
            
        from app.view.pumping_floating import pumping_floating_window
        if not hasattr(self, 'pumping_floating_Interface') or not self.pumping_floating_Interface:
            self.pumping_floating_Interface = pumping_floating_window()
        self.pumping_floating_Interface.show()
        self.pumping_floating_Interface.activateWindow()
        self.pumping_floating_Interface.raise_()

    def start_drag(self, event=None):
        if event and event.button() == Qt.RightButton or not event:
            self.drag_position = self.menu_button.mapToGlobal(self.menu_button.pos()) - self.pos()

    def mousePressEvent(self, event):
        # 禁用点击功能，只允许长按拖动
        if event.button() == Qt.RightButton and event.pos() in self.menu_button.geometry():
            self.start_drag(event)
        else:
            event.ignore()

    def stop_drag(self):
        self.save_position()

    def __init__(self):
        super().__init__()
        self.initUI()
        self.load_position()
        self.move_timer = QTimer(self)
        self.move_timer.setSingleShot(True)
        self.move_timer.timeout.connect(self.save_position)
        
    def mouseMoveEvent(self, event):
        if event.buttons() in [Qt.LeftButton, Qt.RightButton]:
            # 计算窗口位置
            new_pos = QPoint(event.globalPos().x() + 5, event.globalPos().y() + 5)
            
            # 获取屏幕尺寸
            screen = QApplication.desktop().screenGeometry()
            
            # 限制窗口不超出屏幕
            new_pos.setX(max(0, min(new_pos.x(), screen.width() - self.width())))
            new_pos.setY(max(0, min(new_pos.y(), screen.height() - self.height())))
            
            self.move(new_pos)
            self.move_timer.stop()
            self.move_timer.start(300)
            
    def save_position(self):
        pos = self.pos()
        try:
            with open("app/Settings/Settings.json", "r") as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            data = {}
        
        data["position"] = {
            "x": pos.x(), 
            "y": pos.y()
        }
        with open("app/Settings/Settings.json", "w") as f:
            json.dump(data, f, indent=4)
        
    def load_position(self):
        try:
            with open("app/Settings/Settings.json", "r") as f:
                data = json.load(f)
                pos = data.get("position", {"x": 100, "y": 100})
                self.move(QPoint(pos["x"], pos["y"]))
        except (FileNotFoundError, json.JSONDecodeError):
            screen = QApplication.desktop().screenGeometry()
            x = (screen.width() - self.width()) // 2
            y = (screen.height() - self.height()) // 2
            self.move(QPoint(x, y))