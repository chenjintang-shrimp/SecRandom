# 基础设置语言配置
basic_settings = {
    "ZH_CN": {
        "title": {"name": "基础设置", "description": "软件基础设置"},
        "basic_function": {"name": "基础功能", "description": "软件基础功能"},
        "data_management": {"name": "数据管理", "description": "数据管理"},
        "personalised": {"name": "个性化", "description": "软件个性化设置"},
        "autostart": {
            "name": "开机自启",
            "description": "设置软件是否在开机时自动启动",
            "switchbutton_name": {"enable": "开启", "disable": "关闭"},
        },
        "check_update": {
            "name": "检查更新",
            "description": "设置是否在启动时检查软件更新",
            "switchbutton_name": {"enable": "启用", "disable": "禁用"},
        },
        "show_startup_window": {
            "name": "显示启动窗口",
            "description": "设置是否在启动时显示启动窗口",
            "switchbutton_name": {"enable": "显示", "disable": "不显示"},
        },
        "export_diagnostic_data": {
            "name": "导出诊断数据",
            "description": "设置是否在退出时导出诊断数据",
            "pushbutton_name": "导出诊断数据",
        },
        "export_settings": {
            "name": "导出设置",
            "description": "设置是否在退出时导出设置",
            "pushbutton_name": "导出设置",
        },
        "import_settings": {
            "name": "导入设置",
            "description": "设置是否在启动时导入设置",
            "pushbutton_name": "导入设置",
        },
        "export_all_data": {
            "name": "导出所有数据",
            "description": "设置是否在退出时导出所有数据",
            "pushbutton_name": "导出所有数据",
        },
        "import_all_data": {
            "name": "导入所有数据",
            "description": "设置是否在启动时导入所有数据",
            "pushbutton_name": "导入所有数据",
        },
        "dpiScale": {
            "name": "DPI缩放",
            "description": "设置软件DPI缩放比例(重启生效)",
            "combo_items": ["100%", "125%", "150%", "175%", "200%", "Auto"],
        },
        "font": {"name": "字体", "description": "设置软件字体(重启生效)"},
        "theme": {
            "name": "主题",
            "description": "设置软件主题",
            "combo_items": ["浅色", "深色", "跟随系统设置"],
        },
        "theme_color": {"name": "主题色", "description": "软件主题色"},
        "language": {"name": "语言", "description": "设置软件语言(重启生效)"},
    }
}
