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

shared_memory = QSharedMemory("SecRandom")
if not shared_memory.create(1):
    logger.debug('检测到已有 SecRandom 实例运行')
    socket = QLocalSocket()
    socket.connectToServer("SecRandomIPC")

    url_arg = None
    # 读取设置文件中的URL协议启用状态
    url_protocol_enabled = False
    try:
        with open('app/Settings/Settings.json', 'r', encoding='utf-8') as f:
            settings = json.load(f)
            url_protocol_enabled = settings.get('foundation', {}).get('url_protocol_enabled', False)
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    if url_protocol_enabled:
        for arg in sys.argv:
            if arg.startswith('secrandom://'):
                url_arg = arg
                break

    if socket.waitForConnected(1000):
        if url_arg:
            socket.write(url_arg.encode())
        else:
            socket.write(b"show")
        socket.flush()
        socket.waitForBytesWritten(1000)
        socket.disconnectFromServer()
        sys.exit()
    else:
        def sec_():
            # 只有在URL协议已启用时才处理URL参数
            url_arg = None
            # 读取设置文件中的URL协议启用状态
            url_protocol_enabled = False
            try:
                with open('app/Settings/Settings.json', 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    url_protocol_enabled = settings.get('foundation', {}).get('url_protocol_enabled', False)
            except (FileNotFoundError, json.JSONDecodeError):
                pass
            if url_protocol_enabled:
                for arg in sys.argv:
                    if arg.startswith('secrandom://'):
                        url_arg = arg
                        break
            # 再次尝试IPC
            socket = QLocalSocket()
            socket.connectToServer("SecRandomIPC")
            if socket.waitForConnected(1000):
                if url_arg:
                    socket.write(url_arg.encode())
                else:
                    socket.write(b"show")
                socket.flush()
                socket.waitForBytesWritten(1000)
                socket.disconnectFromServer()
            else:
                logger.error("无法连接到已有实例")
            return

        w = Dialog(
            'SecRandom 正在运行',
            'SecRandom 已经在运行！您可以选择打开已有实例的窗口。'
            '\n(若您需要打开多个实例，请在下个版本中可以启用"允许程序多开"的设置选项)'
        )
        w.yesButton.setText("打开主窗口👀")
        w.cancelButton.setText("知道了(不打开主窗口)👌")
        w.yesButton.clicked.connect(lambda: sec_())
        w.setFixedWidth(550)
        w.exec()
        sys.exit()

logger.info("软件启动")
logger.info(f"软件作者: lzy98276")
logger.info(f"软件Github地址: https://github.com/SECTL/SecRandom")

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

try:
    app.exec_()
finally:
    shared_memory.detach()
    sys.exit()