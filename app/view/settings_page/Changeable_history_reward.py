from qfluentwidgets import *
from qfluentwidgets import FluentIcon as FIF 
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import os
from datetime import datetime
import math
import json
from loguru import logger

from app.common.config import cfg, AUTHOR, VERSION, YEAR
from app.common.config import get_theme_icon, load_custom_font
from app.common.path_utils import path_manager, open_file, remove_file

from app.common.Changeable_history_reward_settings import history_reward_SettinsCard

class HistoryDataLoader(QThread):
    """历史记录数据加载线程"""
    data_loaded = pyqtSignal(str, str, list)  # prize_pools_name, reward_name, data
    data_segment_loaded = pyqtSignal(str, str, list, int, int)  # prize_pools_name, reward_name, data, current_segment, total_segments
    error_occurred = pyqtSignal(str)  # error_message
    
    def __init__(self, history_setting_card):
        super().__init__()
        self.history_setting_card = history_setting_card
        self._is_running = True
        self.batch_size = 30  # 初始加载30条数据
        self.enable_segmented_loading = True  # 启用分段加载
        self.total_data = []  # 存储所有数据
        self.current_offset = 0  # 当前加载的偏移量
    
    def run(self):
        """执行数据加载"""
        try:
            prize_pools_name = self.history_setting_card.prize_pools_comboBox.currentText()
            reward_name = self.history_setting_card.reward_comboBox.currentText()
            
            # 获取总数据量
            self.total_data = self._get_class_reward()
            total_count = len(self.total_data)
            
            if total_count == 0:
                if self._is_running:
                    self.data_loaded.emit(prize_pools_name, reward_name, [])
                return
            
            # 重置偏移量
            self.current_offset = 0
            
            # 计算初始分段数量
            initial_segments = 1  # 初始只加载一段
            
            # 加载初始数据
            if self._is_running:
                end_idx = min(self.batch_size, total_count)
                initial_data = self.total_data[0:end_idx]
                self.current_offset = end_idx
                
                # 发送初始数据
                self.data_segment_loaded.emit(
                    prize_pools_name, 
                    reward_name, 
                    initial_data, 
                    1, 
                    math.ceil(total_count / self.batch_size) if total_count > self.batch_size else 1
                )
                
                # 如果数据量小于等于初始加载量，直接发送完成信号
                if total_count <= self.batch_size:
                    if self._is_running:
                        self.data_loaded.emit(prize_pools_name, reward_name, self.total_data)
        except Exception as e:
            if self._is_running:
                self.error_occurred.emit(str(e))
    
    @pyqtSlot()
    def load_more_data(self):
        """加载更多数据"""
        if not self._is_running or self.current_offset >= len(self.total_data):
            return False
        
        try:
            prize_pools_name = self.history_setting_card.prize_pools_comboBox.currentText()
            reward_name = self.history_setting_card.reward_comboBox.currentText()
            
            # 计算当前段和总段数
            current_segment = math.ceil(self.current_offset / self.batch_size) + 1
            total_segments = math.ceil(len(self.total_data) / self.batch_size)
            
            # 加载下一段数据
            end_idx = min(self.current_offset + self.batch_size, len(self.total_data))
            segment_data = self.total_data[self.current_offset:end_idx]
            self.current_offset = end_idx
            
            # 发送分段数据
            self.data_segment_loaded.emit(
                prize_pools_name, 
                reward_name, 
                segment_data, 
                current_segment, 
                total_segments
            )
            
            # 如果已经加载完所有数据，发送完成信号
            if self.current_offset >= len(self.total_data):
                if self._is_running:
                    self.data_loaded.emit(prize_pools_name, reward_name, self.total_data)
            
            return True
        except Exception as e:
            if self._is_running:
                self.error_occurred.emit(str(e))
            return False
    
    def stop(self):
        """停止线程"""
        self._is_running = False
        self.wait()
    
    def _get_class_reward(self):
        """根据奖池/奖品名称获取历史记录数据"""
        # 获取奖池名称
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
                    history_file = path_manager.get_resource_path('reward/history', f'{prize_pools_name}.json') 
 
                    if path_manager.file_exists(history_file): 
                        try: 
                            with open_file(history_file, 'r', encoding='utf-8') as f: 
                                history_data = json.load(f) 
                        except json.JSONDecodeError as e: 
                            logger.error(f"读取历史记录文件时出错: {e}") 
                            history_data = {} 
 
                    # 生成序号(从1开始)并返回学生数据，包含被点次数信息 
                    reward_data = [] 
                    # 先遍历一次计算各列最大位数 
                    max_digits = { 
                        'id': 0, 
                        'pumping_reward': 0 
                    } 
 
                    for i, reward in enumerate(rewards): 
                        reward_name = reward
                        max_digits['id'] = max(max_digits['id'], len(str(cleaned_data[i][0]))) 
                        if 'pumping_reward' in history_data and reward_name in history_data['pumping_reward']: 
                            count = int(history_data['pumping_reward'][reward_name]['total_number_of_times'])
                            max_digits['pumping_reward'] = max(max_digits['pumping_reward'], len(str(count)))
 
                    # 获取当前抽取模式 
                    try: 
                        settings_path = path_manager.get_settings_path('Settings.json') 
                        with open_file(settings_path, 'r', encoding='utf-8') as f: 
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
                        reward_data.append({
                            '序号': str(cleaned_data[i][0]).zfill(max_digits['id']), 
                            '奖品': reward, 
                            '默认权重': cleaned_data[i][2], 
                            '总抽取次数': str(count).zfill(max_digits['pumping_reward'])
                        }) 

                    return reward_data 
 
                except Exception as e: 
                    logger.error(f"读取奖池名单文件失败: {e}") 
                    raise Exception(f"读取奖品名单文件失败: {e}")
            else:
                return []

        elif _reward_name == '奖品记录_时间排序':
            if prize_pools_name:
                # 奖品数据文件路径 
                # 奖品数据文件路径
                reward_file = path_manager.get_resource_path('reward', f'{prize_pools_name}.json')
                history_file = path_manager.get_resource_path('reward/history', f'{prize_pools_name}.json')
                
                # 读取奖品配置
                reward_data = {}
                cleaned_data = []
                try:
                    with open_file(reward_file, 'r', encoding='utf-8') as f:
                        reward_data = json.load(f)
                        # 处理奖品数据，类似"全部奖品"模式
                        for reward_name, reward_info in reward_data.items():
                            if isinstance(reward_info, dict) and 'id' in reward_info:
                                id = reward_info.get('id', '')
                                name = reward_name
                                probability = reward_info.get('probability', '')
                                cleaned_data.append((id, name, probability))
                except (FileNotFoundError, json.JSONDecodeError):
                    logger.error(f"奖品配置文件不存在或格式错误: {reward_file}")
                    return []

                # 计算ID的最大位数
                max_digits = {
                    'id': 0
                }
                for item in cleaned_data:
                    max_digits['id'] = max(max_digits['id'], len(str(item[0])))

                # 读取奖品发放历史
                history_data = {}
                if path_manager.file_exists(history_file):
                    try:
                        with open_file(history_file, 'r', encoding='utf-8') as f:
                            history_data = json.load(f).get('pumping_reward', {})
                    except json.JSONDecodeError:
                        logger.error(f"奖品历史记录格式错误: {history_file}")
                        pass

                # 遍历奖品历史记录
                all_records = []
                reward_items = reward_data
                
                # 创建奖品ID到cleaned_data索引的映射
                reward_id_to_index = {}
                for i, item in enumerate(cleaned_data):
                    reward_id_to_index[item[1]] = i  # 使用奖品名称作为键，索引作为值
                 
                # 遍历奖品历史记录 
                for reward_id, distribution_records in history_data.items():
                    reward_info = reward_items.get(reward_id, {})
                    # 获取正确的奖品ID和名称
                    actual_reward_id = reward_info.get('id', reward_id)  # 使用奖品配置中的id字段，如果没有则使用原ID
                    reward_name = reward_id  # 使用键名作为奖品名称
                    
                    # 获取在cleaned_data中的索引
                    index = reward_id_to_index.get(reward_id, -1)
                    
                    for record in distribution_records.get('time', []):
                        draw_time = record.get('draw_time', '')
                        if draw_time:
                            # 使用str(cleaned_data[i][0]).zfill(max_digits['id'])格式
                            formatted_id = str(actual_reward_id).zfill(max_digits['id']) if index == -1 else str(cleaned_data[index][0]).zfill(max_digits['id'])
                            all_records.append({
                                'time': draw_time,
                                'reward_id': formatted_id,
                                'name': reward_name,
                                'weight': reward_info.get('probability', '1')
                            })
                 
                # 按时间降序排序 
                sorted_records = sorted(all_records, key=lambda x: x['time'], reverse=True) 
                 
                # 转换为规范格式返回 
                result = [] 
                for record in sorted_records: 
                    # 将概率字符串转换为整数权重 
                    weight_str = str(record['weight']) 
                    weight = int(weight_str) if weight_str.isdigit() else 1 
                    result.append({
                        '时间': record['time'], 
                        '序号': record['reward_id'], 
                        '奖品': record['name'], 
                        '默认权重': str(weight)
                    }) 
                 
                return result 
            else: 
                return []

        else:
            if prize_pools_name:
                try:
                    # 初始化历史数据字典
                    history_data = {}
                    # 读取历史记录文件
                    history_file = path_manager.get_resource_path('reward/history', f'{prize_pools_name}.json')

                    if path_manager.file_exists(history_file):
                        try:
                            with open_file(history_file, 'r', encoding='utf-8') as f:
                                history_data = json.load(f)
                        except json.JSONDecodeError:
                            history_data = {}
                            logger.warning(f"历史记录文件格式错误: {history_file}")
                    
                    # 假设历史数据中每个抽取记录有时间、抽取方式和被点次数信息
                    reward_data = []
                    
                    if 'pumping_reward' in history_data and _reward_name in history_data['pumping_reward']:
                        pumping_reward_history = history_data['pumping_reward'][_reward_name]
                        
                        if 'time' in pumping_reward_history:
                            for record in pumping_reward_history['time']:
                                time = record.get('draw_time', '')
                                draw_method = record.get('draw_method', '')
                                if draw_method == 'random':
                                    draw_method_text = '重复抽取'
                                elif draw_method == 'until_reboot':
                                    draw_method_text = '不重复抽取(直到软件重启)'
                                elif draw_method == 'until_all':
                                    draw_method_text = '不重复抽取(直到抽完全部奖)'
                                else:
                                    draw_method_text = draw_method
                                draw_reward_numbers = record.get('draw_reward_numbers', '')
                                reward_data.append([time, draw_method_text, f'{draw_reward_numbers}'])
                        else:
                            logger.warning(f"奖品历史记录中缺少time字段: {_reward_name}")
                    else:
                        logger.warning(f"未找到奖品历史记录: {_reward_name}")

                    return reward_data
                    
                except Exception as e:
                    logger.error(f"读取奖品历史记录失败: {e}")
                    raise Exception(f"读取奖品历史记录失败: {e}")
            else:
                logger.warning("未选择奖池")
                return []
    
    def get_random_method_setting(self) -> int:
        """获取随机抽取方法的设置"""
        return self._get_setting_value('pumping_reward', 'draw_pumping', 0)
    
    def get_probability_weight_method_setting(self) -> int:
        """获取概率权重方法设置"""
        return self._get_setting_value('reward', 'probability_weight', 0)
    
    def _get_setting_value(self, section: str, key: str, default: int) -> int:
        """通用设置读取方法"""
        settings_file = path_manager.get_settings_path()
        try:
            with open_file(settings_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                return settings[section][key]
        except Exception as e:
            logger.error(f"加载设置时出错: {e}, 使用默认设置")
            return default

class changeable_history_reward(QFrame):
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
        # 检测选择的奖池是否改变，如果改变则刷新表格
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
        
        # 添加滚动事件监听
        self.table.verticalScrollBar().valueChanged.connect(self._on_scroll)
        
        # 分段加载相关变量
        self._segmented_data = []  # 存储分段加载的数据
        self._current_segment = 0  # 当前加载的段
        self._total_segments = 0   # 总段数
        self._is_loading_segments = False  # 是否正在分段加载
        self._has_more_data = True  # 是否还有更多数据
        self._scroll_threshold = 5  # 滚动阈值，距离底部多少行时加载更多数据

        if load_on_init:
            self.load_data()

    def load_data(self):
        """加载数据"""
        # 检查是否有正在运行的线程
        if hasattr(self, '_data_loader') and self._data_loader and self._data_loader.isRunning():
            self._data_loader.stop()
        
        # 重置所有状态
        self._segmented_data = []
        self._current_segment = 0
        self._total_segments = 0
        self._is_loading_segments = False
        self._has_more_data = True
        
        # 显示加载状态
        self._show_loading_state()
        
        # 创建并启动数据加载线程
        self._data_loader = HistoryDataLoader(self.history_setting_card)
        self._data_loader.data_loaded.connect(self._on_data_loaded)
        self._data_loader.data_segment_loaded.connect(self._on_data_segment_loaded)
        self._data_loader.error_occurred.connect(self._on_load_error)
        self._data_loader.start()

    def _on_scroll(self, value):
        """滚动事件处理"""
        if not self._has_more_data or self._is_loading_segments:
            return
        
        # 获取滚动条最大值
        max_value = self.table.verticalScrollBar().maximum()
        
        # 如果滚动条值为0或者表格为空，不处理
        if max_value == 0 or self.table.rowCount() == 0:
            return
        
        # 获取当前可见的行数
        row_height = self.table.rowHeight(0)
        visible_rows = self.table.viewport().height() // row_height if row_height > 0 else 0
        
        # 计算当前滚动位置对应的行号
        current_row = value // row_height if row_height > 0 else 0
        
        # 计算距离底部还有多少行
        rows_to_bottom = self.table.rowCount() - current_row - visible_rows
        
        # 如果距离底部小于等于阈值，加载更多数据
        if rows_to_bottom <= self._scroll_threshold:
            self._load_more_data()
    
    def _load_more_data(self):
        """加载更多数据"""
        if self._is_loading_segments or not self._has_more_data:
            return
        
        # 设置加载状态
        self._is_loading_segments = True
        
        # 显示加载提示
        InfoBar.info(
            title="加载中",
            content="正在加载更多数据...",
            parent=self,
            duration=1000
        )
        
        # 调用数据加载器的 load_more_data 方法
        if hasattr(self, '_data_loader') and self._data_loader:
            # 使用 QMetaObject.invokeMethod 确保在主线程中调用
            QMetaObject.invokeMethod(self._data_loader, "load_more_data", Qt.QueuedConnection)
        else:
            # 如果没有数据加载器，重置状态
            self._is_loading_segments = False
    
    def _on_data_segment_loaded(self, prize_pools_name, reward_name, data, current_segment, total_segments):
        """分段数据加载完成回调"""
        # 更新分段加载状态
        self._current_segment = current_segment
        self._total_segments = total_segments
        
        # 将分段数据添加到总数据中
        self._segmented_data.extend(data)
        
        # 如果是第一段数据，初始化表格
        if current_segment == 1:
            self._hide_loading_state()
            # 初始化表格结构，但不填充数据
            if reward_name == '全部奖品':
                self._setup_reward_summary_table([])
            elif reward_name == '奖品记录_时间排序':
                self._setup_reward_time_table([])
            else:
                # 个人历史记录模式
                self._setup_individual_table_headers()
        
        # 填充当前段的数据
        self._fill_table_data(data)
        
        # 检查是否还有更多数据
        self._has_more_data = current_segment < total_segments
        
        # 重置加载状态，允许再次触发加载
        self._is_loading_segments = False
        
        # 更新加载进度
        if self._has_more_data:
            progress_text = f"已加载 {len(self._segmented_data)} 条数据"
            InfoBar.info(
                title="数据加载中",
                content=progress_text,
                parent=self,
                duration=1000
            )
    

    
    def _on_data_loaded(self, prize_pools_name, reward_name, data):
        """所有数据加载完成回调"""
        self._hide_loading_state()
        
        # 重置加载状态
        self._is_loading_segments = False
        self._has_more_data = False
        
        # 如果是分段加载，所有数据已经通过 _on_data_segment_loaded 处理
        if self._segmented_data and len(self._segmented_data) > 0:
            InfoBar.success(
                title="加载完成",
                content=f"已加载全部 {len(self._segmented_data)} 条数据",
                parent=self,
                duration=2000
            )
        else:
            # 如果不是分段加载，初始化表格并填充数据
            if reward_name == '全部奖品':
                self._setup_reward_summary_table(data)
            elif reward_name == '奖品记录_时间排序':
                self._setup_reward_time_table(data)
            else:
                # 个人历史记录模式
                self._setup_individual_table(data)
    
    def _on_load_error(self, error_message):
        """数据加载出错回调"""
        self._hide_loading_state()
        
        # 重置加载状态
        self._is_loading_segments = False
        self._has_more_data = False
        self._current_segment = 0
        self._total_segments = 0
        
        # 显示错误提示
        InfoBar.error(
            title="加载失败",
            content=error_message,
            parent=self,
            duration=3000
        )
        
        # 清空表格
        self.table.setRowCount(0)
        self.table.setColumnCount(0)
    
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
        # 设置列宽为拉伸模式，自动铺满表格
        self.loading_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        # 设置表头字体和居中
        header_font = QFont(load_custom_font(), 12, QFont.Bold)
        self.loading_table.horizontalHeader().setFont(header_font)
        self.loading_table.horizontalHeader().setDefaultAlignment(Qt.AlignCenter)
        
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



    def _setup_table_by_mode(self, reward_name: str, data: list, is_segment: bool = False):
        """根据模式设置表格"""
        if reward_name == '全部奖品':
            self._setup_reward_summary_table(data, is_segment=is_segment)
        elif reward_name == '奖品记录_时间排序':
            self._setup_reward_time_table(data, is_segment=is_segment)
        else:
            self._setup_individual_table(data, is_segment=is_segment)
    
    def _setup_reward_summary_table_headers(self):
        """设置奖品汇总表格表头"""
        headers = ['序号', '奖品', '默认权重', '总抽取次数']
        self._configure_table(0, 4)
        self.table.setHorizontalHeaderLabels(headers)
    
    def _setup_reward_time_table_headers(self):
        """设置奖品时间排序表格表头"""
        headers = ['时间', '序号', '奖品', '默认权重']
        self._configure_table(0, 4)
        self.table.setHorizontalHeaderLabels(headers)
    
    def _setup_individual_table_headers(self):
        """设置个人表格表头"""
        self._configure_table(0, 3)
        self.table.setHorizontalHeaderLabels(['时间', '抽取方式', '抽取时选择的奖品数'])

    def _setup_reward_summary_table(self, data: list, is_segment: bool = False):
        """设置奖品汇总表格"""
        if not data:
            data = []
        
        # 如果是分段加载，只更新表头一次
        if not is_segment:
            self._setup_reward_summary_table_headers()
        
        # 填充数据
        self._fill_table_data(data)
        
        # 只有在非分段加载或者数据加载完成后才进行排序
        if not self._is_loading_segments:
            self.table.sortByColumn(0, Qt.SortOrder.AscendingOrder)

    def _setup_reward_time_table(self, data: list, is_segment: bool = False):
        """设置奖品时间排序表格"""
        if not data:
            data = []
        
        # 如果是分段加载，只更新表头一次
        if not is_segment:
            self._setup_reward_time_table_headers()
        
        # 填充数据
        self._fill_table_data(data)
        
        # 只有在非分段加载或者数据加载完成后才进行排序
        if not self._is_loading_segments:
            self.table.sortByColumn(0, Qt.SortOrder.DescendingOrder)

    def _setup_individual_table(self, data: list, is_segment: bool = False):
        """设置单个奖品表格"""
        if not data:
            data = []

        # 如果是分段加载，只更新表头一次
        if not is_segment:
            self._setup_individual_table_headers()
        
        # 填充数据
        self._fill_table_data(data)
        
        # 只有在非分段加载或者数据加载完成后才进行排序
        if not self._is_loading_segments:
            self.table.sortByColumn(0, Qt.SortOrder.DescendingOrder)

    def _setup_individual_reward_table(self, data: list):
        """设置单个奖品表格"""
        if not data:
            data = []

        self._configure_table(len(data), 3)
        self.table.setHorizontalHeaderLabels(['时间', '抽取方式', '抽取时选择的奖品数'])
        
        # 填充数据
        self._fill_table_data(data)
        
        # 只有在非分段加载或者数据加载完成后才进行排序
        if not self._is_loading_segments:
            self.table.sortByColumn(0, Qt.SortOrder.DescendingOrder)

    def _configure_table(self, row_count: int, column_count: int):
        """配置表格基本属性"""
        # 如果是分段加载模式，不重置行数
        if not self._is_loading_segments:
            self.table.setRowCount(row_count)
        self.table.setColumnCount(column_count)
        
        # 保存当前排序状态
        sort_enabled = self.table.isSortingEnabled()
        sort_column = -1
        sort_order = Qt.SortOrder.DescendingOrder
        
        if sort_enabled:
            sort_column = self.table.horizontalHeader().sortIndicatorSection()
            sort_order = self.table.horizontalHeader().sortIndicatorOrder()
        
        # 临时禁用排序以配置表格
        self.table.setSortingEnabled(False)
        self.table.verticalHeader().hide()
        # 设置列宽为拉伸模式，自动铺满表格
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        # 恢复排序状态
        if sort_enabled:
            self.table.setSortingEnabled(True)
            if sort_column >= 0:
                self.table.sortByColumn(sort_column, sort_order)

    def _fill_table_data(self, data: list):
        """填充表格数据"""
        if not data:
            return
            
        # 保存当前排序状态
        sort_enabled = self.table.isSortingEnabled()
        sort_column = -1
        sort_order = Qt.SortOrder.AscendingOrder
        
        if sort_enabled:
            sort_column = self.table.horizontalHeader().sortIndicatorSection()
            sort_order = self.table.horizontalHeader().sortIndicatorOrder()
            # 临时禁用排序以填充数据
            self.table.setSortingEnabled(False)
            
        # 如果是分段加载模式，只添加新数据，不重新设置整个表格
        if self._is_loading_segments:
            # 获取当前表格行数
            current_row_count = self.table.rowCount()
            # 添加新行
            self.table.setRowCount(current_row_count + len(data))
            
            # 填充新数据
            for i, item in enumerate(data):
                row = current_row_count + i
                if isinstance(item, dict):
                    # 奖池历史记录模式
                    if '时间' in item:
                        # 时间排序模式 - 表头: ['时间', '序号', '奖品', '默认权重']
                        time_item = QTableWidgetItem(item['时间'])
                        time_item.setFont(QFont(load_custom_font(), 12))
                        time_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                        self.table.setItem(row, 0, time_item)
                        
                        id_item = QTableWidgetItem(item['序号'])
                        id_item.setFont(QFont(load_custom_font(), 12))
                        id_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                        self.table.setItem(row, 1, id_item)
                        
                        name_item = QTableWidgetItem(item['奖品'])
                        name_item.setFont(QFont(load_custom_font(), 12))
                        name_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                        self.table.setItem(row, 2, name_item)
                        
                        weight_item = QTableWidgetItem(str(item.get('默认权重', '')))
                        weight_item.setFont(QFont(load_custom_font(), 12))
                        weight_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                        self.table.setItem(row, 3, weight_item)
                    else:
                        # 普通模式 - 表头: ['序号', '奖品', '默认权重', '总抽取次数']
                        id_item = QTableWidgetItem(item['序号'])
                        id_item.setFont(QFont(load_custom_font(), 12))
                        id_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                        self.table.setItem(row, 0, id_item)
                        
                        name_item = QTableWidgetItem(item['奖品'])
                        name_item.setFont(QFont(load_custom_font(), 12))
                        name_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                        self.table.setItem(row, 1, name_item)
                        
                        weight_item = QTableWidgetItem(str(item.get('默认权重', '')))
                        weight_item.setFont(QFont(load_custom_font(), 12))
                        weight_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                        self.table.setItem(row, 2, weight_item)
                        
                        count_item = QTableWidgetItem(str(item.get('总抽取次数', '')))
                        count_item.setFont(QFont(load_custom_font(), 12))
                        count_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                        self.table.setItem(row, 3, count_item)
                else:
                    # 个人历史记录模式 - 表头: ['时间', '抽取方式', '抽取时选择的奖品数']
                    time_item = QTableWidgetItem(item[0])  # 时间
                    time_item.setFont(QFont(load_custom_font(), 12))
                    time_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                    self.table.setItem(row, 0, time_item)
                    
                    method_item = QTableWidgetItem(item[1])  # 抽取方式
                    method_item.setFont(QFont(load_custom_font(), 12))
                    method_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                    self.table.setItem(row, 1, method_item)
                    
                    count_item = QTableWidgetItem(str(item[2]))  # 抽取时选择的奖品数
                    count_item.setFont(QFont(load_custom_font(), 12))
                    count_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                    self.table.setItem(row, 2, count_item)
        else:
            # 非分段加载模式，填充所有数据
            self.table.setRowCount(len(data))
            
            for i, item in enumerate(data):
                if isinstance(item, dict):
                    # 奖池历史记录模式
                    if '时间' in item:
                        # 时间排序模式 - 表头: ['时间', '序号', '奖品', '默认权重']
                        time_item = QTableWidgetItem(item['时间'])
                        time_item.setFont(QFont(load_custom_font(), 12))
                        time_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                        self.table.setItem(i, 0, time_item)
                        
                        id_item = QTableWidgetItem(item['序号'])
                        id_item.setFont(QFont(load_custom_font(), 12))
                        id_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                        self.table.setItem(i, 1, id_item)
                        
                        name_item = QTableWidgetItem(item['奖品'])
                        name_item.setFont(QFont(load_custom_font(), 12))
                        name_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                        self.table.setItem(i, 2, name_item)
                        
                        weight_item = QTableWidgetItem(str(item.get('默认权重', '')))
                        weight_item.setFont(QFont(load_custom_font(), 12))
                        weight_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                        self.table.setItem(i, 3, weight_item)
                    else:
                        # 普通模式 - 表头: ['序号', '奖品', '默认权重', '总抽取次数']
                        id_item = QTableWidgetItem(item['序号'])
                        id_item.setFont(QFont(load_custom_font(), 12))
                        id_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                        self.table.setItem(i, 0, id_item)
                        
                        name_item = QTableWidgetItem(item['奖品'])
                        name_item.setFont(QFont(load_custom_font(), 12))
                        name_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                        self.table.setItem(i, 1, name_item)
                        
                        weight_item = QTableWidgetItem(str(item.get('默认权重', '')))
                        weight_item.setFont(QFont(load_custom_font(), 12))
                        weight_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                        self.table.setItem(i, 2, weight_item)
                        
                        count_item = QTableWidgetItem(str(item.get('总抽取次数', '')))
                        count_item.setFont(QFont(load_custom_font(), 12))
                        count_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                        self.table.setItem(i, 3, count_item)
                else:
                    # 个人历史记录模式 - 表头: ['时间', '抽取方式', '抽取时选择的奖品数']
                    time_item = QTableWidgetItem(item[0])  # 时间
                    time_item.setFont(QFont(load_custom_font(), 12))
                    time_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                    self.table.setItem(i, 0, time_item)
                    
                    method_item = QTableWidgetItem(item[1])  # 抽取方式
                    method_item.setFont(QFont(load_custom_font(), 12))
                    method_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                    self.table.setItem(i, 1, method_item)
                    
                    count_item = QTableWidgetItem(str(item[2]))  # 抽取时选择的奖品数
                    count_item.setFont(QFont(load_custom_font(), 12))
                    count_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                    self.table.setItem(i, 2, count_item)
        
        # 恢复排序状态
        if sort_enabled:
            self.table.setSortingEnabled(True)
            if sort_column >= 0:
                self.table.sortByColumn(sort_column, sort_order)
        
        self._setup_layout()

    def _setup_layout(self):
        """设置布局"""
        self.inner_layout_personal.addWidget(self.table)
        self.scroll_area_personal.setWidget(self.inner_frame_personal)
        
        # 确保排序功能已启用
        if not self.table.isSortingEnabled():
            self.table.setSortingEnabled(True)
        
        if not self.layout():
            main_layout = QVBoxLayout(self)
            main_layout.addWidget(self.scroll_area_personal)
        else:
            self.layout().addWidget(self.scroll_area_personal)

    def get_random_method_setting(self) -> int:
        """获取随机抽取方法的设置"""
        return self._get_setting_value('pumping_reward', 'draw_pumping', 0)

    def get_probability_weight_method_setting(self) -> int:
        """获取概率权重方法设置"""
        return self._get_setting_value('reward', 'probability_weight', 0)

    def _get_setting_value(self, section: str, key: str, default: int) -> int:
        """通用设置读取方法"""
        settings_file = path_manager.get_settings_path()
        try:
            with open_file(settings_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                return settings[section][key]
        except Exception as e:
            logger.error(f"加载设置时出错: {e}, 使用默认设置")
            return default

    def _refresh_table(self):
        """刷新表格"""
        # 检查是否有正在运行的线程
        if hasattr(self, '_data_loader') and self._data_loader and self._data_loader.isRunning():
            self._data_loader.stop()
        
        # 重置所有状态
        self._segmented_data = []
        self._current_segment = 0
        self._total_segments = 0
        self._is_loading_segments = False
        self._has_more_data = True
        
        # 清空表格并重置排序状态
        self.table.setSortingEnabled(False)
        self.table.setRowCount(0)
        self.table.horizontalHeader().setSortIndicator(-1, Qt.SortOrder.AscendingOrder)
        
        # 重新加载表格数据
        self.load_data()

    def __initWidget(self):
        self.__connectSignalToSlot()

    def __connectSignalToSlot(self):
        cfg.themeChanged.connect(setTheme)
