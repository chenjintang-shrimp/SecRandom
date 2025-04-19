from qfluentwidgets import *
from qfluentwidgets import FluentIcon as FIF

from app.common.config import YEAR, MONTH, AUTHOR, VERSION, APPLY_NAME, GITHUB_WEB, BILIBILI_WEB

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
        self.about_author_label = BodyLabel(f"Copyright © {YEAR} {APPLY_NAME}-{MONTH}-{AUTHOR}")

        # 添加组件到分组中
        self.addGroup(FIF.LINK, "哔哩哔哩", "黎泽懿 - bilibili", self.about_bilibili_Button)
        self.addGroup(FIF.GITHUB, "Github", "SecRandom(黎泽懿-lzy98276) - github", self.about_github_Button)
        self.addGroup(FIF.INFO, "版本", "显示的是当前软件版本号", self.about_version_label)