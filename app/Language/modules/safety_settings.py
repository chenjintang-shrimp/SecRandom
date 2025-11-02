# 安全设置语言配置
safety_settings = {"ZH_CN": {"title": {"name": "安全设置", "description": "安全设置"}}}

# 基础安全设置语言配置
basic_safety_settings = {
    "ZH_CN": {
        "title": {"name": "基础安全设置", "description": "基础安全设置"},
        "verification_method": {
            "name": "验证方式",
            "description": "设置安全功能的验证方式",
        },
        "verification_process": {
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
                "密码 + TOTP + U盘解锁",
            ],
        },
        "security_operations": {
            "name": "安全操作",
            "description": "设置安全操作的验证方式",
        },
        "safety_switch": {
            "name": "安全开关",
            "description": "开启后，所有带有安全操作的功能都需要验证密码",
            "switchbutton_name": {"enable": "启用", "disable": "禁用"},
        },
        "set_password": {"name": "设置/修改密码", "description": "设置或修改安全密码"},
        "totp_switch": {
            "name": "是否开启TOTP开关",
            "description": "开启后，将可以在安全操作中使用TOTP",
            "switchbutton_name": {"enable": "启用", "disable": "禁用"},
        },
        "set_totp": {"name": "设置TOTP", "description": "设置TOTP"},
        "usb_switch": {
            "name": "是否开启U盘开关",
            "description": "开启后，将可以在安全操作中使用U盘解锁",
            "switchbutton_name": {"enable": "启用", "disable": "禁用"},
        },
        "bind_usb": {"name": "绑定U盘", "description": "绑定U盘解锁"},
        "unbind_usb": {"name": "解绑U盘", "description": "解绑U盘解锁"},
        "show_hide_floating_window_switch": {
            "name": "显示/隐藏操作是否需安全验证",
            "description": "开启后可在安全操作中显示/隐藏悬浮窗，需安全验证",
            "switchbutton_name": {"enable": "启用", "disable": "禁用"},
        },
        "restart_switch": {
            "name": "重启操作是否需安全验证",
            "description": "开启后重启软件，需安全验证",
            "switchbutton_name": {"enable": "启用", "disable": "禁用"},
        },
        "exit_switch": {
            "name": "退出操作是否需安全验证",
            "description": "开启后退出软件，需安全验证",
            "switchbutton_name": {"enable": "启用", "disable": "禁用"},
        },
    }
}
