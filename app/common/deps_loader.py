import os
import sys
import subprocess
import site
from loguru import logger
from pathlib import Path
from PyQt5.QtWidgets import QMessageBox

class PluginDependencyLoader:
    """插件依赖加载器 - 负责运行时自动安装缺失的库"""
    
    def __init__(self, app_root_dir):
        """
        初始化依赖加载器
        
        Args:
            app_root_dir: 应用程序根目录
        """
        self.app_root_dir = Path(app_root_dir)
        self.wheels_dir = self.app_root_dir / "resource" / "wheels"
        self.installed_plugins = set()
    
    def load_plugin_dependencies(self, plugin_dir, plugin_name, parent_widget=None):
        """
        加载插件依赖，自动安装缺失的库
        
        Args:
            plugin_dir: 插件目录路径
            plugin_name: 插件名称
            parent_widget: 父窗口组件，用于显示错误对话框
            
        Returns:
            bool: 依赖加载是否成功
        """
        plugin_dir = Path(plugin_dir)
        requirements_file = plugin_dir / "__requirements__.txt"
        site_packages_dir = plugin_dir / "site-packages"
        
        # 检查是否已经处理过此插件的依赖
        if plugin_name in self.installed_plugins:
            return True
        
        # 如果插件没有依赖文件，直接返回成功
        if not requirements_file.exists():
            self.installed_plugins.add(plugin_name)
            return True
        
        # 创建插件专属的site-packages目录
        site_packages_dir.mkdir(exist_ok=True)
        
        # 将插件site-packages添加到sys.path
        if str(site_packages_dir) not in sys.path:
            sys.path.insert(0, str(site_packages_dir))
        
        # 读取依赖文件
        try:
            with open(requirements_file, 'r', encoding='utf-8') as f:
                requirements = f.read().strip()
            
            if not requirements:
                self.installed_plugins.add(plugin_name)
                return True
                
        except Exception as e:
            self._show_error_dialog(
                f"读取插件 {plugin_name} 的依赖文件失败: {str(e)}",
                parent_widget
            )
            return False
        
        # 检查并安装依赖
        success = self._install_dependencies(
            requirements, 
            site_packages_dir, 
            plugin_name, 
            parent_widget
        )
        
        if success:
            self.installed_plugins.add(plugin_name)
            
        return success
    
    def _install_dependencies(self, requirements, target_dir, plugin_name, parent_widget):
        """
        安装插件依赖
        
        Args:
            requirements: 依赖文件内容
            target_dir: 目标安装目录
            plugin_name: 插件名称
            parent_widget: 父窗口组件
            
        Returns:
            bool: 安装是否成功
        """
        try:
            # 创建临时requirements文件
            temp_requirements_file = target_dir / "temp_requirements.txt"
            with open(temp_requirements_file, 'w', encoding='utf-8') as f:
                f.write(requirements)
            
            # 构建pip安装命令
            cmd = [
                sys.executable, "-m", "pip", "install",
                "--target", str(target_dir),
                "-r", str(temp_requirements_file),
                "--quiet",  # 静默安装，减少输出
                "--disable-pip-version-check"
            ]
            
            # 如果存在离线wheel缓存，添加--find-links参数
            if self.wheels_dir.exists():
                cmd.extend(["--find-links", str(self.wheels_dir)])
            
            # 执行pip安装
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding='utf-8'
            )
            
            # 删除临时文件
            if temp_requirements_file.exists():
                temp_requirements_file.unlink()
            
            # 检查安装结果
            if result.returncode == 0:
                logger.info(f"插件 {plugin_name} 依赖安装成功")
                return True
            else:
                error_msg = f"插件 {plugin_name} 依赖安装失败:\n{result.stderr}"
                logger.error(error_msg)
                self._show_error_dialog(error_msg, parent_widget)
                return False
                
        except Exception as e:
            error_msg = f"插件 {plugin_name} 依赖安装过程中发生异常: {str(e)}"
            logger.error(error_msg)
            self._show_error_dialog(error_msg, parent_widget)
            return False
    
    def _show_error_dialog(self, message, parent_widget):
        """
        显示错误对话框
        
        Args:
            message: 错误消息
            parent_widget: 父窗口组件
        """
        if parent_widget:
            QMessageBox.critical(
                parent_widget,
                "依赖安装失败",
                message,
                QMessageBox.Ok
            )
        else:
            logger.error(f"依赖安装错误: {message}")
    
    def get_plugin_site_packages(self, plugin_dir):
        """
        获取插件的site-packages目录路径
        
        Args:
            plugin_dir: 插件目录路径
            
        Returns:
            Path: site-packages目录路径
        """
        return Path(plugin_dir) / "site-packages"
    
    def is_dependencies_installed(self, plugin_dir):
        """
        检查插件依赖是否已安装
        
        Args:
            plugin_dir: 插件目录路径
            
        Returns:
            bool: 依赖是否已安装
        """
        requirements_file = Path(plugin_dir) / "__requirements__.txt"
        site_packages_dir = Path(plugin_dir) / "site-packages"
        
        # 如果没有依赖文件，认为已安装
        if not requirements_file.exists():
            return True
            
        # 如果site-packages目录不存在，认为未安装
        if not site_packages_dir.exists():
            return False
            
        # 这里可以添加更复杂的依赖检查逻辑
        # 目前简单认为site-packages目录存在即为已安装
        return True


# 全局依赖加载器实例
_dependency_loader = None


def get_dependency_loader(app_root_dir=None):
    """
    获取全局依赖加载器实例
    
    Args:
        app_root_dir: 应用程序根目录，仅在首次调用时需要
        
    Returns:
        PluginDependencyLoader: 依赖加载器实例
    """
    global _dependency_loader
    
    if _dependency_loader is None:
        if app_root_dir is None:
            raise ValueError("首次调用必须提供app_root_dir参数")
        _dependency_loader = PluginDependencyLoader(app_root_dir)
        
    return _dependency_loader


def load_plugin_dependencies(plugin_dir, plugin_name, parent_widget=None):
    """
    便捷函数：加载插件依赖
    
    Args:
        plugin_dir: 插件目录路径
        plugin_name: 插件名称
        parent_widget: 父窗口组件
        
    Returns:
        bool: 依赖加载是否成功
    """
    loader = get_dependency_loader()
    return loader.load_plugin_dependencies(plugin_dir, plugin_name, parent_widget)