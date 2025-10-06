from qfluentwidgets import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import os
import json
import random
from random import SystemRandom
import asyncio

# 创建SystemRandom实例用于更安全的随机数生成
system_random = SystemRandom()
import time
import io
import pandas as pd
import shutil
import datetime
from loguru import logger

from app.common.config import get_theme_icon, load_custom_font, is_dark_theme, restore_volume
from app.common.path_utils import path_manager, open_file, ensure_dir
from app.common.voice import TTSHandler
from app.view.main_page.vocabulary_pk_settings import VocabularyPKSettingsDialog

is_dark = is_dark_theme(qconfig)

class vocabulary_learning(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # 同步初始化UI
        self.initUI()
        
    def start_auto_next_timer(self):
        """启动自动下一个单词计时器（向后兼容）"""
        # 根据当前活动的侧边启动相应的计时器
        if hasattr(self, '_active_side') and self._active_side == 'right':
            self.start_right_auto_next_timer()
        else:
            self.start_left_auto_next_timer()
            
    def start_left_auto_next_timer(self):
        """启动左侧自动下一个单词计时器"""
        # 如果已经存在左侧计时器，先停止
        if self.left_auto_next_timer is not None:
            self.left_auto_next_timer.stop()
            
        # 创建新的左侧计时器
        self.left_auto_next_timer = QTimer(self)
        self.left_auto_next_timer.timeout.connect(self._on_left_auto_next_timer_timeout)
        
        # 设置计时器间隔（毫秒）并启动
        interval = self.next_word_time * 1000  # 转换为毫秒
        self.left_auto_next_timer.start(interval)
        
    def start_right_auto_next_timer(self):
        """启动右侧自动下一个单词计时器"""
        # 如果已经存在右侧计时器，先停止
        if self.right_auto_next_timer is not None:
            self.right_auto_next_timer.stop()
            
        # 创建新的右侧计时器
        self.right_auto_next_timer = QTimer(self)
        self.right_auto_next_timer.timeout.connect(self._on_right_auto_next_timer_timeout)
        
        # 设置计时器间隔（毫秒）并启动
        interval = self.next_word_time * 1000  # 转换为毫秒
        self.right_auto_next_timer.start(interval)
        
    def stop_auto_next_timer(self):
        """停止自动下一个单词计时器"""
        if self.auto_next_timer is not None:
            self.auto_next_timer.stop()
            self.auto_next_timer = None
            
        # 停止左侧计时器
        if self.left_auto_next_timer is not None:
            self.left_auto_next_timer.stop()
            self.left_auto_next_timer = None
            
        # 停止右侧计时器
        if self.right_auto_next_timer is not None:
            self.right_auto_next_timer.stop()
            self.right_auto_next_timer = None
            
    def _on_auto_next_timer_timeout(self):
        """自动下一个单词计时器超时处理（向后兼容）"""
        # 停止计时器
        self.stop_auto_next_timer()
        
        # 根据当前活动的侧边显示下一个单词
        if hasattr(self, '_active_side') and self._active_side == 'right':
            # 如果当前活动侧边是右侧，显示右侧下一个单词
            self.show_right_next_word()
        else:
            # 默认显示左侧下一个单词
            self.show_next_word()
            
    def _on_left_auto_next_timer_timeout(self):
        """左侧自动下一个单词计时器超时处理"""
        # 停止左侧计时器
        if self.left_auto_next_timer is not None:
            self.left_auto_next_timer.stop()
            self.left_auto_next_timer = None
        
        # 显示左侧下一个单词
        self.show_next_word()
        
    def _on_right_auto_next_timer_timeout(self):
        """右侧自动下一个单词计时器超时处理"""
        # 停止右侧计时器
        if self.right_auto_next_timer is not None:
            self.right_auto_next_timer.stop()
            self.right_auto_next_timer = None
        
        # 显示右侧下一个单词
        self.show_right_next_word()
        
    def initUI(self):
        # 初始化答题统计变量
        self.left_correct_count = 0
        self.left_wrong_count = 0
        self.right_correct_count = 0
        self.right_wrong_count = 0
        self.left_skip_count = 0
        self.right_skip_count = 0

        # 初始化变量
        self.current_word_index = -1
        self.right_word_index = -1
        self.words_list = []  # 左侧词汇列表
        self.distractor_words = []  # 右侧干扰词汇
        self.answer_shown = False
        self.right_answer_shown = False
        self.is_dual_mode = False
        self.current_options = []  # 当前显示的选项
        self.correct_option_index = -1  # 正确答案的索引
        self.distractor_count = 3  # 默认设置3个干扰词汇
        self.right_current_options = []  # 右侧当前显示的选项
        self.right_correct_option_index = -1  # 右侧正确答案的索引
        self.answered_words = set()  # 已回答的单词索引集合（保留用于向后兼容）
        self.left_answered_words = set()  # 左侧已回答的单词索引集合
        self.right_answered_words = set()  # 右侧已回答的单词索引集合
        
        # 添加单词页数记录
        self.word_page_numbers = {}  # 记录每个单词的页数
        self.current_page_number = 0  # 当前页数
        self.right_page_number = 0  # 右侧当前页数
        
        # 添加学习模式控制变量
        self.learning_mode = "无尽模式"  # 默认为无尽模式
        self.repeat_mode = "不重复模式"  # 默认为重复模式
        self.total_questions = 20  # 默认总题数
        self.countdown_hours = 0  # 倒计时小时
        self.countdown_minutes = 30  # 倒计时分钟
        self.countdown_seconds = 0  # 倒计时秒
        self.timer = None  # 倒计时计时器
        self.remaining_time = 0  # 剩余时间（秒）
        self.questions_answered = 0  # 已回答题目数
        
        # 初始化当前词库变量
        self.current_vocabulary = None  # 当前选择的词库
        
        # 自动下一个单词设置
        self.auto_next = False  # 是否启用答题后自动下一个
        self.next_word_time = 3  # 下一个单词等待时间（秒）
        self.auto_next_timer = None  # 自动下一个单词的计时器
        self.left_auto_next_timer = None  # 左侧自动下一个单词的计时器
        self.right_auto_next_timer = None  # 右侧自动下一个单词的计时器
        
        # 创建主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # 创建标题
        title_label = TitleLabel("单词PK")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont(load_custom_font(), 18))
        main_layout.addWidget(title_label)
        
        # 学习状态信息
        self.learning_status_label = BodyLabel("")
        self.learning_status_label.setAlignment(Qt.AlignCenter)
        self.learning_status_label.setFont(QFont(load_custom_font(), 16))
        self.learning_status_label.setFixedHeight(20)
        main_layout.addWidget(self.learning_status_label)
        
        # 创建单词显示区域容器
        self.word_display_container = QWidget()
        word_display_layout = QHBoxLayout(self.word_display_container)
        
        # 左侧单词显示区域（单人模式或双人模式左侧）
        self.left_word_card = CardWidget()
        left_word_layout = QVBoxLayout(self.left_word_card)
        
        # 左侧答题统计信息
        self.left_stats_label = BodyLabel("正确答对0个，答错0个")
        self.left_stats_label.setAlignment(Qt.AlignCenter)
        self.left_stats_label.setFont(QFont(load_custom_font(), 14))
        self.left_stats_label.setFixedHeight(20)
        self.left_stats_label.hide()  # 默认隐藏
        left_word_layout.addWidget(self.left_stats_label)
        

        
        # 左侧单词显示区域
        left_word_area = QWidget()
        left_word_area_layout = QHBoxLayout(left_word_area)
        left_word_area_layout.setContentsMargins(0, 0, 0, 0)
        
        # 左侧单词显示
        self.left_word_label = BodyLabel("")
        self.left_word_label.setAlignment(Qt.AlignCenter)
        self.left_word_label.setFont(QFont(load_custom_font(), 18))
        self.left_word_label.setFixedHeight(40)
        left_word_area_layout.addWidget(self.left_word_label)
        
        # 左侧语音播报按钮
        self.left_voice_button = PushButton("🔊")
        self.left_voice_button.setFixedSize(50, 50)
        self.left_voice_button.setFont(QFont(load_custom_font(), 12))
        self.left_voice_button.clicked.connect(self.play_left_word_voice)
        self.left_voice_button.hide()  # 初始隐藏
        
        left_word_layout.addWidget(left_word_area)
        
        # 左侧音标显示
        self.left_phonetic_label = BodyLabel("")
        self.left_phonetic_label.setAlignment(Qt.AlignCenter)
        self.left_phonetic_label.setFont(QFont(load_custom_font(), 12))
        self.left_phonetic_label.setFixedHeight(25)
        left_word_layout.addWidget(self.left_phonetic_label)
        
        # 左侧单词释义显示
        self.left_meaning_label = BodyLabel("")
        self.left_meaning_label.setAlignment(Qt.AlignCenter)
        self.left_meaning_label.setFont(QFont(load_custom_font(), 14))
        self.left_meaning_label.setWordWrap(True)
        self.left_meaning_label.setFixedHeight(60)
        left_word_layout.addWidget(self.left_meaning_label)
        
        # 左侧示例句子显示
        self.left_example_label = BodyLabel("")
        self.left_example_label.setAlignment(Qt.AlignCenter)
        self.left_example_label.setWordWrap(True)
        self.left_example_label.setFont(QFont(load_custom_font(), 12))
        self.left_example_label.setFixedHeight(60)
        left_word_layout.addWidget(self.left_example_label)
        
        # 左侧选项按钮容器（初始隐藏）
        self.left_options_container = QWidget()
        self.left_options_layout = QVBoxLayout(self.left_options_container)
        self.left_options_layout.setSpacing(10)
        
        # 创建左侧选项按钮
        self.left_option_buttons = []
        if self.distractor_count > 0:
            for i in range(self.distractor_count + 1):  # 最多6个选项（干扰项0-5 + 正确答案）
                option_btn = PushButton(f"选项 {i+1}")
                option_btn.setFont(QFont(load_custom_font(), 12))
                option_btn.clicked.connect(lambda checked, idx=i: self.on_left_option_selected(idx))
                self.left_options_layout.addWidget(option_btn)
                self.left_option_buttons.append(option_btn)
        
            left_word_layout.addWidget(self.left_options_container)
        
        # 左侧翻页按钮区域
        self.left_page_button_container = QWidget()
        left_page_button_layout = QHBoxLayout(self.left_page_button_container)
        
        # 左侧上一个单词按钮
        self.left_prev_button = PushButton("上一个")
        self.left_prev_button.setEnabled(False)
        self.left_prev_button.setFont(QFont(load_custom_font(), 12))
        self.left_prev_button.setFixedWidth(85)
        self.left_prev_button.clicked.connect(self.show_prev_word)
        self.left_prev_button.hide()  # 默认隐藏
        left_page_button_layout.addWidget(self.left_prev_button)

        # 左侧语音播报按钮容器（放在选项和翻页布局中间）
        self.left_voice_button_container = QWidget()
        left_voice_button_layout = QHBoxLayout(self.left_voice_button_container)
        left_voice_button_layout.setAlignment(Qt.AlignCenter)
        left_voice_button_layout.addWidget(self.left_voice_button)
        left_page_button_layout.addWidget(self.left_voice_button_container)
        
        # 左侧下一个单词按钮
        self.left_next_button = PushButton("下一个")
        self.left_next_button.setEnabled(False)
        self.left_next_button.setFont(QFont(load_custom_font(), 12))
        self.left_next_button.setFixedWidth(85)
        self.left_next_button.clicked.connect(self.show_next_word)
        self.left_next_button.hide()  # 默认隐藏
        left_page_button_layout.addWidget(self.left_next_button)
        
        left_word_layout.addWidget(self.left_page_button_container)
        
        # 左侧显示答案按钮容器（初始隐藏）
        self.left_show_answer_button_container = QWidget()
        left_show_answer_button_layout = QHBoxLayout(self.left_show_answer_button_container)
        left_show_answer_button_layout.setAlignment(Qt.AlignCenter)
        
        # 左侧显示答案按钮
        self.left_show_answer_button = PrimaryPushButton("显示答案")
        self.left_show_answer_button.clicked.connect(self.show_answer)
        self.left_show_answer_button.setFont(QFont(load_custom_font(), 12))
        self.left_show_answer_button.setFixedWidth(100)
        self.left_show_answer_button.hide()  # 初始隐藏显示答案按钮
        left_show_answer_button_layout.addWidget(self.left_show_answer_button)
        left_word_layout.addWidget(self.left_show_answer_button_container)
        
        word_display_layout.addWidget(self.left_word_card)
        
        # 右侧单词显示区域（双人模式右侧）
        self.right_word_card = CardWidget()
        right_word_layout = QVBoxLayout(self.right_word_card)
        
        # 右侧答题统计信息
        self.right_stats_label = BodyLabel("正确答对0个，答错0个")
        self.right_stats_label.setAlignment(Qt.AlignCenter)
        self.right_stats_label.setFont(QFont(load_custom_font(), 14))
        self.right_stats_label.setFixedHeight(20)
        self.right_stats_label.hide()  # 默认隐藏
        right_word_layout.addWidget(self.right_stats_label)
        
        # 右侧单词显示区域
        right_word_area = QWidget()
        right_word_area_layout = QHBoxLayout(right_word_area)
        right_word_area_layout.setContentsMargins(0, 0, 0, 0)
        
        # 右侧单词显示
        self.right_word_label = BodyLabel("")
        self.right_word_label.setAlignment(Qt.AlignCenter)
        self.right_word_label.setFont(QFont(load_custom_font(), 18))
        self.right_word_label.setFixedHeight(40)
        right_word_area_layout.addWidget(self.right_word_label)
        
        # 右侧语音播报按钮
        self.right_voice_button = PushButton("🔊")
        self.right_voice_button.setFixedSize(50, 50)
        self.right_voice_button.setFont(QFont(load_custom_font(), 12))
        self.right_voice_button.clicked.connect(self.play_right_word_voice)
        self.right_voice_button.hide()  # 初始隐藏
        
        right_word_layout.addWidget(right_word_area)
        
        # 右侧音标显示
        self.right_phonetic_label = BodyLabel("")
        self.right_phonetic_label.setAlignment(Qt.AlignCenter)
        self.right_phonetic_label.setFont(QFont(load_custom_font(), 12))
        self.right_phonetic_label.setFixedHeight(25)
        right_word_layout.addWidget(self.right_phonetic_label)
        
        # 右侧单词释义显示
        self.right_meaning_label = BodyLabel("")
        self.right_meaning_label.setAlignment(Qt.AlignCenter)
        self.right_meaning_label.setFont(QFont(load_custom_font(), 14))
        self.right_meaning_label.setWordWrap(True)
        self.right_meaning_label.setFixedHeight(60)
        right_word_layout.addWidget(self.right_meaning_label)
        
        # 右侧示例句子显示
        self.right_example_label = BodyLabel("")
        self.right_example_label.setAlignment(Qt.AlignCenter)
        self.right_example_label.setWordWrap(True)
        self.right_example_label.setFont(QFont(load_custom_font(), 12))
        self.right_example_label.setFixedHeight(60)
        right_word_layout.addWidget(self.right_example_label)
        
        # 右侧选项按钮容器（初始隐藏）
        self.right_options_container = QWidget()
        self.right_options_layout = QVBoxLayout(self.right_options_container)
        self.right_options_layout.setSpacing(10)
        
        # 创建右侧选项按钮
        self.right_option_buttons = []
        if self.distractor_count > 0:
            for i in range(self.distractor_count + 1):  # 最多6个选项（干扰项0-5 + 正确答案）
                option_btn = PushButton(f"选项 {i+1}")
                option_btn.setFont(QFont(load_custom_font(), 12))
                option_btn.clicked.connect(lambda checked, idx=i: self.on_right_option_selected(idx))
                self.right_options_layout.addWidget(option_btn)
                self.right_option_buttons.append(option_btn)
        
            right_word_layout.addWidget(self.right_options_container)
        
        # 右侧翻页按钮区域
        self.right_page_button_container = QWidget()
        right_page_button_layout = QHBoxLayout(self.right_page_button_container)
        
        # 右侧上一个单词按钮
        self.right_prev_button = PushButton("上一个")
        self.right_prev_button.setEnabled(False)
        self.right_prev_button.setFont(QFont(load_custom_font(), 12))
        self.right_prev_button.setFixedWidth(85)
        self.right_prev_button.clicked.connect(self.show_right_prev_word)
        self.right_prev_button.hide()  # 默认隐藏
        right_page_button_layout.addWidget(self.right_prev_button)

        # 右侧语音播报按钮容器（放在选项和翻页布局中间）
        self.right_voice_button_container = QWidget()
        right_voice_button_layout = QHBoxLayout(self.right_voice_button_container)
        right_voice_button_layout.setAlignment(Qt.AlignCenter)
        right_voice_button_layout.addWidget(self.right_voice_button)
        right_page_button_layout.addWidget(self.right_voice_button_container)
        
        # 右侧下一个单词按钮
        self.right_next_button = PushButton("下一个")
        self.right_next_button.setEnabled(False)
        self.right_next_button.setFont(QFont(load_custom_font(), 12))
        self.right_next_button.setFixedWidth(85)
        self.right_next_button.clicked.connect(self.show_right_next_word)
        self.right_next_button.hide()  # 默认隐藏
        right_page_button_layout.addWidget(self.right_next_button)
        
        right_word_layout.addWidget(self.right_page_button_container)
        
        # 右侧显示答案按钮容器（初始隐藏）
        self.right_show_answer_button_container = QWidget()
        right_show_answer_button_layout = QHBoxLayout(self.right_show_answer_button_container)
        right_show_answer_button_layout.setAlignment(Qt.AlignCenter)
        
        # 右侧显示答案按钮
        self.right_show_answer_button = PrimaryPushButton("显示答案")
        self.right_show_answer_button.clicked.connect(self.show_right_answer)
        self.right_show_answer_button.setFont(QFont(load_custom_font(), 12))
        self.right_show_answer_button.setFixedWidth(100)
        self.right_show_answer_button.hide()  # 初始隐藏显示答案按钮
        right_show_answer_button_layout.addWidget(self.right_show_answer_button)
        right_word_layout.addWidget(self.right_show_answer_button_container)
        
        word_display_layout.addWidget(self.right_word_card)
        
        # 初始隐藏右侧区域
        self.right_word_card.hide()
        
        main_layout.addWidget(self.word_display_container)
        
        # 为了向后兼容，创建原始标签的引用
        self.word_label = self.left_word_label
        self.phonetic_label = self.left_phonetic_label
        self.meaning_label = self.left_meaning_label
        self.example_label = self.left_example_label
        self.word_card = self.left_word_card
        
        # 为了向后兼容，创建原始按钮的引用
        self.prev_button = self.left_prev_button
        self.next_button = self.left_next_button
        self.show_answer_button = self.left_show_answer_button
        self.button_container = self.left_page_button_container
        
        # 创建选项按钮容器（初始隐藏）- 用于向后兼容
        self.options_container = QWidget()
        self.options_container.hide()  # 初始隐藏
        
        # 添加弹性空间（将控制区域和导入区域推到底部）
        main_layout.addStretch()
        
        # 创建控制区域（将设置按钮移到底部）
        control_layout = QHBoxLayout()
        
        # 开始学习按钮
        self.start_button = PrimaryPushButton("开始学习")
        self.start_button.clicked.connect(self.start_learning)
        self.start_button.setFont(QFont(load_custom_font(), 12))
        self.start_button.setEnabled(True)  # 默认启用按钮
        control_layout.addWidget(self.start_button)
        
        # 左侧pass按钮（初始隐藏）
        self.left_pass_button = PushButton("跳过")
        self.left_pass_button.clicked.connect(self.pass_left_word)
        self.left_pass_button.setFont(QFont(load_custom_font(), 12))
        self.left_pass_button.hide()  # 初始隐藏
        control_layout.addWidget(self.left_pass_button)
        
        # 重新再来按钮（初始隐藏）
        self.restart_button = PushButton("重新再来")
        self.restart_button.clicked.connect(self.restart_learning)
        self.restart_button.setFont(QFont(load_custom_font(), 12))
        self.restart_button.hide()  # 初始隐藏
        control_layout.addWidget(self.restart_button)
        
        # 右侧pass按钮（初始隐藏，双人模式使用）
        self.right_pass_button = PushButton("跳过")
        self.right_pass_button.clicked.connect(self.pass_right_word)
        self.right_pass_button.setFont(QFont(load_custom_font(), 12))
        self.right_pass_button.hide()  # 初始隐藏
        control_layout.addWidget(self.right_pass_button)
        
        # 为了向后兼容，创建原始pass按钮的引用
        self.pass_button = self.left_pass_button
        
        # 单词PK设置按钮
        self.settings_button = PushButton("单词PK设置")
        self.settings_button.clicked.connect(self.open_settings_dialog)
        self.settings_button.setFont(QFont(load_custom_font(), 12))
        self.settings_button.setFixedWidth(120)
        control_layout.addWidget(self.settings_button)
        
        # 添加一些间距
        control_layout.setSpacing(10)
        main_layout.addLayout(control_layout)
        
        # 加载已保存的设置
        self.load_settings()
        
        # 获取可用的词汇文件列表
        available_vocabularies = self.get_available_vocabularies()
        
        # 优先加载当前选择的词库，如果没有则加载第一个可用词库
        if hasattr(self, 'current_vocabulary') and self.current_vocabulary and self.current_vocabulary in available_vocabularies:
            self.load_vocabulary(self.current_vocabulary)
        elif available_vocabularies:
            self.load_vocabulary(available_vocabularies[0])
            self.current_vocabulary = available_vocabularies[0]
        else:
            # 否则加载默认词库
            self.load_vocabulary()
        
    def get_available_vocabularies(self):
        """获取可用的词汇文件列表"""
        vocabularies = []
        documents_dir = path_manager.get_absolute_path('app/resource/documents')
        
        # 检查目录是否存在
        if not documents_dir.exists():
            logger.error(f"词库目录不存在: {documents_dir}")
            return vocabularies
            
        # 遍历目录中的文件
        for file_path in documents_dir.iterdir():
            # 跳过配置文件
            if file_path.name == 'vocabulary_mapping.json':
                continue
                
            # 检查文件扩展名
            if file_path.suffix in ['.xlsx', '.xls', '.csv']:
                # 获取文件名（不含扩展名）作为词库名称
                vocabulary_name = file_path.stem
                vocabularies.append(vocabulary_name)
                
        return vocabularies
        
    def refresh_vocabulary_combo(self):
        """刷新词库"""
        # 获取可用的词汇文件列表
        available_vocabularies = self.get_available_vocabularies()
        
        # 如果没有可用的词汇文件，使用默认选项
        if not available_vocabularies:
            available_vocabularies = ["未添加词库"]
            
        # 加载第一个可用的词库，如果没有可用词库则加载默认词库
        if available_vocabularies and available_vocabularies[0] != "未添加词库":
            self.load_vocabulary(available_vocabularies[0])
            # 保存当前词库
            self.current_vocabulary = available_vocabularies[0]
        else:
            self.load_vocabulary()
         
    def open_settings_dialog(self):
        """打开单词PK设置对话框"""
        # 准备当前设置
        current_settings = {
            'distractor_count': self.distractor_count,
            'repeat_mode': self.repeat_mode,
            'learning_mode': self.learning_mode,
            'total_questions': self.total_questions,
            'countdown_hours': self.countdown_hours,
            'countdown_minutes': self.countdown_minutes,
            'countdown_seconds': self.countdown_seconds,
            'available_vocabularies': self.get_available_vocabularies(),
            'current_vocabulary': self.current_vocabulary if hasattr(self, 'current_vocabulary') else None,
            'player_mode': "双人模式" if self.is_dual_mode else "单人模式",
            'mode': "随机学习",  # 默认随机学习模式
            'auto_next': self.auto_next,
            'next_word_time': self.next_word_time
        }
        
        # 创建并显示设置对话框
        dialog = VocabularyPKSettingsDialog(self, current_settings)
        if dialog.exec_() == QDialog.Accepted:
            # 获取新设置
            new_settings = dialog.get_settings()
            
            # 应用新设置
            self.apply_settings(new_settings)
            
            # 显示设置已应用的提示
            InfoBar.success(
                title="设置已应用",
                content="单词PK设置已成功更新",
                duration=2000,
                parent=self
            )
    
    def load_settings(self):
        """从Settings文件夹加载设置"""
        logger.info("开始加载单词PK设置")
        
        try:
            # 获取Settings目录路径
            settings_dir = path_manager.get_absolute_path('app/Settings')
            settings_file = settings_dir / 'vocabulary_pk_settings.json'
            
            # 如果设置文件存在，则加载设置
            if settings_file.exists():
                with open_file(settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    
                # 应用加载的设置
                if 'distractor_count' in settings:
                    self.distractor_count = settings['distractor_count']
                    self.update_option_buttons_count()
                    
                if 'repeat_mode' in settings:
                    self.repeat_mode = settings['repeat_mode']
                    
                if 'learning_mode' in settings:
                    self.learning_mode = settings['learning_mode']
                    
                if 'total_questions' in settings:
                    self.total_questions = settings['total_questions']
                    
                if 'countdown_hours' in settings:
                    self.countdown_hours = settings['countdown_hours']
                    
                if 'countdown_minutes' in settings:
                    self.countdown_minutes = settings['countdown_minutes']
                    
                if 'countdown_seconds' in settings:
                    self.countdown_seconds = settings['countdown_seconds']
                    
                if 'player_mode' in settings:
                    player_mode = settings['player_mode']
                    if player_mode == "双人模式":
                        self.is_dual_mode = True
                        # 显示右侧区域
                        self.right_word_card.show()
                        # 默认隐藏右侧学习状态标签，开始学习时再显示
                        self.right_stats_label.hide()
                        # 重置右侧答案状态
                        self.right_answer_shown = False
                    else:
                        self.is_dual_mode = False
                        # 隐藏右侧区域
                        self.right_word_card.hide()
                        # 隐藏右侧学习状态标签
                        self.right_stats_label.hide()
                        # 重置左侧答案状态
                        self.answer_shown = False
                        
                if 'current_vocabulary' in settings and settings['current_vocabulary']:
                    self.current_vocabulary = settings['current_vocabulary']
                    # 注意：这里不再立即加载词库，而是由异步方法负责加载
                
                if 'auto_next' in settings:
                    self.auto_next = settings['auto_next']
                    
                if 'next_word_time' in settings:
                    self.next_word_time = settings['next_word_time']
                return True
            else:
                return False
        except Exception as e:
            return False
    
    def save_settings(self):
        """保存当前设置到Settings文件夹"""
        settings = {
            'distractor_count': self.distractor_count,
            'repeat_mode': self.repeat_mode,
            'learning_mode': self.learning_mode,
            'total_questions': self.total_questions,
            'countdown_hours': self.countdown_hours,
            'countdown_minutes': self.countdown_minutes,
            'countdown_seconds': self.countdown_seconds,
            'player_mode': "双人模式" if self.is_dual_mode else "单人模式",
            'current_vocabulary': self.current_vocabulary if hasattr(self, 'current_vocabulary') else None,
            'auto_next': self.auto_next,
            'next_word_time': self.next_word_time
        }
        
        try:
            # 确保Settings目录存在
            settings_dir = path_manager.get_absolute_path('app/Settings')
            ensure_dir(settings_dir)
            
            # 保存设置到vocabulary_pk_settings.json文件
            settings_file = settings_dir / 'vocabulary_pk_settings.json'
            with open_file(settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=4)
                
            logger.info("单词PK设置已保存")
            return True
        except Exception as e:
            logger.error(f"保存单词PK设置失败: {e}")
            return False
    
    def apply_settings(self, settings):
        """应用设置到主界面"""
        # 应用干扰词汇数量设置
        if 'distractor_count' in settings and settings['distractor_count'] != self.distractor_count:
            self.distractor_count = settings['distractor_count']
            # 更新选项按钮数量
            self.update_option_buttons_count()
        
        # 应用重复模式设置
        if 'repeat_mode' in settings:
            self.repeat_mode = settings['repeat_mode']
        
        # 应用学习模式设置
        if 'learning_mode' in settings and settings['learning_mode'] != self.learning_mode:
            self.learning_mode = settings['learning_mode']
        
        # 应用总题数设置
        if 'total_questions' in settings:
            self.total_questions = settings['total_questions']
        
        # 应用倒计时设置
        if 'countdown_hours' in settings:
            self.countdown_hours = settings['countdown_hours']
        
        if 'countdown_minutes' in settings:
            self.countdown_minutes = settings['countdown_minutes']
        
        if 'countdown_seconds' in settings:
            self.countdown_seconds = settings['countdown_seconds']
        
        # 应用玩家模式设置
        if 'player_mode' in settings:
            player_mode = settings['player_mode']
            if player_mode == "双人模式":
                self.is_dual_mode = True
                # 显示右侧区域
                self.right_word_card.show()
                # 默认隐藏右侧学习状态标签，开始学习时再显示
                self.right_stats_label.hide()
                # 重置右侧答案状态
                self.right_answer_shown = False
            else:
                self.is_dual_mode = False
                # 隐藏右侧区域
                self.right_word_card.hide()
                # 隐藏右侧学习状态标签
                self.right_stats_label.hide()
                # 重置左侧答案状态
                self.answer_shown = False
        
        # 应用词库设置
        if 'current_vocabulary' in settings:
            # 获取可用词库列表
            available_vocabularies = self.get_available_vocabularies()
            # 检查选择的词库是否有效
            if settings['current_vocabulary'] and settings['current_vocabulary'] in available_vocabularies:
                # 保存当前选择的词库
                self.current_vocabulary = settings['current_vocabulary']
                # 重新加载词库
                self.load_vocabulary(self.current_vocabulary)
                # 显示词库加载成功的提示
                InfoBar.success(
                    title="词库已更新",
                    content=f"已成功加载词库: {self.current_vocabulary}",
                    duration=2000,
                    parent=self
                )
            else:
                # 如果词库无效，显示错误提示
                InfoBar.error(
                    title="词库加载失败",
                    content=f"无法加载词库: {settings['current_vocabulary']}，请检查词库文件是否存在",
                    duration=3000,
                    parent=self
                )
        
        # 应用自动下一个单词设置
        if 'auto_next' in settings:
            self.auto_next = settings['auto_next']
            
        if 'next_word_time' in settings:
            self.next_word_time = settings['next_word_time']
            # 确保时间在合理范围内（1-120秒）
            self.next_word_time = max(1, min(120, self.next_word_time))
        
        # 保存设置到文件
        self.save_settings()
    
    def update_option_buttons_count(self):
        """更新选项按钮数量"""
        # 如果当前正在学习中，需要先停止学习
        if self.current_word_index >= 0 or self.right_word_index >= 0:
            # 显示提示
            InfoBar.info(
                title="提示",
                content="更改干扰词汇数量需要重新开始学习",
                duration=3000,
                parent=self
            )
            return
        
        # 更新左侧选项按钮
        self.update_side_option_buttons_count(self.left_option_buttons, self.left_options_layout)
        
        # 更新右侧选项按钮
        self.update_side_option_buttons_count(self.right_option_buttons, self.right_options_layout)
    
    def update_side_option_buttons_count(self, option_buttons, options_layout):
        """更新单侧选项按钮数量"""
        current_count = len(option_buttons)
        target_count = self.distractor_count + 1  # 干扰项数量 + 正确答案
        
        if current_count < target_count:
            # 需要添加按钮
            for i in range(current_count, target_count):
                option_btn = PushButton(f"选项 {i+1}")
                option_btn.setFont(QFont(load_custom_font(), 12))
                
                # 根据是左侧还是右侧按钮设置不同的点击事件
                if option_buttons == self.left_option_buttons:
                    option_btn.clicked.connect(lambda checked, idx=i: self.on_left_option_selected(idx))
                else:
                    option_btn.clicked.connect(lambda checked, idx=i: self.on_right_option_selected(idx))
                
                options_layout.addWidget(option_btn)
                option_buttons.append(option_btn)
        elif current_count > target_count:
            # 需要移除按钮
            for i in range(current_count - 1, target_count - 1, -1):
                option_buttons[i].hide()
                options_layout.removeWidget(option_buttons[i])
                option_buttons[i].deleteLater()
                option_buttons.pop(i)
    
    def delete_vocabulary(self, vocabulary_name):
        """删除指定的词汇库"""
        try:
            # 获取documents目录路径
            documents_dir = path_manager.get_absolute_path('app/resource/documents')
            
            # 尝试不同格式的文件
            file_extensions = ['.xlsx', '.xls', '.csv']
            file_deleted = False
            
            for ext in file_extensions:
                file_path = documents_dir / f'{vocabulary_name}{ext}'
                if file_path.exists():
                    # 删除文件
                    file_path.unlink()
                    file_deleted = True
                    logger.info(f"已删除词汇库文件: {file_path}")
                    break
            
            # 如果没有找到文件，返回失败
            if not file_deleted:
                logger.error(f"未找到词汇库文件: {vocabulary_name}")
                return False
            
            # 从vocabulary_mapping.json中删除对应的映射配置
            mapping_file = documents_dir / 'vocabulary_mapping.json'
            if mapping_file.exists():
                try:
                    with open_file(mapping_file, 'r', encoding='utf-8') as f:
                        mapping_data = json.load(f)
                    
                    # 如果存在该词库的映射配置，则删除
                    if vocabulary_name in mapping_data:
                        del mapping_data[vocabulary_name]
                        logger.info(f"已从映射配置中删除词库: {vocabulary_name}")
                        
                        # 保存更新后的映射配置
                        with open_file(mapping_file, 'w', encoding='utf-8') as f:
                            json.dump(mapping_data, f, ensure_ascii=False, indent=2)
                        logger.info("已更新词汇库映射配置文件")
                except Exception as e:
                    logger.error(f"更新词汇库映射配置失败: {e}")
            
            # 检查是否删除的是当前使用的词库
            if hasattr(self, 'current_vocabulary') and self.current_vocabulary == vocabulary_name:
                # 重置当前词库
                self.current_vocabulary = None
                # 清空词库列表
                self.words_list = []
                # 重置学习状态
                self.current_word_index = -1
                self.answer_shown = False
                self.prev_button.setEnabled(False)
                self.next_button.setEnabled(False)
                self.show_answer_button.setEnabled(False)
                # 重置显示
                self.word_label.setText("")
                self.phonetic_label.setText("")
                self.meaning_label.setText("")
                self.example_label.setText("")
                # 隐藏选项按钮
                for btn in self.left_option_buttons:
                    btn.setVisible(False)
                for btn in self.right_option_buttons:
                    btn.setVisible(False)
                # 隐藏语音播报按钮
                self.left_voice_button.hide()
                self.right_voice_button.hide()
                # 隐藏统计标签
                self.left_stats_label.hide()
                self.right_stats_label.hide()
                # 重置学习状态标签
                self.learning_status_label.setText("")
                
                # 如果是双人模式，同样重置右侧
                if self.is_dual_mode:
                    self.right_word_index = -1
                    self.right_answer_shown = False
                    self.right_prev_button.setEnabled(False)
                    self.right_next_button.setEnabled(False)
                    self.right_show_answer_button.setEnabled(False)
                    self.right_word_label.setText("")
                    self.right_phonetic_label.setText("")
                    self.right_meaning_label.setText("")
                    self.right_example_label.setText("")
            
            # 更新设置中的当前词库
            if hasattr(self, 'current_vocabulary') and self.current_vocabulary == vocabulary_name:
                # 获取可用词库列表
                available_vocabularies = self.get_available_vocabularies()
                if available_vocabularies and available_vocabularies[0] != "未添加词库":
                    # 如果还有其他词库，加载第一个
                    self.current_vocabulary = available_vocabularies[0]
                    self.load_vocabulary(self.current_vocabulary)
                else:
                    # 如果没有其他词库，重置为None
                    self.current_vocabulary = None
                
                # 保存设置
                self.save_settings()
            
            return True
        except Exception as e:
            logger.error(f"删除词汇库失败: {e}")
            return False
    
    def load_vocabulary(self, vocabulary_type=None):
        """从文件加载词库"""
        # 停止自动下一个单词的计时器（如果有）
        self.stop_auto_next_timer()
        
        # 如果没有指定词库类型，使用默认词库类型
        if vocabulary_type is None:
            vocabulary_type = "未添加词库"  # 默认词库
        
        # 检查documents目录是否存在
        documents_dir = path_manager.get_absolute_path('app/resource/documents')
        
        # 尝试加载列映射配置
        mapping_file = documents_dir / 'vocabulary_mapping.json'
        
        if mapping_file.exists():
            try:
                with open_file(mapping_file, 'r', encoding='utf-8') as f:
                    mapping_data = json.load(f)
                    # 获取当前词库的列映射配置
                    if vocabulary_type in mapping_data:
                        column_mapping = mapping_data[vocabulary_type].get('column_mapping', None)
            except Exception as e:
                logger.error(f"加载列映射配置失败: {e}")
        
        # 尝试不同格式的文件
        file_extensions = ['.xlsx', '.xls', '.csv']
        vocabulary_file = None
        file_extension = None
        
        for ext in file_extensions:
            file_path = documents_dir / f'{vocabulary_type}{ext}'
            if file_path.exists():
                vocabulary_file = file_path
                file_extension = ext
                break
        
        try:
            # 检查文件是否存在
            if vocabulary_file:
                with open(f'app/resource/documents/{vocabulary_type}{file_extension}', 'rb') as f:
                    # 读取二进制数据
                    content = f.read()
                    # 根据文件扩展名使用不同的读取方法
                    if file_extension in ['.xlsx', '.xls']:
                        # 使用BytesIO将二进制数据转换为文件对象
                        df = pd.read_excel(io.BytesIO(content))
                    elif file_extension == '.csv':
                        # 尝试不同编码读取CSV文件
                        try:
                            # 尝试UTF-8解码
                            text = content.decode('utf-8')
                            # 使用StringIO将文本转换为文件对象
                            df = pd.read_csv(io.StringIO(text))
                        except UnicodeDecodeError:
                            # 尝试GBK解码
                            text = content.decode('gbk')
                            df = pd.read_csv(io.StringIO(text))
                        except Exception as e:
                            logger.error(f"读取CSV文件失败: {e}")
                            df = pd.DataFrame()
                    
                    # 将数据转换为单词列表
                    self.words_list = []
                    
                    # 如果有列映射配置，使用列映射
                    if column_mapping:
                        word_col = column_mapping.get('单词', -1)
                        phonetic_col = column_mapping.get('音标', -1)
                        meaning_col = column_mapping.get('释义', -1)
                        example_col = column_mapping.get('例句', -1)
                        
                        for _, row in df.iterrows():
                            word_data = {
                                "word": str(row.iloc[word_col]).strip() if word_col != -1 and word_col < len(row) else "",
                                "phonetic": str(row.iloc[phonetic_col]).strip() if phonetic_col != -1 and phonetic_col < len(row) else "",
                                "meaning": str(row.iloc[meaning_col]).strip() if meaning_col != -1 and meaning_col < len(row) else "",
                                "example": str(row.iloc[example_col]).strip() if example_col != -1 and example_col < len(row) else ""
                            }
                            # 确保单词和释义不为空
                            if word_data["word"] and word_data["meaning"]:
                                self.words_list.append(word_data)
                    else:
                        # 没有列映射配置，使用默认列名
                        for _, row in df.iterrows():
                            word_data = {
                                "word": row.get('单词', ''),
                                "phonetic": row.get('音标', ''),
                                "meaning": row.get('释义', ''),
                                "example": row.get('例句', '')
                            }
                            # 确保单词和释义不为空
                            if word_data["word"] and word_data["meaning"]:
                                self.words_list.append(word_data)
            else:
                if not vocabulary_type == "未添加词库":
                    logger.info(f"{vocabulary_type}文件不存在")
                    self.words_list = []
                else:
                    self.words_list = []
                
        except Exception as e:
            logger.error(f"加载{vocabulary_type}失败: {e}")
            self.words_list = []
            
        # 重置学习状态
        self.current_word_index = -1
        self.answer_shown = False
        self.prev_button.setEnabled(False)
        self.next_button.setEnabled(False)
        self.show_answer_button.setEnabled(False)
        
        # 重置显示
        self.word_label.setText("")
        self.phonetic_label.setText("")
        self.meaning_label.setText("")
        self.example_label.setText("")
        
        # 隐藏选项按钮
        for btn in self.left_option_buttons:
            btn.setVisible(False)
        for btn in self.right_option_buttons:
            btn.setVisible(False)
            
        # 隐藏语音播报按钮
        self.left_voice_button.hide()
        self.right_voice_button.hide()
        
    def start_learning(self):
        """开始学习"""
        # 停止自动下一个单词的计时器（如果有）
        self.stop_auto_next_timer()
        
        # 重置答题统计变量
        self.left_correct_count = 0
        self.left_wrong_count = 0
        self.right_correct_count = 0
        self.right_wrong_count = 0
        
        # 更新统计标签显示
        self.left_stats_label.setText("正确答对0个，答错0个")
        self.right_stats_label.setText("正确答对0个，答错0个")
        
        # 显示统计标签
        self.left_stats_label.show()
        self.right_stats_label.show()
        
        # 清空已回答单词的集合
        self.answered_words.clear()
        self.left_answered_words.clear()
        self.right_answered_words.clear()
        
        # 重置页数记录
        self.word_page_numbers.clear()
        self.current_page_number = 0
        self.right_page_number = 0
        
        # 根据学习模式初始化相关变量
        if self.learning_mode == "总题数模式":
            # 重置已回答题目数
            self.questions_answered = 0
            # 更新学习状态显示
            self.learning_status_label.setText(f"总题数: {self.total_questions} | 已答题: 0")
            
            # 重置答题记录
            self.answer_records = {}
        elif self.learning_mode == "倒计时模式":
            # 停止之前的计时器（如果有）
            if hasattr(self, 'timer') and self.timer is not None and self.timer.isActive():
                self.timer.stop()
            
            # 计算总秒数
            total_seconds = self.countdown_hours * 3600 + self.countdown_minutes * 60 + self.countdown_seconds
            self.remaining_time = total_seconds
            
            # 更新学习状态显示
            hours = self.remaining_time // 3600
            minutes = (self.remaining_time % 3600) // 60
            seconds = self.remaining_time % 60
            self.learning_status_label.setText(f"剩余时间: {hours:02d}:{minutes:02d}:{seconds:02d}")
            
            # 创建并启动计时器
            self.timer = QTimer()
            self.timer.timeout.connect(self.update_countdown)
            self.timer.start(1000)  # 每秒更新一次
            
            # 重置答题记录
            self.answer_records = {}
        else:  # 无尽模式
            # 重置已回答题目数
            self.questions_answered = 0
            # 更新学习状态显示
            self.learning_status_label.setText(f"无尽模式 | 已答题: 0")
            
            # 重置答题记录
            self.answer_records = {}
            
        # 重置已回答单词集合
        self.left_answered_words.clear()
        self.right_answered_words.clear()
        
        # 加载当前选择的词库
        if hasattr(self, 'current_vocabulary') and self.current_vocabulary:
            self.load_vocabulary(self.current_vocabulary)
        else:
            self.load_vocabulary()
        
        if not self.words_list:
            self.word_label.setText("词库为空，请选择其他词库")
            InfoBar.warning(
                title="词库为空",
                content="当前词库为空，请先导入词库或选择其他词库",
                duration=3000,
                parent=self
            )
            return
            
        # 随机打乱词汇表
        system_random.shuffle(self.words_list)
            
        # 显示第一个单词
        self.current_word_index = 0
        self.show_word()
        
        # 显示按钮
        self.next_button.show()  # 显示下一个按钮
        self.prev_button.show()  # 显示上一个按钮
        # 只有在没有设置干扰词汇时才启用显示答案按钮
        if hasattr(self, 'distractor_count') and self.distractor_count > 0:
            self.show_answer_button.setEnabled(False)
        else:
            self.show_answer_button.setEnabled(True)
            
        # 隐藏开始学习按钮，显示pass按钮和重新再来按钮
        self.start_button.hide()
        self.restart_button.show()
        
        # 根据模式显示pass按钮
        if self.is_dual_mode:
            # 双人模式：显示两个pass按钮，并添加左右标记
            self.left_pass_button.setText("跳过(左)")
            self.left_pass_button.show()
            self.right_pass_button.setText("跳过(右)")
            self.right_pass_button.show()
        else:
            # 单人模式：只显示左侧pass按钮，文本为"跳过"
            self.left_pass_button.setText("跳过")
            self.left_pass_button.show()
            self.right_pass_button.hide()
        
        # 如果是双人模式，初始化右侧
        if self.is_dual_mode:
            # 创建两份打乱的词汇表，分别用于左右两侧
            self.left_words_list = self.words_list.copy()
            self.right_words_list = self.words_list.copy()
            
            # 打乱两份词汇表
            system_random.shuffle(self.left_words_list)
            system_random.shuffle(self.right_words_list)
            
            # 确保两侧第一个单词不同（如果词汇表长度大于1）
            if len(self.words_list) > 1 and self.left_words_list[0] == self.right_words_list[0]:
                # 如果相同，交换右侧词汇表中的第一个和第二个元素
                if len(self.right_words_list) > 1:
                    self.right_words_list[0], self.right_words_list[1] = self.right_words_list[1], self.right_words_list[0]
            
            # 重置两侧索引
            self.current_word_index = 0
            self.right_word_index = 0
            
            # 更新左侧显示
            self.show_word()
            self.show_right_word()
            # 只有在没有设置干扰词汇时才启用右侧显示答案按钮
            if hasattr(self, 'distractor_count') and self.distractor_count > 0:
                self.right_show_answer_button.setEnabled(False)
            else:
                self.right_show_answer_button.setEnabled(True)
            
            # 显示右侧按钮
            self.right_next_button.show()
            self.right_prev_button.show()
        
    def pass_left_word(self):
        """跳过左侧单词"""
        try:
            # 根据模式选择使用的词汇表
            words_list = self.left_words_list if self.is_dual_mode and hasattr(self, 'left_words_list') else self.words_list
            
            # 记录当前单词的答题信息（跳过）
            if 0 <= self.current_word_index < len(words_list):
                word = words_list[self.current_word_index]
                
                # 保存答题的选项记录信息
                if not hasattr(self, 'answer_records'):
                    self.answer_records = {}
                
                # 检查是否已经有答题记录
                if self.current_word_index not in self.answer_records:
                    # 如果没有答题记录，则创建跳过记录
                    self.answer_records[self.current_word_index] = {
                        'word': word['word'],
                        'meaning': word['meaning'],
                        'selected_option': -1,  # -1表示跳过
                        'correct_option': self.correct_option_index if hasattr(self, 'correct_option_index') else 0,
                        'is_correct': False,  # 跳过视为不正确
                        'is_skipped': True,  # 标记为跳过
                        'options': self.current_options.copy() if hasattr(self, 'current_options') else [{'meaning': word['meaning'], 'is_correct': True}]
                    }
                else:
                    # 如果已经有答题记录，保留原有记录，只添加跳过标记
                    self.answer_records[self.current_word_index]['is_skipped'] = True
                
                # 更新左侧答题统计（跳过不计入错误，但计入已答题数）
                # 添加跳过计数
                if not hasattr(self, 'left_skip_count'):
                    self.left_skip_count = 0
                self.left_skip_count += 1
                self.left_stats_label.setText(f"正确答对{self.left_correct_count}个，答错{self.left_wrong_count}个，跳过{self.left_skip_count}个")
                
                # 更新已答题数（如果是总题数模式或无尽模式）
                if self.learning_mode == "总题数模式" or self.learning_mode == "无尽模式":
                    self.questions_answered += 1
                    self.update_learning_status()
                    
                    # 检查是否达到总题数（仅总题数模式）
                    if self.learning_mode == "总题数模式" and self.questions_answered >= self.total_questions:
                        # 显示提示
                        InfoBar.info(
                            title="学习结束",
                            content=f"已完成{self.questions_answered}道题目，学习完成！",
                            duration=3000,
                            parent=self
                        )
                        
                        # 禁用答题按钮
                        self.next_button.setEnabled(False)
                        self.show_answer_button.setEnabled(False)
                        
                        # 如果是双人模式，也禁用右侧按钮
                        if self.is_dual_mode:
                            self.right_next_button.setEnabled(False)
                            self.right_show_answer_button.setEnabled(False)
            
            # 左侧索引增加
            self.current_word_index += 1
            
            # 检查是否超出词汇表范围
            if self.current_word_index >= len(words_list):
                # 如果超出范围，重新打乱词汇表
                system_random.shuffle(words_list)
                self.current_word_index = 0
                
                # 如果是双人模式，更新左侧词汇表
                if self.is_dual_mode and hasattr(self, 'left_words_list'):
                    self.left_words_list = words_list
            
            # 显示左侧下一个单词
            self.show_word()
            
            # 重置答案显示状态
            self.answer_shown = False
            
            # 根据干扰词汇设置更新显示答案按钮状态
            if hasattr(self, 'distractor_count') and self.distractor_count > 0:
                self.show_answer_button.setEnabled(False)
            else:
                self.show_answer_button.setEnabled(True)
                    
        except Exception as e:
            logger.error(f"跳过左侧单词失败: {e}")
    
    def pass_right_word(self):
        """跳过右侧单词"""
        try:
            # 如果是双人模式，跳过右侧单词
            if self.is_dual_mode and hasattr(self, 'right_words_list') and 0 <= self.right_word_index < len(self.right_words_list):
                # 记录右侧单词的答题信息（跳过）
                right_word = self.right_words_list[self.right_word_index]
                
                # 保存答题的选项记录信息
                if not hasattr(self, 'answer_records'):
                    self.answer_records = {}
                
                # 检查是否已经有答题记录
                right_key = f"right_{self.right_word_index}"
                if right_key not in self.answer_records:
                    # 如果没有答题记录，则创建跳过记录
                    self.answer_records[right_key] = {
                        'word': right_word['word'],
                        'meaning': right_word['meaning'],
                        'selected_option': -1,  # -1表示跳过
                        'correct_option': 0,
                        'is_correct': False,  # 跳过视为不正确
                        'is_skipped': True,  # 标记为跳过
                        'is_right': True,  # 标记为右侧单词
                        'options': [{'meaning': right_word['meaning'], 'is_correct': True}]
                    }
                else:
                    # 如果已经有答题记录，保留原有记录，只添加跳过标记
                    self.answer_records[right_key]['is_skipped'] = True
                
                # 更新右侧答题统计（跳过不计入错误，但计入已答题数）
                # 添加跳过计数
                if not hasattr(self, 'right_skip_count'):
                    self.right_skip_count = 0
                self.right_skip_count += 1
                self.right_stats_label.setText(f"正确答对{self.right_correct_count}个，答错{self.right_wrong_count}个，跳过{self.right_skip_count}个")
                
                # 右侧索引增加
                self.right_word_index += 1
                
                # 检查是否超出词汇表范围
                if self.right_word_index >= len(self.right_words_list):
                    # 如果超出范围，重新打乱词汇表
                    system_random.shuffle(self.right_words_list)
                    self.right_word_index = 0
                
                # 显示右侧下一个单词
                self.show_right_word()
                
                # 重置右侧答案显示状态
                if hasattr(self, 'right_answer_shown'):
                    self.right_answer_shown = False
                
                # 根据干扰词汇设置更新右侧显示答案按钮状态
                if hasattr(self, 'distractor_count') and self.distractor_count > 0:
                    self.right_show_answer_button.setEnabled(False)
                else:
                    self.right_show_answer_button.setEnabled(True)
                    
        except Exception as e:
            logger.error(f"跳过右侧单词失败: {e}")
    
    def pass_current_word(self):
        """跳过当前单词（为了向后兼容）"""
        # 在单人模式下，调用左侧单词跳过方法
        if not self.is_dual_mode:
            self.pass_left_word()
        else:
            # 在双人模式下，同时跳过左右两侧单词
            self.pass_left_word()
            self.pass_right_word()
    
    def restart_learning(self):
        """重新触发开始学习流程"""
        try:
            # 停止计时器（如果有）
            if hasattr(self, 'timer') and self.timer is not None and self.timer.isActive():
                self.timer.stop()
            
            # 停止自动下一个单词的计时器（如果有）
            self.stop_auto_next_timer()
            
            # 重新调用开始学习方法
            self.start_learning()
            
        except Exception as e:
            logger.error(f"重新开始学习失败: {e}")
    
    def play_left_word_voice(self):
        """播报左侧单词"""
        try:
            # 根据模式选择使用的词汇表
            words_list = self.left_words_list if self.is_dual_mode and hasattr(self, 'left_words_list') else self.words_list
            
            if 0 <= self.current_word_index < len(words_list):
                word = words_list[self.current_word_index]
                word_text = word["word"]
                
                # 获取语音配置
                with open_file(path_manager.get_voice_engine_path(), 'r', encoding='utf-8') as f:
                    voice_config = json.load(f)
                    voice_engine = voice_config['voice_engine']['voice_engine']
                    edge_tts_voice_name = voice_config['voice_engine']['edge_tts_voice_name']
                    voice_enabled = voice_config['voice_engine']['voice_enabled']
                    system_volume_enabled = voice_config['voice_engine']['system_volume_enabled']
                    voice_volume = voice_config['voice_engine'].get('voice_volume', 100) / 100.0
                    voice_speed = voice_config['voice_engine'].get('voice_speed', 100)
                    volume_value = voice_config['voice_engine'].get('system_volume_value', 50)

                if voice_enabled == True:  # 开启语音
                    if system_volume_enabled == True: # 开启系统音量
                        from app.common.voice import restore_volume
                        restore_volume(volume_value)
                    tts_handler = TTSHandler()
                    config = {
                        'voice_enabled': voice_enabled,
                        'voice_volume': voice_volume,
                        'voice_speed': voice_speed,
                        'system_voice_name': edge_tts_voice_name,
                    }
                    tts_handler.voice_play(config, [word_text], voice_engine, edge_tts_voice_name)
        except Exception as e:
            logger.error(f"语音播报出错: {e}")
    
    def play_right_word_voice(self):
        """播报右侧单词"""
        try:
            # 根据模式选择使用的词汇表
            words_list = self.right_words_list if self.is_dual_mode and hasattr(self, 'right_words_list') else self.words_list
            
            if 0 <= self.right_word_index < len(words_list):
                word = words_list[self.right_word_index]
                word_text = word["word"]
                
                # 获取语音配置
                with open_file(path_manager.get_voice_engine_path(), 'r', encoding='utf-8') as f:
                    voice_config = json.load(f)
                    voice_engine = voice_config['voice_engine']['voice_engine']
                    edge_tts_voice_name = voice_config['voice_engine']['edge_tts_voice_name']
                    voice_enabled = voice_config['voice_engine']['voice_enabled']
                    system_volume_enabled = voice_config['voice_engine']['system_volume_enabled']
                    voice_volume = voice_config['voice_engine'].get('voice_volume', 100) / 100.0
                    voice_speed = voice_config['voice_engine'].get('voice_speed', 100)
                    volume_value = voice_config['voice_engine'].get('system_volume_value', 50)

                if voice_enabled == True:  # 开启语音
                    if system_volume_enabled == True: # 开启系统音量
                        restore_volume(volume_value)
                    tts_handler = TTSHandler()
                    config = {
                        'voice_enabled': voice_enabled,
                        'voice_volume': voice_volume,
                        'voice_speed': voice_speed,
                        'system_voice_name': edge_tts_voice_name,
                    }
                    tts_handler.voice_play(config, [word_text], voice_engine, edge_tts_voice_name)
        except Exception as e:
            logger.error(f"语音播报出错: {e}")
    
    def show_word(self):
        """显示当前单词"""
        # 停止左侧计时器，确保两侧同时点击选项时不会互相干扰
        if hasattr(self, 'left_auto_next_timer') and self.left_auto_next_timer is not None:
            self.left_auto_next_timer.stop()
        
        # 根据模式选择使用的词汇表
        words_list = self.left_words_list if self.is_dual_mode and hasattr(self, 'left_words_list') else self.words_list
        
        if not words_list:
            self.word_label.setText("词库为空，请选择其他词库")
            return

        if 0 <= self.current_word_index < len(words_list):
            word = words_list[self.current_word_index]
            self.word_label.setText(word["word"])
            self.phonetic_label.setText(word["phonetic"])
            self.meaning_label.setText("")
            self.example_label.setText("")
            self.answer_shown = False
            
            # 显示语音播报按钮
            self.left_voice_button.show()
            
            # 记录当前单词的页数
            if self.current_word_index not in self.word_page_numbers:
                # 如果是第一次显示这个单词，分配一个新的页数
                self.current_page_number = len(self.word_page_numbers)
                self.word_page_numbers[self.current_word_index] = self.current_page_number
            
            # 重置所有左侧选项按钮样式为默认样式
            default_button_style = "QPushButton { background-color: #e3f2fd; border: 1px solid #90caf9; border-radius: 5px; padding: 8px; font-size: 14px; } QPushButton:hover { background-color: #bbdefb; } QPushButton:pressed { background-color: #90caf9; }"
            for btn in self.left_option_buttons:
                btn.setStyleSheet(default_button_style)
            
            # 如果当前单词已回答，恢复之前的答题选项样式
            if hasattr(self, 'answer_records') and self.current_word_index in self.answer_records and self.current_word_index in self.left_answered_words:
                record = self.answer_records[self.current_word_index]
                
                # 如果当前单词已回答，显示答案
                self.meaning_label.setText(word["meaning"])
                self.example_label.setText(word["example"])
                self.answer_shown = True
                
                # 如果有选项记录，恢复选项样式
                if 'selected_option' in record and 'correct_option' in record:
                    selected_option = record['selected_option']
                    correct_option = record['correct_option']
                    
                    # 高亮显示正确选项
                    if 0 <= correct_option < len(self.left_option_buttons):
                        self.left_option_buttons[correct_option].setStyleSheet("QPushButton { background-color: #c8e6c9; border: 2px solid #81c784; border-radius: 5px; padding: 8px; font-size: 14px; font-weight: bold; }")
                    
                    # 如果选择的选项不正确，标记错误选项
                    if selected_option != correct_option and 0 <= selected_option < len(self.left_option_buttons):
                        self.left_option_buttons[selected_option].setStyleSheet("QPushButton { background-color: #ffcdd2; border: 2px solid #e57373; border-radius: 5px; padding: 8px; font-size: 14px; }")
                    
                    # 如果选择的选项正确，高亮显示选择的选项
                    elif selected_option == correct_option and 0 <= selected_option < len(self.left_option_buttons):
                        self.left_option_buttons[selected_option].setStyleSheet("QPushButton { background-color: #c8e6c9; border: 2px solid #81c784; border-radius: 5px; padding: 8px; font-size: 14px; font-weight: bold; }")
                    
                    # 禁用所有选项按钮
                    for btn in self.left_option_buttons:
                        btn.setEnabled(False)
            
            # 更新按钮状态
            self.prev_button.setEnabled(self.current_word_index > 0)
            # 如果当前单词已回答，则启用下一页按钮；否则禁用
            self.next_button.setEnabled(
                self.current_word_index < len(words_list) - 1 and 
                self.current_word_index in self.left_answered_words
            )
            
            # 在不重复模式下，如果当前单词已回答，自动跳转到下一个未回答的单词
            # 但如果是从show_prev_word方法调用过来的，则不执行自动跳转
            if (hasattr(self, 'repeat_mode') and self.repeat_mode == "不重复模式" and 
                self.current_word_index in self.left_answered_words and 
                not hasattr(self, '_is_from_prev_word')):
                # 查找下一个未回答的单词
                next_index = self.current_word_index + 1
                while next_index < len(words_list) and next_index in self.left_answered_words:
                    next_index += 1
                
                if next_index < len(words_list):
                    self.current_word_index = next_index
                    self.show_word()  # 递归调用显示下一个单词
                    return  # 提前返回，避免执行后续代码
                else:
                    # 所有单词都已回答
                    if self.learning_mode == "无尽模式":
                        # 无尽模式：重置已回答单词集合
                        self.left_answered_words.clear()
                        self.current_word_index = 0
                        self.show_word()  # 递归调用显示第一个单词
                        
                        InfoBar.info(
                            title="不重复模式",
                            content="所有单词已学习一遍，重新开始！",
                            duration=2000,
                            parent=self
                        )
                        return  # 提前返回，避免执行后续代码
                    else:
                        # 总题数模式：显示提示
                        InfoBar.info(
                            title="不重复模式",
                            content="所有单词已学习一遍！",
                            duration=2000,
                            parent=self
                        )
            
            # 隐藏显示答案按钮，显示选项按钮
            self.show_answer_button.hide()
            
            # 生成选项
            if hasattr(self, 'distractor_count') and self.distractor_count > 0:
                # 隐藏显示答案按钮和容器
                self.show_answer_button.hide()
                self.left_show_answer_button_container.hide()
                
                # 显示选项按钮容器
                self.left_options_container.show()
                
                # 检查是否有答题记录，如果有则使用记录中的选项顺序
                if hasattr(self, 'answer_records') and self.current_word_index in self.answer_records and self.current_word_index in self.left_answered_words:
                    record = self.answer_records[self.current_word_index]
                    if 'options' in record:
                        # 使用保存的选项顺序
                        self.current_options = record['options'].copy()
                        
                        # 找到正确答案的索引
                        self.correct_option_index = 0  # 设置默认值
                        for i, option in enumerate(self.current_options):
                            if option['is_correct']:
                                self.correct_option_index = i
                                break
                    else:
                        # 如果没有保存选项顺序，则生成新的选项
                        self.generate_new_left_options(word)
                else:
                    # 如果没有答题记录或未回答，则生成新的选项
                    self.generate_new_left_options(word)
                        
                # 显示选项按钮
                for i in range(min(len(self.current_options), len(self.left_option_buttons))):
                    self.left_option_buttons[i].setText(self.current_options[i]['meaning'])
                    
                    # 清除工具提示，确保只有在答题后或点击"显示答案"按钮后才会显示
                    self.left_option_buttons[i].setToolTip("")
                    
                    self.left_option_buttons[i].setVisible(True)
                    self.left_option_buttons[i].setEnabled(True)
                    # 移除setStyleSheet调用，使用按钮默认样式

                # 隐藏多余的选项按钮
                for i in range(len(self.current_options), len(self.left_option_buttons)):
                    self.left_option_buttons[i].setVisible(False)
                    
                # 根据distractor_count值控制显示的选项按钮数量
                for i in range(len(self.left_option_buttons)):
                    if i < self.distractor_count + 1:  # +1 是因为包括正确答案
                        self.left_option_buttons[i].setVisible(True)
                    else:
                        self.left_option_buttons[i].setVisible(False)
            else:
                # 没有设置干扰词汇，隐藏选项按钮容器，显示答案按钮容器
                self.left_options_container.hide()
                self.left_show_answer_button_container.show()
                self.show_answer_button.show()
                self.show_answer_button.setEnabled(True)
                
                # 初始化选项列表，只包含正确答案
                self.current_options = [{'meaning': word['meaning'], 'is_correct': True}]
                self.correct_option_index = 0  # 正确答案索引为0
                
                # 隐藏所有选项按钮
                for i in range(len(self.left_option_buttons)):
                    self.left_option_buttons[i].setVisible(False)
            
    def generate_new_left_options(self, word):
        """生成左侧新的选项列表"""
        # 生成干扰词汇
        self.current_distractors = self.generate_distractor_words(word['meaning'], "left")
        
        # 创建选项列表（正确答案+干扰项）
        self.current_options = [{'meaning': word['meaning'], 'is_correct': True}]
        for d in self.current_distractors:
            self.current_options.append({'meaning': d['meaning'], 'is_correct': False})
            
        # 随机排序选项
        system_random.shuffle(self.current_options)
        
        # 验证选项列表中只有一个正确答案
        correct_count = sum(1 for option in self.current_options if option['is_correct'])
        if correct_count != 1:
            # 如果不只有一个正确答案，重新生成选项列表
            # 这种情况理论上不应该发生，但需要处理以防万一
            self.current_options = [{'meaning': word['meaning'], 'is_correct': True}]
            for d in self.current_distractors:
                self.current_options.append({'meaning': d['meaning'], 'is_correct': False})
            system_random.shuffle(self.current_options)
        
        # 找到正确答案的索引
        self.correct_option_index = 0  # 设置默认值
        for i, option in enumerate(self.current_options):
            if option['is_correct']:
                self.correct_option_index = i
                break
    
    def show_answer(self):
        """显示答案"""
        # 根据模式选择使用的词汇表
        words_list = self.left_words_list if self.is_dual_mode and hasattr(self, 'left_words_list') else self.words_list
        
        if 0 <= self.current_word_index < len(words_list) and not self.answer_shown:
            word = words_list[self.current_word_index]
            
            # 普通模式，直接显示答案
            self.meaning_label.setText(word["meaning"])
            self.example_label.setText(word["example"])
            
            # 为所有选项按钮添加工具提示，显示英文单词和读音
            for i, option in enumerate(self.current_options):
                option_word = None
                option_phonetic = None
                
                # 如果是正确答案，使用当前单词的信息
                if option['is_correct']:
                    option_word = word['word']
                    option_phonetic = word['phonetic']
                else:
                    # 如果是干扰项，使用保存的干扰词汇信息
                    if hasattr(self, 'current_distractors'):
                        for d in self.current_distractors:
                            if d['meaning'] == option['meaning']:
                                option_word = d['word']
                                option_phonetic = d['phonetic']
                                break
                
                # 设置工具提示，显示英文单词和读音
                if option_word and option_phonetic and i < len(self.left_option_buttons):
                    self.left_option_buttons[i].setToolTip(f"{option_word} {option_phonetic}")
            
            self.answer_shown = True
            # 将当前单词索引添加到已回答单词集合中
            # 注意：只有在实际跳转到下一个单词时才添加，避免误判答题状态
            # self.answered_words.add(self.current_word_index)  # 注释掉这行，避免误判答题状态
            
            # 启用下一页按钮，因为当前单词已回答
            self.next_button.setEnabled(self.current_word_index < len(words_list) - 1)
            
            # 更新已答题数（如果是总题数模式或无尽模式）
            if self.learning_mode == "总题数模式" or self.learning_mode == "无尽模式":
                self.questions_answered += 1
                self.update_learning_status()
                
                # 检查是否达到总题数（仅总题数模式）
                if self.learning_mode == "总题数模式" and self.questions_answered >= self.total_questions:
                    # 显示提示
                    InfoBar.info(
                        title="学习结束",
                        content=f"已完成{self.questions_answered}道题目，学习完成！",
                        duration=3000,
                        parent=self
                    )
                    
                    # 禁用答题按钮
                    self.next_button.setEnabled(False)
                    self.show_answer_button.setEnabled(False)
                    
                    # 如果是双人模式，也禁用右侧按钮
                    if self.is_dual_mode:
                        self.right_next_button.setEnabled(False)
                        self.right_show_answer_button.setEnabled(False)
            
            # 如果启用了自动下一个单词功能，启动左侧计时器
            if self.auto_next:
                self.start_left_auto_next_timer()
            
    def on_left_option_selected(self, option_index):
        """左侧选项被选中时的处理函数"""
        # 设置当前活动侧边为左侧
        self._active_side = 'left'
        
        # 根据模式选择使用的词汇表
        words_list = self.left_words_list if self.is_dual_mode and hasattr(self, 'left_words_list') else self.words_list
        
        if 0 <= self.current_word_index < len(words_list) and not self.answer_shown:
            word = words_list[self.current_word_index]
            
            # 禁用所有选项按钮
            for btn in self.left_option_buttons:
                btn.setEnabled(False)
            
            # 为所有选项按钮添加工具提示，显示英文单词和读音
            for i, option in enumerate(self.current_options):
                option_word = None
                option_phonetic = None
                
                # 如果是正确答案，使用当前单词的信息
                if option['is_correct']:
                    option_word = word['word']
                    option_phonetic = word['phonetic']
                else:
                    # 如果是干扰项，使用保存的干扰词汇信息
                    if hasattr(self, 'current_distractors'):
                        for d in self.current_distractors:
                            if d['meaning'] == option['meaning']:
                                option_word = d['word']
                                option_phonetic = d['phonetic']
                                break
                
                # 设置工具提示，显示英文单词和读音
                if option_word and option_phonetic and i < len(self.left_option_buttons):
                    self.left_option_buttons[i].setToolTip(f"{option_word} {option_phonetic}")
                
            # 检查选择的答案是否正确
            if option_index == self.correct_option_index:
                # 选择正确
                self.meaning_label.setText("✓ 回答正确！")
                self.meaning_label.setStyleSheet("color: green;")
                
                # 显示完整答案
                self.example_label.setText(f"{word['word']} - {word['meaning']}")
                if word['example']:
                    self.example_label.setText(f"{self.example_label.text()}\n例句: {word['example']}")
                
                # 高亮显示正确选项（添加边界检查）
                if 0 <= option_index < len(self.left_option_buttons):
                    self.left_option_buttons[option_index].setStyleSheet("QPushButton { background-color: #c8e6c9; border: 2px solid #81c784; border-radius: 5px; padding: 8px; font-size: 14px; font-weight: bold; }")
                
                # 更新左侧答题统计
                self.left_correct_count += 1
                self.left_stats_label.setText(f"正确答对{self.left_correct_count}个，答错{self.left_wrong_count}个，跳过{self.left_skip_count}个")
            else:
                # 选择错误
                self.meaning_label.setText("✗ 回答错误！")
                self.meaning_label.setStyleSheet("color: red;")
                
                # 显示正确答案
                correct_option = self.current_options[self.correct_option_index]
                self.example_label.setText(f"正确答案: {correct_option['meaning']}")
                
                # 高亮显示正确选项（添加边界检查）
                if 0 <= self.correct_option_index < len(self.left_option_buttons):
                    self.left_option_buttons[self.correct_option_index].setStyleSheet("QPushButton { background-color: #c8e6c9; border: 2px solid #81c784; border-radius: 5px; padding: 8px; font-size: 14px; font-weight: bold; }")
                
                # 标记错误选项
                if 0 <= option_index < len(self.left_option_buttons):
                    self.left_option_buttons[option_index].setStyleSheet("QPushButton { background-color: #ffcdd2; border: 2px solid #e57373; border-radius: 5px; padding: 8px; font-size: 14px; }")
                
                # 更新左侧答题统计
                self.left_wrong_count += 1
                self.left_stats_label.setText(f"正确答对{self.left_correct_count}个，答错{self.left_wrong_count}个，跳过{self.left_skip_count}个")
            
            # 保存答题的选项记录信息
            if not hasattr(self, 'answer_records'):
                self.answer_records = {}
            
            # 检查之前是否有跳过记录
            was_skipped = False
            if self.current_word_index in self.answer_records:
                was_skipped = self.answer_records[self.current_word_index].get('is_skipped', False)
            
            # 如果之前是跳过的，需要减少跳过计数
            if was_skipped and hasattr(self, 'left_skip_count') and self.left_skip_count > 0:
                self.left_skip_count -= 1
                # 更新统计标签
                self.left_stats_label.setText(f"正确答对{self.left_correct_count}个，答错{self.left_wrong_count}个，跳过{self.left_skip_count}个")
            
            # 记录当前单词的答题信息
            self.answer_records[self.current_word_index] = {
                'word': word['word'],
                'meaning': word['meaning'],
                'selected_option': option_index,
                'correct_option': self.correct_option_index,
                'is_correct': option_index == self.correct_option_index,
                'options': self.current_options.copy(),
                'options_order': self.current_options.copy(),  # 保存选项顺序
                'is_skipped': False  # 明确设置为非跳过状态
            }
                
            self.answer_shown = True
            # 将当前单词索引添加到已回答单词集合中
            # 注意：只有在实际跳转到下一个单词时才添加，避免误判答题状态
            # self.left_answered_words.add(self.current_word_index)  # 注释掉这行，避免误判答题状态
            
            # 启用下一页按钮，因为当前单词已回答
            self.next_button.setEnabled(self.current_word_index < len(self.words_list) - 1)
            
            # 更新已答题数（如果是总题数模式或无尽模式）
            if self.learning_mode == "总题数模式" or self.learning_mode == "无尽模式":
                self.questions_answered += 1
                self.update_learning_status()
                
                # 检查是否达到总题数（仅总题数模式）
                if self.learning_mode == "总题数模式" and self.questions_answered >= self.total_questions:
                    # 显示提示
                    InfoBar.info(
                        title="学习结束",
                        content=f"已完成{self.questions_answered}道题目，学习完成！",
                        duration=3000,
                        parent=self
                    )
                    
                    # 禁用答题按钮
                    self.next_button.setEnabled(False)
                    self.show_answer_button.setEnabled(False)
                    
                    # 如果是双人模式，也禁用右侧按钮
                    if self.is_dual_mode:
                        self.right_next_button.setEnabled(False)
                        self.right_show_answer_button.setEnabled(False)
            
            # 如果启用了自动下一个单词功能，启动左侧计时器
            if self.auto_next:
                self.start_left_auto_next_timer()
    
    def on_right_option_selected(self, option_index):
        """右侧选项被选中时的处理函数"""
        # 设置当前活动侧边为右侧
        self._active_side = 'right'
        
        # 根据模式选择使用的词汇表
        words_list = self.right_words_list if self.is_dual_mode and hasattr(self, 'right_words_list') else self.words_list
        
        if 0 <= self.right_word_index < len(words_list) and not self.right_answer_shown:
            word = words_list[self.right_word_index]
            
            # 禁用所有选项按钮
            for btn in self.right_option_buttons:
                btn.setEnabled(False)
            
            # 为所有选项按钮添加工具提示，显示英文单词和读音
            for i, option in enumerate(self.right_current_options):
                option_word = None
                option_phonetic = None
                
                # 如果是正确答案，使用当前单词的信息
                if option['is_correct']:
                    option_word = word['word']
                    option_phonetic = word['phonetic']
                else:
                    # 如果是干扰项，使用保存的干扰词汇信息
                    if hasattr(self, 'right_current_distractors'):
                        for d in self.right_current_distractors:
                            if d['meaning'] == option['meaning']:
                                option_word = d['word']
                                option_phonetic = d['phonetic']
                                break
                
                # 设置工具提示，显示英文单词和读音
                if option_word and option_phonetic and i < len(self.right_option_buttons):
                    self.right_option_buttons[i].setToolTip(f"{option_word} {option_phonetic}")

            # 检查选择的答案是否正确
            if option_index == self.right_correct_option_index:
                # 选择正确
                self.right_meaning_label.setText("✓ 回答正确！")
                self.right_meaning_label.setStyleSheet("color: green;")
                
                # 显示完整答案
                self.right_example_label.setText(f"{word['word']} - {word['meaning']}")
                if word['example']:
                    self.right_example_label.setText(f"{self.right_example_label.text()}\n例句: {word['example']}")
                
                # 高亮显示正确选项（添加边界检查）
                if 0 <= option_index < len(self.right_option_buttons):
                    self.right_option_buttons[option_index].setStyleSheet("QPushButton { background-color: #c8e6c9; border: 2px solid #81c784; border-radius: 5px; padding: 8px; font-size: 14px; font-weight: bold; }")
                
                # 更新右侧答题统计
                self.right_correct_count += 1
                self.right_stats_label.setText(f"正确答对{self.right_correct_count}个，答错{self.right_wrong_count}个，跳过{self.right_skip_count}个")
            else:
                # 选择错误
                self.right_meaning_label.setText("✗ 回答错误！")
                self.right_meaning_label.setStyleSheet("color: red;")
                
                # 显示正确答案
                correct_option = self.right_current_options[self.right_correct_option_index]
                self.right_example_label.setText(f"正确答案: {correct_option['meaning']}")
                
                # 高亮显示正确选项（添加边界检查）
                if 0 <= self.right_correct_option_index < len(self.right_option_buttons):
                    self.right_option_buttons[self.right_correct_option_index].setStyleSheet("QPushButton { background-color: #c8e6c9; border: 2px solid #81c784; border-radius: 5px; padding: 8px; font-size: 14px; font-weight: bold; }")
                
                # 标记错误选项
                if 0 <= option_index < len(self.right_option_buttons):
                    self.right_option_buttons[option_index].setStyleSheet("QPushButton { background-color: #ffcdd2; border: 2px solid #e57373; border-radius: 5px; padding: 8px; font-size: 14px; }")
                
                # 更新右侧答题统计
                self.right_wrong_count += 1
                self.right_stats_label.setText(f"正确答对{self.right_correct_count}个，答错{self.right_wrong_count}个，跳过{self.right_skip_count}个")
            
            # 保存答题的选项记录信息
            if not hasattr(self, 'answer_records'):
                self.answer_records = {}
            
            # 检查之前是否有跳过记录
            was_skipped = False
            right_key = f"right_{self.right_word_index}"
            if right_key in self.answer_records:
                was_skipped = self.answer_records[right_key].get('is_skipped', False)
            
            # 如果之前是跳过的，需要减少跳过计数
            if was_skipped and hasattr(self, 'right_skip_count') and self.right_skip_count > 0:
                self.right_skip_count -= 1
                # 更新统计标签
                self.right_stats_label.setText(f"正确答对{self.right_correct_count}个，答错{self.right_wrong_count}个，跳过{self.right_skip_count}个")
            
            # 记录当前单词的答题信息
            self.answer_records[self.right_word_index] = {
                'word': word['word'],
                'meaning': word['meaning'],
                'selected_option': option_index,
                'correct_option': self.right_correct_option_index,
                'is_correct': option_index == self.right_correct_option_index,
                'options': self.right_current_options.copy(),
                'options_order': self.right_current_options.copy(),  # 保存选项顺序
                'is_skipped': False  # 明确设置为非跳过状态
            }
            
            # 同时更新right_key记录，确保跳过状态正确
            self.answer_records[right_key] = {
                'word': word['word'],
                'meaning': word['meaning'],
                'selected_option': option_index,
                'correct_option': self.right_correct_option_index,
                'is_correct': option_index == self.right_correct_option_index,
                'options': self.right_current_options.copy(),
                'options_order': self.right_current_options.copy(),  # 保存选项顺序
                'is_skipped': False,  # 明确设置为非跳过状态
                'is_right': True  # 标记为右侧单词
            }
                
            self.right_answer_shown = True
            # 将当前单词索引添加到已回答单词集合中
            # 注意：只有在实际跳转到下一个单词时才添加，避免误判答题状态
            # self.right_answered_words.add(self.right_word_index)  # 注释掉这行，避免误判答题状态
            
            # 启用右侧下一页按钮，因为当前单词已回答
            self.right_next_button.setEnabled(self.right_word_index < len(words_list) - 1)
            
            # 更新已答题数（如果是总题数模式或无尽模式）
            if self.learning_mode == "总题数模式" or self.learning_mode == "无尽模式":
                self.questions_answered += 1
                self.update_learning_status()
                
                # 检查是否达到总题数（仅总题数模式）
                if self.learning_mode == "总题数模式" and self.questions_answered >= self.total_questions:
                    # 显示提示
                    InfoBar.info(
                        title="学习结束",
                        content=f"已完成{self.total_questions}道题目，学习完成！",
                        duration=2000,
                        parent=self
                    )
                    
                    # 禁用答题按钮
                    self.next_button.setEnabled(False)
                    self.show_answer_button.setEnabled(False)
                    
                    # 如果是双人模式，也禁用右侧按钮
                    if self.is_dual_mode:
                        self.right_next_button.setEnabled(False)
                        self.right_show_answer_button.setEnabled(False)
            
            # 如果启用了自动下一个单词功能，启动右侧计时器
            if self.auto_next:
                self.start_right_auto_next_timer()
    
    # 为了向后兼容，保留原始函数名
    def on_option_selected(self, option_index):
        """选项被选中时的处理函数（向后兼容）"""
        self.on_left_option_selected(option_index)
            
    def show_prev_word(self):
        """显示上一个单词"""
        # 停止自动下一个单词的计时器（如果有）
        self.stop_auto_next_timer()
        
        # 根据模式选择使用的词汇表
        words_list = self.left_words_list if self.is_dual_mode and hasattr(self, 'left_words_list') else self.words_list
        
        # 显示当前页的响应状态
        if 0 <= self.current_word_index < len(words_list):
            word = words_list[self.current_word_index]
            
            # 检查当前单词是否已回答
            if self.current_word_index in self.left_answered_words:
                # 显示当前单词的答案
                self.meaning_label.setText(word["meaning"])
                self.example_label.setText(word["example"])
                self.answer_shown = True
                
                # # 显示提示信息
                # InfoBar.info(
                #     title="当前页状态",
                #     content="已显示当前单词的答案",
                #     duration=1500,
                #     parent=self
                # )
            else:
                # # 显示提示信息
                # InfoBar.info(
                #     title="当前页状态",
                #     content="当前单词尚未回答",
                #     duration=1500,
                #     parent=self
                # )
                pass
        
        # 直接翻到上一个单词，不考虑重复模式
        if self.current_word_index > 0:
            self.current_word_index -= 1
            # 设置标记，表明是从上一个单词按钮调用的
            self._is_from_prev_word = True
            self.show_word()
            # 移除标记
            if hasattr(self, '_is_from_prev_word'):
                delattr(self, '_is_from_prev_word')
            
            # 检查上一个单词是否已回答，如果已回答则显示答案并禁用选项按钮
            if self.current_word_index in self.left_answered_words:
                # 显示答案
                word = words_list[self.current_word_index]
                self.meaning_label.setText(word["meaning"])
                self.example_label.setText(word["example"])
                self.answer_shown = True
                
                # 禁用所有左侧选项按钮
                for btn in self.left_option_buttons:
                    btn.setEnabled(False)
            
            # 检查上一个单词是否是跳过的，如果是则减少跳过计数
            if hasattr(self, 'answer_records') and self.current_word_index in self.answer_records:
                record = self.answer_records[self.current_word_index]
                if record.get('is_skipped', False):
                    # 减少跳过计数
                    if hasattr(self, 'left_skip_count') and self.left_skip_count > 0:
                        self.left_skip_count -= 1
                        # 更新统计标签
                        self.left_stats_label.setText(f"正确答对{self.left_correct_count}个，答错{self.left_wrong_count}个，跳过{self.left_skip_count}个")
                    # 移除跳过标记
                    record['is_skipped'] = False
            
    def show_next_word(self):
        """显示下一个单词"""
        # 停止左侧自动下一个单词的计时器（如果有）
        if self.left_auto_next_timer is not None:
            self.left_auto_next_timer.stop()
            self.left_auto_next_timer = None
        
        # 显示当前页的响应状态
        if 0 <= self.current_word_index < len(self.words_list):
            word = self.words_list[self.current_word_index]
            
            # 检查当前单词是否已回答
            if self.current_word_index in self.left_answered_words:
                # 显示当前单词的答案
                self.meaning_label.setText(word["meaning"])
                self.example_label.setText(word["example"])
                self.answer_shown = True
                
                # # 显示提示信息
                # InfoBar.info(
                #     title="当前页状态",
                #     content="已显示当前单词的答案",
                #     duration=1500,
                #     parent=self
                # )
            else:
                # # 显示提示信息
                # InfoBar.info(
                #     title="当前页状态",
                #     content="当前单词尚未回答",
                #     duration=1500,
                #     parent=self
                # )
                pass
        
        # 根据模式选择不同的处理方式
        if hasattr(self, 'repeat_mode') and self.repeat_mode == "不重复模式":
            # 不重复模式：检查下一个单词是否已回答
            if self.answer_shown:
                self.left_answered_words.add(self.current_word_index)
            
            # 获取下一个单词的索引
            next_index = self.current_word_index + 1
            
            # 检查下一个单词是否已回答过
            if next_index < len(self.words_list) and next_index in self.left_answered_words:
                # 如果下一个单词已回答过，直接显示它
                self.current_word_index = next_index
                self.show_word()
            else:
                # 如果下一个单词未回答过，查找下一个未回答的单词
                while next_index < len(self.words_list) and next_index in self.left_answered_words:
                    next_index += 1
                
                if next_index < len(self.words_list):
                    self.current_word_index = next_index
                    self.show_word()
                else:
                    # 所有单词都已回答
                    if self.learning_mode == "无尽模式":
                        # 无尽模式：重置已回答单词集合
                        self.left_answered_words.clear()
                        self.current_word_index = 0
                        self.show_word()
                        
                        InfoBar.info(
                            title="不重复模式",
                            content="所有单词已学习一遍，重新开始！",
                            duration=2000,
                            parent=self
                        )
                    else:
                        # 总题数模式：显示提示
                        InfoBar.info(
                            title="不重复模式",
                            content="所有单词已学习一遍！",
                            duration=2000,
                            parent=self
                        )
        else:
            # 重复模式下，直接翻到下一个单词
            if self.current_word_index < len(self.words_list) - 1:
                # 如果当前单词已回答（通过选项选择或显示答案），则将其添加到已回答集合
                if self.answer_shown:
                    self.left_answered_words.add(self.current_word_index)
                self.current_word_index += 1
                self.show_word()
            

                
    def update_option_buttons_count(self):
        """更新选项按钮数量"""
        # 如果distractor_count为0，隐藏所有选项按钮
        if self.distractor_count == 0:
            for btn in self.left_option_buttons:
                btn.setVisible(False)
            for btn in self.right_option_buttons:
                btn.setVisible(False)
            return
            
        # 计算需要的选项按钮数量（干扰项+正确答案）
        needed_button_count = self.distractor_count + 1
        
        # 更新左侧选项按钮
        self._update_side_option_buttons(self.left_option_buttons, self.left_options_container, self.left_options_layout, 
                                         needed_button_count, "left")
        
        # 更新右侧选项按钮
        self._update_side_option_buttons(self.right_option_buttons, self.right_options_container, self.right_options_layout, 
                                         needed_button_count, "right")
                                         
    def _update_side_option_buttons(self, option_buttons, options_container, options_layout, needed_button_count, side):
        """更新单侧选项按钮数量"""
        # 获取当前按钮数量
        current_button_count = len(option_buttons)
        
        # 如果需要更多按钮，添加新按钮
        if current_button_count < needed_button_count:
            for i in range(current_button_count, needed_button_count):
                option_btn = PushButton(f"选项 {i+1}")
                option_btn.setFont(QFont(load_custom_font(), 12))
                if side == "left":
                    option_btn.clicked.connect(lambda checked, idx=i: self.on_left_option_selected(idx))
                else:
                    option_btn.clicked.connect(lambda checked, idx=i: self.on_right_option_selected(idx))
                options_layout.addWidget(option_btn)
                option_buttons.append(option_btn)
        
        # 如果需要更少按钮，隐藏多余按钮
        elif current_button_count > needed_button_count:
            for i in range(needed_button_count, current_button_count):
                option_buttons[i].setVisible(False)
        
        # 显示需要的按钮
        for i in range(needed_button_count):
            option_buttons[i].setVisible(True)
            
    def generate_distractor_words(self, correct_meaning, side="left"):
        """生成干扰词汇列表"""
        if not hasattr(self, 'distractor_count') or self.distractor_count == 0:
            return []
            
        # 根据模式选择使用的词汇表
        if self.is_dual_mode and hasattr(self, 'left_words_list') and hasattr(self, 'right_words_list'):
            words_list = self.left_words_list if side == "left" else self.right_words_list
        else:
            words_list = self.words_list
            
        # 从词库中随机选择干扰词汇，排除正确答案
        available_words = [word for word in words_list if word["meaning"] != correct_meaning]
        
        # 如果可用词汇不足，使用默认干扰词汇
        if len(available_words) < self.distractor_count:
            default_distractors = [
                {"word": "example", "phonetic": "/ɪɡˈzæmpl/", "meaning": "n. 例子", "example": "This is an example."},
                {"word": "important", "phonetic": "/ɪmˈpɔːrtnt/", "meaning": "adj. 重要的", "example": "This is very important."},
                {"word": "language", "phonetic": "/ˈlæŋɡwɪdʒ/", "meaning": "n. 语言", "example": "She speaks three languages."},
                {"word": "different", "phonetic": "/ˈdɪfərənt/", "meaning": "adj. 不同的", "example": "They have different ideas."},
                {"word": "understand", "phonetic": "/ˌʌndərˈstænd/", "meaning": "v. 理解", "example": "I understand your point."}
            ]
            # 确保默认干扰词汇也不包含正确答案
            filtered_default_distractors = [d for d in default_distractors if d["meaning"] != correct_meaning]
            # 如果过滤后没有足够的干扰词汇，使用全部过滤后的干扰词汇
            if len(filtered_default_distractors) == 0:
                # 如果所有默认干扰词汇都与正确答案相同，则使用原始默认干扰词汇
                # 这种情况极少发生，但需要处理以防万一
                distractors = system_random.sample(default_distractors, min(self.distractor_count, len(default_distractors)))
            else:
                distractors = system_random.sample(filtered_default_distractors, min(self.distractor_count, len(filtered_default_distractors)))
        else:
            # 为左右两侧使用不同的随机种子，确保两侧的干扰词汇不同
            # SystemRandom不需要设置种子，它使用操作系统提供的安全随机源
            distractors = system_random.sample(available_words, self.distractor_count)
            
        return distractors
        
    def show_right_word(self):
        """显示右侧当前单词"""
        # 停止右侧计时器，确保两侧同时点击选项时不会互相干扰
        if hasattr(self, 'right_auto_next_timer') and self.right_auto_next_timer is not None and self.right_auto_next_timer.isActive():
            self.right_auto_next_timer.stop()
        
        # 根据模式选择使用的词汇表
        words_list = self.right_words_list if self.is_dual_mode and hasattr(self, 'right_words_list') else self.words_list
        
        if not words_list:
            self.word_label.setText("词库为空，请选择其他词库")
            return

        if 0 <= self.right_word_index < len(words_list):
            word = words_list[self.right_word_index]
            self.right_word_label.setText(word["word"])
            self.right_phonetic_label.setText(word["phonetic"])
            self.right_meaning_label.setText("")
            self.right_example_label.setText("")
            self.right_answer_shown = False
            
            # 显示语音播报按钮
            self.right_voice_button.show()
            
            # 记录右侧单词的页数
            if self.right_word_index not in self.word_page_numbers:
                # 如果是第一次显示这个单词，分配一个新的页数
                self.right_page_number = len(self.word_page_numbers)
                self.word_page_numbers[self.right_word_index] = self.right_page_number
            
            # 重置所有右侧选项按钮样式为默认样式
            default_button_style = "QPushButton { background-color: #e3f2fd; border: 1px solid #90caf9; border-radius: 5px; padding: 8px; font-size: 14px; } QPushButton:hover { background-color: #bbdefb; } QPushButton:pressed { background-color: #90caf9; }"
            for btn in self.right_option_buttons:
                btn.setStyleSheet(default_button_style)
            
            # 如果当前单词已回答，恢复之前的答题选项样式
            if hasattr(self, 'answer_records') and self.right_word_index in self.answer_records and self.right_word_index in self.right_answered_words:
                record = self.answer_records[self.right_word_index]
                
                # 如果当前单词已回答，显示答案
                self.right_meaning_label.setText(word["meaning"])
                self.right_example_label.setText(word["example"])
                self.right_answer_shown = True
                
                # 如果有选项记录，恢复选项样式
                if 'selected_option' in record and 'correct_option' in record:
                    selected_option = record['selected_option']
                    correct_option = record['correct_option']
                    
                    # 高亮显示正确选项
                    if 0 <= correct_option < len(self.right_option_buttons):
                        self.right_option_buttons[correct_option].setStyleSheet("QPushButton { background-color: #c8e6c9; border: 2px solid #81c784; border-radius: 5px; padding: 8px; font-size: 14px; font-weight: bold; }")
                    
                    # 如果选择的选项不正确，标记错误选项
                    if selected_option != correct_option and 0 <= selected_option < len(self.right_option_buttons):
                        self.right_option_buttons[selected_option].setStyleSheet("QPushButton { background-color: #ffcdd2; border: 2px solid #e57373; border-radius: 5px; padding: 8px; font-size: 14px; }")
                    
                    # 如果选择的选项正确，高亮显示选择的选项
                    elif selected_option == correct_option and 0 <= selected_option < len(self.right_option_buttons):
                        self.right_option_buttons[selected_option].setStyleSheet("QPushButton { background-color: #c8e6c9; border: 2px solid #81c784; border-radius: 5px; padding: 8px; font-size: 14px; font-weight: bold; }")
                    
                    # 禁用所有选项按钮
                    for btn in self.right_option_buttons:
                        btn.setEnabled(False)
            
            # 更新按钮状态
            self.right_prev_button.setEnabled(self.right_word_index > 0)
            # 如果当前单词已回答，则启用右侧下一页按钮；否则禁用
            self.right_next_button.setEnabled(
                self.right_word_index < len(words_list) - 1 and 
                self.right_word_index in self.right_answered_words
            )
            
            # 在不重复模式下，如果当前单词已回答，自动跳转到下一个未回答的单词
            # 但如果是从show_right_prev_word方法调用过来的，则不执行自动跳转
            if (hasattr(self, 'repeat_mode') and self.repeat_mode == "不重复模式" and 
                self.right_word_index in self.right_answered_words and 
                not hasattr(self, '_is_from_right_prev_word')):
                # 查找下一个未回答的单词
                next_index = self.right_word_index + 1
                while next_index < len(words_list) and next_index in self.right_answered_words:
                    next_index += 1
                
                if next_index < len(words_list):
                    self.right_word_index = next_index
                    self.show_right_word()  # 递归调用显示下一个单词
                    return  # 提前返回，避免执行后续代码
                else:
                    # 所有单词都已回答
                    if self.learning_mode == "无尽模式":
                        # 无尽模式：重置已回答单词集合
                        self.right_answered_words.clear()
                        self.right_word_index = 0
                        self.show_right_word()  # 递归调用显示第一个单词
                        
                        InfoBar.info(
                            title="不重复模式",
                            content="所有单词已学习一遍，重新开始！",
                            duration=2000,
                            parent=self
                        )
                        return  # 提前返回，避免执行后续代码
                    else:
                        # 总题数模式：显示提示
                        InfoBar.info(
                            title="不重复模式",
                            content="所有单词已学习一遍！",
                            duration=2000,
                            parent=self
                        )
            
            # 如果设置了干扰词汇，生成选项
            if hasattr(self, 'distractor_count') and self.distractor_count > 0:
                # 隐藏显示答案按钮和容器
                self.right_show_answer_button.hide()
                self.right_show_answer_button_container.hide()
                
                # 显示选项按钮容器
                self.right_options_container.show()
                
                # 检查是否有保存的答题记录
                if hasattr(self, 'answer_records') and self.right_word_index in self.answer_records:
                    record = self.answer_records[self.right_word_index]
                    if 'options_order' in record:
                        # 使用保存的选项顺序
                        self.right_current_options = record['options_order']
                        # 找到正确答案的索引
                        self.right_correct_option_index = 0  # 设置默认值
                        for i, option in enumerate(self.right_current_options):
                            if option['is_correct']:
                                self.right_correct_option_index = i
                                break
                    else:
                        # 生成新的选项
                        self.generate_new_right_options(word)
                else:
                    # 生成新的选项
                    self.generate_new_right_options(word)
                        
                # 显示选项按钮
                for i in range(min(len(self.right_current_options), len(self.right_option_buttons))):
                    self.right_option_buttons[i].setText(self.right_current_options[i]['meaning'])
                    
                    # 清除工具提示，确保只有在答题后或点击"显示答案"按钮后才会显示
                    self.right_option_buttons[i].setToolTip("")
                    
                    self.right_option_buttons[i].setVisible(True)
                    self.right_option_buttons[i].setEnabled(True)
                    # 移除setStyleSheet调用，使用按钮默认样式

                # 隐藏多余的选项按钮
                for i in range(len(self.right_current_options), len(self.right_option_buttons)):
                    self.right_option_buttons[i].setVisible(False)
                    
                # 根据distractor_count值控制显示的选项按钮数量
                for i in range(len(self.right_option_buttons)):
                    if i < self.distractor_count + 1:  # +1 是因为包括正确答案
                        self.right_option_buttons[i].setVisible(True)
                    else:
                        self.right_option_buttons[i].setVisible(False)
            else:
                # 没有设置干扰词汇，隐藏选项按钮容器，显示答案按钮容器
                self.right_options_container.hide()
                self.right_show_answer_button_container.show()
                self.right_show_answer_button.show()
                self.right_show_answer_button.setEnabled(True)
                
                # 初始化选项列表，只包含正确答案
                self.right_current_options = [{'meaning': word['meaning'], 'is_correct': True}]
                self.right_correct_option_index = 0  # 正确答案索引为0
                
                # 隐藏所有选项按钮
                for i in range(len(self.right_option_buttons)):
                    self.right_option_buttons[i].setVisible(False)
            
    def generate_new_right_options(self, word):
        """生成右侧新的选项列表"""
        # 生成干扰词汇
        self.right_current_distractors = self.generate_distractor_words(word['meaning'], "right")
        
        # 创建选项列表（正确答案+干扰项）
        self.right_current_options = [{'meaning': word['meaning'], 'is_correct': True}]
        for d in self.right_current_distractors:
            self.right_current_options.append({'meaning': d['meaning'], 'is_correct': False})
            
        # 随机排序选项
        system_random.shuffle(self.right_current_options)
        
        # 验证选项列表中只有一个正确答案
        correct_count = sum(1 for option in self.right_current_options if option['is_correct'])
        if correct_count != 1:
            # 如果不只有一个正确答案，重新生成选项列表
            # 这种情况理论上不应该发生，但需要处理以防万一
            self.right_current_options = [{'meaning': word['meaning'], 'is_correct': True}]
            for d in self.right_current_distractors:
                self.right_current_options.append({'meaning': d['meaning'], 'is_correct': False})
            system_random.shuffle(self.right_current_options)
        
        # 找到正确答案的索引
        self.right_correct_option_index = 0  # 设置默认值
        for i, option in enumerate(self.right_current_options):
            if option['is_correct']:
                self.right_correct_option_index = i
                break
    
    def show_right_answer(self):
        """显示右侧答案"""
        # 根据模式选择使用的词汇表
        words_list = self.right_words_list if self.is_dual_mode and hasattr(self, 'right_words_list') else self.words_list
        
        if 0 <= self.right_word_index < len(words_list) and not self.right_answer_shown:
            word = words_list[self.right_word_index]
            
            # 普通模式，直接显示答案
            self.right_meaning_label.setText(word["meaning"])
            self.right_example_label.setText(word["example"])
            
            # 为所有选项按钮添加工具提示，显示英文单词和读音
            for i, option in enumerate(self.right_current_options):
                option_word = None
                option_phonetic = None
                
                # 如果是正确答案，使用当前单词的信息
                if option['is_correct']:
                    option_word = word['word']
                    option_phonetic = word['phonetic']
                else:
                    # 如果是干扰项，使用保存的干扰词汇信息
                    if hasattr(self, 'right_current_distractors'):
                        for d in self.right_current_distractors:
                            if d['meaning'] == option['meaning']:
                                option_word = d['word']
                                option_phonetic = d['phonetic']
                                break
                
                # 设置工具提示，显示英文单词和读音
                if option_word and option_phonetic and i < len(self.right_option_buttons):
                    self.right_option_buttons[i].setToolTip(f"{option_word} {option_phonetic}")
            
            self.right_answer_shown = True
            # 将当前单词索引添加到已回答单词集合中
            # 注意：只有在实际跳转到下一个单词时才添加，避免误判答题状态
            # self.right_answered_words.add(self.right_word_index)  # 注释掉这行，避免误判答题状态
            
            # 启用右侧下一页按钮，因为当前单词已回答
            self.right_next_button.setEnabled(self.right_word_index < len(self.words_list) - 1)
            
            # 更新已答题数（如果是总题数模式）
            if self.learning_mode == "总题数模式":
                self.questions_answered += 1
                self.update_learning_status()
                
                # 检查是否达到总题数
                if self.questions_answered >= self.total_questions:
                    # 显示提示
                    InfoBar.info(
                        title="学习结束",
                        content="已完成所有题目，学习完成！",
                        duration=3000,
                        parent=self
                    )
                    
                    # 禁用答题按钮
                    self.next_button.setEnabled(False)
                    self.show_answer_button.setEnabled(False)
                    
                    # 如果是双人模式，也禁用右侧按钮
                    if self.is_dual_mode:
                        self.right_next_button.setEnabled(False)
                        self.right_show_answer_button.setEnabled(False)
            
    def show_right_prev_word(self):
        """显示右侧上一个单词"""
        # 显示当前页的响应状态
        if 0 <= self.right_word_index < len(self.words_list):
            word = self.words_list[self.right_word_index]
            
            # 检查当前单词是否已回答
            if self.right_word_index in self.right_answered_words:
                # 显示当前单词的答案
                self.right_meaning_label.setText(word["meaning"])
                self.right_example_label.setText(word["example"])
                self.right_answer_shown = True
                
                # # 显示提示信息
                # InfoBar.info(
                #     title="当前页状态",
                #     content="已显示当前单词的答案",
                #     duration=1500,
                #     parent=self
                # )
            else:
                # # 显示提示信息
                # InfoBar.info(
                #     title="当前页状态",
                #     content="当前单词尚未回答",
                #     duration=1500,
                #     parent=self
                # )
                pass
        
        # 直接翻到上一个单词，不考虑重复模式
        if self.right_word_index > 0:
            self.right_word_index -= 1
            # 添加标记，防止show_right_word中的自动跳转
            self._is_from_right_prev_word = True
            self.show_right_word()
            # 移除标记
            if hasattr(self, '_is_from_right_prev_word'):
                delattr(self, '_is_from_right_prev_word')
            
            # 检查上一个单词是否已回答，如果已回答则显示答案并禁用选项按钮
            if self.right_word_index in self.right_answered_words:
                # 显示答案
                word = self.words_list[self.right_word_index]
                self.right_meaning_label.setText(word["meaning"])
                self.right_example_label.setText(word["example"])
                self.right_answer_shown = True
                
                # 禁用所有右侧选项按钮
                for btn in self.right_option_buttons:
                    btn.setEnabled(False)
            
            # 检查上一个单词是否是跳过的，如果是则减少跳过计数
            right_key = f"right_{self.right_word_index}"
            if hasattr(self, 'answer_records') and right_key in self.answer_records:
                record = self.answer_records[right_key]
                if record.get('is_skipped', False):
                    # 减少跳过计数
                    if hasattr(self, 'right_skip_count') and self.right_skip_count > 0:
                        self.right_skip_count -= 1
                        # 更新统计标签
                        self.right_stats_label.setText(f"正确答对{self.right_correct_count}个，答错{self.right_wrong_count}个，跳过{self.right_skip_count}个")
                    # 移除跳过标记
                    record['is_skipped'] = False
            
    def show_right_next_word(self):
        """显示右侧下一个单词"""
        # 停止右侧自动下一个单词的计时器（如果有）
        if self.right_auto_next_timer is not None:
            self.right_auto_next_timer.stop()
            self.right_auto_next_timer = None
        
        # 显示当前页的响应状态
        if 0 <= self.right_word_index < len(self.words_list):
            word = self.words_list[self.right_word_index]
            
            # 检查当前单词是否已回答
            if self.right_word_index in self.right_answered_words:
                # 显示当前单词的答案
                self.right_meaning_label.setText(word["meaning"])
                self.right_example_label.setText(word["example"])
                self.right_answer_shown = True
                
                # # 显示提示信息
                # InfoBar.info(
                #     title="当前页状态",
                #     content="已显示当前单词的答案",
                #     duration=1500,
                #     parent=self
                # )
            else:
                # # 显示提示信息
                # InfoBar.info(
                #     title="当前页状态",
                #     content="当前单词尚未回答",
                #     duration=1500,
                #     parent=self
                # )
                pass
        
        # 根据模式选择不同的处理方式
        if hasattr(self, 'repeat_mode') and self.repeat_mode == "不重复模式":
            # 不重复模式：检查下一个单词是否已回答
            if self.right_answer_shown:
                self.right_answered_words.add(self.right_word_index)
            
            # 获取下一个单词的索引
            next_index = self.right_word_index + 1
            
            # 检查下一个单词是否已回答过
            if next_index < len(self.words_list) and next_index in self.right_answered_words:
                # 如果下一个单词已回答过，直接显示它
                self.right_word_index = next_index
                self.show_right_word()
            else:
                # 如果下一个单词未回答过，查找下一个未回答的单词
                while next_index < len(self.words_list) and next_index in self.right_answered_words:
                    next_index += 1
                
                if next_index < len(self.words_list):
                    self.right_word_index = next_index
                    self.show_right_word()
                else:
                    # 所有单词都已回答
                    if self.learning_mode == "无尽模式":
                        # 无尽模式：重置已回答单词集合
                        self.right_answered_words.clear()
                        self.right_word_index = 0
                        self.show_right_word()
                        
                        InfoBar.info(
                            title="不重复模式",
                            content="所有单词已学习一遍，重新开始！",
                            duration=2000,
                            parent=self
                        )
                    else:
                        # 总题数模式：显示提示
                        InfoBar.info(
                            title="不重复模式",
                            content="所有单词已学习一遍！",
                            duration=2000,
                            parent=self
                        )
        else:
            # 重复模式下，直接翻到下一个单词
            if self.right_word_index < len(self.words_list) - 1:
                # 如果当前单词已回答（通过选项选择或显示答案），则将其添加到已回答集合
                if self.right_answer_shown:
                    self.right_answered_words.add(self.right_word_index)
                self.right_word_index += 1
                self.show_right_word()
            
    def import_vocabulary(self):
        """导入词库文件"""
        dialog = ImportVocabularyDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            try:
                file_path, file_type, column_mapping = dialog.get_result()
                # 获取原始文件名（不含扩展名）作为词库名称
                vocabulary_type = os.path.splitext(os.path.basename(file_path))[0]
                
                # 获取文件扩展名
                file_ext = os.path.splitext(file_path)[1].lower()
                
                # 确保documents目录存在
                ensure_dir('app/resource/documents')
                
                # 确定目标文件名（保留原始扩展名）
                target_file = path_manager.get_absolute_path(f'app/resource/documents/{vocabulary_type}{file_ext}')
                
                # 复制文件到documents目录
                shutil.copy2(file_path, target_file)
                
                # 保存列映射配置
                mapping_file = path_manager.get_absolute_path('app/resource/documents/vocabulary_mapping.json')
                
                # 读取现有配置（如果存在）
                mapping_data = {}
                if os.path.exists(mapping_file):
                    try:
                        with open_file(mapping_file, 'r', encoding='utf-8') as f:
                            mapping_data = json.load(f)
                    except Exception as e:
                        logger.error(f"读取现有配置文件失败: {str(e)}，将创建新配置")
                        mapping_data = {}
                
                # 更新或添加当前词汇表的配置
                mapping_data[vocabulary_type] = {
                    'file_type': file_type,
                    'column_mapping': column_mapping
                }
                
                # 保存更新后的配置
                with open_file(mapping_file, 'w', encoding='utf-8') as f:
                    json.dump(mapping_data, f, ensure_ascii=False, indent=2)
                
                # 重新加载词库
                self.load_vocabulary()
                
                # 刷新词库下拉框
                self.refresh_vocabulary_combo()
                
                # 显示成功消息
                InfoBar.success(
                    title="导入成功",
                    content=f"成功导入{vocabulary_type}文件: {os.path.basename(file_path)}",
                    duration=3000,
                    parent=self
                )
                
            except Exception as e:
                logger.error(f"导入词库失败: {str(e)}")
                # 显示错误消息
                InfoBar.error(
                    title="导入失败",
                    content=f"导入词库失败: {str(e)}",
                    duration=3000,
                    parent=self
                )
    
    def update_learning_status(self):
        """更新学习状态显示"""
        if self.learning_mode == "总题数模式":
            # 更新学习状态显示
            self.learning_status_label.setText(f"总题数: {self.total_questions} | 已答题: {self.questions_answered}")
        elif self.learning_mode == "倒计时模式":
            # 倒计时模式由update_countdown方法处理
            pass
        else:  # 无尽模式
            # 更新学习状态显示
            self.learning_status_label.setText(f"无尽模式 | 已答题: {self.questions_answered}")
            
    def update_countdown(self):
        """更新倒计时显示"""
        # 减少剩余时间
        self.remaining_time -= 1
        
        # 更新学习状态显示
        hours = self.remaining_time // 3600
        minutes = (self.remaining_time % 3600) // 60
        seconds = self.remaining_time % 60
        self.learning_status_label.setText(f"剩余时间: {hours:02d}:{minutes:02d}:{seconds:02d}")
        
        # 检查是否时间到了
        if self.remaining_time <= 0:
            # 停止计时器
            if hasattr(self, 'timer') and self.timer is not None:
                self.timer.stop()
            
            # 显示时间到的提示
            InfoBar.info(
                title="时间到",
                content="倒计时已结束，学习自动停止",
                duration=3000,
                parent=self
            )
            
            # 禁用按钮
            self.next_button.setEnabled(False)
            self.prev_button.setEnabled(False)
            self.show_answer_button.setEnabled(False)
            
            # 如果是双人模式，也禁用右侧按钮
            if self.is_dual_mode:
                self.right_next_button.setEnabled(False)
                self.right_prev_button.setEnabled(False)
                self.right_show_answer_button.setEnabled(False)


class ImportVocabularyDialog(QDialog):
    # 🌟 小鸟游星野：单词库导入对话框 ~ (๑•̀ㅂ•́)ญ✧
    def __init__(self, parent=None):
        super().__init__(parent)
        # 🌟 星穹铁道白露：设置无边框但可调整大小的窗口样式并解决屏幕设置冲突~ 
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self.setWindowTitle("导入单词库")
        self.setMinimumSize(600, 535)  # 设置最小大小而不是固定大小
        self.saved = False
        self.dragging = False
        self.drag_position = None
        
        # 确保不设置子窗口的屏幕属性
        if parent is not None:
            self.setParent(parent)
        
        # 🐦 小鸟游星野：创建自定义标题栏啦~ (≧∇≦)ﾉ
        self.title_bar = QWidget()
        self.title_bar.setObjectName("CustomTitleBar")
        self.title_bar.setFixedHeight(35)
        
        # 标题栏布局
        title_layout = QHBoxLayout(self.title_bar)
        title_layout.setContentsMargins(10, 0, 10, 0)
        
        # 窗口标题
        self.title_label = QLabel("导入单词库")
        self.title_label.setObjectName("TitleLabel")
        self.title_label.setFont(QFont(load_custom_font(), 12))
        
        # 窗口控制按钮
        self.close_btn = QPushButton("✕")
        self.close_btn.setObjectName("CloseButton")
        self.close_btn.setFixedSize(25, 25)
        self.close_btn.clicked.connect(self.reject)
        
        # 添加组件到标题栏
        title_layout.addWidget(self.title_label)
        title_layout.addStretch()
        title_layout.addWidget(self.close_btn)

        
        self.dragging = False
        self.drag_position = None

        # 确保不设置子窗口的屏幕属性
        if parent is not None:
            self.setParent(parent)
        
        # 🐦 小鸟游星野：创建自定义标题栏啦~ (≧∇≦)ﾉ
        self.title_bar = QWidget()
        self.title_bar.setObjectName("CustomTitleBar")
        self.title_bar.setFixedHeight(35)
        
        # 标题栏布局
        title_layout = QHBoxLayout(self.title_bar)
        title_layout.setContentsMargins(10, 0, 10, 0)
        
        # 窗口标题
        self.title_label = QLabel("导入单词库")
        self.title_label.setObjectName("TitleLabel")
        self.title_label.setFont(QFont(load_custom_font(), 12))
        
        # 窗口控制按钮
        self.close_btn = QPushButton("✕")
        self.close_btn.setObjectName("CloseButton")
        self.close_btn.setFixedSize(25, 25)
        self.close_btn.clicked.connect(self.reject)
        
        # 添加组件到标题栏
        title_layout.addWidget(self.title_label)
        title_layout.addStretch()
        title_layout.addWidget(self.close_btn)

        self.file_path = None
        self.file_type = 'excel'
        self.column_mapping = {'单词': -1, '音标': -1, '释义': -1, '例句': -1}
        self.include_columns = {'音标': True, '释义': True, '例句': True}
        # 🌟 小鸟游星野：初始化处理后的数据 ~ (๑•̀ㅂ•́)ญ✧
        self.processed_data = None

        self.update_theme_style()
        qconfig.themeChanged.connect(self.update_theme_style)
        self.init_ui()

    def mousePressEvent(self, event):
        # 🐦 小鸟游星野：窗口拖动功能~ 按住标题栏就能移动啦 (๑•̀ㅂ•́)و✧
        if event.button() == Qt.LeftButton and self.title_bar.underMouse():
            self.dragging = True
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.dragging and event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        self.dragging = False

    def update_theme_style(self):
        # 🌟 星穹铁道白露：主题样式更新 ~ 现在包含自定义标题栏啦！
        colors = {'text': '#F5F5F5', 'bg': '#111116', 'title_bg': '#2D2D2D'} if is_dark else {'text': '#111116', 'bg': '#F5F5F5', 'title_bg': '#E0E0E0'}
        self.setStyleSheet(f"""
            QDialog, QDialog * {{
                color: {colors['text']};
                background-color: {colors['bg']};
            }}
            #CustomTitleBar {{
                background-color: {colors['title_bg']};
            }}
            #TitleLabel {{
                color: {colors['text']};
                font-weight: bold; padding: 5px;
                background-color: transparent;
            }}
            #CloseButton {{ 
                background-color: transparent; 
                color: {colors['text']}; 
                border-radius: 4px; 
                font-weight: bold; 
            }}
            #CloseButton:hover {{
                background-color: #ff4d4d;
                color: white;
            }}
        """)

        # 设置标题栏颜色以匹配背景色（仅Windows系统）
        if os.name == 'nt':
            try:
                import ctypes
                # 🌟 星穹铁道白露：修复参数类型错误~ 现在要把窗口ID转成整数才行哦！
                hwnd = int(self.winId())  # 转换为整数句柄
                
                # 🐦 小鸟游星野：颜色格式要改成ARGB才行呢~ 添加透明度通道(๑•̀ㅂ•́)و✧
                bg_color = colors['bg'].lstrip('#')
                # 转换为ARGB格式（添加不透明通道）
                rgb_color = int(f'FF{bg_color}', 16) if len(bg_color) == 6 else int(bg_color, 16)
                
                # 设置窗口标题栏颜色
                ctypes.windll.dwmapi.DwmSetWindowAttribute(
                    ctypes.c_int(hwnd),  # 窗口句柄（整数类型）
                    35,  # DWMWA_CAPTION_COLOR
                    ctypes.byref(ctypes.c_uint(rgb_color)),  # 颜色值指针
                    ctypes.sizeof(ctypes.c_uint)  # 数据大小
                )
            except Exception as e:
                logger.error(f"设置标题栏颜色失败: {str(e)}")

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 添加自定义标题栏
        layout.addWidget(self.title_bar)

        # 创建内容区域布局
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(10, 10, 10, 10)
        content_layout.setSpacing(10)

        # 文件选择区域
        file_layout = QHBoxLayout()
        self.file_path_edit = LineEdit()
        self.file_path_edit.setReadOnly(True)
        browse_btn = PrimaryPushButton("浏览文件")
        browse_btn.setFont(QFont(load_custom_font(), 12))
        browse_btn.clicked.connect(self.browse_file)
        file_layout.addWidget(self.file_path_edit)
        file_layout.addWidget(browse_btn)
        content_layout.addLayout(file_layout)

        # 文件类型选择
        type_layout = QHBoxLayout()
        type_label = BodyLabel("文件类型：")
        type_label.setFont(QFont(load_custom_font(), 12))
        self.type_combo = ComboBox()
        self.type_combo.setFont(QFont(load_custom_font(), 12))
        self.type_combo.addItems(["Excel文件 (*.xlsx)", "CSV文件 (*.csv)"])
        self.type_combo.currentIndexChanged.connect(self.change_file_type)
        type_layout.addWidget(type_label)
        type_layout.addWidget(self.type_combo)
        content_layout.addLayout(type_layout)

        # 列映射区域
        mapping_group = QGroupBox("") 
        mapping_group.setFont(QFont(load_custom_font(), 12))
        mapping_layout = QFormLayout()

        # 创建列选择控件
        self._create_combo_row(mapping_layout, 'word_combo', '单词列：')
        self._create_checkable_combo_row(mapping_layout, 'phonetic_combo', 'phonetic_check', '音标列：', '音标')
        self._create_checkable_combo_row(mapping_layout, 'meaning_combo', 'meaning_check', '释义列：', '释义')
        self._create_checkable_combo_row(mapping_layout, 'example_combo', 'example_check', '例句列：', '例句')

        mapping_group.setLayout(mapping_layout)
        content_layout.addWidget(mapping_group)

        # 按钮区域
        btn_layout = QHBoxLayout()
        cancel_btn = PushButton("取消")
        cancel_btn.setFont(QFont(load_custom_font(), 12))
        ok_btn = PrimaryPushButton("导入")
        ok_btn.setFont(QFont(load_custom_font(), 12))
        cancel_btn.clicked.connect(self.reject)
        ok_btn.clicked.connect(self.accept)
        btn_layout.addStretch(1)
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(ok_btn)
        content_layout.addLayout(btn_layout)

        # 添加内容区域到主布局
        layout.addLayout(content_layout)
        self.setLayout(layout)

    def _create_combo_box(self):
        # 🌟 小鸟游星野：创建下拉框 ~ (๑•̀ㅂ•́)ญ✧
        combo = ComboBox()
        combo.setFont(QFont(load_custom_font(), 12))
        combo.addItem('请选择')
        return combo

    def _create_combo_row(self, layout, combo_attr, label_text):
        # 🌟 星穹铁道白露：创建下拉框行 ~ (๑•̀ㅂ•́)ญ✧
        row_layout = QHBoxLayout()
        combo = self._create_combo_box()
        combo.setFixedWidth(200)
        setattr(self, combo_attr, combo)
        row_layout.addWidget(combo)
        layout.addRow(label_text, row_layout)

    def _create_checkable_combo_row(self, layout, combo_attr, check_attr, label_text, column_name):
        # 🌟 星穹铁道白露：创建带复选框的下拉框行 ~ (๑•̀ㅂ•́)ญ✧
        row_layout = QHBoxLayout()
        combo = self._create_combo_box()
        combo.setFixedWidth(200)
        setattr(self, combo_attr, combo)

        check_box = CheckBox("包含")
        check_box.setFont(QFont(load_custom_font(), 12))
        check_box.setChecked(True)
        check_box.stateChanged.connect(lambda: self.toggle_column(column_name))
        setattr(self, check_attr, check_box)

        row_layout.addWidget(combo)
        row_layout.addWidget(check_box)
        layout.addRow(label_text, row_layout)

    def change_file_type(self, index):
        # 🌟 星穹铁道白露：切换文件类型并更新UI状态 ~ (๑•̀ㅂ•́)ญ✧
        types = ['excel', 'csv']
        self.file_type = types[index]
        
        # 清除并重新加载列数据
        self.file_path_edit.clear()
        self.file_path = None
        self.clear_columns()

    def browse_file(self):
        filters = {
            # 🌟 星穹铁道白露：支持xls和xlsx格式的Excel文件 ~ (๑•̀ㅂ•́)ญ✧
            'excel': "Excel Files (*.xlsx)",
            'csv': "CSV Files (*.csv)"
        }
        self.file_path, _ = QFileDialog.getOpenFileName(
            self, "选择文件", "", filters[self.file_type]
        )
        if self.file_path:
            self.file_path_edit.setText(self.file_path)
            self.load_columns()

    def clear_columns(self):
        # 🌟 小鸟游星野：清空列选择控件 ~ (๑•̀ㅂ•́)ญ✧
        for combo in [self.word_combo, self.phonetic_combo, self.meaning_combo, self.example_combo]:
            combo.clear()
            combo.addItem('请选择')
        self.update_mapping()

    def load_columns(self):
        # 🌟 白露：加载文件列名中~ 请稍等一下哦 (๑•̀ㅂ•́)ญ✧
        try:
            if self.file_type == 'excel':
                self._load_excel_columns()
            elif self.file_type == 'csv' or self.file_type == 'namepicker':
                self._load_csv_columns()
        except Warning as w:
            # 🌟 小鸟游星野：处理提示性警告，不清除文件路径 ~ (๑•̀ㅂ•́)ญ✧
            logger.error(f"列选择提示: {str(w)}")
            msg_box = MessageBox("列选择提示", str(w), self)
            msg_box.yesButton.setText("确定")
            msg_box.cancelButton.hide()
            msg_box.buttonLayout.insertStretch(1)
            msg_box.exec_()
        except Exception as e:
            logger.error(f"加载文件列失败: {str(e)}")
            # 🌟 小鸟游星野：文件加载失败提示 ~ (๑•̀ㅂ•́)ญ✧
            w = MessageBox("加载失败", f"无法读取文件: {str(e)}", self)
            w.yesButton.setText("确定")
            w.cancelButton.hide()
            w.buttonLayout.insertStretch(1)
            w.exec_()
            self.file_path = None
            self.file_path_edit.clear()

    def _init_combo_boxes(self, columns):
        # 🌟 小鸟游星野：初始化所有下拉框 ~ (๑•̀ㅂ•́)ญ✧
        column_items = ['请选择'] + [str(col) for col in columns]
        for combo in [self.word_combo, self.phonetic_combo, self.meaning_combo, self.example_combo]:
            combo.clear()
            combo.addItems(column_items)
            combo.setVisible(True)
        self.update_mapping()

    def _auto_select_columns(self, columns):
        # 🌟 星穹铁道白露：智能列匹配 ~ (๑•̀ㅂ•́)ญ✧
        fields = [
            (self.word_combo, ['word', '单词', 'vocabulary', 'term'], True, '单词'),
            (self.phonetic_combo, ['phonetic', '音标', 'pronunciation'], False, '音标'),
            (self.meaning_combo, ['meaning', '释义', 'definition', 'chinese'], False, '释义'),
            (self.example_combo, ['example', '例句', 'sentence'], False, '例句')
        ]

        # 检查是否为数字列名（如CSV文件没有标题行的情况）
        is_numeric_columns = all(str(col).isdigit() for col in columns)
        
        if is_numeric_columns and len(columns) >= 1:
            # 如果列名都是数字，默认第一列作为单词
            self.word_combo.setCurrentIndex(1)  # 第一列
            # 可选列不自动选择
            self.phonetic_check.setChecked(False)
            self.meaning_check.setChecked(False)
            self.example_check.setChecked(False)
        else:
            # 正常的列名匹配逻辑
            for combo, keywords, is_required, field_name in fields:
                # 自动选择匹配项
                auto_selected = False
                for i, col in enumerate(columns):
                    if any(key in str(col).lower() for key in keywords):
                        combo.setCurrentIndex(i + 1)  # +1是因为第一个选项是"请选择"
                        auto_selected = True
                        break

                # 必选列验证
                self._validate_required_column(combo, is_required, field_name, columns)

                # 可选列未找到匹配时取消勾选
                if not is_required and not auto_selected:
                    if field_name == '音标':
                        self.phonetic_check.setChecked(False)
                    elif field_name == '释义':
                        self.meaning_check.setChecked(False)
                    elif field_name == '例句':
                        self.example_check.setChecked(False)

        self.update_mapping()
        self._validate_mandatory_columns()

    def _validate_required_column(self, combo, is_required, field_name, columns):
        # 🌟 小鸟游星野：必选列验证 ~ (๑•̀ㅂ•́)ญ✧
        if is_required and combo.currentIndex() == 0:  # 0表示"请选择"
            if columns:
                combo.setCurrentIndex(1)  # 选择第一列数据
                raise Warning(f"已自动选择第一列作为{field_name}列，请确认是否正确")
            else:
                raise Exception(f"必须选择{field_name}对应的列")

    def _validate_mandatory_columns(self):
        # 🌟 星穹铁道白露：验证用户选择 ~ (๑•̀ㅂ•́)ญ✧
        if self.column_mapping['单词'] == -1:
            raise Exception("必须选择单词对应的列")

    def _load_excel_columns(self):
        # 🌟 星穹铁道白露：加载Excel列并智能匹配 ~ (๑•̀ㅂ•́)ญ✧
        df = pd.read_excel(self.file_path)
        columns = list(df.columns)
        self._init_combo_boxes(columns)
        self._auto_select_columns(columns)

    def _load_csv_columns(self):
        # 🌟 星穹铁道白露：加载CSV列并智能匹配 ~ (๑•̀ㅂ•́)ญ✧
        df = self._read_csv_file(self.file_path)
        columns = list(df.columns)
        self._init_combo_boxes(columns)
        self._auto_select_columns(columns)

    def update_mapping(self):
        # 🌟 白露：更新列映射，确保索引正确计算~ (๑•̀ㅂ•́)ญ✧
        self.column_mapping['单词'] = self.word_combo.currentIndex() - 1 if self.word_combo.currentIndex() > 0 else -1
        self.column_mapping['音标'] = self.phonetic_combo.currentIndex() - 1 if (self.phonetic_check.isChecked() and self.phonetic_combo.currentIndex() > 0) else -1
        self.column_mapping['释义'] = self.meaning_combo.currentIndex() - 1 if (self.meaning_check.isChecked() and self.meaning_combo.currentIndex() > 0) else -1
        self.column_mapping['例句'] = self.example_combo.currentIndex() - 1 if (self.example_check.isChecked() and self.example_combo.currentIndex() > 0) else -1

    def toggle_column(self, column):
        self.include_columns[column] = not self.include_columns[column]
        self.update_mapping()

    def accept(self):
        # 🌟 小鸟游星野：检查必要条件是否满足并执行导入~ (๑•̀ㅂ•́)ญ✧
        self.update_mapping()
        if not self.file_path:
            self._show_error_message("文件未选择", "请先选择导入文件！")
            return

        # 根据文件类型执行不同的验证逻辑
        validation_methods = {
            'excel': self._validate_excel,
            'csv': self._validate_csv_json
        }

        validator = validation_methods.get(self.file_type)
        if validator and not validator():
            return

        try:
            # 获取词库名称
            file_name = os.path.basename(self.file_path)
            vocabulary_name = os.path.splitext(file_name)[0]
            
            # 🌟 传递最新列映射给导入方法 ~ (๑•̀ㅂ•́)ญ✧
            self.processed_data = self._import_data()
            self._show_success_message("导入成功", f"单词库导入成功！\n共导入 {len(self.processed_data)} 条记录")
            super().accept()
        except Exception as e:
            logger.error(f"导入失败: {str(e)}")
            self._show_error_message("导入失败", f"导入过程中出错: {str(e)}")

    def _read_csv_file(self, file_path):
        # 小鸟游星野: 智能读取CSV文件的专用方法 ~ (｡•̀ᴗ-)✧
        encodings = ['utf-8', 'gbk', 'gb2312', 'latin-1', 'iso-8859-1', 'cp936']
        found_encoding = None
        found_sep = None
        df = None
        
        # 星穹铁道白露: 尝试不同编码和分隔符组合~ (๑•̀ㅂ•́)ญ✧
        for encoding in encodings:
            try:
                for sep in [',', ';', '\t']:
                    df = pd.read_csv(file_path, encoding=encoding, sep=sep, nrows=10)
                    if len(df.columns) > 1:
                        found_encoding = encoding
                        found_sep = sep
                        break
                if found_encoding:
                    break
            except:
                continue
        
        # 验证是否找到合适的解析方式
        if df is None:
            raise Exception("无法解析CSV文件，请检查文件格式是否正确")
        
        # 使用找到的参数读取完整文件
        return pd.read_csv(file_path, encoding=found_encoding, sep=found_sep)

    def _import_data(self):
        # 🌟 星穹铁道白露：执行单词库数据导入并返回处理后的数据 ~ (◍•ᴗ•◍)
        # 小鸟游星野: 根据文件类型选择合适的读取方式 ~ (｡•̀ᴗ-)✧
        file_ext = os.path.splitext(self.file_path)[1].lower()
        
        # 根据扩展名选择读取方法
        if file_ext in ['.xlsx', '.xls']:
            df = pd.read_excel(self.file_path)
        elif file_ext == '.csv':
            df = self._read_csv_file(self.file_path)
        else:
            raise Exception(f"不支持的文件类型: {file_ext}，请使用Excel或CSV文件")

        # 获取列映射
        word_col = self.column_mapping['单词']
        phonetic_col = self.column_mapping['音标']
        meaning_col = self.column_mapping['释义']
        example_col = self.column_mapping['例句']

        # 处理单词库数据
        vocabulary_data = []
        for index, row in df.iterrows():
            # 获取单词（必选字段）
            # 提取并清理单词（去除空白字符）
            word = str(row.iloc[word_col]).strip()

            # 验证必填字段（确保不为空）
            if not word:
                continue

            # 创建单词信息字典
            vocabulary_item = {
                'word': word,
                'phonetic': str(row.iloc[phonetic_col]).strip() if phonetic_col != -1 and not pd.isna(row.iloc[phonetic_col]) else "",
                'meaning': str(row.iloc[meaning_col]).strip() if meaning_col != -1 and not pd.isna(row.iloc[meaning_col]) else "",
                'example': str(row.iloc[example_col]).strip() if example_col != -1 and not pd.isna(row.iloc[example_col]) else ""
            }
            
            vocabulary_data.append(vocabulary_item)

        return vocabulary_data

    def _show_error_message(self, title, message):
        # 🌟 小鸟游星野：统一错误提示对话框 ~ (๑•̀ㅂ•́)ญ✧
        w = MessageBox(title, message, self)
        w.yesButton.setText("确定")
        w.cancelButton.hide()
        w.buttonLayout.insertStretch(1)
        w.exec_()

    def _show_success_message(self, title, message):
        # 🌟 小鸟游星野：统一成功提示对话框 ~ (๑•̀ㅂ•́)ญ✧
        w = MessageBox(title, message, self)
        w.yesButton.setText("确定")
        w.cancelButton.hide()
        w.buttonLayout.insertStretch(1)
        w.exec_()

    def _validate_excel(self):
        # 🌟 星穹铁道白露：Excel文件验证 ~ (๑•̀ㅂ•́)ญ✧
        if self.word_combo.currentIndex() <= 0:
            self._show_error_message("单词列未选择", "请选择有效的单词列！")
            return False

        # 可选列未选择时自动取消勾选
        if self.phonetic_check.isChecked() and self.phonetic_combo.currentIndex() <= 0:
            self.phonetic_check.setChecked(False)
        if self.meaning_check.isChecked() and self.meaning_combo.currentIndex() <= 0:
            self.meaning_check.setChecked(False)
        if self.example_check.isChecked() and self.example_combo.currentIndex() <= 0:
            self.example_check.setChecked(False)

        # 验证列选择唯一性
        selected_columns = []
        if self.word_combo.currentIndex() > 0:
            selected_columns.append(self.word_combo.currentIndex() - 1)
        if self.phonetic_check.isChecked() and self.phonetic_combo.currentIndex() > 0:
            selected_columns.append(self.phonetic_combo.currentIndex() - 1)
        if self.meaning_check.isChecked() and self.meaning_combo.currentIndex() > 0:
            selected_columns.append(self.meaning_combo.currentIndex() - 1)
        if self.example_check.isChecked() and self.example_combo.currentIndex() > 0:
            selected_columns.append(self.example_combo.currentIndex() - 1)

        # 检查重复选择
        if len(selected_columns) != len(set(selected_columns)):
            self._show_error_message("列选择错误", "不能选择重复的列！请确保所有选中的列都是唯一的。")
            return False

        return True

    def _validate_csv_json(self):
        # 🌟 星穹铁道白露：CSV/JSON文件验证 ~ (๑•̀ㅂ•́)ญ✧
        if self.word_combo.currentIndex() <= 0:
            self._show_error_message("验证失败", "文件缺少必要的单词列！")
            return False

        # 可选列未选择时自动取消勾选
        if self.phonetic_check.isChecked() and self.phonetic_combo.currentIndex() <= 0:
            self.phonetic_check.setChecked(False)
        if self.meaning_check.isChecked() and self.meaning_combo.currentIndex() <= 0:
            self.meaning_check.setChecked(False)
        if self.example_check.isChecked() and self.example_combo.currentIndex() <= 0:
            self.example_check.setChecked(False)

        # 验证列选择唯一性
        selected_columns = []
        if self.word_combo.currentIndex() > 0:
            selected_columns.append(self.word_combo.currentIndex() - 1)
        if self.phonetic_check.isChecked() and self.phonetic_combo.currentIndex() > 0:
            selected_columns.append(self.phonetic_combo.currentIndex() - 1)
        if self.meaning_check.isChecked() and self.meaning_combo.currentIndex() > 0:
            selected_columns.append(self.meaning_combo.currentIndex() - 1)
        if self.example_check.isChecked() and self.example_combo.currentIndex() > 0:
            selected_columns.append(self.example_combo.currentIndex() - 1)

        # 检查重复选择
        if len(selected_columns) != len(set(selected_columns)):
            self._show_error_message("列选择错误", "不能选择重复的列！请确保所有选中的列都是唯一的。")
            return False

        return True

    def get_processed_data(self):
        # 🌟 星穹铁道白露：返回处理后的单词库数据 ~ (◍•ᴗ•◍)
        return self.processed_data

    def get_result(self):
        return self.file_path, self.file_type, self.column_mapping
