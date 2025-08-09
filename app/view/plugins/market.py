from qfluentwidgets import *
from qfluentwidgets import FluentIcon as FIF
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import os
import json
import shutil
import subprocess
import sys
import tempfile
import urllib.request
import zipfile
from datetime import datetime
from loguru import logger

from packaging.version import Version
from app.common.config import get_theme_icon, load_custom_font, VERSION


class MarketPluginButtonGroup(QWidget):
    """插件广场的插件按钮组"""
    def __init__(self, plugin_info, parent=None):
        super().__init__(parent)
        self.plugin_info = plugin_info
        
        # 主水平布局
        self.hBoxLayout = QHBoxLayout(self)
        self.hBoxLayout.setContentsMargins(10, 10, 10, 10)
        self.hBoxLayout.setSpacing(10)
        
        # 检查插件安装状态
        self.installed_version = self._check_installed_version()
        
        # 根据安装状态创建不同的按钮
        self.actionButton = PushButton(self._get_button_text(), self)
        self.actionButton.setIcon(self._get_button_icon())
        self.actionButton.clicked.connect(lambda: self.on_action_clicked())
        
        # 查看说明按钮
        self.readmeButton = PushButton("查看说明", self)
        self.readmeButton.setIcon(FIF.DOCUMENT)
        self.readmeButton.clicked.connect(lambda: self.on_readme_clicked())
        
        # 添加到布局
        self.hBoxLayout.addWidget(self.actionButton)
        self.hBoxLayout.addWidget(self.readmeButton)
        self.hBoxLayout.addStretch(1)
        
        # 设置固定高度
        self.setFixedHeight(50)
        
        # 检查插件版本兼容性并设置操作按钮状态
        self._update_action_button_state()

    def _get_repo_name_from_url(self, url):
        """从GitHub URL中提取仓库名称"""
        if "github.com" in url:
            parts = url.rstrip("/").split("/")
            if len(parts) >= 5:
                return parts[-1]
        return None
    
    def _check_installed_version(self):
        """检查插件是否已安装及版本"""
        plugin_dir = "app/plugin"
        if not os.path.exists(plugin_dir):
            return None
        
        # 查找已安装的插件
        for item in os.listdir(plugin_dir):
            item_path = os.path.join(plugin_dir, item)
            if not os.path.isdir(item_path):
                continue
            
            plugin_json_path = os.path.join(item_path, "plugin.json")
            if not os.path.exists(plugin_json_path):
                continue
            
            try:
                with open(plugin_json_path, 'r', encoding='utf-8') as f:
                    plugin_config = json.load(f)
                
                # 检查是否是同一个插件（通过名称或URL匹配）
                if (plugin_config.get("name") == self.plugin_info.get("name") or 
                    plugin_config.get("url") == self.plugin_info.get("url")):
                    return plugin_config.get("version")
                    
            except Exception as e:
                logger.error(f"检查已安装插件版本失败: {e}")
                continue
        
        return None
    
    def _check_plugin_version_compatibility(self):
        """检查插件版本与应用程序的兼容性"""
        try:
            # 获取插件要求的最低应用版本
            plugin_ver = self.plugin_info.get("plugin_ver")
            if not plugin_ver:
                # 如果没有设置插件版本要求，默认兼容
                logger.info(f"插件 {self.plugin_info['name']} 未设置插件版本要求")
                return True
            
            # 获取当前应用版本
            current_version = VERSION.lstrip('v')  # 移除v前缀
            required_version = plugin_ver.lstrip('v')  # 移除v前缀
            
            # 比较版本号
            if Version(current_version) >= Version(required_version):
                logger.info(f"插件 {self.plugin_info['name']} 版本兼容: 当前版本 {current_version} >= 最低要求 {required_version}")
                return True
            else:
                logger.warning(f"插件 {self.plugin_info['name']} 版本不兼容: 当前版本 {current_version} < 最低要求 {required_version}")
                return False
                
        except Exception as e:
            logger.error(f"检查插件版本兼容性失败: {e}")
            # 出错时默认禁用以确保安全
            return False
    
    def _is_plugin_in_market(self, market_plugins=None):
        """检查本地插件是否在插件广场中存在"""
        try:
            # 获取插件名称和URL
            plugin_name = self.plugin_info.get("name")
            plugin_url = self.plugin_info.get("url")
            
            if not plugin_name and not plugin_url:
                logger.warning(f"插件缺少名称和URL信息")
                return False
            
            # 如果没有传入市场插件列表，则获取（保持向后兼容）
            if market_plugins is None:
                plugin_list_url = "https://raw.githubusercontent.com/SECTL/SecRandom-market/master/Plugins/plugin_list.json"
                try:
                    with urllib.request.urlopen(plugin_list_url) as response:
                        market_plugins = json.loads(response.read().decode('utf-8'))
                except Exception as e:
                    logger.error(f"获取插件广场列表失败: {e}")
                    # 如果获取失败，默认允许显示（避免因网络问题导致所有插件都不显示）
                    return True
            
            # 检查插件是否在广场中
            for market_plugin_key, market_plugin_info in market_plugins.items():
                # 跳过示例条目
                if market_plugin_key in ["其他插件...", "您的插件仓库名称"]:
                    continue
                
                # 通过名称或URL匹配
                if (plugin_name and market_plugin_info.get("name") == plugin_name) or \
                   (plugin_url and market_plugin_info.get("url") == plugin_url):
                    logger.info(f"插件 {plugin_name} 在插件广场中存在")
                    return True
            
            logger.warning(f"插件 {plugin_name} 不在插件广场中")
            return False
            
        except Exception as e:
            logger.error(f"检查插件是否在插件广场中失败: {e}")
            # 出错时默认允许显示（避免因检查失败导致插件不显示）
            return True
    
    def _update_action_button_state(self):
        """根据版本兼容性更新操作按钮状态"""
        try:
            is_compatible = self._check_plugin_version_compatibility()
            
            if is_compatible:
                self.actionButton.setEnabled(True)
                logger.info(f"插件 {self.plugin_info['name']} 版本兼容，操作按钮已启用")
            else:
                self.actionButton.setEnabled(False)
                logger.warning(f"插件 {self.plugin_info['name']} 版本不兼容，操作按钮已禁用")
                
        except Exception as e:
            logger.error(f"更新操作按钮状态失败: {e}")
            self.actionButton.setEnabled(False)
    
    def _get_button_text(self):
        """根据安装状态获取按钮文本"""
        if self.installed_version is None:
            return "安装"
        elif self.installed_version == self.plugin_info.get("version"):
            return "卸载"
        else:
            return "更新"
    
    def _get_button_icon(self):
        """根据安装状态获取按钮图标"""
        if self.installed_version is None:
            return FIF.ADD
        elif self.installed_version == self.plugin_info.get("version"):
            return FIF.DELETE
        else:
            return FIF.SYNC
    
    def _download_plugin(self, url, branch, target_dir):
        """下载插件"""
        try:
            # 确保目标目录存在
            os.makedirs(target_dir, exist_ok=True)
            
            # 创建临时文件路径
            zip_path = os.path.join(target_dir, "plugin.zip")
            
            # 从URL中提取owner和repo名称
            if "github.com" in url:
                parts = url.rstrip("/").split("/")
                if len(parts) >= 5:
                    owner = parts[-2]
                    repo = parts[-1]
                    
                    # 获取插件版本
                    plugin_version = self.plugin_info.get("version", "latest")
                    
                    # 构建GitHub Releases API URL
                    if plugin_version == "latest":
                        releases_url = f"https://api.github.com/repos/{owner}/{repo}/releases/latest"
                    else:
                        releases_url = f"https://api.github.com/repos/{owner}/{repo}/releases/tags/{plugin_version}"
                    
                    logger.info(f"正在获取发布信息: {releases_url}")
                    
                    # 获取发布信息
                    try:
                        with urllib.request.urlopen(releases_url) as response:
                            release_info = json.loads(response.read().decode('utf-8'))
                    except Exception as e:
                        logger.error(f"获取发布信息失败: {e}")
                        release_info = None
                    
                    # 只有在成功获取发布信息时才处理assets
                    if release_info:
                        # 获取发布包的下载URL
                        assets = release_info.get("assets", [])
                        if assets:
                            # 优先选择.zip文件
                            zip_asset = None
                            for asset in assets:
                                if asset["name"].endswith(".zip"):
                                    zip_asset = asset
                                    break
                            
                            if zip_asset:
                                download_url = zip_asset["browser_download_url"]
                            else:
                                # 如果没有zip文件，使用第一个资源
                                download_url = assets[0]["browser_download_url"]
                    else:
                        logger.error(f"获取插件发布信息失败: {release_info}")
                        return False


            logger.info(f"正在下载插件: {download_url}")
            
            urllib.request.urlretrieve(download_url, zip_path)
            
            # 解压文件
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(target_dir)
            
            # 清理临时文件
            if os.path.exists(zip_path):
                os.remove(zip_path)
            
            logger.info(f"插件下载成功: {target_dir}")
            return True
            
        except Exception as e:
            logger.error(f"下载插件失败: {e}")
            return False
    
    def on_action_clicked(self):
        """处理操作按钮点击事件"""
        button_text = self.actionButton.text()
        plugin_name = self.plugin_info.get("name")
        
        # 首先检查版本兼容性（仅对安装和更新操作）
        if button_text in ["安装", "更新"]:
            if not self._check_plugin_version_compatibility():
                # 如果版本不兼容，显示提示信息
                required_version = self.plugin_info.get("plugin_ver", "未知版本")
                
                dialog = Dialog(
                    "版本不兼容", 
                    f"该插件需要应用版本 {required_version} 或更高版本才能安装。\n当前版本: {VERSION}\n请更新应用后再试。", 
                    self
                )
                dialog.yesButton.setText("确定")
                dialog.cancelButton.hide()
                dialog.buttonLayout.insertStretch(1)
                dialog.exec()
                return
        
        if button_text == "安装":
            self._install_plugin()
        elif button_text == "卸载":
            self._uninstall_plugin()
        elif button_text == "更新":
            self._update_plugin()
    
    def _install_plugin(self):
        """安装插件"""
        plugin_name = self.plugin_info.get("name")
        url = self.plugin_info.get("url")
        branch = self.plugin_info.get("branch", "main")
        
        # 创建确认对话框
        install_dialog = Dialog("确认安装", f"确定要安装插件 {plugin_name} 吗？", self)
        install_dialog.yesButton.setText("安装")
        install_dialog.cancelButton.setText("取消")
        
        if install_dialog.exec():
            logger.info(f"开始安装插件: {plugin_name}")
            
            # 创建插件目录
            plugin_dir = "app/plugin"
            os.makedirs(plugin_dir, exist_ok=True)
            
            # 生成插件文件夹名称（使用仓库名称）
            repo_name = self._get_repo_name_from_url(url)
            if repo_name:
                folder_name = repo_name
            else:
                folder_name = plugin_name.lower().replace(" ", "_")
            target_dir = os.path.join(plugin_dir, folder_name)
            
            # 下载插件
            if self._download_plugin(url, branch, target_dir):
                # 检查是否有plugin.json文件
                plugin_json_path = os.path.join(target_dir, "plugin.json")
                if os.path.exists(plugin_json_path):
                    try:
                        with open(plugin_json_path, 'r', encoding='utf-8') as f:
                            plugin_config = json.load(f)
                        # 更新按钮状态
                        self.installed_version = plugin_config.get("version")
                        self.actionButton.setText(self._get_button_text())
                        self.actionButton.setIcon(self._get_button_icon())
                        
                        success_dialog = Dialog("安装成功", f"插件 {plugin_name} 安装成功！", self)
                        success_dialog.yesButton.setText("确定")
                        success_dialog.cancelButton.hide()
                        success_dialog.buttonLayout.insertStretch(1)
                        success_dialog.exec()
                            
                    except Exception as e:
                        logger.error(f"安装插件配置失败: {e}")
                        # 清理失败的安装
                        if os.path.exists(target_dir):
                            shutil.rmtree(target_dir)
                        
                        error_dialog = Dialog("安装失败", f"插件 {plugin_name} 安装失败: {str(e)}", self)
                        error_dialog.yesButton.setText("确定")
                        error_dialog.cancelButton.hide()
                        error_dialog.buttonLayout.insertStretch(1)
                        error_dialog.exec()
                else:
                    logger.error("未找到plugin.json文件")
                    # 清理失败的安装
                    if os.path.exists(target_dir):
                        shutil.rmtree(target_dir)
                    
                    error_dialog = Dialog("安装失败", f"插件 {plugin_name} 缺少plugin.json文件", self)
                    error_dialog.yesButton.setText("确定")
                    error_dialog.cancelButton.hide()
                    error_dialog.buttonLayout.insertStretch(1)
                    error_dialog.exec()
            else:
                error_dialog = Dialog("安装失败", f"插件 {plugin_name} 下载失败", self)
                error_dialog.yesButton.setText("确定")
                error_dialog.cancelButton.hide()
                error_dialog.buttonLayout.insertStretch(1)
                error_dialog.exec()
    
    def _uninstall_plugin(self):
        """卸载插件"""
        plugin_name = self.plugin_info.get("name")
        
        # 创建确认对话框
        uninstall_dialog = Dialog("确认卸载", f"确定要卸载插件 {plugin_name} 吗？此操作将删除插件文件夹且无法恢复。", self)
        uninstall_dialog.yesButton.setText("卸载")
        uninstall_dialog.cancelButton.setText("取消")
        
        if uninstall_dialog.exec():
            logger.info(f"开始卸载插件: {plugin_name}")
            
            # 查找插件目录
            plugin_dir = "app/plugin"
            if not os.path.exists(plugin_dir):
                error_dialog = Dialog("卸载失败", f"插件目录不存在", self)
                error_dialog.yesButton.setText("确定")
                error_dialog.cancelButton.hide()
                error_dialog.buttonLayout.insertStretch(1)
                error_dialog.exec()
                return
            
            # 查找已安装的插件
            for item in os.listdir(plugin_dir):
                item_path = os.path.join(plugin_dir, item)
                if not os.path.isdir(item_path):
                    continue
                
                plugin_json_path = os.path.join(item_path, "plugin.json")
                if not os.path.exists(plugin_json_path):
                    continue
                
                try:
                    with open(plugin_json_path, 'r', encoding='utf-8') as f:
                        plugin_config = json.load(f)
                    
                    # 检查是否是同一个插件
                    if plugin_config.get("name") == plugin_name:
                        # 删除插件文件夹
                        shutil.rmtree(item_path)
                        logger.info(f"成功卸载插件: {item_path}")
                        
                        # 更新按钮状态
                        self.installed_version = None
                        self.actionButton.setText(self._get_button_text())
                        self.actionButton.setIcon(self._get_button_icon())
                        
                        success_dialog = Dialog("卸载成功", f"插件 {plugin_name} 卸载成功！", self)
                        success_dialog.yesButton.setText("确定")
                        success_dialog.cancelButton.hide()
                        success_dialog.buttonLayout.insertStretch(1)
                        success_dialog.exec()
                        return
                        
                except Exception as e:
                    logger.error(f"卸载插件失败: {e}")
                    continue
            
            error_dialog = Dialog("卸载失败", f"未找到插件 {plugin_name}", self)
            error_dialog.yesButton.setText("确定")
            error_dialog.cancelButton.hide()
            error_dialog.buttonLayout.insertStretch(1)
            error_dialog.exec()
    
    def _update_plugin(self):
        """更新插件"""
        plugin_name = self.plugin_info.get("name")
        
        # 创建确认对话框
        update_dialog = Dialog("确认更新", f"确定要更新插件 {plugin_name} 吗？", self)
        update_dialog.yesButton.setText("更新")
        update_dialog.cancelButton.setText("取消")
        
        if update_dialog.exec():
            logger.info(f"开始更新插件: {plugin_name}")
            
            # 先卸载旧版本
            self._uninstall_plugin_internal()
            
            # 再安装新版本
            url = self.plugin_info.get("url")
            branch = self.plugin_info.get("branch", "main")
            
            # 创建插件目录
            plugin_dir = "app/plugin"
            os.makedirs(plugin_dir, exist_ok=True)
            
            # 生成插件文件夹名称（使用仓库名称）
            repo_name = self._get_repo_name_from_url(url)
            if repo_name:
                folder_name = repo_name
            else:
                folder_name = plugin_name.lower().replace(" ", "_")
            target_dir = os.path.join(plugin_dir, folder_name)
            
            # 下载插件
            if self._download_plugin(url, branch, target_dir):
                # 检查是否有plugin.json文件
                plugin_json_path = os.path.join(target_dir, "plugin.json")
                if os.path.exists(plugin_json_path):
                    try:
                        with open(plugin_json_path, 'r', encoding='utf-8') as f:
                            plugin_config = json.load(f)
                        
                        
                        # 更新按钮状态
                        self.installed_version = plugin_config.get("version")
                        self.actionButton.setText(self._get_button_text())
                        self.actionButton.setIcon(self._get_button_icon())
                        
                        success_dialog = Dialog("更新成功", f"插件 {plugin_name} 更新成功！", self)
                        success_dialog.yesButton.setText("确定")
                        success_dialog.cancelButton.hide()
                        success_dialog.buttonLayout.insertStretch(1)
                        success_dialog.exec()
                            
                    except Exception as e:
                        logger.error(f"更新插件配置失败: {e}")
                        # 清理失败的安装
                        if os.path.exists(target_dir):
                            shutil.rmtree(target_dir)
                        
                        error_dialog = Dialog("更新失败", f"插件 {plugin_name} 更新失败: {str(e)}", self)
                        error_dialog.yesButton.setText("确定")
                        error_dialog.cancelButton.hide()
                        error_dialog.buttonLayout.insertStretch(1)
                        error_dialog.exec()
                else:
                    logger.error("未找到plugin.json文件")
                    # 清理失败的安装
                    if os.path.exists(target_dir):
                        shutil.rmtree(target_dir)
                    
                    error_dialog = Dialog("更新失败", f"插件 {plugin_name} 缺少plugin.json文件", self)
                    error_dialog.yesButton.setText("确定")
                    error_dialog.cancelButton.hide()
                    error_dialog.buttonLayout.insertStretch(1)
                    error_dialog.exec()
            else:
                error_dialog = Dialog("更新失败", f"插件 {plugin_name} 下载失败", self)
                error_dialog.yesButton.setText("确定")
                error_dialog.cancelButton.hide()
                error_dialog.buttonLayout.insertStretch(1)
                error_dialog.exec()
    
    def _uninstall_plugin_internal(self):
        """内部卸载插件（不显示对话框）"""
        plugin_name = self.plugin_info.get("name")
        plugin_dir = "app/plugin"
        
        if not os.path.exists(plugin_dir):
            return False
        
        # 查找已安装的插件
        for item in os.listdir(plugin_dir):
            item_path = os.path.join(plugin_dir, item)
            if not os.path.isdir(item_path):
                continue
            
            plugin_json_path = os.path.join(item_path, "plugin.json")
            if not os.path.exists(plugin_json_path):
                continue
            
            try:
                with open(plugin_json_path, 'r', encoding='utf-8') as f:
                    plugin_config = json.load(f)
                
                # 检查是否是同一个插件
                if plugin_config.get("name") == plugin_name:
                    # 删除插件文件夹
                    shutil.rmtree(item_path)
                    logger.info(f"成功卸载插件: {item_path}")
                    return True
                    
            except Exception as e:
                logger.error(f"卸载插件失败: {e}")
                continue
        
        return False
    
    def on_readme_clicked(self):
        """处理查看说明按钮点击事件"""
        # 对于插件广场，显示插件描述信息
        plugin_name = self.plugin_info.get("name")
        description = self.plugin_info.get("description", "暂无描述")
        version = self.plugin_info.get("version", "未知版本")
        author = self.plugin_info.get("author", "未知作者")
        url = self.plugin_info.get("url", "")
        
        info_text = f"**插件名称**: {plugin_name}\n\n"
        info_text += f"**版本**: {version}\n\n"
        info_text += f"**作者**: {author}\n\n"
        info_text += f"**描述**: {description}\n\n"
        if url:
            info_text += f"**仓库地址**: [{url}]({url})\n\n"
        
        if self.installed_version:
            info_text += f"**已安装版本**: {self.installed_version}\n\n"
        
        # 创建信息对话框
        info_dialog = Dialog(f"插件信息 - {plugin_name}", info_text, self)
        info_dialog.yesButton.setText("确定")
        info_dialog.cancelButton.hide()
        info_dialog.buttonLayout.insertStretch(1)
        info_dialog.exec()


class PluginMarketPage(GroupHeaderCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("插件广场")
        self.setBorderRadius(8)
        self.settings_file = "app/Settings/plugin_settings.json"
        
        # 插件市场仓库信息
        self.market_repo_url = "https://github.com/SECTL/SecRandom-market"
        self.plugin_list_url = "https://raw.githubusercontent.com/SECTL/SecRandom-market/master/Plugins/plugin_list.json"
        
        # 初始化时加载插件列表
        self.load_market_plugins()
    
    def fetch_plugin_list(self):
        """从远程仓库获取插件列表"""
        try:
            logger.info(f"正在获取插件列表: {self.plugin_list_url}")
            
            # 发送HTTP请求获取插件列表
            with urllib.request.urlopen(self.plugin_list_url) as response:
                data = response.read().decode('utf-8')
                plugin_list = json.loads(data)
            
            logger.info(f"成功获取插件列表，共 {len(plugin_list)} 个插件")
            return plugin_list
            
        except Exception as e:
            logger.error(f"获取插件列表失败: {e}")
            return {}
    
    def create_plugin_button_group(self, plugin_info):
        """创建插件按钮组"""
        button_group = MarketPluginButtonGroup(plugin_info, self)
        return button_group
    
    def load_market_plugins(self):
        """加载插件市场中的插件列表"""
        # 获取插件列表
        plugin_list = self.fetch_plugin_list()
        
        if not plugin_list:
            # 显示无插件提示
            no_plugin_label = BodyLabel("无法获取插件列表，请检查网络连接", self)
            no_plugin_label.setAlignment(Qt.AlignCenter)
            self.addGroup(get_theme_icon("ic_fluent_cloud_download_20_filled"), "无法获取插件列表", "请检查网络连接后重试", no_plugin_label)
            return
        
        # 过滤掉示例条目
        filtered_plugins = {}
        for key, value in plugin_list.items():
            # 跳过"其他插件..."等示例条目
            if key in ["其他插件...", "您的插件仓库名称"]:
                continue
            
            # 检查必需字段
            required_fields = ["name", "version", "description", "author", "url", "branch"]
            if all(field in value for field in required_fields):
                filtered_plugins[key] = value
            else:
                logger.warning(f"插件 {key} 缺少必需字段，跳过")
        
        if not filtered_plugins:
            # 显示无有效插件提示
            no_plugin_label = BodyLabel("暂无可用插件", self)
            no_plugin_label.setAlignment(Qt.AlignCenter)
            self.addGroup(get_theme_icon("ic_fluent_extensions_20_filled"), "暂无可用插件", "插件市场中暂无可用插件", no_plugin_label)
            return
        
        # 一次性获取插件广场列表，避免重复请求
        market_plugins = None
        try:
            plugin_list_url = "https://raw.githubusercontent.com/SECTL/SecRandom-market/master/Plugins/plugin_list.json"
            with urllib.request.urlopen(plugin_list_url) as response:
                market_plugins = json.loads(response.read().decode('utf-8'))
            logger.info(f"成功获取插件广场列表，共 {len(market_plugins)} 个插件")
        except Exception as e:
            logger.error(f"获取插件广场列表失败: {e}")
            # 如果获取失败，设置为None，让每个插件自己处理
            market_plugins = None
        
        # 为每个插件创建按钮组
        for plugin_key, plugin_info in filtered_plugins.items():
            try:
                button_group = self.create_plugin_button_group(plugin_info)
                
                # 检查插件是否在插件广场中存在（传入已获取的列表）
                if button_group._is_plugin_in_market(market_plugins):
                    # 获取插件图标（使用默认图标）
                    icon = get_theme_icon("ic_fluent_extensions_20_filled")
                    
                    # 构建描述信息
                    description = plugin_info.get("description", "暂无描述")
                    version = plugin_info.get("version", "未知版本")
                    author = plugin_info.get("author", "未知作者")
                    update_date = plugin_info.get("update_date", "未知")
                    
                    subtitle = f"版本: {version} | 作者: {author} | 更新: {update_date} | 仓库: {description}"

                    # 添加到界面
                    self.addGroup(icon, plugin_info["name"], subtitle, button_group)
                else:
                    logger.info(f"插件 {plugin_info.get('name')} 不在插件广场中，跳过显示")
                    button_group.deleteLater()
                    
            except Exception as e:
                logger.error(f"创建插件 {plugin_key} 的界面失败: {e}")
                continue
        
        logger.info(f"插件市场加载完成，共显示 {len(filtered_plugins)} 个插件")
    
    def refresh_plugin_list(self):
        """刷新插件列表"""
        logger.info("刷新插件列表")
        self.load_market_plugins()