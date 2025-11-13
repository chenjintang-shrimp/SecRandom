"""
Nuitka 打包配置脚本
用于构建 SecRandom 的独立可执行文件
"""

import subprocess
import sys
from pathlib import Path

# 获取项目根目录
PROJECT_ROOT = Path(__file__).parent
APP_DIR = PROJECT_ROOT / "app"
RESOURCES_DIR = APP_DIR / "resources"
LANGUAGE_MODULES_DIR = APP_DIR / "Language" / "modules"


def get_nuitka_command():
    """生成 Nuitka 打包命令"""

    cmd = [
        sys.executable,
        "-m",
        "nuitka",
        "--standalone",
        "--onefile",
        "--enable-plugin=pyside6",
        "--windows-disable-console",
        "--assume-yes-for-downloads",
        # 输出目录
        "--output-dir=dist",
        # 应用程序信息
        "--product-name=SecRandom",
        "--file-description=公平随机抽取系统",
        "--product-version=1.1.0",
        "--copyright=Copyright (c) 2024",
        # 包含资源文件
        f"--include-data-dir={RESOURCES_DIR}=app/resources",
        # 包含语言模块
        f"--include-data-dir={LANGUAGE_MODULES_DIR}=app/Language/modules",
        # 包含必要的包
        "--include-package=qfluentwidgets",
        "--include-package=app.Language.modules",
        "--include-package=app.view",
        "--include-package=app.tools",
        "--include-package=app.page_building",
        # 隐藏导入
        "--include-module=app.Language.obtain_language",
        "--include-module=app.tools.language_manager",
        "--include-module=app.tools.path_utils",
    ]

    # 添加所有语言模块文件
    if LANGUAGE_MODULES_DIR.exists():
        for file in LANGUAGE_MODULES_DIR.glob("*.py"):
            if file.name != "__init__.py":
                module_name = file.stem
                cmd.append(f"--include-module=app.Language.modules.{module_name}")

    # 主入口文件
    cmd.append("main.py")

    return cmd


def main():
    """执行打包"""
    print("=" * 60)
    print("开始使用 Nuitka 打包 SecRandom")
    print("=" * 60)

    # 生成命令
    cmd = get_nuitka_command()

    # 打印命令
    print("\n执行命令:")
    print(" ".join(cmd))
    print("\n" + "=" * 60)

    # 执行打包
    try:
        subprocess.run(cmd, check=True, cwd=PROJECT_ROOT)
        print("\n" + "=" * 60)
        print("打包成功！")
        print("=" * 60)
    except subprocess.CalledProcessError as e:
        print("\n" + "=" * 60)
        print(f"打包失败: {e}")
        print("=" * 60)
        sys.exit(1)


if __name__ == "__main__":
    main()
