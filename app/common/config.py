from qfluentwidgets import * 
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import os
from loguru import logger

from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from packaging.version import Version
import requests
import comtypes
from comtypes import POINTER

def check_for_updates():
    try:
        current_version = VERSION.lstrip('v')
        url = "https://api.github.com/repos/SECTL/SecRandom/releases/latest"
        response = requests.get(url, timeout=10, verify=False)
        response.raise_for_status()
        latest_release = response.json()
        latest_version_tag = latest_release['tag_name']
        latest_version = latest_version_tag.lstrip('v')
        if Version(latest_version) > Version(current_version):
            logger.info(f"当前版本: {current_version}, 最新版本: {latest_version_tag}, 需要更新")
            return True, latest_version_tag
        else:
            logger.info(f"当前版本: {current_version}, 最新版本: {latest_version_tag}, 无需更新")
            return False, None
    except requests.exceptions.RequestException as e:
        logger.error(f"网络请求错误: {e}")
        return False, None
    except KeyError as e:
        logger.error(f"API响应格式错误: {e}")
        return False, None
    except Exception as e:
        logger.error(f"检查更新失败: {e}")
        return False, None

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
        is_dark = is_dark_theme(qconfig) # True: 深色, False: 浅色
        
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

def is_dark_theme(qconfig):
    if qconfig.theme == Theme.AUTO:
        lightness = QApplication.palette().color(QPalette.Window).lightness()
        return lightness <= 127
    else:
        return qconfig.theme == Theme.DARK

def restore_volume(volume_value):
    # 初始化COM库
    comtypes.CoInitialize()
    
    # 获取默认音频设备
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(
        IAudioEndpointVolume._iid_, comtypes.CLSCTX_ALL, None)
    volume = comtypes.cast(interface, POINTER(IAudioEndpointVolume))
    
    # 取消静音
    volume.SetMute(0, None)
    
    # 设置音量为100%
    volume.SetMasterVolumeLevelScalar(volume_value / 100.0, None)
    
    # 释放COM库
    comtypes.CoUninitialize()


class Config(QConfig):
    dpiScale = OptionsConfigItem(
        "Window", "DpiScale", "Auto", OptionsValidator([1, 1.25, 1.5, 1.75, 2, "Auto"]), restart=True)

YEAR = 2025
MONTH = 4
AUTHOR = "lzy98276"
VERSION = "v0.0.0.0"
APPLY_NAME = "SecRandom"
GITHUB_WEB = "https://github.com/SECTL/SecRandom"
BILIBILI_WEB = "https://space.bilibili.com/520571577"

cfg = Config()

cfg.themeMode.value = Theme.AUTO
qconfig.load('./app/Settings/config.json', cfg)