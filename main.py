# ==================================================
# 🔮 系统魔法工具 (System Magic Tools)
# ==================================================
import os
import sys
import json

# ==================================================
# 📚 第三方魔法书 (Third-Party Magic Books)
# ==================================================
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtNetwork import *
from qfluentwidgets import *
from loguru import logger

# ==================================================
# 📜 内部魔法卷轴 (Internal Magic Scrolls)
# ==================================================
from app.common.config import cfg
from app.view.SecRandom import Window

def send_ipc_message():
    """(^・ω・^ ) 白露的IPC信使魔法！
    正在向已运行的实例发送唤醒消息～ 就像传递小纸条一样神奇！
    如果成功连接，会发送'show'指令让窗口重新出现哦～ ✨"""
    socket = QLocalSocket()
    socket.connectToServer(IPC_SERVER_NAME)

    if socket.waitForConnected(1000):
        socket.write(b"show")
        socket.flush()
        socket.waitForBytesWritten(1000)
        socket.disconnectFromServer()
        logger.debug("白露信使: IPC消息发送成功～ ")
        return True
    logger.warning("白露信使: IPC连接失败，目标实例可能未响应～ ")
    return False


def configure_logging():
    """(^・ω・^ ) 白露的日志魔法师登场！
    正在设置魔法日志卷轴，让程序运行轨迹变得清晰可见～
    日志会自动按大小(1MB)和时间切割，保存30天并压缩归档哦～ 📜✨"""
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
        logger.info("白露魔法: 日志文件夹创建成功～ ")

    logger.configure(patcher=lambda record: record)

    logger.add(
        os.path.join(log_dir, "SecRandom_{time:YYYY-MM-DD}.log"),
        rotation="1 MB",
        encoding="utf-8",
        retention="30 days",
        format="{time:YYYY-MM-DD HH:mm:ss:SSS} | {level} | {name}:{function}:{line} - {message}",
        enqueue=True,  # 启用异步日志记录，像派出小信使一样高效
        compression="tar.gz", # 启用压缩魔法，节省存储空间～
        backtrace=True,  # 启用回溯信息，像魔法追踪器一样定位问题
        diagnose=True,  # 启用诊断信息，提供更详细的魔法检查报告
        catch=True  # 捕获未处理的异常，保护程序稳定运行～
    )
    logger.info("白露魔法: 日志系统配置完成，可以开始记录冒险啦～ ")

# ==================================================
# 📐 显示魔法调节 (Display Magic Adjustment)
# ==================================================
"""(^・ω・^ ) 白露的显示魔法调节！
根据设置自动调整DPI缩放模式，让界面显示更清晰舒适～
就像调整魔法放大镜的焦距一样神奇哦～ ✨"""
if cfg.get(cfg.dpiScale) == "Auto":
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    logger.debug("白露调节: DPI缩放已设置为自动模式～ ")
else:
    os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "0"
    os.environ["QT_SCALE_FACTOR"] = str(cfg.get(cfg.dpiScale))
    logger.debug(f"白露调节: DPI缩放已设置为{cfg.get(cfg.dpiScale)}倍～ ")

# 🌟 星穹铁道白露：设置Qt魔法插件路径，解决启动时插件缺失问题！
import PyQt5
import sys

# 🌟 星穹铁道白露：检测运行环境，区分开发和打包模式
if hasattr(sys, '_MEIPASS'):
    # ✨ 小鸟游星野：PyInstaller打包环境，使用临时目录路径
    # 尝试标准PyInstaller插件路径
      qt_plugin_path = os.path.join(sys._MEIPASS, 'plugins')
      # 如果标准路径不存在，回退到旧路径
      if not os.path.exists(qt_plugin_path):
          qt_plugin_path = os.path.join(sys._MEIPASS, 'PyQt5', 'Qt', 'plugins')
else:
    # 🌙 星穹铁道白露：开发环境，使用标准安装路径
    qt_install_path = os.path.dirname(PyQt5.__file__)
    qt_plugin_path = os.path.join(qt_install_path, "Qt", "plugins")

os.environ["QT_PLUGIN_PATH"] = qt_plugin_path

# 🌟 星穹铁道白露：设置平台插件路径并验证
platforms_path = os.path.join(qt_plugin_path, 'platforms')
os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = platforms_path
# 🌟 星穹铁道白露：显式指定Windows平台插件
os.environ["QT_QPA_PLATFORM"] = "windows"
  
# ✨ 小鸟游星野：检查平台插件目录是否存在
if os.path.exists(platforms_path):
    logger.debug(f"✅ 平台插件目录验证成功: {platforms_path}")
    # 🌟 星穹铁道白露：检查关键Windows平台插件文件
    qwindows_path = os.path.join(platforms_path, 'qwindows.dll')
    if os.path.exists(qwindows_path):
        logger.debug(f"✅ 找到Windows平台插件: {qwindows_path}")
    else:
        logger.critical(f"❌ 缺少关键插件文件: {qwindows_path}")
    # ✨ 小鸟游星野：列出目录内容帮助诊断
    if os.listdir(platforms_path):
        logger.debug(f"📁 发现插件: {os.listdir(platforms_path)}")
    else:
        logger.warning(f"⚠️ 平台插件目录为空: {platforms_path}")
else:
    logger.error(f"❌ 平台插件目录不存在: {platforms_path}")

qt_bin_path = os.path.join(os.path.dirname(qt_plugin_path), "bin")
os.environ["PATH"] = qt_bin_path + os.pathsep + os.environ["PATH"]
logger.debug(f"🔮 双生魔法：Qt插件路径={qt_plugin_path}，二进制路径={qt_bin_path}")

# ==================================================
# 🔐 验证状态初始化 (Verification Status Initialization)
# ==================================================
"""(ﾟДﾟ≡ﾟдﾟ) 星野的安全验证初始化！
正在重置验证状态标记，确保程序启动时处于安全状态喵～
这是防止重复验证的魔法保护措施哦～ 🔒"""
try:
    with open('app/SecRandom/enc_set.json', 'r', encoding='utf-8') as f:
        settings = json.load(f)
    settings['hashed_set']['verification_start'] = False
    with open('app/SecRandom/enc_set.json', 'w', encoding='utf-8') as f:
        json.dump(settings, f, ensure_ascii=False, indent=4)
    logger.info("星野安全: verification_start状态已成功重置为False喵～")
except Exception as e:
    logger.error(f"星野错误: 写入verification_start失败喵～ {e}")

# ==================================================
# 🔮 魔法常量定义 (Magic Constants Definition)
# ==================================================
"""(^・ω・^ ) 白露的魔法常量簿！
定义程序中需要用到的各种魔法密钥和服务器名称～
这些是保证程序各部分正常通讯的重要魔法标识哦～ ✨"""
IPC_SERVER_NAME = 'SecRandomIPC'  # IPC通讯服务器名称
SHARED_MEMORY_KEY = 'SecRandom'   # 共享内存密钥

# ==================================================
# 🧙‍♀️ 应用实例创建 (Application Instance Creation)
# ==================================================
app = QApplication(sys.argv)
logger.debug("白露创建: QApplication实例已创建～ ")


def check_single_instance():
    """(ﾟДﾟ≡ﾟдﾟ) 星野的单实例守卫启动！
    正在执行魔法结界检查，禁止多个程序副本同时运行喵！
    这是为了防止魔法冲突和资源争夺，保证程序稳定运行哦～ 🔒✨"""
    shared_memory = QSharedMemory(SHARED_MEMORY_KEY)
    if not shared_memory.create(1):
        logger.debug('星野警报: 检测到已有 SecRandom 实例正在运行喵！')

        # 尝试直接发送IPC消息唤醒已有实例
        if send_ipc_message():
            logger.info('星野通讯: 成功唤醒已有实例，当前实例将退出喵～')
            sys.exit()
        else:
            # IPC连接失败，重试连接
            def retry_ipc():
                """(ﾟДﾟ≡ﾟдﾟ) 星野的重试魔法！再次尝试连接已有实例喵～"""
                if not send_ipc_message():
                    logger.error("星野错误: 无法连接到已有实例，程序将退出喵～")
                    sys.exit()
            retry_ipc()
                
        sys.exit()
    logger.info('星野结界: 单实例检查通过，可以安全启动程序喵～')
    return shared_memory


def initialize_application():
    """(^・ω・^ ) 白露的应用初始化仪式！
    正在唤醒应用程序的核心组件，就像唤醒沉睡的魔法生物一样～
    完成后将展示主界面，准备开始您的随机选择冒险啦～ ✨"""
    logger.info("白露启动: 软件启动成功～ ")
    logger.info(f"白露启动: 软件作者: lzy98276")
    logger.info(f"白露启动: 软件Github地址: https://github.com/SECTL/SecRandom")

    # 清理过期历史记录，保持魔法空间整洁～
    from app.common.history_cleaner import clean_expired_history, clean_expired_reward_history
    clean_expired_history()
    clean_expired_reward_history()
    logger.debug("白露清理: 已清理过期历史记录～ ")

    # 创建主窗口实例
    sec = Window()
    try:
        with open('app/Settings/Settings.json', 'r', encoding='utf-8') as f:
            settings = json.load(f)
            foundation_settings = settings.get('foundation', {})
            self_starting_enabled = foundation_settings.get('self_starting_enabled', False)
            if not self_starting_enabled:
                sec.show()
                logger.info("白露展示: 根据设置显示主窗口～ ")
    except FileNotFoundError:
        logger.error("白露错误: 加载设置时出错 - 文件不存在, 使用默认显示主窗口")
        sec.show()
    except KeyError:
        logger.error("白露错误: 设置文件中缺少foundation键, 使用默认显示主窗口")
        sec.show()
    except Exception as e:
        logger.error(f"白露错误: 加载设置时出错: {e}, 使用默认显示主窗口")
        sec.show()
    return sec


# ==================================================
# 🎬 魔法冒险开始 (Main Adventure Starts)
# ==================================================
if __name__ == "__main__":
    # 配置日志系统
    configure_logging()
    
    # 检查单实例并创建共享内存
    shared_memory = check_single_instance()
    
    # 初始化应用程序并创建主窗口
    sec = initialize_application()

    # 启动应用程序事件循环
    try:
        logger.info("星野通知: 应用程序事件循环启动喵～")
        app.exec_()
    finally:
        shared_memory.detach()
        logger.info("星野通知: 共享内存已释放，程序完全退出喵～")
        sys.exit()