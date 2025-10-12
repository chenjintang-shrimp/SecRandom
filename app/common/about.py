from venv import logger
import os
import hashlib
import requests
from qfluentwidgets import *
from qfluentwidgets import FluentIcon as FIF
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import os
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

from app.common.config import YEAR, MONTH, AUTHOR, VERSION, APPLY_NAME, GITHUB_WEB, BILIBILI_WEB
from app.common.update_notification import show_update_notification
from app.common.config import get_theme_icon, load_custom_font, check_for_updates, get_update_channel, set_update_channel
from app.common.path_utils import path_manager, open_file, remove_file

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

        # 创建捐赠支持按钮
        self.donation_button = PushButton('捐赠支持')
        self.donation_button.setIcon(get_theme_icon("ic_fluent_document_person_20_filled"))
        self.donation_button.clicked.connect(self.show_donation)
        self.donation_button.setFont(QFont(load_custom_font(), 12))

        # 检查更新按钮
        self.check_update_button = PushButton('检查更新')
        self.check_update_button.setIcon(get_theme_icon("ic_fluent_arrow_sync_20_filled"))
        self.check_update_button.clicked.connect(self.check_updates_async)
        self.check_update_button.setFont(QFont(load_custom_font(), 12))

        # 官网链接按钮
        self.about_website_Button = HyperlinkButton(FIF.GLOBE, "https://secrandom.netlify.app/", 'SecRandom 官网')
        self.about_website_Button.setFont(QFont(load_custom_font(), 12))

        # 添加更新通道选择
        self.channel_combo = ComboBox()
        self.channel_combo.addItems(["稳定通道", "测试通道"])
        self.channel_combo.setCurrentIndex(0)
        self.channel_combo.currentIndexChanged.connect(self.on_channel_changed)
        self.channel_combo.setFont(QFont(load_custom_font(), 12))
            
        self.addGroup(get_theme_icon("ic_fluent_branch_fork_link_20_filled"), "哔哩哔哩", "黎泽懿 - bilibili", self.about_bilibili_Button)
        self.addGroup(FIF.GITHUB, "Github", "SecRandom - github", self.about_github_Button)
        self.addGroup(get_theme_icon("ic_fluent_document_person_20_filled"), "贡献人员", "点击查看详细贡献者信息", self.contributor_button)
        self.addGroup(get_theme_icon("ic_fluent_document_person_20_filled"), "捐赠支持", "支持项目发展，感谢您的捐赠", self.donation_button)
        self.addGroup(get_theme_icon("ic_fluent_class_20_filled"), "版权", "SecRandom 遵循 GPL-3.0 协议", self.about_author_label)
        self.addGroup(FIF.GLOBE, "官网", "访问 SecRandom 官方网站", self.about_website_Button)
        self.addGroup(get_theme_icon("ic_fluent_info_20_filled"), "版本", "软件版本号", self.about_version_label)
        self.addGroup(get_theme_icon("ic_fluent_arrow_sync_20_filled"), "更新通道", "选择更新通道", self.channel_combo)
        self.addGroup(get_theme_icon("ic_fluent_arrow_sync_20_filled"), "检查更新", "检查是否为最新版本(应用启动时会自动检查更新)", self.check_update_button)

        # self.on_channel_changed(self.channel_combo.currentIndex())
        self.read_channel_setting()

    class UpdateCheckWorker(QThread):
        result_ready = pyqtSignal(bool, str)
        
        def run(self):
            update_available, latest_version = check_for_updates()
            self.result_ready.emit(update_available, latest_version)
        
    def check_updates_async(self):
        # 清理可能存在的旧worker，避免内存泄漏
        if hasattr(self, 'update_worker') and self.update_worker is not None:
            try:
                if self.update_worker.isRunning():
                    self.update_worker.quit()
                    self.update_worker.wait(1000)  # 等待1秒让线程正常结束
                self.update_worker.deleteLater()
            except Exception as e:
                logger.error(f"清理旧update_worker时出现错误: {e}")
        
        # 创建新的worker
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
        # 安全地删除worker对象，避免重复删除导致的错误
        if hasattr(self, 'update_worker') and self.update_worker is not None:
            try:
                self.update_worker.deleteLater()
                self.update_worker = None
            except RuntimeError as e:
                logger.error(f"删除update_worker时出现错误: {e}")
            except Exception as e:
                logger.error(f"删除update_worker时出现未知错误: {e}")

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

    def show_donation(self):
        """ 显示捐赠支持 """
        w = DonationDialog(self)
        if w.exec():
            pass


class ContributorDialog(QDialog):
    """ 贡献者信息对话框 """
    def __init__(self, parent=None):
        super().__init__(parent)
        # 设置无边框窗口样式并解决屏幕设置冲突
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self.setWindowTitle('贡献人员')
        self.setMinimumSize(900, 600)
        self.setSizeGripEnabled(True) #启用右下角拖动柄
        self.update_theme_style()
        
        self.saved = False
        self.dragging = False
        self.drag_position = None

        # 确保不设置子窗口的屏幕属性
        if parent is not None:
            self.setParent(parent)
        
        # 创建自定义标题栏
        self.title_bar = QWidget()
        self.title_bar.setObjectName("CustomTitleBar")
        self.title_bar.setFixedHeight(35)
        
        # 标题栏布局
        title_layout = QHBoxLayout(self.title_bar)
        title_layout.setContentsMargins(10, 0, 10, 0)
        
        # 窗口标题
        self.title_label = BodyLabel("贡献人员")
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

        # 创建滚动区域
        scroll = SingleDirectionScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        self.grid_layout = QGridLayout(content)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollArea QWidget {
                border: none;
                background-color: transparent;
            }
        """)
        scroll.setWidget(content)
        
        # 主布局
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        # 添加自定义标题栏
        self.layout.addWidget(self.title_bar)
        # 添加内容区域
        content_layout = QVBoxLayout()
        content_layout.addWidget(scroll)
        content_layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addLayout(content_layout)
        
        self.update_theme_style()
        qconfig.themeChanged.connect(self.update_theme_style)
        
        # 贡献者数据
        app_dir = path_manager._app_root
        contributors = [
            {
                'name': 'lzy98276 (黎泽懿_Aionflux)',
                'role': '设计 & 创意 & 策划 &\n维护 & 文档& 测试',
                'github': 'https://github.com/lzy98276',
                'avatar': str(path_manager.get_resource_path('icon', 'contributor1.png'))

            },
            {
                'name': 'QiKeZhiCao (弃稞之草)',
                'role': '创意 & 维护',
                'github': 'https://github.com/QiKeZhiCao',
                'avatar': str(path_manager.get_resource_path('icon', 'contributor2.png'))
            },
            {
                'name': 'Fox-block-offcial',
                'role': '应用测试 & 文档 & 安装包制作',
                'github': 'https://github.com/Fox-block-offcial',
                'avatar': str(path_manager.get_resource_path('icon', 'contributor3.png'))
            },
            {
                'name': 'yuanbenxin (本新同学)',
                'role': '响应式前端页面\n设计及维护 & 文档',
                'github': 'https://github.com/yuanbenxin',
                'avatar': str(path_manager.get_resource_path('icon', 'contributor4.png'))
            },
            {
                'name': 'zhangjianjian7 (叶背影)',
                'role': '文档',
                'github': 'https://github.com/zhangjianjian7',
                'avatar': str(path_manager.get_resource_path('icon', 'contributor5.png'))
            },
            {
                'name': 'Jursin',
                'role': '响应式前端页面\n设计及维护 & 文档',
                'github': 'https://github.com/jursin',
                'avatar': str(path_manager.get_resource_path('icon', 'contributor6.png'))
            },
        ]
        
        # 计算所有职责文本的行数，让它们变得整齐划一
        font = QFont(load_custom_font(), 12)  # 使用和职责文本相同的字体设置
        fm = QFontMetrics(font)
        max_lines = 0
        role_lines = []

        # 第一步：找出最长的职责文本有多少行
        for contributor in contributors:
            role_text = contributor['role']
            # 计算文本在500像素宽度下的行数（和UI显示保持一致）
            text_rect = fm.boundingRect(QRect(0, 0, 500, 0), Qt.TextWordWrap, role_text)
            line_count = text_rect.height() // fm.lineSpacing()
            role_lines.append(line_count)
            if line_count > max_lines:
                max_lines = line_count

        # 第二步：为每个职责文本添加换行符，确保行数相同
        for i, contributor in enumerate(contributors):
            current_lines = role_lines[i]
            if current_lines < max_lines:
                # 添加缺少的换行符
                contributor['role'] += '\n' * (max_lines - current_lines)

        self.cards = []
        # 添加贡献者卡片
        for contributor in contributors:
            card = self.addContributorCard(contributor)
            self.cards.append(card)
        
        self.update_layout()

    def update_layout(self):
        # 清空网格布局
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.hide()
        
        # 响应式布局配置
        CARD_MIN_WIDTH = 250  # 卡片最小宽度
        MAX_COLUMNS = 12       # 最大列数限制

        def calculate_columns(width):
            """根据窗口宽度和卡片尺寸动态计算列数"""
            if width <= 0:
                return 1
            # 计算最大可能列数（不超过MAX_COLUMNS）
            cols = min(width // CARD_MIN_WIDTH, MAX_COLUMNS)
            # 至少显示1列
            return max(cols, 1)

        # 根据窗口宽度计算列数
        cols = calculate_columns(self.width())
        
        # 添加卡片到网格
        for i, card in enumerate(self.cards):
            row = i // cols
            col = i % cols
            self.grid_layout.addWidget(card, row, col, Qt.AlignCenter)
            card.show()

    def resizeEvent(self, event):
        self.update_layout()
        super().resizeEvent(event)

    def mousePressEvent(self, event):
        # 窗口拖动功能
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
        """根据当前主题更新样式"""
        if qconfig.theme == Theme.AUTO:
            # 获取系统当前主题
            lightness = QApplication.palette().color(QPalette.Window).lightness()
            is_dark = lightness <= 127
        else:
            is_dark = qconfig.theme == Theme.DARK
        
        # 主题样式更新
        colors = {'text': '#F5F5F5', 'bg': '#111116', 'title_bg': '#2D2D2D'} if  is_dark else {'text': '#111116', 'bg': '#F5F5F5', 'title_bg': '#E0E0E0'}
        self.setStyleSheet(f"""
            QDialog {{ background-color: {colors['bg']}; border-radius: 5px; }}
            #CustomTitleBar {{ background-color: {colors['title_bg']}; }}
            #TitleLabel {{ color: {colors['text']}; font-weight: bold; padding: 5px; }}
            #CloseButton {{ 
                background-color: transparent; 
                color: {colors['text']}; 
                border-radius: 4px; 
                font-weight: bold; 
                border: none;
            }}
            #CloseButton:hover {{ 
                background-color: #ff4d4d; 
                color: white; 
                border: none;
            }}
            QLabel, QPushButton, QTextEdit {{ color: {colors['text']}; }}
            QLineEdit {{ 
                background-color: {colors['bg']}; 
                color: {colors['text']}; 
                border: 1px solid #555555; 
                border-radius: 4px; 
                padding: 5px; 
            }}
            QPushButton {{ 
                background-color: {colors['bg']}; 
                color: {colors['text']}; 
                border: 1px solid #555555; 
                border-radius: 4px; 
                padding: 5px; 
            }}
            QPushButton:hover {{ background-color: #606060; }}
            QComboBox {{ 
                background-color: {colors['bg']}; 
                color: {colors['text']}; 
                border: 1px solid #555555; 
                border-radius: 4px; 
                padding: 5px; 
            }}
        """)
        
        # 设置标题栏颜色以匹配背景色（仅Windows系统）
        if os.name == 'nt':
            try:
                import ctypes
                # 修复参数类型错误
                hwnd = int(self.winId())  # 转换为整数句柄
                
                # 颜色格式要改成ARGB格式
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

    def closeEvent(self, event):
        if not self.saved:
            w = Dialog('未保存内容', '确定要关闭吗？', self)
            w.setFont(QFont(load_custom_font(), 12))
            w.yesButton.setText("确定")
            w.cancelButton.setText("取消")
            w.yesButton = PrimaryPushButton('确定')
            w.cancelButton = PushButton('取消')
            
            if w.exec():
                self.reject()
                return
            else:
                event.ignore()
                return
        event.accept()
    
    def update_card_theme_style(self, card):
        """根据当前主题更新样式"""
        if qconfig.theme == Theme.AUTO:
            # 获取系统当前主题
            lightness = QApplication.palette().color(QPalette.Window).lightness()
            is_dark = lightness <= 127
        else:
            is_dark = qconfig.theme == Theme.DARK
        # 主题样式更新
        colors = {'bg': '#111116'} if is_dark else {'bg': '#F5F5F5'}
        card.setStyleSheet(f'''
            QWidget#contributorCard {{
                background: {colors['bg']};
                border-radius: 8px;
                padding: 10px;
                margin-bottom: 10px;
            }}
        ''')
    
    def addContributorCard(self, contributor):
        """ 添加贡献者卡片 """
        card = QWidget()
        card.setObjectName('contributorCard')
        self.update_card_theme_style(card)
        cardLayout = QVBoxLayout(card)  # 垂直布局
        cardLayout.setContentsMargins(15, 15, 15, 15)
        cardLayout.setSpacing(10)

        # 头像
        avatar = AvatarWidget(contributor['avatar'])
        avatar.setRadius(64)
        avatar.setAlignment(Qt.AlignCenter)
        cardLayout.addWidget(avatar, 0, Qt.AlignCenter)

        # 昵称作为GitHub链接
        name = HyperlinkButton(contributor['github'], contributor['name'], self)
        name.setFont(QFont(load_custom_font(), 14))
        name.setStyleSheet('text-decoration: underline; color: #0066cc; background: transparent; border: none; padding: 0;')
        cardLayout.addWidget(name, 0, Qt.AlignCenter)

        # 职责
        role = BodyLabel(contributor['role'])
        role.setAlignment(Qt.AlignCenter)
        role.setFont(QFont(load_custom_font(), 12))
        role.setWordWrap(True)
        role.setMaximumWidth(500)
        cardLayout.addWidget(role, 0, Qt.AlignCenter)

        return card


class DonationDialog(QDialog):
    """ 捐赠支持对话框 """
    
    # 正确的MD5值
    CORRECT_MD5 = {
        'Alipay.png': '7faccb136ac70aa9c193bf7a4f68d131',  # 支付宝收款码
        'WeChat_Pay.png': 'ab01b5ff2c5bbdcfb5007873e9730e96'  # 微信支付收款码
    }
    
    # GitHub下载链接
    GITHUB_BASE_URL = 'https://github.com/SECTL/SecRandom/raw/main/app/resource/assets/contribution/'
    
    # 图片下载完成信号
    image_download_complete = pyqtSignal(str, bool)  # 文件名, 是否成功
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self.setWindowTitle('捐赠支持')
        self.setMinimumSize(800, 500)
        self.setSizeGripEnabled(True)
        self.update_theme_style()
        
        self.saved = False
        self.dragging = False
        self.drag_position = None

        if parent is not None:
            self.setParent(parent)
        
        # 创建自定义标题栏
        self.title_bar = QWidget()
        self.title_bar.setObjectName("CustomTitleBar")
        self.title_bar.setFixedHeight(35)
        
        # 标题栏布局
        title_layout = QHBoxLayout(self.title_bar)
        title_layout.setContentsMargins(10, 0, 10, 0)
        
        # 窗口标题
        self.title_label = BodyLabel("捐赠支持")
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

        # 创建滚动区域
        scroll = SingleDirectionScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        self.main_layout = QVBoxLayout(content)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollArea QWidget {
                border: none;
                background-color: transparent;
            }
        """)
        scroll.setWidget(content)
        
        # 主布局
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        # 添加自定义标题栏
        self.layout.addWidget(self.title_bar)
        # 添加内容区域
        content_layout = QVBoxLayout()
        content_layout.addWidget(scroll)
        content_layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addLayout(content_layout)
        
        self.update_theme_style()
        qconfig.themeChanged.connect(self.update_theme_style)
        
        # 添加感谢文本
        thanks_label = BodyLabel("感谢您对 SecRandom 项目的支持！您的捐赠将帮助我们持续改进和开发新功能。")
        thanks_label.setFont(QFont(load_custom_font(), 14))
        thanks_label.setWordWrap(True)
        thanks_label.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(thanks_label)
        
        # 添加捐赠方式标题
        methods_title = BodyLabel("捐赠方式")
        methods_title.setFont(QFont(load_custom_font(), 16, QFont.Bold))
        methods_title.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(methods_title)
        
        # 创建捐赠卡片布局
        self.cards_layout = QHBoxLayout()
        self.cards_layout.setSpacing(20)
        self.cards_layout.setContentsMargins(20, 10, 20, 10)
        
        # 添加支付宝捐赠卡片
        alipay_card = self.create_donation_card(
            "支付宝",
            f"{path_manager.get_resource_path('assets/contribution', 'Alipay.png')}",
            "使用支付宝扫码捐赠"
        )
        self.cards_layout.addWidget(alipay_card)
        
        # 添加微信支付捐赠卡片
        wechat_card = self.create_donation_card(
            "微信支付",
            f"{path_manager.get_resource_path('assets/contribution', 'WeChat_Pay.png')}",
            "使用微信扫码捐赠"
        )
        self.cards_layout.addWidget(wechat_card)
        
        self.main_layout.addLayout(self.cards_layout)
        
        # 添加说明文本
        note_label = BodyLabel("* 请扫描上方二维码进行捐赠，感谢您的支持！\n* 该捐献金额将会被平分给项目开发人员\n* 您的捐赠将帮助我们继续改进和发展SecRandom项目")
        note_label.setFont(QFont(load_custom_font(), 10))
        note_label.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(note_label)
        
        self.main_layout.addStretch()
        
        # 连接图片下载完成信号
        self.image_download_complete.connect(self.on_image_download_complete)
        
        # 使用独立线程检查并更新收款码图片
        self.download_worker = self.DownloadWorker(self)
        self.download_worker.finished.connect(self.download_worker.deleteLater)
        self.download_worker.start()
    
    def on_image_download_complete(self, filename, success):
        """ 图片下载完成后的回调函数 """
        if success:
            # logger.debug(f"图片下载完成: {filename}")
            # 下载成功后刷新界面
            self.refresh_donation_cards()
        # else:
        #     logger.debug(f"图片下载失败: {filename}")
    
    def refresh_donation_cards(self):
        """ 刷新捐赠卡片以重新加载图片 """
        # 清除现有的捐赠卡片
        if hasattr(self, 'cards_layout'):
            # 清除布局中的所有组件
            while self.cards_layout.count():
                item = self.cards_layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
            
            # 重新创建捐赠卡片
            alipay_card = self.create_donation_card(
                "支付宝",
                f"{path_manager.get_resource_path('assets/contribution', 'Alipay.png')}",
                "使用支付宝扫码捐赠"
            )
            self.cards_layout.addWidget(alipay_card)
            
            wechat_card = self.create_donation_card(
                "微信支付",
                f"{path_manager.get_resource_path('assets/contribution', 'WeChat_Pay.png')}",
                "使用微信扫码捐赠"
            )
            self.cards_layout.addWidget(wechat_card)
            
            # 强制更新界面
            self.update()
            # logger.debug("捐赠卡片已刷新，图片重新加载")
    
    class DownloadWorker(QThread):
        """ 图片下载工作线程 """
        finished = pyqtSignal()
        
        def __init__(self, dialog):
            super().__init__()
            self.dialog = dialog
        
        def run(self):
            """ 在独立线程中执行图片下载 """
            self.check_and_update_qr_codes()
            self.finished.emit()
        
        def check_and_update_qr_codes(self):
            """检查并更新收款码图片"""
            base_path = f"{path_manager.get_resource_path('assets/contribution')}\\"
            files_to_check = ['Alipay.png', 'WeChat_Pay.png']
            
            for filename in files_to_check:
                local_path = base_path + filename
                
                # 计算当前文件的MD5
                current_md5 = self.calculate_file_md5(local_path)
                
                if current_md5 is None:
                    # logger.debug(f"文件不存在: {local_path}")
                    # 文件不存在，直接下载
                    if self.download_file_from_github(filename, local_path):
                        # logger.debug(f"成功下载缺失的文件: {filename}")
                        # 发送下载完成信号
                        self.dialog.image_download_complete.emit(filename, True)
                    else:
                        # logger.debug(f"下载失败: {filename}")
                        self.dialog.image_download_complete.emit(filename, False)
                elif current_md5 != self.dialog.CORRECT_MD5.get(filename):
                    # logger.debug(f"MD5不匹配: {filename} (当前: {current_md5}, 期望: {self.dialog.CORRECT_MD5.get(filename)})")
                    # MD5不匹配，重新下载
                    if self.download_file_from_github(filename, local_path):
                        # 验证下载后的文件MD5
                        new_md5 = self.calculate_file_md5(local_path)
                        if new_md5 == self.dialog.CORRECT_MD5.get(filename):
                            # logger.debug(f"成功更新文件: {filename}")
                            # 发送下载完成信号
                            self.dialog.image_download_complete.emit(filename, True)
                        else:
                            # logger.debug(f"下载后MD5仍不匹配: {filename} (当前: {new_md5}, 期望: {self.dialog.CORRECT_MD5.get(filename)})")
                            self.dialog.image_download_complete.emit(filename, False)
                    else:
                        logger.error(f"更新文件失败: {filename}")
                        self.dialog.image_download_complete.emit(filename, False)
                # else:
                    # logger.debug(f"文件MD5验证通过: {filename}")
        
        def calculate_file_md5(self, file_path):
            """计算文件的MD5值"""
            try:
                # 直接使用内置open函数，避免二进制模式下的encoding参数问题
                with open(file_path, 'rb') as f:
                    file_hash = hashlib.md5()
                    while chunk := f.read(8192):
                        file_hash.update(chunk)
                return file_hash.hexdigest()
            except FileNotFoundError:
                return None
            except Exception as e:
                # logger.debug(f"计算MD5失败 {file_path}: {str(e)}")
                return None
        
        def download_file_from_github(self, filename, local_path):
            """从GitHub下载文件"""
            try:
                url = self.dialog.GITHUB_BASE_URL + filename
                # logger.debug(f"正在下载文件: {url}")
                
                # 尝试正常下载（启用SSL验证）
                response = requests.get(url, timeout=30)
                response.raise_for_status()
                
                # 确保目录存在
                os.makedirs(os.path.dirname(local_path), exist_ok=True)
                
                # 写入文件
                with open(local_path, 'wb') as f:
                    f.write(response.content)
                
                # logger.debug(f"成功下载文件: {filename}")
                return True
                
            except requests.exceptions.SSLError as e:
                # logger.debug(f"SSL证书验证失败 {filename}: {str(e)}")
                # logger.debug("尝试禁用SSL验证重新下载...")
                
                try:
                    # 禁用SSL验证重试
                    response = requests.get(url, timeout=30, verify=False)
                    response.raise_for_status()
                    
                    # 确保目录存在
                    os.makedirs(os.path.dirname(local_path), exist_ok=True)
                    
                    # 写入文件
                    with open(local_path, 'wb') as f:
                        f.write(response.content)
                    
                    # logger.debug(f"成功下载文件(禁用SSL验证): {filename}")
                    return True
                    
                except Exception as e2:
                    # logger.debug(f"禁用SSL验证后下载仍失败 {filename}: {str(e2)}")
                    # logger.debug("建议检查网络环境或防火墙设置")
                    return False
                    
            except requests.exceptions.ConnectionError as e:
                # logger.debug(f"网络连接错误 {filename}: {str(e)}")
                # logger.debug("建议检查网络连接和代理设置")
                return False
                
            except requests.exceptions.Timeout as e:
                # logger.debug(f"下载超时 {filename}: {str(e)}")
                # logger.debug("建议检查网络连接或稍后重试")
                return False
                
            except Exception as e:
                # logger.debug(f"下载文件失败 {filename}: {str(e)}")
                return False

    def create_donation_card(self, title, image_path, description):
        """ 创建捐赠卡片 """
        card = QWidget()
        card.setObjectName('donationCard')
        self.update_card_theme_style(card)
        cardLayout = QVBoxLayout(card)
        cardLayout.setContentsMargins(15, 15, 15, 15)
        cardLayout.setSpacing(10)

        # 标题
        title_label = BodyLabel(title)
        title_label.setFont(QFont(load_custom_font(), 14, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        cardLayout.addWidget(title_label, 0, Qt.AlignCenter)

        # 二维码图片
        try:
            qr_image = QPixmap(image_path)
            if qr_image.isNull():
                raise FileNotFoundError(f"图片文件未找到: {image_path}")
            
            qr_label = QLabel()
            qr_label.setPixmap(qr_image.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            qr_label.setAlignment(Qt.AlignCenter)
            cardLayout.addWidget(qr_label, 0, Qt.AlignCenter)
        except Exception as e:
            error_label = BodyLabel(f"图片加载失败\n{str(e)}")
            error_label.setAlignment(Qt.AlignCenter)
            error_label.setStyleSheet("color: #ff4444;")
            cardLayout.addWidget(error_label, 0, Qt.AlignCenter)

        # 描述
        desc_label = BodyLabel(description)
        desc_label.setFont(QFont(load_custom_font(), 12))
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setWordWrap(True)
        cardLayout.addWidget(desc_label, 0, Qt.AlignCenter)

        return card

    def mousePressEvent(self, event):
        """ 窗口拖动功能 """
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
        """根据当前主题更新样式"""
        if qconfig.theme == Theme.AUTO:
            lightness = QApplication.palette().color(QPalette.Window).lightness()
            is_dark = lightness <= 127
        else:
            is_dark = qconfig.theme == Theme.DARK
        
        colors = {'text': '#F5F5F5', 'bg': '#111116', 'title_bg': '#2D2D2D'} if is_dark else {'text': '#111116', 'bg': '#F5F5F5', 'title_bg': '#E0E0E0'}
        self.setStyleSheet(f"""
            QDialog {{ background-color: {colors['bg']}; border-radius: 5px; }}
            #CustomTitleBar {{ background-color: {colors['title_bg']}; }}
            #TitleLabel {{ color: {colors['text']}; font-weight: bold; padding: 5px; }}
            #CloseButton {{ 
                background-color: transparent; 
                color: {colors['text']}; 
                border-radius: 4px; 
                font-weight: bold; 
                border: none;
            }}
            #CloseButton:hover {{ 
                background-color: #ff4d4d; 
                color: white; 
                border: none;
            }}
            QLabel, QPushButton, QTextEdit {{ color: {colors['text']}; }}
            QLineEdit {{ 
                background-color: {colors['bg']}; 
                color: {colors['text']}; 
                border: 1px solid #555555; 
                border-radius: 4px; 
                padding: 5px; 
            }}
            QPushButton {{ 
                background-color: {colors['bg']}; 
                color: {colors['text']}; 
                border: 1px solid #555555; 
                border-radius: 4px; 
                padding: 5px; 
            }}
            QPushButton:hover {{ background-color: #606060; }}
            QComboBox {{ 
                background-color: {colors['bg']}; 
                color: {colors['text']}; 
                border: 1px solid #555555; 
                border-radius: 4px; 
                padding: 5px; 
            }}
        """)
        
        # 设置标题栏颜色以匹配背景色（仅Windows系统）
        if os.name == 'nt':
            try:
                import ctypes
                hwnd = int(self.winId())
                
                bg_color = colors['bg'].lstrip('#')
                rgb_color = int(f'FF{bg_color}', 16) if len(bg_color) == 6 else int(bg_color, 16)
                
                ctypes.windll.dwmapi.DwmSetWindowAttribute(
                    ctypes.c_int(hwnd),
                    35,
                    ctypes.byref(ctypes.c_uint(rgb_color)),
                    ctypes.sizeof(ctypes.c_uint)
                )
            except Exception as e:
                logger.error(f"设置标题栏颜色失败: {str(e)}")

    def update_card_theme_style(self, card):
        """ 根据当前主题更新卡片样式 """
        if qconfig.theme == Theme.AUTO:
            lightness = QApplication.palette().color(QPalette.Window).lightness()
            is_dark = lightness <= 127
        else:
            is_dark = qconfig.theme == Theme.DARK
        
        colors = {'bg': '#111116'} if is_dark else {'bg': '#F5F5F5'}
        card.setStyleSheet(f'''
            QWidget#donationCard {{
                background: {colors['bg']};
                border-radius: 12px;
                border: 1px solid {'#333333' if is_dark else '#DDDDDD'};
                padding: 15px;
                margin-bottom: 10px;
            }}
        ''')

    def closeEvent(self, event):
        if not self.saved:
            w = Dialog('关闭确认', '确定要关闭捐赠窗口吗？', self)
            w.setFont(QFont(load_custom_font(), 12))
            w.yesButton.setText("确定")
            w.cancelButton.setText("取消")
            w.yesButton = PrimaryPushButton('确定')
            w.cancelButton = PushButton('取消')
            
            if w.exec():
                self.reject()
                return
            else:
                event.ignore()
                return
        event.accept()
        