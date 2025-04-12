from qfluentwidgets import * 
from PyQt5.QtGui import * 

import os
from loguru import logger

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

def load_custom_font():
    font_path = './app/resource/font/HarmonyOS_Sans_SC_Bold.ttf'
    font_id = QFontDatabase.addApplicationFont(font_path)
    if font_id < 0:
        print("Failed to load font")
        return None
    font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
    return font_family

class Config(QConfig):
    # 主题模式
    dpiScale = OptionsConfigItem(
        "Window", "DpiScale", "Auto", OptionsValidator([1, 1.25, 1.5, 1.75, 2, "Auto"]), restart=True)

YEAR = 2025
MONTH = 4
AUTHOR = "lzy98276"
VERSION = "v1.0.1.0"
APPLY_NAME = "SecRandom"
GITHUB_WEB = "https://github.com/SecRandom/SecRandom"

cfg = Config()
cfg.themeMode.value = Theme.AUTO
qconfig.load('./app/Settings/config.json', cfg) 