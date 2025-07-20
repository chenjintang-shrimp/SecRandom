from qfluentwidgets import *
from qfluentwidgets import FluentIcon as FIF
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

from app.common.config import YEAR, MONTH, AUTHOR, VERSION, APPLY_NAME, GITHUB_WEB, BILIBILI_WEB
from app.common.config import get_theme_icon, load_custom_font

class aboutCard(GroupHeaderCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("关于 SecRandom")
        self.setBorderRadius(8)

        # 打开GitHub按钮
        self.about_github_Button = HyperlinkButton(FIF.GITHUB, GITHUB_WEB, 'Github')

        # 打开bilibili按钮
        self.about_bilibili_Button = HyperlinkButton(BILIBILI_WEB, 'Bilibili')

        # 查看当前软件版本号
        self.about_version_label = BodyLabel(f"当前版本: {VERSION}")

        # 查看当前软件版权所属
        self.about_author_label = BodyLabel(f"Copyright © {YEAR} {APPLY_NAME}")

        # 创建贡献人员按钮
        self.contributor_button = PushButton('贡献人员')
        self.contributor_button.setIcon(get_theme_icon("ic_fluent_document_person_20_filled"))
        self.contributor_button.clicked.connect(self.show_contributors)
            
        self.addGroup(get_theme_icon("ic_fluent_branch_fork_link_20_filled"), "哔哩哔哩", "黎泽懿 - bilibili", self.about_bilibili_Button)
        self.addGroup(FIF.GITHUB, "Github", "SecRandom - github", self.about_github_Button)
        self.addGroup(get_theme_icon("ic_fluent_document_person_20_filled"), "贡献人员", "点击查看详细贡献者信息", self.contributor_button)
        self.addGroup(get_theme_icon("ic_fluent_class_20_filled"), "版权", "SecRandom 遵循 GPL-3.0 协议", self.about_author_label)
        self.addGroup(get_theme_icon("ic_fluent_info_20_filled"), "版本", "显示的是当前软件版本号", self.about_version_label)
        
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
        self.setMinimumSize(600, 150)
        self.update_theme_style() 
        
        # 主布局
        self.layout = QVBoxLayout(self)
        
        # 贡献者数据
        contributors = [
            {
                'name': '黎泽懿_Aionflux (lzy98276)',
                'role': '设计, 创意&策划, 维护, 文档',
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
                'role': '测试',
                'github': 'https://github.com/system-linux-cmb',
                'avatar': 'app\\resource\\icon\\contributor3.png'
            }
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
        avatar = QLabel()
        avatar.setPixmap(QPixmap(contributor['avatar']).scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation))
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