# ==================================================
# 🔮 系统魔法工具 (System Magic Tools)
# ==================================================
import os
import sys
import json

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

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
from app.common.config import cfg, VERSION
from app.view.SecRandom import Window
from app.common.url_handler import process_url_if_exists

def send_ipc_message(url_command=None):
    """(^・ω・^ ) 白露的IPC信使魔法！
    正在向已运行的实例发送唤醒消息～ 就像传递小纸条一样神奇！
    如果成功连接，会发送'show'指令或URL命令让窗口重新出现哦～ ✨"""
    socket = QLocalSocket()
    socket.connectToServer(IPC_SERVER_NAME)

    if socket.waitForConnected(1000):
        if url_command:
            # 发送URL命令
            message = f"url:{url_command}"
            socket.write(message.encode('utf-8'))
            logger.debug(f"白露信使: IPC URL消息发送成功～ {message}")
        else:
            # 发送普通的show指令
            socket.write(b"show")
            logger.debug("白露信使: IPC show消息发送成功～ ")
        socket.flush()
        socket.waitForBytesWritten(1000)
        socket.disconnectFromServer()
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

        # 获取URL命令（如果存在）
        url_command = None
        try:
            from app.common.url_handler import get_url_handler
            url_handler = get_url_handler()
            if url_handler.has_url_command():
                url_command = url_handler.get_url_command()
                logger.info(f'星野通讯: 检测到URL命令，将传递给已有实例喵～ {url_command}')
        except Exception as e:
            logger.error(f'星野错误: 获取URL命令失败喵～ {e}')

        # 🌟 星穹铁道白露：异步发送IPC消息，避免阻塞启动流程
        def async_wakeup():
            # 尝试直接发送IPC消息唤醒已有实例
            if send_ipc_message(url_command):
                logger.info('星野通讯: 成功唤醒已有实例，当前实例将退出喵～')
                sys.exit()
            else:
                # IPC连接失败，短暂延迟后重试一次
                QTimer.singleShot(300, lambda:
                    retry_ipc() if not send_ipc_message(url_command) else None
                )

        def retry_ipc():
            """(ﾟДﾟ≡ﾟдﾟ) 星野的重试魔法！再次尝试连接已有实例喵～"""
            logger.error("星野错误: 无法连接到已有实例，程序将退出喵～")
            sys.exit()

        # 立即异步执行唤醒操作
        QTimer.singleShot(0, async_wakeup)
        # 等待异步操作完成
        QApplication.processEvents()
        sys.exit()
    logger.info('星野结界: 单实例检查通过，可以安全启动程序喵～')
    return shared_memory


def check_settings_directory():
    """(^・ω・^ ) 白露的设置目录检查魔法！
    检查引导完成标志文件是否存在以及版本是否匹配～
    返回值说明：
    - 'ok': 引导已完成且版本匹配，正常启动
    - 'guide': 没有文件或引导未完成，需要显示引导界面
    - 'update': 版本过低，需要显示新版本更新内容
    ✨"""
    guide_complete_file = 'app/Settings/guide_complete.json'
    
    # 检查引导完成标志文件是否存在
    if not os.path.exists(guide_complete_file):
        logger.info("白露检查: 引导完成标志文件不存在，需要显示引导界面～ ")
        return 'guide'
    
    # 检查引导完成标志文件内容是否有效
    try:
        with open(guide_complete_file, 'r', encoding='utf-8') as f:
            guide_data = json.load(f)
            
        # 检查是否包含必要的字段
        if not isinstance(guide_data, dict):
            logger.info("白露检查: 引导完成标志文件格式错误，需要显示引导界面～ ")
            return 'guide'
            
        guide_completed = guide_data.get('guide_completed', False)
        if not guide_completed:
            logger.info("白露检查: 引导未完成，需要显示引导界面～ ")
            return 'guide'
        
        # 检查版本是否匹配
        guide_version = guide_data.get('version', '')
        if not guide_version:
            logger.info("白露检查: 引导完成标志文件中缺少版本信息，需要显示引导界面～ ")
            return 'guide'
            
        # 导入版本比较模块
        from packaging.version import Version
        
        # 移除版本前缀并比较
        current_version = VERSION.lstrip('v')
        guide_version_clean = guide_version.lstrip('v')
        
        if Version(guide_version_clean) != Version(current_version):
            logger.info(f"白露检查: 版本不匹配，当前版本 {VERSION}，引导文件版本 {guide_version}，需要显示新版本更新内容～ ")
            return 'update'
            
        logger.info(f"白露检查: 引导已完成且版本匹配 {VERSION}，可以跳过引导界面～ ")
        return 'ok'
    except json.JSONDecodeError:
        logger.info("白露检查: 引导完成标志文件JSON格式错误，需要显示引导界面～ ")
        return 'guide'
    except Exception as e:
        logger.error(f"白露检查: 检查引导完成标志文件时出错: {e}")
        return 'guide'


def initialize_application():
    """(^・ω・^ ) 白露的应用初始化仪式！
    正在唤醒应用程序的核心组件，就像唤醒沉睡的魔法生物一样～
    完成后将展示主界面，准备开始您的随机选择冒险啦～ ✨"""
    logger.info("白露启动: 软件启动成功～ ")
    logger.info(f"白露启动: 软件作者: lzy98276")
    logger.info(f"白露启动: 软件Github地址: https://github.com/SECTL/SecRandom")

    # 检查设置状态
    settings_status = check_settings_directory()
    
    if settings_status == 'guide':
        # 显示引导界面，跳过历史记录清理和插件自启动
        logger.info("白露引导: 首次使用，显示引导界面～ ")
        from app.view.guide_window import GuideWindow
        guide_window = GuideWindow()
        
        # 创建主窗口但不显示
        sec = Window()
        
        # 连接引导窗口的开始使用信号
        def show_main_window():
            # 用户完成引导后，执行正常的初始化流程
            logger.info("白露引导: 用户完成引导，开始正常初始化～ ")
            
            # 清理过期历史记录
            from app.common.history_cleaner import clean_expired_history, clean_expired_reward_history
            clean_expired_history()
            clean_expired_reward_history()
            logger.debug("白露清理: 已清理过期历史记录～ ")
            
            # 🌟 小鸟游星野：检查插件自启动设置 ~ (๑•̀ㅂ•́)ญ✧
            try:
                # 读取插件设置文件
                plugin_settings_file = 'app/Settings/plugin_settings.json'
                if os.path.exists(plugin_settings_file):
                    with open(plugin_settings_file, 'r', encoding='utf-8') as f:
                        plugin_settings = json.load(f)
                        run_plugins_on_startup = plugin_settings.get('plugin_settings', {}).get('run_plugins_on_startup', False)
                        
                        if run_plugins_on_startup:
                            from app.view.plugins.management import PluginManagementPage
                            plugin_manager = PluginManagementPage()
                            plugin_manager.start_autostart_plugins()
                            logger.info("白露插件: 自启动插件功能已启动～ ")
                        else:
                            logger.info("白露插件: 插件自启动功能已禁用～ ")
                else:
                    logger.warning("白露警告: 插件设置文件不存在，跳过插件自启动～ ")
            except Exception as e:
                logger.error(f"白露错误: 检查插件自启动设置失败: {e}")
            
            # 显示主窗口
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
        
        # 连接引导窗口的开始使用信号
        guide_window.start_signal.connect(show_main_window)
        
        # 显示引导窗口
        guide_window.show()
        
        return sec
    elif settings_status == 'update':
        # (^・ω・^ ) 白露的版本更新处理魔法！
        # 检测到版本更新，显示更新日志界面～ ✨
        logger.info("白露主程序: 检测到版本更新，准备显示更新日志界面～ ")
        
        # 创建主窗口但不显示
        sec = Window()
        
        # 显示更新日志窗口
        from app.view.update_log_window import UpdateLogWindow
        update_log_window = UpdateLogWindow()
        
        # 定义更新日志关闭后的处理函数
        def show_main_window_after_update():
            # 用户查看更新内容后，执行正常的初始化流程
            logger.info("白露更新: 用户查看更新内容完成，开始正常初始化～ ")
            
            # 清理过期历史记录
            from app.common.history_cleaner import clean_expired_history, clean_expired_reward_history
            clean_expired_history()
            clean_expired_reward_history()
            logger.debug("白露清理: 已清理过期历史记录～ ")
            
            # 🌟 小鸟游星野：检查插件自启动设置 ~ (๑•̀ㅂ•́)ญ✧
            try:
                # 读取插件设置文件
                plugin_settings_file = 'app/Settings/plugin_settings.json'
                if os.path.exists(plugin_settings_file):
                    with open(plugin_settings_file, 'r', encoding='utf-8') as f:
                        plugin_settings = json.load(f)
                        run_plugins_on_startup = plugin_settings.get('plugin_settings', {}).get('run_plugins_on_startup', False)
                        
                        if run_plugins_on_startup:
                            from app.view.plugins.management import PluginManagementPage
                            plugin_manager = PluginManagementPage()
                            plugin_manager.start_autostart_plugins()
                            logger.info("白露插件: 自启动插件功能已启动～ ")
                        else:
                            logger.info("白露插件: 插件自启动功能已禁用～ ")
                else:
                    logger.warning("白露警告: 插件设置文件不存在，跳过插件自启动～ ")
            except Exception as e:
                logger.error(f"白露错误: 检查插件自启动设置失败: {e}")
            
            # 显示主窗口
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
        
        # 连接更新日志窗口的开始信号
        update_log_window.start_signal_update.connect(show_main_window_after_update)

        # 显示更新日志窗口
        update_log_window.show()
        
        return sec
    else:
        # 正常启动流程
        # 清理过期历史记录，保持魔法空间整洁～
        from app.common.history_cleaner import clean_expired_history, clean_expired_reward_history
        clean_expired_history()
        clean_expired_reward_history()
        logger.debug("白露清理: 已清理过期历史记录～ ")

        # 创建主窗口实例
        sec = Window()
        
        # 🌟 小鸟游星野：检查插件自启动设置 ~ (๑•̀ㅂ•́)ญ✧
        try:
            # 读取插件设置文件
            plugin_settings_file = 'app/Settings/plugin_settings.json'
            if os.path.exists(plugin_settings_file):
                with open(plugin_settings_file, 'r', encoding='utf-8') as f:
                    plugin_settings = json.load(f)
                    run_plugins_on_startup = plugin_settings.get('plugin_settings', {}).get('run_plugins_on_startup', False)
                    
                    if run_plugins_on_startup:
                        from app.view.plugins.management import PluginManagementPage
                        plugin_manager = PluginManagementPage()
                        plugin_manager.start_autostart_plugins()
                        logger.info("白露插件: 自启动插件功能已启动～ ")
                    else:
                        logger.info("白露插件: 插件自启动功能已禁用～ ")
            else:
                logger.warning("白露警告: 插件设置文件不存在，跳过插件自启动～ ")
        except Exception as e:
            logger.error(f"白露错误: 检查插件自启动设置失败: {e}")
        
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

    # 延迟处理URL命令，确保主窗口完全初始化
    def delayed_url_processing():
        """延迟处理URL命令，确保主窗口完全初始化"""
        try:
            logger.info("白露URL: 延迟检查是否有URL命令需要处理～")
            if process_url_if_exists(sec):
                logger.info("白露URL: URL命令处理成功～")
            else:
                logger.info("白露URL: 没有URL命令需要处理～")
        except Exception as e:
            logger.error(f"白露URL: 处理URL命令失败: {e}")
    
    QTimer.singleShot(1000, delayed_url_processing)  # 延迟1秒处理URL

    # 启动应用程序事件循环
    try:
        logger.info("星野通知: 应用程序事件循环启动喵～")
        app.exec_()
    finally:
        shared_memory.detach()
        logger.info("星野通知: 共享内存已释放，程序完全退出喵～")
        sys.exit()