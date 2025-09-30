# ==================================================
# 🔮 系统魔法工具 (System Magic Tools)
# ==================================================
import os
import sys
import json
import time

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# ==================================================
# 📚 第三方魔法书 (Third-Party Magic Books)
# ==================================================
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtNetwork import *
from qfluentwidgets import *
from loguru import logger

# ==================================================
# 📜 内部魔法卷轴 (Internal Magic Scrolls)
# ==================================================
from app.common.config import cfg, VERSION, load_custom_font
from app.view.SecRandom import Window
from app.common.url_handler import process_url_if_exists
from app.common.path_utils import path_manager, ensure_dir, open_file, file_exists
from qfluentwidgets import qconfig, Theme

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
    log_dir = os.path.join(project_root, "logs")
    if not path_manager.file_exists(log_dir):
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

    logger.debug("=" * 50)

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
# 🚀 启动窗口魔法 (Startup Window Magic)
# ==================================================
class StartupWindow(QDialog):
    """(^・ω・^ ) 白露的启动窗口魔法！
    展示软件启动的各个步骤和实时进度，让用户了解启动状态～
    就像魔法仪式的进度条一样，让等待变得有趣哦～ ✨"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SecRandom 启动中...")
        self.setFixedSize(260, 135)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool | Qt.NoFocus | Qt.Popup)
        
        # 移除透明背景属性，使窗口不透明
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # 移除透明化效果
        # self.opacity_effect = QGraphicsOpacityEffect()
        # self.opacity_effect.setOpacity(0.8)
        # self.setGraphicsEffect(self.opacity_effect)

        # 创建主布局
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建背景容器
        self.background_widget = QWidget()
        self.background_widget.setObjectName("backgroundWidget")
        
        # 根据主题设置背景颜色
        self.update_background_theme()
        
        # 创建内容布局
        content_layout = QVBoxLayout(self.background_widget)
        content_layout.setSpacing(15)
        content_layout.setContentsMargins(20, 20, 20, 20)
        
        # 创建顶部水平布局，用于放置图标和标题
        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(0, 0, 0, 10)
        top_layout.setSpacing(10)  # 设置图标和标题之间的间距为10像素
        
        # 添加软件图标到左上角
        try:
            icon_path = str(path_manager.get_resource_path('icon', 'SecRandom.png'))
            if os.path.exists(icon_path):
                icon_label = QLabel()
                pixmap = QPixmap(icon_path)
                # 缩放图标到合适大小
                scaled_pixmap = pixmap.scaled(52, 52, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                icon_label.setPixmap(scaled_pixmap)
                icon_label.setFixedSize(52, 52)
                top_layout.addWidget(icon_label)
            else:
                logger.warning(f"软件图标文件不存在: {icon_path}")
        except Exception as e:
            logger.error(f"加载软件图标失败: {e}")
        
        # 创建垂直布局容器，用于放置标题和版本号
        title_version_layout = QVBoxLayout()
        title_version_layout.setSpacing(2)  # 设置标题和版本号之间的间距
        title_version_layout.setContentsMargins(0, 0, 0, 0)
        
        # 添加标题标签
        self.title_label = BodyLabel("SecRandom")
        self.title_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.title_label.setFont(QFont(load_custom_font(), 16))
        title_version_layout.addWidget(self.title_label)
        
        # 添加版本号标签到标题下方
        self.version_label = BodyLabel(f"{VERSION}")
        self.version_label.setAlignment(Qt.AlignLeft)
        self.version_label.setFont(QFont(load_custom_font(), 10))
        title_version_layout.addWidget(self.version_label)
        
        # 将标题和版本号布局添加到水平布局
        top_layout.addLayout(title_version_layout)
        
        # 添加弹性空间，使图标和标题靠左对齐
        top_layout.addStretch(1)
        
        # 添加顶部布局到内容布局
        content_layout.addLayout(top_layout)

        # 创建详细信息标签
        self.detail_label = BodyLabel("准备启动...")
        self.detail_label.setAlignment(Qt.AlignCenter)
        self.detail_label.setFont(QFont(load_custom_font(), 9))
        content_layout.addWidget(self.detail_label)
        
        # 添加弹性空间，使进度条能够贴底显示
        content_layout.addStretch(1)
        
        # 创建进度条
        self.progress_bar = ProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("%p%")
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: none;
                background-color: #F0F0F0;
                border-radius: 5px;
                text-align: center;
                color: #333333;
            }
            QProgressBar::chunk {
                background-color: #0078D7;
                border-radius: 5px;
            }
        """)
        content_layout.addWidget(self.progress_bar)
        
        # 将背景容器添加到主布局
        main_layout.addWidget(self.background_widget)
        
        # 启动步骤和进度
        self.startup_steps = [
            ("初始化应用程序环境", 10),
            ("配置日志系统", 20),
            ("检查单实例", 30),
            ("加载配置文件", 40),
            ("清理历史记录", 50),
            ("检查插件设置", 60),
            ("注册URL协议", 70),
            ("创建主窗口", 80),
            ("初始化界面组件", 90),
            ("处理URL命令", 95),
            ("启动完成", 100)
        ]
        
        self.current_step = 0
        
    def update_progress(self, step_name=None, progress=None, detail=None):
        """更新启动进度"""
        if progress is not None:
            self.progress_bar.setValue(progress)
        
        if detail:
            self.detail_label.setText(detail)
            
        # 确保界面更新
        QApplication.processEvents()
        
    def next_step(self, detail=None):
        """进入下一个启动步骤"""
        if self.current_step < len(self.startup_steps):
            step_name, progress = self.startup_steps[self.current_step]
            self.update_progress(step_name, progress, detail)
            self.current_step += 1
            return True
        return False
    
    def set_step(self, step_index, detail=None):
        """设置到指定步骤"""
        if 0 <= step_index < len(self.startup_steps):
            step_name, progress = self.startup_steps[step_index]
            self.update_progress(step_name, progress, detail)
            self.current_step = step_index + 1
            return True
        return False
    
    def update_background_theme(self):
        """根据当前主题更新背景颜色"""
        # 检测当前主题
        if qconfig.theme == Theme.AUTO:
            lightness = QApplication.palette().color(QPalette.Window).lightness()
            is_dark = lightness <= 127
        else:
            is_dark = qconfig.theme == Theme.DARK
        
        # 根据主题设置颜色
        if is_dark:
            # 深色主题
            bg_color = "#111116"
            border_color = "#3E3E42"
            text_color = "#F5F5F5"
            progress_bg = "#2D2D30"
            progress_text = "#F5F5F5"
        else:
            # 浅色主题
            bg_color = "#F5F5F5"
            border_color = "#CCCCCC"
            text_color = "#111116"
            progress_bg = "#F0F0F0"
            progress_text = "#333333"
        
        # 设置背景容器样式
        self.background_widget.setStyleSheet(f"""
            #backgroundWidget {{
                background-color: {bg_color};
                border-radius: 15px;
                border: 1px solid {border_color};
            }}
        """)
        
    def close_startup(self):
        """关闭启动窗口"""
        self.close()

class StartupWindowThread(QThread):
    """启动窗口线程类，用于在单独的线程中运行启动窗口"""
    
    def __init__(self, startup_window=None):
        super().__init__()
        self.startup_window = startup_window
        self.running = False
    
    def run(self):
        """线程运行函数"""
        self.running = True
        # 启动事件循环，保持线程响应
        self.exec_()
    
    def update_progress(self, step_name=None, progress=None, detail=None):
        """更新启动进度"""
        if self.startup_window and self.running:
            self.startup_window.update_progress(step_name, progress, detail)
    
    def next_step(self, detail=None):
        """进入下一个启动步骤"""
        if self.startup_window and self.running:
            self.startup_window.next_step(detail)
    
    def set_step(self, step_index, detail=None):
        """设置到指定步骤"""
        if self.startup_window and self.running:
            self.startup_window.set_step(step_index, detail)
    
    def close_window(self):
        """关闭启动窗口"""
        if self.startup_window and self.running:
            self.running = False
            self.startup_window.close()
            self.quit()  # 退出事件循环


# ==================================================
# 🔐 验证状态初始化 (Verification Status Initialization)
# ==================================================
"""(ﾟДﾟ≡ﾟдﾟ) 星野的安全验证初始化！
正在重置验证状态标记，确保程序启动时处于安全状态喵～
这是防止重复验证的魔法保护措施哦～ 🔒"""
try:
    enc_set_path = path_manager.get_enc_set_path()
    ensure_dir(enc_set_path.parent)
    with open_file(enc_set_path, 'r') as f:
        settings = json.load(f)
    settings['hashed_set']['verification_start'] = False
    with open_file(enc_set_path, 'w') as f:
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

def initialize_font_settings():
    """初始化字体设置，加载并应用保存的字体"""
    try:
        # 读取个人设置文件
        settings_file = path_manager.get_settings_path('custom_settings.json')
        ensure_dir(settings_file.parent)
        
        if file_exists(settings_file):
            with open_file(settings_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                personal_settings = settings.get('personal', {})
                font_family = personal_settings.get('font_family')
                
                if font_family:
                    # 应用字体设置
                    apply_font_to_application(font_family)
                    logger.info(f"初始化字体设置: {font_family}")
                else:
                    logger.info("初始化字体设置: 未指定字体家族，使用默认字体")
                    apply_font_to_application('HarmonyOS Sans SC')  
        else:
            # 如果设置文件不存在，使用默认字体
            logger.info("初始化字体设置: 设置文件不存在，使用默认字体")
            apply_font_to_application('HarmonyOS Sans SC')
    except Exception as e:
        logger.error(f"初始化字体设置失败: {e}")
        # 发生错误时使用默认字体
        logger.info("初始化字体设置: 发生错误，使用默认字体")
        apply_font_to_application('HarmonyOS Sans SC')

def apply_font_to_application(font_family):
    """应用字体设置到整个应用程序
    
    Args:
        font_family (str): 字体家族名称
    """
    try:
        # 获取当前应用程序默认字体
        current_font = QApplication.font()
        
        # 创建字体对象，只修改字体家族，保持原有字体大小
        app_font = QFont(font_family)
        app_font.setPointSize(current_font.pointSize())
        
        # 如果是HarmonyOS Sans SC字体，使用特定的字体文件路径
        if font_family == "HarmonyOS Sans SC":
            font_path = path_manager.get_font_path('HarmonyOS_Sans_SC_Bold.ttf')
            if font_path and path_manager.file_exists(font_path):
                font_id = QFontDatabase.addApplicationFont(str(font_path))
                if font_id >= 0:
                    font_families = QFontDatabase.applicationFontFamilies(font_id)
                    if font_families:
                        app_font = QFont(font_families[0])
                        app_font.setPointSize(current_font.pointSize())
                        logger.info(f"已加载HarmonyOS Sans SC字体文件: {font_path}")
                    else:
                        logger.warning(f"无法从字体文件获取字体家族: {font_path}")
                else:
                    logger.warning(f"无法加载字体文件: {font_path}")
            else:
                logger.warning(f"HarmonyOS Sans SC字体文件不存在: {font_path}")
        
        # 定义延迟更新函数
        def delayed_font_update(font_to_apply):
            global main_window
            # 获取所有顶级窗口并更新它们的字体
            widgets_updated = 0
            for widget in QApplication.topLevelWidgets():
                if isinstance(widget, QWidget):
                    # widget_type = type(widget).__name__
                    # widget_name = widget.objectName() or "未命名"
                    # window_title = getattr(widget, 'windowTitle', lambda: "")() or "无标题"
                    # logger.debug(f"更新控件字体: 类型={widget_type}, 名称={widget_name}, 标题={window_title}")
                    update_widget_fonts(widget, font_to_apply)
                    widgets_updated += 1
                
            logger.info(f"已应用字体: {font_family}, 更新了{widgets_updated}个控件")
        
        # 使用QTimer延迟更新字体，确保设置已保存
        QTimer.singleShot(100, lambda: delayed_font_update(app_font))
    except Exception as e:
        logger.error(f"应用字体失败: {e}")

def update_widget_fonts(widget, font):
    """递归更新控件及其子控件的字体
    
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
        
        # 特殊处理某些控件类型
        widget_type = type(widget).__name__
        
        # 对于按钮、标签等控件，确保字体更新
        if widget_type:
            widget.setFont(new_font)
            widget.update()
        
        # 强制控件更新
        widget.update()
        widget.repaint()
        
        # 记录更新的控件信息
        # widget_name = widget.objectName() or "未命名"
        # logger.debug(f"已更新控件: 类型={widget_type}, 名称={widget_name}, 字体={font.family()}")
        
        # 如果控件有子控件，递归更新子控件的字体
        if isinstance(widget, QWidget):
            children = widget.children()
            # logger.debug(f"控件 {widget_name} 有 {len(children)} 个子控件")
            for child in children:
                if isinstance(child, QWidget):
                    update_widget_fonts(child, font)
    except Exception as e:
        logger.error(f"更新控件字体失败: {e}")

def check_single_instance():
    """(ﾟДﾟ≡ﾟдﾟ) 星野的单实例守卫启动！
    正在执行魔法结界检查，禁止多个程序副本同时运行喵！
    这是为了防止魔法冲突和资源争夺，保证程序稳定运行哦～ 🔒✨"""
    # 检查是否有启动窗口线程
    has_startup_thread = 'startup_thread' in globals() and startup_thread is not None and startup_thread.isRunning()
    
    if has_startup_thread:
        startup_thread.next_step(detail="正在检查单实例...")
    
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
                if has_startup_thread:
                    startup_thread.next_step(detail="检测到URL命令，将传递给已有实例")
        except Exception as e:
            logger.error(f'星野错误: 获取URL命令失败喵～ {e}')
            if has_startup_thread:
                startup_thread.next_step(detail=f"获取URL命令失败: {e}")

        # 🌟 星穹铁道白露：异步发送IPC消息，避免阻塞启动流程
        def async_wakeup():
            # 尝试直接发送IPC消息唤醒已有实例
            if send_ipc_message(url_command):
                logger.info('星野通讯: 成功唤醒已有实例，当前实例将退出喵～')
                if has_startup_thread:
                    startup_thread.update_progress(detail="成功唤醒已有实例，当前实例将退出")
                sys.exit()
            else:
                # IPC连接失败，短暂延迟后重试一次
                QTimer.singleShot(300, lambda:
                    retry_ipc() if not send_ipc_message(url_command) else None
                )

        def retry_ipc():
            """(ﾟДﾟ≡ﾟдﾟ) 星野的重试魔法！再次尝试连接已有实例喵～"""
            logger.error("星野错误: 无法连接到已有实例，程序将退出喵～")
            if has_startup_thread:
                startup_thread.update_progress(detail="无法连接到已有实例，程序将退出")
            sys.exit()

        # 立即异步执行唤醒操作
        QTimer.singleShot(0, async_wakeup)
        # 等待异步操作完成
        QApplication.processEvents()
        sys.exit()
    
    logger.info('星野结界: 单实例检查通过，可以安全启动程序喵～')
    if has_startup_thread:
        startup_thread.update_progress(detail="单实例检查通过，可以安全启动程序")
    
    return shared_memory

def log_software_info():
    """(^・ω・^ ) 白露的软件信息记录仪式！
    记录软件启动成功信息和相关元信息，就像记录魔法书的标题一样～ ✨"""
    # 打印分隔线，增强日志可读性
    logger.debug("=" * 50)
    # 记录软件启动成功信息
    logger.info("白露启动: 软件启动成功～ ")
    # 记录软件相关元信息
    software_info = {
        "作者": "lzy98276",
        "Github地址": "https://github.com/SECTL/SecRandom",
        "版本": VERSION
    }
    for key, value in software_info.items():
        logger.info(f"白露启动: 软件{key}: {value}")

def clean_expired_data():
    """(^・ω・^ ) 白露的历史清理仪式！
    清理过期历史记录，保持魔法空间整洁～"""
    # 清理过期历史记录，保持魔法空间整洁～
    from app.common.history_cleaner import clean_expired_history, clean_expired_reward_history
    clean_expired_history()
    clean_expired_reward_history()
    logger.debug("白露清理: 已清理过期历史记录～ ")

def check_plugin_settings():
    """🌟 小鸟游星野：检查插件自启动设置 ~ (๑•̀ㅂ•́)ญ✧
    检查插件设置文件，决定是否启动自启动插件功能"""
    # 检查是否有启动窗口线程
    has_startup_thread = 'startup_thread' in globals() and startup_thread is not None and startup_thread.isRunning()
    
    try:
        # 读取插件设置文件
        plugin_settings_file = path_manager.get_settings_path('plugin_settings.json')
        ensure_dir(plugin_settings_file.parent)
        if file_exists(plugin_settings_file):
            with open_file(plugin_settings_file, 'r') as f:
                plugin_settings = json.load(f)
                run_plugins_on_startup = plugin_settings.get('plugin_settings', {}).get('run_plugins_on_startup', False)
                
                if run_plugins_on_startup:
                    from app.view.plugins.management import PluginManagementPage
                    plugin_manager = PluginManagementPage()
                    plugin_manager.start_autostart_plugins()
                    logger.info("白露插件: 自启动插件功能已启动～ ")
                    if has_startup_thread:
                        startup_thread.update_progress(detail="自启动插件功能已启动")
                else:
                    logger.info("白露插件: 插件自启动功能已禁用～ ")
                    if has_startup_thread:
                        startup_thread.update_progress(detail="插件自启动功能已禁用")
        else:
            logger.warning("白露警告: 插件设置文件不存在，跳过插件自启动～ ")
            if has_startup_thread:
                startup_thread.update_progress(detail="插件设置文件不存在，跳过插件自启动")
    except Exception as e:
        logger.error(f"白露错误: 检查插件自启动设置失败: {e}")
        if has_startup_thread:
            startup_thread.update_progress(detail=f"检查插件自启动设置失败: {e}")

def create_main_window_async():
    """(^・ω・^ ) 白露的异步主窗口创建仪式！
    异步创建主窗口实例并根据设置决定是否显示窗口～"""
    # 检查是否有启动窗口线程
    has_startup_thread = 'startup_thread' in globals() and startup_thread is not None and startup_thread.isRunning()
    
    # 创建主窗口实例
    if has_startup_thread:
        startup_thread.set_step(6, "正在创建主窗口...")
    
    # 使用QTimer异步创建主窗口
    def async_create_window():
        sec = Window()
        
        try:
            settings_file = path_manager.get_settings_path()
            ensure_dir(settings_file.parent)
            with open_file(settings_file, 'r') as f:
                settings = json.load(f)
                foundation_settings = settings.get('foundation', {})
                self_starting_enabled = foundation_settings.get('self_starting_enabled', False)
                
                # 显示窗口
                sec.show()
                logger.info("白露展示: 主窗口已显示～ ")
                
                # 如果是开机自启动，则在短暂延迟后隐藏窗口
                if self_starting_enabled:
                    sec.hide()
                    logger.info("白露隐藏: 开机自启动模式，窗口已隐藏～ ")
        except FileNotFoundError:
            logger.error("白露错误: 加载设置时出错 - 文件不存在, 使用默认显示主窗口")
            sec.show()
        except KeyError:
            logger.error("白露错误: 设置文件中缺少foundation键, 使用默认显示主窗口")
            sec.show()
        except Exception as e:
            logger.error(f"白露错误: 加载设置时出错: {e}, 使用默认显示主窗口")
            sec.show()
        
        # 将创建的主窗口保存到全局变量
        global main_window
        main_window = sec
    
    # 延迟50ms后异步创建主窗口
    QTimer.singleShot(100, async_create_window)


# ==================================================
# 🎬 魔法冒险开始 (Main Adventure Starts)
# ==================================================
if __name__ == "__main__":
    # 全局变量，用于存储主窗口实例
    main_window = None
    
    # 检查是否显示启动窗口
    show_startup_window = True  # 默认显示启动窗口
    try:
        settings_file = path_manager.get_settings_path()
        ensure_dir(settings_file.parent)
        if file_exists(settings_file):
            with open_file(settings_file, 'r') as f:
                settings = json.load(f)
                foundation_settings = settings.get('foundation', {})
                show_startup_window = foundation_settings.get('show_startup_window_switch', False)
    except Exception as e:
        logger.warning(f"白露警告: 读取启动窗口设置失败，使用默认显示启动窗口: {e}")
    
    # 根据设置决定是否创建启动窗口
    if show_startup_window:
        # 在主线程中创建启动窗口
        startup_window = StartupWindow()
        startup_window.show()
        
        # 创建启动窗口线程并启动
        startup_thread = StartupWindowThread(startup_window)
        startup_thread.start()
        
        # 更新启动窗口进度
        startup_thread.next_step("正在初始化应用程序环境...")
    else:
        # 不显示启动窗口，创建空的启动窗口线程对象以避免错误
        startup_window = None
        startup_thread = None
        logger.info("白露提示: 启动窗口已禁用，跳过启动窗口显示")
    
    # 设置工作目录为程序所在目录，解决URL协议唤醒时工作目录错误的问题
    if getattr(sys, 'frozen', False):
        # 打包后的可执行文件
        program_dir = os.path.dirname(sys.executable)
    else:
        # 开发环境
        program_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 配置日志系统
    if startup_thread:
        startup_thread.next_step("正在配置日志系统...")
    configure_logging()

    # 更改当前工作目录
    if os.getcwd() != program_dir:
        os.chdir(program_dir)
        logger.info(f"白露目录: 工作目录已设置为: {program_dir}")
    
    # 检查单实例并创建共享内存
    if startup_thread:
        startup_thread.next_step("正在检查单实例...")
    shared_memory = check_single_instance()
    
    # 初始化应用程序并创建主窗口
    if startup_thread:
        startup_thread.next_step("正在加载配置文件...")
    log_software_info()

    if startup_thread:
        startup_thread.set_step(4, "正在清理历史记录...")
    clean_expired_data()

    if startup_thread:
        startup_thread.set_step(5, "正在检查插件设置...")
    check_plugin_settings()

    # 自动注册URL协议
    if startup_thread:
        startup_thread.set_step(6, "正在注册URL协议...")
    try:
        from app.common.foundation_settings import register_url_protocol_on_startup
        register_url_protocol_on_startup()
        logger.info("白露URL: URL协议自动注册完成～")
        if startup_thread:
            startup_thread.update_progress(detail="URL协议自动注册完成")
    except Exception as e:
        logger.error(f"白露URL: URL协议自动注册失败: {e}")
        if startup_thread:
            startup_thread.update_progress(detail=f"URL协议自动注册失败: {e}")

    # 检查是否有启动窗口线程
    has_startup_thread = startup_thread is not None and startup_thread.isRunning()

    # 创建主窗口实例
    if has_startup_thread:
        startup_thread.set_step(7, "正在创建主窗口...")

    create_main_window_async()

    if has_startup_thread:
        startup_thread.set_step(8, "正在初始化界面组件...")

    app.setQuitOnLastWindowClosed(False)

    # 延迟处理URL命令，确保主窗口完全初始化
    def delayed_url_processing():
        """(ﾟДﾟ≡ﾟдﾟ) 星野的URL命令处理魔法！
        延迟处理URL命令，避免阻塞启动流程喵～
        这是为了确保主界面完全加载后再处理URL命令哦～ 🌐✨"""
        # 检查是否有启动窗口线程
        has_startup_thread = 'startup_thread' in globals() and startup_thread is not None and startup_thread.isRunning()
        
        if has_startup_thread:
            startup_thread.set_step(9, "正在初始化界面组件...")
        
        try:
            logger.info("白露URL: 延迟检查是否有URL命令需要处理～")
            # 检查主窗口是否已创建
            global main_window
            if 'main_window' in globals() and main_window:
                if process_url_if_exists(main_window):
                    logger.info("白露URL: URL命令处理成功～")
                    if has_startup_thread:
                        startup_thread.update_progress(detail="URL命令处理成功")
                else:
                    logger.info("白露URL: 没有URL命令需要处理～")
                    if has_startup_thread:
                        startup_thread.update_progress(detail="没有URL命令需要处理")
            else:
                logger.warning("白露URL: 主窗口尚未创建，跳过URL命令处理～")
                if has_startup_thread:
                    startup_thread.update_progress(detail="主窗口尚未创建，跳过URL命令处理")
        except Exception as e:
            logger.error(f"白露URL: 处理URL命令失败: {e}")
            if has_startup_thread:
                startup_thread.update_progress(detail=f"处理URL命令失败: {e}")
        finally:
            # 启动完成，关闭启动窗口
            if has_startup_thread:
                startup_thread.set_step(10, "启动完成！")
                QTimer.singleShot(500, startup_thread.close_window)
    
    # 初始化字体设置
    initialize_font_settings()
    
    # 使用QTimer延迟处理URL命令，确保主窗口完全初始化
    QTimer.singleShot(2000, delayed_url_processing)  # 延迟1秒处理URL

    # 启动应用程序事件循环
    try:
        logger.info("星野通知: 应用程序事件循环启动喵～")
        app.exec_()
    finally:
        shared_memory.detach()
        logger.info("星野通知: 共享内存已释放，程序完全退出喵～")
        # 确保启动窗口线程已退出
    if startup_thread and startup_thread.isRunning():
        startup_thread.close_window()
        startup_thread.wait(1000)  # 等待最多1秒
        sys.exit()