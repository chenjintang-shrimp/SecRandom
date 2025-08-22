# ================================================== ✧*｡٩(ˊᗜˋ*)و✧*｡
# 魔法导入水晶球 🔮
# ================================================== ✧*｡٩(ˊᗜˋ*)و✧*｡

# ✨ 系统自带魔法道具 ✨
import os
import json
import webbrowser
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from qfluentwidgets import *
from loguru import logger

# 🏰 应用内部魔法卷轴 🏰
from app.common.config import get_theme_icon, load_custom_font, VERSION
from app.common.path_utils import path_manager
from app.common.path_utils import open_file, ensure_dir


class GuideWindow(MSFluentWindow):
    """(^・ω・^ ) 白露的引导精灵！
    为首次使用SecRandom的用户提供友好的引导界面～
    帮助用户快速了解软件功能和使用方法！✨"""
    
    # 定义信号
    start_signal = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('欢迎使用 SecRandom')
        self.setWindowIcon(QIcon(path_manager.get_resource_path('icon/SecRandom.png')))
        self.resize(800, 600)
        
        # 设置窗口居中
        self.center_window()
        
        # 创建引导界面
        self.setup_ui()
        
        logger.info("白露引导: 引导窗口已创建～ ")
    
    def center_window(self):
        """(^・ω・^ ) 白露的窗口居中魔法！
        让引导窗口出现在屏幕正中央，视觉效果最佳哦～ ✨"""
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)
    
    def setup_ui(self):
        """(^・ω・^ ) 白露的界面布置魔法！
        精心设计引导界面的布局和内容～ 让用户一目了然！(๑•̀ㅂ•́)و✧)"""
        
        # 创建多个引导页面
        self.create_guide_pages()
        
        # 初始化导航系统
        self.initNavigation()
        
        # 显示第一个引导页面
        self.switchTo(self.welcomeInterface)
        
        # 当前页面索引
        self.current_page_index = 0
        self.total_pages = 6
        
        # 将底部按钮容器添加到窗口主布局
        self.add_bottom_buttons()
    
    def create_guide_pages(self):
        """(^・ω・^ ) 白露的多页面创建魔法！
        创建多个引导页面，每个页面展示不同的内容～ ✨"""
        
        # 1. 欢迎页面
        self.welcomeInterface = QWidget()
        self.welcomeInterface.setObjectName("welcomeInterface")
        
        # 创建滚动区域
        welcome_scroll_area = SingleDirectionScrollArea(self.welcomeInterface)
        welcome_scroll_area.setWidgetResizable(True)
        # 设置样式表
        welcome_scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollArea QWidget {
                border: none;
                background-color: transparent;
            }
        """)
        # 启用鼠标滚轮
        QScroller.grabGesture(welcome_scroll_area.viewport(), QScroller.LeftMouseButtonGesture)
        # 创建内部框架
        welcome_inner_frame = QWidget(welcome_scroll_area)
        welcome_layout = QVBoxLayout(welcome_inner_frame)
        welcome_layout.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignTop)
        welcome_scroll_area.setWidget(welcome_inner_frame)
        
        # 设置欢迎页面布局
        welcome_main_layout = QVBoxLayout(self.welcomeInterface)
        welcome_main_layout.addWidget(welcome_scroll_area)
        
        welcome_layout.setSpacing(12)
        welcome_layout.setContentsMargins(25, 25, 25, 25)
        welcome_layout.setAlignment(Qt.AlignCenter)
        
        # 大标题
        title_label = TitleLabel('🎉 欢迎使用 SecRandom 🎉')
        title_label.setFont(QFont(load_custom_font(), 20))
        title_label.setAlignment(Qt.AlignCenter)
        welcome_layout.addWidget(title_label)
        
        # 副标题
        subtitle_label = BodyLabel('一个简洁、美观、公平、易用的班级点名软件')
        subtitle_label.setFont(QFont(load_custom_font(), 13))
        subtitle_label.setAlignment(Qt.AlignCenter)
        welcome_layout.addWidget(subtitle_label)

        # 当前版本
        version_label = BodyLabel(f'当前版本：{VERSION}')
        version_label.setFont(QFont(load_custom_font(), 13))
        version_label.setAlignment(Qt.AlignCenter)
        welcome_layout.addWidget(version_label)
        
        # 功能特点介绍
        features_layout = QVBoxLayout()
        features_layout.setSpacing(8)
        features_layout.setAlignment(Qt.AlignCenter)

        features_title = SubtitleLabel('✨ 主要功能特点')
        features_title.setFont(QFont(load_custom_font(), 18))
        features_title.setAlignment(Qt.AlignCenter)
        features_layout.addWidget(features_title)
        
        features_content = BodyLabel(
            '🎯 随机抽人：公平公正的随机选择，让每个人都有机会参与\n'
            '🎁 幸运抽奖：支持多种抽奖模式，增加课堂趣味性\n'
            '📊 历史记录：完整记录抽取历史，方便查看和统计\n'
            '🎨 美观界面：现代化设计，支持深色/浅色主题切换\n'
            '⚙️ 灵活配置：支持多种名单管理，满足不同使用场景\n'
            '🔒 安全可靠：本地数据存储，保护用户隐私安全'
        )
        features_content.setFont(QFont(load_custom_font(), 12))
        features_content.setWordWrap(True)
        features_content.setAlignment(Qt.AlignLeft)
        features_layout.addWidget(features_content)
        
        welcome_layout.addLayout(features_layout)
        welcome_layout.addStretch()
        
        # 2. 抽人名单设置页面
        self.setupPeopleInterface = QWidget()
        self.setupPeopleInterface.setObjectName("setupPeopleInterface")
        
        # 创建滚动区域
        setup_people_scroll_area = SingleDirectionScrollArea(self.setupPeopleInterface)
        setup_people_scroll_area.setWidgetResizable(True)
        # 设置样式表
        setup_people_scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollArea QWidget {
                border: none;
                background-color: transparent;
            }
        """)
        # 启用鼠标滚轮
        QScroller.grabGesture(setup_people_scroll_area.viewport(), QScroller.LeftMouseButtonGesture)
        # 创建内部框架
        setup_people_inner_frame = QWidget(setup_people_scroll_area)
        setup_people_layout = QVBoxLayout(setup_people_inner_frame)
        setup_people_layout.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignTop)
        setup_people_scroll_area.setWidget(setup_people_inner_frame)
        
        # 设置抽人名单设置页面布局
        setup_people_main_layout = QVBoxLayout(self.setupPeopleInterface)
        setup_people_main_layout.addWidget(setup_people_scroll_area)
        
        setup_people_layout.setSpacing(12)
        setup_people_layout.setContentsMargins(25, 25, 25, 25)
        setup_people_layout.setAlignment(Qt.AlignCenter)

        # 标题
        setup_people_title = SubtitleLabel('🎯 随机抽人名单设置')
        setup_people_title.setFont(QFont(load_custom_font(), 18))
        setup_people_title.setAlignment(Qt.AlignCenter)
        setup_people_layout.addWidget(setup_people_title)
        
        # 详细步骤
        steps_content = BodyLabel(
            '1. 右键点击任务栏右侧的 SecRandom 托盘图标\n'
            '2. 在弹出菜单中选择「打开设置界面」\n'
            '3. 在设置界面中找到「抽人名单」选项\n'
            '4. 点击「添加名单」按钮，输入名单名称（如：班级名单）\n'
            '5. 在名单中添加人员信息，支持手动添加或批量导入\n'
            '6. 设置抽取规则：是否允许重复抽取、抽取权重等\n'
            '7. 保存设置后即可开始使用随机抽取功能'
        )
        steps_content.setFont(QFont(load_custom_font(), 12))
        steps_content.setWordWrap(True)
        steps_content.setAlignment(Qt.AlignLeft)
        setup_people_layout.addWidget(steps_content)
        
        # 功能特点
        features_content = BodyLabel(
            '✨ 主要功能特点：\n\n'
            '• 公平随机：确保每个人被抽中的概率均等\n'
            '• 权重设置：可以为不同人员设置不同的抽取权重\n'
            '• 重复抽取：可设置是否允许同一人被重复抽中\n'
            '• 批量导入：支持从Excel/CSV文件批量导入名单\n'
            '• 历史记录：完整记录抽取历史，方便查看和统计'
        )
        features_content.setFont(QFont(load_custom_font(), 12))
        features_content.setWordWrap(True)
        features_content.setAlignment(Qt.AlignLeft)
        setup_people_layout.addWidget(features_content)
        
        setup_people_layout.addStretch()
        
        # 3. 抽奖名单设置页面
        self.setupRewardInterface = QWidget()
        self.setupRewardInterface.setObjectName("setupRewardInterface")
        
        # 创建滚动区域
        setup_reward_scroll_area = SingleDirectionScrollArea(self.setupRewardInterface)
        setup_reward_scroll_area.setWidgetResizable(True)
        # 设置样式表
        setup_reward_scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollArea QWidget {
                border: none;
                background-color: transparent;
            }
        """)
        # 启用鼠标滚轮
        QScroller.grabGesture(setup_reward_scroll_area.viewport(), QScroller.LeftMouseButtonGesture)
        # 创建内部框架
        setup_reward_inner_frame = QWidget(setup_reward_scroll_area)
        setup_reward_layout = QVBoxLayout(setup_reward_inner_frame)
        setup_reward_layout.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignTop)
        setup_reward_scroll_area.setWidget(setup_reward_inner_frame)
        
        # 设置抽奖名单设置页面布局
        setup_reward_main_layout = QVBoxLayout(self.setupRewardInterface)
        setup_reward_main_layout.addWidget(setup_reward_scroll_area)
        
        setup_reward_layout.setSpacing(12)
        setup_reward_layout.setContentsMargins(25, 25, 25, 25)
        setup_reward_layout.setAlignment(Qt.AlignCenter)

        
        # 标题
        setup_reward_title = SubtitleLabel('🎁 幸运抽奖名单设置')
        setup_reward_title.setFont(QFont(load_custom_font(), 18))
        setup_reward_title.setAlignment(Qt.AlignCenter)
        setup_reward_layout.addWidget(setup_reward_title)
        
        # 详细步骤
        reward_steps = BodyLabel(
            '1️. 在设置界面中找到「抽奖名单」选项\n'
            '2️. 点击「添加名单」按钮，输入名单名称（如：奖品名单）\n'
            '3️. 添加奖品信息，包括奖品名称、数量、概率等\n'
            '4️. 设置抽奖规则：每人可抽奖次数、中奖概率等\n'
            '5️. 保存设置后即可开始使用抽奖功能'
        )
        reward_steps.setFont(QFont(load_custom_font(), 12))
        reward_steps.setWordWrap(True)
        reward_steps.setAlignment(Qt.AlignLeft)
        setup_reward_layout.addWidget(reward_steps)
        
        # 功能特点
        reward_features = BodyLabel(
            '✨ 抽奖功能特点：\n\n'
            '• 多种奖品：支持设置多个不同奖品\n'
            '• 概率控制：精确控制每个奖品的中奖概率\n'
            '• 公平公正：采用随机算法确保抽奖公平性'
        )
        reward_features.setFont(QFont(load_custom_font(), 12))
        reward_features.setWordWrap(True)
        reward_features.setAlignment(Qt.AlignLeft)
        setup_reward_layout.addWidget(reward_features)
        
        setup_reward_layout.addStretch()
        
        # 4. 使用技巧页面
        self.tipsInterface = QWidget()
        self.tipsInterface.setObjectName("tipsInterface")
        
        # 创建滚动区域
        tips_scroll_area = SingleDirectionScrollArea(self.tipsInterface)
        tips_scroll_area.setWidgetResizable(True)
        # 设置样式表
        tips_scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollArea QWidget {
                border: none;
                background-color: transparent;
            }
        """)
        # 启用鼠标滚轮
        QScroller.grabGesture(tips_scroll_area.viewport(), QScroller.LeftMouseButtonGesture)
        # 创建内部框架
        tips_inner_frame = QWidget(tips_scroll_area)
        tips_layout = QVBoxLayout(tips_inner_frame)
        tips_layout.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignTop)
        tips_scroll_area.setWidget(tips_inner_frame)
        
        # 设置使用技巧页面布局
        tips_main_layout = QVBoxLayout(self.tipsInterface)
        tips_main_layout.addWidget(tips_scroll_area)
        
        tips_layout.setSpacing(12)
        tips_layout.setContentsMargins(25, 25, 25, 25)
        tips_layout.setAlignment(Qt.AlignCenter)

        # 标题
        tips_title = SubtitleLabel('💡 使用小技巧')
        tips_title.setFont(QFont(load_custom_font(), 18))
        tips_title.setAlignment(Qt.AlignCenter)
        tips_layout.addWidget(tips_title)
        
        # 批量操作技巧
        batch_section = QVBoxLayout()
        batch_section.setSpacing(6)
        batch_section.setAlignment(Qt.AlignCenter)
        
        batch_title = BodyLabel('📋 批量操作技巧')
        batch_title.setFont(QFont(load_custom_font(), 16))
        batch_title.setAlignment(Qt.AlignCenter)
        batch_section.addWidget(batch_title)
        
        batch_content = BodyLabel(
            '• 支持从Excel/CSV文件批量导入名单\n'
            '• 可以一次性添加多个人员信息\n'
            '• 支持批量编辑人员信息和权重\n'
            '• 可以导出名单为Excel或CSV格式'
        )
        batch_content.setFont(QFont(load_custom_font(), 12))
        batch_content.setWordWrap(True)
        batch_content.setAlignment(Qt.AlignLeft)
        batch_section.addWidget(batch_content)
        
        tips_layout.addLayout(batch_section)
        
        # 抽取模式技巧
        mode_section = QVBoxLayout()
        mode_section.setSpacing(6)
        mode_section.setAlignment(Qt.AlignCenter)
        
        mode_title = BodyLabel('🎯 抽取模式技巧')
        mode_title.setFont(QFont(load_custom_font(), 16))
        mode_title.setAlignment(Qt.AlignCenter)
        mode_section.addWidget(mode_title)
        
        mode_content = BodyLabel(
            '• 随机抽取：完全随机，每个人概率均等\n'
            '• 公平抽取：确保每个人被抽中的次数尽量均等'
        )
        mode_content.setFont(QFont(load_custom_font(), 12))
        mode_content.setWordWrap(True)
        mode_content.setAlignment(Qt.AlignLeft)
        mode_section.addWidget(mode_content)
        
        tips_layout.addLayout(mode_section)
        
        # 高级功能技巧
        advanced_section = QVBoxLayout()
        advanced_section.setSpacing(6)
        advanced_section.setAlignment(Qt.AlignCenter)
        
        advanced_title = BodyLabel('⚙️ 高级功能技巧')
        advanced_title.setFont(QFont(load_custom_font(), 16))
        advanced_title.setAlignment(Qt.AlignCenter)
        advanced_section.addWidget(advanced_title)
        
        advanced_content = BodyLabel(
            '• 支持历史记录查看和导出\n'
            '• 可以设置抽取结果的语音播报\n'
            '• 支持自定义抽取动画效果\n'
            '• 可以设置抽取间隔时间和音效'
        )
        advanced_content.setFont(QFont(load_custom_font(), 12))
        advanced_content.setWordWrap(True)
        advanced_content.setAlignment(Qt.AlignLeft)
        advanced_section.addWidget(advanced_content)
        
        tips_layout.addLayout(advanced_section)
        tips_layout.addStretch()
        
        # 5. 开源说明页面
        self.openSourceInterface = QWidget()
        self.openSourceInterface.setObjectName("openSourceInterface")
        
        # 创建滚动区域
        opensource_scroll_area = SingleDirectionScrollArea(self.openSourceInterface)
        opensource_scroll_area.setWidgetResizable(True)
        # 设置样式表
        opensource_scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollArea QWidget {
                border: none;
                background-color: transparent;
            }
        """)
        # 启用鼠标滚轮
        QScroller.grabGesture(opensource_scroll_area.viewport(), QScroller.LeftMouseButtonGesture)
        # 创建内部框架
        opensource_inner_frame = QWidget(opensource_scroll_area)
        open_source_layout = QVBoxLayout(opensource_inner_frame)
        open_source_layout.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignTop)
        opensource_scroll_area.setWidget(opensource_inner_frame)
        
        # 设置开源说明页面布局
        opensource_main_layout = QVBoxLayout(self.openSourceInterface)
        opensource_main_layout.addWidget(opensource_scroll_area)
        
        open_source_layout.setSpacing(10)
        open_source_layout.setContentsMargins(25, 25, 25, 25)
        
        # 标题
        open_source_title = SubtitleLabel('🌈 开源精神与自由软件')
        open_source_title.setFont(QFont(load_custom_font(), 18))
        open_source_title.setAlignment(Qt.AlignCenter)
        open_source_layout.addWidget(open_source_title)
        
        # 开源协议说明
        license_section = QVBoxLayout()
        license_section.setSpacing(6)
        license_section.setAlignment(Qt.AlignCenter)
        
        license_title = BodyLabel('📜 开源协议')
        license_title.setFont(QFont(load_custom_font(), 16))
        license_title.setAlignment(Qt.AlignCenter)
        license_section.addWidget(license_title)
        
        license_content = BodyLabel(
            'SecRandom 是基于 GNU GPLv3 协议开源的免费软件。\n\n'
            '这意味着您拥有以下自由：\n'
            '✅ 自由使用：可以自由使用软件，不受限制\n'
            '✅ 自由研究：可以查看和修改源代码\n'
            '✅ 自由分发：可以自由复制和分发软件\n'
            '✅ 自由改进：可以改进软件并分享改进版本'
        )
        license_content.setFont(QFont(load_custom_font(), 12))
        license_content.setWordWrap(True)
        license_content.setAlignment(Qt.AlignLeft)
        license_section.addWidget(license_content)
        
        open_source_layout.addLayout(license_section)
        
        # 参与贡献
        contribute_section = QVBoxLayout()
        contribute_section.setSpacing(6)
        contribute_section.setAlignment(Qt.AlignCenter)
        
        contribute_title = BodyLabel('🤝 参与贡献')
        contribute_title.setFont(QFont(load_custom_font(), 16))
        contribute_title.setAlignment(Qt.AlignCenter)
        contribute_section.addWidget(contribute_title)
        
        contribute_content = BodyLabel(
            '我们欢迎各种形式的贡献：\n\n'
            '💻 代码贡献：提交Bug修复、新功能开发\n'
            '📝 文档改进：完善使用说明、开发文档\n'
            '🐛 问题反馈：报告使用中发现的Bug\n'
            '💡 功能建议：提出新的功能需求\n'
            '🌍 国际化：帮助翻译到其他语言\n\n'
            '让我们一起让SecRandom变得更好！'
        )
        contribute_content.setFont(QFont(load_custom_font(), 12))
        contribute_content.setWordWrap(True)
        contribute_content.setAlignment(Qt.AlignLeft)
        contribute_section.addWidget(contribute_content)
        
        open_source_layout.addLayout(contribute_section)
        open_source_layout.addStretch()
        
        # 6. 官方链接页面
        self.linksInterface = QWidget()
        self.linksInterface.setObjectName("linksInterface")
        
        # 创建滚动区域
        official_link_scroll_area = SingleDirectionScrollArea(self.linksInterface)
        official_link_scroll_area.setWidgetResizable(True)
        # 设置样式表
        official_link_scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollArea QWidget {
                border: none;
                background-color: transparent;
            }
        """)
        # 启用鼠标滚轮
        QScroller.grabGesture(official_link_scroll_area.viewport(), QScroller.LeftMouseButtonGesture)
        # 创建内部框架
        official_link_inner_frame = QWidget(official_link_scroll_area)
        links_layout = QVBoxLayout(official_link_inner_frame)
        links_layout.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignTop)
        official_link_scroll_area.setWidget(official_link_inner_frame)
        
        # 设置官方链接页面布局
        official_link_main_layout = QVBoxLayout(self.linksInterface)
        official_link_main_layout.addWidget(official_link_scroll_area)
        
        links_layout.setSpacing(10)
        links_layout.setContentsMargins(20, 20, 20, 20)
        
        # 标题
        links_title = SubtitleLabel('🌐 联系我们')
        links_title.setFont(QFont(load_custom_font(), 18, QFont.Bold))
        links_title.setAlignment(Qt.AlignCenter)
        links_layout.addWidget(links_title)
        
        # 副标题
        links_subtitle = BodyLabel('获取帮助、参与社区')
        links_subtitle.setFont(QFont(load_custom_font(), 16))
        links_subtitle.setAlignment(Qt.AlignCenter)
        links_subtitle.setStyleSheet('color: #666666; margin-bottom: 3px;')
        links_layout.addWidget(links_subtitle)
        
        # 快速链接区域 - 使用网格布局
        quick_links_widget = QWidget()
        quick_links_layout = QGridLayout(quick_links_widget)
        quick_links_layout.setSpacing(6)
        
        # 定义快速链接
        quick_links = [
            ('📖 文档', 'https://secrandom.netlify.app/', '#3498db'),
            ('💻 GitHub', 'https://github.com/SECTL/SecRandom', '#333333'),
            ('🎬 视频', 'https://www.bilibili.com/video/BV1kt81zdEoR/', '#e74c3c'),
            ('💬 QQ群', 'https://qm.qq.com/q/aySxtzOSvS', '#27ae60'),
            ('📥 下载', 'https://github.com/SECTL/SecRandom/releases', '#f39c12'),
            ('🔧 FAQ', 'https://secrandom.netlify.app/faq', '#9b59b6')
        ]
        
        # 创建按钮网格 (2行3列)
        for i, (text, url, color) in enumerate(quick_links):
            row = i // 3
            col = i % 3
            
            button = PushButton(text)
            button.setFont(QFont(load_custom_font(), 12))
            button.setStyleSheet(f'QPushButton {{ background: {color}; color: white; border: none; border-radius: 3px; padding: 4px 6px; min-height: 25px; }} QPushButton:hover {{ background: {color}99; }}')
            button.clicked.connect(lambda checked, u=url: webbrowser.open(u))
            quick_links_layout.addWidget(button, row, col)
        
        links_layout.addWidget(quick_links_widget)
        
        # 详细信息区域 - 使用紧凑的标签页
        details_widget = QWidget()
        details_widget.setStyleSheet('background: #f8f9fa; border-radius: 4px; padding: 8px;')
        details_layout = QVBoxLayout(details_widget)
        details_layout.setSpacing(4)
        
        # 反馈信息
        feedback_text = BodyLabel('📝 反馈：GitHub Issue 或 QQ群')
        feedback_text.setFont(QFont(load_custom_font(), 12))
        feedback_text.setStyleSheet('color: #333333;')
        details_layout.addWidget(feedback_text)
        
        # 联系信息
        contact_text = BodyLabel('📧 邮箱：lzy.12@foxmail.com')
        contact_text.setFont(QFont(load_custom_font(), 12))
        contact_text.setStyleSheet('color: #333333;')
        details_layout.addWidget(contact_text)
        
        # 工作时间
        work_time = BodyLabel('🕒 工作时间：周六至周日 12:00-24:00')
        work_time.setFont(QFont(load_custom_font(), 12))
        work_time.setStyleSheet('color: #333333;')
        details_layout.addWidget(work_time)
        
        links_layout.addWidget(details_widget)
        
        # 感谢语
        thanks_text = BodyLabel('❤️ 感谢使用！')
        thanks_text.setFont(QFont(load_custom_font(), 14, QFont.Bold))
        thanks_text.setAlignment(Qt.AlignCenter)
        thanks_text.setStyleSheet('color: #e74c3c; margin-top: 5px;')
        links_layout.addWidget(thanks_text)
        
        links_layout.addStretch()
    
    def initNavigation(self):
        """(^・ω・^ ) 白露的导航系统初始化魔法！
        创建顶部导航栏和底部按钮区域～ ✨"""
        
        # 添加引导页面到导航并获取导航项
        welcome_item = self.addSubInterface(self.welcomeInterface, '🎉', '欢迎', position=NavigationItemPosition.TOP)
        setup_people_item = self.addSubInterface(self.setupPeopleInterface, '🎯', '抽人设置', position=NavigationItemPosition.TOP)
        setup_reward_item = self.addSubInterface(self.setupRewardInterface, '🎁', '抽奖设置', position=NavigationItemPosition.TOP)
        tips_item = self.addSubInterface(self.tipsInterface, '💡', '使用技巧', position=NavigationItemPosition.TOP)
        open_source_item = self.addSubInterface(self.openSourceInterface, '🌈', '开源声明', position=NavigationItemPosition.TOP)
        links_item = self.addSubInterface(self.linksInterface, '🔗', '官方链接', position=NavigationItemPosition.TOP)
        
        # 创建底部导航按钮区域
        self.nav_button_container = QWidget()
        self.nav_button_container.setObjectName("navButtonContainer")
        self.nav_button_container.setFixedHeight(60)
        nav_button_layout = QHBoxLayout(self.nav_button_container)
        nav_button_layout.setContentsMargins(90, 10, 20, 10)
        
        # 上一个按钮
        self.prev_button = PushButton('← 上一个')
        self.prev_button.setFont(QFont(load_custom_font(), 12))
        self.prev_button.clicked.connect(self.show_previous_page)
        self.prev_button.setEnabled(False)  # 第一页时禁用
        
        # 页面指示器
        self.page_label = BodyLabel('1 / 6')
        self.page_label.setFont(QFont(load_custom_font(), 12))
        self.page_label.setAlignment(Qt.AlignCenter)
        
        # 下一个按钮
        self.next_button = PushButton('下一个 →')
        self.next_button.setFont(QFont(load_custom_font(), 12))
        self.next_button.clicked.connect(self.show_next_page)
        
        # 开始使用按钮（最后一页显示）
        self.start_button = PrimaryPushButton('🚀 开始使用')
        self.start_button.setFont(QFont(load_custom_font(), 12))
        self.start_button.clicked.connect(self.start_using)
        self.start_button.hide()  # 初始隐藏
        
        nav_button_layout.addWidget(self.prev_button)
        nav_button_layout.addStretch()
        nav_button_layout.addWidget(self.page_label)
        nav_button_layout.addStretch()
        nav_button_layout.addWidget(self.next_button)
        nav_button_layout.addWidget(self.start_button)
        
        # 按钮容器将在add_bottom_buttons方法中添加到窗口主布局
        
        # 连接导航切换信号
        welcome_item.clicked.connect(lambda: self.on_navigation_changed(self.welcomeInterface))
        setup_people_item.clicked.connect(lambda: self.on_navigation_changed(self.setupPeopleInterface))
        setup_reward_item.clicked.connect(lambda: self.on_navigation_changed(self.setupRewardInterface))
        tips_item.clicked.connect(lambda: self.on_navigation_changed(self.tipsInterface))
        open_source_item.clicked.connect(lambda: self.on_navigation_changed(self.openSourceInterface))
        links_item.clicked.connect(lambda: self.on_navigation_changed(self.linksInterface))

        
    def on_navigation_changed(self, interface):
        """(^・ω・^ ) 白露的导航切换魔法！
        当用户点击导航项时更新页面状态～ ✨"""
        
        # 更新当前页面索引
        if interface == self.welcomeInterface:
            self.current_page_index = 0
        elif interface == self.setupPeopleInterface:
            self.current_page_index = 1
        elif interface == self.setupRewardInterface:
            self.current_page_index = 2
        elif interface == self.tipsInterface:
            self.current_page_index = 3
        elif interface == self.openSourceInterface:
            self.current_page_index = 4
        elif interface == self.linksInterface:
            self.current_page_index = 5
        
        self.update_navigation_buttons()
    
    def show_previous_page(self):
        """(^・ω・^ ) 白露的上一页魔法！
        切换到上一个引导页面～ ✨"""
        if self.current_page_index > 0:
            self.current_page_index -= 1
            self.switch_to_current_page()
            self.update_navigation_buttons()
    
    def show_next_page(self):
        """(^・ω・^ ) 白露的下一页魔法！
        切换到下一个引导页面～ ✨"""
        if self.current_page_index < self.total_pages - 1:
            self.current_page_index += 1
            self.switch_to_current_page()
            self.update_navigation_buttons()
    
    def switch_to_current_page(self):
        """(^・ω・^ ) 白露的页面切换魔法！
        根据当前索引切换到对应的引导页面～ ✨"""
        if self.current_page_index == 0:
            self.switchTo(self.welcomeInterface)
        elif self.current_page_index == 1:
            self.switchTo(self.setupPeopleInterface)
        elif self.current_page_index == 2:
            self.switchTo(self.setupRewardInterface)
        elif self.current_page_index == 3:
            self.switchTo(self.tipsInterface)
        elif self.current_page_index == 4:
            self.switchTo(self.openSourceInterface)
        elif self.current_page_index == 5:
            self.switchTo(self.linksInterface)
    
    def update_navigation_buttons(self):
        """(^・ω・^ ) 白露的按钮状态更新魔法！
        根据当前页面更新按钮状态和显示～ ✨"""
        
        # 更新页面指示器
        self.page_label.setText(f'{self.current_page_index + 1} / {self.total_pages}')
        
        # 更新上一个按钮状态
        self.prev_button.setEnabled(self.current_page_index > 0)
        
        # 更新下一个按钮状态
        if self.current_page_index < self.total_pages - 1:
            self.next_button.show()
            self.start_button.hide()
        else:
            self.next_button.hide()
            self.start_button.show()
    
    def start_using(self):
        """(^・ω・^ ) 白露的开始使用魔法！
        用户点击开始使用后，关闭引导窗口并显示主界面～ ✨"""
        logger.info("白露引导: 用户点击开始使用，准备显示主界面～ ")
        
        # 获取引导完成标志文件路径
        guide_complete_file = path_manager.get_guide_complete_path()
        
        # 确保设置目录存在
        ensure_dir(os.path.dirname(guide_complete_file))
        
        # 创建引导完成标志文件
        guide_complete_data = {
            'guide_completed': True,
            'completion_time': self.get_current_time_string(),
            'version': VERSION
        }
        
        try:
            with open_file(guide_complete_file, 'w', encoding='utf-8') as f:
                json.dump(guide_complete_data, f, ensure_ascii=False, indent=4)
            logger.info("白露魔法: 创建了引导完成标志文件哦～ ✧*｡٩(ˊᗜˋ*)و✧*｡")
        except Exception as e:
            logger.error(f"白露错误: 创建引导完成标志文件失败: {e}")
        
        self.close()
        
        # 发射信号通知主程序显示主界面
        self.start_signal.emit()
    
    def get_current_time_string(self):
        """(^・ω・^ ) 白露的时间获取魔法！
        获取当前时间的字符串表示～ ✨"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def add_bottom_buttons(self):
        """(^・ω・^ ) 白露的底部按钮添加魔法！
        将按钮容器添加到窗口底部～ ✨"""
        # 设置按钮容器的父对象为窗口
        self.nav_button_container.setParent(self)
        
        # 将按钮容器移动到窗口底部
        self.nav_button_container.move(0, self.height() - 60)
        
        # 设置按钮容器宽度与窗口相同
        self.nav_button_container.setFixedWidth(self.width())
        
        # 显示按钮容器
        self.nav_button_container.show()
        
        # 连接窗口大小改变事件，以调整按钮容器位置
        self.resizeEvent = self.on_window_resized
    
    def on_window_resized(self, event):
        """(^・ω・^ ) 白露的窗口大小调整魔法！
        当窗口大小改变时调整按钮容器的位置和大小～ ✨"""
        # 调用父类的resizeEvent
        super().resizeEvent(event)
        
        # 调整按钮容器的位置和大小
        if hasattr(self, 'nav_button_container'):
            self.nav_button_container.move(0, self.height() - 60)
            self.nav_button_container.setFixedWidth(self.width())
    
    def closeEvent(self, event):
        """(^・ω・^ ) 白露的窗口关闭魔法！
        确保引导窗口关闭时正确清理资源～ ✨"""
        logger.debug("白露引导: 引导窗口已关闭～ ")
        self.start_using()
        self.start_signal.emit()
        super().closeEvent(event)