# 标准库
import os
import sys
import time
import json
import datetime
import subprocess

# 第三方库
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtNetwork import *
from qfluentwidgets import *
from loguru import logger

# 本地模块
from app.common.config import cfg
from app.view.SecRandom import Window 
from app.common.history_cleaner import clean_expired_history, clean_expired_reward_history
from app.common.password_dialog import PasswordDialog

# 常量定义
APP_PROTOCOL = 'secrandom://'
IPC_SERVER_NAME = 'SecRandomIPC'
SHARED_MEMORY_KEY = 'SecRandom'
LOG_DIR = "logs"

# 初始化日志
os.makedirs(LOG_DIR, exist_ok=True)
logger.configure(patcher=lambda record: record)
logger.add(
    os.path.join(LOG_DIR, "SecRandom_{time:YYYY-MM-DD}.log"),
    rotation="1 MB", encoding="utf-8", retention="30 days",
    format="{time:YYYY-MM-DD HH:mm:ss:SSS} | {level} | {name}:{function}:{line} - {message}",
    enqueue=True, compression="tar.gz", backtrace=True, diagnose=True, catch=True, delay=True
)

if cfg.get(cfg.dpiScale) == "Auto":
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
else:
    os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "0"
    os.environ["QT_SCALE_FACTOR"] = str(cfg.get(cfg.dpiScale))

try:
    with open('app/SecRandom/enc_set.json', 'r', encoding='utf-8') as f:
        settings = json.load(f)
    settings['hashed_set']['verification_start'] = False
    with open('app/SecRandom/enc_set.json', 'w', encoding='utf-8') as f:
        json.dump(settings, f, ensure_ascii=False, indent=4)
except Exception as e:
    logger.error(f"写入verification_start失败: {e}")

def main():
    # 单实例检测
    url_protocol_enabled = load_url_protocol_setting()
    url_arg = parse_url_arg(sys.argv) if url_protocol_enabled else None

    shared_memory = QSharedMemory(SHARED_MEMORY_KEY)
    max_retries, retry_delay = 3, 0.2
    instance_detected = True

    for attempt in range(max_retries):
        if shared_memory.create(1):
            logger.info(f"共享内存创建成功 (尝试 {attempt + 1}/{max_retries})")
            instance_detected = False
            break
        logger.error(f"共享内存创建失败 (尝试 {attempt + 1}/{max_retries}): {shared_memory.errorString()}")
        if attempt < max_retries - 1: time.sleep(retry_delay)

    if instance_detected:
        logger.debug('检测到已有 SecRandom 实例运行')
        if send_ipc_message(url_arg): sys.exit()
        sys.exit()

    # 初始化应用
    app = QApplication(sys.argv)
    shared_memory = None

    try:

        # 启动IPC服务器
        start_ipc_server(None)  # 临时传递None，后续会更新

        # 启动日志
        logger.info("软件启动")
        logger.info(f"软件作者: lzy98276")
        logger.info(f"软件Github地址: https://github.com/SECTL/SecRandom")

        # 清理历史记录
        clean_expired_history()
        clean_expired_reward_history()

        # 显示主窗口
        sec = Window()
        try:
            with open('app/Settings/Settings.json', 'r', encoding='utf-8') as f:
                settings = json.load(f)
                if not settings.get('foundation', {}).get('self_starting_enabled', False):
                    sec.show()
        except (FileNotFoundError, KeyError, Exception) as e:
            logger.error(f"加载设置时出错: {e}, 使用默认显示主窗口")
            sec.show()

        # 更新IPC服务器的主窗口引用
        for server in QLocalServer.allServers():
            if server.serverName() == IPC_SERVER_NAME:
                server.newConnection.disconnect()
                server.newConnection.connect(lambda: handle_new_connection(server, sec))
                break

        return app.exec_()

    finally:
        if shared_memory and shared_memory.isAttached():
            shared_memory.detach()
            time.sleep(0.5)  # 等待共享内存完全释放
            logger.info("共享内存已释放并等待0.5秒")
            shared_memory.detach()
        sys.exit()


def load_url_protocol_setting():
    try:
        with open('app/Settings/Settings.json', 'r', encoding='utf-8') as f:
            return json.load(f).get('foundation', {}).get('url_protocol_enabled', False)
    except (FileNotFoundError, json.JSONDecodeError):
        return False


def parse_url_arg(args, protocol_prefix=APP_PROTOCOL):
    url = next((arg for arg in args if arg.startswith(protocol_prefix)), None)
    if url:
        # 提取协议后的路径部分并分割命令
        path = url[len(protocol_prefix):].split('?')[0]  # 忽略查询参数
        command = path.split('/')[0].lower()  # 获取第一个路径段并转为小写
        return command if command else None
    return None


def send_ipc_message(url_arg=None):
    socket = QLocalSocket()
    socket.setSocketOption(QLocalSocket.SendBufferSizeSocketOption, 4096)
    socket.setSocketOption(QLocalSocket.ReceiveBufferSizeSocketOption, 4096)
    logger.info(f"尝试连接到IPC服务器: {IPC_SERVER_NAME}")
    
    for attempt in range(2):
        socket.connectToServer(IPC_SERVER_NAME)
        if socket.waitForConnected(500):
            logger.info(f"成功连接到IPC服务器，发送消息: {url_arg or 'show'}")
            socket.write(b"restart" if url_arg == "restart" else url_arg.encode() if url_arg else b"show")
            socket.flush()
            # 短暂等待确保数据发送完成
            socket.waitForBytesWritten(100)
            socket.disconnectFromServer()
            logger.info("消息已发送")
            return True
        logger.warning(f"连接尝试 {attempt+1} 失败: {socket.errorString()}")
        if attempt < 1:
            socket.abort()
            time.sleep(0.1)
    
    logger.error("所有连接尝试均失败")
    return False


def start_ipc_server(main_window):
    server = QLocalServer()
    if not server.listen(IPC_SERVER_NAME):
        logger.error(f"无法启动IPC服务器: {server.errorString()}")
        return False
    
    logger.info(f"IPC服务器启动，监听: {IPC_SERVER_NAME}")
    server.newConnection.connect(lambda: handle_new_connection(server, main_window))
    return True


def handle_new_connection(server, main_window):
    client_socket = server.nextPendingConnection()
    if not client_socket:
        logger.error("获取客户端连接失败")
        return
    client_socket.readyRead.connect(lambda: process_client_message(client_socket, main_window))
    client_socket.disconnected.connect(client_socket.deleteLater)
    logger.info("新的IPC客户端已连接")


def process_client_message(socket, main_window):
    data = socket.readAll().data().decode().strip()
    logger.info(f"收到IPC消息: {data}")
    if data == "restart":
        logger.info("开始处理重启命令...")
        try:
            restart_app()
            logger.info("重启命令处理完成")
        except Exception as e:
            logger.error(f"重启过程发生异常: {str(e)}", exc_info=True)
    elif data == "show":
        if main_window is None:
            logger.warning("主窗口尚未初始化，无法处理显示命令")
            return
        logger.info("收到显示窗口命令，激活主窗口")
        main_window.show()
        main_window.raise_()
        main_window.activateWindow()
    socket.disconnectFromServer()


def restart_app():
    try:
        file_path = 'app/SecRandom/enc_set.json'
        if not os.path.exists(file_path):
            logger.error(f"加密设置文件不存在，创建默认文件: {file_path}")
            settings = {'hashed_set': {'start_password_enabled': False, 'restart_verification_enabled': False}}
            with open(file_path, 'w', encoding='utf-8') as f: json.dump(settings, f)
        else:
            if not os.access(file_path, os.R_OK):
                raise PermissionError(f"无法读取文件: {file_path}")
            with open(file_path, 'r', encoding='utf-8') as f: settings = json.load(f)
            settings.setdefault('hashed_set', {})
            logger.info(f"加载设置文件: {json.dumps(settings, ensure_ascii=False)[:100]}...")

        verify = settings['hashed_set'].get('start_password_enabled', False) and settings['hashed_set'].get('restart_verification_enabled', False)
        logger.info(f"密码验证设置: {verify}")

        if verify and PasswordDialog(None).exec_() != QDialog.Accepted:
            logger.warning("用户取消重启操作")
            return
        logger.info(verify and "密码验证通过" or "无需密码验证")
    except Exception as e:
        logger.error(f"重启过程出错: {str(e)}", exc_info=True)
        return

    # 启动新进程
    try:
        if not os.path.exists(sys.executable):
            raise FileNotFoundError(f"Python可执行文件不存在: {sys.executable}")

        cmd_args = [os.path.abspath(sys.executable)] + sys.argv
        logger.info(f"启动命令: {subprocess.list2cmdline(cmd_args)}")

        log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, f"restart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

        with open(log_file, 'w', encoding='utf-8') as f:
            new_process = subprocess.Popen(
                cmd_args,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
                cwd=os.getcwd(),
                env=os.environ.copy(),
                stdout=f,
                stderr=subprocess.STDOUT
            )
        logger.info(f"新进程启动成功，PID: {new_process.pid}, 日志: {log_file}")
    except Exception as e:
        logger.error(f"启动新进程失败: {str(e)}", exc_info=True)
        return

    # 释放资源并退出
    logger.info("准备退出当前进程")
    global shared_memory
    try:
        if shared_memory and shared_memory.isAttached():
            shared_memory.detach()
            logger.info("共享内存已释放")
    except Exception as e:
        logger.error(f"释放共享内存异常: {str(e)}")
    finally:
        if shared_memory: shared_memory.detach()
        os._exit(0)

if __name__ == '__main__':
    main()