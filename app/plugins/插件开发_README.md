# SecRandom 插件系统

## 概述
SecRandom 支持插件系统，允许用户扩展应用功能。插件可以包含自定义界面和功能。

## 插件结构

每个插件应该包含以下文件：

```
app/plugins/your_plugin_name/
├── plugin.json      # 插件配置文件
└── page.py          # 插件页面文件（可选）
```

## 插件配置文件 (plugin.json)

```json
{
  "name": "插件名称",
  "version": "1.0.0",
  "author": "作者名称",
  "description": "插件描述",
  "icon": "plugins/插件名称/assets/icon.png"
}
```

### 配置字段说明

- `name`: 插件显示名称
- `version`: 插件版本号
- `author`: 插件作者
- `description`: 插件描述
- `icon`: 插件图标(使用相对路径-插件文件夹根目录下的assets文件夹,名称要为'icon.png', 'icon.ico', 'icon.svg'其中之一)

## 插件页面文件 (page.py)

如果插件需要显示界面，需要创建 `page.py` 文件并包含 `PluginPage` 类：

```python
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from qfluentwidgets import *


class PluginPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("插件页面")
        self.setup_ui()
    
    def setup_ui(self):
        # 在这里设置你的界面
        layout = QVBoxLayout(self)
        
        title_label = TitleLabel("我的插件")
        layout.addWidget(title_label)
        
        # 添加更多界面元素...
```

## 插件管理

### 1. 通过设置界面管理

1. 打开主应用
2. 点击设置按钮
3. 选择"插件管理"选项卡
4. 在插件管理界面中，你可以：
   - 查看已安装的插件
   - 导入新的插件包（.zip 文件）
   - 删除现有插件
   - 打开插件页面（如果插件有页面文件）

### 2. 通过托盘菜单快速访问

右键点击系统托盘图标，选择"打开插件管理"可以直接进入插件管理界面。

### 3. 导入插件

1. 点击"导入"按钮
2. 选择插件包文件（.zip 格式）
3. 插件包必须包含 `plugin.json` 配置文件
4. 系统会自动解压并加载插件

### 4. 删除插件

1. 在插件卡片中点击"删除"按钮
2. 确认删除操作
3. 插件将被完全移除

## 插件包格式

插件包是一个 .zip 文件，包含以下结构：

```
plugin_name.zip
├── plugin.json
├── page.py (可选)
└── 其他资源文件 (可选)
```

## 示例插件

系统提供了一个示例插件 `example_plugin`，你可以参考它的结构来创建自己的插件。

## 注意事项

1. 插件目录位于 `app/plugins/`
2. 插件名称必须唯一，不能重复
3. 插件页面类必须命名为 `PluginPage`
4. 插件可以使用 qfluentwidgets 的所有组件
5. 插件页面会在独立的窗口中打开

## 常用 Fluent Icon

- 可以看app\resource\assets路径下的图标
- 如需增加需要自行添加到assets路径下(需要按照格式添加暗色和亮色图标)
- 或者您可以自己在插件路径下添加图标文件(需要自己在插件中自行写图标的相对路径)

## 开发建议

1. 保持插件简单和专注
2. 提供清晰的描述和作者信息
3. 测试插件在不同主题下的显示效果
4. 遵循现有的 UI 风格和交互模式
5. 添加适当的错误处理和日志记录