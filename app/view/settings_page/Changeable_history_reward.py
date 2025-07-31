from qfluentwidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import os
import math
from loguru import logger

from app.common.config import cfg, AUTHOR, VERSION, YEAR
from app.common.config import load_custom_font

from app.common.Changeable_history_reward_settings import history_reward_SettinsCard

class changeable_history_reward(QFrame):
    def __init__(self, parent: QFrame = None):
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
        # 检测是否点击清除历史记录按钮，如果点击则刷新表格
        self.history_setting_card.clear_history_Button.clicked.connect(self._refresh_table)
        # 检测选择的同学是否改变，如果改变则刷新表格
        self.history_setting_card.reward_comboBox.currentIndexChanged.connect(self._refresh_table)

        # 创建表格
        self.table = TableWidget(self.inner_frame_personal) # 创建表格
        self.table.setBorderVisible(True) # 边框
        self.table.setBorderRadius(8) # 圆角
        self.table.setWordWrap(False) # 不换行
        self.table.setEditTriggers(TableWidget.NoEditTriggers) # 静止编辑
        self.table.scrollDelagate.verticalSmoothScroll.setSmoothMode(SmoothMode.NO_SMOOTH) # 静止平滑滚动
        self.table.setSortingEnabled(True) # 启用排序

        self.show_table()

    def show_table(self):
        """显示历史记录表格"""
        data = self.__getClassrewards()
        prize_pools_name = self.history_setting_card.prize_pools_comboBox.currentText()
        reward_name = self.history_setting_card.reward_comboBox.currentText()

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

        self._setup_table_by_mode(reward_name, data)
        self.__initWidget()

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
            data = [['0', '无', '无', '无']]

        self._configure_table(len(data), 4)
        self._fill_table_data(data)
        self.table.setHorizontalHeaderLabels(['序号', '奖品', '默认权重', '总抽取次数'])
        self.table.sortItems(0, Qt.AscendingOrder)

    def _setup_reward_time_table(self, data: list):
        """设置奖品时间排序表格"""
        if not data:
            data = [['无', '0', '无', '无']]

        self._configure_table(len(data), 4)
        self._fill_table_data(data)
        self.table.setHorizontalHeaderLabels(['时间', '序号', '奖品', '默认权重'])

    def _setup_individual_reward_table(self, data: list):
        """设置单个奖品表格"""
        current_time = QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm:ss")
        if not data:
            data = [[current_time, '无', '无']]

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

    def __getClassrewards(self):
        """根据班级/学生名称获取历史记录数据"""
        # 获取班级名称
        prize_pools_name = self.history_setting_card.prize_pools_comboBox.currentText()
        _reward_name = self.history_setting_card.reward_comboBox.currentText()
        if _reward_name == '全部奖品':
            if prize_pools_name:
                # 读取配置文件
                reward_file = f'app/resource/reward/{prize_pools_name}.json'

                try:
                    with open(reward_file, 'r', encoding='utf-8') as f:
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
                    history_file = f'app/resource/reward/history/{prize_pools_name}.json'

                    if os.path.exists(history_file):
                        try:
                            with open(history_file, 'r', encoding='utf-8') as f:
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
                    try:
                        with open('app/Settings/Settings.json', 'r', encoding='utf-8') as f:
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
                    logger.error(f"读取奖池名单文件失败: {e}")
                    InfoBar.error(
                        title="读取奖池名单文件失败",
                        content=f"错误信息: （请到日志文件查看）",
                        duration=3000,
                        orient=Qt.Horizontal,
                        parent=self,
                        isClosable=True,
                        position=InfoBarPosition.TOP
                    )
                    return []
            else:
                return []

        elif _reward_name == '奖品记录_时间排序':
            if prize_pools_name:
                # 奖品数据文件路径
                reward_file = f'app/resource/reward/{prize_pools_name}.json'
                history_file = f'app/resource/reward/history/{prize_pools_name}.json'
                
                # 读取奖品配置
                reward_data = {}
                try:
                    with open(reward_file, 'r', encoding='utf-8') as f:
                        reward_data = json.load(f)
                except (FileNotFoundError, json.JSONDecodeError):
                    logger.error(f"奖品配置文件不存在或格式错误: {reward_file}")
                    return []

                # 读取奖品发放历史
                history_data = {}
                if os.path.exists(history_file):
                    try:
                        with open(history_file, 'r', encoding='utf-8') as f:
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
                    history_file = f'app/resource/reward/history/{prize_pools_name}.json'

                    if os.path.exists(history_file):
                        try:
                            with open(history_file, 'r', encoding='utf-8') as f:
                                history_data = json.load(f)
                        except json.JSONDecodeError:
                            history_data = {}
                    
                    # 假设历史数据中每个抽取记录有时间、抽取方式和被点次数信息
                    reward_data = []
                    if _reward_name in history_data.get('pumping_reward', {}):
                        pumping_reward_history = history_data['pumping_reward'][_reward_name]['time']
                        for record in pumping_reward_history:
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
                    print(reward_data)
                    return reward_data
                    
                except Exception as e:
                    logger.error(f"读取奖池名单文件失败: {e}")
                    InfoBar.error(
                        title="读取奖池名单文件失败",
                        content=f"错误信息: （请到日志文件查看）",
                        duration=3000,
                        orient=Qt.Horizontal,
                        parent=self,
                        isClosable=True,
                        position=InfoBarPosition.TOP
                    )
                    return []
            else:
                return []

    def _refresh_table(self):
        """刷新表格"""
        # 清空表格
        self.table.setRowCount(0)
        # 重新加载表格数据
        self.show_table()

    def __initWidget(self):
        self.__connectSignalToSlot()

    def __connectSignalToSlot(self):
        cfg.themeChanged.connect(setTheme)
