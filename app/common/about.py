from qfluentwidgets import *
from qfluentwidgets import FluentIcon as FIF
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

from app.common.config import YEAR, MONTH, AUTHOR, VERSION, APPLY_NAME, GITHUB_WEB, BILIBILI_WEB
from app.common.config import load_custom_font

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
        self.contributor_button.setIcon(QIcon("app/resource/assets/ic_fluent_document_person_20_filled.svg"))
        self.contributor_button.clicked.connect(self.show_contributors)
            
        self.addGroup(QIcon("app/resource/assets/ic_fluent_branch_fork_link_20_filled.svg"), "哔哩哔哩", "黎泽懿 - bilibili", self.about_bilibili_Button)
        self.addGroup(FIF.GITHUB, "Github", "SecRandom - github", self.about_github_Button)
        self.addGroup(QIcon("app/resource/assets/ic_fluent_document_person_20_filled.svg"), "贡献人员", "点击查看详细贡献者信息", self.contributor_button)
        self.addGroup(QIcon("app/resource/assets/ic_fluent_class_20_filled.svg"), "版权", "SecRandom 遵循 GPL-3.0 协议", self.about_author_label)
        self.addGroup(QIcon("app/resource/assets/ic_fluent_info_20_filled.svg"), "版本", "显示的是当前软件版本号", self.about_version_label)
        
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
        self.setMinimumSize(600, 400)
        self.setStyleSheet('''
            QDialog {
                background: #f5f5f5;
            }
        ''')    
        
        # 主布局
        self.layout = QVBoxLayout(self)
        
        # 贡献者数据
        contributors = [
            {
                'name': '黎泽懿 (lzy98276)',
                'role': '负责: 设计, 创意&策划, 维护, 文档',
                'github': 'https://github.com/lzy98276',
                'avatar': 'app\\resource\\icon\\contributor1.png'
            }
        ]
        
        # 添加贡献者卡片
        for contributor in contributors:
            self.addContributorCard(contributor)
    
    def addContributorCard(self, contributor):
        """ 添加贡献者卡片 """
        card = QWidget()
        card.setObjectName('contributorCard')
        card.setStyleSheet('''
            QWidget#contributorCard {
                background: white;
                border-radius: 8px;
                padding: 15px;
                margin-bottom: 15px;
            }
        ''')
        cardLayout = QVBoxLayout(card)
        cardLayout.setSpacing(10)

        # 头像
        avatar = QLabel()
        avatar.setPixmap(QPixmap(contributor['avatar']).scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        avatar.setAlignment(Qt.AlignCenter)
        cardLayout.addWidget(avatar)

        # 昵称
        name = TitleLabel(contributor['name'])
        name.setAlignment(Qt.AlignCenter)
        name.setFont(QFont(load_custom_font(), 14))
        cardLayout.addWidget(name)

        # 职责
        role = BodyLabel(contributor['role'])
        role.setAlignment(Qt.AlignCenter)
        role.setFont(QFont(load_custom_font(), 12))
        cardLayout.addWidget(role)

        # GitHub链接
        github = HyperlinkButton(
            url=contributor['github'],
            text=f'GitHub',
            parent=self
        )
        github.setIconSize(QSize(16, 16))
        github.setFixedWidth(120)
        cardLayout.addWidget(github, 0, Qt.AlignCenter)

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