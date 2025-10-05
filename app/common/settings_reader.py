"""
设置文件读取器 - 提供一次性读取所有设置文件的功能

该模块提供统一的方法来读取应用程序中的所有设置文件，
并将它们整合到一个统一的字典中，方便其他模块使用。
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, Union
from loguru import logger

from app.common.path_utils import path_manager, open_file


class SettingsReader:
    """设置文件读取器 - 一次性读取所有设置文件"""
    
    def __init__(self):
        """初始化设置文件读取器"""
        self.settings_cache = {}
        self.enc_set_path = path_manager.get_enc_set_path()
        self.settings_files = self._get_all_settings_files()
    
    def _get_all_settings_files(self) -> Dict[str, Path]:
        """获取所有设置文件的路径
        
        Returns:
            设置文件名到路径的映射字典
        """
        settings_dir = path_manager.get_settings_path().parent
        settings_files = {}
        
        # 定义所有设置文件及其对应的逻辑名称
        file_mappings = {
            "Settings.json": "settings",
            "custom_settings.json": "custom_settings",
            "config.json": "config",
            "voice_engine.json": "voice_engine",
            "CleanupTimes.json": "cleanup_times",
            "ForegroundSoftware.json": "foreground_software",
            "guide_complete.json": "guide_complete",
            "plugin_settings.json": "plugin_settings",
            "time_settings.json": "time_settings",
            "vocabulary_pk_settings.json": "vocabulary_pk_settings"
        }
        
        # 检查每个文件是否存在
        for filename, logical_name in file_mappings.items():
            file_path = settings_dir / filename
            if path_manager.file_exists(file_path):
                settings_files[logical_name] = file_path
            else:
                logger.error(f"设置文件不存在: {file_path}")
        
        # 添加安全设置文件的特殊处理
        if path_manager.file_exists(self.enc_set_path):
            settings_files["password_settings"] = self.enc_set_path
        else:
            logger.error(f"安全设置文件不存在: {self.enc_set_path}")
        
        return settings_files
    
    def read_all_settings(self, force_refresh: bool = False) -> Dict[str, Any]:
        """一次性读取所有设置文件
        
        Args:
            force_refresh: 是否强制刷新缓存
            
        Returns:
            包含所有设置项的字典
        """
        if not force_refresh and self.settings_cache:
            # logger.debug("使用缓存的设置数据")
            return self.settings_cache
        
        # logger.info("开始读取所有设置文件")
        all_settings = {}
        
        try:
            # 读取每个设置文件
            for logical_name, file_path in self.settings_files.items():
                try:
                    with open_file(file_path, 'r', encoding='utf-8') as f:
                        settings_data = json.load(f)
                        all_settings[logical_name] = settings_data
                        # logger.debug(f"成功读取设置文件: {logical_name}")
                except Exception as e:
                    logger.error(f"读取设置文件失败 {logical_name}: {str(e)}")
                    # 添加空字典以保持结构完整
                    all_settings[logical_name] = {}
                    
                    # 如果是安全设置文件读取失败，提供更详细的错误信息
                    if logical_name == "password_settings":
                        logger.error(f"安全设置文件读取失败，可能是文件损坏或权限不足: {file_path}")
            
            # 缓存设置数据
            self.settings_cache = all_settings
            # logger.info("所有设置文件读取完成")
            
            return all_settings
            
        except Exception as e:
            logger.error(f"读取设置文件时发生错误: {str(e)}")
            return {}
    
    def get_settings_by_category(self, category: str, force_refresh: bool = False) -> Dict[str, Any]:
        """根据分类获取设置
        
        Args:
            category: 设置分类名称
            force_refresh: 是否强制刷新缓存
            
        Returns:
            指定分类的设置项
        """
        all_settings = self.read_all_settings(force_refresh)
        
        # 根据advanced_settings.py中的分类逻辑处理
        if category in ["foundation", "pumping_people", "instant_draw", "pumping_reward", "history", "channel", "position", "update_channel"]:
            # 这些分类都在Settings.json文件中
            if "settings" in all_settings:
                settings_data = all_settings["settings"]
                
                if category == "channel":
                    # channel是根级别的字符串
                    return {"channel": settings_data.get("channel", "")}
                elif category == "position":
                    # position是根级别的对象
                    return {"position": settings_data.get("position", {})}
                elif category == "update_channel":
                    # update_channel是根级别的字符串
                    return {"update_channel": settings_data.get("update_channel", "stable")}
                else:
                    # 其他分类是嵌套对象
                    return {category: settings_data.get(category, {})}
        
        elif category in ["fixed_url", "personal", "floating_window", "roll_call", "reward", "program_functionality", "sidebar", "tray"]:
            # 这些分类都在custom_settings.json文件中
            if "custom_settings" in all_settings:
                settings_data = all_settings["custom_settings"]
                return {category: settings_data.get(category, {})}
        
        elif category == "voice_engine":
            # voice_engine设置
            if "voice_engine" in all_settings:
                return {"voice_engine": all_settings["voice_engine"]}
        
        elif category == "config":
            # config设置
            if "config" in all_settings:
                return all_settings["config"]
        
        elif category == "CleanupTimes":
            # CleanupTimes设置
            if "cleanup_times" in all_settings:
                return {"CleanupTimes": all_settings["cleanup_times"].get("cleanuptimes", {})}
        
        elif category == "foreground_software":
            # ForegroundSoftware设置
            if "foreground_software" in all_settings:
                return all_settings["foreground_software"]
        
        elif category == "time_settings":
            # time_settings设置
            if "time_settings" in all_settings:
                return {"time_settings": all_settings["time_settings"]}
        
        elif category == "password_settings":
            # password_settings设置（使用已读取的安全设置数据）
            if "password_settings" in all_settings:
                return {"password_settings": all_settings["password_settings"]}
            else:
                # 如果缓存中没有，尝试直接读取文件
                if path_manager.file_exists(self.enc_set_path):
                    try:
                        with open_file(self.enc_set_path, 'r', encoding='utf-8') as f:
                            security_data = json.load(f)
                            return {"password_settings": security_data}
                    except Exception as e:
                        logger.error(f"读取安全设置文件失败: {str(e)}")
                        return {"password_settings": {}}
                else:
                    logger.error(f"安全设置文件不存在: {self.enc_set_path}")
                    return {"password_settings": {}}
        
        # 其他分类直接返回
        if category in all_settings:
            return {category: all_settings[category]}
        
        logger.error(f"未找到设置分类: {category}")
        return {}
    
    def get_setting_value(self, category: str, key: str, default: Any = None, force_refresh: bool = False) -> Any:
        """获取特定设置项的值
        
        Args:
            category: 设置分类名称
            key: 设置项键名
            default: 默认值
            force_refresh: 是否强制刷新缓存
            
        Returns:
            设置项的值
        """
        category_settings = self.get_settings_by_category(category, force_refresh)
        
        # 处理特殊分类
        if category in ["channel", "position", "CleanupTimes", "update_channel"]:
            # 这些分类的键名就是分类名
            if category in category_settings:
                return category_settings[category].get(key, default)
        
        # 处理config分类的特殊情况
        if category == "config":
            # config设置可能有多个分区
            for section_name, section_data in category_settings.items():
                if key in section_data:
                    return section_data[key]
            return default
        
        # 处理普通分类
        if category in category_settings and key in category_settings[category]:
            return category_settings[category][key]
        
        return default
    
    def refresh_cache(self):
        """刷新设置缓存"""
        self.settings_cache = {}
        self.read_all_settings()
    
    def get_settings_summary(self) -> Dict[str, int]:
        """获取设置文件的摘要信息
        
        Returns:
            设置文件摘要信息，包含每个文件的设置项数量
        """
        all_settings = self.read_all_settings()
        summary = {}
        
        for logical_name, settings_data in all_settings.items():
            # 计算设置项数量
            count = self._count_settings(settings_data)
            summary[logical_name] = count
        
        return summary
    
    def _count_settings(self, settings_data: Dict[str, Any], parent_key: str = "") -> int:
        """递归计算设置项数量
        
        Args:
            settings_data: 设置数据
            parent_key: 父级键名
            
        Returns:
            设置项数量
        """
        count = 0
        
        for key, value in settings_data.items():
            if isinstance(value, dict):
                # 递归计算嵌套字典
                count += self._count_settings(value, f"{parent_key}.{key}" if parent_key else key)
            else:
                count += 1
        
        return count


# 创建全局设置读取器实例
settings_reader = SettingsReader()


# 便捷函数
def get_all_settings(force_refresh: bool = False) -> Dict[str, Any]:
    """获取所有设置的便捷函数
    
    Args:
        force_refresh: 是否强制刷新缓存
        
    Returns:
        包含所有设置项的字典
    """
    return settings_reader.read_all_settings(force_refresh)


def get_settings_by_category(category: str, force_refresh: bool = False) -> Dict[str, Any]:
    """根据分类获取设置的便捷函数
    
    Args:
        category: 设置分类名称
        force_refresh: 是否强制刷新缓存
        
    Returns:
        指定分类的设置项
    """
    return settings_reader.get_settings_by_category(category, force_refresh)


def get_setting_value(category: str, key: str, default: Any = None, force_refresh: bool = False) -> Any:
    """获取特定设置项值的便捷函数
    
    Args:
        category: 设置分类名称
        key: 设置项键名
        default: 默认值
        force_refresh: 是否强制刷新缓存
        
    Returns:
        设置项的值
    """
    return settings_reader.get_setting_value(category, key, default, force_refresh)


def refresh_settings_cache():
    """刷新设置缓存的便捷函数"""
    settings_reader.refresh_cache()


def get_settings_summary() -> Dict[str, int]:
    """获取设置文件摘要信息的便捷函数
    
    Returns:
        设置文件摘要信息
    """
    return settings_reader.get_settings_summary()


def update_settings(category: str, settings_data: Dict[str, Any]) -> bool:
    """更新指定分类的设置
    
    Args:
        category: 设置分类名称
        settings_data: 要更新的设置数据
        
    Returns:
        更新是否成功
    """
    try:
        # 确定要更新的文件
        if category in ["foundation", "pumping_people", "instant_draw", "pumping_reward", "history", "channel", "position", "update_channel"]:
            # 这些分类都在Settings.json文件中
            file_path = settings_reader.settings_files.get("settings")
            if not file_path:
                logger.error("Settings.json 文件不存在")
                return False
                
            # 读取现有设置
            with open_file(file_path, 'r', encoding='utf-8') as f:
                existing_settings = json.load(f)
            
            # 更新设置
            if category in ["channel", "position", "update_channel"]:
                # channel、position和update_channel是根级别的键
                existing_settings[category] = settings_data.get(category, {})
            else:
                # 其他分类是嵌套对象
                if category not in existing_settings:
                    existing_settings[category] = {}
                existing_settings[category].update(settings_data.get(category, {}))
                
        elif category in ["fixed_url", "personal", "floating_window", "roll_call", "reward", "program_functionality", "sidebar", "tray"]:
            # 这些分类都在custom_settings.json文件中
            file_path = settings_reader.settings_files.get("custom_settings")
            if not file_path:
                logger.error("custom_settings.json 文件不存在")
                return False
                
            # 读取现有设置
            with open_file(file_path, 'r', encoding='utf-8') as f:
                existing_settings = json.load(f)
            
            # 更新设置
            if category not in existing_settings:
                existing_settings[category] = {}
            existing_settings[category].update(settings_data.get(category, {}))
            
        elif category == "voice_engine":
            # voice_engine设置
            file_path = settings_reader.settings_files.get("voice_engine")
            if not file_path:
                logger.error("voice_engine.json 文件不存在")
                return False
                
            # 读取现有设置
            with open_file(file_path, 'r', encoding='utf-8') as f:
                existing_settings = json.load(f)
            
            # 更新设置
            existing_settings.update(settings_data.get("voice_engine", {}))
            
        elif category == "config":
            # config设置
            file_path = settings_reader.settings_files.get("config")
            if not file_path:
                logger.error("config.json 文件不存在")
                return False
                
            # 读取现有设置
            with open_file(file_path, 'r', encoding='utf-8') as f:
                existing_settings = json.load(f)
            
            # 更新设置
            existing_settings.update(settings_data)
            
        elif category == "CleanupTimes":
            # CleanupTimes设置
            file_path = settings_reader.settings_files.get("cleanup_times")
            if not file_path:
                logger.error("CleanupTimes.json 文件不存在")
                return False
                
            # 读取现有设置
            with open_file(file_path, 'r', encoding='utf-8') as f:
                existing_settings = json.load(f)
            
            # 更新设置
            if "cleanuptimes" not in existing_settings:
                existing_settings["cleanuptimes"] = {}
            existing_settings["cleanuptimes"].update(settings_data.get("CleanupTimes", {}))
            
        elif category == "foreground_software":
            # ForegroundSoftware设置
            file_path = settings_reader.settings_files.get("foreground_software")
            if not file_path:
                logger.error("ForegroundSoftware.json 文件不存在")
                return False
                
            # 读取现有设置
            with open_file(file_path, 'r', encoding='utf-8') as f:
                existing_settings = json.load(f)
            
            # 更新设置
            existing_settings.update(settings_data)
            
        elif category == "password_settings":
            # password_settings设置（使用enc_set_path）
            file_path = settings_reader.enc_set_path
            if not path_manager.file_exists(file_path):
                logger.error(f"安全设置文件不存在: {file_path}")
                return False
                
            # 读取现有设置
            try:
                with open_file(file_path, 'r', encoding='utf-8') as f:
                    existing_settings = json.load(f)
            except Exception as e:
                logger.error(f"读取安全设置文件失败: {str(e)}")
                existing_settings = {}
            
            # 更新设置
            existing_settings.update(settings_data.get("password_settings", {}))
            
        else:
            logger.error(f"不支持的设置分类: {category}")
            return False
        
        # 保存更新后的设置
        with open_file(file_path, 'w', encoding='utf-8') as f:
            json.dump(existing_settings, f, indent=4, ensure_ascii=False)
        
        # 刷新缓存
        settings_reader.refresh_cache()
        
        # logger.info(f"成功更新 {category} 分类设置")
        return True
        
    except Exception as e:
        logger.error(f"更新 {category} 分类设置失败: {str(e)}")
        return False