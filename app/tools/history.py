# ==================================================
# 导入库
# ==================================================
import json
from datetime import datetime
from typing import Dict, List, Any

from loguru import logger

from app.tools.path_utils import get_path

# ==================================================
# 历史记录处理函数
# ==================================================


def get_class_name_history() -> List[str]:
    """获取所有有点名历史记录的班级名称列表

    Returns:
        List[str]: 班级名称列表
    """
    try:
        # 获取历史记录文件夹路径
        roll_call_history_dir = get_path("app/resources/history/roll_call_history")

        # 如果文件夹不存在，返回空列表
        if not roll_call_history_dir.exists():
            logger.warning(f"点名历史记录文件夹不存在: {roll_call_history_dir}")
            return []

        # 获取所有JSON文件
        class_files = list(roll_call_history_dir.glob("*.json"))

        # 提取班级名称（去掉文件扩展名）
        class_names = [file.stem for file in class_files]

        # 按字母顺序排序
        class_names.sort()

        return class_names

    except Exception as e:
        logger.error(f"获取班级历史记录列表失败: {e}")
        return []


def get_student_history(class_name: str) -> List[Dict[str, Any]]:
    """获取指定班级的学生历史记录

    Args:
        class_name: 班级名称

    Returns:
        List[Dict[str, Any]]: 学生历史记录列表
    """
    try:
        # 获取历史记录文件路径
        roll_call_history_dir = get_path("app/resources/history/roll_call_history")
        class_file_path = roll_call_history_dir / f"{class_name}.json"

        # 如果文件不存在，返回空列表
        if not class_file_path.exists():
            logger.warning(f"班级历史记录文件不存在: {class_file_path}")
            return []

        # 读取JSON文件
        with open(class_file_path, "r", encoding="utf-8") as f:
            history_data = json.load(f)

        # 提取学生数据
        students = []
        students_dict = history_data.get("students", {})
        if isinstance(students_dict, dict):
            for name, info in students_dict.items():
                students.append(
                    {
                        "name": name,
                        "id": info.get("id", 0),
                        "gender": info.get("gender", "未知"),
                        "group": info.get("group", "未分组"),
                        "total_count": info.get("total_count", 0),
                        "group_gender_count": info.get("group_gender_count", 0),
                        "last_drawn_time": info.get("last_drawn_time", ""),
                        "rounds_missed": info.get("rounds_missed", 0),
                        "history": info.get("history", []),
                    }
                )
        elif isinstance(students_dict, list):
            # 如果已经是列表，直接使用
            students = students_dict

        # 按ID排序
        students.sort(key=lambda x: x["id"])

        return students

    except Exception as e:
        logger.error(f"获取学生历史记录失败: {e}")
        return []


def get_draw_sessions_history(class_name: str) -> List[Dict[str, Any]]:
    """获取指定班级的抽取会话历史记录

    Args:
        class_name: 班级名称

    Returns:
        List[Dict[str, Any]]: 抽取会话历史记录列表
    """
    try:
        # 获取历史记录文件路径
        roll_call_history_dir = get_path("app/resources/history/roll_call_history")
        class_file_path = roll_call_history_dir / f"{class_name}.json"

        # 如果文件不存在，返回空列表
        if not class_file_path.exists():
            logger.warning(f"班级历史记录文件不存在: {class_file_path}")
            return []

        # 读取JSON文件
        with open(class_file_path, "r", encoding="utf-8") as f:
            history_data = json.load(f)

        # 提取抽取会话数据
        sessions = history_data.get("draw_sessions", [])

        # 按时间倒序排序（最新的在前）
        sessions.sort(key=lambda x: x.get("draw_time", ""), reverse=True)

        return sessions

    except Exception as e:
        logger.error(f"获取抽取会话历史记录失败: {e}")
        return []


def get_individual_statistics(class_name: str) -> List[Dict[str, Any]]:
    """获取指定班级的个人统计历史记录

    Args:
        class_name: 班级名称

    Returns:
        List[Dict[str, Any]]: 个人统计历史记录列表
    """
    try:
        # 获取历史记录文件路径
        roll_call_history_dir = get_path("app/resources/history/roll_call_history")
        class_file_path = roll_call_history_dir / f"{class_name}.json"

        # 如果文件不存在，返回空列表
        if not class_file_path.exists():
            logger.warning(f"班级历史记录文件不存在: {class_file_path}")
            return []

        # 读取JSON文件
        with open(class_file_path, "r", encoding="utf-8") as f:
            history_data = json.load(f)

        # 提取统计数据
        statistics = history_data.get("statistics", {})
        total_draws = statistics.get("total_draws", 0)
        group_stats = statistics.get("group_stats", {})
        gender_stats = statistics.get("gender_stats", {})

        # 创建个人统计记录
        individual_stats = []

        # 添加总体统计
        individual_stats.append(
            {
                "time": history_data.get("metadata", {}).get("last_updated", ""),
                "mode": "总体统计",
                "people_count": total_draws,
                "gender": f"男:{gender_stats.get('男', 0)} 女:{gender_stats.get('女', 0)}",
                "group": ", ".join(
                    [f"{group}:{count}" for group, count in group_stats.items()]
                ),
            }
        )

        return individual_stats

    except Exception as e:
        logger.error(f"获取个人统计历史记录失败: {e}")
        return []


def save_roll_call_history(
    class_name: str, students: List[Dict[str, Any]], draw_session: Dict[str, Any]
) -> bool:
    """保存点名历史记录

    Args:
        class_name: 班级名称
        students: 学生列表
        draw_session: 抽取会话信息

    Returns:
        bool: 保存是否成功
    """
    try:
        # 获取历史记录文件夹路径
        roll_call_history_dir = get_path("app/resources/history/roll_call_history")

        # 确保目录存在
        roll_call_history_dir.mkdir(parents=True, exist_ok=True)

        # 获取历史记录文件路径
        class_file_path = roll_call_history_dir / f"{class_name}.json"

        # 读取现有数据或创建新数据结构
        if class_file_path.exists():
            with open(class_file_path, "r", encoding="utf-8") as f:
                history_data = json.load(f)
        else:
            # 创建新的历史记录结构
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            history_data = {
                "metadata": {
                    "class_name": class_name,
                    "created_time": current_time,
                    "last_updated": current_time,
                },
                "students": {},
                "draw_sessions": [],
                "statistics": {"total_draws": 0, "group_stats": {}, "gender_stats": {}},
            }

        # 更新元数据
        history_data["metadata"]["last_updated"] = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        # 更新学生数据
        for student in students:
            name = student.get("name", "")
            if not name:
                continue

            if name not in history_data["students"]:
                # 新学生
                history_data["students"][name] = {
                    "id": student.get("id", 0),
                    "gender": student.get("gender", "未知"),
                    "group": student.get("group", "未分组"),
                    "total_count": 0,
                    "group_gender_count": 0,
                    "last_drawn_time": "",
                    "rounds_missed": 0,
                    "history": [],
                }

            # 更新学生统计
            student_data = history_data["students"][name]
            student_data["total_count"] += 1

            # 如果是按性别或小组抽取，增加特殊计数
            draw_mode = draw_session.get("draw_mode", "")
            if "性别" in draw_mode or "小组" in draw_mode:
                student_data["group_gender_count"] += 1

            student_data["last_drawn_time"] = draw_session.get("draw_time", "")

            # 添加历史记录
            student_data["history"].append(
                {
                    "draw_time": draw_session.get("draw_time", ""),
                    "draw_mode": draw_session.get("draw_mode", ""),
                    "draw_people_count": draw_session.get("draw_people_count", 0),
                    "draw_gender": draw_session.get("draw_gender", ""),
                    "draw_group": draw_session.get("draw_group", ""),
                }
            )

        # 添加抽取会话记录
        history_data["draw_sessions"].append(draw_session)

        # 更新统计数据
        history_data["statistics"]["total_draws"] += 1

        # 更新小组统计
        selected_students = draw_session.get("selected_students", [])
        for student_name in selected_students:
            if student_name in history_data["students"]:
                group = history_data["students"][student_name].get("group", "未分组")
                if group not in history_data["statistics"]["group_stats"]:
                    history_data["statistics"]["group_stats"][group] = 0
                history_data["statistics"]["group_stats"][group] += 1

                # 更新性别统计
                gender = history_data["students"][student_name].get("gender", "未知")
                if gender not in history_data["statistics"]["gender_stats"]:
                    history_data["statistics"]["gender_stats"][gender] = 0
                history_data["statistics"]["gender_stats"][gender] += 1

        # 保存到文件
        with open(class_file_path, "w", encoding="utf-8") as f:
            json.dump(history_data, f, ensure_ascii=False, indent=4)

        logger.info(f"点名历史记录已保存: {class_name}")
        return True

    except Exception as e:
        logger.error(f"保存点名历史记录失败: {e}")
        return False


def clear_roll_call_history(class_name: str) -> bool:
    """清除指定班级的点名历史记录

    Args:
        class_name: 班级名称

    Returns:
        bool: 清除是否成功
    """
    try:
        # 获取历史记录文件路径
        roll_call_history_dir = get_path("app/resources/history/roll_call_history")
        class_file_path = roll_call_history_dir / f"{class_name}.json"

        # 如果文件不存在，返回成功
        if not class_file_path.exists():
            logger.info(f"班级历史记录文件不存在，无需清除: {class_file_path}")
            return True

        # 删除文件
        class_file_path.unlink()

        logger.info(f"点名历史记录已清除: {class_name}")
        return True

    except Exception as e:
        logger.error(f"清除点名历史记录失败: {e}")
        return False
