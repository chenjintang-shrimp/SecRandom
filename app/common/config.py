from qfluentwidgets import * 
from PyQt5.QtGui import *

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
VERSION = "v1.0.2.1-beta"
APPLY_NAME = "SecRandom"
GITHUB_WEB = "https://github.com/SecRandom/SecRandom"
BILIBILI_WEB = "https://space.bilibili.com/520571577"

cfg = Config()
cfg.themeMode.value = Theme.AUTO
qconfig.load('./app/Settings/config.json', cfg) 