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
from PyQt5.QtCore import QObject, pyqtSignal, QTimer, QFileSystemWatcher, QCoreApplication

# 内部模块
from app.common.path_utils import ensure_dir, path_manager


# ==================================================
# 消息接收类
# ==================================================
class MessageReceiver(QObject):
    """消息接收类，负责监听文件系统变化，接收来自其他进程的 JSON 消息"""

    # 定义信号
    json_message_received = pyqtSignal(dict)  # 接收到 JSON 消息时发射

    def __init__(self, parent=None):
        """初始化消息接收器"""
        super().__init__(parent)
        # 设置临时目录和文件路径
        self.temp_dir = tempfile.gettempdir()
        self.json_file = os.path.join(self.temp_dir, "SecRandom_message_received.json")
        self.unread_file = os.path.join(self.temp_dir, "SecRandom_unread_received")
        
        # 创建文件系统监视器和定时器
        self.file_watcher = QFileSystemWatcher(self)
        
        # 创建消息检查定时器，每500ms检查一次
        self.message_check_timer = QTimer(self)
        self.message_check_timer.timeout.connect(self.check_for_messages)
        self.message_check_timer.start(500)  # 每500ms触发一次
        
        # 需要发射信号的消息类型
        self.emit_signal_types = ["class_status"]
        
        # 初始化监视器
        self._setup_watcher()
    
    # ===== 文件监视方法 =====
    
    def _setup_watcher(self):
        """设置文件监视器"""
        try:
            # 检查是否存在 QCoreApplication 实例
            if not QCoreApplication.instance():
                logger.error("QCoreApplication 实例不存在，QFileSystemWatcher 可能无法正常工作")
                return
            
            # 确保临时目录存在
            ensure_dir(self.temp_dir)
            
            # 清除现有监视路径
            if self.file_watcher.files():
                self.file_watcher.removePaths(self.file_watcher.files())
            if self.file_watcher.directories():
                self.file_watcher.removePaths(self.file_watcher.directories())
            
            # 监视临时目录
            if not self.file_watcher.addPath(self.temp_dir):
                logger.error(f"无法监视临时目录: {self.temp_dir}")
            
            # 监视 unread 文件（如果存在）
            if os.path.exists(self.unread_file):
                if not self.file_watcher.addPath(self.unread_file):
                    logger.error(f"无法监视文件: {self.unread_file}")
            
            # 连接文件变化信号
            if not self.file_watcher.receivers(self.file_watcher.fileChanged):
                self.file_watcher.fileChanged.connect(self._on_file_changed)
            
            # logger.debug("文件监视器设置完成")
        except Exception as e:
            logger.error(f"设置文件监视器失败: {e}")

    def _on_file_changed(self, path: str):
        """文件变化处理函数"""
        try:
            # 如果是 unread 文件发生变化，检查是否有新消息
            if path == self.unread_file:
                self.check_for_messages()
            # 如果是 json 文件发生变化，也检查是否有新消息
            elif path == self.json_file:
                self.check_for_messages()
        except Exception as e:
            logger.error(f"处理文件变化失败: {e}")
    
    # ===== 消息检查和处理方法 =====
    
    def check_for_messages(self):
        """检查是否有新消息"""
        try:
            # 检查 unread 文件是否存在
            if os.path.exists(self.unread_file):
                # 读取消息内容
                if os.path.exists(self.json_file):
                    try:
                        # 使用 utf-8-sig 编码处理可能带有 BOM 的文件
                        with open(self.json_file, "r", encoding="utf-8-sig") as f:
                            message_content = f.read().strip()
                        
                        if message_content:
                            # 处理消息
                            self._process_message(message_content)
                        else:
                            # logger.warning("消息内容为空")
                            pass
                        
                        # 删除 unread 文件，表示消息已处理
                        try:
                            os.remove(self.unread_file)
                            # logger.debug(f"已删除 {self.unread_file} 文件")
                        except Exception as e:
                            logger.error(f"删除 {self.unread_file} 文件失败: {e}")
                    except Exception as e:
                        logger.error(f"读取消息文件失败: {e}")
                else:
                    # logger.warning(f"消息文件 {self.json_file} 不存在")
                    pass
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
                else:
                    # logger.debug("消息不是字典格式，已忽略")
                    pass
            except json.JSONDecodeError as e:
                # 如果是 UTF-8 BOM 问题，尝试移除 BOM 后再解析
                if content.startswith('\ufeff'):
                    try:
                        # 移除 BOM 后再尝试解析
                        clean_content = content[1:]
                        data = json.loads(clean_content)
                        if isinstance(data, dict):
                            # 处理 JSON 消息
                            self._handle_json_message(data)
                        else:
                            # logger.debug("消息不是字典格式，已忽略")
                            pass
                    except json.JSONDecodeError as e2:
                        logger.error(f"移除 BOM 后仍无法解析 JSON 消息，已忽略: {e2}")
                else:
                    # 不是 BOM 问题，记录原始错误
                    # logger.debug(f"收到非 JSON 格式消息，已忽略: {e}")
                    pass
        except Exception as e:
            logger.error(f"处理消息失败: {e}")
    
    # ===== 消息类型处理方法 =====
    
    def _handle_json_message(self, data: Dict[str, Any]):
        """处理 JSON 消息"""
        try:
            # 根据 type 字段处理不同类型的消息
            message_type = data.get("type", "")
            
            # 使用消息处理器字典来处理不同类型的消息
            if message_type in self.emit_signal_types:
                self.json_message_received.emit(data)
                # logger.debug(f"已发射 JSON 消息信号，类型: {message_type}")
        except Exception as e:
            logger.error(f"处理 JSON 消息失败: {e}")

# ==================================================
# 全局实例
# ==================================================

# 全局消息接收器实例（懒加载）
_message_receiver_instance = None

def get_message_receiver():
    """获取消息接收器实例（懒加载）"""
    global _message_receiver_instance
    if _message_receiver_instance is None:
        # 检查是否存在 QCoreApplication 实例
        if not QCoreApplication.instance():
            logger.error("QCoreApplication 实例不存在，MessageReceiver 可能无法正常工作")
        _message_receiver_instance = MessageReceiver()
    return _message_receiver_instance

# 延迟创建全局消息接收器实例，确保在QApplication实例创建之后
message_receiver = None

def init_message_receiver():
    """初始化消息接收器实例，应在QApplication实例创建后调用"""
    global message_receiver
    if message_receiver is None:
        message_receiver = get_message_receiver()
    return message_receiver