# ==================================================
# 默认内容文本配置
# ==================================================
"""
该模块包含所有应用程序内容文本的默认值配置
使用层级结构组织内容文本项，第一层为分类，第二层为具体内容文本项
"""
from app.tools.path_utils import get_resources_path
from app.tools.settings_access import readme_settings
from app.Language.ZH_CN import ZH_CN
import json

language = readme_settings("basic_settings", "language")
if language == "ZH_CN" or language is None:
    Language = ZH_CN
else:
    # 获取语言文件路径并加载JSON内容
    language_file_path = get_resources_path("Language", f"{language}.json")
    try:
        with open(language_file_path, 'r', encoding='utf-8') as f:
            Language = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # 如果文件不存在或解析失败，回退到中文
        Language = ZH_CN  

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
                    current = current[key]
                else:
                    return None
            return current
    return None