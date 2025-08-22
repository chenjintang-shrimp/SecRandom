import os
import json
import datetime
from pathlib import Path
from loguru import logger
from functools import lru_cache
from app.common.path_utils import path_manager, open_file

@lru_cache(maxsize=None)
def _parse_time(time_str):
    try:
        return datetime.datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
    except (ValueError, TypeError):
        return None

def _clean_history(history_type, settings_key, retention_days_key, history_dir, record_keys, enabled_key):
    try:
        settings_file = path_manager.get_settings_path()
        if not path_manager.file_exists(settings_file):
            logger.warning("设置文件不存在，无法清理历史记录")
            return

        with open_file(settings_file, 'r', encoding='utf-8') as f:
            settings = json.load(f)
            retention_days = settings.get(settings_key, {}).get(retention_days_key, 0)
            history_enabled = settings.get(settings_key, {}).get(enabled_key, True)

        if not history_enabled or retention_days <= 0:
            return

        cutoff_date = datetime.datetime.now() - datetime.timedelta(days=retention_days)

        # 构建历史记录目录的绝对路径
        history_dir_abs = path_manager.get_absolute_path(history_dir)
        if not path_manager.file_exists(history_dir_abs):
            return

        for filename in os.listdir(history_dir_abs):
            if filename.endswith('.json'):
                history_file = history_dir_abs / filename
                try:
                    with open_file(history_file, 'r', encoding='utf-8') as f:
                        history_data = json.load(f)

                    for record_key in record_keys:
                        if record_key in history_data:
                            for entry in list(history_data[record_key].keys()):
                                records = history_data[record_key][entry].get('time', [])
                                valid_records = []
                                for record in records:
                                    draw_time = record.get('draw_time')
                                    parsed_time = _parse_time(draw_time)
                                    if parsed_time is None:
                                        if draw_time is None:
                                            logger.warning("解析记录时间失败: 缺少'draw_time'字段")
                                        else:
                                            logger.warning(f"解析记录时间失败: 无效格式 '{draw_time}'")
                                        valid_records.append(record)
                                    elif parsed_time >= cutoff_date:
                                        valid_records.append(record)

                                history_data[record_key][entry]['time'] = valid_records
                                if not valid_records:
                                    del history_data[record_key][entry]

                    with open_file(history_file, 'w', encoding='utf-8') as f:
                        json.dump(history_data, f, ensure_ascii=False, indent=4)

                    logger.info(f"已清理{history_type}过期历史记录: {filename}")

                except Exception as e:
                    logger.error(f"清理{history_type}历史记录文件 {filename} 时出错: {e}")

    except Exception as e:
        logger.error(f"清理过期{history_type}历史记录时出错: {e}")

def clean_expired_history():
    """清理过期的抽人/抽组历史记录"""
    _clean_history(
        history_type="抽人/抽组",
        settings_key="history",
        retention_days_key="history_days",
        history_dir="app/resource/history",
        record_keys=['pumping_people', 'pumping_group'],
        enabled_key='history_enabled'
    )

def clean_expired_reward_history():
    """清理过期的抽奖历史记录"""
    _clean_history(
        history_type="抽奖",
        settings_key="history",
        retention_days_key="history_reward_days",
        history_dir="app/resource/reward/history",
        record_keys=['pumping_reward'],
        enabled_key='reward_history_enabled'
    )