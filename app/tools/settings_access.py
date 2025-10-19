# ==================================================
# 导入模块
# ==================================================
from qfluentwidgets import * 
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtNetwork import *

import json
from loguru import logger
from typing import Any

from app.tools.variable import *
from app.tools.path_utils import *
from app.tools.settings_default import *
from app.common.config import cfg

# ==================================================
# 设置访问函数
# ==================================================
def update_settings(first_level_key: str, second_level_key: str, value: Any):
    """更新设置
    
    Args:
        first_level_key: 第一层的键
        second_level_key: 第二层的键
        value: 要写入的值（可以是任何类型）
        
    Returns:
        bool: 更新是否成功
    """
    try:
        # 获取设置文件路径
        settings_path = get_settings_path()
        
        # 确保设置目录存在
        ensure_dir(settings_path.parent)
        
        # 读取现有设置
        settings_data = {}
        if file_exists(settings_path):
            with open_file(settings_path, 'r', encoding='utf-8') as f:
                settings_data = json.load(f)
        
        # 更新设置
        if first_level_key not in settings_data:
            settings_data[first_level_key] = {}
        
        # 直接保存值，不保存嵌套结构
        settings_data[first_level_key][second_level_key] = value
        
        # 写入设置文件
        with open_file(settings_path, 'w', encoding='utf-8') as f:
            json.dump(settings_data, f, ensure_ascii=False, indent=4)
        
        logger.debug(f"设置更新成功: {first_level_key}.{second_level_key} = {value}")
    except Exception as e:
        logger.error(f"设置更新失败: {e}")

def readme_settings(first_level_key: str, second_level_key: str):
    """读取设置
    
    Args:
        first_level_key: 第一层的键
        second_level_key: 第二层的键
        
    Returns:
        设置值，如果不存在则返回默认值
    """
    try:
        # 获取设置文件路径
        settings_path = get_settings_path()
        
        # 如果设置文件存在，尝试读取设置
        if file_exists(settings_path):
            with open_file(settings_path, 'r', encoding='utf-8') as f:
                settings_data = json.load(f)
                
                # 检查设置是否存在
                if (first_level_key in settings_data and 
                    second_level_key in settings_data[first_level_key]):
                    value = settings_data[first_level_key][second_level_key]
                    logger.debug(f"从设置文件读取: {first_level_key}.{second_level_key} = {value}")
                    return value
        
        # 如果设置不存在或文件不存在，从默认设置获取
        default_setting = _get_default_setting(first_level_key, second_level_key)
        # 从嵌套结构中提取 default_value
        if isinstance(default_setting, dict) and 'default_value' in default_setting:
            default_value = default_setting['default_value']
        else:
            default_value = default_setting
        logger.debug(f"使用默认设置: {first_level_key}.{second_level_key} = {default_value}")
        return default_value
    except Exception as e:
        logger.error(f"读取设置失败: {e}")
        # 发生错误时返回默认值
        default_setting = _get_default_setting(first_level_key, second_level_key)
        if isinstance(default_setting, dict) and 'default_value' in default_setting:
            return default_setting['default_value']
        return default_setting

def _get_default_setting(first_level_key: str, second_level_key: str):
    """获取默认设置值
    
    Args:
        first_level_key: 第一层的键
        second_level_key: 第二层的键
        
    Returns:
        默认设置值
    """
    # 从settings_default模块获取默认值
    default_settings = get_default_settings()
    
    # 检查设置是否存在
    if first_level_key in default_settings:
        if second_level_key in default_settings[first_level_key]:
            setting_info = default_settings[first_level_key][second_level_key]
            # 如果是嵌套结构，提取 default_value
            if isinstance(setting_info, dict) and 'default_value' in setting_info:
                return setting_info['default_value']
            # 否则直接返回值
            return setting_info
    
    return None

