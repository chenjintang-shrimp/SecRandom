# ==================================================
# 全局变量模块
# ==================================================

from PyQt5.QtCore import *
from PyQt5.QtNetwork import *

import threading
from loguru import logger

from app.view.settings import settings_Window

class GlobalVars:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(GlobalVars, cls).__new__(cls)
                    cls._instance.settingInterface = None
                    cls._instance.creatingSettingInterface = False
        return cls._instance
        
    def create_setting_instance(self):
        """创建设置界面实例
        使用QTimer异步创建设置界面的实例，不显示界面"""
        
        # 检查是否已经在创建中
        if self.creatingSettingInterface:
            logger.warning("设置界面实例已在创建中，跳过")
            return
            
        self.creatingSettingInterface = True
        
        # 使用QTimer异步创建界面，避免阻塞主线程
        QTimer.singleShot(0, self._create_setting_instance_async)
    
    def _create_setting_instance_async(self):
        """异步创建设置界面实例的实际实现"""
        try:
            # 创建设置界面实例
            self.settingInterface = settings_Window(self)
            self.settingInterface.setObjectName("settingInterface")
            self.settingInterface.hide()
            # logger.debug("设置界面实例异步创建完成")
        except Exception as e:
            logger.error(f"创建设置界面实例时发生异常: {e}")
            import traceback
            logger.error(f"异常详情: {traceback.format_exc()}")
        finally:
            self.creatingSettingInterface = False
    
    def _handle_new_connection(self, confirmation):
        """处理新的连接"""
        logger.debug(f"收到新连接确认: {confirmation}，当前设置界面实例: {self.settingInterface}")
        if confirmation == "show_setting_interface":
            logger.debug(f"准备显示设置界面，settingInterface类型: {type(self.settingInterface)}")
            if self.settingInterface:
                if self.settingInterface.isVisible() and not self.settingInterface.isMinimized():
                    self.settingInterface.showNormal() 
                    self.settingInterface.activateWindow()
                    self.settingInterface.raise_()
                else:
                    if self.settingInterface.isMinimized():
                        self.settingInterface.showNormal()
                        self.settingInterface.activateWindow()
                        self.settingInterface.raise_()
                    else:
                        self.settingInterface.show()
                        self.settingInterface.activateWindow()
                        self.settingInterface.raise_()
        elif confirmation == "hide_setting_interface":
            if self.settingInterface:
                self.settingInterface.hide()

    # 获取设置界面实例
    def get_setting_interface(self, create_if_not_exists=False):
        """获取设置界面实例"""
        # 确保设置界面实例存在
        if self.settingInterface is None:
            self.create_setting_instance()

        if create_if_not_exists:
            show_request = "show_setting_interface"
        else:
            show_request = "hide_setting_interface"
        
        self._handle_new_connection(show_request)
        
        # 返回设置界面实例
        return self.settingInterface
