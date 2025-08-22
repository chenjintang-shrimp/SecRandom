"""
路径工具模块 - 提供跨平台的路径处理功能

该模块提供统一的路径处理方法，解决Linux兼容性问题。
所有相对路径都应通过此模块转换为绝对路径。
"""

import os
import sys
from pathlib import Path
from typing import Union, Optional
from loguru import logger


class PathManager:
    """路径管理器 - 统一管理应用程序中的所有路径"""
    
    def __init__(self):
        self._app_root = self._get_app_root()
        logger.info(f"应用程序根目录: {self._app_root}")
    
    def _get_app_root(self) -> Path:
        """获取应用程序根目录"""
        if getattr(sys, 'frozen', False):
            # 打包后的可执行文件
            return Path(sys.executable).parent
        else:
            # 开发环境
            return Path(__file__).parent.parent.parent
    
    def get_absolute_path(self, relative_path: Union[str, Path]) -> Path:
        """将相对路径转换为绝对路径
        
        Args:
            relative_path: 相对于app目录的路径，如 'app/resource/file.json'
            
        Returns:
            绝对路径
        """
        if isinstance(relative_path, str):
            relative_path = Path(relative_path)
        
        # 如果已经是绝对路径，直接返回
        if relative_path.is_absolute():
            return relative_path
        
        # 拼接为绝对路径
        absolute_path = self._app_root / relative_path
        return absolute_path
    
    def ensure_directory_exists(self, path: Union[str, Path]) -> Path:
        """确保目录存在，如果不存在则创建
        
        Args:
            path: 目录路径（相对或绝对）
            
        Returns:
            绝对路径
        """
        absolute_path = self.get_absolute_path(path)
        absolute_path.mkdir(parents=True, exist_ok=True)
        return absolute_path
    
    def get_settings_path(self, filename: str = "Settings.json") -> Path:
        """获取设置文件路径
        
        Args:
            filename: 设置文件名
            
        Returns:
            设置文件的绝对路径
        """
        return self.get_absolute_path(f"app/Settings/{filename}")
    
    def get_resource_path(self, resource_type: str, filename: str) -> Path:
        """获取资源文件路径
        
        Args:
            resource_type: 资源类型，如 'reward', 'list', 'images'等
            filename: 文件名
            
        Returns:
            资源文件的绝对路径
        """
        return self.get_absolute_path(f"app/resource/{resource_type}/{filename}")
    
    def get_temp_path(self, filename: str) -> Path:
        """获取临时文件路径
        
        Args:
            filename: 临时文件名
            
        Returns:
            临时文件的绝对路径
        """
        return self.get_absolute_path(f"app/resource/Temp/{filename}")
    
    def get_plugin_path(self, filename: str = "") -> Path:
        """获取插件相关路径
        
        Args:
            filename: 插件文件名或目录名
            
        Returns:
            插件相关路径的绝对路径
        """
        if filename:
            return self.get_absolute_path(f"app/plugin/{filename}")
        else:
            return self.get_absolute_path("app/plugin")
    
    def get_cache_path(self, filename: str) -> Path:
        """获取缓存文件路径
        
        Args:
            filename: 缓存文件名
            
        Returns:
            缓存文件的绝对路径
        """
        return self.get_absolute_path(f"app/cache/{filename}")
    
    def get_voice_engine_path(self) -> Path:
        """获取语音引擎配置文件路径
        
        Returns:
            语音引擎配置文件的绝对路径
        """
        return self.get_absolute_path("app/Settings/voice_engine.json")
    
    def get_enc_set_path(self) -> Path:
        """获取加密设置文件路径
        
        Returns:
            加密设置文件的绝对路径
        """
        return self.get_absolute_path("app/SecRandom/enc_set.json")
    
    def get_guide_complete_path(self) -> Path:
        """获取引导完成标记文件路径
        
        Returns:
            引导完成标记文件的绝对路径
        """
        return self.get_absolute_path("app/Settings/guide_complete.json")
    
    def get_cleanup_times_path(self) -> Path:
        """获取清理时间记录文件路径
        
        Returns:
            清理时间记录文件的绝对路径
        """
        return self.get_absolute_path("app/Settings/CleanupTimes.json")
    
    def get_font_path(self, filename: str = "HarmonyOS_Sans_SC_Bold.ttf") -> Path:
        """获取字体文件路径
        
        Args:
            filename: 字体文件名
            
        Returns:
            字体文件的绝对路径
        """
        return self.get_absolute_path(f"app/resource/font/{filename}")
    
    def get_icon_path(self, icon_name: str, theme: str = "dark") -> Path:
        """获取图标文件路径
        
        Args:
            icon_name: 图标名称
            theme: 主题，'dark' 或 'light'
            
        Returns:
            图标文件的绝对路径
        """
        suffix = "_light" if theme == "light" else "_dark"
        prefix = "light" if theme == "light" else "dark"
        return self.get_absolute_path(f"app/resource/assets/{prefix}/{icon_name}{suffix}.svg")
    
    def file_exists(self, path: Union[str, Path]) -> bool:
        """检查文件是否存在
        
        Args:
            path: 文件路径（相对或绝对）
            
        Returns:
            文件是否存在
        """
        absolute_path = self.get_absolute_path(path)
        return absolute_path.exists()
    
    def open_file(self, path: Union[str, Path], mode: str = "r", encoding: str = "utf-8"):
        """打开文件
        
        Args:
            path: 文件路径（相对或绝对）
            mode: 文件打开模式
            encoding: 文件编码
            
        Returns:
            文件对象
        """
        absolute_path = self.get_absolute_path(path)
        return open(absolute_path, mode, encoding=encoding)
    
    def remove_file(self, path: Union[str, Path]) -> bool:
        """删除文件
        
        Args:
            path: 文件路径（相对或绝对）
            
        Returns:
            删除是否成功
        """
        try:
            absolute_path = self.get_absolute_path(path)
            if absolute_path.exists():
                absolute_path.unlink()
                return True
            return False
        except Exception as e:
            logger.error(f"删除文件失败: {path}, 错误: {e}")
            return False


# 创建全局路径管理器实例
path_manager = PathManager()


# 便捷函数
def get_path(relative_path: Union[str, Path]) -> Path:
    """获取绝对路径的便捷函数
    
    Args:
        relative_path: 相对路径
        
    Returns:
        绝对路径
    """
    return path_manager.get_absolute_path(relative_path)


def ensure_dir(path: Union[str, Path]) -> Path:
    """确保目录存在的便捷函数
    
    Args:
        path: 目录路径
        
    Returns:
        绝对路径
    """
    return path_manager.ensure_directory_exists(path)


def file_exists(path: Union[str, Path]) -> bool:
    """检查文件是否存在的便捷函数
    
    Args:
        path: 文件路径
        
    Returns:
        文件是否存在
    """
    return path_manager.file_exists(path)


def open_file(path: Union[str, Path], mode: str = "r", encoding: str = "utf-8"):
    """打开文件的便捷函数
    
    Args:
        path: 文件路径
        mode: 文件打开模式
        encoding: 文件编码
        
    Returns:
        文件对象
    """
    return path_manager.open_file(path, mode, encoding)


def remove_file(path: Union[str, Path]) -> bool:
    """删除文件的便捷函数
    
    Args:
        path: 文件路径
        
    Returns:
        删除是否成功
    """
    return path_manager.remove_file(path)