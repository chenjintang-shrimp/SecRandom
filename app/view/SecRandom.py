from qfluentwidgets import * # type: ignore
from qfluentwidgets import FluentIcon as fIcon # type: ignore
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize, QEventLoop, QTimer 

import sys
import json
import os
from loguru import logger

# 确认是否存在设置目录
if ('./app/Settings') != None and not os.path.exists('./app/Settings'): # type: ignore
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
# 读取配置文件
def read_json(json_path): # type: ignore
    if os.path.exists(json_path): # type: ignore
        try:
            with open(json_path, 'r', encoding='utf-8') as file: # type: ignore
                return json.load(file)
        except json.JSONDecodeError:
            # 如果文件内容不是有效的 JSON 格式，返回空字典
            return {} # type: ignore
    return {} # type: ignore
#读取以及写入配置文件
def write_json(json_path, field_name, default_value):  # type: ignore
    try:
        with open(json_path, 'r', encoding='utf-8') as file:  # type: ignore
            json_file = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        json_file = {}
    json_file[field_name] = default_value
    json_file.update(json_file)  # type: ignore
    with open(json_path, 'w', encoding='utf-8') as file:  # type: ignore
        json.dump(json_file, file, ensure_ascii=False, indent=4)

# 写入默认数据
write_json('./app/Settings/Settings.json', 'software_author', 'lzy98276')
write_json('./app/Settings/Settings.json', 'software_name', 'SecRandom')
write_json('./app/Settings/Settings.json', 'version', '1.0.0.0-beta')

# 导入子页面
from app.view.setting import setting
from app.view.single import single

class Window(MSFluentWindow):
    def __init__(self):
        super().__init__() # type: ignore
        self.resize(800, 600)
        self.setMinimumSize(600, 400)
        self.setWindowTitle('SecRandom')
        self.setWindowIcon(QIcon('./app/resource/icon/SecRandom.png'))
        # 获取主屏幕
        screen = QApplication.primaryScreen()
        # 获取屏幕的可用几何信息
        desktop = screen.availableGeometry() # type: ignore
        w, h = desktop.width(), desktop.height()
        self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)

        self.splashScreen = SplashScreen(self.windowIcon(), self)
        self.splashScreen.setIconSize(QSize(168, 168))
        self.show()
        self.createSubInterface()
        self.splashScreen.finish()

    def createSubInterface(self):
        loop = QEventLoop(self)
        QTimer.singleShot(1000, loop.quit) # type: ignore
        loop.exec()

        self.singleInterface = single(self) # type: ignore
        self.singleInterface.setObjectName("singleInterface")  # 设置对象名称

        self.settingInterface = setting(self) # type: ignore
        self.settingInterface.setObjectName("settingInterface")  # 设置对象名称

        self.initNavigation()
        self.initWindow()

    def initNavigation(self):
        # 使用 MSFluentWindow 的 addSubInterface 方法
        self.addSubInterface(self.singleInterface, fIcon.PEOPLE, '抽单人', position=NavigationItemPosition.TOP) # type: ignore

        self.addSubInterface(self.settingInterface, fIcon.SETTING, '设置', position=NavigationItemPosition.BOTTOM) # type: ignore

    def initWindow(self):
        self.resize(800, 600)
        self.setWindowIcon(QIcon('./app/resource/icon/SecRandom.png'))
        self.setWindowTitle('SecRandom')

        # 获取主屏幕
        screen = QApplication.primaryScreen()
        # 获取屏幕的可用几何信息
        desktop = screen.availableGeometry() # type: ignore
        w, h = desktop.width(), desktop.height()
        self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)

    def closeEvent(self, event):
        """窗口关闭时清理临时抽取记录文件"""
        # 获取抽选模式设置
        try:
            with open('app/Settings/Settings.json', 'r', encoding='utf-8') as f:
                settings = json.load(f)
                single_player_draw_mode = settings['single_player']['draw_mode']
                if single_player_draw_mode == 0:
                    global_draw_mode = settings['global']['draw_mode']
        except Exception as e:
            single_player_draw_mode = 1
            logger.error(f"加载抽选模式设置时出错: {e}, 使用默认:不重复抽取(直到软件重启)模式来清理临时抽取记录文件")

        import glob
        temp_dir = "app/resource/Temp"
        # 根据抽选模式执行不同逻辑
        # 跟随全局设置
        if global_draw_mode == 1  and single_player_draw_mode == 0:  # 不重复抽取(直到软件重启)
            if os.path.exists(temp_dir):
                for file in glob.glob(f"{temp_dir}/until_the_reboot_draw_*.json"):
                    try:
                        os.remove(file)
                        logger.info(f"已清理临时抽取记录文件: {file}")
                    except Exception as e:
                        logger.error(f"清理临时抽取记录文件失败: {e}")
            event.accept()
        # 跟随单抽设置
        elif single_player_draw_mode == 2:  # 不重复抽取(直到软件重启)
            if os.path.exists(temp_dir):
                for file in glob.glob(f"{temp_dir}/until_the_reboot_draw_*.json"):
                    try:
                        os.remove(file)
                        logger.info(f"已清理临时抽取记录文件: {file}")
                    except Exception as e:
                        logger.error(f"清理临时抽取记录文件失败: {e}")
            event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    SecRandom = Window()
    SecRandom.show()
    sys.exit(app.exec())