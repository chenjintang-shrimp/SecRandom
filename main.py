# ==================================================
# SecRandom 主程序文件
# ==================================================

# ==================================================
# 系统工具导入
# ==================================================
import os
import sys
import json
import time
import multiprocessing

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# ==================================================
# 第三方库导入
# ==================================================
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtNetwork import *
from qfluentwidgets import *
from loguru import logger
from pathlib import Path

# ==================================================
# 内部模块导入
# ==================================================
from app.common.config import cfg, VERSION, load_custom_font, WEBSITE, APPLY_NAME
from app.view.startup_window import StartupWindow
from app.view.settings import settings_Window
from app.view.SecRandom import Window
from app.common.url_handler import process_url_if_exists
from app.common.path_utils import path_manager, ensure_dir, open_file, file_exists
from qfluentwidgets import qconfig, Theme

# ==================================================
# 常量定义
# ==================================================
C_SE = 'SecRandomIPC'  # IPC通讯服务器名称
SHARED_MEMORY_KEY = 'SecRandom'   # 共享内存密钥

# ==================================================
# 日志配置相关函数
# ==================================================
def configure_logging():
    """配置日志系统"""
    # 确保日志目录存在
    log_dir = Path(os.path.dirname(os.path.abspath(__file__))) / 'logs'
    log_dir.mkdir(exist_ok=True)
    
    # 配置日志格式
    logger.add(
        log_dir / "SecRandom_{time:YYYY-MM-DD-HH-mm-ss}.log",
        rotation="1 MB",
        retention="30 days",
        compression="tar.gz",  # 启用压缩
        backtrace=True,  # 启用回溯信息
        diagnose=True,  # 启用诊断信息
        catch=True  # 捕获未处理的异常
    )

    logger.info("=" * 50)
    logger.info("日志系统配置完成")

def log_software_info():
    """记录软件启动成功信息和相关元信息"""
    # 打印分隔线，增强日志可读性
    logger.info("=" * 50)
    # 记录软件启动成功信息
    logger.info("软件启动成功")
    # 记录软件相关元信息
    software_info = {
        "作者": "lzy98276",
        "Github地址": "https://github.com/SECTL/SecRandom",
        "版本": VERSION
    }
    for key, value in software_info.items():
        logger.info(f"软件{key}: {value}")

# ==================================================
# IPC通信相关函数
# ==================================================
def send_ipc_message(url_command=None):
    """向已有实例发送IPC消息
    
    Args:
        url_command (str, optional): URL命令，如果有的话会传递给已有实例
    
    Returns:
        bool: 发送是否成功
    """
    try:
        # 创建本地socket连接
        socket = QLocalSocket()
        
        # 连接到IPC服务器
        socket.connectToServer(C_SE)
        
        # 等待连接建立
        if socket.waitForConnected(1000):  # 等待1秒
            # 构建要发送的消息
            if url_command:
                message = f"url:{url_command}"
            else:
                message = "show"
            
            # 发送消息
            socket.write(message.encode('utf-8'))
            socket.flush()
            
            # 等待消息发送完成
            if socket.waitForBytesWritten(1000):  # 等待1秒
                # 关闭连接
                socket.disconnectFromServer()
                if socket.state() == QLocalSocket.UnconnectedState or socket.waitForDisconnected(1000):
                    return True
            else:
                logger.error("IPC消息发送超时")
        else:
            logger.error(f"IPC连接失败: {socket.errorString()}")
        
        # 关闭连接
        socket.disconnectFromServer()
        return False
    except Exception as e:
        logger.error(f"发送IPC消息时发生异常: {e}")
        return False

# ==================================================
# 单实例检查相关函数
# ==================================================
def check_single_instance():
    """检查单实例，防止多个程序副本同时运行
    
    Returns:
        QSharedMemory: 共享内存对象
    """
    shared_memory = QSharedMemory(SHARED_MEMORY_KEY)
    if not shared_memory.create(1):
        logger.info('检测到已有 SecRandom 实例正在运行')

        # 获取URL命令（如果存在）
        url_command = None
        try:
            from app.common.url_handler import get_url_handler
            url_handler = get_url_handler()
            if url_handler.has_url_command():
                url_command = url_handler.get_url_command()
                logger.info(f'检测到URL命令，将传递给已有实例: {url_command}')
        except Exception as e:
            logger.error(f'获取URL命令失败: {e}')

        # 尝试直接发送IPC消息唤醒已有实例
        if send_ipc_message(url_command):
            logger.info('成功唤醒已有实例，当前实例将退出')
            sys.exit()
        else:
            # IPC连接失败，短暂延迟后重试一次
            time.sleep(0.3)
            if not send_ipc_message(url_command):
                logger.error("无法连接到已有实例，程序将退出")
                sys.exit()
    
    logger.info('单实例检查通过，可以安全启动程序')
    
    return shared_memory

# ==================================================
# 字体设置相关函数
# ==================================================
def apply_font_settings():
    """应用字体设置，加载并应用保存的字体（后台创建，不阻塞进程）"""
    try:
        # 检查是否已经加载过字体，避免重复加载
        if hasattr(apply_font_settings, '_font_loaded') and apply_font_settings._font_loaded:
            logger.debug("字体已加载，跳过重复加载")
            return
            
        # 读取字体设置文件
        settings_file = path_manager.get_settings_path('custom_settings.json')
        ensure_dir(settings_file.parent)
        
        font_family = 'HarmonyOS Sans SC'  # 默认字体
        
        if file_exists(settings_file):
            try:
                with open_file(settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    personal_settings = settings.get('personal', {})
                    custom_font_family = personal_settings.get('font_family', '')
                    if custom_font_family:
                        font_family = custom_font_family
            except Exception as e:
                logger.error(f"读取字体设置失败: {e}")
        
        # 应用字体设置（后台创建，不阻塞进程）
        logger.info(f"字体设置: {font_family}")
        # 用QTimer在后台应用字体，不阻塞主进程
        QTimer.singleShot(0, lambda: apply_font_to_application(font_family))
        
        # 标记字体已加载
        apply_font_settings._font_loaded = True
    except Exception as e:
        logger.error(f"初始化字体设置失败: {e}")
        # 发生错误时使用默认字体
        logger.info("初始化字体设置: 发生错误，使用默认字体")
        # 用QTimer在后台应用字体，不阻塞主进程
        QTimer.singleShot(0, lambda: apply_font_to_application('HarmonyOS Sans SC'))

def apply_font_to_application(font_family):
    """应用字体设置到整个应用程序
    
    Args:
        font_family (str): 字体家族名称
    """
    try:
        # 检查是否已经应用过字体，避免重复应用
        if hasattr(apply_font_to_application, '_font_applied') and apply_font_to_application._font_applied == font_family:
            logger.debug(f"字体 {font_family} 已应用，跳过重复应用")
            return
            
        # 获取当前应用程序默认字体
        current_font = QApplication.font()
        
        # 创建字体对象，只修改字体家族，保持原有字体大小
        app_font = QFont(font_family)
        app_font.setPointSize(current_font.pointSize())
        
        # 如果是HarmonyOS Sans SC字体，使用特定的字体文件路径
        if font_family == "HarmonyOS Sans SC":
            # 检查字体是否已加载，避免重复加载
            if not hasattr(apply_font_to_application, '_harmony_font_loaded'):
                font_path = path_manager.get_font_path('HarmonyOS_Sans_SC_Bold.ttf')
                if font_path and path_manager.file_exists(font_path):
                    font_id = QFontDatabase.addApplicationFont(str(font_path))
                    if font_id >= 0:
                        font_families = QFontDatabase.applicationFontFamilies(font_id)
                        if font_families:
                            app_font = QFont(font_families[0])
                            app_font.setPointSize(current_font.pointSize())
                            # logger.debug(f"已加载HarmonyOS Sans SC字体文件: {font_path}")
                            # 标记字体已加载
                            apply_font_to_application._harmony_font_loaded = True
                        else:
                            logger.error(f"无法从字体文件获取字体家族: {font_path}")
                    else:
                        logger.error(f"无法加载字体文件: {font_path}")
                else:
                    logger.error(f"HarmonyOS Sans SC字体文件不存在: {font_path}")
            else:
                # 字体已加载，直接使用
                font_families = QFontDatabase.applicationFontFamilies(QFontDatabase.addApplicationFont(str(path_manager.get_font_path('HarmonyOS_Sans_SC_Bold.ttf'))))
                if font_families:
                    app_font = QFont(font_families[0])
                    app_font.setPointSize(current_font.pointSize())
        
        # 获取所有顶级窗口并更新它们的字体
        widgets_updated = 0
        for widget in QApplication.allWidgets():
            if isinstance(widget, QWidget):
                update_widget_fonts(widget, app_font)
                widgets_updated += 1
            
        # logger.debug(f"已应用字体: {font_family}, 更新了{widgets_updated}个控件字体")
        
        # 标记字体已应用
        apply_font_to_application._font_applied = font_family
    except Exception as e:
        logger.error(f"应用字体失败: {e}")

def update_widget_fonts(widget, font):
    """更新控件及其子控件的字体，优化版本减少内存占用
    
    Args:
        widget: 要更新字体的控件
        font: 要应用的字体
    """
    if widget is None:
        return
        
    try:
        # 获取控件当前字体
        current_widget_font = widget.font()
        
        # 创建新字体，只修改字体家族，保持原有字体大小和其他属性
        new_font = QFont(font.family(), current_widget_font.pointSize())
        # 保持原有字体的粗体和斜体属性
        new_font.setBold(current_widget_font.bold())
        new_font.setItalic(current_widget_font.italic())
        
        # 更新当前控件的字体
        widget.setFont(new_font)
        
        # 如果控件有子控件，递归更新子控件的字体
        if isinstance(widget, QWidget):
            children = widget.children()
            for child in children:
                if isinstance(child, QWidget):
                    update_widget_fonts(child, font)
    except Exception as e:
        logger.error(f"更新控件字体时发生异常: {e}")

# ==================================================
# 历史记录清理相关函数
# ==================================================
def clean_expired_data():
    """清理过期历史记录，避免阻塞启动过程"""
    # 使用QTimer在后台清理历史记录
    QTimer.singleShot(0, _clean_expired_data)
    logger.info("已启动后台任务清理过期历史记录")

def _clean_expired_data():
    """实际执行清理过期历史记录的函数"""
    try:
        from app.common.history_cleaner import clean_expired_history, clean_expired_reward_history
        clean_expired_history()
        clean_expired_reward_history()
    except Exception as e:
        logger.error(f"清理过期历史记录时出错: {e}")


# ==================================================
# 启动窗口相关函数
# ==================================================
def run_startup_window():
    """运行启动窗口的函数，用于在单独进程中显示启动窗口"""
    try:
        # 创建QApplication实例（如果还没有）
        app_startup = QApplication.instance()
        if app_startup is None:
            app_startup = QApplication(sys.argv)
        
        # 创建启动窗口实例
        startup_window = StartupWindow()
        
        # 显示启动窗口
        startup_window.show()
        
        # 创建本地服务器，用于接收主程序的进度更新
        server = QLocalServer()
        server_name = "SecRandomStartup"  # 使用简单名称，不包含路径
        server.listen(server_name)
        
        # 连接新连接信号
        server.newConnection.connect(lambda: handle_new_connection(server, startup_window))
        
        # 运行事件循环
        app_startup.exec_()
        
        # 关闭服务器
        server.close()
        
    except Exception as e:
        logger.error(f"启动窗口运行出错: {e}")
        # 确保应用程序实例退出
        app = QApplication.instance()
        if app is not None:
            app.quit()

def handle_new_connection(server, startup_window):
    """处理新的连接，接收主程序的进度更新"""
    socket = server.nextPendingConnection()
    if socket:
        # 连接readyRead信号
        socket.readyRead.connect(lambda: read_progress_update(socket, startup_window))
        # 连接disconnected信号
        socket.disconnected.connect(socket.deleteLater)

def read_progress_update(socket, startup_window):
    """读取进度更新并更新启动窗口"""
    while socket.bytesAvailable() > 0:
        data = socket.readAll().data().decode('utf-8')
        if data.startswith("progress:"):
            try:
                step_index = int(data.split(":")[1])
                if 0 <= step_index < len(startup_window.startup_steps):
                    step_name, _ = startup_window.startup_steps[step_index]
                    startup_window.set_step(step_index, step_name)
                    # logger.info(f"启动窗口进度更新: {step_name}")
            except (ValueError, IndexError) as e:
                logger.error(f"解析进度更新失败: {e}")
        elif data == "close":
            startup_window.close_startup()
            # 退出应用程序实例
            app = QApplication.instance()
            if app is not None:
                app.quit()

def update_startup_progress(step_index):
    """更新启动窗口进度
    
    Args:
        step_index (int): 步骤索引
    """
    try:
        # 创建本地socket连接
        socket = QLocalSocket()
        
        # 连接到启动窗口服务器
        server_name = "SecRandomStartup"  # 使用简单名称，不包含路径
        socket.connectToServer(server_name)
        
        # 等待连接建立
        if socket.waitForConnected(500):  # 等待0.5秒
            # 发送进度更新
            message = f"progress:{step_index}"
            socket.write(message.encode('utf-8'))
            socket.flush()
            
            # 等待消息发送完成
            socket.waitForBytesWritten(500)
            
            # 关闭连接
            socket.disconnectFromServer()
        else:
            # 连接失败，可能是启动窗口还未准备好
            # logger.debug(f"无法连接到启动窗口服务器: {socket.errorString()}")
            pass
        
        # 关闭连接
        socket.disconnectFromServer()
    except Exception as e:
        logger.error(f"更新启动窗口进度时发生异常: {e}")

def close_startup_window():
    """关闭启动窗口"""
    try:
        # 创建本地socket连接
        socket = QLocalSocket()
        
        # 连接到启动窗口服务器
        server_name = "SecRandomStartup"  # 使用简单名称，不包含路径
        socket.connectToServer(server_name)
        
        # 等待连接建立
        if socket.waitForConnected(500):  # 等待0.5秒
            # 发送关闭命令
            message = "close"
            socket.write(message.encode('utf-8'))
            socket.flush()
            
            # 等待消息发送完成
            socket.waitForBytesWritten(500)
            
            # 关闭连接
            socket.disconnectFromServer()
        
        # 关闭连接
        socket.disconnectFromServer()
    except Exception as e:
        logger.error(f"关闭启动窗口时发生异常: {e}")

# ==================================================
# 应用程序初始化相关函数
# ==================================================
def initialize_app():
    """初始化应用程序，使用QTimer避免阻塞主线程"""
    # 设置工作目录为程序所在目录，解决URL协议唤醒时工作目录错误的问题
    if getattr(sys, 'frozen', False):
        # 打包后的可执行文件
        program_dir = os.path.dirname(sys.executable)
    else:
        # 开发环境
        program_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 更改当前工作目录
    if os.getcwd() != program_dir:
        os.chdir(program_dir)
        logger.info(f"工作目录已设置为: {program_dir}")
    
    # 更新启动窗口进度 - 初始化应用程序环境
    update_startup_progress(0)
    
    # 更新启动窗口进度 - 配置日志系统
    update_startup_progress(1)
    
    # 检查单实例
    global shared_memory
    shared_memory = check_single_instance()
    
    # 更新启动窗口进度 - 检查单实例运行
    update_startup_progress(2)
    
    # 记录软件信息
    log_software_info()
    
    # 更新启动窗口进度 - 加载配置文件
    update_startup_progress(3)
    
    # 清理过期数据
    clean_expired_data()
    
    # 更新启动窗口进度 - 清理过期历史记录
    update_startup_progress(4)
    
    # 注册URL协议
    try:
        from app.common.foundation_settings import register_url_protocol_on_startup
        result = register_url_protocol_on_startup()
        if result:
            # logger.info("URL协议自动注册完成")
            pass
        else:
            # logger.info("URL协议注册失败或已跳过")
            pass
    except Exception as e:
        logger.error(f"注册URL协议时发生异常: {str(e)}")
    
    # 更新启动窗口进度 - 注册URL协议
    update_startup_progress(5)
    
    # 创建主窗口前先进行释放未使用的内存（不知道有没有用）
    import gc
    gc.collect()
    
    # 创建主窗口实例（窗口不会立即显示，等待所有组件加载完成）
    sec = Window()
    # 先隐藏窗口，等待所有组件加载完成后再显示
    sec.hide()
    
    # 更新启动窗口进度 - 创建主窗口
    update_startup_progress(6)
    
    # 将创建的主窗口保存到全局变量
    global main_window
    main_window = sec
    
    # 再次进行垃圾回收，释放创建窗口过程中产生的临时对象
    gc.collect()
    
    # 更新启动窗口进度 - 初始化界面组件
    update_startup_progress(7)
    
    # 处理URL命令
    process_url_if_exists()
    
    # 更新启动窗口进度 - 处理URL命令
    update_startup_progress(8)
    
    # 更新启动窗口进度 - 启动完成
    update_startup_progress(9)
    
    # 关闭启动窗口
    close_startup_window()
    
    # 等待启动窗口进程结束
    if startup_process.is_alive():
        startup_process.join(timeout=1.0)  # 最多等待1秒
    
    # 所有组件加载完成后，显示主窗口
    # 检查是否是开机自启动模式
    if hasattr(main_window, 'is_self_starting') and main_window.is_self_starting:
        logger.info("开机自启动模式，窗口已隐藏")
    else:
        main_window.show()
        logger.info("主窗口已显示")

# ==================================================
# 主程序入口
# ==================================================
def main_async():
    """主异步函数，用于启动应用程序"""
    # 延迟初始化应用程序
    QTimer.singleShot(200, lambda: initialize_app())
    QTimer.singleShot(300, apply_font_settings)

if __name__ == "__main__":
    # 重置全局变量
    main_window = None
    shared_memory = None
    
    # 创建QApplication实例
    app = QApplication(sys.argv)
    
    # 导入垃圾回收模块，用于优化内存使用
    import gc
    gc.enable()  # 确保垃圾回收已启用
    
    try:
        # 首先配置日志系统，确保日志能正确记录
        configure_logging()
        logger.info("日志系统配置完成")

        # 创建并显示启动窗口（在单独进程中）
        startup_process = multiprocessing.Process(target=run_startup_window)
        startup_process.daemon = True  # 设置为守护进程，主程序退出时自动结束
        startup_process.start()

        # 启动主函数
        main_async()
        
        # 启动应用程序事件循环
        app.exec_()
        
        # 在启动完成后进行一次垃圾回收
        gc.collect()
        
        # 退出程序
        sys.exit()
    except Exception as e:
        print(f"应用程序启动失败: {e}")
        # 记录错误日志
        try:
            logger.error(f"应用程序启动失败: {e}", exc_info=True)
        except:
            pass
        sys.exit(1)