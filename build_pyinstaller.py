"""
PyInstaller 打包脚本
用于构建 SecRandom 的独立可执行文件
"""

import subprocess
import sys
from pathlib import Path

# 获取项目根目录
PROJECT_ROOT = Path(__file__).parent


def main():
    """执行 PyInstaller 打包"""
    print("=" * 60)
    print("开始使用 PyInstaller 打包 SecRandom")
    print("=" * 60)

    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "Secrandom.spec",
        "--clean",
        "--noconfirm",
    ]

    # 打印命令
    print("\n执行命令:")
    print(" ".join(cmd))
    print("\n" + "=" * 60)

    # 执行打包
    try:
        subprocess.run(cmd, check=True, cwd=PROJECT_ROOT)
        print("\n" + "=" * 60)
        print("打包成功！")
        print("可执行文件位于: dist/SecRandom.exe")
        print("=" * 60)
    except subprocess.CalledProcessError as e:
        print("\n" + "=" * 60)
        print(f"打包失败: {e}")
        print("=" * 60)
        sys.exit(1)


if __name__ == "__main__":
    main()
