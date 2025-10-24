# ==================================================
# 导入模块
# ==================================================
import os
import threading
from typing import Dict, Optional, Tuple
from loguru import logger
from PyQt6.QtGui import QFont, QFontDatabase
from PyQt6.QtCore import QObject, QTimer, pyqtSignal

from app.tools.path_utils import get_resources_path, file_exists
from app.tools.variable import FONT_CONFIG_MAP, DEFAULT_FONT_NAME_PRIMARY

# ==================================================
# 字体管理器类
# ==================================================
class FontManager(QObject):
    """字体管理器 - 单例模式，负责字体加载和管理"""
    
    # 定义信号，用于通知字体加载完成
    font_loaded = pyqtSignal(str, bool)  # 字体名称, 是否成功
    
    def __init__(self):
        super().__init__()
        self._loaded_fonts: Dict[str, Tuple[int, str]] = {}  # 字体名称 -> (字体ID, 字体家族)
        self._loading_fonts: Dict[str, bool] = {}  # 正在加载的字体
        self._font_lock = threading.RLock()
    
    def load_font_async(self, font_name: str) -> None:
        """异步加载字体
        
        Args:
            font_name: 字体名称
        """
        # 检查字体是否已加载或正在加载
        with self._font_lock:
            if font_name in self._loaded_fonts:
                self.font_loaded.emit(font_name, True)
                return
            
            if font_name in self._loading_fonts:
                return  # 已在加载中
        
        # 启动线程加载字体
        threading.Thread(
            target=self._load_font_thread,
            args=(font_name,),
            daemon=True
        ).start()
    
    def _load_font_thread(self, font_name: str) -> None:
        """在线程中加载字体
        
        Args:
            font_name: 字体名称
        """
        try:
            with self._font_lock:
                if font_name in self._loading_fonts:
                    return  # 已被其他线程加载
                
                self._loading_fonts[font_name] = True
            
            # 检查字体是否在配置映射表中
            if font_name not in FONT_CONFIG_MAP:
                logger.warning(f"字体 {font_name} 不在配置映射表中")
                with self._font_lock:
                    self._loading_fonts.pop(font_name, None)
                self.font_loaded.emit(font_name, False)
                return
            
            # 获取字体配置
            config = FONT_CONFIG_MAP[font_name]
            font_path = get_resources_path('font', config['filename'])
            
            # 检查字体文件是否存在
            if not font_path or not file_exists(font_path):
                logger.error(f"{config['display_name']}字体文件不存在: {font_path}")
                with self._font_lock:
                    self._loading_fonts.pop(font_name, None)
                self.font_loaded.emit(font_name, False)
                return
            
            # 加载字体文件
            font_id = QFontDatabase.addApplicationFont(str(font_path))
            
            if font_id >= 0:
                font_families = QFontDatabase.applicationFontFamilies(font_id)
                if font_families:
                    with self._font_lock:
                        self._loaded_fonts[font_name] = (font_id, font_families[0])
                        self._loading_fonts.pop(font_name, None)
                    logger.info(f"字体 {font_name} 加载成功")
                    self.font_loaded.emit(font_name, True)
                else:
                    logger.error(f"无法从字体文件获取字体家族: {font_path}")
                    with self._font_lock:
                        self._loading_fonts.pop(font_name, None)
                    self.font_loaded.emit(font_name, False)
            else:
                logger.error(f"无法加载字体文件: {font_path}")
                with self._font_lock:
                    self._loading_fonts.pop(font_name, None)
                self.font_loaded.emit(font_name, False)
                
        except Exception as e:
            logger.error(f"加载字体 {font_name} 时发生异常: {e}")
            with self._font_lock:
                self._loading_fonts.pop(font_name, None)
            self.font_loaded.emit(font_name, False)
    
    def get_font(self, font_name: str, point_size: int = 12) -> QFont:
        """获取字体对象
        
        Args:
            font_name: 字体名称
            point_size: 字体大小
            
        Returns:
            QFont: 字体对象
        """
        # 如果字体未加载，尝试加载
        if font_name not in self._loaded_fonts:
            # 如果字体不在加载中，启动异步加载
            if font_name not in self._loading_fonts:
                self.load_font_async(font_name)
            
            # 返回默认字体
            return QFont(DEFAULT_FONT_NAME_PRIMARY, point_size)
        
        # 返回已加载的字体
        _, font_family = self._loaded_fonts[font_name]
        return QFont(font_family, point_size)
    
    def is_font_loaded(self, font_name: str) -> bool:
        """检查字体是否已加载
        
        Args:
            font_name: 字体名称
            
        Returns:
            bool: 是否已加载
        """
        with self._font_lock:
            return font_name in self._loaded_fonts
    
    def preload_fonts(self, font_names: list = None) -> None:
        """预加载常用字体
        
        Args:
            font_names: 要预加载的字体名称列表，如果为None则预加载默认字体
        """
        if font_names is None:
            font_names = [DEFAULT_FONT_NAME_PRIMARY]
        
        for font_name in font_names:
            if not self.is_font_loaded(font_name):
                self.load_font_async(font_name)

# 创建全局字体管理器实例 - 使用模块级变量实现单例模式
_font_manager = None
_font_manager_lock = threading.Lock()

def get_font_manager() -> FontManager:
    """获取全局字体管理器实例"""
    global _font_manager
    if _font_manager is None:
        with _font_manager_lock:
            if _font_manager is None:
                _font_manager = FontManager()
    return _font_manager

# ==================================================
# 字体管理辅助函数
# ==================================================
def load_font_async(font_name: str) -> None:
    """异步加载字体
    
    Args:
        font_name: 字体名称
    """
    get_font_manager().load_font_async(font_name)

def get_font(font_name: str, point_size: int = 12) -> QFont:
    """获取字体对象
    
    Args:
        font_name: 字体名称
        point_size: 字体大小
        
    Returns:
        QFont: 字体对象
    """
    return get_font_manager().get_font(font_name, point_size)

def is_font_loaded(font_name: str) -> bool:
    """检查字体是否已加载
    
    Args:
        font_name: 字体名称
        
    Returns:
        bool: 是否已加载
    """
    return get_font_manager().is_font_loaded(font_name)

def preload_fonts(font_names: list = None) -> None:
    """预加载常用字体
    
    Args:
        font_names: 要预加载的字体名称列表，如果为None则预加载默认字体
    """
    get_font_manager().preload_fonts(font_names)