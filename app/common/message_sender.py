# ==================================================
# 系统导入
# ==================================================

# 系统模块
import os
import tempfile
import json
import time
from typing import Dict, Any

# 第三方库
from loguru import logger

# 内部模块
from app.common.path_utils import ensure_dir


# ==================================================
# 消息发送类
# ==================================================
class MessageSender:
    """消息发送类
    负责通过文件系统与 ClassWidgets 插件进行通信，发送 JSON 格式的通知消息"""

    def __init__(self):
        """初始化消息发送器"""
        self.temp_dir = tempfile.gettempdir()
        self.json_file = os.path.join(self.temp_dir, "SecRandom_message_sent.json")
        self.unread_file = os.path.join(self.temp_dir, "SecRandom_unread")
        logger.debug(f"消息发送器已初始化，临时目录: {self.temp_dir}")

    def send_json_message(self, data: Dict[str, Any]) -> bool:
        """发送 JSON 格式的结构化消息"""
        try:
            # 将字典转换为 JSON 字符串
            json_str = json.dumps(data, ensure_ascii=False)
            
            # 将 JSON 内容写入 json_file 文件
            with open(self.json_file, "w", encoding="utf-8") as f:
                f.write(json_str)
            
            # 创建 unread 文件作为信号
            with open(self.unread_file, "w") as f:
                f.write("1")  # 内容不重要，文件存在即可
            
            logger.info(f"JSON 消息发送成功")
            return True
        except Exception as e:
            logger.error(f"发送 JSON 消息失败: {e}")
            return False

    def send_selection_result_json(self, selected_name: str, use_cwci_display_time: bool = False) -> bool:
        """发送 JSON 格式的抽选结果通知"""
        try:
            # 构建 JSON 消息
            data = {
                "type": "selection_result",
                "name": selected_name,
                "display_time": use_cwci_display_time,
                "time": time.strftime("%H:%M:%S")
            }
            
            # 发送 JSON 消息
            return self.send_json_message(data)
        except Exception as e:
            logger.error(f"发送 JSON 格式抽选结果失败: {e}")
            return False

    def send_reward_result_json(self, reward_name: str, use_cwci_display_time: bool = False) -> bool:
        """发送 JSON 格式的抽奖结果通知"""
        try:
            # 构建 JSON 消息
            data = {
                "type": "reward_result",
                "reward": reward_name,
                "display_time": use_cwci_display_time,
                "time": time.strftime("%H:%M:%S")
            }
            
            # 发送 JSON 消息
            return self.send_json_message(data)
        except Exception as e:
            logger.error(f"发送 JSON 格式抽奖结果失败: {e}")
            return False

    def send_custom_notification_json(self, title: str, content: str, notification_type: str = "custom") -> bool:
        """发送 JSON 格式的自定义通知"""
        try:
            # 构建 JSON 消息
            data = {
                "type": notification_type,
                "title": title,
                "content": content,
                "time": time.strftime("%H:%M:%S")
            }
            
            # 发送 JSON 消息
            return self.send_json_message(data)
        except Exception as e:
            logger.error(f"发送 JSON 格式自定义通知失败: {e}")
            return False


# ==================================================
# 全局实例
# ==================================================

# 创建全局消息发送器实例
message_sender = MessageSender()


# ==================================================
# 便捷函数
# ==================================================

def send_json_message(data: Dict[str, Any]) -> bool:
    """发送 JSON 格式的结构化消息的便捷函数"""
    return message_sender.send_json_message(data)

def send_selection_result_json(selected_name: str, use_cwci_display_time: bool = False) -> bool:
    """发送 JSON 格式的抽选结果通知的便捷函数"""
    return message_sender.send_selection_result_json(selected_name, use_cwci_display_time)

def send_reward_result_json(reward_name: str, use_cwci_display_time: bool = False) -> bool:
    """发送 JSON 格式的抽奖结果通知的便捷函数"""
    return message_sender.send_reward_result_json(reward_name, use_cwci_display_time)

def send_custom_notification_json(title: str, content: str, notification_type: str = "custom") -> bool:
    """发送 JSON 格式的自定义通知的便捷函数"""
    return message_sender.send_custom_notification_json(title, content, notification_type)