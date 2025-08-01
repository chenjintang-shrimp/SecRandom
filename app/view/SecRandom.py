# ================================================== ✧*｡٩(ˊᗜˋ*)و✧*｡
# 魔法导入水晶球 🔮
# ================================================== ✧*｡٩(ˊᗜˋ*)و✧*｡

# ✨ 系统自带魔法道具 ✨
import json
import os
import sys
import subprocess
import warnings
from urllib3.exceptions import InsecureRequestWarning

# 🧙‍♀️ 第三方魔法典籍 🧙‍♂️
from loguru import logger
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtNetwork import *
from qfluentwidgets import *
from qfluentwidgets import FluentIcon as fIcon

# 🏰 应用内部魔法卷轴 🏰
from app.common.config import YEAR, MONTH, AUTHOR, VERSION, APPLY_NAME, GITHUB_WEB, BILIBILI_WEB
from app.common.config import get_theme_icon, load_custom_font, check_for_updates, get_update_channel
from app.view.settings import settings_Window
from app.view.main_page.pumping_people import pumping_people
from app.view.main_page.pumping_reward import pumping_reward
from app.view.main_page.history_handoff_setting import history_handoff_setting
from app.view.levitation import LevitationWindow
from app.view.settings_page.about_setting import about

# ================================================== (^・ω・^ )
# 白露的初始化魔法阵 ⭐
# ================================================== (^・ω・^ )

# 🔮 忽略那些烦人的不安全请求警告
warnings.filterwarnings('ignore', category=InsecureRequestWarning)

# 星野导航：使用相对路径定位设置目录 ✧*｡٩(ˊᗜˋ*)و✧*｡
settings_dir = './app/Settings'
if not os.path.exists(settings_dir):
    os.makedirs(settings_dir)
    logger.info("白露魔法: 创建了设置目录哦~ ✧*｡٩(ˊᗜˋ*)و✧*｡")

def show_update_notification(latest_version):
    """显示自定义更新通知窗口"""
    try:
        from app.common.update_notification import UpdateNotification
        import sys

        # 确保有应用实例
        if QApplication.instance() is None:
            app = QApplication(sys.argv)
        else:
            app = QApplication.instance()

        # 创建并显示通知窗口
        notification = UpdateNotification(latest_version)
        notification.show()
        # 防止通知窗口关闭时程序退出
        original_quit_setting = app.quitOnLastWindowClosed()
        app.setQuitOnLastWindowClosed(False)
        notification.destroyed.connect(lambda: app.setQuitOnLastWindowClosed(original_quit_setting))
        logger.info(f"自定义更新通知已显示，版本: {latest_version}")

    except ImportError as e:
        logger.error(f"导入自定义通知失败: {str(e)}")
    except Exception as e:
        logger.error(f"显示更新通知失败: {str(e)}", exc_info=True)

# ==================================================
# 配置管理类
# ==================================================
class ConfigurationManager:
    """(^・ω・^ ) 白露的配置管理魔法书
    负责保管所有设置的小管家哦~ 会把重要的配置都藏在安全的地方！
    还会自动缓存设置，减少不必要的IO操作，是不是很聪明呀？(๑•̀ㅂ•́)و✧"""

    def __init__(self):
        """开启白露的配置魔法~ 初始化设置路径和默认值"""
        self.settings_path = 'app/Settings/Settings.json'  # 📜 普通设置文件路径
        self.enc_settings_path = 'app/SecRandom/enc_set.json'  # 🔒 加密设置文件路径
        self.default_settings = {
            'foundation': {
                'main_window_focus_mode': 0,
                'main_window_focus_time': 0,
                'window_width': 800,
                'window_height': 600,
                'pumping_floating_enabled': True,
                'pumping_floating_side': 0,
                'pumping_reward_side': 0,
                'main_window_mode': 0,
                'check_on_startup': True
            }
        }  # 📝 默认设置模板

    def load_settings(self):
        """(^・ω・^ ) 读取配置文件的魔法
        尝试打开设置文件，如果失败就用默认设置哦~ 不会让程序崩溃的！
        就像找不到钥匙时，总有备用钥匙可以用呢~ ✧*｡٩(ˊᗜˋ*)و✧*｡"""
        try:
            with open(self.settings_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"白露魔法出错: 加载设置文件失败了呢~ {e}")
            return self.default_settings  # 返回默认设置作为后备方案

    def get_foundation_setting(self, key):
        """(^・ω・^ ) 获取基础设置的小魔法
        从设置中找到对应的key值，如果找不到就用默认值哦~ 
        像在魔法袋里找东西，总能找到需要的那个！✨"""
        settings = self.load_settings()
        return settings.get('foundation', {}).get(key, self.default_settings['foundation'][key])

    def save_window_size(self, width, height):
        """(^・ω・^ ) 保存窗口大小的魔法咒语
        确保窗口不会太小（至少600x400），然后把新尺寸记下来~ 
        就像整理房间一样，要保持整洁又实用呢！(๑•̀ㅂ•́)و✧"""
        if width < 600 or height < 400:  # 太小的窗口可不行哦~ 
            logger.warning("白露提醒: 窗口尺寸太小啦，不保存哦~ ")
            return

        try:
            settings = self.load_settings()
            if 'foundation' not in settings:
                settings['foundation'] = {}  # 如果没有基础设置，就创建一个
            settings['foundation']['window_width'] = width
            settings['foundation']['window_height'] = height

            with open(self.settings_path, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=4)
            logger.info(f"白露魔法成功: 窗口大小已保存为 {width}x{height} ✨")
        except Exception as e:
            logger.error(f"白露魔法出错: 保存窗口大小失败了呢~ {e}")


# ==================================================
# 更新检查类
# ==================================================
class UpdateChecker(QObject):
    """(ﾟДﾟ≡ﾟдﾟ) 星野的更新巡逻队！
    负责监视有没有新版本发布，发现时会发出警报信号喵！
    就像太空巡逻兵一样，保护软件安全又新鲜！🚀✨"""

    update_available = pyqtSignal(str)  # 🚨 发现新版本时发射的信号

    def __init__(self, parent=None):
        """启动星野的更新检查系统！准备好监视版本变化喵！"""
        super().__init__(parent)

    def check_for_updates(self):
        """(ﾟДﾟ≡ﾟдﾟ) 启动更新检查任务！
        派出 Worker 小分队去执行秘密任务，不会打扰主线程喵！
        就像派出侦察机一样，悄悄地收集情报～ 🕵️‍♂️✨"""
        self.worker = self.UpdateCheckWorker()
        self.worker.result_ready.connect(self.on_update_result)
        self.worker.start()
        logger.info("星野指令: 更新检查小分队已出发！")

    class UpdateCheckWorker(QThread):
        """(ﾟДﾟ≡ﾟдﾟ) 更新检查特工队！
        在后台默默工作的线程，专门负责版本侦察任务喵！
        绝对不会打扰UI主线程的工作，非常专业！💪"""
        result_ready = pyqtSignal(bool, str)  # 📡 发送侦察结果的信号

        def run(self):
            """特工队行动开始！连接服务器获取最新版本信息！"""
            channel = get_update_channel()
            update_available, latest_version = check_for_updates(channel)
            self.result_ready.emit(update_available, latest_version)

    def on_update_result(self, update_available, latest_version):
        """(ﾟДﾟ≡ﾟдﾟ) 收到侦察报告！
        如果发现新版本，立刻拉响警报发射信号喵！
        绝不让用户错过任何重要更新！🚨✨"""
        if update_available and latest_version:
            logger.info(f"星野警报: 发现新版本 {latest_version}！准备通知用户！")
            self.update_available.emit(latest_version)  # 发射新版本信号


# ==================================================
# 系统托盘管理类
# ==================================================
class TrayIconManager:
    """(^・ω・^ ) 白露的系统托盘精灵！
    负责管理可爱的托盘图标和菜单，右键点击会有惊喜哦～
    就像藏在任务栏里的小助手，随时待命呢！(๑•̀ㅂ•́)و✧"""

    def __init__(self, main_window):
        """(^・ω・^ ) 唤醒托盘精灵！
        初始化系统托盘图标，设置好图标和提示文字～ 
        让它在任务栏安营扎寨，随时准备为用户服务！🏕️✨"""
        self.main_window = main_window
        self.tray_icon = QSystemTrayIcon(main_window)
        self.tray_icon.setIcon(QIcon('./app/resource/icon/SecRandom.png'))  # 设置可爱的图标
        self.tray_icon.setToolTip('SecRandom')  # 鼠标放上去会显示的文字
        self._create_menu()  # 创建魔法菜单
        self.tray_icon.show()  # 让托盘图标显示出来
        self.tray_icon.activated.connect(self._on_tray_activated)  # 连接点击事件
        logger.info("白露魔法: 托盘精灵已唤醒！")

    def _create_menu(self):
        """(^・ω・^ ) 制作托盘菜单魔法！
        精心设计的右键菜单，包含各种常用功能～ 
        就像准备了一桌丰盛的点心，总有一款适合你！🍰✨"""
        self.tray_menu = RoundMenu(parent=self.main_window)
        # 关于SecRandom
        self.tray_menu.addAction(Action(get_theme_icon("ic_fluent_info_20_filled"), '关于SecRandom', triggered=self.main_window.show_about_tab))
        self.tray_menu.addSeparator()
        # 主界面控制
        self.tray_menu.addAction(Action(get_theme_icon("ic_fluent_power_20_filled"), '暂时显示/隐藏主界面', triggered=self.main_window.toggle_window))
        self.tray_menu.addAction(Action(get_theme_icon("ic_fluent_window_ad_20_filled"), '暂时显示/隐藏浮窗', triggered=self.main_window.toggle_levitation_window))
        self.tray_menu.addAction(Action(get_theme_icon("ic_fluent_settings_20_filled"), '打开设置界面', triggered=self.main_window.show_setting_interface))
        self.tray_menu.addSeparator()
        # 系统操作
        # self.tray_menu.addAction(Action(get_theme_icon("ic_fluent_arrow_sync_20_filled"), '重启', triggered=self.main_window.restart_app))
        self.tray_menu.addAction(Action(get_theme_icon("ic_fluent_arrow_exit_20_filled"), '退出', triggered=self.main_window.close_window_secrandom))
        logger.info("白露魔法: 托盘菜单已准备就绪！")

    def _on_tray_activated(self, reason):
        """(^・ω・^ ) 托盘精灵响应事件！
        当用户点击托盘图标时，显示精心准备的菜单～ 
        就像有人敲门时，立刻开门迎接客人一样热情！(๑•̀ㅂ•́)و✧"""
        if reason in (QSystemTrayIcon.Trigger, QSystemTrayIcon.Context):
            pos = QCursor.pos()  # 获取鼠标位置
            self.tray_menu.exec_(pos)  # 在鼠标位置显示菜单
            logger.debug("白露魔法: 托盘菜单已显示给用户～ ")


# ==================================================
# 主窗口类
# ==================================================
class Window(MSFluentWindow):
    """(ﾟДﾟ≡ﾟдﾟ) 星野的主窗口司令部！
    这里是程序的核心指挥中心喵！所有重要操作都从这里发起～
    不要随便修改这里的核心逻辑，会导致系统崩溃喵！(๑•̀ㅂ•́)و✧"""

    # ==============================
    # 星野的魔法常量库 ✨
    # ==============================
    FOCUS_TIMEOUT_MAP = [
        0, 0, 3000, 5000, 10000, 15000, 30000, 60000, 120000, 180000, 300000, 600000, 1800000,
        2700000, 3600000, 7200000, 10800000, 21600000, 43200000
    ]
    """(ﾟДﾟ≡ﾟдﾟ) 星野的焦点超时魔法数组！
    存储不同模式下窗口自动隐藏的时间阈值（毫秒）喵～
    0=不隐藏，1=立即隐藏，其他值按索引对应不同时长！"""

    FOCUS_TIMEOUT_TIME = [
        0, 1000, 2000, 3000, 5000, 10000, 15000, 30000, 60000, 300000, 600000, 900000, 1800000,
        3600000, 7200000, 10800000, 21600000, 43200000
    ]
    """(ﾟДﾟ≡ﾟдﾟ) 星野的检查间隔魔法数组！
    存储焦点检查的时间间隔（毫秒）喵～
    不同索引对应不同的检查频率，数值越小检查越频繁！"""

    MINIMUM_WINDOW_SIZE = (600, 400)
    """(^・ω・^ ) 白露的窗口尺寸保护魔法！
    窗口最小不能小于这个尺寸哦～ 太小了会看不清内容的！(๑•̀ㅂ•́)و✧"""

    # ==============================
    # 初始化与生命周期方法
    # ==============================
    def __init__(self):
        super().__init__()
        # 初始化管理器
        self.config_manager = ConfigurationManager()
        self.update_checker = UpdateChecker(self)
        self.update_checker.update_available.connect(show_update_notification)

        # 初始化IPC服务器
        self.server = QLocalServer(self)
        self.server.newConnection.connect(self.handle_new_connection)
        self.server.listen("SecRandomIPC")

        # 初始化定时器
        self.focus_timer = QTimer(self)
        self.focus_timer.timeout.connect(self.check_focus_timeout)
        self.last_focus_time = QDateTime.currentDateTime()

        self.resize_timer = QTimer(self)
        self.resize_timer.setSingleShot(True)
        self.resize_timer.timeout.connect(lambda: self.config_manager.save_window_size(self.width(), self.height()))

        # 初始化焦点模式设置
        self.focus_mode = self.config_manager.get_foundation_setting('main_window_focus_mode')
        self.focus_time = self.config_manager.get_foundation_setting('main_window_focus_time')

        # 验证焦点时间有效性
        if self.focus_time >= len(self.FOCUS_TIMEOUT_TIME):
            self.focus_time = 1

        # 启动焦点计时器
        # ✨ 小鸟游星野：修复CPU占用过高问题，设置最低计时器间隔为200ms
        if self.focus_time == 0:
            self.focus_timer.start(200)  # 避免0ms间隔导致的CPU满载
        else:
            # 🌟 星穹铁道白露：确保计时器间隔不小于200ms
            interval = max(self.FOCUS_TIMEOUT_TIME[self.focus_time], 200)
            self.focus_timer.start(interval)

        # 设置窗口属性
        window_width = self.config_manager.get_foundation_setting('window_width')
        window_height = self.config_manager.get_foundation_setting('window_height')
        self.resize(window_width, window_height)
        self.setMinimumSize(*self.MINIMUM_WINDOW_SIZE)
        self.setWindowTitle('SecRandom')
        self.setWindowIcon(QIcon('./app/resource/icon/SecRandom.png'))

        # 初始化悬浮窗
        self.start_cleanup()
        self.levitation_window = LevitationWindow()
        pumping_floating_enabled = self.config_manager.get_foundation_setting('pumping_floating_enabled')
        if pumping_floating_enabled:
            self.levitation_window.show()

        # 初始化系统托盘
        self.tray_manager = TrayIconManager(self)
        """星野部署：
        系统托盘图标已激活
        右键可以召唤菜单喵～(ฅ´ω`ฅ)"""

        # 定位窗口
        self._position_window()

        # 启动画面
        self.splashScreen = SplashScreen(self.windowIcon(), self)
        self.splashScreen.setIconSize(QSize(256, 256))

        # 显示窗口设置
        self._apply_window_visibility_settings()

        # 创建子界面
        self.createSubInterface()
        self.splashScreen.finish()

        # 检查更新
        check_startup = self.config_manager.get_foundation_setting('check_on_startup')
        if check_startup:
            QTimer.singleShot(1000, self.check_updates_async)

    def _position_window(self):
        """(^・ω・^ ) 白露的窗口定位魔法！
        根据屏幕尺寸和用户设置自动计算最佳位置～
        确保窗口出现在最舒服的视觉位置，不会让眼睛疲劳哦！(๑•̀ㅂ•́)و✧"""
        screen = QApplication.primaryScreen()
        desktop = screen.availableGeometry()
        w, h = desktop.width(), desktop.height()
        main_window_mode = self.config_manager.get_foundation_setting('main_window_mode')
        
        if main_window_mode == 0:
            # 模式0：屏幕正中央定位
            self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)
        elif main_window_mode == 1:
            # 模式1：屏幕偏下定位（更符合视觉习惯）
            self.move(w // 2 - self.width() // 2, h * 3 // 5 - self.height() // 2)
        logger.debug(f"白露魔法: 窗口已定位到({self.x()}, {self.y()})位置～ ")

    def _apply_window_visibility_settings(self):
        """(^・ω・^ ) 白露的窗口显示魔法！
        根据用户保存的设置决定窗口是否自动显示～
        如果上次设置为显示，启动时就会自动出现哦！(๑•̀ㅂ•́)و✧"""
        try:
            settings = self.config_manager.load_settings()
            if settings.get('toggle_window') == 'show':
                self.show()
                logger.info("白露魔法: 根据设置自动显示主窗口～ ")
        except Exception as e:
            logger.error(f"白露魔法出错: 加载窗口显示设置失败了呢～ {e}")

    def check_updates_async(self):
        """(ﾟДﾟ≡ﾟдﾟ) 星野的太空巡逻队出发！
        正在异步执行版本侦察任务喵～ 不会阻塞主线程哦！
        发现新版本时会立刻拉响警报通知用户喵！🚀✨"""
        self.update_checker.check_for_updates()
        logger.info("星野指令: 更新检查任务已启动，正在扫描宇宙寻找新版本～ ")

    def createSubInterface(self):
        """(^・ω・^ ) 白露的魔法建筑师开工啦！
        正在搭建子界面导航系统，就像建造一座功能齐全的魔法城堡～
        每个功能模块都是城堡的房间，马上就能入住使用啦！🏰✨"""
        # 创建事件循环确保界面组件正确初始化
        loop = QEventLoop(self)
        QTimer.singleShot(1, loop.quit)
        loop.exec()
        logger.debug("白露建筑: 界面初始化事件循环已完成～ ")

        # 创建设置界面
        self.settingInterface = settings_Window(self)
        self.settingInterface.setObjectName("settingInterface")
        logger.debug("白露建筑: 设置界面房间已建成～ ")

        # 创建历史交接设置界面
        self.history_handoff_settingInterface = history_handoff_setting(self)
        self.history_handoff_settingInterface.setObjectName("history_handoff_settingInterface")
        logger.debug("白露建筑: 历史交接设置界面房间已建成～ ")

        # 创建抽人界面（主界面）
        self.pumping_peopleInterface = pumping_people(self)
        self.pumping_peopleInterface.setObjectName("pumping_peopleInterface")
        logger.debug("白露建筑: 抽人界面房间已建成～ ")

        # 创建关于界面
        self.about_settingInterface = about(self)
        self.about_settingInterface.setObjectName("about_settingInterface")
        logger.debug("白露建筑: 关于界面房间已建成～ ")

        # 创建抽奖界面
        self.pumping_rewardInterface = pumping_reward(self)
        self.pumping_rewardInterface.setObjectName("pumping_rewardInterface")
        logger.debug("白露建筑: 抽奖界面房间已建成～ ")

        # 初始化导航系统
        self.initNavigation()
        logger.info("白露建筑: 所有子界面和导航系统已完工！城堡可以正式对外开放啦～ ")

    def initNavigation(self):
        """(^・ω・^ ) 白露的魔法导航系统启动！
        根据用户设置构建个性化菜单导航～ 就像魔法地图一样清晰！
        确保每个功能模块都有明确路标，不会让用户迷路哦！🧭✨"""
        try:
            with open('app/Settings/Settings.json', 'r', encoding='utf-8') as f:
                settings = json.load(f)
                foundation_settings = settings.get('foundation', {})
                logger.debug("白露导航: 已读取导航配置，准备构建个性化菜单～ ")

                # 根据设置决定"抽人"界面位置
                if foundation_settings.get('pumping_floating_side', 0) == 1:
                    self.addSubInterface(self.pumping_peopleInterface, get_theme_icon("ic_fluent_people_community_20_filled"), '抽人', position=NavigationItemPosition.BOTTOM)
                    logger.debug("白露导航: '抽人'界面已放置在底部导航栏～ ")
                else:
                    self.addSubInterface(self.pumping_peopleInterface, get_theme_icon("ic_fluent_people_community_20_filled"), '抽人', position=NavigationItemPosition.TOP)
                    logger.debug("白露导航: '抽人'界面已放置在顶部导航栏～ ")

                # 根据设置决定"抽奖"界面位置
                if foundation_settings.get('pumping_reward_side', 0) == 1:
                    self.addSubInterface(self.pumping_rewardInterface, get_theme_icon("ic_fluent_reward_20_filled"), '抽奖', position=NavigationItemPosition.BOTTOM)
                    logger.debug("白露导航: '抽奖'界面已放置在底部导航栏～ ")
                else:
                    self.addSubInterface(self.pumping_rewardInterface, get_theme_icon("ic_fluent_reward_20_filled"), '抽奖', position=NavigationItemPosition.TOP)
                    logger.debug("白露导航: '抽奖'界面已放置在顶部导航栏～ ")

        except FileNotFoundError as e:
            logger.error(f"白露导航出错: 配置文件找不到啦～ {e}, 使用默认顶部导航布局")
            self.addSubInterface(self.pumping_peopleInterface, get_theme_icon("ic_fluent_people_community_20_filled"), '抽人', position=NavigationItemPosition.TOP)
            self.addSubInterface(self.pumping_rewardInterface, get_theme_icon("ic_fluent_reward_20_filled"), '抽奖', position=NavigationItemPosition.TOP)

        # 添加固定位置的导航项
        self.addSubInterface(self.history_handoff_settingInterface, get_theme_icon("ic_fluent_chat_history_20_filled"), '历史记录', position=NavigationItemPosition.BOTTOM)
        self.addSubInterface(self.about_settingInterface, get_theme_icon("ic_fluent_info_20_filled"), '关于', position=NavigationItemPosition.BOTTOM)
        logger.info("白露导航: 所有导航项已布置完成，导航系统可以正常使用啦～ ")

    def closeEvent(self, event):
        """(ﾟДﾟ≡ﾟдﾟ) 星野的安全防御系统启动！
        检测到窗口关闭事件！已成功拦截喵～ 
        程序将撤退到系统托盘继续潜伏运行喵！(=｀ω´=)"""
        self.hide()
        event.ignore()
        self.save_window_size()
        logger.info("星野防御: 窗口关闭事件已拦截，程序已转入后台运行～ ")

    def resizeEvent(self, event):
        """(ﾟДﾟ≡ﾟдﾟ) 星野的尺寸感应系统触发！
        检测到窗口大小变化喵～ 正在启动尺寸记录倒计时！
        500毫秒内如果不再变化就会自动保存新尺寸喵～(=｀ω´=)"""
        self.resize_timer.start(500)
        super().resizeEvent(event)

    def save_window_size(self):
        """(^・ω・^ ) 白露的尺寸保管员上线！
        正在用魔法记录当前窗口尺寸～ 就像用相机拍照存档一样！
        下次启动时会自动恢复到这个大小，不用重新调整啦～ ✨"""
        if not self.isMaximized():
            self.config_manager.save_window_size(self.width(), self.height())
            logger.info(f"白露存档: 已保存窗口尺寸为{self.width()}x{self.height()}像素～ ")

    def update_focus_mode(self, mode):
        """(^・ω・^ ) 白露的焦点模式调节器！
        已成功切换到{mode}档魔法模式～ 就像调节台灯亮度一样简单！
        不同档位会触发不同的自动隐藏魔法，数值越大隐藏速度越快哦～ ✨"""
        self.focus_mode = mode
        self.last_focus_time = QDateTime.currentDateTime()
        logger.debug(f"白露调节: 焦点模式已切换到{mode}档～ ")

        if mode < len(self.focus_timeout_map):
            self.focus_timeout = self.focus_timeout_map[mode]
            logger.debug(f"白露调节: 自动隐藏阈值已设置为{self.focus_timeout}毫秒～ ")

    def update_focus_time(self, time):
        """(^・ω・^ ) 白露的时间魔法更新！
        焦点检查时间间隔已调整为{time}档～ 就像给闹钟设置新的提醒周期！
        现在每{self.focus_timeout_time[time] if time < len(self.focus_timeout_time) else 0}毫秒检查一次窗口焦点哦～ ⏰"""
        self.focus_time = time
        self.last_focus_time = QDateTime.currentDateTime()
        logger.debug(f"白露计时: 焦点检查时间已更新到{time}档～ ")

        if time < len(self.focus_timeout_time):
            self.focus_timeout = self.focus_timeout_time[time]
            self.focus_timer.start(self.focus_timeout)
            logger.debug(f"白露计时: 检查间隔已设置为{self.focus_timeout}毫秒～ ")
        else:
            self.focus_timer.start(0)
            logger.debug(f"白露计时: 检查间隔已设置为连续模式～ ")

    def check_focus_timeout(self):
        """(ﾟДﾟ≡ﾟдﾟ) 星野的焦点监视器启动！
        正在扫描窗口焦点状态喵～ {self.focus_timeout}毫秒无操作将触发自动隐藏魔法！
        不要走开太久哦，否则我会躲起来喵～(=｀ω´=)"""
        if self.focus_mode == 0:  # 不关闭模式
            return

        if not self.isActiveWindow() and not self.isMinimized():
            elapsed = self.last_focus_time.msecsTo(QDateTime.currentDateTime())
            timeout = self.focus_timeout_map[self.focus_mode]
            logger.debug(f"星野监视: 窗口已闲置{elapsed}毫秒，阈值为{timeout}毫秒～ ")

            if self.focus_mode == 1:  # 直接关闭模式
                self.hide()
                logger.info("星野行动: 焦点模式1触发，窗口已自动隐藏～ ")
            elif elapsed >= timeout:
                self.hide()
                logger.info(f"星野行动: 窗口闲置超过{timeout}毫秒，已自动隐藏～ ")
        else:
            self.last_focus_time = QDateTime.currentDateTime()
            logger.debug("星野监视: 检测到用户活动，重置闲置计时器～ ")

    def stop_focus_timer(self):
        """星野守卫：
        焦点检测计时器已停止！
        窗口不会自动隐藏啦喵～(=｀ω´=)"""
        self.focus_timer.stop()

    def showEvent(self, event):
        """白露唤醒：
        窗口显示时重置焦点时间
        开始监控用户活动哦～(>^ω^<)"""
        super().showEvent(event)
        self.last_focus_time = QDateTime.currentDateTime()

    def focusInEvent(self, event):
        """星野注意：
        窗口获得焦点！
        重置闲置计时器喵～(ฅ´ω`ฅ)"""
        super().focusInEvent(event)
        self.last_focus_time = QDateTime.currentDateTime()

    def show_about_tab(self):
        """白露向导：
        正在导航到关于页面
        这里可以查看软件版本和作者信息哦～(>^ω^<)"""
        if self.isMinimized():
            self.showNormal()
        else:
            self.show()
            self.activateWindow()
            self.raise_()
        self.switchTo(self.about_settingInterface)

    def start_cleanup(self):
        """(ﾟДﾟ≡ﾟдﾟ) 星野的启动清理魔法！
        软件启动时清理上次遗留的临时抽取记录文件喵～
        根据抽选模式决定是否需要清理，保持系统整洁！"""
        try:
            with open('app/Settings/Settings.json', 'r', encoding='utf-8') as f:
                settings = json.load(f)
                pumping_people_draw_mode = settings['pumping_people']['draw_mode']
                logger.debug(f"星野侦察: 抽选模式为{pumping_people_draw_mode}，准备执行对应清理方案～ ")

        except Exception as e:
            pumping_people_draw_mode = 1
            logger.error(f"星野魔法出错: 加载抽选模式设置失败了喵～ {e}, 使用默认:不重复抽取(直到软件重启)模式")

        import glob
        temp_dir = "app/resource/Temp"

        if pumping_people_draw_mode == 1:  # 不重复抽取(直到软件重启)
            if os.path.exists(temp_dir):
                for file in glob.glob(f"{temp_dir}/until_the_reboot_*.json"):
                    try:
                        os.remove(file)
                        logger.info(f"星野清理: 已删除临时抽取记录文件: {file}")
                    except Exception as e:
                        logger.error(f"星野清理失败: 删除临时文件出错喵～ {e}")



    def toggle_window(self):
        """(ﾟДﾟ≡ﾟдﾟ) 星野的窗口切换魔法！
        显示→隐藏→显示，像捉迷藏一样好玩喵～
        切换时会自动激活抽人界面，方便用户继续操作！"""  
        if self.isVisible():
            self.hide()
            logger.info("星野魔法: 主窗口已隐藏～ ")
            if self.isMinimized():
                self.showNormal()
        else:
            if self.isMinimized():
                self.showNormal()
            else:
                self.show()
                self.activateWindow()
                self.raise_()
            logger.info("星野魔法: 主窗口已显示～ ")
        self.switchTo(self.pumping_peopleInterface)

    def calculate_menu_position(self, menu):
        """白露定位系统：
        正在计算托盘菜单最佳显示位置
        确保菜单不会超出屏幕边界哦～(๑•̀ㅂ•́)و✧"""
        screen = QApplication.primaryScreen().availableGeometry()
        menu_size = menu.sizeHint()

        cursor_pos = QCursor.pos()

        x = cursor_pos.x() + 20
        y = cursor_pos.y() - menu_size.height()

        if x + menu_size.width() > screen.right():
            x = screen.right() - menu_size.width()
        if y < screen.top():
            y = screen.top()

        return QPoint(x, y)

    def close_window_secrandom(self):
        """(ﾟДﾟ≡ﾟдﾟ) 星野的终极安全检查！
        检测到退出请求！需要通过密码验证才能离开基地喵！
        这是最高级别的安全防御，不能让坏人随便入侵喵！🔒✨"""
        try:
            with open('app/SecRandom/enc_set.json', 'r', encoding='utf-8') as f:
                settings = json.load(f)
                logger.debug("星野安检: 正在读取安全设置，准备执行退出验证～ ")

                if settings.get('hashed_set', {}).get('start_password_enabled', False) == True:
                    if settings.get('hashed_set', {}).get('exit_verification_enabled', False) == True:
                        from app.common.password_dialog import PasswordDialog
                        dialog = PasswordDialog(self)
                        if dialog.exec_() != QDialog.Accepted:
                            logger.warning("星野安检: 用户取消退出程序操作，安全防御已解除～ ")
                            return
        except Exception as e:
            logger.error(f"星野安检失败: 密码验证系统出错喵～ {e}")
            return

        logger.info("星野撤退: 安全验证通过，开始执行完全退出程序流程～ ")
        self.hide()
        if hasattr(self, 'levitation_window'):
            self.levitation_window.hide()
            logger.debug("星野撤退: 悬浮窗已隐藏～ ")
        if hasattr(self, 'focus_timer'):
            self.stop_focus_timer()
            logger.debug("星野撤退: 焦点计时器已停止～ ")
        if hasattr(self, 'server'):
            self.server.close()
            logger.debug("星野撤退: IPC服务器已关闭～ ")
        # 关闭共享内存
        if hasattr(self, 'shared_memory'):
            self.shared_memory.detach()
            logger.info("星野撤退: 共享内存已安全关闭～ ")
        logger.remove()
        # 确保完全退出应用程序
        QApplication.quit()
        sys.exit(0)

    def restart_app(self):
        """星野重启指令：
        正在执行程序重启流程！
        多数设置将在重启后生效喵～(ﾟДﾟ≡ﾟдﾟ)"""
        try:
            with open('app/SecRandom/enc_set.json', 'r', encoding='utf-8') as f:
                settings = json.load(f)
                if settings.get('hashed_set', {}).get('start_password_enabled', False) == True:
                    if settings.get('hashed_set', {}).get('restart_verification_enabled', False) == True:
                        from app.common.password_dialog import PasswordDialog
                        dialog = PasswordDialog(self)
                        if dialog.exec_() != QDialog.Accepted:
                            logger.warning("用户取消重启操作")
                            return
        except Exception as e:
            logger.error(f"密码验证过程出错: {e}")
            return

        logger.info("星野重启: 安全验证通过，开始执行完全重启程序流程～ ")
        self.hide()
        if hasattr(self, 'levitation_window'):
            self.levitation_window.hide()
            logger.debug("星野重启: 悬浮窗已隐藏～ ")
        if hasattr(self, 'focus_timer'):
            self.stop_focus_timer()
            logger.debug("星野重启: 焦点计时器已停止～ ")
        if hasattr(self, 'server'):
            self.server.close()
            logger.debug("星野重启: IPC服务器已关闭～ ")
        # 关闭共享内存
        if hasattr(self, 'shared_memory'):
            self.shared_memory.detach()
            logger.info("星野重启: 共享内存已安全关闭～ ")
        logger.remove()
        # 使用新进程组启动，避免被当前进程退出影响
        subprocess.Popen([sys.executable] + sys.argv, creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
        # 退出当前进程
        sys.exit(0)


    def show_setting_interface(self):
        """白露设置向导：
        正在打开设置界面
        小心不要乱动高级选项哦～(^・ω・^ )"""
        try:
            with open('app/SecRandom/enc_set.json', 'r', encoding='utf-8') as f:
                settings = json.load(f)
                if settings.get('hashed_set', {}).get('start_password_enabled', False):
                    from app.common.password_dialog import PasswordDialog
                    dialog = PasswordDialog(self)
                    if dialog.exec_() != QDialog.Accepted:
                        logger.warning("用户取消打开设置界面操作")
                        return
        except Exception as e:
            logger.error(f"密码验证失败: {e}")

        try:
            with open('app/SecRandom/enc_set.json', 'r', encoding='utf-8') as f:
                settings = json.load(f)
            settings['hashed_set']['verification_start'] = True
            with open('app/SecRandom/enc_set.json', 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=4)
        except Exception as e:
            logger.error(f"写入verification_start失败: {e}")

        if not hasattr(self, 'settingInterface') or not self.settingInterface:
            self.settingInterface = settings_Window(self)
        if not self.settingInterface.isVisible():
            if self.settingInterface.isMinimized():
                self.settingInterface.showNormal()
            else:
                self.settingInterface.show()
                self.settingInterface.activateWindow()
                self.settingInterface.raise_()

    def toggle_levitation_window(self):
        """星野悬浮控制：
        浮窗显示状态切换中！
        注意不要让它挡住重要内容喵～(ฅ´ω`ฅ)"""
        try:
            with open('app/SecRandom/enc_set.json', 'r', encoding='utf-8') as f:
                settings = json.load(f)
                if settings.get('hashed_set', {}).get('start_password_enabled', False) == True:
                    if settings.get('hashed_set', {}).get('show_hide_verification_enabled', False) == True:
                        from app.common.password_dialog import PasswordDialog
                        dialog = PasswordDialog(self)
                        if dialog.exec_() != QDialog.Accepted:
                            logger.warning("用户取消暂时切换浮窗显示/隐藏状态操作")
                            return
        except Exception as e:
            logger.error(f"密码验证失败: {e}")
            return

        if not hasattr(self, 'levitation_window') or not self.levitation_window:
            self.levitation_window.show()
        elif self.levitation_window.isVisible():
            self.levitation_window.hide()
        else:
            self.levitation_window.show()
            self.levitation_window.activateWindow()
            self.levitation_window.raise_()

    def handle_new_connection(self):
        client_connection = self.server.nextPendingConnection()
        if not client_connection:
            return

        client_connection.readyRead.connect(lambda: self.read_client_data(client_connection))
        client_connection.disconnected.connect(client_connection.deleteLater)

    def read_client_data(self, client_connection):
        data = client_connection.readAll().data().decode().strip()
        if data == 'show':
            self.toggle_window()
        client_connection.disconnectFromServer()
        client_connection.readyRead.connect(lambda: self.read_client_data(client_connection))
        client_connection.disconnected.connect(client_connection.deleteLater)

    def show_window_from_ipc(self, socket):
        """从IPC接收显示窗口请求并激活窗口"""
        data = socket.readAll().data().decode().strip()
        logger.info(f"接收到IPC窗口显示请求: {data}")
        
        # 确保主窗口资源正确加载并显示
        self.show()
        self.activateWindow()
        self.raise_()
        
        # 处理悬浮窗口
        self._handle_levitation_window()
        
        socket.disconnectFromServer()

    def _handle_levitation_window(self):
        """处理悬浮窗口激活"""
        if hasattr(self, 'levitation_window') and self.levitation_window:
            self.levitation_window.raise_()
            self.levitation_window.activateWindow()