# 浮窗管理语言配置
floating_window_management = {
    "ZH_CN": {
        "title": {"name": "浮窗管理", "description": "配置浮动窗口相关设置"},
        "basic_settings": {"name": "基本设置", "description": "配置浮动窗口基本设置"},
        "appearance_settings": {
            "name": "外观设置",
            "description": "配置浮动窗口外观设置",
        },
        "edge_settings": {"name": "贴边设置", "description": "配置浮动窗口贴边设置"},
        "startup_display_floating_window": {
            "name": "启动时显示浮窗",
            "description": "控制软件启动时是否自动显示浮动窗口",
            "switchbutton_name": {"enable": "显示", "disable": "隐藏"},
        },
        "floating_window_opacity": {
            "name": "浮窗透明度",
            "description": "调整浮动窗口透明度",
        },
        "reset_floating_window_position_button": {
            "name": "重置浮窗位置",
            "description": "将浮动窗口位置重置为默认位置",
            "pushbutton_name": "重置位置",
        },
        "floating_window_button_control": {
            "name": "浮窗控件配置",
            "description": "选择在浮动窗口中显示的功能按钮",
            "combo_items": [
                "点名",
                "闪抽",
                "即抽",
                "自定义抽",
                "抽奖",
                "点名+闪抽",
                "点名+自定义抽",
                "点名+抽奖",
                "闪抽+自定义抽",
                "闪抽+抽奖",
                "自定义抽+抽奖",
                "点名+闪抽+自定义抽",
                "点名+闪抽+抽奖",
                "点名+自定义抽+抽奖",
                "闪抽+自定义抽+抽奖",
                "点名+闪抽+自定义抽+抽奖",
            ],
        },
        "floating_window_placement": {
            "name": "浮窗排列方式",
            "description": "设置浮动窗口中控件排列方式",
            "combo_items": ["矩形排列", "竖向排列", "横向排列"],
        },
        "floating_window_display_style": {
            "name": "浮窗显示样式",
            "description": "设置浮动窗口中控件显示样式",
            "combo_items": ["图标+文字", "图标", "文字"],
        },
        "floating_window_stick_to_edge": {
            "name": "贴边功能",
            "description": "控制浮动窗口是否自动贴边",
            "switchbutton_name": {"enable": "", "disable": ""},
        },
        "floating_window_stick_to_edge_recover_seconds": {
            "name": "贴边收纳时间",
            "description": "设置浮动窗口贴边后自动收纳时间（秒）",
        },
        "floating_window_long_press_duration": {
            "name": "长按时间",
            "description": "设置浮动窗口长按时间（毫秒）",
        },
        "floating_window_stick_to_edge_display_style": {
            "name": "贴边显示样式",
            "description": "设置浮动窗口贴边时显示样式",
            "combo_items": ["图标", "文字", "箭头"],
        },
    }
}

# 侧边栏/托盘管理语言配置
sidebar_tray_management = {
    "ZH_CN": {
        "title": {
            "name": "侧边栏/托盘管理",
            "description": "配置侧边栏和系统托盘相关设置",
        }
    }
}

# 主界面侧边栏语言配置
sidebar_management_window = {
    "ZH_CN": {
        "title": {
            "name": "主界面侧边栏",
            "description": "配置主界面侧边栏管理相关设置",
        },
        "roll_call_sidebar_position": {
            "name": "点名侧边栏位置",
            "description": "配置点名功能在侧边栏位置",
            "combo_items": ["顶部", "底部", "不显示"],
        },
        "custom_roll_call_sidebar_position": {
            "name": "自定义抽侧边栏位置",
            "description": "配置自定义抽功能在侧边栏位置",
            "combo_items": ["顶部", "底部", "不显示"],
        },
        "lottery_sidebar_position": {
            "name": "抽奖侧边栏位置",
            "description": "配置抽奖功能在侧边栏位置",
            "combo_items": ["顶部", "底部", "不显示"],
        },
        "main_window_history": {
            "name": "主窗口历史记录位置",
            "description": "配置历史记录功能在侧边栏位置",
            "combo_items": ["顶部", "底部", "不显示"],
        },
        "settings_icon": {
            "name": "设置图标位置",
            "description": "配置设置图标在侧边栏位置",
            "combo_items": ["顶部", "底部", "不显示"],
        },
    }
}

# 设置窗口侧边栏语言配置
sidebar_management_settings = {
    "ZH_CN": {
        "title": {
            "name": "设置窗口侧边栏",
            "description": "配置设置窗口侧边栏",
        },
        "base_settings": {
            "name": "基础设置位置",
            "description": "设置基础设置项在侧边栏位置",
            "combo_items": ["顶部", "底部", "不显示"],
        },
        "name_management": {
            "name": "名单管理位置",
            "description": "设置名单管理项在侧边栏位置",
            "combo_items": ["顶部", "底部", "不显示"],
        },
        "draw_settings": {
            "name": "抽取设置位置",
            "description": "设置抽取设置项在侧边栏位置",
            "combo_items": ["顶部", "底部", "不显示"],
        },
        "notification_service": {
            "name": "通知服务位置",
            "description": "设置通知服务项在侧边栏位置",
            "combo_items": ["顶部", "底部", "不显示"],
        },
        "security_settings": {
            "name": "安全设置位置",
            "description": "设置安全设置项在侧边栏位置",
            "combo_items": ["顶部", "底部", "不显示"],
        },
        "personal_settings": {
            "name": "个性设置位置",
            "description": "设置个性设置项在侧边栏位置",
            "combo_items": ["顶部", "底部"],
        },
        "voice_settings": {
            "name": "语音设置位置",
            "description": "设置语音设置项在侧边栏位置",
            "combo_items": ["顶部", "底部", "不显示"],
        },
        "settings_history": {
            "name": "设置历史记录位置",
            "description": "设置历史记录项在侧边栏位置",
            "combo_items": ["顶部", "底部", "不显示"],
        },
        "more_settings": {
            "name": "更多设置位置",
            "description": "设置更多设置项在侧边栏位置",
            "combo_items": ["顶部", "底部", "不显示"],
        },
    }
}

# 托盘管理语言配置
tray_management = {
    "ZH_CN": {
        "title": {"name": "托盘管理", "description": "配置系统托盘相关设置"},
        "show_hide_main_window": {
            "name": "暂时显示/隐藏主界面",
            "description": "控制主界面显示和隐藏",
            "switchbutton_name": {"enable": "显示", "disable": "隐藏"},
        },
        "open_settings": {
            "name": "打开设置窗口",
            "description": "控制是否在托盘菜单中显示设置窗口选项",
            "switchbutton_name": {"enable": "显示", "disable": "隐藏"},
        },
        "show_hide_float_window": {
            "name": "暂时显示/隐藏浮窗",
            "description": "控制浮动窗口显示和隐藏",
            "switchbutton_name": {"enable": "显示", "disable": "隐藏"},
        },
        "restart": {
            "name": "重启应用",
            "description": "控制是否在托盘菜单中显示重启选项",
            "switchbutton_name": {"enable": "显示", "disable": "隐藏"},
        },
        "exit": {
            "name": "退出应用",
            "description": "控制是否在托盘菜单中显示退出选项",
            "switchbutton_name": {"enable": "显示", "disable": "隐藏"},
        },
    }
}
