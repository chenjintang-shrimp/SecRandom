# ==================================================
# 导入模块
# ==================================================
import os
import json
from pathlib import Path
from typing import List, Dict, Any
from loguru import logger

from app.tools.path_utils import *

# ==================================================
# 班级列表管理函数
# ==================================================
def get_class_name_list() -> List[str]:
    """获取班级名称列表
    
    从 app/resources/list/roll_call_list 文件夹中读取所有班级名单文件，
    并返回班级名称列表
    
    Returns:
        List[str]: 班级名称列表
    """
    try:
        # 获取班级名单文件夹路径
        roll_call_list_dir = get_path("app/resources/list/roll_call_list")
        
        # 如果文件夹不存在，创建文件夹
        if not roll_call_list_dir.exists():
            logger.warning(f"班级名单文件夹不存在: {roll_call_list_dir}")
            roll_call_list_dir.mkdir(parents=True, exist_ok=True)
            return []
        
        # 获取文件夹中的所有文件
        class_files = []
        for file_path in roll_call_list_dir.glob("*.json"):
            # 获取文件名（不带扩展名）作为班级名称
            class_name = file_path.stem
            class_files.append(class_name)
        
        # 按字母顺序排序
        class_files.sort()
        
        # logger.debug(f"找到 {len(class_files)} 个班级: {class_files}")
        return class_files
    
    except Exception as e:
        logger.error(f"获取班级列表失败: {e}")
        return []

def get_student_list(class_name: str) -> List[Dict[str, Any]]:
    """获取指定班级的学生列表
    
    从 app/resources/list/roll_call_list 文件夹中读取指定班级的名单文件，
    并返回学生列表
    
    Args:
        class_name: 班级名称
        
    Returns:
        List[Dict[str, Any]]: 学生列表，每个学生是一个字典，包含姓名、ID、性别、小组等信息
    """
    try:
        # 获取班级名单文件路径
        roll_call_list_dir = get_path("app/resources/list/roll_call_list")
        class_file_path = roll_call_list_dir / f"{class_name}.json"
        
        # 如果文件不存在，返回空列表
        if not class_file_path.exists():
            logger.warning(f"班级名单文件不存在: {class_file_path}")
            return []
        
        # 读取JSON文件
        with open(class_file_path, 'r', encoding='utf-8') as f:
            student_data = json.load(f)
        
        # 将字典数据转换为列表形式
        student_list = []
        for name, info in student_data.items():
            student = {
                "name": name,
                "id": info.get("id", 0),
                "gender": info.get("gender", "未知"),
                "group": info.get("group", "未分组"),
                "exist": info.get("exist", True)
            }
            student_list.append(student)
        
        # 按ID排序
        student_list.sort(key=lambda x: x["id"])
        
        # logger.debug(f"班级 {class_name} 共有 {len(student_list)} 名学生")
        return student_list
    
    except Exception as e:
        logger.error(f"获取学生列表失败: {e}")
        return []

# ==================================================
# 奖池列表管理函数
# ==================================================
def get_pool_name_list() -> List[str]:
    """获取奖池名称列表
    
    从 app/resources/list/lottery_list 文件夹中读取所有奖池名单文件，
    并返回奖池名称列表
    
    Returns:
        List[str]: 奖池名称列表
    """
    try:
        # 获取奖池名单文件夹路径
        lottery_list_dir = get_path("app/resources/list/lottery_list")
        
        # 如果文件夹不存在，创建文件夹
        if not lottery_list_dir.exists():
            logger.warning(f"奖池名单文件夹不存在: {lottery_list_dir}")
            lottery_list_dir.mkdir(parents=True, exist_ok=True)
            return []
        
        # 获取文件夹中的所有文件
        pool_files = []
        for file_path in lottery_list_dir.glob("*.json"):
            # 获取文件名（不带扩展名）作为奖池名称
            pool_name = file_path.stem
            pool_files.append(pool_name)
        
        # 按字母顺序排序
        pool_files.sort()
        
        # logger.debug(f"找到 {len(pool_files)} 个奖池: {pool_files}")
        return pool_files
    
    except Exception as e:
        logger.error(f"获取奖池列表失败: {e}")
        return []

def get_pool_data(pool_name: str) -> Dict[str, Any]:
    """获取指定奖池的数据
    
    从 app/resources/list/lottery_list 文件夹中读取指定奖池的名单文件，
    并返回奖池数据
    
    Args:
        pool_name: 奖池名称
        
    Returns:
        Dict[str, Any]: 奖池数据，包含奖品名称、权重、是否存在等信息
    """
    try:
        # 获取奖池名单文件路径
        lottery_list_dir = get_path("app/resources/list/lottery_list")
        pool_file_path = lottery_list_dir / f"{pool_name}.json"
        
        # 如果文件不存在，返回空字典
        if not pool_file_path.exists():
            logger.warning(f"奖池名单文件不存在: {pool_file_path}")
            return {}
        
        # 读取JSON文件
        with open(pool_file_path, 'r', encoding='utf-8') as f:
            pool_data = json.load(f)
        
        # 将字典数据转换为列表形式
        pool_list = []
        for name, info in pool_data.items():
            pool = {
                "name": name,
                "id": info.get("id", 0),
                "weight": info.get("weight", 1),
                "exist": info.get("exist", True)
            }
            pool_list.append(pool)
        
        # 按ID排序
        pool_list.sort(key=lambda x: x["id"])
        
        # logger.debug(f"奖池 {pool_name} 共有 {len(pool_list)} 个奖品")
        return pool_list
    
    except Exception as e:
        logger.error(f"获取奖池数据失败: {e}")
        return []

def get_pool_list(pool_name: str) -> List[Dict[str, Any]]:
    """获取指定奖池的奖品列表
    
    从 app/resources/list/lottery_list 文件夹中读取指定奖池的名单文件，
    并返回奖品列表
    
    Args:
        pool_name: 奖池名称
        
    Returns:
        List[Dict[str, Any]]: 奖品列表，每个奖品是一个字典，包含名称、ID、权重等信息
    """
    try:
        # 获取奖池名单文件路径
        lottery_list_dir = get_path("app/resources/list/lottery_list")
        pool_file_path = lottery_list_dir / f"{pool_name}.json"
        
        # 如果文件不存在，返回空列表
        if not pool_file_path.exists():
            logger.warning(f"奖池名单文件不存在: {pool_file_path}")
            return []
        
        # 读取JSON文件
        with open(pool_file_path, 'r', encoding='utf-8') as f:
            pool_data = json.load(f)
        
        # 将字典数据转换为列表形式
        pool_list = []
        for name, info in pool_data.items():
            pool = {
                "name": name,
                "id": info.get("id", 0),
                "weight": info.get("weight", 1),
                "exist": info.get("exist", True)
            }
            pool_list.append(pool)
        
        # 按ID排序
        pool_list.sort(key=lambda x: x["id"])
        
        # logger.debug(f"奖池 {pool_name} 共有 {len(pool_list)} 个奖品")
        return pool_list
    
    except Exception as e:
        logger.error(f"获取奖池列表失败: {e}")
        return []