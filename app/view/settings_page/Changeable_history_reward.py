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
        self.scroll_area_personal = QScrollArea(self)
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
            /* 垂直滚动条整体 */
            QScrollBar:vertical {
                background-color: #E5DDF8;   /* 背景透明 */
                width: 8px;                    /* 宽度 */
                margin: 0px;                   /* 外边距 */
            }
            /* 垂直滚动条的滑块 */
            QScrollBar::handle:vertical {
                background-color: rgba(0, 0, 0, 0.3);    /* 半透明滑块 */
                border-radius: 4px;                      /* 圆角 */
                min-height: 20px;                        /* 最小高度 */
            }
            /* 鼠标悬停在滑块上 */
            QScrollBar::handle:vertical:hover {
                background-color: rgba(0, 0, 0, 0.5);
            }
            /* 滚动条的上下按钮和顶部、底部区域 */
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical,
            QScrollBar::up-arrow:vertical,
            QScrollBar::down-arrow:vertical {
                height: 0px;
            }
        
            /* 水平滚动条整体 */
            QScrollBar:horizontal {
                background-color: #E5DDF8;   /* 背景透明 */
                height: 8px;
                margin: 0px;
            }
            /* 水平滚动条的滑块 */
            QScrollBar::handle:horizontal {
                background-color: rgba(0, 0, 0, 0.3);
                border-radius: 4px;
                min-width: 20px;
            }
            /* 鼠标悬停在滑块上 */
            QScrollBar::handle:horizontal:hover {
                background-color: rgba(0, 0, 0, 0.5);
            }
            /* 滚动条的左右按钮和左侧、右侧区域 */
            QScrollBar::add-line:horizontal,
            QScrollBar::sub-line:horizontal,
            QScrollBar::left-arrow:horizontal,
            QScrollBar::right-arrow:horizontal {
                width: 0px;
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
        # 根据班级名称获取学生名单数据
        data = self.__getClassrewards()

        # 如果data为空，则显示提示信息
        # 获取当前时间
        current_time = QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm:ss")
        if not data:
            data = [[f'{current_time}', '无', '无']]

        # 获取选择的奖池和奖品名称
        prize_pools_name = self.history_setting_card.prize_pools_comboBox.currentText()
        reward_name = self.history_setting_card.reward_comboBox.currentText()

        if data:
            InfoBar.success(
                title="读取历史记录文件成功",
                content=f"读取历史记录文件成功,班级:{prize_pools_name},学生:{reward_name}",
                duration=6000,
                orient=Qt.Horizontal,
                parent=self,
                isClosable=True,
                position=InfoBarPosition.TOP
            )
        
        if reward_name == '全部奖品':
            # 设置表格行数为实际学生数量
            self.table.setRowCount(len(data))
            self.table.setSortingEnabled(False)
            self.table.setColumnCount(4)
            # 填充表格数据
            for i, row in enumerate(data):
                for j in range(4):
                    self.table.setItem(i, j, QTableWidgetItem(row[j]))
                    self.table.item(i, j).setTextAlignment(Qt.AlignmentFlag.AlignCenter) # 居中
                    self.table.item(i, j).setFont(QFont(load_custom_font(), 12)) # 设置字体
            # 设置表头
            self.table.setHorizontalHeaderLabels(['序号', '奖品', '默认权重', '总抽取次数'])
            self.table.verticalHeader().hide() # 隐藏垂直表头
            self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch) # 自适应
            
            # 添加到布局
            self.inner_layout_personal.addWidget(self.table)

            # 将内部的 QFrame 设置为 QScrollArea 的内容
            self.scroll_area_personal.setWidget(self.inner_frame_personal)

            self.table.setSortingEnabled(True) # 启用排序

            # 设置主布局
            if not self.layout():
                main_layout = QVBoxLayout(self)
                main_layout.addWidget(self.scroll_area_personal)
            else:
                # 如果已有布局，只需更新内容
                self.layout().addWidget(self.scroll_area_personal)
        else:
            self.table.setRowCount(len(data))
            self.table.setSortingEnabled(False) # 禁止排序
            self.table.setColumnCount(3)
            
            # 填充表格数据
            for i, row in enumerate(data):
                for j in range(3):
                    self.table.setItem(i, j, QTableWidgetItem(row[j]))
                    self.table.item(i, j).setTextAlignment(Qt.AlignmentFlag.AlignCenter) # 居中
                    self.table.item(i, j).setFont(QFont(load_custom_font(), 12)) # 设置字体
                    
            # 设置表头
            self.table.setHorizontalHeaderLabels(['时间', '抽取方式', '抽取时选择的奖品数'])
            self.table.verticalHeader().hide() # 隐藏垂直表头
            self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch) # 自适应
            self.table.setSortingEnabled(True) # 启用排序
            self.table.sortByColumn(0, Qt.SortOrder.DescendingOrder)
            
            # 添加到布局
            self.inner_layout_personal.addWidget(self.table)

            # 将内部的 QFrame 设置为 QScrollArea 的内容
            self.scroll_area_personal.setWidget(self.inner_frame_personal)

            # 设置主布局
            if not self.layout():
                main_layout = QVBoxLayout(self)
                main_layout.addWidget(self.scroll_area_personal)
            else:
                # 如果已有布局，只需更新内容
                self.layout().addWidget(self.scroll_area_personal)

        self.__initWidget()

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
