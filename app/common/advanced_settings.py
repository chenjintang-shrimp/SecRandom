from ast import In
from shlex import join
from qfluentwidgets import *
from qfluentwidgets import FluentIcon as FIF
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

import json
import os
import sys
import platform
from pathlib import Path
from datetime import datetime
from loguru import logger

import winreg

from app.common.config import get_theme_icon, load_custom_font, is_dark_theme, VERSION
from app.common.path_utils import path_manager
from app.common.path_utils import open_file, ensure_dir


class advanced_settingsCard(GroupHeaderCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("高级设置")
        self.setBorderRadius(8)
        self.settings_file = path_manager.get_settings_path()
        self.default_settings = {
        }

        # 导出诊断数据按钮
        self.export_diagnostic_button = PushButton("导出诊断数据")
        self.export_diagnostic_button.clicked.connect(self.export_diagnostic_data)
        self.export_diagnostic_button.setFont(QFont(load_custom_font(), 12))

        # 导入设置按钮
        self.import_settings_button = PushButton("导入设置")
        self.import_settings_button.clicked.connect(self.import_settings)
        self.import_settings_button.setFont(QFont(load_custom_font(), 12))

        # 导出设置按钮
        self.export_settings_button = PushButton("导出设置")
        self.export_settings_button.clicked.connect(self.export_settings)
        self.export_settings_button.setFont(QFont(load_custom_font(), 12))

        # 数据管理设置
        self.addGroup(get_theme_icon("ic_fluent_group_20_filled"), "导出诊断数据", "生成并导出系统诊断信息用于技术支持", self.export_diagnostic_button)
        self.addGroup(get_theme_icon("ic_fluent_multiselect_ltr_20_filled"), "导入设置", "从配置文件恢复软件的各项设置参数", self.import_settings_button)
        self.addGroup(get_theme_icon("ic_fluent_multiselect_ltr_20_filled"), "导出设置", "将当前软件设置保存到配置文件中", self.export_settings_button)
        
    def export_diagnostic_data(self):
        """导出诊断数据到压缩文件"""
        # 首先显示安全确认对话框，告知用户将要导出敏感数据
        try:
            # 创建安全确认对话框
            confirm_box = Dialog(
                title='⚠️ 敏感数据导出确认',
                content=(
                    '您即将导出诊断数据，这些数据可能包含敏感信息：\n\n'
                    '📋 包含的数据类型：\n'
                    '• 点名名单数据、抽奖设置文件、历史记录文件\n'
                    '• 软件设置文件、系统日志文件\n\n'
                    '⚠️ 注意事项：\n'
                    '• 这些数据可能包含个人信息和使用记录\n'
                    '• 请妥善保管导出的压缩包文件\n'
                    '• 不要将导出文件分享给不可信的第三方\n'
                    '• 如不再需要，请及时删除导出的文件\n\n'
                    '确认要继续导出诊断数据吗？'
                ),
                parent=self
            )
            confirm_box.yesButton.setText('确认导出')
            confirm_box.cancelButton.setText('取消')
            confirm_box.setFont(QFont(load_custom_font(), 12))
            
            # 如果用户取消导出，则直接返回
            if not confirm_box.exec():
                logger.info("用户取消了诊断数据导出")
                InfoBar.info(
                    title='导出已取消',
                    content='诊断数据导出操作已取消',
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=3000,
                    parent=self
                )
                return
                
        except Exception as e:
            logger.error(f"创建安全确认对话框失败: {str(e)}")
            pass

        try:
            from app.common.path_utils import path_manager
            enc_set_file = path_manager.get_enc_set_path()
            with open_file(enc_set_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                logger.info("正在读取安全设置，准备执行导出诊断数据验证")

                if settings.get('hashed_set', {}).get('start_password_enabled', False) == True:
                    from app.common.password_dialog import PasswordDialog
                    dialog = PasswordDialog(self)
                    if dialog.exec_() != QDialog.Accepted:
                        logger.error("用户取消导出诊断数据操作，安全防御已解除")
                        return
        except Exception as e:
            logger.error(f"密码验证系统出错: {e}")
            return
            
        try:
            import zipfile
            from datetime import datetime
            
            # 让用户选择导出位置
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            default_filename = f"SecRandom_诊断数据_{timestamp}.zip"
            
            # 打开文件保存对话框，让用户选择导出位置
            zip_path, _ = QFileDialog.getSaveFileName(
                self,
                "选择诊断数据导出位置",
                default_filename,
                "压缩文件 (*.zip);;所有文件 (*.*)"
            )
            
            # 如果用户取消了选择，则直接返回
            if not zip_path:
                logger.info("用户取消了诊断数据导出位置选择")
                InfoBar.info(
                    title='导出已取消',
                    content='诊断数据导出操作已取消',
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=3000,
                    parent=self
                )
                return
            
            # 确保文件扩展名是.zip
            if not zip_path.lower().endswith('.zip'):
                zip_path += '.zip'
            
            # 需要导出的文件夹列表
            export_folders = [
                path_manager.get_resource_path('list'), 
                path_manager.get_resource_path('reward'),
                path_manager.get_resource_path('history'),
                path_manager._app_root / "app" / "settings",
                path_manager._app_root / "logs"
            ]

            app_dir = path_manager._app_root
            
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                exported_count = 0
                
                for folder_path in export_folders:
                    if folder_path.exists():
                        for root, dirs, files in os.walk(folder_path):
                            for file in files:
                                file_path = Path(root) / file
                                arcname = str(file_path.relative_to(app_dir))
                                zipf.write(file_path, arcname)
                                exported_count += 1
                    else:
                        # 如果文件夹不存在，自动创建目录以确保导出完整
                        try:
                            folder_path.mkdir(parents=True, exist_ok=True)
                            logger.info(f"自动创建不存在的文件夹: {folder_path}")
                            
                            # 创建一个说明文件，记录该文件夹是自动创建的
                            readme_path = folder_path / "_auto_created_readme.txt"
                            with open(readme_path, 'w', encoding='utf-8') as f:
                                f.write(f"此文件夹是在诊断数据导出时自动创建的\n")
                                f.write(f"创建时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                                f.write(f"原因: 原文件夹不存在，为确保导出完整性而自动创建\n")
                            
                            # 将创建的说明文件添加到压缩包
                            arcname = str(readme_path.relative_to(app_dir))
                            zipf.write(readme_path, arcname)
                            exported_count += 1
                            
                        except Exception as create_error:
                            # 如果创建失败，记录错误但继续导出其他文件夹
                            logger.error(f"创建文件夹失败 {folder_path}: {str(create_error)}")
                            relative_path = str(folder_path.relative_to(app_dir))
                            error_info = {
                                "folder": relative_path,
                                "status": "creation_failed",
                                "error": str(create_error),
                                "note": "自动创建文件夹失败"
                            }
                            zipf.writestr(f"_error_{relative_path.replace('/', '_')}.json", 
                                        json.dumps(error_info, ensure_ascii=False, indent=2))
                
                # 创建结构化的系统信息报告 - 使用JSON格式便于程序解析
                system_info = {
                    # 【导出元数据】基础信息记录
                    "export_metadata": {
                        "software": "SecRandom",                                                # 软件名称
                        "export_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),            # 人类可读时间
                        "export_timestamp": datetime.now().isoformat(),                         # ISO标准时间戳
                        "version": VERSION,                                                     # 当前软件版本
                        "export_type": "diagnostic",                                            # 导出类型（诊断数据）
                    },
                    # 【系统环境信息】详细的运行环境数据
                    "system_info": {
                        "software_path": str(app_dir),                                           # 软件安装路径
                        "operating_system": self._get_operating_system(),                       # 操作系统版本（正确识别Win11）
                        "platform_details": {                                                   # 平台详细信息
                            "system": platform.system(),                                        # 系统类型 (Windows/Linux/Darwin)
                            "release": self._get_platform_release(),                          # 系统发行版本（正确识别Win11）
                            "version": self._get_platform_version(),                          # 完整系统版本（正确识别Win11）
                            "machine": platform.machine(),                                      # 机器架构 (AMD64/x86_64)
                            "processor": platform.processor()                                   # 处理器信息
                        },
                        "python_version": sys.version,                                          # Python完整版本信息
                        "python_executable": sys.executable                                     # Python可执行文件路径
                    },
                    # 【导出摘要】统计信息和导出详情
                    "export_summary": {
                        "total_files_exported": exported_count,                                 # 成功导出的文件总数
                        "export_folders": [str(folder) for folder in export_folders],         # 导出的文件夹列表（转换为字符串）
                        "export_location": str(zip_path)                                         # 导出压缩包的完整路径
                    }
                }
                # 将系统信息写入JSON文件，使用中文编码确保兼容性
                diagnostic_filename = f"SecRandom_诊断报告_{VERSION}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                zipf.writestr(diagnostic_filename, json.dumps(system_info, ensure_ascii=False, indent=2))
            
            # 显示成功提示
            InfoBar.success(
                title='导出成功',
                content=f'诊断数据已导出到: {zip_path}',
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=5000,
                parent=self
            )
            
            logger.success(f"诊断数据导出成功: {zip_path}")
            
            # 打开导出文件所在的文件夹 - 提供用户友好的选择提示
            try:
                # 创建消息框询问用户是否打开导出目录
                msg_box = Dialog(
                    title='诊断数据导出完成',
                    content=f'诊断数据已成功导出到桌面！\n\n文件位置: {zip_path}\n\n是否立即打开导出文件夹查看文件？',
                    parent=self
                )
                msg_box.yesButton.setText('打开文件夹')
                msg_box.cancelButton.setText('稍后再说')
                msg_box.setFont(QFont(load_custom_font(), 12))
                
                if msg_box.exec():
                    # 用户选择打开文件夹
                    os.startfile(os.path.dirname(zip_path))
                    logger.info("用户选择打开诊断数据导出文件夹")
                else:
                    # 用户选择不打开
                    logger.info("用户选择不打开诊断数据导出文件夹")
                    
            except Exception as e:
                # 如果消息框创建失败，回退到简单的提示
                logger.error(f"创建消息框失败: {str(e)}")
                try:
                    os.startfile(os.path.dirname(zip_path))
                except:
                    logger.error("无法打开诊断数据导出文件夹")
            except:
                pass
                
        except Exception as e:
            logger.error(f"导出诊断数据时出错: {str(e)}")
            InfoBar.error(
                title='导出失败',
                content=f'导出诊断数据时出错: {str(e)}',
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=5000,
                parent=self
            )

    def _get_operating_system(self):
        """
        获取操作系统版本信息，正确识别Windows 11系统
        
        Returns:
            str: 操作系统版本字符串
        """
        try:
            system = platform.system()
            if system != "Windows":
                # 非Windows系统直接返回标准信息
                return f"{system} {platform.release()}"
            
            # Windows系统特殊处理，正确识别Windows 11
            try:
                import winreg
                # 查询注册表获取当前Windows版本号
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion")
                current_build = winreg.QueryValueEx(key, "CurrentBuild")[0]
                display_version = winreg.QueryValueEx(key, "DisplayVersion")[0]
                product_name = winreg.QueryValueEx(key, "ProductName")[0]
                winreg.CloseKey(key)
                
                # Windows 11的构建版本号从22000开始
                if int(current_build) >= 22000:
                    return f"Windows 11 (Build {current_build}, Version {display_version})"
                else:
                    # Windows 10或其他版本
                    return f"{product_name} (Build {current_build}, Version {display_version})"
                    
            except Exception as e:
                logger.error(f"从注册表获取Windows版本信息失败: {str(e)}")
                # 回退到标准方法
                release = platform.release()
                version = platform.version()
                # 通过版本号简单判断（不精确但比直接显示Windows 10好）
                if release == "10" and version and version.split(".")[-1] >= "22000":
                    return f"Windows 11 {version}"
                return f"Windows {release} {version}"
                
        except Exception as e:
            logger.error(f"获取操作系统版本信息失败: {str(e)}")
            # 最终回退方案
            return f"{platform.system()} {platform.release()} {platform.version()}"

    def _get_platform_release(self):
        """
        获取系统发行版本，正确识别Windows 11
        
        Returns:
            str: 系统发行版本
        """
        try:
            system = platform.system()
            if system != "Windows":
                # 非Windows系统直接返回标准信息
                return platform.release()
            
            # Windows系统特殊处理，正确识别Windows 11
            try:
                import winreg
                # 查询注册表获取当前Windows版本号
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion")
                current_build = winreg.QueryValueEx(key, "CurrentBuild")[0]
                product_name = winreg.QueryValueEx(key, "ProductName")[0]
                winreg.CloseKey(key)
                
                # Windows 11的构建版本号从22000开始
                if int(current_build) >= 22000:
                    return "11"
                else:
                    # 从产品名称中提取版本号
                    if "Windows 10" in product_name:
                        return "10"
                    elif "Windows 8" in product_name:
                        return "8"
                    elif "Windows 7" in product_name:
                        return "7"
                    else:
                        # 回退到标准方法
                        return platform.release()
                        
            except Exception as e:
                logger.error(f"从注册表获取Windows版本信息失败: {str(e)}")
                # 回退到标准方法
                release = platform.release()
                version = platform.version()
                # 通过版本号简单判断
                if release == "10" and version and version.split(".")[-1] >= "22000":
                    return "11"
                return release
                
        except Exception as e:
            logger.error(f"获取系统发行版本失败: {str(e)}")
            # 最终回退方案
            return platform.release()
    
    def _get_platform_version(self):
        """
        获取完整系统版本，正确识别Windows 11
        
        Returns:
            str: 完整系统版本
        """
        try:
            system = platform.system()
            if system != "Windows":
                # 非Windows系统直接返回标准信息
                return platform.version()
            
            # Windows系统特殊处理，正确识别Windows 11
            try:
                import winreg
                # 查询注册表获取当前Windows版本号
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion")
                current_build = winreg.QueryValueEx(key, "CurrentBuild")[0]
                display_version = winreg.QueryValueEx(key, "DisplayVersion")[0]
                ubr = winreg.QueryValueEx(key, "UBR")[0]  # Update Build Revision
                winreg.CloseKey(key)
                
                # 构建更准确的版本字符串
                if int(current_build) >= 22000:
                    # Windows 11
                    return f"{current_build}.{ubr} (Version {display_version})"
                else:
                    # Windows 10或其他版本
                    return f"{current_build}.{ubr} (Version {display_version})"
                    
            except Exception as e:
                logger.error(f"从注册表获取Windows版本信息失败: {str(e)}")
                # 回退到标准方法但进行修正
                version = platform.version()
                release = platform.release()
                if release == "10" and version and version.split(".")[-1] >= "22000":
                    # 修正为Windows 11版本信息
                    return version
                return version
                
        except Exception as e:
            logger.error(f"获取完整系统版本失败: {str(e)}")
            # 最终回退方案
            return platform.version()

    def import_settings(self):
        """导入设置"""
        try:
            # 打开文件选择对话框
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "选择要导入的设置文件",
                "",
                "设置文件 (*.json);;所有文件 (*.*)"
            )
            
            if not file_path:
                return
            
            # 读取导入的设置文件
            with open_file(file_path, 'r', encoding='utf-8') as f:
                imported_settings = json.load(f)
            
            # 显示设置选择对话框
            dialog = SettingsSelectionDialog(mode="import", parent=self)
            if dialog.exec_() == QDialog.Accepted:
                selected_settings = dialog.get_selected_settings()
                
                # 应用选中的设置
                for file_name, subcategories in selected_settings.items():
                    if not subcategories:  # 如果没有选中的设置项，跳过
                        continue
                        
                    # 获取目标文件路径
                    target_file_path = self._get_settings_file_path(file_name)
                    if not target_file_path:
                        continue
                    
                    from app.common.path_utils import path_manager
                    if not path_manager.file_exists(target_file_path):
                        continue
                    
                    try:
                        # 读取现有设置
                        with open_file(target_file_path, 'r', encoding='utf-8') as f:
                            current_settings = json.load(f)
                        
                        # 使用辅助方法更新设置
                        self._update_settings_by_file_type(file_name, subcategories, current_settings, imported_settings)
                        
                        # 保存更新后的设置
                        with open_file(target_file_path, 'w', encoding='utf-8') as f:
                            json.dump(current_settings, f, indent=4, ensure_ascii=False)
                            
                    except Exception as e:
                        logger.error(f"更新设置文件 {file_name} 失败: {str(e)}")
                        continue
                
                # 显示成功消息
                w = Dialog("导入成功", "设置已成功导入，现在需要重启应用才能生效。", None)
                w.yesButton.setText("确定")
                w.cancelButton.hide()
                w.buttonLayout.insertStretch(1)
                w.exec_()
        except Exception as e:
            logger.error(f"导入设置失败: {str(e)}")
            w = Dialog("导入失败", f"导入设置时发生错误: {str(e)}", None)
            w.yesButton.setText("确定")
            w.cancelButton.hide()
            w.buttonLayout.insertStretch(1)
            w.exec_()
    
    def _get_settings_file_path(self, file_name):
        """根据文件名获取设置文件路径"""
        from app.common.path_utils import path_manager
        settings_dir = path_manager.get_settings_path()
        
        if file_name in ["foundation", "pumping_people", "instant_draw", "pumping_reward", "history", "channel", "position"]:
            return os.path.join(settings_dir, "Settings.json")
        elif file_name in ["fixed_url", "personal", "floating_window", "roll_call", "reward", "program_functionality"]:
            return os.path.join(settings_dir, "custom_settings.json")
        else:
            return os.path.join(settings_dir, f"{file_name}.json")
    
    def _update_settings_by_file_type(self, file_name, subcategories, current_settings, imported_settings):
        """根据文件类型更新设置"""
        for subcategory_name, settings in subcategories.items():
            if not settings:  # 如果没有选中的设置项，跳过
                continue
                
            if file_name in ["foundation", "pumping_people", "instant_draw", "pumping_reward", "history", "channel", "position"]:
                self._update_settings_json_categories(file_name, settings, current_settings, imported_settings)
            elif file_name == "voice_engine":
                self._update_voice_engine_settings(settings, current_settings, imported_settings)
            elif file_name == "config":
                self._update_config_settings(settings, current_settings, imported_settings)
            elif file_name == "CleanupTimes":
                self._update_cleanup_times_settings(current_settings, imported_settings)
            elif file_name == "ForegroundSoftware":
                self._update_foreground_software_settings(settings, current_settings, imported_settings)
            elif file_name in ["fixed_url", "personal", "floating_window", "roll_call", "reward", "program_functionality"]:
                self._update_generic_settings(file_name, settings, current_settings, imported_settings)
    
    def _update_settings_json_categories(self, file_name, settings, current_settings, imported_settings):
        """更新Settings.json中的分类设置"""
        if file_name == "channel":
            # channel是根级别的字符串，不是嵌套对象
            if "channel" in imported_settings:
                current_settings["channel"] = imported_settings["channel"]
        elif file_name == "position":
            # position是根级别的对象
            if "position" in imported_settings:
                current_settings["position"] = imported_settings["position"]
        else:
            # foundation、pumping_people、pumping_reward、history等分类
            if file_name not in current_settings:
                current_settings[file_name] = {}
            
            for setting_name in settings:
                if file_name in imported_settings and setting_name in imported_settings[file_name]:
                    current_settings[file_name][setting_name] = imported_settings[file_name][setting_name]
    
    def _update_voice_engine_settings(self, settings, current_settings, imported_settings):
        """更新voice_engine设置"""
        if "voice_engine" not in current_settings:
            current_settings["voice_engine"] = {}
        
        for setting_name in settings:
            if "voice_engine" in imported_settings and setting_name in imported_settings["voice_engine"]:
                current_settings["voice_engine"][setting_name] = imported_settings["voice_engine"][setting_name]
    
    def _update_config_settings(self, settings, current_settings, imported_settings):
        """更新config设置"""
        for setting_name in settings:
            # 确定目标分区
            if setting_name == "DpiScale":
                target_section = "Window"
            elif setting_name in ["ThemeColor", "ThemeMode"]:
                target_section = "QFluentWidgets"
            else:
                target_section = "config"
            
            if target_section not in current_settings:
                current_settings[target_section] = {}
            
            if target_section in imported_settings and setting_name in imported_settings[target_section]:
                current_settings[target_section][setting_name] = imported_settings[target_section][setting_name]
    
    def _update_cleanup_times_settings(self, current_settings, imported_settings):
        """更新CleanupTimes设置"""
        if "CleanupTimes" not in current_settings and "cleanuptimes" in imported_settings:
            current_settings["CleanupTimes"] = imported_settings["cleanuptimes"]
    
    def _update_foreground_software_settings(self, settings, current_settings, imported_settings):
        """更新ForegroundSoftware设置"""
        if "ForegroundSoftware" not in current_settings:
            current_settings["ForegroundSoftware"] = {}
        
        for setting_name in settings:
            if "ForegroundSoftware" in imported_settings and setting_name in imported_settings["ForegroundSoftware"]:
                current_settings["ForegroundSoftware"][setting_name] = imported_settings["ForegroundSoftware"][setting_name]
    
    def _update_generic_settings(self, file_name, settings, current_settings, imported_settings):
        """更新通用设置"""
        if file_name not in current_settings:
            current_settings[file_name] = {}
        
        for setting_name in settings:
            if file_name in imported_settings and setting_name in imported_settings[file_name]:
                current_settings[file_name][setting_name] = imported_settings[file_name][setting_name]

    def export_settings(self):
        """导出设置"""
        try:
            # 显示设置选择对话框
            dialog = SettingsSelectionDialog(mode="export", parent=self)
            if dialog.exec_() == QDialog.Accepted:
                selected_settings = dialog.get_selected_settings()
                
                # 获取设置目录路径
                from app.common.path_utils import path_manager
                settings_dir = path_manager.get_settings_path()
                
                # 收集选中的设置
                exported_settings = {}
                
                # 遍历选中的设置项，现在category_name直接就是文件名
                for file_name, subcategories in selected_settings.items():
                    for subcategory_name, settings in subcategories.items():
                        if settings:  # 如果有选中的设置项
                            # 根据文件名确定文件路径
                            file_path = self._get_settings_file_path(file_name, settings_dir)
                            
                            if path_manager.file_exists(file_path):
                                # 读取设置文件
                                with open_file(file_path, 'r', encoding='utf-8') as f:
                                    current_settings = json.load(f)
                                
                                # 根据文件类型处理导出逻辑
                                self._process_export_by_file_type(
                                    file_name, settings, current_settings, 
                                    exported_settings, selected_settings
                                )
                
                # 保存导出的设置
                self._save_exported_settings(exported_settings)
                
        except Exception as e:
            logger.error(f"导出设置失败: {str(e)}")
            w = Dialog("导出失败", f"导出设置时发生错误: {str(e)}", None)
            w.yesButton.setText("确定")
            w.cancelButton.hide()
            w.buttonLayout.insertStretch(1)
            w.exec_()
    
    def _get_settings_file_path(self, file_name, settings_dir):
        """根据文件名获取设置文件路径"""
        # 特殊处理：所有设置项实际上都在Settings.json文件中
        if file_name in ["foundation", "pumping_people", "instant_draw", "pumping_reward", "history", "channel", "position"]:
            return os.path.join(settings_dir, "Settings.json")
        elif file_name == ["fixed_url", "personal", "sidebar", "floating_window", "roll_call", "reward", "program_functionality"]:
            return os.path.join(settings_dir, "custom_settings.json")
        else:
            return os.path.join(settings_dir, f"{file_name}.json")
    
    def _process_export_by_file_type(self, file_name, settings, current_settings, exported_settings, selected_settings):
        """根据文件类型处理导出逻辑"""
        # 初始化导出设置中的文件分类
        if file_name not in exported_settings:
            exported_settings[file_name] = {}
        
        # 处理Settings.json中的分类
        if file_name in ["foundation", "pumping_people", "instant_draw", "pumping_reward", "history", "channel", "position"]:
            self._export_settings_json_categories(file_name, settings, current_settings, exported_settings)
        # 处理voice_engine文件
        elif file_name == "voice_engine":
            self._export_voice_engine_settings(settings, current_settings, exported_settings)
        # 处理pumping_people和pumping_reward文件（特殊处理音效设置）
        elif file_name in ["pumping_people", "pumping_reward"]:
            self._export_pumping_settings(file_name, settings, current_settings, exported_settings, selected_settings)
        # 处理config文件
        elif file_name == "config":
            self._export_config_settings(settings, current_settings, exported_settings)
        # 处理CleanupTimes文件
        elif file_name == "CleanupTimes":
            self._export_cleanup_times_settings(settings, current_settings, exported_settings)
        # 处理ForegroundSoftware文件
        elif file_name == "ForegroundSoftware":
            self._export_foreground_software_settings(settings, current_settings, exported_settings)
        # 处理其他文件类型
        else:
            self._export_generic_settings(file_name, settings, current_settings, exported_settings)
    
    def _export_settings_json_categories(self, file_name, settings, current_settings, exported_settings):
        """导出Settings.json中的分类设置"""
        if file_name == "channel":
            # channel是根级别的字符串，不是嵌套对象
            if "channel" in current_settings:
                exported_settings[file_name] = current_settings["channel"]
        elif file_name == "position":
            # position是根级别的对象
            if "position" in current_settings:
                exported_settings[file_name] = current_settings["position"]
        else:
            # foundation、pumping_people、pumping_reward、history等分类
            if file_name in current_settings:
                # 如果该分类还没有在导出设置中，则创建
                if file_name not in exported_settings:
                    exported_settings[file_name] = {}
                
                # 导出该分类下的所有选中的设置项
                for setting_name in settings:
                    if setting_name in current_settings[file_name]:
                        exported_settings[file_name][setting_name] = current_settings[file_name][setting_name]
    
    def _export_voice_engine_settings(self, settings, current_settings, exported_settings):
        """导出voice_engine设置"""
        section_name = "voice_engine"
        if section_name not in exported_settings["voice_engine"]:
            exported_settings["voice_engine"][section_name] = {}
        
        for setting_name in settings:
            if section_name in current_settings and setting_name in current_settings[section_name]:
                exported_settings["voice_engine"][section_name][setting_name] = current_settings[section_name][setting_name]
    
    def _export_pumping_settings(self, file_name, settings, current_settings, exported_settings, selected_settings):
        """导出pumping_people和pumping_reward设置（包含音效设置的特殊处理）"""
        section_name = file_name
        # 确保分类存在
        if section_name not in exported_settings:
            exported_settings[section_name] = {}
        
        # 导出基础设置
        for setting_name in settings:
            if section_name in current_settings and setting_name in current_settings[section_name]:
                exported_settings[section_name][setting_name] = current_settings[section_name][setting_name]
        
        # 如果当前处理的是pumping_reward，并且有音效设置被选中，需要添加音效设置
        if file_name == "pumping_reward":
            self._export_sound_settings(current_settings, exported_settings, selected_settings, section_name)
    
    def _export_sound_settings(self, current_settings, exported_settings, selected_settings, section_name):
        """导出音效设置"""
        # 检查是否有音效设置被选中
        sound_settings = ["animation_music_enabled", "result_music_enabled", 
                         "animation_music_volume", "result_music_volume",
                         "music_fade_in", "music_fade_out"]
        
        # 获取选中的音效设置
        selected_sound_settings = []
        for category_name, subcategories in selected_settings.items():
            for subcategory_name, settings_list in subcategories.items():
                if subcategory_name == "音效设置":
                    selected_sound_settings = settings_list
                    break
        
        # 如果有音效设置被选中，添加到pumping_reward分类中
        if selected_sound_settings:
            for sound_setting in selected_sound_settings:
                if sound_setting in sound_settings and sound_setting in current_settings.get("pumping_reward", {}):
                    exported_settings[section_name][sound_setting] = current_settings["pumping_reward"][sound_setting]
    
    def _export_config_settings(self, settings, current_settings, exported_settings):
        """导出config设置"""
        for setting_name in settings:
            # 根据设置名确定目标分类
            if setting_name == "DpiScale":
                target_section = "Window"
            elif setting_name in ["ThemeColor", "ThemeMode"]:
                target_section = "QFluentWidgets"
            else:
                target_section = "config"
            
            # 确保目标分类存在
            if target_section not in exported_settings["config"]:
                exported_settings["config"][target_section] = {}
            
            # 添加设置项
            if target_section in current_settings and setting_name in current_settings[target_section]:
                exported_settings["config"][target_section][setting_name] = current_settings[target_section][setting_name]
    
    def _export_cleanup_times_settings(self, settings, current_settings, exported_settings):
        """导出CleanupTimes设置"""
        if "cleanuptimes" in current_settings:
            exported_settings["CleanupTimes"] = current_settings["cleanuptimes"]
    
    def _export_foreground_software_settings(self, settings, current_settings, exported_settings):
        """导出ForegroundSoftware设置"""
        if "ForegroundSoftware" in current_settings:
            exported_settings["ForegroundSoftware"] = current_settings["ForegroundSoftware"]
    
    def _export_generic_settings(self, file_name, settings, current_settings, exported_settings):
        """导出通用设置"""
        if file_name not in exported_settings:
            exported_settings[file_name] = {}
        
        for setting_name in settings:
            if file_name in current_settings and setting_name in current_settings[file_name]:
                exported_settings[file_name][setting_name] = current_settings[file_name][setting_name]
    
    def _save_exported_settings(self, exported_settings):
        """保存导出的设置到文件"""
        # 打开保存文件对话框
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "保存设置文件",
            f"settings_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            "设置文件 (*.json)"
        )
        
        if file_path:
            # 确保文件扩展名是.json
            if not file_path.endswith('.json'):
                file_path += '.json'
            
            # 保存导出的设置
            with open_file(file_path, 'w', encoding='utf-8') as f:
                json.dump(exported_settings, f, indent=4, ensure_ascii=False)
            
            # 显示成功消息
            w = Dialog("导出成功", f"设置已成功导出到:\n{file_path}", None)
            w.yesButton.setText("确定")
            w.cancelButton.hide()
            w.buttonLayout.insertStretch(1)
            w.exec_()




class SettingsSelectionDialog(QDialog):
    """设置选择对话框，用于选择要导入导出的设置项"""
    def __init__(self, mode="export", parent=None):
        super().__init__(parent)
        self.mode = mode  # "export" 或 "import"
        self.setWindowTitle("选择设置项" if mode == "export" else "导入设置")
        self.setMinimumSize(600, 500)  # 设置最小大小而不是固定大小
        self.dragging = False
        self.drag_position = None
        
        # 设置无边框但可调整大小的窗口
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        
        # 创建自定义标题栏
        self.title_bar = QWidget()
        self.title_bar.setObjectName("CustomTitleBar")
        self.title_bar.setFixedHeight(35)
        
        title_layout = QHBoxLayout(self.title_bar)
        title_layout.setContentsMargins(10, 0, 10, 0)
        
        # 创建包含图标的标题布局
        title_content_layout = QHBoxLayout()
        title_content_layout.setContentsMargins(0, 0, 0, 0)
        
        # 添加设置图标
        settings_icon = BodyLabel()
        icon_path = path_manager.get_resource_path('icon', 'secrandom-icon-paper.png')
        if path_manager.file_exists(icon_path):
            settings_icon.setPixmap(QIcon(str(icon_path)).pixmap(20, 20))
        else:
            # 如果图标文件不存在，使用备用图标
            settings_icon.setPixmap(QIcon.fromTheme("document-properties", QIcon()).pixmap(20, 20))
        title_content_layout.addWidget(settings_icon)
        
        # 添加功能描述标题
        title_text = "导出设置 - 选择要导出的设置项" if mode == "export" else "导入设置 - 选择要导入的设置项"
        self.title_label = BodyLabel(title_text)
        self.title_label.setObjectName("TitleLabel")
        self.title_label.setFont(QFont(load_custom_font(), 12))
        title_content_layout.addWidget(self.title_label)
        title_content_layout.addStretch()
        
        self.close_btn = QPushButton("✕")
        self.close_btn.setObjectName("CloseButton")
        self.close_btn.setFixedSize(25, 25)
        self.close_btn.clicked.connect(self.reject)
        
        # 将标题内容布局添加到主标题布局中
        title_layout.addLayout(title_content_layout)
        title_layout.addWidget(self.close_btn)
        
        # 创建滚动区域
        self.scroll_area = ScrollArea()
        self.scroll_area.setWidgetResizable(True)
        
        # 创建内容容器
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setAlignment(Qt.AlignLeft)
        
        # 创建设置项选择区域
        self.settings_groups = {}
        self.create_setting_selections()
        
        self.scroll_area.setWidget(self.content_widget)
        
        # 创建按钮
        self.select_all_button = PushButton("全选")
        self.deselect_all_button = PushButton("取消全选")
        self.ok_button = PrimaryPushButton("确定")
        self.cancel_button = PushButton("取消")
        
        self.select_all_button.clicked.connect(self.select_all)
        self.deselect_all_button.clicked.connect(self.deselect_all)
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
        
        # 设置字体
        for widget in [self.select_all_button, self.deselect_all_button, self.ok_button, self.cancel_button]:
            widget.setFont(QFont(load_custom_font(), 12))
        
        # 布局
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.select_all_button)
        button_layout.addWidget(self.deselect_all_button)
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.ok_button)
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.title_bar)
        main_layout.addWidget(self.scroll_area)
        main_layout.addLayout(button_layout)
        
        self.setLayout(main_layout)
        
        # 更新主题样式
        self.update_theme_style()
        qconfig.themeChanged.connect(self.update_theme_style)
    
    def create_setting_selections(self):
        """创建设置项选择界面"""
        # 定义按文件分类的设置项结构
        self.settings_structure = {
            "foundation": {
                "主窗口设置": [
                    "main_window_mode", "main_window_focus_mode", "main_window_focus_time",
                    "topmost_switch", "window_width", "window_height",
                    "show_startup_window_switch"
                ],
                "设置窗口设置": [
                    "settings_window_mode", "settings_window_width", "settings_window_height"
                ],
                "闪抽窗口设置": [
                    "flash_window_auto_close", "flash_window_close_time",
                ],
                "启动设置": [
                    "check_on_startup", "self_starting_enabled", "url_protocol_enabled"
                ],
                "全局快捷键设置": [
                    "global_shortcut_enabled", "global_shortcut_target", "global_shortcut_key",
                    "local_pumping_shortcut_key", "local_reward_shortcut_key",
                ]
            },
            "pumping_people": {
                "基础设置": [
                    "draw_mode", "draw_pumping", "student_id", "student_name", "people_theme",
                    "max_draw_count", "Draw_pumping"
                ],
                "显示设置": [
                    "display_format", "font_size", "animation_color", "show_student_image",
                    "show_random_member", "random_member_format"
                ],
                "动画设置": [
                    "animation_mode", "animation_interval", "animation_auto_play"
                ],
                "音效设置": [
                    "animation_music_enabled", "result_music_enabled",
                    "animation_music_volume", "result_music_volume",
                    "music_fade_in", "music_fade_out"
                ]
            },
            "instant_draw": {
                "基础设置": [
                    "follow_roll_call", "draw_mode", "draw_pumping", "student_id", "student_name", "people_theme",
                    "max_draw_count"
                ],
                "显示设置": [
                    "display_format", "font_size", "animation_color", "show_student_image",
                    "show_random_member", "random_member_format"
                ],
                "动画设置": [
                    "animation_mode", "animation_interval", "animation_auto_play"
                ],
                "联动设置": [
                    "use_cwci_display", "use_cwci_display_time"
                ],
                "音效设置": [
                    "animation_music_enabled", "result_music_enabled",
                    "animation_music_volume", "result_music_volume",
                    "music_fade_in", "music_fade_out"
                ]
            },
            "pumping_reward": {
                "基础设置": [
                    "draw_mode", "draw_pumping", "reward_theme"
                ],
                "显示设置": [
                    "display_format", "font_size", "animation_color", "show_reward_image"
                ],
                "动画设置": [
                    "animation_mode", "animation_interval", "animation_auto_play"
                ],
                "音效设置": [
                    "animation_music_enabled", "result_music_enabled",
                    "animation_music_volume", "result_music_volume",
                    "music_fade_in", "music_fade_out"
                ]
            },
            "history": {
                "点名历史": [
                    "history_enabled", "probability_weight", "history_days"
                ],
                "抽奖历史": [
                    "reward_history_enabled", "history_reward_days"
                ]
            },
            "channel": {
                "更新设置": [
                    "channel"
                ]
            },
            "position": {
                "位置设置": [
                    "x", "y"
                ]
            },
            "config": {
                "主题与显示": [
                    "ThemeColor", "ThemeMode", "DpiScale"
                ]
            },
            "voice_engine": {
                "语音引擎设置": [
                    "voice_engine", "edge_tts_voice_name", "voice_enabled", "voice_volume",
                    "voice_speed", "system_volume_enabled", "system_volume_value"
                ]
            },
            "CleanupTimes": {
                "清理时间设置": [
                    "cleanuptimes"
                ]
            },
            "ForegroundSoftware": {
                "前台软件设置": [
                    "foregroundsoftware_class", "foregroundsoftware_title", "foregroundsoftware_process"
                ]
            },
            "fixed_url": {
                "固定URL设置": [
                    "enable_main_url", "enable_settings_url", "enable_pumping_url", "enable_reward_url",
                    "enable_history_url", "enable_floating_url", "enable_about_url", "enable_direct_extraction_url",
                    "enable_pumping_action_url", "enable_reward_action_url", "enable_about_action_url",
                    "enable_pumping_start_url", "enable_pumping_stop_url", "enable_pumping_reset_url", "enable_reward_start_url",
                    "enable_reward_stop_url", "enable_reward_reset_url", "enable_about_donation_url", "enable_about_contributor_url",
                    "main_url_notification", "settings_url_notification", "pumping_url_notification",
                    "reward_url_notification", "history_url_notification", "floating_url_notification", "about_url_notification",
                    "direct_extraction_url_notification", "pumping_start_url_notification", "pumping_stop_url_notification",
                    "pumping_reset_url_notification", "reward_start_url_notification", "reward_stop_url_notification", "reward_reset_url_notification",
                    "about_donation_url_notification", "about_contributor_url_notification", "settings_url_skip_security",
                    "floating_url_skip_security"
                ]
            },
            "personal": {
                "主题设置": [
                    "enable_background_icon", "background_blur", "background_brightness", "enable_main_background",
                    "enable_settings_background", "enable_flash_background", "main_background_image", "settings_background_image",
                    "flash_background_image", "font_family"
                ]
            },
            "sidebar": {
                "侧边栏设置": [
                    "pumping_floating_side", "pumping_reward_side", "show_settings_icon", "main_window_side_switch",
                    "main_window_history_switch", "show_security_settings_switch", 
                    "show_voice_settings_switch", "show_history_settings_switch"
                ]
            },
            "floating_window": {
                "浮窗设置": [
                    "pumping_floating_enabled", "pumping_floating_transparency_mode", "pumping_floating_visible",
                    "button_arrangement_mode", "floating_icon_mode", "flash_window_side_switch", "custom_retract_time",
                    "custom_display_mode", "floating_window_visibility"
                ],
            },
            "roll_call": {
                "点名界面管理": [
                    "pumping_people_control_Switch", "modify_button_switch", "show_reset_button", "show_refresh_button", "show_quantity_control",
                    "show_start_button", "show_list_toggle", "selection_range", "selection_gender", "people_theme"
                ]
            },
            "reward": {
                "抽奖界面管理": [
                    "pumping_reward_control_Switch", "show_reset_button", "show_refresh_button", "show_quantity_control",
                    "show_list_toggle", "reward_theme", "show_start_button"
                ]
            },
            "program_functionality": {
                "软件功能设置": [
                    "instant_draw_disable", "clear_draw_records_switch", "clear_draw_records_time"
                ]
            }
        }
        
        # 为每个功能分类创建选择区域
        for category_name, subcategories in self.settings_structure.items():
            file_group = GroupHeaderCardWidget()
            file_group.setTitle(category_name)
            file_group.setBorderRadius(8)
            
            self.settings_groups[category_name] = {}
            
            # 遍历每个子分类和设置项，为每个设置项创建独立的分组
            for subcategory_name, settings in subcategories.items():
                self.settings_groups[category_name][subcategory_name] = {}
                
                # 为每个设置项创建独立的分组
                for setting in settings:
                    # 创建独立的设置项容器
                    setting_widget = QWidget()
                    setting_layout = QVBoxLayout(setting_widget)
                    setting_layout.setAlignment(Qt.AlignLeft)
                    setting_layout.setSpacing(4)
                    
                    # 创建复选框
                    checkbox = CheckBox(self.get_setting_display_name(setting))
                    checkbox.setFont(QFont(load_custom_font(), 10))
                    checkbox.setChecked(True)
                    self.settings_groups[category_name][subcategory_name][setting] = checkbox
                    
                    # 创建水平布局让复选框靠左
                    checkbox_layout = QHBoxLayout()
                    checkbox_layout.addWidget(checkbox)
                    checkbox_layout.setAlignment(Qt.AlignLeft)
                    checkbox_layout.addStretch()
                    
                    # 将复选框布局添加到设置布局中
                    checkbox_widget = QWidget()
                    checkbox_widget.setLayout(checkbox_layout)
                    setting_layout.addWidget(checkbox_widget)
                    
                    # 简化分类逻辑，直接使用子分类名称和设置项显示名称
                    display_name = self.get_setting_display_name(setting)
                    file_group.addGroup(None, subcategory_name, f"{display_name}设置项", setting_widget)
            
            self.content_layout.addWidget(file_group)

    def get_setting_display_name(self, setting_name):
        """获取设置项的显示名称"""
        display_names = {
            # foundation设置
            "check_on_startup": "启动时检查更新", # 有
            "self_starting_enabled": "开机自启动", # 有
            "main_window_focus_mode": "主窗口焦点模式", # 有
            "main_window_focus_time": "焦点检测时间", # 有
            "main_window_mode": "主窗口位置", # 有
            "settings_window_mode": "设置窗口位置", # 有
            "flash_window_auto_close": "闪抽窗口自动关闭", # 有
            "flash_window_close_time": "闪抽窗口关闭时间", # 有
            "topmost_switch": "主窗口置顶", # 有
            "window_width": "主窗口宽度", # 有
            "window_height": "主窗口高度", # 有
            "settings_window_width": "设置窗口宽度", # 有
            "settings_window_height": "设置窗口高度", # 有
            "url_protocol_enabled": "URL协议注册", # 有
            "global_shortcut_enabled": "全局快捷键启用", # 有
            "global_shortcut_target": "全局快捷键目标", # 有
            "global_shortcut_key": "全局快捷键", # 有
            "local_pumping_shortcut_key": "点名操作快捷键", # 有
            "local_reward_shortcut_key": "抽奖操作快捷键", # 有
            "show_startup_window_switch": "显示启动窗口", # 有
            # advanced设置
            "floating_window_visibility": "浮窗显隐条件", # 有
            # pumping_people设置（跟pumping_reward设置有重复的不计入）
            "student_id": "显示学号", # 有
            "student_name": "显示姓名", # 有
            "people_theme": "主题", # 有
            "show_random_member": "显示随机成员", # 有
            "random_member_format": "随机成员格式", # 有
            "show_student_image": "显示学生图片", # 有
            # instant_draw设置
            "follow_roll_call": "跟随点名设置", # 有
            "use_cwci_display": "使用cw/ci显示结果", # 有
            "use_cwci_display_time": "使用cw/ci显示结果时间", # 有
            # pumping_reward设置（跟pumping_people设置有重复的不计入）
            "reward_theme": "主题", # 有
            "show_reward_image": "显示奖品图片", # 有
            # pumping_people设置和pumping_reward设置 重复设置项
            "draw_mode": "抽取模式", # 有
            "draw_pumping": "抽取方式", # 有
            "animation_mode": "动画模式", # 有
            "animation_interval": "动画间隔", # 有
            "animation_auto_play": "自动播放", # 有
            "animation_music_enabled": "动画音乐", # 有
            "result_music_enabled": "结果音乐", # 有
            "animation_music_volume": "动画音量", # 有
            "result_music_volume": "结果音量", # 有
            "music_fade_in": "音乐淡入", # 有
            "music_fade_out": "音乐淡出", # 有
            "display_format": "显示格式", # 有
            "animation_color": "动画颜色", # 有
            "font_size": "字体大小", # 有
            # history设置
            "history_enabled": "历史记录启用", # 有
            "probability_weight": "概率权重", # 有
            "history_days": "历史记录天数", # 有
            "reward_history_enabled": "奖品历史启用", # 有
            "history_reward_days": "奖品历史天数", # 有
            # position设置
            "x": "浮窗X坐标", # 有
            "y": "浮窗Y坐标", # 有
            # channel设置
            "channel": "更新通道", # 有
            # config设置
            "DpiScale": "DPI缩放", # 有
            "ThemeColor": "主题颜色", # 有
            "ThemeMode": "主题模式", # 有
            # voice_engine设置
            "voice_engine": "语音引擎", # 有
            "edge_tts_voice_name": "Edge TTS语音", # 有
            "voice_enabled": "语音启用", # 有
            "voice_volume": "语音音量", # 有
            "voice_speed": "语音速度", # 有
            "system_volume_enabled": "系统音量控制", # 有
            "system_volume_value": "系统音量值", # 有
            # CleanupTimes设置
            "cleanuptimes": "清理时间", # 有
            # ForegroundSoftware设置
            "foregroundsoftware_class": "前台软件类名", # 有
            "foregroundsoftware_title": "前台软件标题", # 有
            "foregroundsoftware_process": "前台软件进程名", # 有
            # fixed_url设置
            "enable_main_url": "主界面URL启用", # 有
            "enable_settings_url": "设置界面URL启用", # 有
            "enable_pumping_url": "点名界面URL启用", # 有
            "enable_reward_url": "抽奖界面URL启用", # 有
            "enable_history_url": "历史记录界面URL启用", # 有
            "enable_floating_url": "浮窗界面URL启用", # 有
            "enable_about_url": "关于界面URL启用", # 有
            "enable_direct_extraction_url": "直接抽取URL启用", # 有
            "enable_pumping_action_url": "点名操作URL启用", # 有
            "enable_reward_action_url": "抽奖操作URL启用", # 有
            "enable_about_action_url": "关于操作URL启用", # 有
            "enable_pumping_start_url": "点名开始URL启用", # 有
            "enable_pumping_stop_url": "点名停止URL启用", # 有
            "enable_pumping_reset_url": "点名重置URL启用", # 有
            "enable_reward_start_url": "抽奖开始URL启用", # 有
            "enable_reward_stop_url": "抽奖停止URL启用", # 有
            "enable_reward_reset_url": "抽奖重置URL启用", # 有
            "enable_about_donation_url": "关于捐赠URL启用", # 有
            "enable_about_contributor_url": "关于贡献者URL启用", # 有
            "main_url_notification": "主界面URL通知", # 有
            "settings_url_notification": "设置界面URL通知", # 有
            "pumping_url_notification": "点名界面URL通知", # 有
            "reward_url_notification": "抽奖界面URL通知", # 有
            "history_url_notification": "历史记录界面URL通知", # 有
            "floating_url_notification": "浮窗界面URL通知", # 有
            "about_url_notification": "关于界面URL通知", # 有
            "direct_extraction_url_notification": "直接抽取URL通知", # 有
            "pumping_start_url_notification": "点名开始URL通知", # 有
            "pumping_stop_url_notification": "点名停止URL通知", # 有
            "pumping_reset_url_notification": "点名重置URL通知", # 有
            "reward_start_url_notification": "抽奖开始URL通知", # 有
            "reward_stop_url_notification": "抽奖停止URL通知", # 有
            "reward_reset_url_notification": "抽奖重置URL通知", # 有
            "about_donation_url_notification": "关于捐赠URL通知", # 有
            "about_contributor_url_notification": "关于贡献者URL通知", # 有
            "settings_url_skip_security": "设置界面URL跳过安全检查", # 有
            "floating_url_skip_security": "浮窗界面URL跳过安全检查", # 有
            # personal设置
            "enable_background_icon": "背景图标启用", # 有
            "background_blur": "背景模糊度", # 有
            "background_brightness": "背景亮度", # 有
            "enable_main_background": "主界面背景启用", # 有
            "enable_settings_background": "设置界面背景启用", # 有
            "enable_flash_background": "闪屏背景启用", # 有
            "main_background_image": "主界面背景图片", # 有
            "settings_background_image": "设置界面背景图片", # 有
            "flash_background_image": "闪屏背景图片", # 有
            "font_family": "字体系列", # 有
            # sidebar设置
            "pumping_floating_side": "点名功能侧边栏", # 有
            "pumping_reward_side": "抽奖功能侧边栏", # 有
            "show_settings_icon": "主窗口上的设置侧边栏", # 有
            "main_window_side_switch": "主窗口侧边栏", # 有
            "main_window_history_switch": "主窗口历史记录侧边栏", # 有
            "show_security_settings_switch": "安全设置侧边栏", # 有
            "show_voice_settings_switch": "语音设置侧边栏", # 有
            "show_history_settings_switch": "设置历史记录侧边栏", # 有
            # floating_window设置
            "pumping_floating_enabled": "浮窗启用", # 有
            "pumping_floating_transparency_mode": "浮窗透明度", # 有
            "pumping_floating_visible": "浮窗", # 有
            "button_arrangement_mode": "浮窗按钮布局", # 有
            "floating_icon_mode": "浮窗图标", # 有
            "flash_window_side_switch": "浮窗窗口贴边", # 有
            "custom_retract_time": "自定义收起时间", # 有
            "custom_display_mode": "自定义显示模式", # 有
            # roll_call 和 reward 的相同设置
            "pumping_people_control_Switch": "点名控制面板位置",
            "show_reset_button": "重置按钮显隐",
            "show_refresh_button": "刷新按钮显隐",
            "show_quantity_control": "数量控制显隐",
            "show_start_button": "开始按钮显隐",
            "show_list_toggle": "名单切换下拉框显隐",
            "selection_range": "选择范围下拉框显隐",
            "selection_gender": "选择性别下拉框显隐",
            "people_theme": "显示剩余数量显隐",
            # roll_call设置
            "modify_button_switch": "修改姓名设置按钮显隐",
            # reward设置
            "pumping_reward_control_Switch": "抽奖控制面板位置",
            "reward_theme": "显示剩余数量",
            # program_functionality设置
            "instant_draw_disable": "直接抽取禁用",
            "clear_draw_records_switch": "清理临时记录",
            "clear_draw_records_time": "清理临时记录时间",
        }
        return display_names.get(setting_name, setting_name)
    
    def select_all(self):
        """全选所有设置项"""
        for category_name in self.settings_groups:
            for subcategory_name in self.settings_groups[category_name]:
                for setting_name in self.settings_groups[category_name][subcategory_name]:
                    self.settings_groups[category_name][subcategory_name][setting_name].setChecked(True)
    
    def deselect_all(self):
        """取消全选所有设置项"""
        for category_name in self.settings_groups:
            for subcategory_name in self.settings_groups[category_name]:
                for setting_name in self.settings_groups[category_name][subcategory_name]:
                    self.settings_groups[category_name][subcategory_name][setting_name].setChecked(False)
    
    def get_selected_settings(self):
        """获取选中的设置项"""
        selected = {}
        for file_name in self.settings_groups:
            selected[file_name] = {}
            for subcategory_name in self.settings_groups[file_name]:
                selected[file_name][subcategory_name] = []
                for setting_name in self.settings_groups[file_name][subcategory_name]:
                    if self.settings_groups[file_name][subcategory_name][setting_name].isChecked():
                        selected[file_name][subcategory_name].append(setting_name)
        return selected
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.title_bar.underMouse():
            self.dragging = True
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        if self.dragging and event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_position)
            event.accept()
    
    def mouseReleaseEvent(self, event):
        self.dragging = False
    
    def update_theme_style(self):
        colors = {'text': '#F5F5F5', 'bg': '#111116', 'title_bg': '#2D2D2D'} if is_dark_theme else {'text': '#111116', 'bg': '#F5F5F5', 'title_bg': '#E0E0E0'}
        self.setStyleSheet(f"""
            QDialog {{ background-color: {colors['bg']}; border-radius: 5px; }}
            #CustomTitleBar {{ background-color: {colors['title_bg']}; }}
            #TitleLabel {{ color: {colors['text']}; font-weight: bold; padding: 5px; }}
            #CloseButton {{ 
                background-color: transparent; 
                color: {colors['text']}; 
                border-radius: 4px; 
                font-weight: bold; 
            }}
            #CloseButton:hover {{ background-color: #ff4d4d; color: white; }}
            QLabel, QPushButton, QCheckBox {{ color: {colors['text']}; }}
        """)
        
        # 设置标题栏颜色（仅Windows系统）
        if os.name == 'nt':
            try:
                import ctypes
                hwnd = int(self.winId())
                bg_color = colors['bg'].lstrip('#')
                rgb_color = int(f'FF{bg_color}', 16) if len(bg_color) == 6 else int(bg_color, 16)
                
                ctypes.windll.dwmapi.DwmSetWindowAttribute(
                    ctypes.c_int(hwnd), 35,
                    ctypes.byref(ctypes.c_uint(rgb_color)),
                    ctypes.sizeof(ctypes.c_uint)
                )
            except Exception as e:
                logger.error(f"设置标题栏颜色失败: {str(e)}")
