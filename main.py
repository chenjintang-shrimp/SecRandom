# ==================================================
# 导入库
# ==================================================
import os
import sys
import json
import time
import multiprocessing

from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtNetwork import *
from qfluentwidgets import *
from loguru import logger
from pathlib import Path

from app.tools.variable import *
from app.tools.path_utils import *
from app.tools.settings_default import *
from app.common.config import cfg
from app.Language.obtain_language import *

from app.view.main.window import MainWindow
from app.view.settings.settings import SettingsWindow


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
        catch=True  # 捕获未处理的异常
    )

# ==================================================
# 显示调节
# ==================================================
"""根据设置自动调整DPI缩放模式"""
if cfg.get(cfg.dpiScale) == "Auto":
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"
    logger.debug("DPI缩放已设置为自动模式")
else:
    os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "0"
    os.environ["QT_SCALE_FACTOR"] = str(cfg.get(cfg.dpiScale))
    logger.debug(f"DPI缩放已设置为{cfg.get(cfg.dpiScale)}倍")

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
    
    logger.info('单实例检查通过，可以安全启动程序')
    
    return shared_memory

# ==================================================
# 字体设置相关函数
# ==================================================
def apply_font_settings():
    """应用字体设置"""
    font_family = DEFAULT_FONT_NAME_PRIMARY
    logger.info(f"字体设置: {font_family}")
    setFontFamilies([font_family])
    QTimer.singleShot(FONT_APPLY_DELAY, lambda: apply_font_to_application(font_family))

def apply_font_to_application(font_family):
    """应用字体设置到整个应用程序，只更新字体不是指定font_family的控件
    
    Args:
        font_family (str): 字体家族名称
    """
    try:
        # 获取当前应用程序默认字体
        current_font = QApplication.font()
        
        # 创建字体对象，只修改字体家族，保持原有字体大小
        app_font = QFont(font_family)
        app_font.setPointSize(current_font.pointSize())
        
        # 使用从variable.py导入的字体配置映射表
        font_config_map = FONT_CONFIG_MAP
        
        # 如果字体在配置映射表中，则加载对应的字体文件
        if font_family in font_config_map:
            config = font_config_map[font_family]
            font_path = get_resources_path('font', config['filename'])
            if font_path and file_exists(font_path):
                font_id = QFontDatabase.addApplicationFont(str(font_path))
                if font_id >= 0:
                    font_families = QFontDatabase.applicationFontFamilies(font_id)
                    if font_families:
                        app_font = QFont(font_families[0])
                        app_font.setPointSize(current_font.pointSize())
                    else:
                        logger.error(f"无法从字体文件获取字体家族: {font_path}")
                else:
                    logger.error(f"无法加载字体文件: {font_path}")
            else:
                logger.error(f"{config['display_name']}字体文件不存在: {font_path}")
        
        # 获取所有顶级窗口并更新它们的字体
        widgets_updated = 0
        widgets_skipped = 0
        for widget in QApplication.allWidgets():
            if isinstance(widget, QWidget):
                if update_widget_fonts(widget, app_font, font_family):
                    widgets_updated += 1
                else:
                    widgets_skipped += 1
            
        logger.info(f"已应用字体: {font_family}, 更新了{widgets_updated}个控件字体, 跳过了{widgets_skipped}个已有相同字体的控件")
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
        # 检查控件是否有font属性，只有有font属性的控件才尝试设置字体
        if not hasattr(widget, 'font') or not hasattr(widget, 'setFont'):
            return False
            
        # 获取控件当前字体
        current_widget_font = widget.font()
        
        # 检查当前字体是否已经是目标字体家族，如果是则跳过
        if current_widget_font.family() == font_family:
            updated = False
        else:
            # 创建新字体，只修改字体家族，保持原有字体大小和其他属性
            new_font = QFont(font.family(), current_widget_font.pointSize())
            # 保持原有字体的粗体和斜体属性
            new_font.setBold(current_widget_font.bold())
            new_font.setItalic(current_widget_font.italic())
            
            # 更新当前控件的字体
            widget.setFont(new_font)
            updated = True
        
        # 如果控件有子控件，递归更新子控件的字体
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
        # 创建主窗口实例
        main_window = MainWindow()
        # 连接信号到处理函数
        main_window.showSettingsRequested.connect(show_settings_window)
        main_window.show()
    except Exception as e:
        logger.error(f"创建主窗口失败: {e}", exc_info=True)

def create_settings_window():
    """创建设置窗口实例"""
    global settings_window
    try:
        settings_window = SettingsWindow()
        show_settings_window()
    except Exception as e:
        logger.error(f"创建设置窗口失败: {e}", exc_info=True)

def show_settings_window():
    """显示设置窗口"""
    try:
        settings_window.show_settings_window()
    except Exception as e:
        logger.error(f"显示设置窗口失败: {e}", exc_info=True)

# ==================================================
# 应用程序初始化相关函数
# ==================================================
def initialize_app():
    """初始化应用程序，使用QTimer避免阻塞主线程"""
    # 设置工作目录为程序所在目录，解决URL协议唤醒时工作目录错误的问题
    program_dir = str(get_app_root())
    
    # 更改当前工作目录
    if os.getcwd() != program_dir:
        os.chdir(program_dir)
        logger.info(f"工作目录已设置为: {program_dir}")
    
    # # 检查单实例
    # global shared_memory
    # shared_memory = check_single_instance()
    
    # 管理设置文件，确保其存在且完整
    QTimer.singleShot(APP_INIT_DELAY, manage_settings_file)

    # 创建主窗口实例
    QTimer.singleShot(APP_INIT_DELAY, start_main_window)

    # 创建设置窗口实例
    QTimer.singleShot(APP_INIT_DELAY, create_settings_window)

    # 应用字体设置
    QTimer.singleShot(APP_INIT_DELAY, apply_font_settings)

# ==================================================
# 主程序入口
# ==================================================
def main_async():
    """主异步函数，用于启动应用程序"""
    QTimer.singleShot(0, initialize_app)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    import gc
    gc.enable()

    app.setQuitOnLastWindowClosed(APP_QUIT_ON_LAST_WINDOW_CLOSED)
    
    try:
        configure_logging()

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