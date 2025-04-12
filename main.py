import os
import sys
import json

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from qfluentwidgets import *

from app.common.config import cfg
from app.view.SecRandom import Window 
from loguru import logger

from app.common.singleapplication import SingleApplication

# 配置日志记录
log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

logger.add(
    os.path.join(log_dir, "SecRandom_{time:YYYY-MM-DD}.log"),
    rotation="1 MB",
    encoding="utf-8",
    retention="30 days",
    format="{time:YYYY-MM-DD HH:mm:ss:SSS} | {level} | {name}:{function}:{line} - {message}"
)

if cfg.get(cfg.dpiScale) == "Auto":
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
else:
    os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "0"
    os.environ["QT_SCALE_FACTOR"] = str(cfg.get(cfg.dpiScale))

app = SingleApplication(sys.argv)
if not app.is_running:
    w = Window()
    app.main_window = w
    try:
        with open('app/Settings/Settings.json', 'r', encoding='utf-8') as f:
            settings = json.load(f)
            foundation_settings = settings.get('foundation', {})
            self_starting_enabled = foundation_settings.get('self_starting_enabled', False)
            if self_starting_enabled == False:
                w.show()
    except FileNotFoundError:
        logger.error("加载设置时出错: 文件不存在, 使用默认显示主窗口")
        w.show()
    except KeyError:
        logger.error("设置文件中缺少'foundation'键, 使用默认显示主窗口")
        w.show()
    except Exception as e:
        logger.error(f"加载设置时出错: {e}, 使用默认显示主窗口")
        w.show()
    sys.exit(app.exec_())
else:
    app.quit()