import os
from qfluentwidgets import *  # type: ignore
from PyQt5.QtGui import QFontDatabase  # type: ignore

# 读取配置文件
def read_json(json_path): # type: ignore
    # 确认是否存在设置目录
    if './app/Settings' != None and not os.path.exists('./app/Settings'): # type: ignore
        os.makedirs('./app/Settings')
    if os.path.exists(json_path): # type: ignore
        try:
            with open(json_path, 'r', encoding='utf-8') as file: # type: ignore
                return json.load(file)
        except json.JSONDecodeError:
            # 如果文件内容不是有效的 JSON 格式，返回空字典
            return {} # type: ignore
    return {} # type: ignore

def modify_setting(): # type: ignore
    json_path = './app/Settings/Settings.json'
    read_json_dict = read_json(json_path) # type: ignore
    # 读取配置文件的version值
    version = read_json_dict.get('version', 0)  # type: ignore
    return version  # type: ignore

# 修改或新增指定软件配置中的某个值
def modify_setting_config(json_path, software_name, key, new_value):  # type: ignore
    # 确认是否存在设置目录
    if not os.path.exists('./app/Settings'):
        os.makedirs('./app/Settings')
    try:
        with open(json_path, 'r', encoding='utf-8') as file:  # type: ignore
            json_file = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        json_file = {}
    
    # 检查指定软件的配置是否存在
    if software_name not in json_file:
        json_file[software_name] = {}
    elif not isinstance(json_file[software_name], dict):
        # 如果不是字典，将其转换为字典
        json_file[software_name] = {}
    
    # 修改或新增指定键的值
    json_file[software_name][key] = new_value
    
    # 将更新后的数据写回文件
    with open(json_path, 'w', encoding='utf-8') as file: # type: ignore
        json.dump(json_file, file, ensure_ascii=False, indent=4)

def load_custom_font():
    font_path = './app/resource/font/HarmonyOS_Sans_SC_Bold.ttf'
    font_id = QFontDatabase.addApplicationFont(font_path)
    if font_id < 0:
        print("Failed to load font")
        return None
    font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
    return font_family

class Config(QConfig):
    # 主题模式
    dpiScale = OptionsConfigItem(
        "Window", "DpiScale", "Auto", OptionsValidator([1, 1.25, 1.5, 1.75, 2, "Auto"]), restart=True)
        
    # 全局动画模式配置
    globalAnimationMode = OptionsConfigItem(
        "Animation", "GlobalAnimationMode", "手动停止动画",
        OptionsValidator(["手动停止动画", "自动播放完整动画", "直接显示结果"]),
        restart=True)
        
    # 抽单人动画模式配置
    singleAnimationMode = OptionsConfigItem(
        "Animation", "SingleAnimationMode", "跟随全局设置",
        OptionsValidator(["跟随全局设置", "手动停止动画", "自动播放完整动画", "直接显示结果"]),
        restart=True)
        
    # 抽多人动画模式配置
    multiAnimationMode = OptionsConfigItem(
        "Animation", "MultiAnimationMode", "跟随全局设置",
        OptionsValidator(["跟随全局设置", "手动停止动画", "自动播放完整动画", "直接显示结果"]),
        restart=True)
        
    # 抽小组动画模式配置
    groupAnimationMode = OptionsConfigItem(
        "Animation", "GroupAnimationMode", "跟随全局设置",
        OptionsValidator(["跟随全局设置", "手动停止动画", "自动播放完整动画", "直接显示结果"]),
        restart=True)
    
    # 全局抽取重复模式配置
    globalDrawMode = OptionsConfigItem(
        "DrawMode", "GlobalDrawMode", "重复抽取",
        OptionsValidator(["重复抽取", "不重复抽取(直到软件重启)", "不重复抽取(直到抽完全部人)"]),
        restart=True)

    # 抽单人模式配置
    singleDrawMode = OptionsConfigItem(
        "DrawMode", "SingleDrawMode", "跟随全局设置", 
        OptionsValidator(["跟随全局设置", "重复抽取", "不重复抽取(直到软件重启)", "不重复抽取(直到抽完全部人)"]), 
        restart=True)
        
    # 多人抽取模式配置
    multiDrawMode = OptionsConfigItem(
        "DrawMode", "MultiDrawMode", "跟随全局设置",
        OptionsValidator(["跟随全局设置", "重复抽取", "不重复抽取(直到软件重启)", "不重复抽取(直到抽完全部人)"]),
        restart=True)
    
    # 抽小组抽取模式配置
    groupDrawMode = OptionsConfigItem(
        "DrawMode", "GroupDrawMode", "跟随全局设置",
        OptionsValidator(["跟随全局设置", "重复抽取", "不重复抽取(直到软件重启)", "不重复抽取(直到抽完全部人)"]),
        restart=True)
        
    # 全局语音播放配置
    globalVoicePlay = OptionsConfigItem(
        "VoicePlay", "GlobalVoicePlay", "是",
        OptionsValidator(["是", "否"]),
        restart=True)
        
    # 抽单人语音播放配置
    singleVoicePlay = OptionsConfigItem(
        "VoicePlay", "SingleVoicePlay", "跟随全局设置",
        OptionsValidator(["跟随全局设置", "是", "否"]),
        restart=True)
        
    # 抽多人语音播放配置
    multiVoicePlay = OptionsConfigItem(
        "VoicePlay", "MultiVoicePlay", "跟随全局设置",
        OptionsValidator(["跟随全局设置", "是", "否"]),
        restart=True)
        
    # 抽小组语音播放配置
    groupVoicePlay = OptionsConfigItem(
        "VoicePlay", "GroupVoicePlay", "跟随全局设置",
        OptionsValidator(["跟随全局设置", "是", "否"]),
        restart=True)

modify_setting_text = modify_setting() # type: ignore

YEAR = 2025
AUTHOR = "lzy98276"
VERSION = modify_setting_text # type: ignore
HELP_URL = "https://qfluentwidgets.com"
REPO_URL = "https://github.com/zhiyiYo/PyQt-Fluent-Widgets"
EXAMPLE_URL = "https://github.com/zhiyiYo/PyQt-Fluent-Widgets/tree/master/examples"
FEEDBACK_URL = "https://github.com/zhiyiYo/PyQt-Fluent-Widgets/issues"
RELEASE_URL = "https://github.com/zhiyiYo/PyQt-Fluent-Widgets/releases/latest"
ZH_SUPPORT_URL = "https://qfluentwidgets.com/zh/price/"
EN_SUPPORT_URL = "https://qfluentwidgets.com/price/"

cfg = Config()
cfg.themeMode.value = Theme.AUTO
qconfig.load('./app/Settings/config.json', cfg)  # type: ignore