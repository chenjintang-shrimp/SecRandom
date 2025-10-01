# ==================================================
# 系统导入
# ==================================================

# 系统模块
import os
import tempfile
import json
import time
from typing import Union, Dict, List, Any, Optional, Callable

# 第三方库
from loguru import logger
from PyQt5.QtCore import QObject, pyqtSignal, QTimer, QFileSystemWatcher

# 内部模块
from app.common.path_utils import ensure_dir, path_manager


# ==================================================
# 消息接收类
# ==================================================
class MessageReceiver(QObject):
    """消息接收类，负责监听文件系统变化，接收来自其他进程的 JSON 消息"""

    # 定义信号
    json_message_received = pyqtSignal(dict)  # 接收到 JSON 消息时发射
    class_status_received = pyqtSignal(str, str)  # 接收到上课下课状态时发射 (状态类型, 状态内容)
    next_class_time_received = pyqtSignal(str)  # 接收到下一节课上课时间时发射

    def __init__(self, parent=None):
        """初始化消息接收器"""
        super().__init__(parent)
        
        # 设置临时目录和文件路径
        self.temp_dir = tempfile.gettempdir()
        self.json_file = os.path.join(self.temp_dir, "SecRandom_message_received.json")
        self.unread_file = os.path.join(self.temp_dir, "SecRandom_unread")
        
        # 创建文件系统监视器和定时器
        self.file_watcher = QFileSystemWatcher(self)
        self.check_timer = QTimer(self)
        self.check_timer.timeout.connect(self.check_for_messages)
        self.check_timer.start(300)  # 每300毫秒检查一次
        
        # 上次检查时间
        self.last_check_time = 0
        
        # 消息处理回调函数字典
        self.message_handlers = {
            "json": self._handle_json_message,                        # 处理 JSON 消息
            "class_status": self._handle_class_status,                # 处理上课下课状态消息
            "next_class_time": self._handle_next_class_time           # 处理下一节课上课时间消息
        }
        
        # 加载上课状态和下一节课时间
        self.is_in_class, self.next_class_time = self._load_class_status_and_time()
        
        # 初始化监视器
        self._setup_watcher()
        
        logger.debug(f"消息接收器已初始化，临时目录: {self.temp_dir}")
    
    # ===== 监听控制方法 =====
    
    def start_listening(self):
        """开始监听消息"""
        self.check_timer.start()
        logger.info("消息接收器已开始监听")

    def stop_listening(self):
        """停止监听消息"""
        self.check_timer.stop()
        logger.info("消息接收器已停止监听")

    def is_listening(self) -> bool:
        """检查是否正在监听消息"""
        return self.check_timer.isActive()
    
    # ===== 配置管理方法 =====
    
    def reload_config(self):
        """重新加载上课状态和下一节课时间配置"""
        self.is_in_class, self.next_class_time = self._load_class_status_and_time()
        logger.info("已重新加载上课状态和下一节课时间")
    
    def _load_class_status_and_time(self) -> tuple:
        """从配置文件加载上课状态和下一节课时间"""
        try:
            config_path = path_manager.get_settings_path("time_settings.json")
            
            if os.path.exists(config_path):
                with open(config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
                
                # 获取上课状态和下一节课时间
                class_session_config = config.get("class_session", {})
                is_in_class = class_session_config.get("is_in_class", False)
                next_class_time = class_session_config.get("next_class_time", "")
                
                logger.debug(f"已加载上课状态: {is_in_class}, 下一节课时间: {next_class_time}")
                return is_in_class, next_class_time
            else:
                logger.warning(f"配置文件不存在: {config_path}")
                return False, ""
        except Exception as e:
            logger.error(f"加载上课状态和下一节课时间失败: {e}")
            return False, ""

    def _save_class_status_and_time(self):
        """保存上课状态和下一节课时间到配置文件"""
        try:
            config_path = path_manager.get_settings_path("time_settings.json")
            
            if os.path.exists(config_path):
                with open(config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
                
                # 更新上课状态和下一节课时间
                if "class_session" not in config:
                    config["class_session"] = {}
                config["class_session"]["is_in_class"] = self.is_in_class
                config["class_session"]["next_class_time"] = self.next_class_time
                
                # 保存配置
                with open(config_path, "w", encoding="utf-8") as f:
                    json.dump(config, f, indent=4, ensure_ascii=False)
                
                logger.debug(f"已保存上课状态: {self.is_in_class}, 下一节课时间: {self.next_class_time}")
            else:
                logger.warning(f"配置文件不存在: {config_path}")
        except Exception as e:
            logger.error(f"保存上课状态和下一节课时间失败: {e}")
    
    # ===== 文件监视方法 =====
    
    def _setup_watcher(self):
        """设置文件监视器"""
        try:
            # 确保临时目录存在
            ensure_dir(self.temp_dir)
            
            # 监视临时目录
            if not self.file_watcher.addPath(self.temp_dir):
                logger.warning(f"无法监视临时目录: {self.temp_dir}")
            
            # 监视 unread 文件（如果存在）
            if os.path.exists(self.unread_file):
                if not self.file_watcher.addPath(self.unread_file):
                    logger.warning(f"无法监视文件: {self.unread_file}")
            
            # 连接文件变化信号
            self.file_watcher.fileChanged.connect(self._on_file_changed)
            
            logger.debug("文件监视器设置完成")
        except Exception as e:
            logger.error(f"设置文件监视器失败: {e}")

    def _on_file_changed(self, path: str):
        """文件变化处理函数"""
        try:
            # 如果是 unread 文件发生变化，检查是否有新消息
            if path == self.unread_file:
                self.check_for_messages()
        except Exception as e:
            logger.error(f"处理文件变化失败: {e}")
    
    # ===== 消息检查和处理方法 =====
    
    def check_for_messages(self):
        """检查是否有新消息"""
        try:
            # 避免频繁检查
            current_time = time.time()
            if current_time - self.last_check_time < 0.05:  # 50毫秒内不重复检查
                return
            
            self.last_check_time = current_time
            
            # 检查 unread 文件是否存在
            if os.path.exists(self.unread_file):
                # 读取消息内容
                if os.path.exists(self.json_file):
                    with open(self.json_file, "r", encoding="utf-8") as f:
                        message_content = f.read().strip()
                    
                    # 处理消息
                    self._process_message(message_content)
                    
                    # 删除 unread 文件，表示消息已处理
                    try:
                        os.remove(self.unread_file)
                        logger.debug("已删除 unread 文件")
                    except Exception as e:
                        logger.error(f"删除 unread 文件失败: {e}")
                else:
                    logger.warning("message.json 文件不存在")
        except Exception as e:
            logger.error(f"检查消息失败: {e}")

    def _process_message(self, content: str):
        """处理接收到的消息内容"""
        try:
            # 尝试解析为 JSON
            try:
                data = json.loads(content)
                if isinstance(data, dict):
                    # 处理 JSON 消息
                    self._handle_json_message(data)
            except json.JSONDecodeError:
                # 不是 JSON 格式，忽略
                logger.debug("收到非 JSON 格式消息，已忽略")
        except Exception as e:
            logger.error(f"处理消息失败: {e}")
    
    # ===== 消息类型处理方法 =====
    
    def _handle_json_message(self, data: Dict[str, Any]):
        """处理 JSON 消息"""
        try:
            # 发射 JSON 消息信号
            self.json_message_received.emit(data)
            
            # 根据 type 字段处理不同类型的消息
            message_type = data.get("type", "")
            
            if message_type == "class_status":
                status_type = data.get("status_type", "")
                status_content = data.get("content", "")
                
                # 发射上课下课状态信号
                self.class_status_received.emit(status_type, status_content)
                
                # 调用处理方法
                self._handle_class_status(status_type, status_content)
            
            elif message_type == "next_class_time":
                next_time = data.get("time", "")
                
                # 发射下一节课上课时间信号
                self.next_class_time_received.emit(next_time)
                
                # 调用处理方法
                self._handle_next_class_time(next_time)
            
            logger.debug(f"已处理 JSON 消息，类型: {message_type}")
        except Exception as e:
            logger.error(f"处理 JSON 消息失败: {e}")
    
    # ===== 消息处理回调方法 =====

    def _handle_class_status(self, status_type: str, status_content: str):
        """处理上课下课状态"""
        # 更新上课状态
        if status_type == "class_start":
            self.is_in_class = True
        elif status_type == "class_end":
            self.is_in_class = False
        
        # 保存上课状态和下一节课时间
        self._save_class_status_and_time()
        
        # 这个方法可以被子类重写，实现自定义处理逻辑
        pass

    def _handle_next_class_time(self, next_time: str):
        """处理下一节课上课时间"""
        # 更新下一节课时间
        self.next_class_time = next_time
        
        # 保存上课状态和下一节课时间
        self._save_class_status_and_time()
        
        # 发射信号
        self.next_class_time_received.emit(next_time)
        
        # 这个方法可以被子类重写，实现自定义处理逻辑
        pass

# ==================================================
# 全局实例
# ==================================================

# 创建全局消息接收器实例
message_receiver = MessageReceiver()