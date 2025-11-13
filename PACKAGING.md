# SecRandom 打包修复说明

## 问题描述

打包后的应用程序出现以下问题：
1. 文本无法加载（语言模块加载失败）
2. 界面无法正常显示（资源文件路径错误）

## 修复内容

### 1. 路径管理修复 (`app/tools/path_utils.py`)

**问题**: 打包后无法正确识别应用程序根目录和资源文件路径

**修复**:
```python
def _get_app_root(self) -> Path:
    if getattr(sys, "frozen", False):
        # PyInstaller 会设置 sys._MEIPASS 指向临时解压目录
        if hasattr(sys, '_MEIPASS'):
            return Path(sys._MEIPASS)
        else:
            return Path(sys.executable).parent
    else:
        # 开发环境
        return Path(__file__).parent.parent.parent
```

这样确保：
- 开发环境：使用项目根目录
- PyInstaller打包：使用 `sys._MEIPASS` 临时目录
- Nuitka打包：使用可执行文件所在目录

### 2. 语言模块动态加载修复 (`app/tools/language_manager.py`)

**问题**: 使用 `importlib.util.spec_from_file_location` 在打包环境中无法正确加载模块

**修复**:
```python
# 尝试直接导入（适用于打包环境）
try:
    module = __import__(
        f'app.Language.modules.{language_module_name}',
        fromlist=[language_module_name]
    )
except ImportError:
    # 如果直接导入失败，使用动态加载（开发环境）
    spec = importlib.util.spec_from_file_location(...)
    ...
```

这样确保：
- 优先使用标准导入（打包环境兼容）
- 回退到动态加载（开发环境灵活）

### 3. PyInstaller 配置修复 (`Secrandom.spec`)

**修复内容**:

#### 3.1 语言模块收集
```python
# 保持正确的目录结构
for file in os.listdir(language_modules_dir):
    if file.endswith('.py') and file != '__init__.py':
        src_path = os.path.join(language_modules_dir, file)
        dst_path = os.path.join('app', 'Language', 'modules')
        language_modules_datas.append((src_path, dst_path))
```

#### 3.2 资源文件收集
```python
# 保持相对路径结构
for root, dirs, files in os.walk(resources_dir):
    for file in files:
        src_path = os.path.join(root, file)
        rel_path = os.path.relpath(root, project_root)
        resources_datas.append((src_path, rel_path))
```

#### 3.3 QFluentWidgets 资源
```python
# 自动收集 QFluentWidgets 相关资源
qfluentwidgets_datas = collect_data_files('qfluentwidgets')
resources_datas.extend(qfluentwidgets_datas)
```

### 4. 模块包结构完善

添加缺失的 `__init__.py` 文件：
- `app/Language/__init__.py`
- `app/Language/modules/__init__.py`

这确保 Python 能够正确识别这些目录为包。

## 使用方法

### PyInstaller 打包

```powershell
# 方法 1: 使用构建脚本（推荐）
python build_pyinstaller.py

# 方法 2: 直接使用 PyInstaller
python -m PyInstaller Secrandom.spec --clean --noconfirm
```

### Nuitka 打包

```powershell
# 使用构建脚本
python build_nuitka.py
```

## 验证方法

打包完成后，验证以下功能：

1. **语言加载测试**
   - 启动应用程序
   - 检查界面文字是否正确显示
   - 尝试切换语言（如果支持）

2. **资源文件测试**
   - 检查图标是否正常显示
   - 检查字体是否正确加载
   - 检查其他资源文件（音频、图片等）

3. **功能完整性测试**
   - 测试主要功能是否正常工作
   - 检查设置是否能正确保存和读取
   - 验证历史记录等数据功能

## 常见问题排查

### 问题 1: 打包后仍然无法加载文本

**解决方案**:
1. 检查 `logs` 目录中的日志文件，查看具体错误
2. 确认 `app/Language/modules` 中的所有 `.py` 文件都被包含
3. 检查 `app/resources/Language` 中的 JSON 文件是否存在

### 问题 2: 界面资源无法显示

**解决方案**:
1. 确认 `app/resources` 目录被完整打包
2. 检查日志中的路径错误信息
3. 验证 `sys._MEIPASS` 是否正确设置

### 问题 3: Nuitka 打包失败

**解决方案**:
1. 确保已安装 C++ 编译器（Visual Studio Build Tools）
2. 检查 Python 版本是否与 Nuitka 兼容
3. 尝试添加 `--show-progress` 参数查看详细进度

## 技术细节

### PyInstaller 工作原理

PyInstaller 打包时：
1. 分析 Python 脚本的依赖
2. 将所有依赖打包到一个目录或单个文件
3. 运行时解压到临时目录（`sys._MEIPASS`）
4. 从临时目录执行程序

### 资源文件路径解析流程

```
开发环境:
项目根目录/app/resources/xxx.png

打包后:
临时目录(_MEIPASS)/app/resources/xxx.png
```

### 模块导入优先级

```python
1. 标准导入 (打包环境)
   ↓ 失败
2. 动态文件加载 (开发环境)
   ↓ 失败
3. 记录错误日志
```

## 维护建议

1. **添加新语言模块时**
   - 确保在 `app/Language/modules/` 目录下
   - 重新打包时会自动包含

2. **添加新资源文件时**
   - 放在 `app/resources/` 对应子目录
   - 重新打包时会自动包含

3. **更新依赖时**
   - 更新 `pyproject.toml` 中的版本
   - 清理旧的构建文件 (`build/`, `dist/`)
   - 重新打包

4. **调试打包问题**
   - 启用控制台模式：修改 `.spec` 中 `console=True`
   - 查看启动时的日志输出
   - 使用 `--debug all` 参数获取详细信息

## 更新日志

### 2025-11-13
- 修复路径管理器对打包环境的支持
- 修复语言模块动态加载问题
- 更新 PyInstaller 配置文件
- 创建 Nuitka 打包脚本
- 添加打包构建脚本
- 完善模块包结构

---

如有其他问题，请查看日志文件或提交 Issue。
