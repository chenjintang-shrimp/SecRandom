# ==================================================
# 导入模块
# ==================================================
import os
import threading
from typing import Dict, Optional, Any
from loguru import logger
from PyQt6.QtCore import QObject, pyqtSignal

from app.tools.path_utils import get_resources_path
from app.tools.settings_access import readme_settings
from app.Language.ZH_CN import ZH_CN
import json

# ==================================================
# 语言管理器类
# ==================================================
class LanguageManager(QObject):
    """语言管理器 - 单例模式，负责语言文件加载和管理"""
    
    # 定义信号，用于通知语言加载完成
    language_loaded = pyqtSignal(str, bool)  # 语言代码, 是否成功
    
    def __init__(self):
        super().__init__()
        self._loaded_languages: Dict[str, Dict[str, Any]] = {}  # 语言代码 -> 语言数据
        self._loading_languages: Dict[str, bool] = {}  # 正在加载的语言
        self._current_language: Optional[str] = None
        self._language_lock = threading.RLock()
        
        # 默认加载中文
        self._loaded_languages["ZH_CN"] = ZH_CN
    
    def load_language_async(self, language_code: str) -> None:
        """异步加载语言文件
        
        Args:
            language_code: 语言代码
        """
        # 检查语言是否已加载或正在加载
        with self._language_lock:
            if language_code in self._loaded_languages:
                self.language_loaded.emit(language_code, True)
                return
            
            if language_code in self._loading_languages:
                return  # 已在加载中
        
        # 启动线程加载语言
        threading.Thread(
            target=self._load_language_thread,
            args=(language_code,),
            daemon=True
        ).start()
    
    def _load_language_thread(self, language_code: str) -> None:
        """在线程中加载语言文件
        
        Args:
            language_code: 语言代码
        """
        try:
            with self._language_lock:
                if language_code in self._loading_languages:
                    return  # 已被其他线程加载
                
                self._loading_languages[language_code] = True
            
            # 获取语言文件路径
            language_file_path = get_resources_path("Language", f"{language_code}.json")
            
            # 检查语言文件是否存在
            if not language_file_path or not os.path.exists(language_file_path):
                logger.warning(f"语言文件不存在: {language_file_path}")
                with self._language_lock:
                    self._loading_languages.pop(language_code, None)
                self.language_loaded.emit(language_code, False)
                return
            
            # 加载语言文件
            with open(language_file_path, 'r', encoding='utf-8') as f:
                language_data = json.load(f)
                
                with self._language_lock:
                    self._loaded_languages[language_code] = language_data
                    self._loading_languages.pop(language_code, None)
                
                logger.info(f"语言 {language_code} 加载成功")
                self.language_loaded.emit(language_code, True)
                
        except Exception as e:
            logger.error(f"加载语言 {language_code} 时发生异常: {e}")
            with self._language_lock:
                self._loading_languages.pop(language_code, None)
            self.language_loaded.emit(language_code, False)
    
    def get_language_data(self, language_code: Optional[str] = None) -> Dict[str, Any]:
        """获取语言数据
        
        Args:
            language_code: 语言代码，如果为None则使用当前语言
            
        Returns:
            语言数据字典
        """
        # 如果没有指定语言代码，使用当前语言
        if language_code is None:
            language_code = self._current_language
            
        # 如果当前语言未设置，从设置中获取
        if language_code is None:
            language_code = readme_settings("basic_settings", "language")
            if language_code is None:
                language_code = "ZH_CN"
            self._current_language = language_code
        
        # 如果语言未加载，尝试加载
        if language_code not in self._loaded_languages:
            # 如果语言不在加载中，启动异步加载
            if language_code not in self._loading_languages:
                self.load_language_async(language_code)
            
            # 返回默认中文
            return ZH_CN
        
        # 返回已加载的语言
        return self._loaded_languages[language_code]
    
    def set_current_language(self, language_code: str) -> None:
        """设置当前语言
        
        Args:
            language_code: 语言代码
        """
        self._current_language = language_code
        
        # 如果语言未加载，异步加载
        if language_code not in self._loaded_languages:
            self.load_language_async(language_code)
    
    def is_language_loaded(self, language_code: str) -> bool:
        """检查语言是否已加载
        
        Args:
            language_code: 语言代码
            
        Returns:
            bool: 是否已加载
        """
        with self._language_lock:
            return language_code in self._loaded_languages
    
    def preload_languages(self, language_codes: list = None) -> None:
        """预加载常用语言
        
        Args:
            language_codes: 要预加载的语言代码列表，如果为None则预加载当前语言
        """
        if language_codes is None:
            # 获取当前语言设置
            current_language = readme_settings("basic_settings", "language")
            if current_language:
                language_codes = [current_language]
            else:
                language_codes = ["ZH_CN"]
        
        for language_code in language_codes:
            if not self.is_language_loaded(language_code):
                self.load_language_async(language_code)

# 创建全局语言管理器实例 - 使用模块级变量实现单例模式
_language_manager = None
_language_manager_lock = threading.Lock()

def get_language_manager() -> LanguageManager:
    """获取全局语言管理器实例"""
    global _language_manager
    if _language_manager is None:
        with _language_manager_lock:
            if _language_manager is None:
                _language_manager = LanguageManager()
    return _language_manager

# ==================================================
# 语言管理辅助函数
# ==================================================
def load_language_async(language_code: str) -> None:
    """异步加载语言文件
    
    Args:
        language_code: 语言代码
    """
    get_language_manager().load_language_async(language_code)

def get_language_data(language_code: Optional[str] = None) -> Dict[str, Any]:
    """获取语言数据
    
    Args:
        language_code: 语言代码，如果为None则使用当前语言
        
    Returns:
        语言数据字典
    """
    return get_language_manager().get_language_data(language_code)

def set_current_language(language_code: str) -> None:
    """设置当前语言
    
    Args:
        language_code: 语言代码
    """
    get_language_manager().set_current_language(language_code)

def is_language_loaded(language_code: str) -> bool:
    """检查语言是否已加载
    
    Args:
        language_code: 语言代码
        
    Returns:
        bool: 是否已加载
    """
    return get_language_manager().is_language_loaded(language_code)

def preload_languages(language_codes: list = None) -> None:
    """预加载常用语言
    
    Args:
        language_codes: 要预加载的语言代码列表，如果为None则预加载当前语言
    """
    get_language_manager().preload_languages(language_codes)

def set_current_language(language_code: str) -> None:
    """设置当前语言
    
    Args:
        language_code: 语言代码
    """
    _language_manager.set_current_language(language_code)

def is_language_loaded(language_code: str) -> bool:
    """检查语言是否已加载
    
    Args:
        language_code: 语言代码
        
    Returns:
        bool: 是否已加载
    """
    return _language_manager.is_language_loaded(language_code)

def preload_languages(language_codes: list = None) -> None:
    """预加载常用语言
    
    Args:
        language_codes: 要预加载的语言代码列表，如果为None则预加载当前语言
    """
    _language_manager.preload_languages(language_codes)