# ==================================================
# 导入库
# ==================================================
import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from pathlib import Path

from loguru import logger
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtNetwork import *
from qfluentwidgets import *

from app.tools.variable import *
from app.tools.path_utils import *
from app.tools.personalised import *
from app.tools.settings_default import *
from app.tools.settings_access import *
from app.Language.obtain_language import *

# ==================================================
# 历史记录处理函数
# ==================================================

def get_history_file_path(history_type: str, file_name: str) -> Path:
    """获取历史记录文件路径
    
    Args:
        history_type: 历史记录类型 (roll_call, lottery 等)
        file_name: 文件名（不含扩展名）
        
    Returns:
        Path: 历史记录文件路径
    """
    history_dir = get_path(f"app/resources/history/{history_type}_history")
    history_dir.mkdir(parents=True, exist_ok=True)
    return history_dir / f"{file_name}.json"

def load_history_data(history_type: str, file_name: str) -> Dict[str, Any]:
    """加载历史记录数据
    
    Args:
        history_type: 历史记录类型 (roll_call, lottery 等)
        file_name: 文件名（不含扩展名）
        
    Returns:
        Dict[str, Any]: 历史记录数据
    """
    file_path = get_history_file_path(history_type, file_name)
    
    if not file_path.exists():
        return {}
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"加载历史记录数据失败: {e}")
        return {}

def save_history_data(history_type: str, file_name: str, data: Dict[str, Any]) -> bool:
    """保存历史记录数据
    
    Args:
        history_type: 历史记录类型 (roll_call, lottery 等)
        file_name: 文件名（不含扩展名）
        data: 要保存的数据
        
    Returns:
        bool: 保存是否成功
    """
    file_path = get_history_file_path(history_type, file_name)
    
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        logger.error(f"保存历史记录数据失败: {e}")
        return False

def get_all_history_names(history_type: str) -> List[str]:
    """获取所有历史记录名称列表
    
    Args:
        history_type: 历史记录类型 (roll_call, lottery 等)
        
    Returns:
        List[str]: 历史记录名称列表
    """
    try:
        history_dir = get_path(f"app/resources/history/{history_type}_history")
        
        if not history_dir.exists():
            return []
        
        # 获取所有JSON文件
        history_files = list(history_dir.glob("*.json"))
        
        # 提取名称（去掉文件扩展名）
        names = [file.stem for file in history_files]
        
        # 按字母顺序排序
        names.sort()
        
        return names
    
    except Exception as e:
        logger.error(f"获取历史记录名称列表失败: {e}")
        return []

def clear_history(history_type: str, file_name: str) -> bool:
    """清除指定历史记录
    
    Args:
        history_type: 历史记录类型 (roll_call, lottery 等)
        file_name: 文件名（不含扩展名）
        
    Returns:
        bool: 清除是否成功
    """
    file_path = get_history_file_path(history_type, file_name)
    
    try:
        if file_path.exists():
            file_path.unlink()
        return True
    except Exception as e:
        logger.error(f"清除历史记录失败: {e}")
        return False

def calculate_weight(students: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """计算学生的权重
    
    Args:
        students: 学生列表
        base_weight: 基础权重值
        
    Returns:
        List[Dict[str, Any]]: 包含权重的学生列表
    """
    base_weight = 1.0
    
    total_draws = sum(student.get('total_count', 0) for student in students)
    if total_draws == 0:
        for student in students:
            student['next_weight'] = base_weight
        return students

    max_count = max(student.get('total_count', 0) for student in students)
    for student in students:
        count = student.get('total_count', 0)
        student['next_weight'] = (max_count - count + 1) * base_weight
    
    return students

def format_table_item(value: Union[str, int, float], is_percentage: bool = False) -> str:
    """格式化表格项显示值
    
    Args:
        value: 要格式化的值
        is_percentage: 是否为百分比值
        
    Returns:
        str: 格式化后的字符串
    """
    if isinstance(value, (int, float)):
        if is_percentage:
            return f"{value:.2%}"
        else:
            return f"{value:.2f}"
    return str(value)

def create_table_item(value: Union[str, int, float], 
                     font_size: int = 12, 
                     is_centered: bool = True,
                     is_percentage: bool = False) -> 'QTableWidgetItem':
    """创建表格项
    
    Args:
        value: 要显示的值
        font_size: 字体大小
        is_centered: 是否居中
        is_percentage: 是否为百分比值
        
    Returns:
        QTableWidgetItem: 表格项对象
    """
    # 格式化显示值
    display_value = format_table_item(value, is_percentage)
    
    # 创建表格项
    item = QTableWidgetItem(display_value)
    
    # 设置字体
    from app.tools.personalised import load_custom_font
    item.setFont(QFont(load_custom_font(), font_size))
    
    # 设置对齐方式
    if is_centered:
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
    
    # 设置不可编辑
    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
    
    return item

def get_student_history(class_name: str) -> List[Dict[str, Any]]:
    """获取指定班级的学生历史记录
    
    Args:
        class_name: 班级名称
        
    Returns:
        List[Dict[str, Any]]: 学生历史记录列表
    """
    # 加载历史记录数据
    history_data = load_history_data("roll_call", class_name)
    students = []
    students_dict = history_data.get("students", {})
    if isinstance(students_dict, dict):
        for name, info in students_dict.items():
            students.append({
                "name": name,
                "gender": info.get("gender", "未知"),
                "group": info.get("group", "未分组"),
                "total_count": info.get("total_count", 0),
                "group_gender_count": info.get("group_gender_count", 0),
                "last_drawn_time": info.get("last_drawn_time", ""),
                "rounds_missed": info.get("rounds_missed", 0),
                "history": info.get("history", [])
            })
    elif isinstance(students_dict, list):
        students = students_dict
    return students

def get_draw_sessions_history(class_name: str) -> List[Dict[str, Any]]:
    """获取指定班级的抽取会话历史记录
    
    Args:
        class_name: 班级名称
        
    Returns:
        List[Dict[str, Any]]: 抽取会话历史记录列表
    """
    # 加载历史记录数据
    history_data = load_history_data("roll_call", class_name)
    sessions = []
    students_dict = history_data.get("students", {})
    if isinstance(students_dict, dict):
        for student_name, student_info in students_dict.items():
            session_list = student_info.get("history", [])
            for session_info in session_list:
                if isinstance(session_info, dict):
                    sessions.append({
                        "draw_time": session_info.get("draw_time", ""),
                        "draw_method": session_info.get("draw_method", ""),
                    "draw_people_numbers": session_info.get("draw_people_numbers", 0),
                    "draw_group": session_info.get("draw_group", ""),
                    "draw_gender": session_info.get("draw_gender", ""),
                    "draw_people": session_info.get("draw_people", [])
                })
    if not isinstance(sessions, list):
        sessions = []
    sessions.sort(key=lambda x: x.get("draw_time", ""), reverse=True)
    return sessions

def get_individual_statistics(class_name: str) -> List[Dict[str, Any]]:
    """获取指定班级的个人统计记录
    
    Args:
        class_name: 班级名称
        
    Returns:
        List[Dict[str, Any]]: 个人统计记录列表
    """
    history_data = load_history_data("roll_call", class_name)
    individual_stats = []
    students_dict = history_data.get("students", {})
    if isinstance(students_dict, dict):
        for student_name, student_info in students_dict.items():
            individual_stats.append({
                "name": student_name,
                "gender": student_info.get("gender", "未知"),
                "group": student_info.get("group", "未分组"),
                "total_count": student_info.get("total_count", 0),
                "last_drawn_time": student_info.get("last_drawn_time", ""),
                "group_gender_count": student_info.get("group_gender_count", 0),
                "rounds_missed": student_info.get("rounds_missed", 0)
            })
    if not isinstance(individual_stats, list):
        individual_stats = []
    return individual_stats

def save_roll_call_history(class_name: str, students: List[Dict[str, Any]], 
                          selected_students: List[Dict[str, Any]], 
                          mode: str = "随机", count: int = 1,
                          random_method: str = "uniform", 
                          probability_weight_method: str = "equal") -> bool:
    """保存点名历史记录
    
    Args:
        class_name: 班级名称
        students: 所有学生列表
        selected_students: 被选中的学生列表
        mode: 点名模式
        count: 点名人数
        random_method: 随机方法
        probability_weight_method: 概率权重方法
        
    Returns:
        bool: 保存是否成功
    """
    try:
        # 获取当前时间
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 加载现有历史记录
        history_data = load_history_data("roll_call", class_name)
        
        # 更新元数据
        if "metadata" not in history_data:
            history_data["metadata"] = {}
        history_data["metadata"]["last_updated"] = current_time
        
        # 更新学生数据
        if "students" not in history_data:
            history_data["students"] = {}
        
        # 更新所有学生的信息
        for student in students:
            student_name = student.get("name", "")
            if not student_name:
                continue
                
            if student_name not in history_data["students"]:
                history_data["students"][student_name] = {
                    "id": student.get("id", 0),
                    "gender": student.get("gender", "未知"),
                    "group": student.get("group", "未分组"),
                    "total_count": 0,
                    "group_gender_count": 0,
                    "last_drawn_time": "",
                    "rounds_missed": 0,
                    "history": []
                }
            
            # 如果学生被选中，更新其信息
            is_selected = any(s.get("name") == student_name for s in selected_students)
            if is_selected:
                history_data["students"][student_name]["total_count"] += 1
                history_data["students"][student_name]["last_drawn_time"] = current_time
                history_data["students"][student_name]["history"].append(current_time)
        
        # 更新未被选中的学生的未选中次数
        selected_names = [s.get("name") for s in selected_students]
        for student_name, student_data in history_data["students"].items():
            if student_name not in selected_names:
                student_data["rounds_missed"] += 1
        
        # 添加会话记录
        if "sessions" not in history_data:
            history_data["sessions"] = []
        
        session_record = {
            "draw_time": current_time,
            "mode": mode,
            "count": count,
            "random_method": random_method,
            "probability_weight_method": probability_weight_method,
            "selected_students": [
                {
                    "name": s.get("name", ""),
                    "id": s.get("id", 0),
                    "gender": s.get("gender", "未知"),
                    "group": s.get("group", "未分组")
                } for s in selected_students
            ]
        }
        history_data["sessions"].append(session_record)
        
        # 添加个人统计记录
        if "individual_stats" not in history_data:
            history_data["individual_stats"] = []
        
        # 统计性别和小组
        gender_count = {"男": 0, "女": 0, "未知": 0}
        group_count = {}
        for student in selected_students:
            gender = student.get("gender", "未知")
            group = student.get("group", "未分组")
            
            gender_count[gender] = gender_count.get(gender, 0) + 1
            group_count[group] = group_count.get(group, 0) + 1
        
        individual_stat = {
            "time": current_time,
            "mode": mode,
            "people_count": len(selected_students),
            "gender": f"男:{gender_count.get('男', 0)} 女:{gender_count.get('女', 0)}",
            "group": ", ".join([f"{group}:{count}" for group, count in group_count.items()])
        }
        history_data["individual_stats"].append(individual_stat)
        
        # 保存历史记录
        return save_history_data("roll_call", class_name, history_data)
    
    except Exception as e:
        logger.error(f"保存点名历史记录失败: {e}")
        return False
