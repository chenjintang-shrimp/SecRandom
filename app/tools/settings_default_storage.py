from app.tools.variable import *

# ==================================================
# 默认设置列表 - 层级结构
# ==================================================
DEFAULT_SETTINGS = {
    "home": {
        "title": {
            "default_value": None,
            "ZH_CN": {
                "name": "主页",
                "description": "软件主页"
            },
            "EN_US": {
                "name": "Home",
                "description": "Software home page"
            }
        },
    },
    "basic_settings": {
        "title": {
            "default_value": None,
            "ZH_CN": {
                "name": "基础设置",
                "description": "软件基础设置"
            },
            "EN_US": {
                "name": "Basic Set",
                "description": "Software basic settings"
            }
        },
        "basic_function": {
            "default_value": None,
            "ZH_CN": {
                "name": "基础功能",
                "description": "软件基础功能"
            },
            "EN_US": {
                "name": "Basic Function",
                "description": "Software basic function"
            }
        },
        "data_management": {
            "default_value": None,
            "ZH_CN": {
                "name": "数据管理",
                "description": "数据管理"
            },
            "EN_US": {
                "name": "Data Management",
                "description": "Data management"
            }
        },
        "autostart": {
            "default_value": False,
            "ZH_CN": {
                "name": "开机自启",
                "description": "设置软件是否在开机时自动启动",
                "switchbutton_name": {
                    "enable": "开启",
                    "disable": "关闭"
                }
            },
            "EN_US": {
                "name": "Autostart",
                "description": "Set whether the software should start automatically when the system boots",
                "switchbutton_name": {
                    "enable": "Enable",
                    "disable": "Disable"
                }
            }
        },
        "check_update": {
            "default_value": True,
            "ZH_CN": {
                "name": "检查更新",
                "description": "设置是否在启动时检查软件更新",
                "switchbutton_name": {
                    "enable": "启用",
                    "disable": "禁用"
                }
            },
            "EN_US": {
                "name": "Check Update",
                "description": "Set whether the software should check for updates when it starts",
                "switchbutton_name": {
                    "enable": "Enable",
                    "disable": "Disable"
                }
            },
        },
        "show_startup_window": {
            "default_value": True,
            "ZH_CN": {
                "name": "显示启动窗口",
                "description": "设置是否在启动时显示启动窗口",
                "switchbutton_name": {
                    "enable": "显示",
                    "disable": "不显示"
                }
            },
            "EN_US": {
                "name": "Show Startup Window",
                "description": "Set whether the software should show the startup window when it starts",
                "switchbutton_name": {
                    "enable": "Show",
                    "disable": "Hide"
                }
            },
        },
        "export_diagnostic_data": {
            "default_value": None,
            "ZH_CN": {
                "name": "导出诊断数据",
                "description": "设置是否在退出时导出诊断数据",
                "pushbutton_name": "导出诊断数据"
            },
            "EN_US": {
                "name": "Export Diagnostic Data",
                "description": "Set whether the software should export diagnostic data when it exits",
                "pushbutton_name": "Export Diagnostic Data"
            },
        },
        "export_settings": {
            "default_value": None,
            "ZH_CN": {
                "name": "导出设置",
                "description": "设置是否在退出时导出设置",
                "pushbutton_name": "导出设置"
            },
            "EN_US": {
                "name": "Export Settings",
                "description": "Set whether the software should export settings when it exits",
                "pushbutton_name": "Export Settings"
            },
        },
        "import_settings": {
            "default_value": None,
            "ZH_CN": {
                "name": "导入设置",
                "description": "设置是否在启动时导入设置",
                "pushbutton_name": "导入设置"
            },
            "EN_US": {
                "name": "Import Settings",
                "description": "Set whether the software should import settings when it starts",
                "pushbutton_name": "Import Settings"
            },
        },
        "export_all_data": {
            "default_value": None,
            "ZH_CN": {
                "name": "导出所有数据",
                "description": "设置是否在退出时导出所有数据",
                "pushbutton_name": "导出所有数据"
            },
            "EN_US": {
                "name": "Export All Data",
                "description": "Set whether the software should export all data when it exits",
                "pushbutton_name": "Export All Data"
            },
        },
        "import_all_data": {
            "default_value": None,
            "ZH_CN": {
                "name": "导入所有数据",
                "description": "设置是否在启动时导入所有数据",
                "pushbutton_name": "导入所有数据"
            },
            "EN_US": {
                "name": "Import All Data",
                "description": "Set whether the software should import all data when it starts",
                "pushbutton_name": "Import All Data"
            },
        },
    },
    "list_management":{
        "title": {
            "default_value": None,
            "ZH_CN": {
                "name": "名单管理",
                "description": "软件名单管理页面"
            },
            "EN_US": {
                "name": "List Mgt",
                "description": "Software list management page"
            }
        },
    },
    "roll_call_list": {
        "title": {
            "default_value": None,
            "ZH_CN": {
                "name": "点名名单",
                "description": "点名名单"
            },
            "EN_US": {
                "name": "Roll Call",
                "description": "Roll call list"
            }
        },
        "set_class_name": {
            "default_value": None,
            "ZH_CN": {
                "name": "设置班级名称",
                "description": "设置班级名称"
            },
            "EN_US": {
                "name": "Set Class Name",
                "description": "Set class name"
            }
        },
        "select_class_name": {
            "default_value": 0,
            "ZH_CN": {
                "name": "选择班级",
                "description": "选择班级"
            },
            "EN_US": {
                "name": "Select Class",
                "description": "Select class"
            }
        },
        "import_student_name": {
            "default_value": None,
            "ZH_CN": {
                "name": "导入学生名单",
                "description": "导入学生名单"
            },
            "EN_US": {
                "name": "Import Student List",
                "description": "Import student list"
            }
        },
        "name_setting": {
            "default_value": None,
            "ZH_CN": {
                "name": "设置姓名",
                "description": "设置姓名"
            },
            "EN_US": {
                "name": "Set Name",
                "description": "Set name"
            }
        },
        "gender_setting": {
            "default_value": None,
            "ZH_CN": {
                "name": "设置性别",
                "description": "设置性别"
            },
            "EN_US": {
                "name": "Set Gender",
                "description": "Set gender"
            }
        },
        "group_setting": {
            "default_value": None,
            "ZH_CN": {
                "name": "设置班级",
                "description": "设置班级"
            },
            "EN_US": {
                "name": "Set Group",
                "description": "Set group"
            }
        },
        "export_student_name": {
            "default_value": None,
            "ZH_CN": {
                "name": "导出学生名单",
                "description": "导出学生名单"
            },
            "EN_US": {
                "name": "Export Student List",
                "description": "Export student list"
            }
        },
    },
    "roll_call_table": {
        "title": {
            "default_value": None,
            "ZH_CN": {
                "name": "点名表格",
                "description": "用于展示和管理点名名单的表格"
            },
            "EN_US": {
                "name": "Roll Call Table",
                "description": "Table for displaying and managing roll call lists"
            }
        },
        "HeaderLabels": {
            "default_value": None,
            "ZH_CN": {
                "name": ["存在", "学号", "姓名", "性别", "小组"],
                "description": "点名表格的列标题"
            },
            "EN_US": {
                "name": ["Exist", "Student ID", "Name", "Gender", "Group"],
                "description": "Column headers for the roll call table"
            }
        },
    },
    "custom_draw_list": {
        "title": {
            "default_value": None,
            "ZH_CN": {
                "name": "自定义抽签",
                "description": "自定义抽签"
            },
            "EN_US": {
                "name": "Cust Draw",
                "description": "Custom draw"
            }
        },
    },
    "lottery_list": {
        "title": {
            "default_value": None,
            "ZH_CN": {
                "name": "抽奖名单",
                "description": "抽奖名单"
            },
            "EN_US": {
                "name": "Lottery",
                "description": "Lottery list"
            }
        },
        "set_pool_name": {
            "default_value": None,
            "ZH_CN": {
                "name": "设置奖池名称",
                "description": "设置奖池名称"
            },
            "EN_US": {
                "name": "Set Pool Name",
                "description": "Set pool name"
            }
        },
        "select_pool_name": {
            "default_value": 0,
            "ZH_CN": {
                "name": "选择奖池   ",
                "description": "选择奖池"
            },
            "EN_US": {
                "name": "Select Pool",
                "description": "Select pool"
            }
        },
        "import_prize_name": {
            "default_value": None,
            "ZH_CN": {
                "name": "导入奖品名单",
                "description": "导入奖品名单"
            },
            "EN_US": {
                "name": "Import Prize List",
                "description": "Import prize list"  
            }
        },
        "prize_setting": {
            "default_value": None,
            "ZH_CN": {
                "name": "设置奖品",
                "description": "设置奖品"
            },
            "EN_US": {
                "name": "Set Prize",
                "description": "Set prize"
            }
        },
        "prize_weight_setting": {
            "default_value": None,
            "ZH_CN": {
                "name": "设置权重",
                "description": "设置权重"
            },
            "EN_US": {
                "name": "Set Weight",
                "description": "Set weight"
            }
        },
        "export_prize_name": {
            "default_value": None,
            "ZH_CN": {
                "name": "导出奖品名单",
                "description": "导出奖品名单"
            },
            "EN_US": {
                "name": "Export Prize List",
                "description": "Export prize list"
            }
        },
    },
    "lottery_table": {
        "title": {
            "default_value": None,
            "ZH_CN": {
                "name": "抽奖表格",
                "description": "用于展示和管理抽奖名单的表格"
            },
            "EN_US": {
                "name": "Lottery Table",
                "description": "Table for displaying and managing lottery lists"
            }
        },
        "HeaderLabels": {
            "default_value": None,
            "ZH_CN": {
                "name": ["存在", "序号", "奖品", "权重"],
                "description": "抽奖表格的列标题"
            },
            "EN_US": {
                "name": ["Exist", "No.", "Prize", "Weight"],
                "description": "Column headers for the lottery table"
            }
        },
    },
    "extraction_settings": {
        "title": {
            "default_value": None,
            "ZH_CN": {
                "name": "抽取设置",
                "description": "抽取设置"
            },
            "EN_US": {
                "name": "Draw Set",
                "description": "Roll call settings"
            }
        },
    },
    "roll_call_settings": {
        "title": {
            "default_value": None,
            "ZH_CN": {
                "name": "点名设置",
                "description": "点名设置"
            },
            "EN_US": {
                "name": "Roll Call Settings",
                "description": "Roll call settings"
            }
        },
        "extraction_function": {
            "default_value": None,
            "ZH_CN": {
                "name": "抽取功能",
                "description": "点名抽取功能相关设置"
            },
            "EN_US": {
                "name": "Extraction Function",
                "description": "Settings related to roll call extraction function"
            }
        },
        "display_settings": {
            "default_value": None,
            "ZH_CN": {
                "name": "显示设置",
                "description": "点名结果显示相关设置"
            },
            "EN_US": {
                "name": "Display Settings",
                "description": "Settings related to roll call result display"
            }
        },
        "basic_animation_settings": {
            "default_value": None,
            "ZH_CN": {
                "name": "动画设置",
                "description": "点名动画效果相关设置"
            },
            "EN_US": {
                "name": "Animation Settings",
                "description": "Settings related to roll call animation effects"
            }
        },
        "color_theme_settings": {
            "default_value": None,
            "ZH_CN": {
                "name": "颜色主题设置",
                "description": "点名结果显示的颜色主题相关设置"
            },
            "EN_US": {
                "name": "Color Theme Settings",
                "description": "Settings related to roll call result display color theme"
            }
        },
        "student_image_settings": {
            "default_value": None,
            "ZH_CN": {
                "name": "学生头像设置",
                "description": "点名结果显示的学生头像相关设置"
            },
            "EN_US": {
                "name": "Student Image Settings",
                "description": "Settings related to roll call result display student images"
            }
        },
        "music_settings": {
            "default_value": None,
            "ZH_CN": {
                "name": "音乐设置",
                "description": "点名音乐相关设置"
            },
            "EN_US": {
                "name": "Music Settings",
                "description": "Settings related to roll call music"
            }
        },
        "draw_mode": {
            "default_value": 1,
            "ZH_CN": {
                "name": "抽取模式",
                "description": "设置点名抽取的模式",
                "combo_items": ["重复抽取", "不重复抽取", "半重复抽取"]
            },
            "EN_US": {
                "name": "Draw Mode",
                "description": "Set the mode of roll call extraction",
                "combo_items": ["Repeat Draw", "No Repeat Draw", "Half Repeat Draw"]
            }
        },
        "clear_record": {
            "default_value": 0,
            "ZH_CN": {
                "name": "清除抽取记录方式",
                "description": "设置清除点名抽取记录的方式",
                "combo_items": ["重启后清除", "直到全部抽取完"],
                "combo_items_other": ["重启后清除", "直到全部抽取完", "无需清除"]
            },
            "EN_US": {
                "name": "Clear Record Method",
                "description": "Set the method to clear roll call extraction records",
                "combo_items": ["Restart Clear", "Until All Extracted"],
                "combo_items_other": ["Restart Clear", "Until All Extracted", "No Clear"]
            }
        },
        "half_repeat": {
            "default_value": 1,
            "ZH_CN": {
                "name": "半重复抽取次数",
                "description": "设置半重复抽取的次数"
            },
            "EN_US": {
                "name": "Half Repeat Count",
                "description": "Set the count of half repeat extraction"
            }
        },
        "clear_time": {
            "default_value": 0,
            "ZH_CN": {
                "name": "抽取后定时清除时间",
                "description": "设置抽取后定时清除记录的时间（秒）"
            },
            "EN_US": {
                "name": "Auto Clear Time",
                "description": "Set the time to automatically clear records after extraction (seconds)"
            }
        },
        "draw_type": {
            "default_value": 0,
            "ZH_CN": {
                "name": "抽取方式",
                "description": "设置点名抽取的方式",
                "combo_items": ["随机抽取", "公平抽取"]
            },
            "EN_US": {
                "name": "Draw Type",
                "description": "Set the type of roll call extraction",
                "combo_items": ["Random Draw", "Fair Draw"]
            }
        },
        "font_size": {
            "default_value": 50,
            "ZH_CN": {
                "name": "字体大小",
                "description": "设置点名结果显示的字体大小"
            },
            "EN_US": {
                "name": "Font Size",
                "description": "Set the font size of roll call result display"
            }
        },
        "display_format": {
            "default_value": 0,
            "ZH_CN": {
                "name": "结果显示格式",
                "description": "设置点名结果的显示格式",
                "combo_items": ["学号+姓名", "姓名", "学号"]
            },
            "EN_US": {
                "name": "Display Format",
                "description": "Set the display format of roll call results",
                "combo_items": ["Number+Name", "Name", "Number"]
            }
        },
        "show_random": {
            "default_value": 0,
            "ZH_CN": {
                "name": "显示随机组员格式",
                "description": "设置随机组员的显示格式",
                "combo_items": ["不显示", "组名[换行]姓名", "组名[短横杠]姓名"]
            },
            "EN_US": {
                "name": "Random Member Format",
                "description": "Set the display format of random members",
                "combo_items": ["Not Show", "Group Name[Line Break]Name", "Group Name[Dash]Name"]
            }
        },
        "animation": {
            "default_value": 1,
            "ZH_CN": {
                "name": "动画模式",
                "description": "设置点名抽取的动画效果",
                "combo_items": ["手动停止动画", "自动播放动画", "直接显示结果"]
            },
            "EN_US": {
                "name": "Animation Mode",
                "description": "Set the animation effect of roll call extraction",
                "combo_items": ["Manual Stop", "Autoplay", "Show Result"]
            }
        },
        "animation_interval": {
            "default_value": 80,
            "ZH_CN": {
                "name": "动画间隔",
                "description": "设置点名动画的间隔时间（毫秒）"
            },
            "EN_US": {
                "name": "Animation Interval",
                "description": "Set the interval time of roll call animation (milliseconds)"
            }
        },
        "autoplay_count": {
            "default_value": 5,
            "ZH_CN": {
                "name": "自动播放次数",
                "description": "设置点名动画自动播放的次数"
            },
            "EN_US": {
                "name": "Autoplay Count",
                "description": "Set the autoplay count of roll call animation"
            }
        },
        "animation_color_theme": {
            "default_value": 0,
            "ZH_CN": {
                "name": "动画颜色主题",
                "description": "设置点名动画的颜色主题",
                "combo_items": ["关闭", "随机颜色", "固定颜色"]
            },
            "EN_US": {
                "name": "Animation Color Theme",
                "description": "Set the color theme of roll call animation",
                "combo_items": ["Close", "Random Color", "Fixed Color"]
            }
        },
        "result_color_theme": {
            "default_value": 0,
            "ZH_CN": {
                "name": "结果颜色主题",
                "description": "设置点名结果显示的颜色主题",
                "combo_items": ["关闭", "随机颜色", "固定颜色"]
            },
            "EN_US": {
                "name": "Result Color Theme",
                "description": "Set the color theme of roll call result display",
                "combo_items": ["Close", "Random Color", "Fixed Color"]
            }
        },
        "animation_fixed_color": {
            "default_value": DEFAULT_THEME_COLOR,
            "ZH_CN": {
                "name": "动画固定颜色",
                "description": "设置点名动画的固定颜色"
            },
            "EN_US": {
                "name": "Animation Fixed Color",
                "description": "Set the fixed color of roll call animation"
            }
        },
        "result_fixed_color": {
            "default_value": DEFAULT_THEME_COLOR,
            "ZH_CN": {
                "name": "结果固定颜色",
                "description": "设置点名结果显示的固定颜色"
            },
            "EN_US": {
                "name": "Result Fixed Color",
                "description": "Set the fixed color of roll call result display"
            }
        },
        "student_image": {
            "default_value": False,
            "ZH_CN": {
                "name": "显示学生图片",
                "description": "设置是否显示学生图片",
                "switchbutton_name": {
                    "enable": "显示",
                    "disable": "隐藏"
                }
            },
            "EN_US": {
                "name": "Show Student Image",
                "description": "Set whether to show student images",
                "switchbutton_name": {
                    "enable": "Show",
                    "disable": "Hide"
                }
            }
        },
        "open_student_image_folder": {
            "default_value": None,
            "ZH_CN": {
                "name": "学生图片文件夹",
                "description": "管理学生图片文件，图片文件名需与学生姓名一致",
            },
            "EN_US": {
                "name": "Student Image Folder",
                "description": "Manage student image files, image file names must match student names"
            }
        },
        "animation_music": {
            "default_value": False,
            "ZH_CN": {
                "name": "动画音乐",
                "description": "设置是否播放动画音乐",
                "switchbutton_name": {
                    "enable": "播放",
                    "disable": "关闭"
                }
            },
            "EN_US": {
                "name": "Animation Music",
                "description": "Set whether to play animation music",
                "switchbutton_name": {
                    "enable": "Play",
                    "disable": "Stop"
                }
            }
        },
        "result_music": {
            "default_value": False,
            "ZH_CN": {
                "name": "结果音乐",
                "description": "设置是否播放结果音乐",
                "switchbutton_name": {
                    "enable": "播放",
                    "disable": "关闭"
                }
            },
            "EN_US": {
                "name": "Result Music",
                "description": "Set whether to play result music",
                "switchbutton_name": {
                    "enable": "Play",
                    "disable": "Stop"
                }
            }
        },
        "open_animation_music_folder": {
            "default_value": None,
            "ZH_CN": {
                "name": "打开动画音乐文件夹",
                "description": "管理动画音乐文件并支持随机播放功能"
            },
            "EN_US": {
                "name": "Open Animation Music Folder",
                "description": "Manage animation music files and support random play functionality"
            }
        },
        "open_result_music_folder": {
            "default_value": None,
            "ZH_CN": {
                "name": "打开结果音乐文件夹",
                "description": "管理结果音乐文件并支持随机播放功能"
            },
            "EN_US": {
                "name": "Open Result Music Folder",
                "description": "Manage result music files and support random play functionality"
            }
        },
        "animation_music_volume": {
            "default_value": 30,
            "ZH_CN": {
                "name": "动画音乐音量",
                "description": "设置动画音乐的音量"
            },
            "EN_US": {
                "name": "Animation Music Volume",
                "description": "Set the volume of animation music"
            }
        },
        "result_music_volume": {
            "default_value": 30,
            "ZH_CN": {
                "name": "结果音乐音量",
                "description": "设置结果音乐的音量"
            },
            "EN_US": {
                "name": "Result Music Volume",
                "description": "Set the volume of result music"
            }
        },
        "animation_music_fade_in": {
            "default_value": 300,
            "ZH_CN": {
                "name": "动画音乐淡入时间",
                "description": "设置动画音乐淡入的时间"
            },
            "EN_US": {
                "name": "Animation Music Fade In Time",
                "description": "Set the fade in time of animation music"
            }
        },
        "result_music_fade_in": {
            "default_value": 300,
            "ZH_CN": {
                "name": "结果音乐淡入时间",
                "description": "设置结果音乐淡入的时间"
            },
            "EN_US": {
                "name": "Result Music Fade In Time",
                "description": "Set the fade in time of result music"
            }
        },
        "animation_music_fade_out": {
            "default_value": 300,
            "ZH_CN": {
                "name": "动画音乐淡出时间",
                "description": "设置动画音乐淡出的时间"
            },
            "EN_US": {
                "name": "Animation Music Fade Out Time",
                "description": "Set the fade out time of animation music"
            }
        },
        "result_music_fade_out": {
            "default_value": 300,
            "ZH_CN": {
                "name": "结果音乐淡出时间",
                "description": "设置结果音乐淡出的时间"
            },
            "EN_US": {
                "name": "Result Music Fade Out Time",
                "description": "Set the fade out time of result music"
            }
        },
    },
    "quick_draw_settings": {
        "title": {
            "default_value": None,
            "ZH_CN": {
                "name": "闪抽设置",
                "description": "闪抽设置"
            },
            "EN_US": {
                "name": "Quick Draw Settings",
                "description": "Quick draw settings"
            }
        },
        "extraction_function": {
            "default_value": None,
            "ZH_CN": {
                "name": "抽取功能",
                "description": "闪抽抽取功能相关设置"
            },
            "EN_US": {
                "name": "Extraction Function",
                "description": "Settings related to quick draw extraction function"
            }
        },
        "display_settings": {
            "default_value": None,
            "ZH_CN": {
                "name": "显示设置",
                "description": "闪抽结果显示相关设置"
            },
            "EN_US": {
                "name": "Display Settings",
                "description": "Settings related to quick draw result display"
            }
        },
        "basic_animation_settings": {
            "default_value": None,
            "ZH_CN": {
                "name": "动画设置",
                "description": "闪抽动画效果相关设置"
            },
            "EN_US": {
                "name": "Animation Settings",
                "description": "Settings related to quick draw animation effects"
            }
        },
        "color_theme_settings": {
            "default_value": None,
            "ZH_CN": {
                "name": "颜色主题设置",
                "description": "闪抽结果显示的颜色主题相关设置"
            },
            "EN_US": {
                "name": "Color Theme Settings",
                "description": "Settings related to quick draw result display color theme"
            }
        },
        "student_image_settings": {
            "default_value": None,
            "ZH_CN": {
                "name": "学生头像设置",
                "description": "闪抽结果显示的学生头像相关设置"
            },
            "EN_US": {
                "name": "Student Image Settings",
                "description": "Settings related to quick draw result display student images"
            }
        },
        "music_settings": {
            "default_value": None,
            "ZH_CN": {
                "name": "音乐设置",
                "description": "闪抽音乐相关设置"
            },
            "EN_US": {
                "name": "Music Settings",
                "description": "Settings related to quick draw music"
            }
        },
        "draw_mode": {
            "default_value": 1,
            "ZH_CN": {
                "name": "抽取模式",
                "description": "设置闪抽抽取的模式",
                "combo_items": ["重复抽取", "不重复抽取", "半重复抽取"]
            },
            "EN_US": {
                "name": "Draw Mode",
                "description": "Set the mode of quick draw extraction",
                "combo_items": ["Repeat Draw", "No Repeat Draw", "Half Repeat Draw"]
            }
        },
        "clear_record": {
            "default_value": 0,
            "ZH_CN": {
                "name": "清除抽取记录方式",
                "description": "设置清除闪抽抽取记录的方式",
                "combo_items": ["重启后清除", "直到全部抽取完"],
                "combo_items_other": ["重启后清除", "直到全部抽取完", "无需清除"]
            },
            "EN_US": {
                "name": "Clear Record Method",
                "description": "Set the method to clear quick draw extraction records",
                "combo_items": ["Restart Clear", "Until All Extracted"],
                "combo_items_other": ["Restart Clear", "Until All Extracted", "No Clear"]
            }
        },
        "half_repeat": {
            "default_value": 1,
            "ZH_CN": {
                "name": "半重复抽取次数",
                "description": "设置半重复抽取的次数"
            },
            "EN_US": {
                "name": "Half Repeat Count",
                "description": "Set the count of half repeat extraction"
            }
        },
        "clear_time": {
            "default_value": 0,
            "ZH_CN": {
                "name": "抽取后定时清除时间",
                "description": "设置抽取后定时清除记录的时间（秒）"
            },
            "EN_US": {
                "name": "Auto Clear Time",
                "description": "Set the time to automatically clear records after extraction (seconds)"
            }
        },
        "draw_type": {
            "default_value": 0,
            "ZH_CN": {
                "name": "抽取方式",
                "description": "设置闪抽抽取的方式",
                "combo_items": ["随机抽取", "公平抽取"]
            },
            "EN_US": {
                "name": "Draw Type",
                "description": "Set the type of quick draw extraction",
                "combo_items": ["Random Draw", "Fair Draw"]
            }
        },
        "font_size": {
            "default_value": 50,
            "ZH_CN": {
                "name": "字体大小",
                "description": "设置闪抽结果显示的字体大小"
            },
            "EN_US": {
                "name": "Font Size",
                "description": "Set the font size of quick draw result display"
            }
        },
        "display_format": {
            "default_value": 0,
            "ZH_CN": {
                "name": "结果显示格式",
                "description": "设置闪抽结果的显示格式",
                "combo_items": ["学号+姓名", "姓名", "学号"]
            },
            "EN_US": {
                "name": "Display Format",
                "description": "Set the display format of quick draw results",
                "combo_items": ["Number+Name", "Name", "Number"]
            }
        },
        "show_random": {
            "default_value": 0,
            "ZH_CN": {
                "name": "显示随机组员格式",
                "description": "设置随机组员的显示格式",
                "combo_items": ["不显示", "组名[换行]姓名", "组名[短横杠]姓名"]
            },
            "EN_US": {
                "name": "Random Member Format",
                "description": "Set the display format of random members",
                "combo_items": ["Not Show", "Group Name[Line Break]Name", "Group Name[Dash]Name"]
            }
        },
        "animation": {
            "default_value": 1,
            "ZH_CN": {
                "name": "动画模式",
                "description": "设置闪抽抽取的动画效果",
                "combo_items": ["手动停止动画", "自动播放动画", "直接显示结果"]
            },
            "EN_US": {
                "name": "Animation Mode",
                "description": "Set the animation effect of quick draw extraction",
                "combo_items": ["Manual Stop", "Autoplay", "Show Result"]
            }
        },
        "animation_interval": {
            "default_value": 80,
            "ZH_CN": {
                "name": "动画间隔",
                "description": "设置闪抽动画的间隔时间（毫秒）"
            },
            "EN_US": {
                "name": "Animation Interval",
                "description": "Set the interval time of quick draw animation (milliseconds)"
            }
        },
        "autoplay_count": {
            "default_value": 5,
            "ZH_CN": {
                "name": "自动播放次数",
                "description": "设置闪抽动画自动播放的次数"
            },
            "EN_US": {
                "name": "Autoplay Count",
                "description": "Set the autoplay count of quick draw animation"
            }
        },
        "animation_color_theme": {
            "default_value": 0,
            "ZH_CN": {
                "name": "动画颜色主题",
                "description": "设置闪抽动画的颜色主题",
                "combo_items": ["关闭", "随机颜色", "固定颜色"]
            },
            "EN_US": {
                "name": "Animation Color Theme",
                "description": "Set the color theme of quick draw animation",
                "combo_items": ["Close", "Random Color", "Fixed Color"]
            }
        },
        "result_color_theme": {
            "default_value": 0,
            "ZH_CN": {
                "name": "结果颜色主题",
                "description": "设置闪抽结果显示的颜色主题",
                "combo_items": ["关闭", "随机颜色", "固定颜色"]
            },
            "EN_US": {
                "name": "Result Color Theme",
                "description": "Set the color theme of quick draw result display",
                "combo_items": ["Close", "Random Color", "Fixed Color"]
            }
        },
        "animation_fixed_color": {
            "default_value": DEFAULT_THEME_COLOR,
            "ZH_CN": {
                "name": "动画固定颜色",
                "description": "设置闪抽动画的固定颜色"
            },
            "EN_US": {
                "name": "Animation Fixed Color",
                "description": "Set the fixed color of quick draw animation"
            }
        },
        "result_fixed_color": {
            "default_value": DEFAULT_THEME_COLOR,
            "ZH_CN": {
                "name": "结果固定颜色",
                "description": "设置闪抽结果显示的固定颜色"
            },
            "EN_US": {
                "name": "Result Fixed Color",
                "description": "Set the fixed color of quick draw result display"
            }
        },
        "student_image": {
            "default_value": False,
            "ZH_CN": {
                "name": "显示学生图片",
                "description": "设置是否显示学生图片",
                "switchbutton_name": {
                    "enable": "显示",
                    "disable": "隐藏"
                }
            },
            "EN_US": {
                "name": "Show Student Image",
                "description": "Set whether to show student images",
                "switchbutton_name": {
                    "enable": "Show",
                    "disable": "Hide"
                }
            }
        },
        "open_student_image_folder": {
            "default_value": None,
            "ZH_CN": {
                "name": "学生图片文件夹",
                "description": "管理学生图片文件，图片文件名需与学生姓名一致",
            },
            "EN_US": {
                "name": "Student Image Folder",
                "description": "Manage student image files, image file names must match student names"
            }
        },
        "animation_music": {
            "default_value": False,
            "ZH_CN": {
                "name": "动画音乐",
                "description": "设置是否播放动画音乐",
                "switchbutton_name": {
                    "enable": "播放",
                    "disable": "关闭"
                }
            },
            "EN_US": {
                "name": "Animation Music",
                "description": "Set whether to play animation music",
                "switchbutton_name": {
                    "enable": "Play",
                    "disable": "Stop"
                }
            }
        },
        "result_music": {
            "default_value": False,
            "ZH_CN": {
                "name": "结果音乐",
                "description": "设置是否播放结果音乐",
                "switchbutton_name": {
                    "enable": "播放",
                    "disable": "关闭"
                }
            },
            "EN_US": {
                "name": "Result Music",
                "description": "Set whether to play result music",
                "switchbutton_name": {
                    "enable": "Play",
                    "disable": "Stop"
                }
            }
        },
        "open_animation_music_folder": {
            "default_value": None,
            "ZH_CN": {
                "name": "打开动画音乐文件夹",
                "description": "管理动画音乐文件并支持随机播放功能"
            },
            "EN_US": {
                "name": "Open Animation Music Folder",
                "description": "Manage animation music files and support random play functionality"
            }
        },
        "open_result_music_folder": {
            "default_value": None,
            "ZH_CN": {
                "name": "打开结果音乐文件夹",
                "description": "管理结果音乐文件并支持随机播放功能"
            },
            "EN_US": {
                "name": "Open Result Music Folder",
                "description": "Manage result music files and support random play functionality"
            }
        },
        "animation_music_volume": {
            "default_value": 30,
            "ZH_CN": {
                "name": "动画音乐音量",
                "description": "设置动画音乐的音量"
            },
            "EN_US": {
                "name": "Animation Music Volume",
                "description": "Set the volume of animation music"
            }
        },
        "result_music_volume": {
            "default_value": 30,
            "ZH_CN": {
                "name": "结果音乐音量",
                "description": "设置结果音乐的音量"
            },
            "EN_US": {
                "name": "Result Music Volume",
                "description": "Set the volume of result music"
            }
        },
        "animation_music_fade_in": {
            "default_value": 300,
            "ZH_CN": {
                "name": "动画音乐淡入时间",
                "description": "设置动画音乐淡入的时间"
            },
            "EN_US": {
                "name": "Animation Music Fade In Time",
                "description": "Set the fade in time of animation music"
            }
        },
        "result_music_fade_in": {
            "default_value": 300,
            "ZH_CN": {
                "name": "结果音乐淡入时间",
                "description": "设置结果音乐淡入的时间"
            },
            "EN_US": {
                "name": "Result Music Fade In Time",
                "description": "Set the fade in time of result music"
            }
        },
        "animation_music_fade_out": {
            "default_value": 300,
            "ZH_CN": {
                "name": "动画音乐淡出时间",
                "description": "设置动画音乐淡出的时间"
            },
            "EN_US": {
                "name": "Animation Music Fade Out Time",
                "description": "Set the fade out time of animation music"
            }
        },
        "result_music_fade_out": {
            "default_value": 300,
            "ZH_CN": {
                "name": "结果音乐淡出时间",
                "description": "设置结果音乐淡出的时间"
            },
            "EN_US": {
                "name": "Result Music Fade Out Time",
                "description": "Set the fade out time of result music"
            }
        },
    },
    "instant_draw_settings": {
        "title": {
            "default_value": None,
            "ZH_CN": {
                "name": "即抽设置",
                "description": "即时抽取功能的相关设置"
            },
            "EN_US": {
                "name": "Instant Draw Settings",
                "description": "Settings related to the instant draw function"
            }
        },
        "extraction_function": {
            "default_value": None,
            "ZH_CN": {
                "name": "抽取功能",
                "description": "即抽抽取功能相关设置"
            },
            "EN_US": {
                "name": "Extraction Function",
                "description": "Settings related to instant draw extraction function"
            }
        },
        "display_settings": {
            "default_value": None,
            "ZH_CN": {
                "name": "显示设置",
                "description": "即抽结果显示相关设置"
            },
            "EN_US": {
                "name": "Display Settings",
                "description": "Settings related to instant draw result display"
            }
        },
        "basic_animation_settings": {
            "default_value": None,
            "ZH_CN": {
                "name": "动画设置",
                "description": "即抽动画效果相关设置"
            },
            "EN_US": {
                "name": "Animation Settings",
                "description": "Settings related to instant draw animation effects"
            }
        },
        "color_theme_settings": {
            "default_value": None,
            "ZH_CN": {
                "name": "颜色主题设置",
                "description": "即抽结果显示的颜色主题相关设置"
            },
            "EN_US": {
                "name": "Color Theme Settings",
                "description": "Settings related to instant draw result display color theme"
            }
        },
        "student_image_settings": {
            "default_value": None,
            "ZH_CN": {
                "name": "学生头像设置",
                "description": "即抽结果显示的学生头像相关设置"
            },
            "EN_US": {
                "name": "Student Image Settings",
                "description": "Settings related to instant draw result display student images"
            }
        },
        "music_settings": {
            "default_value": None,
            "ZH_CN": {
                "name": "音乐设置",
                "description": "即抽音乐相关设置"
            },
            "EN_US": {
                "name": "Music Settings",
                "description": "Settings related to instant draw music"
            }
        },
        "draw_mode": {
            "default_value": 1,
            "ZH_CN": {
                "name": "抽取模式",
                "description": "设置即抽抽取的模式",
                "combo_items": ["重复抽取", "不重复抽取", "半重复抽取"]
            },
            "EN_US": {
                "name": "Draw Mode",
                "description": "Set the mode of quick draw extraction",
                "combo_items": ["Repeat Draw", "No Repeat Draw", "Half Repeat Draw"]
            }
        },
        "clear_record": {
            "default_value": 0,
            "ZH_CN": {
                "name": "清除抽取记录方式",
                "description": "设置清除即抽抽取记录的方式",
                "combo_items": ["重启后清除", "直到全部抽取完"],
                "combo_items_other": ["重启后清除", "直到全部抽取完", "无需清除"]
            },
            "EN_US": {
                "name": "Clear Record Method",
                "description": "Set the method to clear instant draw extraction records",
                "combo_items": ["Restart Clear", "Until All Extracted"],
                "combo_items_other": ["Restart Clear", "Until All Extracted", "No Clear"]
            }
        },
        "half_repeat": {
            "default_value": 1,
            "ZH_CN": {
                "name": "半重复抽取次数",
                "description": "设置半重复抽取的次数"
            },
            "EN_US": {
                "name": "Half Repeat Count",
                "description": "Set the count of half repeat extraction"
            }
        },
        "clear_time": {
            "default_value": 0,
            "ZH_CN": {
                "name": "抽取后定时清除时间",
                "description": "设置抽取后定时清除记录的时间（秒）"
            },
            "EN_US": {
                "name": "Auto Clear Time",
                "description": "Set the time to automatically clear records after extraction (seconds)"
            }
        },
        "draw_type": {
            "default_value": 0,
            "ZH_CN": {
                "name": "抽取方式",
                "description": "设置即抽抽取的方式",
                "combo_items": ["随机抽取", "公平抽取"]
            },
            "EN_US": {
                "name": "Draw Type",
                "description": "Set the type of instant draw extraction",
                "combo_items": ["Random Draw", "Fair Draw"]
            }
        },
        "font_size": {
            "default_value": 50,
            "ZH_CN": {
                "name": "字体大小",
                "description": "设置即抽结果显示的字体大小"
            },
            "EN_US": {
                "name": "Font Size",
                "description": "Set the font size of instant draw result display"
            }
        },
        "display_format": {
            "default_value": 0,
            "ZH_CN": {
                "name": "结果显示格式",
                "description": "设置即抽结果的显示格式",
                "combo_items": ["学号+姓名", "姓名", "学号"]
            },
            "EN_US": {
                "name": "Display Format",
                "description": "Set the display format of instant draw results",
                "combo_items": ["Number+Name", "Name", "Number"]
            }
        },
        "show_random": {
            "default_value": 0,
            "ZH_CN": {
                "name": "显示随机组员格式",
                "description": "设置随机组员的显示格式",
                "combo_items": ["不显示", "组名[换行]姓名", "组名[短横杠]姓名"]
            },
            "EN_US": {
                "name": "Random Member Format",
                "description": "Set the display format of random members",
                "combo_items": ["Not Show", "Group Name[Line Break]Name", "Group Name[Dash]Name"]
            }
        },
        "animation": {
            "default_value": 1,
            "ZH_CN": {
                "name": "动画模式",
                "description": "设置即抽抽取的动画效果",
                "combo_items": ["手动停止动画", "自动播放动画", "直接显示结果"]
            },
            "EN_US": {
                "name": "Animation Mode",
                "description": "Set the animation effect of instant draw extraction",
                "combo_items": ["Manual Stop", "Autoplay", "Show Result"]
            }
        },
        "animation_interval": {
            "default_value": 80,
            "ZH_CN": {
                "name": "动画间隔",
                "description": "设置即抽动画的间隔时间（毫秒）"
            },
            "EN_US": {
                "name": "Animation Interval",
                "description": "Set the interval time of instant draw animation (milliseconds)"
            }
        },
        "autoplay_count": {
            "default_value": 5,
            "ZH_CN": {
                "name": "自动播放次数",
                "description": "设置即抽动画自动播放的次数"
            },
            "EN_US": {
                "name": "Autoplay Count",
                "description": "Set the autoplay count of instant draw animation"
            }
        },
        "animation_color_theme": {
            "default_value": 0,
            "ZH_CN": {
                "name": "动画颜色主题",
                "description": "设置即抽动画的颜色主题",
                "combo_items": ["关闭", "随机颜色", "固定颜色"]
            },
            "EN_US": {
                "name": "Animation Color Theme",
                "description": "Set the color theme of instant draw animation",
                "combo_items": ["Close", "Random Color", "Fixed Color"]
            }
        },
        "result_color_theme": {
            "default_value": 0,
            "ZH_CN": {
                "name": "结果颜色主题",
                "description": "设置即抽结果显示的颜色主题",
                "combo_items": ["关闭", "随机颜色", "固定颜色"]
            },
            "EN_US": {
                "name": "Result Color Theme",
                "description": "Set the color theme of instant draw result display",
                "combo_items": ["Close", "Random Color", "Fixed Color"]
            }
        },
        "animation_fixed_color": {
            "default_value": DEFAULT_THEME_COLOR,
            "ZH_CN": {
                "name": "动画固定颜色",
                "description": "设置即抽动画的固定颜色"
            },
            "EN_US": {
                "name": "Animation Fixed Color",
                "description": "Set the fixed color of instant draw animation"
            }
        },
        "result_fixed_color": {
            "default_value": DEFAULT_THEME_COLOR,
            "ZH_CN": {
                "name": "结果固定颜色",
                "description": "设置即抽结果显示的固定颜色"
            },
            "EN_US": {
                "name": "Result Fixed Color",
                "description": "Set the fixed color of instant draw result display"
            }
        },
        "student_image": {
            "default_value": False,
            "ZH_CN": {
                "name": "显示学生图片",
                "description": "设置是否显示学生图片",
                "switchbutton_name": {
                    "enable": "显示",
                    "disable": "隐藏"
                }
            },
            "EN_US": {
                "name": "Show Student Image",
                "description": "Set whether to show student images",
                "switchbutton_name": {
                    "enable": "Show",
                    "disable": "Hide"
                }
            }
        },
        "open_student_image_folder": {
            "default_value": None,
            "ZH_CN": {
                "name": "学生图片文件夹",
                "description": "管理学生图片文件，图片文件名需与学生姓名一致",
            },
            "EN_US": {
                "name": "Student Image Folder",
                "description": "Manage student image files, image file names must match student names"
            }
        },
        "animation_music": {
            "default_value": False,
            "ZH_CN": {
                "name": "动画音乐",
                "description": "设置是否播放动画音乐",
                "switchbutton_name": {
                    "enable": "播放",
                    "disable": "关闭"
                }
            },
            "EN_US": {
                "name": "Animation Music",
                "description": "Set whether to play animation music",
                "switchbutton_name": {
                    "enable": "Play",
                    "disable": "Stop"
                }
            }
        },
        "result_music": {
            "default_value": False,
            "ZH_CN": {
                "name": "结果音乐",
                "description": "设置是否播放结果音乐",
                "switchbutton_name": {
                    "enable": "播放",
                    "disable": "关闭"
                }
            },
            "EN_US": {
                "name": "Result Music",
                "description": "Set whether to play result music",
                "switchbutton_name": {
                    "enable": "Play",
                    "disable": "Stop"
                }
            }
        },
        "open_animation_music_folder": {
            "default_value": None,
            "ZH_CN": {
                "name": "打开动画音乐文件夹",
                "description": "管理动画音乐文件并支持随机播放功能"
            },
            "EN_US": {
                "name": "Open Animation Music Folder",
                "description": "Manage animation music files and support random play functionality"
            }
        },
        "open_result_music_folder": {
            "default_value": None,
            "ZH_CN": {
                "name": "打开结果音乐文件夹",
                "description": "管理结果音乐文件并支持随机播放功能"
            },
            "EN_US": {
                "name": "Open Result Music Folder",
                "description": "Manage result music files and support random play functionality"
            }
        },
        "animation_music_volume": {
            "default_value": 30,
            "ZH_CN": {
                "name": "动画音乐音量",
                "description": "设置动画音乐的音量"
            },
            "EN_US": {
                "name": "Animation Music Volume",
                "description": "Set the volume of animation music"
            }
        },
        "result_music_volume": {
            "default_value": 30,
            "ZH_CN": {
                "name": "结果音乐音量",
                "description": "设置结果音乐的音量"
            },
            "EN_US": {
                "name": "Result Music Volume",
                "description": "Set the volume of result music"
            }
        },
        "animation_music_fade_in": {
            "default_value": 300,
            "ZH_CN": {
                "name": "动画音乐淡入时间",
                "description": "设置动画音乐淡入的时间"
            },
            "EN_US": {
                "name": "Animation Music Fade In Time",
                "description": "Set the fade in time of animation music"
            }
        },
        "result_music_fade_in": {
            "default_value": 300,
            "ZH_CN": {
                "name": "结果音乐淡入时间",
                "description": "设置结果音乐淡入的时间"
            },
            "EN_US": {
                "name": "Result Music Fade In Time",
                "description": "Set the fade in time of result music"
            }
        },
        "animation_music_fade_out": {
            "default_value": 300,
            "ZH_CN": {
                "name": "动画音乐淡出时间",
                "description": "设置动画音乐淡出的时间"
            },
            "EN_US": {
                "name": "Animation Music Fade Out Time",
                "description": "Set the fade out time of animation music"
            }
        },
        "result_music_fade_out": {
            "default_value": 300,
            "ZH_CN": {
                "name": "结果音乐淡出时间",
                "description": "设置结果音乐淡出的时间"
            },
            "EN_US": {
                "name": "Result Music Fade Out Time",
                "description": "Set the fade out time of result music"
            }
        },
    },
    "custom_draw_settings": {
        "title": {
            "default_value": None,
            "ZH_CN": {
                "name": "自定义抽设置",
                "description": "自定义抽设置"
            },
            "EN_US": {
                "name": "Custom Draw Settings",
                "description": "Custom draw settings"
            }
        },
    },
    "lottery_settings": {
        "title": {
            "default_value": None,
            "ZH_CN": {
                "name": "抽奖设置",
                "description": "抽奖设置"
            },
            "EN_US": {
                "name": "Lottery Settings",
                "description": "Lottery settings"
            }
        },
        "extraction_function": {
            "default_value": None,
            "ZH_CN": {
                "name": "抽取功能",
                "description": "抽奖抽取功能相关设置"
            },
            "EN_US": {
                "name": "Extraction Function",
                "description": "Settings related to lottery extraction function"
            }
        },
        "display_settings": {
            "default_value": None,
            "ZH_CN": {
                "name": "显示设置",
                "description": "抽奖结果显示相关设置"
            },
            "EN_US": {
                "name": "Display Settings",
                "description": "Settings related to lottery result display"
            }
        },
        "basic_animation_settings": {
            "default_value": None,
            "ZH_CN": {
                "name": "动画设置",
                "description": "抽奖动画效果相关设置"
            },
            "EN_US": {
                "name": "Animation Settings",
                "description": "Settings related to lottery animation effects"
            }
        },
        "color_theme_settings": {
            "default_value": None,
            "ZH_CN": {
                "name": "颜色主题设置",
                "description": "抽奖结果显示的颜色主题相关设置"
            },
            "EN_US": {
                "name": "Color Theme Settings",
                "description": "Settings related to lottery result display color theme"
            }
        },
        "student_image_settings": {
            "default_value": None,
            "ZH_CN": {
                "name": "奖品图片设置",
                "description": "抽奖结果显示的奖品图片相关设置"
            },
            "EN_US": {
                "name": "Prize Image Settings",
                "description": "Settings related to lottery result display prize images"
            }
        },
        "music_settings": {
            "default_value": None,
            "ZH_CN": {
                "name": "音乐设置",
                "description": "抽奖音乐相关设置"
            },
            "EN_US": {
                "name": "Music Settings",
                "description": "Settings related to lottery music"
            }
        },
        "draw_mode": {
            "default_value": 1,
            "ZH_CN": {
                "name": "抽取模式",
                "description": "设置抽奖抽取的模式",
                "combo_items": ["重复抽取", "不重复抽取", "半重复抽取"]
            },
            "EN_US": {
                "name": "Draw Mode",
                "description": "Set the mode of lottery extraction",
                "combo_items": ["Repeat Draw", "No Repeat Draw", "Half Repeat Draw"]
            }
        },
        "clear_record": {
            "default_value": 0,
            "ZH_CN": {
                "name": "清除抽取记录方式",
                "description": "设置清除抽奖抽取记录的方式",
                "combo_items": ["重启后清除", "直到全部抽取完"],
                "combo_items_other": ["重启后清除", "直到全部抽取完", "无需清除"]
            },
            "EN_US": {
                "name": "Clear Record Method",
                "description": "Set the method to clear lottery extraction records",
                "combo_items": ["Restart Clear", "Until All Extracted"],
                "combo_items_other": ["Restart Clear", "Until All Extracted", "No Clear"]
            }
        },
        "half_repeat": {
            "default_value": 1,
            "ZH_CN": {
                "name": "半重复抽取次数",
                "description": "设置半重复抽取的次数"
            },
            "EN_US": {
                "name": "Half Repeat Count",
                "description": "Set the count of half repeat extraction"
            }
        },
        "clear_time": {
            "default_value": 0,
            "ZH_CN": {
                "name": "抽取后定时清除时间",
                "description": "设置抽取后定时清除记录的时间（秒）"
            },
            "EN_US": {
                "name": "Auto Clear Time",
                "description": "Set the time to automatically clear records after extraction (seconds)"
            }
        },
        "draw_type": {
            "default_value": 0,
            "ZH_CN": {
                "name": "抽取方式",
                "description": "设置抽奖抽取的方式",
                "combo_items": ["随机抽取", "公平抽取"]
            },
            "EN_US": {
                "name": "Draw Type",
                "description": "Set the type of lottery extraction",
                "combo_items": ["Random Draw", "Fair Draw"]
            }
        },
        "font_size": {
            "default_value": 50,
            "ZH_CN": {
                "name": "字体大小",
                "description": "设置抽奖结果显示的字体大小"
            },
            "EN_US": {
                "name": "Font Size",
                "description": "Set the font size of lottery result display"
            }
        },
        "display_format": {
            "default_value": 0,
            "ZH_CN": {
                "name": "结果显示格式",
                "description": "设置抽奖结果的显示格式",
                "combo_items": ["序号+名称", "名称", "序号"]
            },
            "EN_US": {
                "name": "Display Format",
                "description": "Set the display format of lottery results",
                "combo_items": ["Number+Name", "Name", "Number"]
            }
        },
        "animation": {
            "default_value": 1,
            "ZH_CN": {
                "name": "动画模式",
                "description": "设置抽奖抽取的动画效果",
                "combo_items": ["手动停止动画", "自动播放动画", "直接显示结果"]
            },
            "EN_US": {
                "name": "Animation Mode",
                "description": "Set the animation effect of lottery extraction",
                "combo_items": ["Manual Stop", "Autoplay", "Show Result"]
            }
        },
        "animation_interval": {
            "default_value": 80,
            "ZH_CN": {
                "name": "动画间隔",
                "description": "设置抽奖动画的间隔时间（毫秒）"
            },
            "EN_US": {
                "name": "Animation Interval",
                "description": "Set the interval time of lottery animation (milliseconds)"
            }
        },
        "autoplay_count": {
            "default_value": 5,
            "ZH_CN": {
                "name": "自动播放次数",
                "description": "设置抽奖动画自动播放的次数"
            },
            "EN_US": {
                "name": "Autoplay Count",
                "description": "Set the autoplay count of lottery animation"
            }
        },
        "animation_color_theme": {
            "default_value": 0,
            "ZH_CN": {
                "name": "动画颜色主题",
                "description": "设置抽奖动画的颜色主题",
                "combo_items": ["关闭", "随机颜色", "固定颜色"]
            },
            "EN_US": {
                "name": "Animation Color Theme",
                "description": "Set the color theme of lottery animation",
                "combo_items": ["Close", "Random Color", "Fixed Color"]
            }
        },
        "result_color_theme": {
            "default_value": 0,
            "ZH_CN": {
                "name": "结果颜色主题",
                "description": "设置抽奖结果显示的颜色主题",
                "combo_items": ["关闭", "随机颜色", "固定颜色"]
            },
            "EN_US": {
                "name": "Result Color Theme",
                "description": "Set the color theme of lottery result display",
                "combo_items": ["Close", "Random Color", "Fixed Color"]
            }
        },
        "animation_fixed_color": {
            "default_value": DEFAULT_THEME_COLOR,
            "ZH_CN": {
                "name": "动画固定颜色",
                "description": "设置抽奖动画的固定颜色"
            },
            "EN_US": {
                "name": "Animation Fixed Color",
                "description": "Set the fixed color of lottery animation"
            }
        },
        "result_fixed_color": {
            "default_value": DEFAULT_THEME_COLOR,
            "ZH_CN": {
                "name": "结果固定颜色",
                "description": "设置抽奖结果显示的固定颜色"
            },
            "EN_US": {
                "name": "Result Fixed Color",
                "description": "Set the fixed color of lottery result display"
            }
        },
        "lottery_image": {
            "default_value": False,
            "ZH_CN": {
                "name": "显示学生图片",
                "description": "设置是否显示学生图片",
                "switchbutton_name": {
                    "enable": "显示",
                    "disable": "隐藏"
                }
            },
            "EN_US": {
                "name": "Show Student Image",
                "description": "Set whether to show student images",
                "switchbutton_name": {
                    "enable": "Show",
                    "disable": "Hide"
                }
            }
        },
        "open_lottery_image_folder": {
            "default_value": None,
            "ZH_CN": {
                "name": "奖品图片文件夹",
                "description": "管理奖品图片文件，图片文件名需与奖品名称一致",
            },
            "EN_US": {
                "name": "Prize Image Folder",
                "description": "Manage prize image files, image file names must match prize names"
            }
        },
        "animation_music": {
            "default_value": False,
            "ZH_CN": {
                "name": "动画音乐",
                "description": "设置是否播放动画音乐",
                "switchbutton_name": {
                    "enable": "播放",
                    "disable": "关闭"
                }
            },
            "EN_US": {
                "name": "Animation Music",
                "description": "Set whether to play animation music",
                "switchbutton_name": {
                    "enable": "Play",
                    "disable": "Stop"
                }
            }
        },
        "result_music": {
            "default_value": False,
            "ZH_CN": {
                "name": "结果音乐",
                "description": "设置是否播放结果音乐",
                "switchbutton_name": {
                    "enable": "播放",
                    "disable": "关闭"
                }
            },
            "EN_US": {
                "name": "Result Music",
                "description": "Set whether to play result music",
                "switchbutton_name": {
                    "enable": "Play",
                    "disable": "Stop"
                }
            }
        },
        "open_animation_music_folder": {
            "default_value": None,
            "ZH_CN": {
                "name": "打开动画音乐文件夹",
                "description": "管理动画音乐文件并支持随机播放功能"
            },
            "EN_US": {
                "name": "Open Animation Music Folder",
                "description": "Manage animation music files and support random play functionality"
            }
        },
        "open_result_music_folder": {
            "default_value": None,
            "ZH_CN": {
                "name": "打开结果音乐文件夹",
                "description": "管理结果音乐文件并支持随机播放功能"
            },
            "EN_US": {
                "name": "Open Result Music Folder",
                "description": "Manage result music files and support random play functionality"
            }
        },
        "animation_music_volume": {
            "default_value": 30,
            "ZH_CN": {
                "name": "动画音乐音量",
                "description": "设置动画音乐的音量"
            },
            "EN_US": {
                "name": "Animation Music Volume",
                "description": "Set the volume of animation music"
            }
        },
        "result_music_volume": {
            "default_value": 30,
            "ZH_CN": {
                "name": "结果音乐音量",
                "description": "设置结果音乐的音量"
            },
            "EN_US": {
                "name": "Result Music Volume",
                "description": "Set the volume of result music"
            }
        },
        "animation_music_fade_in": {
            "default_value": 300,
            "ZH_CN": {
                "name": "动画音乐淡入时间",
                "description": "设置动画音乐淡入的时间"
            },
            "EN_US": {
                "name": "Animation Music Fade In Time",
                "description": "Set the fade in time of animation music"
            }
        },
        "result_music_fade_in": {
            "default_value": 300,
            "ZH_CN": {
                "name": "结果音乐淡入时间",
                "description": "设置结果音乐淡入的时间"
            },
            "EN_US": {
                "name": "Result Music Fade In Time",
                "description": "Set the fade in time of result music"
            }
        },
        "animation_music_fade_out": {
            "default_value": 300,
            "ZH_CN": {
                "name": "动画音乐淡出时间",
                "description": "设置动画音乐淡出的时间"
            },
            "EN_US": {
                "name": "Animation Music Fade Out Time",
                "description": "Set the fade out time of animation music"
            }
        },
        "result_music_fade_out": {
            "default_value": 300,
            "ZH_CN": {
                "name": "结果音乐淡出时间",
                "description": "设置结果音乐淡出的时间"
            },
            "EN_US": {
                "name": "Result Music Fade Out Time",
                "description": "Set the fade out time of result music"
            }
        },
    },
    "safety_settings": {
        "title": {
            "default_value": None,
            "ZH_CN": {
                "name": "安全设置",
                "description": "安全设置"
            },
            "EN_US": {
                "name": "Safe Set",
                "description": "safety settings"
            }
        },
    },
    "basic_safety_settings": {
        "title": {
            "default_value": None,
            "ZH_CN": {
                "name": "基础安全设置",
                "description": "基础安全设置"
            },
            "EN_US": {
                "name": "Basic Safety Set",
                "description": "Basic safety settings"
            }
        },
        "verification_method": {
            "default_value": None,
            "ZH_CN": {
                "name": "验证方式",
                "description": "设置安全功能的验证方式"
            },
            "EN_US": {
                "name": "Verification Method",
                "description": "Set verification methods for security features"
            }
        },
        "verification_process": {
            "default_value": None,
            "ZH_CN": {
                "name": "验证流程",
                "description": "设置安全功能的验证流程"
            },
            "EN_US": {
                "name": "Verification Process",
                "description": "Set verification process for security features"
            }
        },
        "security_operations": {
            "default_value": None,
            "ZH_CN": {
                "name": "安全操作",
                "description": "设置安全操作的验证方式"
            },
            "EN_US": {
                "name": "Security Operations",
                "description": "Set verification methods for security operations"
            }
        },
        "safety_switch": {
            "default_value": False,
            "ZH_CN": {
                "name": "安全开关",
                "description": "开启后，所有带有安全操作的功能都需要验证密码",
                "switchbutton_name": {
                    "enable": "启用",
                    "disable": "禁用"
                }
            },
            "EN_US": {
                "name": "Safety Switch",
                "description": "Enabled: Security ops require password",
                "switchbutton_name": {
                    "enable": "Enable",
                    "disable": "Disable"
                }
            }
        },
        "set_password": {
            "default_value": None,
            "ZH_CN": {
                "name": "设置/修改密码",
                "description": "设置或修改安全密码"
            },
            "EN_US": {
                "name": "Set/Change Password",
                "description": "Set or change security password"
            }
        },
        "totp_switch": {
            "default_value": False,
            "ZH_CN": {
                "name": "是否开启TOTP开关",
                "description": "开启后，将可以在安全操作中使用TOTP",
                "switchbutton_name": {
                    "enable": "启用",
                    "disable": "禁用"
                }
            },
            "EN_US": {
                "name": "Enable TOTP Switch",
                "description": "Enable to use TOTP in security ops",
                "switchbutton_name": {
                    "enable": "Enable",
                    "disable": "Disable"
                }
            }
        },
        "set_totp": {
            "default_value": None,
            "ZH_CN": {
                "name": "设置TOTP",
                "description": "设置TOTP"
            },
            "EN_US": {
                "name": "Set TOTP",
                "description": "Set TOTP"
            }
        },
        "usb_switch": {
            "default_value": False,
            "ZH_CN": {
                "name": "是否开启U盘开关",
                "description": "开启后，将可以在安全操作中使用U盘解锁",
                "switchbutton_name": {
                    "enable": "启用",
                    "disable": "禁用"
                }
            },
            "EN_US": {
                "name": "Enable USB flash drive Switch",
                "description": "Enable to use USB flash drive to unlock in security ops",
                "switchbutton_name": {
                    "enable": "Enable",
                    "disable": "Disable"
                }
            }
        },
        "bind_usb": {
            "default_value": None,
            "ZH_CN": {
                "name": "绑定U盘",
                "description": "绑定U盘解锁"
            },
            "EN_US": {
                "name": "Bind USB flash drive",
                "description": "Bind USB flash drive to unlock"
            }
        },
        "unbind_usb": {
            "default_value": None,
            "ZH_CN": {
                "name": "解绑U盘",
                "description": "解绑U盘解锁"
            },
            "EN_US": {
                "name": "Unbind USB flash drive",
                "description": "Unbind USB flash drive to unlock"
            }
        },
        "verification_process": {
            "default_value": 0,
            "ZH_CN": {
                "name": "安全验证步骤",
                "description": "设置安全功能的验证步骤",
                "combo_items": [
                    "单步验证（任选一种方式）",
                    "仅 密码",
                    "仅 TOTP",
                    "仅 U盘解锁",
                    "密码 + TOTP",
                    "密码 + U盘解锁",
                    "TOTP + U盘解锁",
                    "密码 + TOTP + U盘解锁"
                ]
            },
            "EN_US": {
                "name": "Security Verification Steps",
                "description": "Set verification steps for security features",
                "combo_items": [
                    "Single-step verification (choose any method)",
                    "Password only",
                    "TOTP only",
                    "USB drive only",
                    "Password + TOTP",
                    "Password + USB drive",
                    "TOTP + USB drive",
                    "Password + TOTP + USB drive"
                ]
            }
        },
        "show_hide_floating_window_switch": {
            "default_value": False,
            "ZH_CN": {
                "name": "显示/隐藏操作是否需安全验证",
                "description": "开启后可在安全操作中显示/隐藏悬浮窗，需安全验证",
                "switchbutton_name": {
                    "enable": "启用",
                    "disable": "禁用"
                }
            },
            "EN_US": {
                "name": "Enable Show/Hide Floating Window Switch",
                "description": "Enable to show/hide floating window in security ops, with verification",
                "switchbutton_name": {
                    "enable": "Enable",
                    "disable": "Disable"
                }
            }
        },
        "restart_switch": {
            "default_value": False,
            "ZH_CN": {
                "name": "重启操作是否需安全验证",
                "description": "开启后重启软件，需安全验证",
                "switchbutton_name": {
                    "enable": "启用",
                    "disable": "禁用"
                }
            },
            "EN_US": {
                "name": "Enable Restart Switch",
                "description": "Enable to restart software, with verification",
                "switchbutton_name": {
                    "enable": "Enable",
                    "disable": "Disable"
                }
            }
        },
        "exit_switch": {
            "default_value": False,
            "ZH_CN": {
                "name": "退出操作是否需安全验证",
                "description": "开启后退出软件，需安全验证",
                "switchbutton_name": {
                    "enable": "启用",
                    "disable": "禁用"
                }
            },
            "EN_US": {
                "name": "Enable Exit Switch",
                "description": "Enable to exit software, with verification",
                "switchbutton_name": {
                    "enable": "Enable",
                    "disable": "Disable"
                }
            }
        },
    },
    "advanced_safety_settings": {
        "title": {
            "default_value": None,
            "ZH_CN": {
                "name": "进阶安全设置",
                "description": "进阶安全设置"
            },
            "EN_US": {
                "name": "Advanced Safety Settings",
                "description": "Advanced safety settings"
            }
        },
        "strong_protection": {
            "default_value": None,
            "ZH_CN": {
                "name": "强力防删除设置",
                "description": "强力防删除功能设置"
            },
            "EN_US": {
                "name": "Strong Anti-Deletion Settings",
                "description": "anti-deletion function settings"
            }
        },
        "data_encryption": {
            "default_value": None,
            "ZH_CN": {
                "name": "数据加密设置",
                "description": "数据加密功能设置"
            },
            "EN_US": {
                "name": "Data Encryption Settings",
                "description": "Data encryption function settings"
            }
        },
        "encryption_strong_switch": {
            "default_value": False,
            "ZH_CN": {
                "name": "软件主程序自我保护",
                "description": "开启后软件主程序将启用自我保护功能",
                "switchbutton_name": {
                    "enable": "启用",
                    "disable": "禁用"
                }
            },
            "EN_US": {
                "name": "Software Self Protection",
                "description": "Enable to protect software main process",
                "switchbutton_name": {
                    "enable": "Enable",
                    "disable": "Disable"
                }
            }
        },
        "encryption_strong_mode": {
            "default_value": 0,
            "ZH_CN": {
                "name": "保护强度模式",
                "description": "选择软件自我保护强度模式",
                "combo_items": {
                    "仅软件目录备份",
                    "软件目录+系统缓存目录备份"
                }
            },
            "EN_US": {
                "name": "Strong Protection Mode",
                "description": "Select strong protection mode",
                "combo_items": {
                    "Only backup software directory",
                    "Backup software directory and system cache directory"
                }
            }
        },
        "strong_list_switch": {
            "default_value": False,
            "ZH_CN": {
                "name": "保护名单文件",
                "description": "开启后软件将保护名单文件",
                "switchbutton_name": {
                    "enable": "启用",
                    "disable": "禁用"
                }
            },
            "EN_US": {
                "name": "Strong Protection List",
                "description": "Enable to strong protection list",
                "switchbutton_name": {
                    "enable": "Enable",
                    "disable": "Disable"
                }
            }
        },
        "strong_history_switch": {
            "default_value": False,
            "ZH_CN": {
                "name": "保护历史记录",
                "description": "开启后软件将保护历史",
                "switchbutton_name": {
                    "enable": "启用",
                    "disable": "禁用"
                }
            },
            "EN_US": {
                "name": "Strong Protection History",
                "description": "Enable to strong protection history",
                "switchbutton_name": {
                    "enable": "Enable",
                    "disable": "Disable"
                }
            }
        },
        "strong_temp_switch": {
            "default_value": False,
            "ZH_CN": {
                "name": "保护临时记录",
                "description": "开启后软件将保护临时已抽取记录",
                "switchbutton_name": {
                    "enable": "启用",
                    "disable": "禁用"
                }
            },
            "EN_US": {
                    "name": "Strong Protection Temporary History",
                "description": "Enable to strong protection temporary history",
                "switchbutton_name": {
                    "enable": "Enable",
                    "disable": "Disable"
                }
            }
        },
        "encryption_list_switch": {
            "default_value": False,
            "ZH_CN": {
                "name": "加密名单文件",
                "description": "开启后软件将加密名单文件",
                "switchbutton_name": {
                    "enable": "启用",
                    "disable": "禁用"
                }
            },
            "EN_US": {
                "name": "Encryption List",
                "description": "Enable to encryption list",
                "switchbutton_name": {
                    "enable": "Enable",
                    "disable": "Disable"
                }
            }
        },
        "encryption_history_switch": {
            "default_value": False,
            "ZH_CN": {
                "name": "加密历史记录",
                "description": "开启后软件将加密历史记录",
                "switchbutton_name": {
                    "enable": "启用",
                    "disable": "禁用"
                }
            },
            "EN_US": {
                "name": "Encryption History",
                "description": "Enable to encrypt history",
                "switchbutton_name": {
                    "enable": "Enable",
                    "disable": "Disable"
                }
            }
        },
        "encryption_temp_switch": {
            "default_value": False,
            "ZH_CN": {
                "name": "加密临时记录",
                "description": "开启后软件将加密临时已抽取记录",
                "switchbutton_name": {
                    "enable": "启用",
                    "disable": "禁用"
                }
            },
            "EN_US": {
                "name": "Encryption Temporary History",
                "description": "Enable to encryption temporary history",
                "switchbutton_name": {
                    "enable": "Enable",
                    "disable": "Disable"
                }
            }
        }
    },
    "custom_settings": {
        "title": {
            "default_value": None,
            "ZH_CN": {
                "name": "个性设置",
                "description": "个性设置"
            },
            "EN_US": {
                "name": "Cust Set",
                "description": "Custom settings"
            }
        },
    },
    "page_management": {
        "title": {
            "default_value": None,
            "ZH_CN": {
                "name": "页面管理",
                "description": "页面管理设置"
            },
            "EN_US": {
                "name": "Page Mgt",
                "description": "Page management settings"
            }
        },
        "roll_call": {
            "default_value": None,
            "ZH_CN": {
                "name": "点名设置",
                "description": "点名设置"
            },
            "EN_US": {
                "name": "Roll Call Settings",
                "description": "Roll call settings"
            }
        },
        "lottery": {
            "default_value": None,
            "ZH_CN": {
                "name": "抽奖设置",
                "description": "抽奖设置"
            },
            "EN_US": {
                "name": "Lottery Settings",
                "description": "Lottery settings"
            }
        },
        "roll_call_method": {
            "default_value": 1,
            "ZH_CN": {
                "name": "点名控制面板位置",
                "description": "配置点名控制面板位置",
                "combo_items": [
                    "左侧",
                    "右侧",
                    "左侧底部",
                    "右侧底部"
                ]
            },
            "EN_US": {
                "name": "Roll Call Method",
                "description": "Roll call method",
                "combo_items": [
                    "Left",
                    "Right",
                    "Left Bottom",
                    "Right Bottom"
                ]
            }
        },
        "show_name": {
            "default_value": False,
            "ZH_CN": {
                "name": "名称设置按钮",
                "description": "开启后软件将显示名称设置按钮",
                "switchbutton_name": {
                    "enable": "显示",
                    "disable": "隐藏"
                }
            },
            "EN_US": {
                "name": "Name Setting Switch",
                "description": "Enable to show name setting switch",
                "switchbutton_name": {
                    "enable": "Show",
                    "disable": "Hide"
                }
            }
        },
        "reset_roll_call": {
            "default_value": True,
            "ZH_CN": {
                "name": "重置点名按钮",
                "description": "开启后软件将显示重置点名按钮",
                "switchbutton_name": {
                    "enable": "显示",
                    "disable": "隐藏"
                }
            },
            "EN_US": {
                "name": "Reset Roll Call",
                "description": "Enable to show reset roll call button",
                "switchbutton_name": {
                    "enable": "Show",
                    "disable": "Hide"
                }
            }
        },
        "roll_call_quantity_control": {
            "default_value": True,
            "ZH_CN": {
                "name": "增加/减少抽取数量控制条",
                "description": "开启后软件将显示增加/减少抽取数量控制条",
                "switchbutton_name": {
                    "enable": "显示",
                    "disable": "隐藏"
                }
            },
            "EN_US": {
                "name": "Roll Call Quantity Control",
                "description": "Enable to limit roll call quantity",
                "switchbutton_name": {
                    "enable": "Show",
                    "disable": "Hide"
                }
            }
        },
        "roll_call_start_button": {
            "default_value": True,
            "ZH_CN": {
                "name": "开始按钮",
                "description": "开启后软件将显示开始按钮",
                "switchbutton_name": {
                    "enable": "显示",
                    "disable": "隐藏"
                }
            },
            "EN_US": {
                "name": "Roll Call Start Button",
                "description": "Enable to show start button",
                "switchbutton_name": {
                    "enable": "Show",
                    "disable": "Hide"
                }
            }
        },
        "roll_call_list": {
            "default_value": True,
            "ZH_CN": {
                "name": "点名名单切换下拉框",
                "description": "开启后软件将显示点名名单切换下拉框",
                "switchbutton_name": {
                    "enable": "显示",
                    "disable": "隐藏"
                }
            },
            "EN_US": {
                "name": "Roll Call List Combo",
                "description": "Enable to show roll call list combo",
                "switchbutton_name": {
                    "enable": "Show",
                    "disable": "Hide"
                }
            }
        },
        "roll_call_range": {
            "default_value": True,
            "ZH_CN": {
                "name": "点名范围下拉框",
                "description": "开启后软件将显示点名范围",
                "switchbutton_name": {
                    "enable": "显示",
                    "disable": "隐藏"
                }
            },
            "EN_US": {
                "name": "Roll Call Range Combo",
                "description": "Enable to show roll call range",
                "switchbutton_name": {
                    "enable": "Show",
                    "disable": "Hide"
                }
            }
        },
        "roll_call_gender": {
            "default_value": True,
            "ZH_CN": {
                "name": "点名性别范围下拉框",
                "description": "开启后软件将显示点名性别范围下拉框",
                "switchbutton_name": {
                    "enable": "显示",
                    "disable": "隐藏"
                }
            },
            "EN_US": {
                "name": "Roll Call Gender Combo",
                "description": "Enable to show roll call gender combo",
                "switchbutton_name": {
                    "enable": "Show",
                    "disable": "Hide"
                }
            }
        },
        "roll_call_quantity_label": {
            "default_value": True,
            "ZH_CN": {
                "name": "数量标签",
                "description": "开启后软件将显示人数/组数数量标签",
                "switchbutton_name": {
                    "enable": "显示",
                    "disable": "隐藏"
                }
            },
            "EN_US": {
                "name": "Quantity Label",
                "description": "Enable to show person/group quantity label", 
                "switchbutton_name": {
                    "enable": "Show",
                    "disable": "Hide"
                }
            }
        },
        "lottery_method": {
            "default_value": 1,
            "ZH_CN": {
                "name": "抽奖控制面板位置",
                "description": "配置抽奖控制面板位置",
                "combo_items": [
                    "左侧",
                    "右侧",
                    "左侧底部",
                    "右侧底部"
                ]
            },
            "EN_US": {
                "name": "Lottery Method",
                "description": "Lottery method",
                "combo_items": [
                    "Left",
                    "Right",
                    "Left Bottom",
                    "Right Bottom"
                ]
            }
        },
        "show_lottery_name": {
            "default_value": False,
            "ZH_CN": {
                "name": "名称设置按钮",
                "description": "开启后软件将显示名称设置按钮",
                "switchbutton_name": {
                    "enable": "显示",
                    "disable": "隐藏"
                }
            },
            "EN_US": {
                "name": "Name Setting Switch",
                "description": "Enable to show name setting switch",
                "switchbutton_name": {
                    "enable": "Show",
                    "disable": "Hide"
                }
            }
        },
        "reset_lottery": {
            "default_value": True,
            "ZH_CN": {
                "name": "重置抽奖按钮",
                "description": "开启后软件将显示重置抽奖按钮",
                "switchbutton_name": {
                    "enable": "显示",
                    "disable": "隐藏"
                }
            },
            "EN_US": {
                "name": "Reset Lottery",
                "description": "Enable to show reset Lottery button",
                "switchbutton_name": {
                    "enable": "Show",
                    "disable": "Hide"
                }
            }
        },
        "lottery_quantity_control": {
            "default_value": True,
            "ZH_CN": {
                "name": "增加/减少抽取数量控制条",
                "description": "开启后软件将显示增加/减少抽取数量控制条",
                "switchbutton_name": {
                    "enable": "显示",
                    "disable": "隐藏"
                }
            },
            "EN_US": {
                "name": "Lottery Quantity Control",
                "description": "Enable to limit Lottery quantity",
                "switchbutton_name": {
                    "enable": "Show",
                    "disable": "Hide"
                }
            }
        },
        "lottery_start_button": {
            "default_value": True,
            "ZH_CN": {
                "name": "开始按钮",
                "description": "开启后软件将显示开始按钮",
                "switchbutton_name": {
                    "enable": "显示",
                    "disable": "隐藏"
                }
            },
            "EN_US": {
                "name": "Lottery Start Button",
                "description": "Enable to show start button",
                "switchbutton_name": {
                    "enable": "Show",
                    "disable": "Hide"
                }
            }
        },
        "lottery_list": {
            "default_value": True,
            "ZH_CN": {
                "name": "抽奖名单切换下拉框",
                "description": "开启后软件将显示抽奖名单切换下拉框",
                "switchbutton_name": {
                    "enable": "显示",
                    "disable": "隐藏"
                }
            },
            "EN_US": {
                "name": "Lottery List Combo",
                "description": "Enable to show Lottery list combo",
                "switchbutton_name": {
                    "enable": "Show",
                    "disable": "Hide"
                }
            }
        },
        "lottery_quantity_label": {
            "default_value": True,
            "ZH_CN": {
                "name": "数量标签",
                "description": "开启后软件将显示奖数标签",
                "switchbutton_name": {
                    "enable": "显示",
                    "disable": "隐藏"
                }
            },
            "EN_US": {
                "name": "Quantity Label",
                "description": "Enable to show Lottery quantity label",
                "switchbutton_name": {
                    "enable": "Show",
                    "disable": "Hide"
                }
            }
        }
    },
    "about": {
        "title": {
            "default_value": None,
            "ZH_CN": {
                "name": "关于",
                "description": "软件关于页面"
            },
            "EN_US": {
                "name": "About",
                "description": "Software about page"
            }
        },
        "github": {
            "default_value": None,
            "ZH_CN": {
                "name": "Github",
                "description": "访问项目仓库"
            },
            "EN_US": {
                "name": "Github",
                "description": "Visit project repository"
            }
        },
        "bilibili": {
            "default_value": None,
            "ZH_CN": {
                "name": "Bilibili",
                "description": "访问 黎泽懿_Aionflux 的 Bilibili 账号"
            },
            "EN_US": {
                "name": "Bilibili",
                "description": "Visit 黎泽懿_Aionflux's Bilibili account"
            }
        },
        "contributor": {
            "default_value": None,
            "ZH_CN": {
                "name": "贡献人员",
                "description": "点击查看详细贡献者信息",
                "contributor_role_1": "设计 & 创意 & 策划 &\n维护 & 文档& 测试",
                "contributor_role_2": "创意 & 维护",
                "contributor_role_3": "应用测试 & 文档 & 安装包制作",
                "contributor_role_4": "响应式前端页面\n设计及维护 & 文档",
                "contributor_role_5": "创意 & 文档",
                "contributor_role_6": "响应式前端页面\n设计及维护 & 文档",
            },
            "EN_US": {
                "name": "Contributor",
                "description": "Click to view detailed contributor information",
                "contributor_role_1": "Design & Creative & Planning &\nMaintenance & Documentation & Testing",
                "contributor_role_2": "Creative & Maintenance",
                "contributor_role_3": "Application Testing & Documentation & Installer Packaging",
                "contributor_role_4": "Responsive Front-end Page\nDesign & Maintenance & Documentation",
                "contributor_role_5": "Creative & Documentation",
                "contributor_role_6": "Responsive Front-end Page\nDesign & Maintenance & Documentation",
            }
        },
        "donation": {
            "default_value": None,
            "ZH_CN": {
                "name": "捐赠支持",
                "description": "支持项目发展，感谢您的捐赠"
            },
            "EN_US": {
                "name": "Donation",
                "description": "Support project development, thank you for your donation"
            }
        },
        "check_update": {
            "default_value": None,
            "ZH_CN": {
                "name": "检查更新",
                "description": "检查当前是否为最新版本"
            },
            "EN_US": {
                "name": "Check Update",
                "description": "Check if the software is the latest version"
            }
        },
        "website": {
            "default_value": None,
            "ZH_CN": {
                "name": "SecRandom 官网",
                "description": "访问 SecRandom 软件官网"
            },
            "EN_US": {
                "name": "SecRandom Website",
                "description": "Visit SecRandom software website"
            }
        },
        "channel": {
            "default_value": 0,
            "ZH_CN": {
                "name": "更新通道",
                "description": "选择 SecRandom 软件更新通道",
                "combo_items": ["正式版本", "测试版本"]
            },
            "EN_US": {
                "name": "Update Channel",
                "description": "Select SecRandom software update channel",
                "combo_items": ["Stable Version", "Test Version"]
            }
        },
        "copyright": {
            "default_value": None,
            "ZH_CN": {
                "name": "版权",
                "description": "SecRandom 遵循 GPL-3.0 协议"
            },
            "EN_US": {
                "name": "Copyright",
                "description": "SecRandom follows GPL-3.0 protocol"
            }
        },
        "version": {
            "default_value": None,
            "ZH_CN": {
                "name": "版本",
                "description": "显示当前软件版本号"
            },
            "EN_US": {
                "name": "Version",
                "description": "Display current software version number"
            }
        }
    }
}