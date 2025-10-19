# ==================================================
# 默认设置配置
# ==================================================
"""
该模块包含所有应用程序设置的默认值配置
使用层级结构组织设置项，第一层为分类，第二层为具体设置项
"""

import json

from app.tools.variable import *
from app.tools.path_utils import *
from app.tools.settings_default_storage import *

Language = DEFAULT_LANGUAGE

# ==================================================
# 便捷函数
# ==================================================
def get_default_settings():
    """获取所有默认设置
    
    Returns:
        dict: 包含所有默认设置的层级字典
    """
    return DEFAULT_SETTINGS

def get_default_setting(first_level_key: str, second_level_key: str):
    """根据键获取指定的默认设置值
    
    Args:
        first_level_key: 第一层的键
        second_level_key: 第二层的键
        
    Returns:
        默认设置值，如果不存在则返回None
    """
    if first_level_key in DEFAULT_SETTINGS:
        if second_level_key in DEFAULT_SETTINGS[first_level_key]:
            return DEFAULT_SETTINGS[first_level_key][second_level_key]["default_value"]
    return None

def get_setting_name(first_level_key: str, second_level_key: str):
    """根据键获取设置项的名称
    
    Args:
        first_level_key: 第一层的键
        second_level_key: 第二层的键
        
    Returns:
        设置项的名称，如果不存在则返回None
    """
    if first_level_key in DEFAULT_SETTINGS:
        if second_level_key in DEFAULT_SETTINGS[first_level_key]:
            return DEFAULT_SETTINGS[first_level_key][second_level_key][Language]["name"]
    return None

def get_setting_description(first_level_key: str, second_level_key: str):
    """根据键获取设置项的描述
    
    Args:
        first_level_key: 第一层的键
        second_level_key: 第二层的键
        
    Returns:
        设置项的描述，如果不存在则返回None
    """
    if first_level_key in DEFAULT_SETTINGS:
        if second_level_key in DEFAULT_SETTINGS[first_level_key]:
            return DEFAULT_SETTINGS[first_level_key][second_level_key][Language]["description"]
    return None

def get_setting_pushbutton_name(first_level_key: str, second_level_key: str):
    """根据键获取设置项的按钮名称
    
    Args:
        first_level_key: 第一层的键
        second_level_key: 第二层的键
        
    Returns:
        设置项的按钮名称，如果不存在则返回None
    """
    if first_level_key in DEFAULT_SETTINGS:
        if second_level_key in DEFAULT_SETTINGS[first_level_key]:
            return DEFAULT_SETTINGS[first_level_key][second_level_key][Language]["pushbutton_name"]
    return None

def get_setting_switchbutton_name(first_level_key: str, second_level_key: str, is_enable: str):
    """根据键获取设置项的开关按钮名称
    
    Args:
        first_level_key: 第一层的键
        second_level_key: 第二层的键
        is_enable: 是否启用开关按钮("enable"或"disable")
        
    Returns:
        设置项的开关按钮名称，如果不存在则返回None
    """
    if first_level_key in DEFAULT_SETTINGS:
        if second_level_key in DEFAULT_SETTINGS[first_level_key]:
            return DEFAULT_SETTINGS[first_level_key][second_level_key][Language]["switchbutton_name"][is_enable]
    return None

def get_setting_combo_name(first_level_key: str, second_level_key: str):
    """根据键获取设置项的下拉框内容
    
    Args:
        first_level_key: 第一层的键
        second_level_key: 第二层的键
        
    Returns:
        设置项的下拉框内容，如果不存在则返回None
    """
    if first_level_key in DEFAULT_SETTINGS:
        if second_level_key in DEFAULT_SETTINGS[first_level_key]:
            return DEFAULT_SETTINGS[first_level_key][second_level_key][Language]["combo_items"]
    return None

def get_any_position_value(first_level_key: str, second_level_key: str, *keys):
    """根据层级键获取任意位置的值
    
    Args:
        first_level_key: 第一层的键
        second_level_key: 第二层的键
        *keys: 后续任意层级的键
        
    Returns:
        指定位置的值，如果不存在则返回None
    """
    if first_level_key in DEFAULT_SETTINGS:
        current = DEFAULT_SETTINGS[first_level_key]
        if second_level_key in current:
            current = current[second_level_key]
            for key in keys:
                if isinstance(current, dict) and key in current:
                    current = current[key]
                else:
                    return None
            return current
    return None

# ==================================================
# 设置文件管理相关函数
# ==================================================
def manage_settings_file():
    """管理设置文件，确保其存在且完整
    
    该函数会执行以下操作：
    1. 如果设置文件不存在，创建带有默认值的设置文件
    2. 如果设置文件存在但缺少某些设置项，补全这些设置项
    3. 如果设置文件中有多余的设置项，移除这些设置项
    """
    try:
        settings_file = get_settings_path()
        ensure_dir(settings_file.parent)
        
        default_settings = get_default_settings()
        
        if not file_exists(settings_file):
            logger.info(f"设置文件不存在，创建默认设置文件: {settings_file}")
            flat_settings = {}
            for first_level_key, first_level_value in default_settings.items():
                flat_settings[first_level_key] = {}
                for second_level_key, second_level_value in first_level_value.items():
                    # 如果默认值为 None，则不写入设置文件
                    if second_level_value["default_value"] is not None:
                        flat_settings[first_level_key][second_level_key] = second_level_value["default_value"]
            
            with open_file(settings_file, 'w', encoding='utf-8') as f:
                json.dump(flat_settings, f, indent=4, ensure_ascii=False)
            return
        
        try:
            with open_file(settings_file, 'r', encoding='utf-8') as f:
                current_settings = json.load(f)
        except Exception as e:
            logger.error(f"读取设置文件失败: {e}，将重新创建默认设置文件")
            flat_settings = {}
            for first_level_key, first_level_value in default_settings.items():
                flat_settings[first_level_key] = {}
                for second_level_key, second_level_value in first_level_value.items():
                    # 如果默认值为 None，则不写入设置文件
                    if second_level_value["default_value"] is not None:
                        flat_settings[first_level_key][second_level_key] = second_level_value["default_value"]
            
            with open_file(settings_file, 'w', encoding='utf-8') as f:
                json.dump(flat_settings, f, indent=4, ensure_ascii=False)
            return
        
        # 检查并更新设置文件
        settings_updated = False
        updated_settings = {}
        
        # 处理现有设置项
        for first_level_key, first_level_value in current_settings.items():
            if first_level_key in default_settings:
                updated_settings[first_level_key] = {}
                for second_level_key, second_level_value in first_level_value.items():
                    if second_level_key in default_settings[first_level_key]:
                        # 检查现有值是否已经是简单的值（非字典）
                        if not isinstance(second_level_value, dict):
                            # 如果值为 null，则不写入更新后的设置
                            if second_level_value is not None:
                                # 如果已经是简单值，直接使用
                                updated_settings[first_level_key][second_level_key] = second_level_value
                        else:
                            # 如果是字典结构，提取 default_value
                            if "default_value" in second_level_value:
                                # 如果 default_value 为 null，则不写入更新后的设置
                                if second_level_value["default_value"] is not None:
                                    updated_settings[first_level_key][second_level_key] = second_level_value["default_value"]
                            else:
                                # 如果没有 default_value，使用整个值（但检查是否为 null）
                                if second_level_value is not None:
                                    updated_settings[first_level_key][second_level_key] = second_level_value
        
        # 添加缺失的设置项
        for first_level_key, first_level_value in default_settings.items():
            if first_level_key not in updated_settings:
                updated_settings[first_level_key] = {}
            
            for second_level_key, second_level_value in first_level_value.items():
                if second_level_key not in updated_settings[first_level_key]:
                    # 如果默认值为 None，则不添加到设置文件
                    if second_level_value["default_value"] is not None:
                        updated_settings[first_level_key][second_level_key] = second_level_value["default_value"]
                        settings_updated = True
                        logger.debug(f"添加缺失的设置项: {first_level_key}.{second_level_key} = {second_level_value['default_value']}")
        
        # 移除多余的设置项
        for first_level_key in list(current_settings.keys()):
            if first_level_key not in default_settings:
                logger.debug(f"移除多余的设置分类: {first_level_key}")
                settings_updated = True
                if first_level_key in updated_settings:
                    del updated_settings[first_level_key]
                continue
                
            for second_level_key in list(current_settings[first_level_key].keys()):
                if second_level_key not in default_settings[first_level_key]:
                    logger.debug(f"移除多余的设置项: {first_level_key}.{second_level_key}")
                    settings_updated = True
                    if first_level_key in updated_settings and second_level_key in updated_settings[first_level_key]:
                        del updated_settings[first_level_key][second_level_key]
        
        if settings_updated:
            logger.debug("设置文件已更新")
            with open_file(settings_file, 'w', encoding='utf-8') as f:
                json.dump(updated_settings, f, indent=4, ensure_ascii=False)
        else:
            logger.debug("设置文件已是最新，无需更新")
            
    except Exception as e:
        logger.error(f"管理设置文件时发生错误: {e}")