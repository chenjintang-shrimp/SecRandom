# 打包修复说明（快速指南）

## 修复的问题

✅ 修复了 PyInstaller 和 Nuitka 打包后文本无法加载的问题
✅ 修复了打包后界面资源文件路径错误的问题
✅ 修复了语言模块动态加载在打包环境中失败的问题

## 快速开始

### 使用 PyInstaller 打包

```powershell
python build_pyinstaller.py
```

### 使用 Nuitka 打包

```powershell
python build_nuitka.py
```

## 主要修改文件

1. **app/tools/path_utils.py** - 修复打包后的路径识别
2. **app/tools/language_manager.py** - 修复语言模块动态加载
3. **Secrandom.spec** - 更新 PyInstaller 资源收集配置
4. **build_nuitka.py** - 新增 Nuitka 打包脚本（新文件）
5. **build_pyinstaller.py** - 新增 PyInstaller 打包脚本（新文件）

## 详细文档

查看 [PACKAGING.md](PACKAGING.md) 获取完整的技术细节和故障排查指南。
