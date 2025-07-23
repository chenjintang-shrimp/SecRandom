import os
import sys
import json

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtNetwork import *
from qfluentwidgets import *

from app.common.config import cfg
from app.view.SecRandom import Window 
from loguru import logger

log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

logger.configure(patcher=lambda record: record)

logger.add(
    os.path.join(log_dir, "SecRandom_{time:YYYY-MM-DD}.log"),
    rotation="1 MB",
    encoding="utf-8",
    retention="30 days",
    format="{time:YYYY-MM-DD HH:mm:ss:SSS} | {level} | {name}:{function}:{line} - {message}",
    enqueue=True,  # 启用异步日志记录
    compression="tar.gz", # 启用压缩
    backtrace=True,  # 启用回溯信息
    diagnose=True,  # 启用诊断信息
    catch=True  # 捕获未处理的异常
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

# 常量定义
APP_PROTOCOL = 'secrandom://'
IPC_SERVER_NAME = 'SecRandomIPC'
SHARED_MEMORY_KEY = 'SecRandom'


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
    socket.connectToServer(IPC_SERVER_NAME)

    if socket.waitForConnected(1000):
        if url_arg:
            socket.write(url_arg.encode())
        else:
            socket.write(b"show")
        socket.flush()
        socket.waitForBytesWritten(1000)
        socket.disconnectFromServer()
        return True
    return False


# 主逻辑开始
url_protocol_enabled = load_url_protocol_setting()
url_arg = parse_url_arg(sys.argv) if url_protocol_enabled else None

# 共享内存检测单实例
shared_memory = QSharedMemory(SHARED_MEMORY_KEY)
if not shared_memory.create(1):
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
from app.common.history_cleaner import clean_expired_history, clean_expired_reward_history
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

# 处理更新通知点击事件
if url_arg == "secrandom://update":
    from app.common.update_dialog import UpdateDialog
    dialog = UpdateDialog(sec)
    dialog.exec_()

try:
    app.exec_()
finally:
    shared_memory.detach()
    sys.exit()