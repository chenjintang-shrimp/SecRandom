# 语音设置语言配置
voice_settings = {
    "ZH_CN": {"title": {"name": "语音设置", "description": "语音设置页面"}}
}

# 基础语音设置语言配置
basic_voice_settings = {
    "ZH_CN": {
        "title": {"name": "基础语音设置", "description": "基础语音设置"},
        "voice_engine_group": {"name": "语音引擎", "description": "选择语音合成引擎"},
        "volume_group": {"name": "音量设置", "description": "设置语音播放的音量大小"},
        "system_volume_group": {
            "name": "系统音量控制",
            "description": "选择要控制的系统音量类型",
        },
        "voice_engine": {
            "name": "语音引擎",
            "description": "选择语音合成引擎",
            "combo_items": ["系统TTS", "Edge TTS"],
        },
        "edge_tts_voice_name": {
            "name": "Edge TTS-语音名称",
            "description": "选择Edge TTS语音",
            "combo_items": [
                "zh-CN-XiaoxiaoNeural",
                "zh-CN-YunxiNeural",
                "zh-CN-XiaoyiNeural",
                "en-US-JennyNeural",
                "en-US-GuyNeural",
            ],
        },
        "voice_playback": {
            "name": "语音播放",
            "description": "选择语音播放设备",
            "combo_items": ["系统默认", "扬声器", "耳机", "蓝牙设备"],
        },
        "volume_size": {"name": "音量大小", "description": "设置语音播放的音量大小"},
        "speech_rate": {"name": "语速调节", "description": "设置语音播放的语速"},
        "system_volume_control": {
            "name": "系统音量控制",
            "description": "选择要控制的系统音量类型",
            "combo_items": ["主音量", "应用音量", "系统音效", "麦克风音量"],
        },
        "system_volume_size": {
            "name": "系统音量大小",
            "description": "设置系统音量大小",
        },
    }
}
