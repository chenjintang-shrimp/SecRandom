from qfluentwidgets import * 
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import os
from loguru import logger

def load_custom_font():
    font_path = './app/resource/font/HarmonyOS_Sans_SC_Bold.ttf'
    font_id = QFontDatabase.addApplicationFont(font_path)
    if font_id < 0:
        print("Failed to load font")
        return None
    font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
    return font_family

def get_theme_icon(icon_name):
    try:
        if qconfig.theme == Theme.AUTO:
            lightness = QApplication.palette().color(QPalette.Window).lightness()
            is_dark = lightness <= 127
        else:
            is_dark = qconfig.theme == Theme.DARK
        
        prefix = "light" if is_dark else "dark"
        suffix = "_light" if is_dark else "_dark"
        icon_path = f"app/resource/assets/{prefix}/{icon_name}{suffix}.svg"
        
        if not os.path.exists(icon_path):
            logger.warning(f"图标文件缺失: {icon_path}")
            # 返回默认图标
            default_path = f"app/resource/assets/{prefix}/ic_fluent_info_20_filled{suffix}.svg"
            if os.path.exists(default_path):
                return QIcon(default_path)
            return QIcon()
            
        return QIcon(icon_path)
    except Exception as e:
        logger.error(f"加载图标{icon_name}出错: {str(e)}")
        return QIcon()

class Config(QConfig):
    dpiScale = OptionsConfigItem(
        "Window", "DpiScale", "Auto", OptionsValidator([1, 1.25, 1.5, 1.75, 2, "Auto"]), restart=True)

YEAR = 2025
MONTH = 4
AUTHOR = "lzy98276"
VERSION = "v1.9.9.9"
APPLY_NAME = "SecRandom"
GITHUB_WEB = "https://github.com/SECTL/SecRandom"
BILIBILI_WEB = "https://space.bilibili.com/520571577"

cfg = Config()

cfg.themeMode.value = Theme.AUTO
qconfig.load('./app/Settings/config.json', cfg)