# ==================================================
# 导入库
# ==================================================
import json
import os
import sys
import subprocess

from loguru import logger
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtNetwork import *
from qfluentwidgets import *
from qfluentwidgets import FluentIcon as FIF

from app.tools.variable import *
from app.tools.path_utils import *
from app.tools.personalised import *
from app.tools.settings_default import *
from app.tools.settings_access import *

from app.common.another_window import ContributorDialog

# ==================================================
# 关于卡片类
# ==================================================
class about(GroupHeaderCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(get_setting_name("about", "title"))
        self.setBorderRadius(8)

        # 打开GitHub按钮
        self.about_github_Button = HyperlinkButton(FIF.GITHUB, GITHUB_WEB, get_setting_name("about", "github"))
        self.about_github_Button.setFont(QFont(load_custom_font(), 12))

        # 打开bilibili按钮
        self.about_bilibili_Button = HyperlinkButton(BILIBILI_WEB, get_setting_name("about", "bilibili"))
        self.about_bilibili_Button.setFont(QFont(load_custom_font(), 12))

        # 查看当前软件版本号
        version_text = f"Dev Version-{NEXT_VERSION}" if VERSION == "v0.0.0.0" else VERSION
        self.about_version_label = BodyLabel(version_text)
        self.about_version_label.setFont(QFont(load_custom_font(), 12))

        # 查看当前软件版权所属
        self.about_author_label = BodyLabel(f"Copyright © {YEAR} {APPLY_NAME}")
        self.about_author_label.setFont(QFont(load_custom_font(), 12))

        # 创建贡献人员按钮
        self.contributor_button = PushButton(get_setting_name("about", "contributor"))
        self.contributor_button.setIcon(get_theme_icon("ic_fluent_document_person_20_filled"))
        self.contributor_button.clicked.connect(self.show_contributors)
        self.contributor_button.setFont(QFont(load_custom_font(), 12))

        # 创建捐赠支持按钮
        self.donation_button = PushButton(get_setting_name("about", "donation"))
        self.donation_button.setIcon(get_theme_icon("ic_fluent_document_person_20_filled"))
        self.donation_button.clicked.connect(self.open_donation_url)
        self.donation_button.setFont(QFont(load_custom_font(), 12))

        # 检查更新按钮
        self.check_update_button = PushButton(get_setting_name("about", "check_update"))
        self.check_update_button.setIcon(get_theme_icon("ic_fluent_arrow_sync_20_filled"))
        self.check_update_button.clicked.connect(self.check_updates)
        self.check_update_button.setFont(QFont(load_custom_font(), 12))

        # 官网链接按钮
        self.about_website_Button = HyperlinkButton(FIF.GLOBE, "https://secrandom.netlify.app/", get_setting_name("about", "website"))
        self.about_website_Button.setFont(QFont(load_custom_font(), 12))

        # 添加更新通道选择
        self.channel_combo = ComboBox()
        self.channel_combo.addItems(get_setting_combo_name("about", "channel"))
        self.channel_combo.setCurrentIndex(readme_settings("about", "channel"))
        self.channel_combo.currentIndexChanged.connect(lambda: update_settings("about", "channel", self.channel_combo.currentIndex()))
        self.channel_combo.setFont(QFont(load_custom_font(), 12))
            
        self.addGroup(get_theme_icon("ic_fluent_branch_fork_link_20_filled"), get_setting_name("about", "bilibili"), get_setting_description("about", "bilibili"), self.about_bilibili_Button)
        self.addGroup(FIF.GITHUB, get_setting_name("about", "github"), get_setting_description("about", "github"), self.about_github_Button)
        self.addGroup(get_theme_icon("ic_fluent_document_person_20_filled"), get_setting_name("about", "contributor"), get_setting_description("about", "contributor"), self.contributor_button)
        self.addGroup(get_theme_icon("ic_fluent_document_person_20_filled"), get_setting_name("about", "donation"), get_setting_description("about", "donation"), self.donation_button)
        self.addGroup(get_theme_icon("ic_fluent_class_20_filled"), get_setting_name("about", "copyright"), get_setting_description("about", "copyright"), self.about_author_label)
        self.addGroup(FIF.GLOBE, get_setting_name("about", "website"), get_setting_description("about", "website"), self.about_website_Button)
        self.addGroup(get_theme_icon("ic_fluent_info_20_filled"), get_setting_name("about", "version"), get_setting_description("about", "version"), self.about_version_label)
        self.addGroup(get_theme_icon("ic_fluent_arrow_sync_20_filled"), get_setting_name("about", "channel"), get_setting_description("about", "channel"), self.channel_combo)
        self.addGroup(get_theme_icon("ic_fluent_arrow_sync_20_filled"), get_setting_name("about", "check_update"), get_setting_description("about", "check_update"), self.check_update_button)

    def show_contributors(self):
        """ 显示贡献人员 """
        w = ContributorDialog(self)
        if w.exec():
            pass

    def open_donation_url(self):
        """ 打开捐赠链接 """
        QDesktopServices.openUrl(QUrl(DONATION_URL))

    def check_updates(self):
        """ 检查更新 """
        logger.debug("检查更新")