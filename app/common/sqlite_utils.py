import sqlite3
from datetime import datetime
import os
import json
from loguru import logger

class SQLiteHistoryManager:
    """
    SQLite历史记录管理工具类
    """
    def __init__(self, db_path='app/resource/history/history.db'):
        """
        初始化数据库连接
        :param db_path: 数据库文件路径
        """
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """初始化数据库表结构"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 创建学生抽取历史表
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS student_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                class_name TEXT NOT NULL,
                student_name TEXT NOT NULL,
                student_id TEXT,
                student_group TEXT,
                student_gender TEXT,
                draw_method TEXT NOT NULL,
                draw_time TEXT NOT NULL,
                draw_count INTEGER NOT NULL,
                draw_group TEXT,
                draw_gender TEXT,
                UNIQUE(class_name, student_name, draw_time)
            )
            ''')
            
            # 创建奖品抽取历史表
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS reward_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                reward_pool TEXT NOT NULL,
                reward_name TEXT NOT NULL,
                reward_id TEXT,
                draw_method TEXT NOT NULL,
                draw_time TEXT NOT NULL,
                draw_count INTEGER NOT NULL,
                UNIQUE(reward_pool, reward_name, draw_time)
            )
            ''')
            
            # 创建统计信息表
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT NOT NULL,  -- 'student' or 'reward'
                class_or_pool TEXT NOT NULL,
                name TEXT NOT NULL,
                value INTEGER NOT NULL,
                last_updated TEXT NOT NULL,
                UNIQUE(type, class_or_pool, name)
            )
            ''')
            
            conn.commit()
    
    def add_student_history(self, class_name, student_name, student_id=None, student_group=None, 
                          student_gender=None, draw_method='random', draw_count=1, 
                          draw_group=None, draw_gender=None):
        """
        添加学生抽取历史记录
        """
        draw_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 插入历史记录
            cursor.execute('''
            INSERT OR REPLACE INTO student_history (
                class_name, student_name, student_id, student_group, student_gender,
                draw_method, draw_time, draw_count, draw_group, draw_gender
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                class_name, student_name, student_id, student_group, student_gender,
                draw_method, draw_time, draw_count, draw_group, draw_gender
            ))
            
            # 更新小组统计
            if student_group:
                self._update_stat(conn, 'student', class_name, f'group_{student_group}', 1)
            
            # 更新性别统计
            if student_gender:
                self._update_stat(conn, 'student', class_name, f'gender_{student_gender}', 1)
            
            # 更新学生个人统计
            self._update_stat(conn, 'student', class_name, f'student_{student_name}', 1)
            
            # 更新总轮次
            self._update_stat(conn, 'student', class_name, 'total_rounds', 1)
            
            conn.commit()
    
    def add_reward_history(self, reward_pool, reward_name, reward_id=None, draw_method='random', draw_count=1):
        """
        添加奖品抽取历史记录
        """
        draw_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 插入历史记录
            cursor.execute('''
            INSERT OR REPLACE INTO reward_history (
                reward_pool, reward_name, reward_id, draw_method, draw_time, draw_count
            ) VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                reward_pool, reward_name, reward_id, draw_method, draw_time, draw_count
            ))
            
            # 更新奖品统计
            self._update_stat(conn, 'reward', reward_pool, f'reward_{reward_name}', 1)
            
            # 更新总轮次
            self._update_stat(conn, 'reward', reward_pool, 'total_rounds', 1)
            
            conn.commit()
    
    def _update_stat(self, conn, stat_type, class_or_pool, name, increment=1):
        """
        更新统计信息
        """
        cursor = conn.cursor()
        
        # 检查是否已有记录
        cursor.execute('''
        SELECT value FROM stats 
        WHERE type = ? AND class_or_pool = ? AND name = ?
        ''', (stat_type, class_or_pool, name))
        
        result = cursor.fetchone()
        current_value = result[0] + increment if result else increment
        
        # 更新或插入记录
        cursor.execute('''
        INSERT OR REPLACE INTO stats (type, class_or_pool, name, value, last_updated)
        VALUES (?, ?, ?, ?, ?)
        ''', (
            stat_type, class_or_pool, name, current_value, 
            datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ))
    
    def get_student_history(self, class_name, student_name=None):
        """
        获取学生抽取历史记录
        :param class_name: 班级名称
        :param student_name: 学生姓名(可选)
        :return: 历史记录列表
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if student_name:
                # 获取特定学生的历史记录
                cursor.execute('''
                SELECT * FROM student_history
                WHERE class_name = ? AND student_name = ?
                ORDER BY draw_time DESC
                ''', (class_name, student_name))
            else:
                # 获取全班学生的历史记录
                cursor.execute('''
                SELECT * FROM student_history
                WHERE class_name = ?
                ORDER BY draw_time DESC
                ''', (class_name,))
            
            return cursor.fetchall()
    
    def get_reward_history(self, reward_pool, reward_name=None):
        """
        获取奖品抽取历史记录
        :param reward_pool: 奖池名称
        :param reward_name: 奖品名称(可选)
        :return: 历史记录列表
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if reward_name:
                # 获取特定奖品的历史记录
                cursor.execute("""
                SELECT * FROM reward_history
                WHERE reward_pool = ? AND reward_name = ?
                ORDER BY draw_time DESC
                """, (reward_pool, reward_name))
            else:
                # 获取全部奖品的历史记录
                cursor.execute("""
                SELECT * FROM reward_history
                WHERE reward_pool = ?
                ORDER BY draw_time DESC
                """, (reward_pool,))
            
            return cursor.fetchall()
    
    def get_student_stats(self, class_name):
        """
        获取学生统计信息
        :param class_name: 班级名称
        :return: 统计信息字典
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # 🌸 小鸟游星野提醒：获取所有学生统计信息
            cursor.execute("""
            SELECT name, value FROM stats
            WHERE type = 'student' AND class_or_pool = ?
            """, (class_name,))
            
            stats = {}
            group_stats = {}
            gender_stats = {}
            total_rounds = 0
            
            for row in cursor.fetchall():
                name = row['name']
                value = row['value']
                
                # ✨ 星穹铁道白露提示：处理学生个人统计
                if name.startswith('student_'):
                    try:
                        # 尝试解析存储的JSON数据
                        if isinstance(value, str):
                            value_data = json.loads(value)
                        elif isinstance(value, dict):
                            value_data = value
                        else:
                            value_data = {'total_number_of_times': int(value), 'total_number_auxiliary': 0}
                        
                        # 💫 确保字典结构完整
                        stats[name] = {
                            'total_number_of_times': int(value_data.get('total_number_of_times', 0)),
                            'total_number_auxiliary': int(value_data.get('total_number_auxiliary', 0))
                        }
                    except (json.JSONDecodeError, ValueError):
                        # 🌟 处理旧数据格式
                        stats[name] = {
                            'total_number_of_times': int(value) if value else 0,
                            'total_number_auxiliary': 0
                        }
                
                # 🌸 获取小组统计
                elif name.startswith('group_'):
                    group_name = name.replace('group_', '', 1)
                    try:
                        group_stats[group_name] = int(value) if value else 0
                    except (ValueError, TypeError):
                        group_stats[group_name] = 0
                
                # ✨ 获取性别统计
                elif name.startswith('gender_'):
                    gender_name = name.replace('gender_', '', 1)
                    try:
                        gender_stats[gender_name] = int(value) if value else 0
                    except (ValueError, TypeError):
                        gender_stats[gender_name] = 0
                
                # 💫 获取总轮次
                elif name == 'total_rounds':
                    try:
                        total_rounds = int(value) if value else 0
                    except (ValueError, TypeError):
                        total_rounds = 0
            
            # 🌟 返回完整的统计信息
            stats.update({
                'group_stats': group_stats,
                'gender_stats': gender_stats,
                'total_rounds': total_rounds
            })
            
            return stats
    
    def get_reward_stats(self, reward_pool):
        """
        获取奖品统计信息
        :param reward_pool: 奖池名称
        :return: 统计信息字典
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
            SELECT name, value FROM stats
            WHERE type = 'reward' AND class_or_pool = ?
            """, (reward_pool,))
            
            stats = {}
            for row in cursor.fetchall():
                stats[row['name']] = row['value']
            
            return stats
    
    def get_drawn_students(self, class_name, group_name=None, gender=None, draw_mode=None):
        """
        获取已抽取的学生名单
        :param class_name: 班级名称
        :param group_name: 小组名称(可选)
        :param gender: 性别(可选)
        :param draw_mode: 抽取模式(可选)
        :return: 已抽取学生名单列表
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = lambda cursor, row: row[0]
            cursor = conn.cursor()
            
            query = """
            SELECT DISTINCT student_name FROM student_history
            WHERE class_name = ?
            """
            params = [class_name]
            
            if group_name:
                query += " AND draw_group = ?"
                params.append(group_name)
                
            if gender:
                query += " AND draw_gender = ?"
                params.append(gender)
                
            if draw_mode:
                query += " AND draw_method = ?"
                params.append(draw_mode)
                
            cursor.execute(query, params)
            return cursor.fetchall()
            
    def get_drawn_rewards(self, prize_pool, draw_mode=None):
        """
        获取已抽取的奖品名单
        :param prize_pool: 奖池名称
        :param draw_mode: 抽取模式(可选)
        :return: 已抽取奖品名单列表
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = lambda cursor, row: row[0]
            cursor = conn.cursor()
            
            query = """
            SELECT DISTINCT reward_name FROM reward_history
            WHERE reward_pool = ?
            """
            params = [prize_pool]
            
            if draw_mode:
                query += " AND draw_method = ?"
                params.append(draw_mode)
                
            cursor.execute(query, params)
            return cursor.fetchall()

    def increment_rounds_missed(self, class_name, student_names):
        """
        # 小鸟游星野提醒：增加未选中学生的rounds_missed计数
        :param class_name: 班级名称
        :param student_names: 未选中学生名单
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            for student_name in student_names:
                # 星穹铁道白露提示：更新未选中学生的轮次计数
                cursor.execute('''
                UPDATE stats SET value = value + 1 
                WHERE type = 'student' AND class_or_pool = ? AND name = ?
                ''', (class_name, f'student_{student_name}'))
            conn.commit()

    def close(self):
        """关闭数据库连接"""
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()

# 单例模式
history_manager = SQLiteHistoryManager()