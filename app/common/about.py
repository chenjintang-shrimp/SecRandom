from venv import logger
from qfluentwidgets import *
from qfluentwidgets import FluentIcon as FIF
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

from app.common.config import YEAR, MONTH, AUTHOR, VERSION, APPLY_NAME, GITHUB_WEB, BILIBILI_WEB
from app.common.update_notification import show_update_notification
from app.common.config import get_theme_icon, load_custom_font, check_for_updates, get_update_channel, set_update_channel

class aboutCard(GroupHeaderCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("关于 SecRandom")
        self.setBorderRadius(8)

        # 打开GitHub按钮
        self.about_github_Button = HyperlinkButton(FIF.GITHUB, GITHUB_WEB, 'Github')
        self.about_github_Button.setFont(QFont(load_custom_font(), 12))

        # 打开bilibili按钮
        self.about_bilibili_Button = HyperlinkButton(BILIBILI_WEB, 'Bilibili')
        self.about_bilibili_Button.setFont(QFont(load_custom_font(), 12))

        # 查看当前软件版本号
        self.about_version_label = BodyLabel(f"当前版本: {VERSION}")
        self.about_version_label.setFont(QFont(load_custom_font(), 12))

        # 查看当前软件版权所属
        self.about_author_label = BodyLabel(f"Copyright © {YEAR} {APPLY_NAME}")
        self.about_author_label.setFont(QFont(load_custom_font(), 12))

        # 创建贡献人员按钮
        self.contributor_button = PushButton('贡献人员')
        self.contributor_button.setIcon(get_theme_icon("ic_fluent_document_person_20_filled"))
        self.contributor_button.clicked.connect(self.show_contributors)
        self.contributor_button.setFont(QFont(load_custom_font(), 12))

        # 检查更新按钮
        self.check_update_button = PushButton('检查更新')
        self.check_update_button.setIcon(get_theme_icon("ic_fluent_arrow_sync_20_filled"))
        self.check_update_button.clicked.connect(self.check_updates_async)
        self.check_update_button.setFont(QFont(load_custom_font(), 12))

        # 添加更新通道选择
        self.channel_combo = ComboBox()
        self.channel_combo.addItems(["稳定通道", "测试通道"])
        self.channel_combo.setCurrentIndex(0)
        self.channel_combo.currentIndexChanged.connect(self.on_channel_changed)
        self.channel_combo.setFont(QFont(load_custom_font(), 12))
            
        self.addGroup(get_theme_icon("ic_fluent_branch_fork_link_20_filled"), "哔哩哔哩", "黎泽懿 - bilibili", self.about_bilibili_Button)
        self.addGroup(FIF.GITHUB, "Github", "SecRandom - github", self.about_github_Button)
        self.addGroup(get_theme_icon("ic_fluent_document_person_20_filled"), "贡献人员", "点击查看详细贡献者信息", self.contributor_button)
        self.addGroup(get_theme_icon("ic_fluent_class_20_filled"), "版权", "SecRandom 遵循 GPL-3.0 协议", self.about_author_label)
        self.addGroup(get_theme_icon("ic_fluent_info_20_filled"), "版本", "软件版本号", self.about_version_label)
        self.addGroup(get_theme_icon("ic_fluent_arrow_sync_20_filled"), "更新通道", "选择更新通道", self.channel_combo)
        self.addGroup(get_theme_icon("ic_fluent_arrow_sync_20_filled"), "检查更新", "检查是否为最新版本(应用启动时会自动检查更新)", self.check_update_button)

        self.on_channel_changed(self.channel_combo.currentIndex())
        self.read_channel_setting()

    class UpdateCheckWorker(QThread):
        result_ready = pyqtSignal(bool, str)
        
        def run(self):
            update_available, latest_version = check_for_updates()
            self.result_ready.emit(update_available, latest_version)
        
    def check_updates_async(self):
        self.update_worker = self.UpdateCheckWorker()
        self.update_worker.result_ready.connect(self.on_update_check_finished)
        self.update_worker.start()

    def on_update_check_finished(self, update_available, latest_version):
        if update_available and latest_version:
            show_update_notification(latest_version)
        else:
            w = Dialog("检查更新", "当前版本已是最新版本", self)
            w.yesButton.setText("知道啦👌")
            w.cancelButton.hide()
            w.buttonLayout.insertStretch(1)
            if w.exec():
                logger.info("用户点击了知道啦👌")
        self.update_worker.deleteLater()

    def on_channel_changed(self, index):
        channel = 'stable' if index == 0 else 'beta'
        set_update_channel(channel)

    def read_channel_setting(self):
        channel = get_update_channel()
        if channel == 'stable':
            self.channel_combo.setCurrentIndex(0)
        else:
            self.channel_combo.setCurrentIndex(1)

    def show_contributors(self):
        """ 显示贡献人员 """
        w = ContributorDialog(self)
        if w.exec():
            pass


class ContributorDialog(QDialog):
    """ 贡献者信息对话框 """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('贡献人员')
        self.setMinimumSize(600, 200)
        self.update_theme_style() 
        
        # 主布局
        self.layout = QVBoxLayout(self)
        
        # 贡献者数据
        contributors = [
            {
                'name': '黎泽懿_Aionflux (lzy98276)',
                'role': '设计, 创意&策划, 维护, 文档, 测试',
                'github': 'https://github.com/lzy98276',
                'avatar': 'app\\resource\\icon\\contributor1.png'
            },
            {
                'name': '弃稞之草 (QiKeZhiCao)',
                'role': '创意, 维护',
                'github': 'https://github.com/QiKeZhiCao',
                'avatar': 'app\\resource\\icon\\contributor2.png'
            },
            {
                'name': 'system-linux-cmb',
                'role': '应用测试',
                'github': 'https://github.com/system-linux-cmb',
                'avatar': 'app\\resource\\icon\\contributor3.png'
            },
            {
                'name': 'yuanbenxin',
                'role': '响应式前端页面设计及维护, 文档',
                'github': 'https://github.com/yuanbenxin',
                'avatar': 'app\\resource\\icon\\contributor4.png'
            },
        ]
        
        # 添加贡献者卡片
        for contributor in contributors:
            self.addContributorCard(contributor)

    def update_theme_style(self):
        """根据当前主题更新样式"""
        if qconfig.theme == Theme.AUTO:
            # 获取系统当前主题
            lightness = QApplication.palette().color(QPalette.Window).lightness()
            is_dark = lightness <= 127
        else:
            is_dark = qconfig.theme == Theme.DARK
        if is_dark:
            self.setStyleSheet("""
                QDialog {
                    background-color: #202020;
                    color: #ffffff;
                }
                QLineEdit {
                    background-color: #3c3c3c;
                    color: #ffffff;
                    border: 1px solid #555555;
                    border-radius: 4px;
                    padding: 5px;
                }
                QPushButton {
                    background-color: #505050;
                    color: #ffffff;
                    border: 1px solid #555555;
                    border-radius: 4px;
                    padding: 5px;
                }
                QPushButton:hover {
                    background-color: #606060;
                }
                QComboBox {
                    background-color: #3c3c3c;
                    color: #ffffff;
                    border: 1px solid #555555;
                    border-radius: 4px;
                    padding: 5px;
                }
            """)
        else:
            self.setStyleSheet("""
                QDialog {
                    background-color: #ffffff;
                    color: #000000;
                }
                QLineEdit {
                    background-color: #ffffff;
                    color: #000000;
                    border: 1px solid #cccccc;
                    border-radius: 4px;
                    padding: 5px;
                }
                QPushButton {
                    background-color: #f0f0f0;
                    color: #000000;
                    border: 1px solid #cccccc;
                    border-radius: 4px;
                    padding: 5px;
                }
                QPushButton:hover {
                    background-color: #e0e0e0;
                }
                QComboBox {
                    background-color: #ffffff;
                    color: #000000;
                    border: 1px solid #cccccc;
                    border-radius: 4px;
                    padding: 5px;
                }
            """)
    
    def update_card_theme_style(self, card):
        """根据当前主题更新样式"""
        if qconfig.theme == Theme.AUTO:
            # 获取系统当前主题
            lightness = QApplication.palette().color(QPalette.Window).lightness()
            is_dark = lightness <= 127
        else:
            is_dark = qconfig.theme == Theme.DARK
        if is_dark:
            card.setStyleSheet('''
                QWidget#contributorCard {
                    background: 2b2b2b;
                    border-radius: 8px;
                    padding: 10px;
                    margin-bottom: 10px;
                }
            ''')
        else:
            card.setStyleSheet('''
                QWidget#contributorCard {
                    background: white;
                    border-radius: 8px;
                    padding: 10px;
                    margin-bottom: 10px;
                }
            ''')
    
    def addContributorCard(self, contributor):
        """ 添加贡献者卡片 """
        card = QWidget()
        card.setObjectName('contributorCard')
        self.update_card_theme_style(card)
        cardLayout = QHBoxLayout(card)

        # 头像
        avatar = AvatarWidget(contributor['avatar'])
        avatar.setRadius(48)
        avatar.setAlignment(Qt.AlignLeft)
        cardLayout.addWidget(avatar, 0, Qt.AlignCenter)

        # 昵称
        name = TitleLabel(contributor['name'])
        name.setAlignment(Qt.AlignLeft)
        name.setFont(QFont(load_custom_font(), 14))
        # 创建垂直布局存放文本信息
        textLayout = QVBoxLayout()
        textLayout.setContentsMargins(5, 8, 0, 8)

        # 添加姓名
        textLayout.addWidget(name)

        # 职责
        role = BodyLabel(contributor['role'])
        role.setAlignment(Qt.AlignLeft)
        role.setFont(QFont(load_custom_font(), 12))
        textLayout.addWidget(role)

        # GitHub链接
        github_link = HyperlinkButton(contributor['github'], 'GitHub', self)
        github_link.setMinimumWidth(40)
        github_link.setIconSize(QSize(16, 16))
        github_link.setFixedWidth(70)
        textLayout.addWidget(github_link)
        
        textLayout.setAlignment(Qt.AlignLeft | Qt.AlignVCenter) 

        cardLayout.addLayout(textLayout, 0)

        self.layout.addWidget(card)
        
        # 添加滚动区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        # 假设需要创建一个合适的布局实例
        layout_instance = QVBoxLayout()
        content.setLayout(layout_instance)
        scroll.setWidget(content)
        self.layout.addWidget(scroll)