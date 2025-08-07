# 插件依赖离线缓存目录

此目录用于存放插件依赖的离线wheel文件，支持插件在没有网络连接的情况下安装依赖。

## 使用方法

### 1. 下载wheel文件
```bash
# 下载指定包的wheel文件
pip download package_name==version -d resources/wheels/

# 下载多个包的wheel文件
pip download -r requirements.txt -d resources/wheels/
```

### 2. 支持的包类型
- **ollama**: 用于大语言模型交互
- **transformers**: 用于自然语言处理
- **torch**: 深度学习框架
- **numpy**: 数值计算
- **pandas**: 数据处理
- **requests**: HTTP请求
- 其他常用Python包

### 3. 目录结构
```
resources/wheels/
├── ollama-0.1.0-py3-none-any.whl
├── transformers-4.20.0-py3-none-any.whl
├── torch-1.12.0-cp39-cp39-win_amd64.whl
├── numpy-1.21.0-cp39-cp39-win_amd64.whl
└── ...
```

### 4. 插件依赖安装流程
1. 插件加载时检查 `__requirements__.txt` 文件
2. 在插件目录下创建 `site-packages` 目录
3. 使用以下命令安装依赖：
   ```bash
   pip install --target <plugin_dir>/site-packages -r __requirements__.txt --find-links resources/wheels
   ```
4. 将 `site-packages` 目录添加到 `sys.path`
5. 依赖安装成功后加载插件

### 5. 注意事项
- wheel文件应该与目标Python版本兼容
- 建议定期更新wheel文件以获取最新版本
- 某些包可能需要额外的系统依赖
- 在Windows环境下，优先下载 `.whl` 文件而非源码包

## 维护建议

### 定期更新wheel文件
```bash
# 批量更新常用包
pip download --upgrade ollama transformers torch numpy pandas requests -d resources/wheels/
```

### 清理旧版本
```bash
# 删除指定包的旧版本
find resources/wheels/ -name "package_name-*" -not -name "package_name-latest-version*" -delete
```

### 验证wheel文件完整性
```bash
# 检查wheel文件是否损坏
for file in resources/wheels/*.whl; do
    if unzip -t "$file" > /dev/null 2>&1; then
        echo "✓ $file is valid"
    else
        echo "✗ $file is corrupted"
    fi
done
```