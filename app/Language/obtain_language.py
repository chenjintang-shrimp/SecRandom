# ==================================================
# 默认内容文本配置
# ==================================================
"""
该模块包含所有应用程序内容文本的默认值配置
使用层级结构组织内容文本项，第一层为分类，第二层为具体内容文本项
"""
from app.tools.language_manager import get_language_data, set_current_language, preload_languages, get_language_manager
from app.tools.settings_access import readme_settings
from app.Language.ZH_CN import ZH_CN

from loguru import logger

# 获取当前语言设置
language = readme_settings("basic_settings", "language")

# 确保语言管理器已初始化
get_language_manager()

# 设置当前语言
set_current_language(language)

# 预加载当前语言
preload_languages()

# 获取语言数据
Language = get_language_data()  

# ==================================================
# 便捷函数
# ==================================================
def get_content_name(first_level_key: str, second_level_key: str):
    """根据键获取内容文本项的名称
    
    Args:
        first_level_key: 第一层的键
        second_level_key: 第二层的键
        
    Returns:
        内容文本项的名称，如果不存在则返回None
    """
    if first_level_key in Language:
        if second_level_key in Language[first_level_key]:
            # logger.debug(f"获取内容文本项: {first_level_key}.{second_level_key}")
            return Language[first_level_key][second_level_key]["name"]
    return None

def get_content_description(first_level_key: str, second_level_key: str):
    """根据键获取内容文本项的描述
    
    Args:
        first_level_key: 第一层的键
        second_level_key: 第二层的键
        
    Returns:
        内容文本项的描述，如果不存在则返回None
    """
    if first_level_key in Language:
        if second_level_key in Language[first_level_key]:
            # logger.debug(f"获取内容文本项描述: {first_level_key}.{second_level_key}")
            return Language[first_level_key][second_level_key]["description"]
    return None

def get_content_pushbutton_name(first_level_key: str, second_level_key: str):
    """根据键获取内容文本项的按钮名称
    
    Args:
        first_level_key: 第一层的键
        second_level_key: 第二层的键
        
    Returns:
        内容文本项的按钮名称，如果不存在则返回None
    """
    if first_level_key in Language:
        if second_level_key in Language[first_level_key]:
            # logger.debug(f"获取内容文本项按钮名称: {first_level_key}.{second_level_key}")
            return Language[first_level_key][second_level_key]["pushbutton_name"]
    return None

def get_content_switchbutton_name(first_level_key: str, second_level_key: str, is_enable: str):
    """根据键获取内容文本项的开关按钮名称
    
    Args:
        first_level_key: 第一层的键
        second_level_key: 第二层的键
        is_enable: 是否启用开关按钮("enable"或"disable")
        
    Returns:
        内容文本项的开关按钮名称，如果不存在则返回None
    """
    if first_level_key in Language:
        if second_level_key in Language[first_level_key]:
            # logger.debug(f"获取内容文本项开关按钮名称: {first_level_key}.{second_level_key}")
            return Language[first_level_key][second_level_key]["switchbutton_name"][is_enable]
    return None

def get_content_combo_name(first_level_key: str, second_level_key: str):
    """根据键获取内容文本项的下拉框内容
    
    Args:
        first_level_key: 第一层的键
        second_level_key: 第二层的键
        
    Returns:
        内容文本项的下拉框内容，如果不存在则返回None
    """
    if first_level_key in Language:
        if second_level_key in Language[first_level_key]:
            # logger.debug(f"获取内容文本项下拉框内容: {first_level_key}.{second_level_key}")
            return Language[first_level_key][second_level_key]["combo_items"]
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
    if first_level_key in Language:
        current = Language[first_level_key]
        if second_level_key in current:
            current = current[second_level_key]
            for key in keys:
                if isinstance(current, dict) and key in current:
                    # logger.debug(f"获取内容文本项: {first_level_key}.{second_level_key}.{key}")
                    current = current[key]
                else:
                    return None
            return current
    return None