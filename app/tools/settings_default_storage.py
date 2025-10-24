from app.tools.variable import *

# ==================================================
# 默认设置列表
# ==================================================
DEFAULT_SETTINGS = {
    "home": {
        "title": {
            "default_value": None
        }
    },
    "basic_settings": {
        "title": {
            "default_value": None
        },
        "basic_function": {
            "default_value": None
        },
        "data_management": {
            "default_value": None
        },
        "personalised": {
            "default_value": None
        },
        "autostart": {
            "default_value": False
        },
        "check_update": {
            "default_value": True
        },
        "show_startup_window": {
            "default_value": True
        },
        "export_diagnostic_data": {
            "default_value": None
        },
        "export_settings": {
            "default_value": None
        },
        "import_settings": {
            "default_value": None
        },
        "export_all_data": {
            "default_value": None
        },
        "import_all_data": {
            "default_value": None
        },
        "theme": {
            "default_value": DEFAULT_THEME_COLOR
        },
        "language": {
            "default_value": "ZH_CN"
        }
    },
    "list_management": {
        "title": {
            "default_value": None
        }
    },
    "roll_call_list": {
        "title": {
            "default_value": None
        },
        "set_class_name": {
            "default_value": None
        },
        "select_class_name": {
            "default_value": 0
        },
        "import_student_name": {
            "default_value": None
        },
        "name_setting": {
            "default_value": None
        },
        "gender_setting": {
            "default_value": None
        },
        "group_setting": {
            "default_value": None
        },
        "export_student_name": {
            "default_value": None
        }
    },
    "roll_call_table": {
        "title": {
            "default_value": None
        },
        "HeaderLabels": {
            "default_value": None
        }
    },
    "custom_draw_list": {
        "title": {
            "default_value": None
        }
    },
    "lottery_list": {
        "title": {
            "default_value": None
        },
        "set_pool_name": {
            "default_value": None
        },
        "select_pool_name": {
            "default_value": 0
        },
        "import_prize_name": {
            "default_value": None
        },
        "prize_setting": {
            "default_value": None
        },
        "prize_weight_setting": {
            "default_value": None
        },
        "export_prize_name": {
            "default_value": None
        }
    },
    "lottery_table": {
        "title": {
            "default_value": None
        },
        "HeaderLabels": {
            "default_value": None
        }
    },
    "extraction_settings": {
        "title": {
            "default_value": None
        }
    },
    "roll_call_settings": {
        "title": {
            "default_value": None
        },
        "extraction_function": {
            "default_value": None
        },
        "display_settings": {
            "default_value": None
        },
        "basic_animation_settings": {
            "default_value": None
        },
        "color_theme_settings": {
            "default_value": None
        },
        "student_image_settings": {
            "default_value": None
        },
        "music_settings": {
            "default_value": None
        },
        "draw_mode": {
            "default_value": 1
        },
        "clear_record": {
            "default_value": 0
        },
        "half_repeat": {
            "default_value": 1
        },
        "clear_time": {
            "default_value": 0
        },
        "draw_type": {
            "default_value": 0
        },
        "font_size": {
            "default_value": 50
        },
        "display_format": {
            "default_value": 0
        },
        "show_random": {
            "default_value": 0
        },
        "animation": {
            "default_value": 1
        },
        "animation_interval": {
            "default_value": 80
        },
        "autoplay_count": {
            "default_value": 5
        },
        "animation_color_theme": {
            "default_value": 0
        },
        "result_color_theme": {
            "default_value": 0
        },
        "animation_fixed_color": {
            "default_value": DEFAULT_THEME_COLOR
        },
        "result_fixed_color": {
            "default_value": DEFAULT_THEME_COLOR
        },
        "student_image": {
            "default_value": False
        },
        "open_student_image_folder": {
            "default_value": None
        },
        "animation_music": {
            "default_value": False
        },
        "result_music": {
            "default_value": False
        },
        "open_animation_music_folder": {
            "default_value": None
        },
        "open_result_music_folder": {
            "default_value": None
        },
        "animation_music_volume": {
            "default_value": 30
        },
        "result_music_volume": {
            "default_value": 30
        },
        "animation_music_fade_in": {
            "default_value": 300
        },
        "result_music_fade_in": {
            "default_value": 300
        },
        "animation_music_fade_out": {
            "default_value": 300
        },
        "result_music_fade_out": {
            "default_value": 300
        }
    },
    "quick_draw_settings": {
        "title": {
            "default_value": None
        },
        "extraction_function": {
            "default_value": None
        },
        "display_settings": {
            "default_value": None
        },
        "basic_animation_settings": {
            "default_value": None
        },
        "color_theme_settings": {
            "default_value": None
        },
        "student_image_settings": {
            "default_value": None
        },
        "music_settings": {
            "default_value": None
        },
        "draw_mode": {
            "default_value": 1
        },
        "clear_record": {
            "default_value": 0
        },
        "half_repeat": {
            "default_value": 1
        },
        "clear_time": {
            "default_value": 0
        },
        "draw_type": {
            "default_value": 0
        },
        "font_size": {
            "default_value": 50
        },
        "display_format": {
            "default_value": 0
        },
        "show_random": {
            "default_value": 0
        },
        "animation": {
            "default_value": 1
        },
        "animation_interval": {
            "default_value": 80
        },
        "autoplay_count": {
            "default_value": 5
        },
        "animation_color_theme": {
            "default_value": 0
        },
        "result_color_theme": {
            "default_value": 0
        },
        "animation_fixed_color": {
            "default_value": DEFAULT_THEME_COLOR
        },
        "result_fixed_color": {
            "default_value": DEFAULT_THEME_COLOR
        },
        "student_image": {
            "default_value": False
        },
        "open_student_image_folder": {
            "default_value": None
        },
        "animation_music": {
            "default_value": False
        },
        "result_music": {
            "default_value": False
        },
        "open_animation_music_folder": {
            "default_value": None
        },
        "open_result_music_folder": {
            "default_value": None
        },
        "animation_music_volume": {
            "default_value": 30
        },
        "result_music_volume": {
            "default_value": 30
        },
        "animation_music_fade_in": {
            "default_value": 300
        },
        "result_music_fade_in": {
            "default_value": 300
        },
        "animation_music_fade_out": {
            "default_value": 300
        },
        "result_music_fade_out": {
            "default_value": 300
        }
    },
    "instant_draw_settings": {
        "title": {
            "default_value": None
        },
        "extraction_function": {
            "default_value": None
        },
        "display_settings": {
            "default_value": None
        },
        "basic_animation_settings": {
            "default_value": None
        },
        "color_theme_settings": {
            "default_value": None
        },
        "student_image_settings": {
            "default_value": None
        },
        "music_settings": {
            "default_value": None
        },
        "draw_mode": {
            "default_value": 1
        },
        "clear_record": {
            "default_value": 0
        },
        "half_repeat": {
            "default_value": 1
        },
        "clear_time": {
            "default_value": 0
        },
        "draw_type": {
            "default_value": 0
        },
        "font_size": {
            "default_value": 50
        },
        "display_format": {
            "default_value": 0
        },
        "show_random": {
            "default_value": 0
        },
        "animation": {
            "default_value": 1
        },
        "animation_interval": {
            "default_value": 80
        },
        "autoplay_count": {
            "default_value": 5
        },
        "animation_color_theme": {
            "default_value": 0
        },
        "result_color_theme": {
            "default_value": 0
        },
        "animation_fixed_color": {
            "default_value": DEFAULT_THEME_COLOR
        },
        "result_fixed_color": {
            "default_value": DEFAULT_THEME_COLOR
        },
        "student_image": {
            "default_value": False
        },
        "open_student_image_folder": {
            "default_value": None
        },
        "animation_music": {
            "default_value": False
        },
        "result_music": {
            "default_value": False
        },
        "open_animation_music_folder": {
            "default_value": None
        },
        "open_result_music_folder": {
            "default_value": None
        },
        "animation_music_volume": {
            "default_value": 30
        },
        "result_music_volume": {
            "default_value": 30
        },
        "animation_music_fade_in": {
            "default_value": 300
        },
        "result_music_fade_in": {
            "default_value": 300
        },
        "animation_music_fade_out": {
            "default_value": 300
        },
        "result_music_fade_out": {
            "default_value": 300
        }
    },
    "custom_draw_settings": {
        "title": {
            "default_value": None
        }
    },
    "lottery_settings": {
        "title": {
            "default_value": None
        },
        "extraction_function": {
            "default_value": None
        },
        "display_settings": {
            "default_value": None
        },
        "basic_animation_settings": {
            "default_value": None
        },
        "color_theme_settings": {
            "default_value": None
        },
        "student_image_settings": {
            "default_value": None
        },
        "music_settings": {
            "default_value": None
        },
        "draw_mode": {
            "default_value": 1
        },
        "clear_record": {
            "default_value": 0
        },
        "half_repeat": {
            "default_value": 1
        },
        "clear_time": {
            "default_value": 0
        },
        "draw_type": {
            "default_value": 0
        },
        "font_size": {
            "default_value": 50
        },
        "display_format": {
            "default_value": 0
        },
        "animation": {
            "default_value": 1
        },
        "animation_interval": {
            "default_value": 80
        },
        "autoplay_count": {
            "default_value": 5
        },
        "animation_color_theme": {
            "default_value": 0
        },
        "result_color_theme": {
            "default_value": 0
        },
        "animation_fixed_color": {
            "default_value": DEFAULT_THEME_COLOR
        },
        "result_fixed_color": {
            "default_value": DEFAULT_THEME_COLOR
        },
        "lottery_image": {
            "default_value": False
        },
        "open_lottery_image_folder": {
            "default_value": None
        },
        "animation_music": {
            "default_value": False
        },
        "result_music": {
            "default_value": False
        },
        "open_animation_music_folder": {
            "default_value": None
        },
        "open_result_music_folder": {
            "default_value": None
        },
        "animation_music_volume": {
            "default_value": 30
        },
        "result_music_volume": {
            "default_value": 30
        },
        "animation_music_fade_in": {
            "default_value": 300
        },
        "result_music_fade_in": {
            "default_value": 300
        },
        "animation_music_fade_out": {
            "default_value": 300
        },
        "result_music_fade_out": {
            "default_value": 300
        }
    },
    "safety_settings": {
        "title": {
            "default_value": None
        }
    },
    "basic_safety_settings": {
        "title": {
            "default_value": None
        },
        "verification_method": {
            "default_value": None
        },
        "verification_process": {
            "default_value": 0
        },
        "security_operations": {
            "default_value": None
        },
        "safety_switch": {
            "default_value": False
        },
        "set_password": {
            "default_value": None
        },
        "totp_switch": {
            "default_value": False
        },
        "set_totp": {
            "default_value": None
        },
        "usb_switch": {
            "default_value": False
        },
        "bind_usb": {
            "default_value": None
        },
        "unbind_usb": {
            "default_value": None
        },
        "show_hide_floating_window_switch": {
            "default_value": False
        },
        "restart_switch": {
            "default_value": False
        },
        "exit_switch": {
            "default_value": False
        }
    },
    "advanced_safety_settings": {
        "title": {
            "default_value": None
        },
        "strong_protection": {
            "default_value": None
        },
        "data_encryption": {
            "default_value": None
        },
        "encryption_strong_switch": {
            "default_value": False
        },
        "encryption_strong_mode": {
            "default_value": 0
        },
        "strong_list_switch": {
            "default_value": False
        },
        "strong_history_switch": {
            "default_value": False
        },
        "strong_temp_switch": {
            "default_value": False
        },
        "encryption_list_switch": {
            "default_value": False
        },
        "encryption_history_switch": {
            "default_value": False
        },
        "encryption_temp_switch": {
            "default_value": False
        }
    },
    "custom_settings": {
        "title": {
            "default_value": None
        }
    },
    "page_management": {
        "title": {
            "default_value": None
        },
        "roll_call": {
            "default_value": None
        },
        "lottery": {
            "default_value": None
        },
        "roll_call_method": {
            "default_value": 1
        },
        "show_name": {
            "default_value": False
        },
        "reset_roll_call": {
            "default_value": True
        },
        "roll_call_quantity_control": {
            "default_value": True
        },
        "roll_call_start_button": {
            "default_value": True
        },
        "roll_call_list": {
            "default_value": True
        },
        "roll_call_range": {
            "default_value": True
        },
        "roll_call_gender": {
            "default_value": True
        },
        "roll_call_quantity_label": {
            "default_value": True
        },
        "lottery_method": {
            "default_value": 1
        },
        "show_lottery_name": {
            "default_value": False
        },
        "reset_lottery": {
            "default_value": True
        },
        "lottery_quantity_control": {
            "default_value": True
        },
        "lottery_start_button": {
            "default_value": True
        },
        "lottery_list": {
            "default_value": True
        },
        "lottery_quantity_label": {
            "default_value": True
        }
    },
    "about": {
        "title": {
            "default_value": None
        },
        "github": {
            "default_value": None
        },
        "bilibili": {
            "default_value": None
        },
        "contributor": {
            "default_value": None
        },
        "donation": {
            "default_value": None
        },
        "check_update": {
            "default_value": None
        },
        "website": {
            "default_value": None
        },
        "channel": {
            "default_value": 0
        },
        "copyright": {
            "default_value": None
        },
        "version": {
            "default_value": None
        }
    }
}
