from qfluentwidgets import * 
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtNetwork import *

import json
import os
from pathlib import Path
from loguru import logger
import requests
# 禁用requests的SSL验证警告
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from packaging.version import Version
import platform
import subprocess
import sys
from app.common.path_utils import path_manager
from app.common.path_utils import open_file, ensure_dir

# Windows-specific imports
if platform.system() == 'Windows':
    try:
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
        import comtypes
        from comtypes import POINTER
        WINDOWS_AUDIO_AVAILABLE = True
    except ImportError:
        WINDOWS_AUDIO_AVAILABLE = False
else:
    WINDOWS_AUDIO_AVAILABLE = False

def get_update_channel():
    """获取当前选择的更新通道，默认为稳定通道"""
    try:
        settings_file = path_manager.get_settings_path()
        if settings_file.exists():
            with open_file(settings_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return config.get('channel', 'stable')
        return 'stable'
    except Exception as e:
        logger.error(f"读取更新通道配置失败: {e}")
        return 'stable'


def set_update_channel(channel):
    """保存更新通道配置，保留其他配置信息"""
    try:
        settings_file = path_manager.get_settings_path()
        # 读取现有配置
        config = {}
        if settings_file.exists():
            with open_file(settings_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
        
        # 检查通道是否已设置，避免重复操作
        if config.get('channel') == channel:
            # logger.debug(f"更新通道已为 {channel}，无需更改")
            return
        
        # 更新通道配置
        config['channel'] = channel
        
        # 确保目录存在
        ensure_dir(settings_file.parent)
        
        # 保存更新后的配置
        with open_file(settings_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        logger.info(f"更新通道已设置为: {channel}")
    except json.JSONDecodeError:
        logger.error("配置文件格式错误，将创建新的配置文件")
        # 创建新的配置文件
        settings_file = path_manager.get_settings_path()
        ensure_dir(settings_file.parent)
        with open_file(settings_file, 'w', encoding='utf-8') as f:
            json.dump({'channel': channel}, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"保存更新通道配置失败: {e}")


def check_for_updates(channel=None):
    """检查应用程序更新
    在后台检查更新，支持稳定通道(stable)和测试通道(beta)"""
    # 如果未指定通道，使用配置中的默认通道
    if channel is None:
        channel = get_update_channel()
    try:
        current_version = VERSION.lstrip('v')
        if channel == 'stable':
            url = "https://api.github.com/repos/SECTL/SecRandom/releases/latest"
        else:
            url = "https://api.github.com/repos/SECTL/SecRandom/releases"

        # 发送网络请求
        headers = {
            'User-Agent': 'SecRandom-Updater'
        }
        
        # 禁用SSL验证以避免证书验证失败的问题
        response = requests.get(url, headers=headers, timeout=10, verify=False)
        response.raise_for_status()
        
        response_json = response.json()
        
        if channel == 'stable':
            latest_release = response_json
            latest_version_tag = latest_release['tag_name']
        else:
            # 获取所有发布并筛选预发布版本
            releases = response_json
            # 解析所有版本并比较版本号
            all_versions = []
            for release in releases:
                version_tag = release['tag_name']
                # 提取版本号并移除'v'前缀
                version = version_tag.lstrip('v')
                all_versions.append((Version(version), release))
            # 按版本号降序排序
            all_versions.sort(reverse=True, key=lambda x: x[0])
            if not all_versions:
                return False, None
            latest_version, latest_release = all_versions[0]
            latest_version_tag = latest_release['tag_name']

        latest_version = latest_version_tag.lstrip('v')
        if Version(latest_version) > Version(current_version):
            logger.info(f"发现新版本: 当前版本 {current_version}, 最新版本 {latest_version_tag}")
            return True, latest_version_tag
        else:
            logger.info(f"当前版本 {current_version} 已经是最新版本")
            return False, None
    except requests.exceptions.RequestException as e:
        logger.error(f"网络请求失败: {e}")
        return False, None
    except json.JSONDecodeError as e:
        logger.error(f"API响应格式错误: {e}")
        return False, None
    except Exception as e:
        logger.error(f"检查更新失败: {e}")
        return False, None

def load_custom_font():
    """加载自定义字体，根据用户设置决定是否加载 HarmonyOS Sans SC 字体
    
    Returns:
        str: 字体家族名称，如果加载失败则返回 None
    """
    # 检查是否已经加载过字体，避免重复加载
    if hasattr(load_custom_font, '_font_cache') and load_custom_font._font_cache:
        return load_custom_font._font_cache
    
    # 读取自定义设置文件
    try:
        custom_settings_path = path_manager.get_settings_path('custom_settings.json')
        if custom_settings_path.is_file():
            with open_file(custom_settings_path, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                personal_settings = settings.get('personal', {})
                font_family_setting = personal_settings.get('font_family', '')
            
            # 如果字体设置为 HarmonyOS Sans SC，则加载自定义字体
            if font_family_setting == "HarmonyOS Sans SC":
                font_path = path_manager.get_resource_path('font', 'HarmonyOS_Sans_SC_Bold.ttf')
                font_id = QFontDatabase.addApplicationFont(str(font_path))
                if font_id < 0:
                    logger.error(f"加载自定义字体失败: {font_path}")
                    return None
                font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
                # logger.info(f"成功加载自定义字体: {font_family}")
                # 缓存字体
                load_custom_font._font_cache = font_family
                return font_family
            else:
                # logger.info(f"使用系统默认字体: {font_family_setting}")
                # 缓存字体
                load_custom_font._font_cache = font_family_setting
                return font_family_setting
        else:
            # 如果自定义设置文件不存在，默认加载 HarmonyOS Sans SC 字体
            font_path = path_manager.get_resource_path('font', 'HarmonyOS_Sans_SC_Bold.ttf')
            font_id = QFontDatabase.addApplicationFont(str(font_path))
            if font_id < 0:
                logger.error(f"加载自定义字体失败: {font_path}")
                return None
            font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
            # logger.info(f"成功加载默认字体: {font_family}")
            # 缓存字体
            load_custom_font._font_cache = font_family
            return font_family
    except Exception as e:
        logger.error(f"读取自定义设置失败，使用默认字体: {e}")
        # 出错时默认加载 HarmonyOS Sans SC 字体
        font_path = path_manager.get_resource_path('font', 'HarmonyOS_Sans_SC_Bold.ttf')
        font_id = QFontDatabase.addApplicationFont(str(font_path))
        if font_id < 0:
            logger.error(f"加载自定义字体失败: {font_path}")
            return None
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
        # 缓存字体
        load_custom_font._font_cache = font_family
        return font_family

class FluentSystemIcons(FluentFontIconBase):
    """Fluent System Icons 字体图标类"""
    
    def __init__(self, char):
        """初始化字体图标
        
        Args:
            char: 图标字符
        """
        super().__init__(char)
    
    def path(self, theme=Theme.AUTO):
        """返回字体文件路径"""
        return str(path_manager.get_resource_path('assets', 'FluentSystemIcons-Filled.ttf'))
    
    def iconNameMapPath(self):
        """返回图标名称到图标码点的映射表文件路径"""
        return str(path_manager.get_resource_path('assets', 'FluentSystemIcons-Filled.json'))


def get_theme_icon(icon_name):
    """获取主题相关的图标
    
    Args:
        icon_name: 图标名称或码点
        
    Returns:
        QIcon: 图标对象
    """
    try:
        # 尝试使用名称获取图标
        if isinstance(icon_name, str) and not icon_name.startswith('\\u'):
            # 尝试从JSON文件中直接获取码点
            try:
                map_path = path_manager.get_resource_path('assets', 'FluentSystemIcons-Filled.json')
                with open(map_path, 'r', encoding='utf-8') as f:
                    icon_map = json.load(f)
                
                if icon_name in icon_map:
                    # 获取图标码点并转换为字符串
                    code_point = icon_map[icon_name]
                    char = chr(code_point)
                    icon = FluentSystemIcons(char)
                    return icon
                else:
                    raise ValueError(f"图标名称 '{icon_name}' 未在图标映射表中找到")
            except Exception as json_error:
                logger.error(f"从JSON加载图标'{icon_name}'也失败: {str(json_error)}")
                raise
        else:
            # 处理码点输入
            if isinstance(icon_name, str) and icon_name.startswith('\\u'):
                # 将Unicode字符串转换为字符
                code_point = int(icon_name[2:], 16)
                char = chr(code_point)
                icon = FluentSystemIcons(char)
            elif isinstance(icon_name, int):
                # 将整数码点转换为字符
                char = chr(icon_name)
                icon = FluentSystemIcons(char)
            else:
                # 直接使用字符
                icon = FluentSystemIcons(icon_name)
            
        return icon
    except Exception as e:
        logger.error(f"加载图标{icon_name}出错: {str(e)}")
        # 返回默认图标
        try:
            # 尝试使用码点创建默认图标
            default_char = chr(62634)  # 使用info图标的码点
            return FluentSystemIcons(default_char)
        except Exception as default_error:
            logger.error(f"加载默认图标也失败: {str(default_error)}")
            # 返回空的QIcon作为最后备选
            return QIcon()

def is_dark_theme(qconfig):
    if qconfig.theme == Theme.AUTO:
        lightness = QApplication.palette().color(QPalette.Window).lightness()
        return lightness <= 127
    else:
        return qconfig.theme == Theme.DARK

def restore_volume(volume_value):
    """跨平台音量恢复函数
    
    Args:
        volume_value (int): 音量值 (0-100)
    """
    # Windows音频控制
    try:
        # 初始化COM库
        comtypes.CoInitialize()
        
        # 获取默认音频设备
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(
            IAudioEndpointVolume._iid_, comtypes.CLSCTX_ALL, None)
        volume = comtypes.cast(interface, POINTER(IAudioEndpointVolume))
        
        try:
            # 取消静音
            volume.SetMute(0, None)
            
            # 设置音量
            volume.SetMasterVolumeLevelScalar(volume_value / 100.0, None)
            logger.info(f"Windows音量设置为: {volume_value}%")
        finally:
            # 确保COM对象在释放COM库前被正确释放
            # 通过将对象设置为None来减少引用计数
            volume = None
            interface = None
            devices = None
            
            # 释放COM库
            comtypes.CoUninitialize()
    except Exception as e:
        logger.error(f"Windows音量控制失败: {e}")


class Config(QConfig):
    dpiScale = OptionsConfigItem(
        "Window", "DpiScale", "Auto", OptionsValidator([1, 1.25, 1.5, 1.75, 2, "Auto"]), restart=True)
    themeColor = ColorConfigItem(
        "Theme", "Color", "#0078D4")  # Windows系统默认蓝色

YEAR = 2025
MONTH = 4
AUTHOR = "lzy98276"
VERSION = "v0.0.0.0"
APPLY_NAME = "SecRandom"
GITHUB_WEB = "https://github.com/SECTL/SecRandom"
BILIBILI_WEB = "https://space.bilibili.com/520571577"
WEBSITE = "https://secrandom.netlify.app"
APP_DESCRIPTION = "一个易用的班级抽号软件，专为教育场景设计，让课堂点名更高效透明"  # 应用程序描述
APP_COPYRIGHT = f"Copyright © {YEAR} {AUTHOR}. All rights reserved."  # 应用程序版权信息
APP_LICENSE = "GPL-3.0 License"  # 应用程序许可证
APP_EMAIL = "lzy.12@foxmail.com"  # 应用程序邮箱

cfg = Config()

cfg.themeMode.value = Theme.AUTO

# 获取配置文件的绝对路径
def get_config_file_path():
    """获取配置文件的绝对路径"""
    return path_manager.get_settings_path('config.json')

config_file_path = get_config_file_path()
# 确保配置目录存在
path_manager.ensure_directory_exists(config_file_path.parent)
qconfig.load(str(config_file_path), cfg)

def setThemeColor(color):
    """设置主题色
    
    Args:
        color: 主题色，可以是 QColor、Qt.GlobalColor 或字符串（十六进制颜色或颜色名称）
    """
    if isinstance(color, QColor):
        hex_color = color.name()
    elif isinstance(color, Qt.GlobalColor):
        hex_color = QColor(color).name()
    elif isinstance(color, str):
        # 检查是否是十六进制颜色
        if color.startswith('#'):
            hex_color = color
        else:
            # 尝试解析颜色名称
            qcolor = QColor(color)
            if qcolor.isValid():
                hex_color = qcolor.name()
            else:
                logger.error(f"无效的颜色名称: {color}")
                return
    else:
        logger.error(f"不支持的颜色类型: {type(color)}")
        return
    
    # 设置主题色
    cfg.themeColor.value = hex_color
    # 保存配置
    qconfig.save()
    logger.info(f"主题色已设置为: {hex_color}")

def themeColor():
    """获取当前主题色
    
    Returns:
        str: 十六进制格式的主题色
    """
    try:
        # 获取当前主题色
        return cfg.themeColor.value
    except Exception as e:
        logger.error(f"获取主题色失败: {e}")
        # 返回默认主题色
        return "#3AF2FF"