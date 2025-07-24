# 标准库
import os
import sys
import json
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

# 确保日志目录存在
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

logger.configure(patcher=lambda record: record)

logger.add(
    os.path.join(LOG_DIR, "SecRandom_{time:YYYY-MM-DD}.log"),
    rotation="1 MB",
    encoding="utf-8",
    retention="30 days",
    format="{time:YYYY-MM-DD HH:mm:ss:SSS} | {level} | {name}:{function}:{line} - {message}",
    enqueue=True,  # 启用异步日志记录
    compression="tar.gz", # 启用压缩
    backtrace=True,  # 启用回溯信息
    diagnose=True,  # 启用诊断信息
    catch=True,  # 捕获未处理的异常
    delay=True  # 延迟文件打开以避免重启时的文件锁定
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

app = QApplication(sys.argv)

def load_url_protocol_setting():
    """加载URL协议启用设置"""
    try:
        with open('app/Settings/Settings.json', 'r', encoding='utf-8') as f:
            settings = json.load(f)
            return settings.get('foundation', {}).get('url_protocol_enabled', False)
    except (FileNotFoundError, json.JSONDecodeError):
        return False


def parse_url_arg(args, protocol_prefix=APP_PROTOCOL):
    """解析命令行参数中的URL协议"""
    for arg in args:
        if arg.startswith(protocol_prefix):
            return arg
    return None


def send_ipc_message(url_arg=None):
    """向已有实例发送IPC消息"""
    socket = QLocalSocket()
    logger.info(f"尝试连接到IPC服务器: {IPC_SERVER_NAME}")
    socket.connectToServer(IPC_SERVER_NAME)

    if socket.waitForConnected(1000):
        logger.info(f"成功连接到IPC服务器，发送消息: {url_arg or 'show'}")
        if url_arg == "restart":
            socket.write(b"restart")
        elif url_arg:
            socket.write(url_arg.encode())
        else:
            socket.write(b"show")
        socket.flush()
        if socket.waitForBytesWritten(1000):
            logger.info("消息发送成功")
        else:
            logger.error("消息发送超时")
        socket.disconnectFromServer()
        return True
    else:
        logger.error(f"无法连接到IPC服务器: {socket.errorString()}")
        return False


# 主逻辑开始
url_protocol_enabled = load_url_protocol_setting()
url_arg = parse_url_arg(sys.argv) if url_protocol_enabled else None

# 共享内存检测单实例 - 添加重试机制
shared_memory = QSharedMemory(SHARED_MEMORY_KEY)
max_retries = 10
retry_delay = 2  # 秒 (增加重试次数和延迟时间)
instance_detected = False

for attempt in range(max_retries):
    if shared_memory.create(1):
        logger.info(f"共享内存创建成功 (尝试 {attempt + 1}/{max_retries})")
        instance_detected = False
        break
    else:
        logger.error(f"共享内存创建失败 (尝试 {attempt + 1}/{max_retries}): {shared_memory.errorString()}")
        instance_detected = True
        if attempt < max_retries - 1:
            time.sleep(retry_delay)

if instance_detected:
    logger.debug('检测到已有 SecRandom 实例运行')

    # 尝试直接发送IPC消息
    if send_ipc_message(url_arg):
        sys.exit()

    # IPC连接失败，显示对话框
    def retry_ipc():
        """重试IPC连接"""
        new_url_arg = parse_url_arg(sys.argv) if load_url_protocol_setting() else None
        if not send_ipc_message(new_url_arg):
            logger.error("无法连接到已有实例")
            
    sys.exit()

logger.info("软件启动")
logger.info(f"软件作者: lzy98276")
logger.info(f"软件Github地址: https://github.com/SECTL/SecRandom")

# 清理过期历史记录
clean_expired_history()
clean_expired_reward_history()

sec = Window()
try:
    with open('app/Settings/Settings.json', 'r', encoding='utf-8') as f:
        settings = json.load(f)
        foundation_settings = settings.get('foundation', {})
        self_starting_enabled = foundation_settings.get('self_starting_enabled', False)
        if not self_starting_enabled:
            sec.show()
except FileNotFoundError:
    logger.error("加载设置时出错: 文件不存在, 使用默认显示主窗口")
    sec.show()
except KeyError:
    logger.error("设置文件中缺少foundation键, 使用默认显示主窗口")
    sec.show()
except Exception as e:
    logger.error(f"加载设置时出错: {e}, 使用默认显示主窗口")
    sec.show()

def start_ipc_server():
    """启动IPC服务器以接收重启命令"""
    server = QLocalServer()
    if not server.listen(IPC_SERVER_NAME):
        logger.error(f"无法启动IPC服务器: {server.errorString()}")
        return False
    
    logger.info(f"IPC服务器启动，监听: {IPC_SERVER_NAME}")
    server.newConnection.connect(lambda: handle_new_connection(server))
    return True

def handle_new_connection(server):
    """处理新的IPC连接"""
    client_socket = server.nextPendingConnection()
    if not client_socket:
        logger.error("获取客户端连接失败")
        return
    client_socket.readyRead.connect(lambda: process_client_message(client_socket))
    client_socket.disconnected.connect(client_socket.deleteLater)
    logger.info("新的IPC客户端已连接")

def process_client_message(socket):
    """处理客户端发送的IPC消息"""
    data = socket.readAll().data().decode().strip()
    logger.info(f"收到IPC消息: {data}")
    if data == "restart":
        logger.info("开始处理重启命令...")
        try:
            restart_app()
        except Exception as e:
            logger.error(f"重启过程发生异常: {str(e)}", exc_info=True)
    socket.disconnectFromServer()

# 启动IPC服务器
start_ipc_server()

def restart_app():
    try:
        logger.info("读取加密设置文件")
        file_path = 'app/SecRandom/enc_set.json'
        logger.info(f"检查文件是否存在: {file_path}")
        if not os.path.exists(file_path):
            logger.error(f"加密设置文件不存在: {file_path}")
            # 尝试创建默认设置文件
            default_settings = {'hashed_set': {'start_password_enabled': False, 'restart_verification_enabled': False}}
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(default_settings, f)
            logger.info(f"已创建默认加密设置文件: {file_path}")
            settings = default_settings
        else:
            logger.info(f"文件存在，检查权限")
            if not os.access(file_path, os.R_OK):
                logger.error(f"没有读取权限: {file_path}")
                raise PermissionError(f"无法读取文件: {file_path}")
            with open(file_path, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                logger.info(f"成功加载设置文件，内容: {json.dumps(settings, ensure_ascii=False)[:100]}...")
            # 验证设置结构
        if 'hashed_set' not in settings:
            logger.warning("设置文件缺少hashed_set节点，使用默认值")
            settings['hashed_set'] = {}
        
        start_password_enabled = settings['hashed_set'].get('start_password_enabled', False)
        restart_verification_enabled = settings['hashed_set'].get('restart_verification_enabled', False)
        logger.info(f"密码验证设置 - start_password_enabled: {start_password_enabled}, restart_verification_enabled: {restart_verification_enabled}")
        
        if start_password_enabled and restart_verification_enabled:
            logger.info("启动密码验证对话框")
            dialog = PasswordDialog(None)
            if dialog.exec_() != QDialog.Accepted:
                logger.warning("用户取消重启操作")
                return
            logger.info("密码验证通过")
        else:
            logger.info("无需密码验证或验证已禁用")
    except Exception as e:
        logger.error(f"重启过程出错: {str(e)}", exc_info=True)
    # 使用新进程组启动，避免被当前进程退出影响
    try:
        logger.info(f"尝试启动新进程: {sys.executable} {' '.join(sys.argv)}")
        # 检查Python可执行文件路径
        if not os.path.exists(sys.executable):
            logger.error(f"Python可执行文件不存在: {sys.executable}")
            raise FileNotFoundError(f"Python可执行文件不存在: {sys.executable}")
        
        # 使用绝对路径和完整参数启动新进程
        python_path = os.path.abspath(sys.executable)
        cmd_args = [python_path] + sys.argv
        logger.info(f"完整启动命令: {subprocess.list2cmdline(cmd_args)}")
        
        # 使用独立进程组和窗口隐藏标志启动新进程
        # 重定向输出到日志文件以便调试
        try:
            # 重定向输出到日志文件以便调试
            log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
            os.makedirs(log_dir, exist_ok=True)
            logger.info(f"日志目录已确认: {log_dir}")
            log_file = os.path.join(log_dir, f"restart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
            
            with open(log_file, 'w', encoding='utf-8') as f:
                logger.info(f"尝试启动新进程，输出将写入: {log_file}")
                new_process = subprocess.Popen(
                    cmd_args,
                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS | subprocess.CREATE_NO_WINDOW,
                    cwd=os.getcwd(),
                    env=os.environ.copy(),
                    stdout=f,
                    stderr=subprocess.STDOUT
                )
            logger.info(f"新进程启动成功，PID: {new_process.pid}, 工作目录: {os.getcwd()}")
        except Exception as e:
            logger.error(f"启动新进程时发生异常: {str(e)}", exc_info=True)
            raise
    except subprocess.TimeoutExpired:
        logger.warning("新进程启动超时，但可能仍在运行")
    except Exception as e:
        logger.error(f"启动新进程失败: {str(e)}", exc_info=True)
        return
    
    # 强制退出当前进程前释放共享内存
    logger.info("准备强制退出当前进程，释放共享内存")
    global shared_memory
    # 详细日志记录共享内存状态
    logger.info(f"共享内存状态检查 - 存在: {'shared_memory' in globals()}, 已附加: {shared_memory.isAttached() if 'shared_memory' in globals() else False}")
    if 'shared_memory' in globals():
        if shared_memory.isAttached():
            shared_memory.detach()
            logger.info("共享内存已成功释放")
            logger.info(f"释放后状态 - 已附加: {shared_memory.isAttached()}")
            # 延长延迟时间确保共享内存完全释放
            import time
            time.sleep(5)  # 延长延迟至5秒确保资源完全释放
        else:
            logger.warning("共享内存未附加，无需释放")
    else:
        logger.error("共享内存变量不存在，无法释放")
    import os
    os._exit(0)

try:
    app.exec_()
finally:
    shared_memory.detach()
    sys.exit()