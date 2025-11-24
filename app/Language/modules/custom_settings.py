# 个性设置页面的语言文件

custom_settings = {"ZH_CN": {"title": {"name": "个性设置", "description": "个性化设置选项"}}}

# 页面管理语言配置
page_management = {
    "ZH_CN": {
        "title": {"name": "页面管理", "description": "页面管理设置选项"},
        "roll_call": {"name": "点名设置", "description": "点名功能设置"},
        "lottery": {"name": "抽奖设置", "description": "抽奖功能设置"},
        "custom": {"name": "自定义抽设置", "description": "自定义抽取功能设置"},
        "roll_call_method": {
            "name": "点名控制面板位置",
            "description": "设置点名控制面板显示位置",
            "combo_items": ["左侧", "右侧"],
        },
        "roll_call_reset_button": {
            "name": "重置点名按钮",
            "description": "开启后显示重置点名按钮",
            "switchbutton_name": {"enable": "显示", "disable": "隐藏"},
        },
        "roll_call_quantity_control": {
            "name": "抽取数量控制条",
            "description": "控制是否显示抽取数量调整控件",
            "switchbutton_name": {"enable": "显示", "disable": "隐藏"},
        },
        "roll_call_start_button": {
            "name": "开始按钮",
            "description": "控制是否显示点名开始按钮",
            "switchbutton_name": {"enable": "显示", "disable": "隐藏"},
        },
        "roll_call_list": {
            "name": "点名名单切换下拉框",
            "description": "控制是否显示点名名单切换框",
            "switchbutton_name": {"enable": "显示", "disable": "隐藏"},
        },
        "roll_call_range": {
            "name": "点名范围下拉框",
            "description": "控制是否显示点名范围选择框",
            "switchbutton_name": {"enable": "显示", "disable": "隐藏"},
        },
        "roll_call_gender": {
            "name": "点名性别范围下拉框",
            "description": "控制是否显示点名性别范围选择框",
            "switchbutton_name": {"enable": "显示", "disable": "隐藏"},
        },
        "roll_call_quantity_label": {
            "name": "数量标签",
            "description": "控制是否显示抽取人数/组数的标签",
            "switchbutton_name": {"enable": "显示", "disable": "隐藏"},
        },
        "roll_call_remaining_button": {
            "name": "查看剩余名单按钮",
            "description": "控制是否显示查看剩余名单按钮",
            "switchbutton_name": {"enable": "显示", "disable": "隐藏"},
        },
        "lottery_method": {
            "name": "抽奖控制面板位置",
            "description": "设置抽奖控制面板显示位置",
            "combo_items": ["左侧", "右侧"],
        },
        "lottery_reset_button": {
            "name": "重置抽奖按钮",
            "description": "控制是否显示抽奖重置按钮",
            "switchbutton_name": {"enable": "显示", "disable": "隐藏"},
        },
        "lottery_quantity_control": {
            "name": "抽取数量控制条",
            "description": "控制是否显示抽奖数量调整控件",
            "switchbutton_name": {"enable": "显示", "disable": "隐藏"},
        },
        "lottery_start_button": {
            "name": "开始按钮",
            "description": "控制是否显示抽奖开始按钮",
            "switchbutton_name": {"enable": "显示", "disable": "隐藏"},
        },
        "lottery_list": {
            "name": "抽奖名单切换下拉框",
            "description": "控制是否显示抽奖名单切换框",
            "switchbutton_name": {"enable": "显示", "disable": "隐藏"},
        },
        "lottery_roll_call_list": {
            "name": "抽奖中的学生名单切换下拉框",
            "description": "控制是否显示抽奖中的学生名单切换框",
            "switchbutton_name": {"enable": "显示", "disable": "隐藏"},
        },
        "lottery_roll_call_range": {
            "name": "抽奖中的学生点名范围下拉框",
            "description": "控制是否显示抽奖中的学生点名范围选择框",
            "switchbutton_name": {"enable": "显示", "disable": "隐藏"},
        },
        "lottery_roll_call_gender": {
            "name": "抽奖中的学生点名性别范围下拉框",
            "description": "控制是否显示抽奖中的学生点名性别范围选择框",
            "switchbutton_name": {"enable": "显示", "disable": "隐藏"},
        },
        "lottery_quantity_label": {
            "name": "数量标签",
            "description": "控制是否显示中奖数量标签",
            "switchbutton_name": {"enable": "显示", "disable": "隐藏"},
        },
        "lottery_remaining_button": {
            "name": "查看剩余名单按钮",
            "description": "控制是否显示查看剩余名单按钮",
            "switchbutton_name": {"enable": "显示", "disable": "隐藏"},
        },
        "custom_method": {
            "name": "自定义抽控制面板位置",
            "description": "设置自定义抽取控制面板显示位置",
            "combo_items": ["左侧", "右侧"],
        },
        "custom_reset_button": {
            "name": "重置自定义抽按钮",
            "description": "控制是否显示自定义抽取重置按钮",
            "switchbutton_name": {"enable": "显示", "disable": "隐藏"},
        },
        "custom_quantity_control": {
            "name": "抽取数量控制条",
            "description": "控制是否显示自定义抽取数量调整控件",
            "switchbutton_name": {"enable": "显示", "disable": "隐藏"},
        },
        "custom_start_button": {
            "name": "开始按钮",
            "description": "控制是否显示自定义抽取开始按钮",
            "switchbutton_name": {"enable": "显示", "disable": "隐藏"},
        },
        "custom_list": {
            "name": "自定义抽名单切换下拉框",
            "description": "控制是否显示自定义抽取名单切换框",
            "switchbutton_name": {"enable": "显示", "disable": "隐藏"},
        },
        "custom_range_start": {
            "name": "自定义抽范围下拉框",
            "description": "控制是否显示自定义抽取范围选择框",
            "switchbutton_name": {"enable": "显示", "disable": "隐藏"},
        },
        "custom_range_end": {
            "name": "自定义抽性别范围下拉框",
            "description": "控制是否显示自定义抽取性别范围选择框",
            "switchbutton_name": {"enable": "显示", "disable": "隐藏"},
        },
        "draw_custom_method": {
            "name": "自定义抽控制面板位置",
            "description": "控制是否显示自定义抽取控制面板位置",
            "switchbutton_name": {"enable": "显示", "disable": "隐藏"},
        },
        "custom_quantity_label": {
            "name": "数量标签",
            "description": "控制是否显示自定义抽取人数/组数的标签",
            "switchbutton_name": {"enable": "显示", "disable": "隐藏"},
        },
        "custom_remaining_button": {
            "name": "查看剩余名单按钮",
            "description": "控制是否显示查看剩余名单按钮",
            "switchbutton_name": {"enable": "显示", "disable": "隐藏"},
        },
    }
}
