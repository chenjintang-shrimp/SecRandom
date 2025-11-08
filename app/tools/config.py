"""
通知工具模块
提供便捷的InfoBar通知功能，用于在应用程序中显示重要的用户信息
"""

from typing import Optional, Union
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt

from qfluentwidgets import InfoBar, InfoBarPosition, FluentIcon, InfoBarIcon


def show_success_notification(
    title: str,
    content: str,
    parent: Optional[QWidget] = None,
    duration: int = 3000,
    position: Union[InfoBarPosition, str] = InfoBarPosition.TOP,
    is_closable: bool = True,
    orient: Qt.Orientation = Qt.Orientation.Horizontal
) -> InfoBar:
    """
    显示成功通知
    
    Args:
        title: 通知标题
        content: 通知内容
        parent: 父窗口组件
        duration: 显示时长(毫秒)，-1表示永不消失
        position: 显示位置，默认为顶部
        is_closable: 是否可关闭
        orient: 布局方向，默认为水平
        
    Returns:
        InfoBar实例
    """
    return InfoBar.success(
        title=title,
        content=content,
        orient=orient,
        isClosable=is_closable,
        position=position,
        duration=duration,
        parent=parent
    )


def show_warning_notification(
    title: str,
    content: str,
    parent: Optional[QWidget] = None,
    duration: int = -1,
    position: Union[InfoBarPosition, str] = InfoBarPosition.BOTTOM,
    is_closable: bool = True,
    orient: Qt.Orientation = Qt.Orientation.Horizontal
) -> InfoBar:
    """
    显示警告通知
    
    Args:
        title: 通知标题
        content: 通知内容
        parent: 父窗口组件
        duration: 显示时长(毫秒)，-1表示永不消失
        position: 显示位置，默认为底部
        is_closable: 是否可关闭
        orient: 布局方向，默认为水平
        
    Returns:
        InfoBar实例
    """
    return InfoBar.warning(
        title=title,
        content=content,
        orient=orient,
        isClosable=is_closable,
        position=position,
        duration=duration,
        parent=parent
    )


def show_error_notification(
    title: str,
    content: str,
    parent: Optional[QWidget] = None,
    duration: int = 5000,
    position: Union[InfoBarPosition, str] = InfoBarPosition.BOTTOM_RIGHT,
    is_closable: bool = True,
    orient: Qt.Orientation = Qt.Orientation.Vertical
) -> InfoBar:
    """
    显示错误通知
    
    Args:
        title: 通知标题
        content: 通知内容
        parent: 父窗口组件
        duration: 显示时长(毫秒)，-1表示永不消失
        position: 显示位置，默认为右下角
        is_closable: 是否可关闭
        orient: 布局方向，默认为垂直(适合长内容)
        
    Returns:
        InfoBar实例
    """
    return InfoBar.error(
        title=title,
        content=content,
        orient=orient,
        isClosable=is_closable,
        position=position,
        duration=duration,
        parent=parent
    )


def show_info_notification(
    title: str,
    content: str,
    parent: Optional[QWidget] = None,
    duration: int = -1,
    position: Union[InfoBarPosition, str] = InfoBarPosition.BOTTOM_LEFT,
    is_closable: bool = True,
    orient: Qt.Orientation = Qt.Orientation.Horizontal
) -> InfoBar:
    """
    显示信息通知
    
    Args:
        title: 通知标题
        content: 通知内容
        parent: 父窗口组件
        duration: 显示时长(毫秒)，-1表示永不消失
        position: 显示位置，默认为左下角
        is_closable: 是否可关闭
        orient: 布局方向，默认为水平
        
    Returns:
        InfoBar实例
    """
    return InfoBar.info(
        title=title,
        content=content,
        orient=orient,
        isClosable=is_closable,
        position=position,
        duration=duration,
        parent=parent
    )


def show_custom_notification(
    title: str,
    content: str,
    icon: Union[FluentIcon, InfoBarIcon, str] = InfoBarIcon.INFORMATION,
    parent: Optional[QWidget] = None,
    duration: int = 3000,
    position: Union[InfoBarPosition, str] = InfoBarPosition.TOP,
    is_closable: bool = True,
    orient: Qt.Orientation = Qt.Orientation.Horizontal,
    background_color: Optional[str] = None,
    text_color: Optional[str] = None
) -> InfoBar:
    """
    显示自定义通知
    
    Args:
        title: 通知标题
        content: 通知内容
        icon: 通知图标
        parent: 父窗口组件
        duration: 显示时长(毫秒)，-1表示永不消失
        position: 显示位置，默认为顶部
        is_closable: 是否可关闭
        orient: 布局方向，默认为水平
        background_color: 背景颜色
        text_color: 文本颜色
        
    Returns:
        InfoBar实例
    """
    info_bar = InfoBar.new(
        icon=icon,
        title=title,
        content=content,
        orient=orient,
        isClosable=is_closable,
        position=position,
        duration=duration,
        parent=parent
    )
    
    if background_color and text_color:
        info_bar.setCustomBackgroundColor(background_color, text_color)
    
    return info_bar


class NotificationConfig:
    """通知配置类，用于定义通知的各种参数"""
    
    def __init__(
        self,
        title: str = "",
        content: str = "",
        icon: Union[FluentIcon, InfoBarIcon, str] = None,
        duration: int = 3000,
        position: Union[InfoBarPosition, str] = InfoBarPosition.TOP,
        is_closable: bool = True,
        orient: Qt.Orientation = Qt.Orientation.Horizontal,
        background_color: Optional[str] = None,
        text_color: Optional[str] = None
    ):
        self.title = title
        self.content = content
        self.icon = icon
        self.duration = duration
        self.position = position
        self.is_closable = is_closable
        self.orient = orient
        self.background_color = background_color
        self.text_color = text_color


class NotificationType:
    """预定义的通知类型"""
    
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    INFO = "info"
    CUSTOM = "custom"


def show_notification(
    notification_type: str,
    config: NotificationConfig,
    parent: Optional[QWidget] = None
) -> InfoBar:
    """
    显示通知
    
    Args:
        notification_type: 通知类型，值为NotificationType中定义的常量
        config: 通知配置对象
        parent: 父窗口组件
        
    Returns:
        InfoBar实例
    """
    if notification_type == NotificationType.SUCCESS:
        return InfoBar.success(
            title=config.title,
            content=config.content,
            orient=config.orient,
            isClosable=config.is_closable,
            position=config.position,
            duration=config.duration,
            parent=parent
        )
    elif notification_type == NotificationType.WARNING:
        return InfoBar.warning(
            title=config.title,
            content=config.content,
            orient=config.orient,
            isClosable=config.is_closable,
            position=config.position,
            duration=config.duration,
            parent=parent
        )
    elif notification_type == NotificationType.ERROR:
        return InfoBar.error(
            title=config.title,
            content=config.content,
            orient=config.orient,
            isClosable=config.is_closable,
            position=config.position,
            duration=config.duration,
            parent=parent
        )
    elif notification_type == NotificationType.INFO:
        return InfoBar.info(
            title=config.title,
            content=config.content,
            orient=config.orient,
            isClosable=config.is_closable,
            position=config.position,
            duration=config.duration,
            parent=parent
        )
    elif notification_type == NotificationType.CUSTOM:
        info_bar = InfoBar.new(
            icon=config.icon or InfoBarIcon.INFORMATION,
            title=config.title,
            content=config.content,
            orient=config.orient,
            isClosable=config.is_closable,
            position=config.position,
            duration=config.duration,
            parent=parent
        )
        
        if config.background_color and config.text_color:
            info_bar.setCustomBackgroundColor(config.background_color, config.text_color)
            
        return info_bar
    else:
        raise ValueError(f"不支持的通知类型: {notification_type}")
