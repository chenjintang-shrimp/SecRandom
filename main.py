# ==================================================
# 导入库
# ==================================================
import os
import sys
import time

from PySide6.QtGui import *
from PySide6.QtCore import *
from PySide6.QtWidgets import *
from PySide6.QtNetwork import *
from qfluentwidgets import *
from loguru import logger

from app.tools.variable import *
from app.tools.path_utils import *
from app.tools.settings_default import *
from app.tools.settings_access import *
from app.Language.obtain_language import *
from app.tools.config import *

# 避免在模块导入时加载大量UI相关模块，使用延迟导入以缩短启动时的阻塞
# MainWindow 和 SettingsWindow 会在需要时动态导入

# 全局窗口引用（延迟创建）
main_window = None
settings_window = None


# 添加项目根目录到Python路径
project_root = str(get_app_root())
if project_root not in sys.path:
    sys.path.insert(0, project_root)


# ==================================================
# 日志配置相关函数
# ==================================================
def configure_logging():
    """配置日志系统"""
    # 确保日志目录存在
    log_dir = get_path(LOG_DIR)
    log_dir.mkdir(exist_ok=True)

    # 配置日志格式
    logger.add(
        log_dir / LOG_FILENAME_FORMAT,
        rotation=LOG_ROTATION_SIZE,
        retention=LOG_RETENTION_DAYS,
        compression=LOG_COMPRESSION,  # 启用压缩
        backtrace=True,  # 启用回溯信息
        diagnose=True,  # 启用诊断信息
        catch=True,  # 捕获未处理的异常
    )


# ==================================================
# 显示调节
# ==================================================
"""根据设置自动调整DPI缩放模式"""


def configure_dpi_scale():
    """配置DPI缩放模式"""
    dpiScale = readme_settings("basic_settings", "dpiScale")

    if dpiScale == "Auto":
        QApplication.setHighDpiScaleFactorRoundingPolicy(
            Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
        )
        os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"
        logger.debug("DPI缩放已设置为自动模式")
    else:
        os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "0"
        os.environ["QT_SCALE_FACTOR"] = str(dpiScale)
        logger.debug(f"DPI缩放已设置为{dpiScale}倍")


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
        logger.info("检测到已有 SecRandom 实例正在运行")

    logger.info("单实例检查通过，可以安全启动程序")

    return shared_memory


# ==================================================
# 字体设置相关函数
# ==================================================
def apply_font_settings():
    """应用字体设置 - 优化版本，使用字体管理器异步加载"""
    from app.tools.settings_access import readme_settings

    font_family = readme_settings("basic_settings", "font")

    setFontFamilies([font_family])
    QTimer.singleShot(FONT_APPLY_DELAY, lambda: apply_font_to_application(font_family))


def apply_font_to_application(font_family):
    """应用字体设置到整个应用程序，优化版本使用字体管理器

    Args:
        font_family (str): 字体家族名称
    """
    try:
        current_font = QApplication.font()
        app_font = QFont(font_family, current_font.pointSize())
        widgets_updated = 0
        widgets_skipped = 0
        for widget in QApplication.allWidgets():
            if isinstance(widget, QWidget):
                if update_widget_fonts(widget, app_font, font_family):
                    widgets_updated += 1
                else:
                    widgets_skipped += 1
        logger.debug(
            f"已应用字体: {font_family}, 更新了{widgets_updated}个控件字体, 跳过了{widgets_skipped}个已有相同字体的控件"
        )
    except Exception as e:
        logger.error(f"应用字体失败: {e}")


def update_widget_fonts(widget, font, font_family):
    """更新控件及其子控件的字体，优化版本减少内存占用，特别处理ComboBox等控件

    Args:
        widget: 要更新字体的控件
        font: 要应用的字体
        font_family: 目标字体家族名称

    Returns:
        bool: 是否更新了控件的字体
    """
    if widget is None:
        return False

    try:
        if not hasattr(widget, "font") or not hasattr(widget, "setFont"):
            return False
        current_widget_font = widget.font()
        if current_widget_font.family() == font_family:
            updated = False
        else:
            new_font = QFont(font.family(), current_widget_font.pointSize())
            new_font.setBold(current_widget_font.bold())
            new_font.setItalic(current_widget_font.italic())
            widget.setFont(new_font)
            updated = True

        if isinstance(widget, QWidget):
            children = widget.children()
            for child in children:
                if isinstance(child, QWidget):
                    child_updated = update_widget_fonts(child, font, font_family)
                    if child_updated:
                        updated = True
        return updated
    except Exception as e:
        logger.error(f"更新控件字体时发生异常: {e}")
        return False


def start_main_window():
    """创建主窗口实例"""
    global main_window
    try:
        # 延迟导入主窗口类，避免在模块导入阶段加载大量UI代码
        from app.view.main.window import MainWindow

        main_window = MainWindow()
        main_window.showSettingsRequested.connect(lambda: show_settings_window())
        main_window.showSettingsRequestedAbout.connect(
            lambda: show_settings_window_about
        )
        main_window.show()
        try:
            elapsed = time.perf_counter() - app_start_time
            logger.info(f"主窗口创建并显示完成，启动耗时: {elapsed:.3f}s")
        except Exception:
            pass
    except Exception as e:
        logger.error(f"创建主窗口失败: {e}", exc_info=True)


def create_settings_window():
    """创建设置窗口实例"""
    global settings_window
    try:
        # 延迟导入设置窗口，按需创建
        from app.view.settings.settings import SettingsWindow

        settings_window = SettingsWindow()
    except Exception as e:
        logger.error(f"创建设置窗口失败: {e}", exc_info=True)


def show_settings_window():
    """显示设置窗口"""
    try:
        # 按需创建设置窗口以减少启动阶段开销
        global settings_window
        if settings_window is None:
            create_settings_window()
        if settings_window is not None:
            settings_window.show_settings_window()
    except Exception as e:
        logger.error(f"显示设置窗口失败: {e}", exc_info=True)


def show_settings_window_about():
    """显示关于窗口"""
    try:
        global settings_window
        if settings_window is None:
            create_settings_window()
        if settings_window is not None:
            settings_window.show_settings_window_about()
    except Exception as e:
        logger.error(f"显示关于窗口失败: {e}", exc_info=True)


# ==================================================
# 应用程序初始化相关函数
# ==================================================
def initialize_app():
    """初始化应用程序，使用QTimer避免阻塞主线程，实现并行加载"""
    program_dir = str(get_app_root())

    # 更改当前工作目录
    if os.getcwd() != program_dir:
        os.chdir(program_dir)
        logger.info(f"工作目录已设置为: {program_dir}")

    # 并行加载资源
    # 管理设置文件，确保其存在且完整
    manage_settings_file()

    # 配置DPI缩放模式
    configure_dpi_scale()

    # 加载主题
    QTimer.singleShot(
        APP_INIT_DELAY,
        lambda: (
            # 读取主题设置并安全映射到Theme
            (
                lambda: (
                    setTheme(Theme.DARK)
                    if readme_settings("basic_settings", "theme") == "DARK"
                    else (
                        setTheme(Theme.AUTO)
                        if readme_settings("basic_settings", "theme") == "AUTO"
                        else setTheme(Theme.LIGHT)
                    )
                )
            )()
        ),
    )

    # 加载主题颜色
    QTimer.singleShot(
        APP_INIT_DELAY,
        lambda: (setThemeColor(readme_settings("basic_settings", "theme_color"))),
    )

    # 清除重启记录
    QTimer.singleShot(APP_INIT_DELAY, lambda: (remove_record("", "", "", "restart")))

    # 创建主窗口实例
    QTimer.singleShot(APP_INIT_DELAY, lambda: (start_main_window()))

    # 注意: 不预创建设置窗口，改为按需延迟创建以减少启动开销

    # 应用字体设置
    QTimer.singleShot(APP_INIT_DELAY, lambda: (apply_font_settings()))

    # 记录初始化完成时间（辅助诊断）
    logger.info("应用初始化调度已启动，主窗口将在延迟后创建")


# ==================================================
# 主程序入口
# ==================================================
def main_async():
    """主异步函数，用于启动应用程序"""
    QTimer.singleShot(APP_INIT_DELAY, initialize_app)


if __name__ == "__main__":
    # 记录应用启动时间，用于诊断各阶段耗时
    app_start_time = time.perf_counter()

    app = QApplication(sys.argv)

    import gc

    gc.enable()

    app.setQuitOnLastWindowClosed(APP_QUIT_ON_LAST_WINDOW_CLOSED)

    # 解决Dialog和FluentWindow共存时的窗口拉伸问题
    app.setAttribute(Qt.ApplicationAttribute.AA_DontCreateNativeWidgetSiblings)

    try:
        # 首先配置日志系统
        configure_logging()

        # 初始化应用程序
        main_async()

        app.exec()

        gc.collect()

        sys.exit()
    except Exception as e:
        print(f"应用程序启动失败: {e}")
        try:
            logger.error(f"应用程序启动失败: {e}", exc_info=True)
        except:
            pass
        sys.exit(1)
