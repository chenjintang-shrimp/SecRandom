from qfluentwidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import os
from datetime import datetime
import math
import json
from loguru import logger

from app.common.config import cfg, AUTHOR, VERSION, YEAR
from app.common.config import load_custom_font
from app.common.path_utils import path_manager, open_file, remove_file

from app.common.history_reward_settings import history_reward_SettinsCard

class RewardDataLoader(QThread):
    """奖品历史记录数据加载线程"""
    data_loaded = pyqtSignal(str, str, list)  # prize_pools_name, reward_name, data
    error_occurred = pyqtSignal(str)  # error_message
    
    def __init__(self, history_setting_card):
        super().__init__()
        self.history_setting_card = history_setting_card
        self._is_running = True
    
    def run(self):
        """执行数据加载"""
        try:
            prize_pools_name = self.history_setting_card.prize_pools_comboBox.currentText()
            reward_name = self.history_setting_card.reward_comboBox.currentText()
            data = self._get_class_rewards()
            
            if self._is_running:
                self.data_loaded.emit(prize_pools_name, reward_name, data)
        except Exception as e:
            if self._is_running:
                self.error_occurred.emit(str(e))
    
    def stop(self):
        """停止线程"""
        self._is_running = False
        self.wait()
    
    def _get_class_rewards(self):
        """根据班级/学生名称获取历史记录数据"""
        # 获取班级名称
        prize_pools_name = self.history_setting_card.prize_pools_comboBox.currentText()
        _reward_name = self.history_setting_card.reward_comboBox.currentText()
        if _reward_name == '全部奖品':
            if prize_pools_name:
                # 读取配置文件
                reward_file = path_manager.get_resource_path('reward', f'{prize_pools_name}.json')

                try:
                    with open_file(reward_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        cleaned_data = []
                        for reward_name, reward_info in data.items():
                            if isinstance(reward_info, dict) and 'id' in reward_info:
                                id = reward_info.get('id', '')
                                name = reward_name
                                probability = reward_info.get('probability', '')
                                cleaned_data.append((id, name, probability))
                    
                    rewards = [item[1] for item in cleaned_data]
                        
                    # 初始化历史数据字典
                    history_data = {}
                    # 读取历史记录文件
                    history_file = path_manager.get_resource_path('reward', f'history/{prize_pools_name}.json')
                    if remove_file(history_file):
                        try:
                            with open_file(history_file, 'r', encoding='utf-8') as f:
                                history_data = json.load(f)
                        except json.JSONDecodeError:
                            history_data = {}

                    # 生成序号(从1开始)并返回学生数据，包含被点次数信息
                    reward_data = []
                    # 先遍历一次计算各列最大位数
                    max_digits = {
                        'id': 0,
                        'pumping_reward': 0
                    }

                    for i, reward in enumerate(rewards):
                        reward_name = reward if not reward else reward[1:-1]
                        max_digits['id'] = max(max_digits['id'], len(str(cleaned_data[i][0])))
                        if 'pumping_reward' in history_data and reward_name in history_data['pumping_reward']:
                            count = int(history_data['pumping_reward'][reward_name]['total_number_of_times'])
                            max_digits['pumping_reward'] = max(max_digits['pumping_reward'], len(str(count)))

                    # 获取当前抽取模式
                    settings_file = path_manager.get_settings_path()
                    try:
                        with open_file(settings_file, 'r', encoding='utf-8') as f:
                            settings = json.load(f)
                            pumping_reward_draw_mode = settings['pumping_reward']['draw_mode']
                    except Exception as e:
                        pumping_reward_draw_mode = 0
                        logger.error(f"加载设置时出错: {e}, 使用默认设置")

                    # 根据抽选模式执行不同逻辑
                    # 跟随全局设置
                    if pumping_reward_draw_mode == 0:  # 重复随机
                        self.draw_mode = "random"
                    elif pumping_reward_draw_mode == 1:  # 不重复抽取(直到软件重启)
                        self.draw_mode = "until_reboot"
                    elif pumping_reward_draw_mode == 2:  # 不重复抽取(直到抽完全部人)
                        self.draw_mode = "until_all"

                    # 生成最终数据
                    for i, reward in enumerate(rewards):
                        pumping_reward_count = int(history_data['pumping_reward'].get(reward, {}).get('total_number_of_times', 0)) if 'pumping_reward' in history_data else 0
                        reward_data.append([
                            str(cleaned_data[i][0]).zfill(max_digits['id']),
                            reward,
                            cleaned_data[i][2],
                            str(pumping_reward_count).zfill(max_digits['pumping_reward'])
                        ])

                    return reward_data

                except Exception as e:
                    logger.error(f"读取奖励历史文件失败: {e}")
                    raise Exception(f"读取奖励历史文件失败: {e}")
            else:
                return []

        elif _reward_name == '奖品记录_时间排序':
            if prize_pools_name:
                # 奖品数据文件路径
                reward_file = path_manager.get_resource_path('reward', f'{prize_pools_name}.json')
                history_file = path_manager.get_resource_path('reward', f'history/{prize_pools_name}.json')
                
                # 读取奖品配置
                reward_data = {}
                try:
                    with open_file(reward_file, 'r', encoding='utf-8') as f:
                        reward_data = json.load(f)
                except (FileNotFoundError, json.JSONDecodeError):
                    logger.error(f"奖品配置文件不存在或格式错误: {reward_file}")
                    return []

                # 读取奖品发放历史
                history_data = {}
                if remove_file(history_file):
                    try:
                        with open_file(history_file, 'r', encoding='utf-8') as f:
                            history_data = json.load(f).get('pumping_reward', {})
                    except json.JSONDecodeError:
                        logger.error(f"奖品历史记录格式错误: {history_file}")
                        pass

                # 收集所有奖品发放记录
                all_records = []
                reward_items = reward_data
                
                # 遍历奖品历史记录
                for reward_id, distribution_records in history_data.items():
                    reward_info = reward_items.get(reward_id, {})
                    reward_name = reward_id  # 直接使用键名作为奖品名称
                    
                    for record in distribution_records.get('time', []):
                        draw_time = record.get('draw_time', '')
                        if draw_time:
                            all_records.append({
                                'time': draw_time,
                                'reward_id': reward_id,
                                'name': reward_name,
                                'weight': reward_info.get('probability', '1')
                            })
                
                # 按时间降序排序
                sorted_records = sorted(all_records, key=lambda x: x['time'], reverse=True)
                
                # 转换为规范格式返回
                result = []
                for record in sorted_records:
                    # 将概率字符串转换为整数权重
                    weight = int(record['weight']) if record['weight'].isdigit() else 1
                    result.append([
                        record['time'],
                        record['reward_id'],
                        record['name'],
                        str(weight)
                    ])
                
                return result
            else:
                return []
        
        else:
            if prize_pools_name:
                try:
                    # 初始化历史数据字典
                    history_data = {}
                    # 读取历史记录文件
                    history_file = path_manager.get_resource_path('reward', f'history/{prize_pools_name}.json')

                    if remove_file(history_file):
                        try:
                            with open_file(history_file, 'r', encoding='utf-8') as f:
                                history_data = json.load(f)
                        except json.JSONDecodeError:
                            history_data = {}
                    
                    # 修复历史记录数据访问路径
                    reward_data = []
                    pumping_reward = history_data.get('pumping_reward', {})
                    
                    # 添加调试日志
                    logger.debug(f"当前选择的奖励名称: {_reward_name}")
                    
                    # 尝试直接访问时间记录（适配实际数据结构）
                    if isinstance(pumping_reward, dict):
                        # 根据用户选择的奖励名称筛选记录
                        for reward_id, reward_info in pumping_reward.items():
                            # 检查当前奖励ID是否与用户选择的奖励名称匹配
                            if reward_id == _reward_name and isinstance(reward_info, dict) and 'time' in reward_info:
                                for record in reward_info['time']:
                                    time = record.get('draw_time', '')
                                    draw_method = record.get('draw_method', '')
                                    
                                    # 统一处理抽取方式文本
                                    draw_method_map = {
                                        'random': '重复抽取',
                                        'until_reboot': '不重复抽取(直到软件重启)',
                                        'until_all': '不重复抽取(直到抽完全部人)'
                                    }
                                    draw_method_text = draw_method_map.get(draw_method, draw_method)
                                    
                                    # 获取抽取数量，支持列表或单个值
                                    draw_reward_numbers = record.get('draw_reward_numbers', '')
                                    if isinstance(draw_reward_numbers, list):
                                        draw_reward_numbers = ', '.join(map(str, draw_reward_numbers))
                                    
                                    reward_data.append([time, draw_method_text, str(draw_reward_numbers)])
                    
                    # 按时间倒序排序
                    reward_data.sort(reverse=True, key=lambda x: x[0])
                    return reward_data
                    
                except Exception as e:
                    logger.error(f"读取奖品名单文件失败: {e}")
                    raise Exception(f"读取奖品名单文件失败: {e}")
            else:
                return []

class history_reward(QFrame):
    def __init__(self, parent: QFrame = None, load_on_init: bool = True):
        super().__init__(parent=parent)
        # 创建一个 QScrollArea
        self.scroll_area_personal = SingleDirectionScrollArea(self)
        self.scroll_area_personal.setWidgetResizable(True)
        # 设置滚动条样式
        self.scroll_area_personal.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollArea QWidget {
                border: none;
                background-color: transparent;
            }
        """)
        # 启用触屏滚动
        QScroller.grabGesture(self.scroll_area_personal.viewport(), QScroller.LeftMouseButtonGesture)

        # 创建一个内部的 QFrame 用于放置内容
        self.inner_frame_personal = QWidget(self.scroll_area_personal)
        self.inner_layout_personal = QVBoxLayout(self.inner_frame_personal)
        self.inner_layout_personal.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignTop)

        # 历史记录设置卡片组
        self.history_setting_card = history_reward_SettinsCard()
        self.inner_layout_personal.addWidget(self.history_setting_card)
        # 检测选择的班级是否改变，如果改变则刷新表格
        self.history_setting_card.prize_pools_comboBox.currentIndexChanged.connect(self._refresh_table)
        # 检测选择的同学是否改变，如果改变则刷新表格
        self.history_setting_card.reward_comboBox.currentIndexChanged.connect(self._refresh_table)

        # 创建加载状态指示器
        self.loading_widget = self._create_loading_widget()
        self.inner_layout_personal.addWidget(self.loading_widget)

        # 创建表格
        self.table = TableWidget(self.inner_frame_personal) # 创建表格
        self.table.setBorderVisible(True) # 边框
        self.table.setBorderRadius(8) # 圆角
        self.table.setWordWrap(False) # 不换行
        self.table.setEditTriggers(TableWidget.NoEditTriggers) # 静止编辑
        self.table.scrollDelagate.verticalSmoothScroll.setSmoothMode(SmoothMode.NO_SMOOTH) # 静止平滑滚动
        self.table.setSortingEnabled(True) # 启用排序
        self.table.hide()  # 初始隐藏表格

        if load_on_init:
            self.load_data()

    def load_data(self):
        """加载数据"""
        # 检查是否有正在运行的线程，如果有则停止
        if hasattr(self, '_data_loader') and self._data_loader and self._data_loader.isRunning():
            self._data_loader.stop()
        
        # 显示加载状态
        self._show_loading_state()
        
        # 创建并启动数据加载线程
        self._data_loader = RewardDataLoader(self.history_setting_card)
        self._data_loader.data_loaded.connect(self._on_data_loaded)
        self._data_loader.error_occurred.connect(self._on_load_error)
        self._data_loader.start()

    def _on_data_loaded(self, prize_pools_name: str, reward_name: str, data: list):
        """数据加载完成回调"""
        if data:
            InfoBar.success(
                title="读取历史记录文件成功",
                content=f"读取历史记录文件成功,奖池:{prize_pools_name},奖品:{reward_name}",
                duration=3000,
                orient=Qt.Horizontal,
                parent=self,
                isClosable=True,
                position=InfoBarPosition.TOP
            )
        
        # 隐藏加载状态，显示真实数据
        self._hide_loading_state()
        self._setup_table_by_mode(reward_name, data)
        self.__initWidget()
    
    def _on_load_error(self, error_message: str):
        """数据加载错误回调"""
        logger.error(f"加载奖品历史记录数据失败: {error_message}")
        InfoBar.error(
            title="加载失败",
            content="加载奖品历史记录数据失败，请稍后重试",
            duration=3000,
            orient=Qt.Horizontal,
            parent=self,
            isClosable=True,
            position=InfoBarPosition.TOP
        )
        # 隐藏加载状态，显示空表格
        self._hide_loading_state()
        self._setup_table_by_mode('', [])
    
    def _show_loading_state(self):
        """显示加载状态"""
        self.loading_widget.show()
        self.table.hide()
    
    def _hide_loading_state(self):
        """隐藏加载状态"""
        self.loading_widget.hide()
        self.table.show()
    
    def _create_loading_widget(self):
        """创建加载状态组件"""
        loading_widget = QWidget()
        loading_layout = QVBoxLayout(loading_widget)
        loading_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 创建占位表格
        self.loading_table = TableWidget()
        self.loading_table.setBorderVisible(True)
        self.loading_table.setBorderRadius(8)
        self.loading_table.setRowCount(1)
        self.loading_table.setColumnCount(1)
        self.loading_table.setHorizontalHeaderLabels(['界面正在加载中...'])
        self.loading_table.verticalHeader().hide()
        self.loading_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        # 填充占位数据
        for i in range(1):
            for j in range(1):
                item = QTableWidgetItem("--")
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                item.setFont(QFont(load_custom_font(), 12))
                item.setForeground(QColor(200, 200, 200))  # 灰色占位符
                self.loading_table.setItem(i, j, item)
        
        loading_layout.addWidget(self.loading_table)
        
        return loading_widget



    def _setup_table_by_mode(self, reward_name: str, data: list):
        """根据模式设置表格"""
        if reward_name == '全部奖品':
            self._setup_reward_summary_table(data)
        elif reward_name == '奖品记录_时间排序':
            self._setup_reward_time_table(data)
        else:
            self._setup_individual_reward_table(data)

    def _setup_reward_summary_table(self, data: list):
        """设置奖品汇总表格"""
        if not data:
            data = []

        self._configure_table(len(data), 4)
        self._fill_table_data(data)
        self.table.setHorizontalHeaderLabels(['序号', '奖品', '默认权重', '总抽取次数'])
        self.table.sortItems(0, Qt.AscendingOrder)

    def _setup_reward_time_table(self, data: list):
        """设置奖品时间排序表格"""
        if not data:
            data = []

        self._configure_table(len(data), 4)
        self._fill_table_data(data)
        self.table.setHorizontalHeaderLabels(['时间', '序号', '奖品', '默认权重'])

    def _setup_individual_reward_table(self, data: list):
        """设置单个奖品表格"""
        current_time = QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm:ss")
        if not data:
            data = []

        self._configure_table(len(data), 3)
        self._fill_table_data(data)
        self.table.setHorizontalHeaderLabels(['时间', '抽取方式', '抽取时选择的奖品数'])
        self.table.sortByColumn(0, Qt.SortOrder.DescendingOrder)

    def _configure_table(self, row_count: int, column_count: int):
        """配置表格基本属性"""
        self.table.setRowCount(row_count)
        self.table.setColumnCount(column_count)
        self.table.setSortingEnabled(False)
        self.table.verticalHeader().hide()
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def _fill_table_data(self, data: list):
        """填充表格数据"""
        for i, row in enumerate(data):
            for j in range(len(row)):
                item = QTableWidgetItem(str(row[j]))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                item.setFont(QFont(load_custom_font(), 12))
                self.table.setItem(i, j, item)

        self._setup_layout()

    def _setup_layout(self):
        """设置布局"""
        self.inner_layout_personal.addWidget(self.table)
        self.scroll_area_personal.setWidget(self.inner_frame_personal)
        self.table.setSortingEnabled(True)
        
        if not self.layout():
            main_layout = QVBoxLayout(self)
            main_layout.addWidget(self.scroll_area_personal)
        else:
            self.layout().addWidget(self.scroll_area_personal)

    def get_random_method_setting(self):
        """获取随机抽取方法的设置"""
        settings_file = path_manager.get_settings_path()
        try:
            with open_file(settings_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                random_method = settings['pumping_reward']['draw_pumping']
                return random_method
        except Exception as e:
            logger.error(f"加载随机抽取方法设置时出错: {e}, 使用默认设置")
            return 0

    def _refresh_table(self):
        """刷新表格"""
        # 清空表格
        self.table.setRowCount(0)
        # 重新加载表格数据
        self.load_data()

    def __initWidget(self):
        self.__connectSignalToSlot()

    def __connectSignalToSlot(self):
        cfg.themeChanged.connect(setTheme)