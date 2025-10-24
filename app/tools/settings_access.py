# ==================================================
# 导入模块
# ==================================================
from qfluentwidgets import * 
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtNetwork import *

import json
import threading
from loguru import logger
from typing import Any, Dict, Optional

from app.tools.variable import *
from app.tools.path_utils import *
from app.tools.settings_default import *
from app.common.config import cfg

# ==================================================
# 设置缓存系统
# ==================================================
class SettingsCache:
    """设置缓存管理器 - 单例模式"""
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(SettingsCache, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._settings_cache: Dict[str, Dict[str, Any]] = {}
            self._cache_lock = threading.RLock()
            self._cache_initialized = False
            self._default_settings_cache = {}
            self._initialized = True
    
    def is_initialized(self) -> bool:
        """检查缓存是否已初始化"""
        return self._cache_initialized
    
    def initialize_cache(self, force: bool = False) -> None:
        """初始化设置缓存
        
        Args:
            force: 是否强制重新初始化缓存
        """
        if self._cache_initialized and not force:
            return
            
        with self._cache_lock:
            if self._cache_initialized and not force:
                return
                
            try:
                # 获取设置文件路径
                settings_path = get_settings_path()
                
                # 初始化缓存为空字典
                self._settings_cache = {}
                
                # 如果设置文件存在，加载到缓存
                if file_exists(settings_path):
                    with open_file(settings_path, 'r', encoding='utf-8') as f:
                        self._settings_cache = json.load(f)
                        logger.debug("设置文件已加载到缓存")
                
                self._cache_initialized = True
                logger.debug("设置缓存初始化完成")
                
            except Exception as e:
                logger.error(f"初始化设置缓存失败: {e}")
                self._settings_cache = {}
                self._cache_initialized = True  # 即使失败也标记为已初始化，避免重复尝试
    
    def get_setting(self, first_level_key: str, second_level_key: str) -> Any:
        """获取设置值
        
        Args:
            first_level_key: 第一层的键
            second_level_key: 第二层的键
            
        Returns:
            设置值，如果不存在则返回默认值
        """
        # 确保缓存已初始化
        if not self._cache_initialized:
            self.initialize_cache()
        
        with self._cache_lock:
            # 首先尝试从缓存获取
            if (first_level_key in self._settings_cache and 
                second_level_key in self._settings_cache[first_level_key]):
                value = self._settings_cache[first_level_key][second_level_key]
                logger.debug(f"从缓存读取: {first_level_key}.{second_level_key} = {value}")
                return value
            
            # 缓存中没有，从默认设置获取
            default_setting = _get_default_setting(first_level_key, second_level_key)
            if isinstance(default_setting, dict) and 'default_value' in default_setting:
                default_value = default_setting['default_value']
            else:
                default_value = default_setting
            
            logger.debug(f"使用默认设置: {first_level_key}.{second_level_key} = {default_value}")
            return default_value
    
    def update_setting(self, first_level_key: str, second_level_key: str, value: Any) -> bool:
        """更新设置值
        
        Args:
            first_level_key: 第一层的键
            second_level_key: 第二层的键
            value: 要写入的值（可以是任何类型）
            
        Returns:
            bool: 更新是否成功
        """
        try:
            # 确保缓存已初始化
            if not self._cache_initialized:
                self.initialize_cache()
            
            with self._cache_lock:
                # 更新缓存
                if first_level_key not in self._settings_cache:
                    self._settings_cache[first_level_key] = {}
                self._settings_cache[first_level_key][second_level_key] = value
                
                # 写入设置文件
                settings_path = get_settings_path()
                ensure_dir(settings_path.parent)
                with open_file(settings_path, 'w', encoding='utf-8') as f:
                    json.dump(self._settings_cache, f, ensure_ascii=False, indent=4)
                
                logger.debug(f"设置更新成功: {first_level_key}.{second_level_key} = {value}")
                return True
        except Exception as e:
            logger.error(f"设置更新失败: {e}")
            return False
    
    def refresh_cache(self) -> None:
        """刷新设置缓存 - 当外部修改了设置文件时调用"""
        self.initialize_cache(force=True)
    
    def preload_default_settings(self) -> None:
        """预加载默认设置到缓存中"""
        if self._default_settings_cache:
            return  # 已经预加载过
            
        try:
            default_settings = get_default_settings()
            with self._cache_lock:
                for first_level_key, first_level_value in default_settings.items():
                    if first_level_key not in self._settings_cache:
                        self._settings_cache[first_level_key] = {}
                    for second_level_key, second_level_value in first_level_value.items():
                        if second_level_key not in self._settings_cache[first_level_key]:
                            # 只缓存非None的默认值
                            if second_level_value["default_value"] is not None:
                                self._settings_cache[first_level_key][second_level_key] = second_level_value["default_value"]
            
            self._default_settings_cache = default_settings
            logger.debug("默认设置已预加载到缓存")
        except Exception as e:
            logger.error(f"预加载默认设置失败: {e}")

# 创建全局设置缓存实例
_settings_cache = SettingsCache()

# ==================================================
# 缓存管理辅助函数
# ==================================================
def initialize_settings_cache(force: bool = False) -> None:
    """初始化设置缓存
    
    Args:
        force: 是否强制重新初始化缓存
    """
    _settings_cache.initialize_cache(force)

def refresh_settings_cache() -> None:
    """刷新设置缓存 - 当外部修改了设置文件时调用"""
    _settings_cache.refresh_cache()

def preload_default_settings() -> None:
    """预加载默认设置到缓存中"""
    _settings_cache.preload_default_settings()

def is_settings_cache_initialized() -> bool:
    """检查设置缓存是否已初始化"""
    return _settings_cache.is_initialized()

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
    return _settings_cache.update_setting(first_level_key, second_level_key, value)

def readme_settings(first_level_key: str, second_level_key: str):
    """读取设置
    
    Args:
        first_level_key: 第一层的键
        second_level_key: 第二层的键
        
    Returns:
        设置值，如果不存在则返回默认值
    """
    return _settings_cache.get_setting(first_level_key, second_level_key)

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

