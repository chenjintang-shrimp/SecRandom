"""
URL处理器模块
用于处理通过URL协议启动SecRandom时的命令行参数
"""

import sys
import argparse
from loguru import logger
from PyQt5.QtWidgets import QApplication


class URLHandler:
    """URL处理器类"""
    
    def __init__(self):
        self.url_command = None
        self.parse_command_line()
    
    def parse_command_line(self):
        """解析命令行参数"""
        try:
            parser = argparse.ArgumentParser(description='SecRandom URL处理器')
            parser.add_argument('--url', type=str, help='通过URL协议启动的URL')
            
            # 只解析已知的参数，忽略其他参数
            args, unknown = parser.parse_known_args()
            
            if args.url:
                self.url_command = args.url
                logger.info(f"接收到URL命令: {self.url_command}")
            
        except Exception as e:
            logger.error(f"解析命令行参数失败: {str(e)}")
    
    def has_url_command(self):
        """检查是否有URL命令"""
        return self.url_command is not None
    
    def get_url_command(self):
        """获取URL命令"""
        return self.url_command
    
    def process_url_command(self, main_window=None):
        """处理URL命令"""
        if not self.has_url_command():
            return False
        
        try:
            url = self.get_url_command()
            logger.info(f"开始处理URL命令: {url}")
            
            if not url.startswith("secrandom://"):
                logger.error(f"无效的SecRandom URL: {url}")
                return False
            
            # 解析URL
            from urllib.parse import urlparse, parse_qs
            parsed_url = urlparse(url)
            path = parsed_url.path.strip('/')
            query_params = parse_qs(parsed_url.query)
            
            logger.info(f"URL路径: {path}")
            logger.info(f"URL参数: {query_params}")
            
            # 如果没有提供主窗口，尝试获取
            if main_window is None:
                main_window = self.get_main_window()
            
            if main_window is None:
                logger.error("找不到主窗口实例")
                return False
            
            # 界面映射字典
            interface_map = {
                "main": "show_main_window",
                "settings": "show_settings_window",
                "pumping": "show_pumping_window",
                "reward": "show_reward_window",
                "history": "show_history_window",
                "floating": "show_floating_window"
            }
            
            # 根据路径打开对应界面
            if path in interface_map:
                method_name = interface_map[path]
                if hasattr(main_window, method_name):
                    method = getattr(main_window, method_name)
                    method()
                    logger.info(f"通过URL成功打开界面: {path}")
                    
                    # 处理额外的参数
                    self.handle_additional_params(main_window, query_params)
                    
                    return True
                else:
                    logger.error(f"主窗口缺少方法: {method_name}")
            else:
                logger.error(f"未知的界面路径: {path}")
                
                # 显示可用路径
                available_paths = ", ".join(interface_map.keys())
                logger.info(f"可用的界面路径: {available_paths}")
            
            return False
            
        except Exception as e:
            logger.error(f"处理URL命令失败: {str(e)}")
            return False
    
    def handle_additional_params(self, main_window, query_params):
        """处理额外的URL参数"""
        try:
            # 处理action参数
            if 'action' in query_params:
                action = query_params['action'][0]
                logger.info(f"执行动作: {action}")
                
                # 根据动作执行相应操作
                if action == 'start' and hasattr(main_window, 'start_random_selection'):
                    main_window.start_random_selection()
                elif action == 'stop' and hasattr(main_window, 'stop_random_selection'):
                    main_window.stop_random_selection()
                elif action == 'reset' and hasattr(main_window, 'reset_selection'):
                    main_window.reset_selection()
            
        except Exception as e:
            logger.error(f"处理额外参数失败: {str(e)}")
    
    def get_main_window(self):
        """获取主窗口实例"""
        try:
            for widget in QApplication.topLevelWidgets():
                # 通过特征识别主窗口
                if hasattr(widget, 'update_focus_mode') or hasattr(widget, 'show_main_window'):
                    return widget
            return None
        except Exception as e:
            logger.error(f"获取主窗口失败: {str(e)}")
            return None
    
    def get_available_interfaces(self):
        """获取可用的界面列表"""
        return {
            "main": "主界面",
            "settings": "设置界面",
            "pumping": "抽人界面",
            "reward": "抽奖界面",
            "history": "历史记录界面",
            "floating": "浮窗界面"
        }
    
    def generate_url_examples(self):
        """生成URL使用示例"""
        examples = []
        interfaces = self.get_available_interfaces()
        
        for path, name in interfaces.items():
            examples.append(f"secrandom://{path} - 打开{name}")
        
        # 添加带参数的示例
        examples.extend([
            "secrandom://pumping?action=start - 开始抽人",
            "secrandom://reward?action=stop - 停止抽奖"
        ])
        
        return examples


# 全局URL处理器实例
url_handler = URLHandler()


def get_url_handler():
    """获取全局URL处理器实例"""
    return url_handler


def process_url_if_exists(main_window=None):
    """如果存在URL命令则处理"""
    handler = get_url_handler()
    if handler.has_url_command():
        return handler.process_url_command(main_window)
    return False


if __name__ == "__main__":
    # 测试URL处理器
    handler = URLHandler()
    
    if handler.has_url_command():
        print(f"URL命令: {handler.get_url_command()}")
    else:
        print("没有URL命令")
    
    # 显示可用界面
    interfaces = handler.get_available_interfaces()
    print("\n可用界面:")
    for path, name in interfaces.items():
        print(f"  {path}: {name}")
    
    # 显示URL示例
    examples = handler.generate_url_examples()
    print("\nURL使用示例:")
    for example in examples:
        print(f"  {example}")