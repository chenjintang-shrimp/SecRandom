# SecRandom 安装包构建指南

## 概述

本文档描述了如何使用 Inno Setup 为 SecRandom 创建 Windows 安装包，以及安装包特有的自动更新功能。

## 安装包特性

### 1. 安装包标识
安装包会在 `app/Settings/installer_marker.json` 中创建唯一标识，用于区分压缩包和安装包版本。

### 2. 自动更新功能
安装包版本支持自动更新功能：
- 检测到新版本时，显示自动更新对话框
- 支持从 GitHub 直接下载新版本安装包
- 自动执行静默安装更新

## 构建步骤

### 本地构建

1. **安装 Inno Setup**
   - 从 [jrsoftware.org](https://jrsoftware.org) 下载并安装 Inno Setup
   - 确保 Inno Setup 安装目录在系统 PATH 中

2. **准备构建环境**
   ```bash
   # 确保已安装所有依赖
   pip install -r requirements.txt
   
   # 构建应用程序
   pyinstaller main.py -w -D -i ./resources/SecRandom.ico -n SecRandom --add-data ./app/resource:app/resource --add-data LICENSE:.
   ```

3. **构建安装包**
   ```bash
   # 使用 Inno Setup 编译脚本
   "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer.iss
   ```

### GitHub Actions 自动构建

项目已配置 GitHub Actions 自动构建：
- 每次推送标签 `v*` 时自动触发
- 自动构建所有平台的安装包和压缩包
- 自动发布到 GitHub Releases

## 安装包结构

```
安装目录/
├── SecRandom.exe          # 主程序
├── app/
│   ├── resource/          # 资源文件
│   └── Settings/
│       ├── Settings.json  # 用户设置
│       └── installer_marker.json  # 安装包标识
├── LICENSE                # 许可证文件
└── ...                    # 其他依赖文件
```

## 自动更新机制

### 工作原理

1. **版本检测**：启动时检查 GitHub 最新版本
2. **用户提示**：发现新版本时显示更新通知
3. **自动下载**：点击更新后自动下载新安装包
4. **静默安装**：下载完成后自动执行静默安装
5. **应用重启**：安装完成后自动重启应用

### 更新流程

```
用户启动应用
    ↓
检查新版本
    ↓
发现新版本 → 显示更新通知
    ↓
用户点击更新 → 下载新安装包
    ↓
下载完成 → 启动静默安装
    ↓
安装完成 → 重启应用
```

## 配置说明

### installer.iss 关键配置

- **AppName**: 应用程序名称
- **AppVersion**: 应用程序版本（自动从 GitHub 标签获取）
- **DefaultDirName**: 默认安装路径
- **OutputBaseFilename**: 输出安装包文件名

### 安装包标识文件

`app/Settings/installer_marker.json`:
```json
{
    "installer_package": true,
    "package_type": "innosetup_installer",
    "created_by": "SecRandom Inno Setup Installer",
    "installation_date": "2024-xx-xx",
    "installation_path": "C:\\Program Files\\SecRandom",
    "auto_update_enabled": true,
    "version": "1.2.0.0"
}
```

## 故障排除

### 常见问题

1. **Inno Setup 未找到**
   - 确保已安装 Inno Setup
   - 检查 PATH 环境变量

2. **构建失败**
   - 检查 dist 目录是否存在且包含正确文件
   - 验证 installer.iss 中的路径设置

3. **自动更新失败**
   - 检查网络连接
   - 验证 GitHub API 访问权限
   - 检查临时目录写入权限

### 调试模式

在 installer.iss 中添加以下参数启用调试：
```
[Setup]
; 调试参数
OutputBaseFilename=SecRandom-Setup-{#MyAppVersion}-DEBUG
SignTool=none
```

## 版本更新

当发布新版本时：

1. 更新 `installer.iss` 中的 `MyAppVersion`
2. 确保 `requirements.txt` 中的依赖是最新的
3. 测试安装包在干净系统上的安装
4. 验证自动更新功能正常工作

## 支持

如有问题，请在 GitHub Issues 中提交，或联系维护团队。