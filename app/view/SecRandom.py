from qfluentwidgets import *
from qfluentwidgets import FluentIcon as fIcon
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize, QEventLoop, QTimer, pyqtSignal 

import sys
import json
import os
from loguru import logger

# 确认是否存在设置目录
if ('./app/Settings') != None and not os.path.exists('./app/Settings'):
    os.makedirs('./app/Settings')

# 配置日志记录
log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

logger.add(
    os.path.join(log_dir, "SecRandom_{time:YYYY-MM-DD}.log"),
    rotation="1 MB",
    encoding="utf-8",
    retention="30 days",
    format="{time:YYYY-MM-DD HH:mm:ss:SSS} | {level} | {name}:{function}:{line} - {message}"
)

# 导入子页面
from app.view.quicksetup import quicksetup
from app.view.setting import setting
from app.view.history import history
from app.view.single import single
from app.view.multiplayer import multiplayer
from app.view.group import groupplayer

class Window(MSFluentWindow):
    def __init__(self):
        super().__init__()
        self.resize(1200, 800)
        self.setMinimumSize(1000, 800)
        self.setWindowTitle('SecRandom')
        self.setWindowIcon(QIcon('./app/resource/icon/SecRandom.png'))
        self.start_cleanup()

        # 获取主屏幕
        screen = QApplication.primaryScreen()
        # 获取屏幕的可用几何信息
        desktop = screen.availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)

        # self.show()
        self.createSubInterface()

    def createSubInterface(self):
        loop = QEventLoop(self)
        QTimer.singleShot(1000, loop.quit)
        loop.exec()

        self.quicksetupInterface = quicksetup(self)
        self.quicksetupInterface.setObjectName("quicksetupInterface")

        self.settingInterface = setting(self)
        self.settingInterface.setObjectName("settingInterface")

        self.historyInterface = history(self)
        self.historyInterface.setObjectName("historyInterface")

        self.singleInterface = single(self)
        self.singleInterface.setObjectName("singleInterface")

        self.multiInterface = multiplayer(self)
        self.multiInterface.setObjectName("multiInterface")

        self.groupInterface = groupplayer(self)
        self.groupInterface.setObjectName("groupInterface")

        self.initNavigation()

    def initNavigation(self):
        # 使用 MSFluentWindow 的 addSubInterface 方法
        self.addSubInterface(self.singleInterface, fIcon.ROBOT, '抽单人', position=NavigationItemPosition.TOP)
        self.addSubInterface(self.multiInterface, fIcon.PEOPLE, '抽多人', position=NavigationItemPosition.TOP)
        self.addSubInterface(self.groupInterface, fIcon.TILES, '抽小组', position=NavigationItemPosition.TOP) 

        self.addSubInterface(self.historyInterface, fIcon.HISTORY, '历史记录', position=NavigationItemPosition.BOTTOM)
        self.addSubInterface(self.quicksetupInterface, fIcon.QUICK_NOTE, '名单设置', position=NavigationItemPosition.BOTTOM)  
        self.addSubInterface(self.settingInterface, fIcon.SETTING, '设置', position=NavigationItemPosition.BOTTOM)

    def closeEvent(self, event):
        """窗口关闭时清理临时抽取记录文件"""
        # 获取抽选模式设置
        try:
            with open('app/Settings/Settings.json', 'r', encoding='utf-8') as f:
                settings = json.load(f)
                global_draw_mode = settings['global']['draw_mode']

        except Exception as e:
            global_draw_mode = 1
            logger.error(f"加载抽选模式设置时出错: {e}, 使用默认:不重复抽取(直到软件重启)模式来清理临时抽取记录文件")

        import glob
        temp_dir = "app/resource/Temp"
        # 根据抽选模式执行不同逻辑
        # 跟随全局设置
        if global_draw_mode == 1:  # 不重复抽取(直到软件重启)
            # 清理临时抽取记录文件
            if os.path.exists(temp_dir):
                for file in glob.glob(f"{temp_dir}/until_the_reboot_draw_*.json"):
                    try:
                        os.remove(file)
                        logger.info(f"已清理临时抽取记录文件: {file}")
                    except Exception as e:
                        logger.error(f"清理临时抽取记录文件失败: {e}")
            # 清理临时抽取范围记录文件            
            if os.path.exists(temp_dir):
                for file in glob.glob(f"{temp_dir}/until_the_reboot_scope_*.json"):
                    try:
                        os.remove(file)
                        logger.info(f"已清理临时抽取记录文件: {file}")
                    except Exception as e:
                        logger.error(f"清理临时抽取记录文件失败: {e}")
            event.accept()

    def start_cleanup(self):
        """软件启动时清理临时抽取记录文件"""
        # 获取抽选模式设置
        try:
            with open('app/Settings/Settings.json', 'r', encoding='utf-8') as f:
                settings = json.load(f)
                global_draw_mode = settings['global']['draw_mode']

        except Exception as e:
            global_draw_mode = 1
            logger.error(f"加载抽选模式设置时出错: {e}, 使用默认:不重复抽取(直到软件重启)模式来清理临时抽取记录文件")

        import glob
        temp_dir = "app/resource/Temp"
        # 根据抽选模式执行不同逻辑
        # 跟随全局设置
        if global_draw_mode == 1:  # 不重复抽取(直到软件重启)
            # 清理临时抽取记录文件
            if os.path.exists(temp_dir):
                for file in glob.glob(f"{temp_dir}/until_the_reboot_draw_*.json"):
                    try:
                        os.remove(file)
                        logger.info(f"已清理临时抽取记录文件: {file}")
                    except Exception as e:
                        logger.error(f"清理临时抽取记录文件失败: {e}")
            # 清理临时抽取范围记录文件            
            if os.path.exists(temp_dir):
                for file in glob.glob(f"{temp_dir}/until_the_reboot_scope_*.json"):
                    try:
                        os.remove(file)
                        logger.info(f"已清理临时抽取记录文件: {file}")
                    except Exception as e:
                        logger.error(f"清理临时抽取记录文件失败: {e}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    SecRandom = Window()
    SecRandom.show()
    sys.exit(app.exec())