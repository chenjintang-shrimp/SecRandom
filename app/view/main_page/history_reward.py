from qfluentwidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import os
from datetime import datetime
import math
from loguru import logger

from app.common.config import cfg, AUTHOR, VERSION, YEAR
from app.common.config import load_custom_font

from app.common.history_reward_settings import history_reward_SettinsCard

class history_reward(QFrame):
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

        self.show_table()

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

    def show_table(self):
        """显示历史记录表格"""
        # 显示加载状态
        self.loading_widget.show()
        self.table.hide()
        
        # 使用QTimer延迟加载数据，避免界面卡顿
        QTimer.singleShot(100, self._load_data_async)

    def _load_data_async(self):
        """异步加载数据"""
        try:
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

            # 隐藏加载状态，显示真实数据
            self.loading_widget.hide()
            self.table.show()
            self._setup_table_by_mode(reward_name, data)
            self.__initWidget()
            
        except Exception as e:
            logger.error(f"加载奖品历史记录数据失败: {e}")
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
            self.loading_widget.hide()
            self.table.show()
            self._setup_table_by_mode('', [])

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

    def get_random_method_setting(self):
        """获取随机抽取方法的设置"""
        try:
            with open('app/Settings/Settings.json', 'r', encoding='utf-8') as f:
                settings = json.load(f)
                random_method = settings['pumping_reward']['draw_pumping']
                return random_method
        except Exception as e:
            logger.error(f"加载随机抽取方法设置时出错: {e}, 使用默认设置")
            return 0

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
                        
                    # 使用SQLite数据库读取历史记录
                    from app.common.sqlite_utils import history_manager
                    
                    # 获取奖品历史记录
                    reward_stats = history_manager.get_reward_stats(prize_pools_name)
                    
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
                        
                        # 从数据库获取奖品被抽中次数
                        count_key = f'reward_{reward_name}'
                        if count_key in reward_stats:
                            count = reward_stats[count_key]
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
                        
                    # 从SQLite数据库获取已抽取奖品记录
                    drawn_rewards = history_manager.get_drawn_rewards(
                        prize_pool=prize_pools_name,
                        draw_mode=self.draw_mode
                    )

                    # 🌸 小鸟游星野提醒：生成最终数据，避免前导零
                    for i, reward in enumerate(rewards):
                        reward_name = reward if not reward else reward[1:-1]
                        count_key = f'reward_{reward_name}'
                        pumping_reward_count = reward_stats.get(count_key, 0)
                        reward_data.append([
                            str(cleaned_data[i][0]).zfill(max_digits['id']),
                            reward,
                            cleaned_data[i][2],
                            str(pumping_reward_count)
                        ])

                    return reward_data

                except Exception as e:
                    logger.error(f"读取奖励历史文件失败: {e}")
                    InfoBar.error(
                        title="读取学生名单文件失败",
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
                reward_file = f'app/resource/reward/{prize_pools_name}.json'
                
                # 读取奖品名单
                try:
                    with open(reward_file, 'r', encoding='utf-8') as f:
                        reward_data = json.load(f)
                except (FileNotFoundError, json.JSONDecodeError):
                    return []

                # 清理奖品数据
                cleaned_rewards = {}
                for name, info in reward_data.items():
                    if isinstance(info, dict):
                        cleaned_rewards[name] = {
                            'id': str(info.get('id', '')),
                            'weight': str(info.get('probability', '1'))
                        }

                # 🌸 小鸟游野提醒：使用SQLite数据库获取全班奖品时间排序记录
                from app.common.sqlite_utils import history_manager
                
                # 获取全班奖品历史记录
                all_history = history_manager.get_reward_history(prize_pools_name)
                
                # 转换为时间排序的格式
                all_records = []
                for record in all_history:
                    reward_name = record['reward_name']
                    if reward_name in cleaned_rewards:
                        reward_info = cleaned_rewards[reward_name]
                        all_records.append([
                            record['draw_time'],
                            reward_info['id'],
                            reward_name,
                            reward_info['weight']
                        ])
                
                # 按时间降序排序
                all_records.sort(reverse=True, key=lambda x: x[0])
                
                return all_records
            else:
                return []
        
        else:
            if prize_pools_name:
                try:
                    # 🌸 小鸟游星野提醒：使用SQLite数据库获取单个奖品的历史记录
                    from app.common.sqlite_utils import history_manager
                    
                    # 直接从数据库获取该奖品的历史记录
                    reward_history = history_manager.get_reward_history(prize_pools_name, _reward_name)
                    
                    reward_data = []
                    for record in reward_history:
                        # 转换抽取方式文本
                        draw_method_map = {
                            'random': '重复抽取',
                            'until_reboot': '不重复抽取(直到软件重启)',
                            'until_all': '不重复抽取(直到抽完全部人)'
                        }
                        draw_method_text = draw_method_map.get(record['draw_method'], record['draw_method'])
                        
                        reward_data.append([
                            record['draw_time'],
                            draw_method_text,
                            str(record['draw_count'])
                        ])
                    
                    # 按时间倒序排序
                    reward_data.sort(reverse=True, key=lambda x: x[0])
                    return reward_data
                    
                except Exception as e:
                    logger.error(f"读取奖品历史记录失败: {e}")
                    InfoBar.error(
                        title="读取奖品历史记录失败",
                        content=f"错误信息: {str(e)}",
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