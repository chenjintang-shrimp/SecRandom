#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SecRandom 本地打包脚本
基于 .github/workflows/build.yml 的打包逻辑
"""

import os
import sys
import subprocess
import shutil
import platform
from pathlib import Path


def run_command(cmd, cwd=None, check=True):
    """运行命令并返回结果"""
    print(f"执行命令: {cmd}")
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=cwd,
            check=check,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        if result.stdout:
            print(result.stdout)
        return result
    except subprocess.CalledProcessError as e:
        print(f"命令执行失败: {e}")
        if e.stderr:
            print(f"错误信息: {e.stderr}")
        if check:
            sys.exit(1)
        return e


def safe_remove_directory(path, max_retries=5, retry_delay=2):
    """安全删除目录，处理文件锁定问题"""
    import time
    import stat
    
    def on_rm_error(func, path, exc_info):
        """处理删除时的错误，尝试修改文件权限后重试"""
        # 尝试修改文件权限
        os.chmod(path, stat.S_IWRITE)
        func(path)
    
    for attempt in range(max_retries):
        try:
            if os.path.exists(path):
                # 使用错误回调函数处理权限问题
                shutil.rmtree(path, onerror=on_rm_error)
                print(f"成功删除目录: {path}")
                return True
        except (OSError, PermissionError) as e:
            if attempt < max_retries - 1:
                print(f"删除目录失败 (尝试 {attempt + 1}/{max_retries}): {e}")
                print(f"等待 {retry_delay} 秒后重试...")
                time.sleep(retry_delay)
                
                # 尝试强制关闭可能占用文件的进程
                if platform.system() == 'Windows':
                    try:
                        # 终止Python相关进程
                        subprocess.run(['taskkill', '/F', '/IM', 'python.exe'], 
                                     capture_output=True, check=False)
                        subprocess.run(['taskkill', '/F', '/IM', 'pythonw.exe'], 
                                     capture_output=True, check=False)
                        # 尝试终止Git相关进程（可能锁定.gitignore）
                        subprocess.run(['taskkill', '/F', '/IM', 'git.exe'], 
                                     capture_output=True, check=False)
                        # 尝试终止资源管理器（可能锁定文件）
                        subprocess.run(['taskkill', '/F', '/IM', 'explorer.exe'], 
                                     capture_output=True, check=False)
                        # 等待一秒让进程完全终止
                        time.sleep(1)
                    except:
                        pass
            else:
                print(f"无法删除目录 {path}，请手动关闭可能使用该目录的程序后重试")
                print(f"错误详情: {e}")
                return False
    
    return False


def check_uv_installed():
    """检查uv是否安装"""
    try:
        result = subprocess.run(['uv', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"uv已安装: {result.stdout.strip()}")
            return True
    except FileNotFoundError:
        pass
    print("uv未安装，请先安装uv: https://docs.astral.sh/uv/getting-started/installation/")
    return False


def create_virtual_environment():
    """创建虚拟环境"""
    print("创建虚拟环境...")
    if os.path.exists('.venv'):
        print("虚拟环境已存在，删除旧环境...")
        if not safe_remove_directory('.venv'):
            print("警告: 无法删除旧虚拟环境")
            print("建议手动关闭可能占用文件的程序后重试")
            print("或者尝试使用现有虚拟环境继续打包")
            
            # 询问用户是否继续使用现有环境
            try:
                response = input("是否继续使用现有虚拟环境? (y/N): ").strip().lower()
                if response != 'y':
                    print("用户选择退出，请手动解决问题后重试")
                    sys.exit(1)
                else:
                    print("继续使用现有虚拟环境...")
            except KeyboardInterrupt:
                print("\n用户中断操作")
                sys.exit(1)
    
    run_command('uv venv')
    print("虚拟环境创建完成")


def get_venv_python():
    """获取虚拟环境中的Python解释器路径"""
    if platform.system() == 'Windows':
        return '.venv/Scripts/python.exe'
    else:
        return '.venv/bin/python'


def get_venv_pip():
    """获取虚拟环境中的pip路径"""
    if platform.system() == 'Windows':
        return '.venv/Scripts/pip.exe'
    else:
        return '.venv/bin/pip'


def install_dependencies():
    """安装依赖"""
    print("安装依赖...")
    venv_pip = get_venv_pip()
    
    # 清理uv缓存以避免使用旧版本
    print("清理uv缓存...")
    run_command('uv cache clean')
    
    # 使用uv安装依赖
    run_command('uv pip install -r requirements.txt')
    print("依赖安装完成")


def install_pyinstaller():
    """安装PyInstaller"""
    print("安装PyInstaller...")
    run_command('uv pip install pyinstaller')
    print("PyInstaller安装完成")


def build_application(pack_mode='onefile'):
    """使用PyInstaller打包应用程序
    
    Args:
        pack_mode: 打包模式，'onefile'为单文件模式，'dir'为目录模式
    """
    print(f"开始打包应用程序（{pack_mode}模式）...")
    
    # 检查必要文件
    required_files = ['main.py', 'resources/SecRandom.ico', 'LICENSE']
    for file in required_files:
        if not os.path.exists(file):
            print(f"错误: 缺少必要文件 {file}")
            sys.exit(1)
    
    # 检查version_info.txt文件
    version_file = 'version_info.txt'
    if not os.path.exists(version_file):
        print(f"警告: {version_file} 不存在，将跳过版本信息")
        version_option = ''
    else:
        version_option = f'--version-file={version_file}'
    
    # 构建PyInstaller命令基础参数
    cmd = [
        'pyinstaller', 'main.py',
        '-w',  # 无控制台窗口
        '-i', './resources/SecRandom.ico',  # 图标
        '-n', 'SecRandom',  # 应用程序名称
        '--add-data', './app/resource:app/resource',
        '--add-data', 'LICENSE:.',
        '--hidden-import=psutil._psutil_windows',
        '--hidden-import=pandas._libs.interval',
        '--hidden-import=pandas._libs.ops',
        '--hidden-import=pandas._libs.tslibs',
        '--hidden-import=pandas._libs.lib',
        '--hidden-import=pandas._libs.testing',
        '--hidden-import=pandas._libs.window',
        '--hidden-import=pandas._libs.missing',
        '--hidden-import=pandas._libs.hashtable',
        '--hidden-import=pandas._libs.skiplist',
        '--hidden-import=pandas._libs.hashing',
        '--hidden-import=pandas._libs.writers',
        '--hidden-import=pandas._libs.json',
        '--hidden-import=pandas._libs.parsers',
        '--hidden-import=pandas._libs.properties',
        '--hidden-import=pandas._libs.reshape',
        '--hidden-import=pandas._libs.sparse',
        '--hidden-import=pandas._libs.groupby',
        '--hidden-import=pandas._libs.join',
        '--hidden-import=pandas._libs.reduction',
        '--hidden-import=pandas._libs.algos',
        '--hidden-import=pandas._libs.ops_dispatch',
        '--hidden-import=pandas._libs.arrays',
        '--hidden-import=pandas._libs.internals',
        '--hidden-import=pandas._libs.tslibs.base',
        '--hidden-import=pandas._libs.tslibs.dtypes',
        '--hidden-import=pandas._libs.tslibs.conversion',
        '--hidden-import=pandas._libs.tslibs.nattype',
        '--hidden-import=pandas._libs.tslibs.np_datetime',
        '--hidden-import=pandas._libs.tslibs.period',
        '--hidden-import=pandas._libs.tslibs.strptime',
        '--hidden-import=pandas._libs.tslibs.timestamps',
        '--hidden-import=pandas._libs.tslibs.timedeltas',
        '--hidden-import=pandas._libs.tslibs.timezones',
        '--hidden-import=pandas._libs.tslibs.tzconversion',
        '--hidden-import=pandas._libs.tslibs.vectorized',
        '--hidden-import=numpy',
        '--hidden-import=numpy.core',
        '--hidden-import=numpy.core._dtype_ctypes',
        '--hidden-import=numpy.core._exceptions',
        '--hidden-import=numpy.core._internal',
        '--hidden-import=numpy.core._methods',
        '--hidden-import=numpy.core._string_helpers',
        '--hidden-import=numpy.core._type_aliases',
        '--hidden-import=numpy.core._ufunc_config',
        '--hidden-import=numpy.linalg',
        '--hidden-import=numpy.linalg.linalg',
        '--hidden-import=numpy.linalg._umath_linalg',
        '--hidden-import=numpy.fft',
        '--hidden-import=numpy.fft._pocketfft_internal',
        '--hidden-import=numpy.random',
        '--hidden-import=numpy.random.bit_generator',
        '--hidden-import=numpy.random._common',
        '--hidden-import=numpy.random._pickle',
        '--hidden-import=numpy.random._mt19937',
        '--hidden-import=numpy.random._philox',
        '--hidden-import=numpy.random._pcg64',
        '--hidden-import=numpy.random._sfc64',
        '--hidden-import=numpy.random._generator',
        '--hidden-import=numpy.random._bounded_integers',
        '--hidden-import=numpy.random.mtrand',
        '--hidden-import=numpy.lib',
        '--hidden-import=numpy.lib.scimath',
        '--hidden-import=numpy.lib.stride_tricks',
        '--hidden-import=numpy.core._multiarray_umath',
        '--hidden-import=numpy.core._multiarray_tests',
        '--hidden-import=numpy.polynomial',
        '--hidden-import=numpy.testing',
        '--hidden-import=numpy.distutils',
        '--hidden-import=numpy.f2py',
        '--hidden-import=numpy.ma',
        '--hidden-import=numpy.matrixlib',
        '--hidden-import=numpy.compat',
        '--hidden-import=numpy.ctypeslib',
        '--collect-data=pandas',
        '--collect-data=numpy',
        '--collect-submodules=numpy',
        '--collect-submodules=pandas'
    ]
    
    # 根据打包模式添加不同参数
    if pack_mode == 'onefile':
        cmd.append('-F')  # 单文件模式
    elif pack_mode == 'dir':
        cmd.append('-D')  # 目录模式
    else:
        print(f"错误: 不支持的打包模式 {pack_mode}")
        sys.exit(1)
    
    if version_option:
        cmd.append(version_option)
    
    # 在Windows上使用PowerShell语法
    if platform.system() == 'Windows':
        # 正确处理PowerShell命令格式，只对包含空格的参数加引号
        cmd_parts = []
        for item in cmd:
            if ' ' in item:
                cmd_parts.append(f'"{item}"')
            else:
                cmd_parts.append(item)
        cmd_str = ' '.join(cmd_parts)
    else:
        cmd_str = ' '.join(cmd)
    
    run_command(cmd_str)
    print(f"应用程序打包完成（{pack_mode}模式）")


def prepare_distribution(pack_mode='onefile'):
    """准备分发文件
    
    Args:
        pack_mode: 打包模式，'onefile'为单文件模式，'dir'为目录模式
    """
    print(f"准备分发文件（{pack_mode}模式）...")
    
    # 创建zip_dist目录
    zip_dist_dir = 'zip_dist/SecRandom'
    if os.path.exists('zip_dist'):
        shutil.rmtree('zip_dist')
    
    os.makedirs(zip_dist_dir, exist_ok=True)
    
    # 根据打包模式复制不同的文件
    if pack_mode == 'onefile':
        # 单文件模式：复制SecRandom.exe可执行文件
        if os.path.exists('dist/SecRandom.exe'):
            shutil.copy2('dist/SecRandom.exe', os.path.join(zip_dist_dir, 'SecRandom.exe'))
    elif pack_mode == 'dir':
        # 目录模式：复制SecRandom文件夹内容
        if os.path.exists('dist/SecRandom'):
            for item in os.listdir('dist/SecRandom'):
                src = os.path.join('dist/SecRandom', item)
                dst = os.path.join(zip_dist_dir, item)
                if os.path.isdir(src):
                    shutil.copytree(src, dst)
                else:
                    shutil.copy2(src, dst)
    else:
        print(f"错误: 不支持的打包模式 {pack_mode}")
        return
    
    # 复制app/resource文件夹
    if os.path.exists('app/resource'):
        resource_dst = os.path.join(zip_dist_dir, 'app', 'resource')
        os.makedirs(os.path.dirname(resource_dst), exist_ok=True)
        shutil.copytree('app/resource', resource_dst)
    
    # 复制LICENSE文件
    if os.path.exists('LICENSE'):
        shutil.copy2('LICENSE', os.path.join(zip_dist_dir, 'LICENSE'))
    
    print(f"分发文件准备完成（{pack_mode}模式）")


def create_zip_archive(pack_mode='onefile'):
    """创建ZIP压缩包
    
    Args:
        pack_mode: 打包模式，'onefile'为单文件模式，'dir'为目录模式
    """
    print(f"创建ZIP压缩包（{pack_mode}模式）...")
    
    # 创建zip目录
    os.makedirs('zip', exist_ok=True)
    
    # 获取版本信息
    version = "latest"
    if os.path.exists('version_info.txt'):
        try:
            with open('version_info.txt', 'r', encoding='utf-8') as f:
                for line in f:
                    if line.startswith('VSVersionInfo('):
                        # 简单提取版本信息
                        import re
                        version_match = re.search(r'version=\((\d+),\s*(\d+),\s*(\d+),\s*(\d+)\)', line)
                        if version_match:
                            version = f"v{version_match.group(1)}.{version_match.group(2)}.{version_match.group(3)}.{version_match.group(4)}"
                            break
        except Exception as e:
            print(f"读取版本信息失败: {e}")
    
    # 构建ZIP文件名
    arch = platform.machine().lower()
    if arch == 'amd64':
        arch = 'x64'
    elif arch == 'x86':
        arch = 'x86'
    
    # 添加打包模式到文件名
    pack_mode_name = 'onefile' if pack_mode == 'onefile' else 'dir'
    zip_name = f"SecRandom-Windows-{version}-{arch}-{pack_mode_name}.zip"
    zip_path = os.path.join('zip', zip_name)
    
    # 创建ZIP文件
    import zipfile
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk('zip_dist/SecRandom'):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, 'zip_dist/SecRandom')
                zipf.write(file_path, arcname)
    
    print(f"ZIP压缩包创建完成: {zip_path}")


def cleanup_build_files():
    """清理构建文件（不包括zip目录）"""
    print("清理构建文件...")
    
    # 清理PyInstaller生成的文件（不包括zip目录）
    cleanup_items = ['build', 'dist', 'zip_dist', 'SecRandom.spec']
    for item in cleanup_items:
        if os.path.exists(item):
            if os.path.isdir(item):
                safe_remove_directory(item)
            else:
                try:
                    os.remove(item)
                    print(f"删除文件: {item}")
                except OSError as e:
                    print(f"删除文件失败 {item}: {e}")
    
    print("构建文件清理完成")


def cleanup():
    """清理临时文件"""
    print("清理临时文件...")
    
    # 清理PyInstaller生成的文件
    cleanup_items = ['build', 'dist', 'zip_dist', 'zip', 'SecRandom.spec']
    for item in cleanup_items:
        if os.path.exists(item):
            if os.path.isdir(item):
                safe_remove_directory(item)
            else:
                try:
                    os.remove(item)
                    print(f"删除文件: {item}")
                except OSError as e:
                    print(f"删除文件失败 {item}: {e}")
    
    print("清理完成")


def main():
    """主函数"""
    print("=== SecRandom 本地打包脚本 ===")
    print(f"操作系统: {platform.system()} {platform.release()}")
    print(f"架构: {platform.machine()}")
    print(f"Python版本: {sys.version}")
    print()
    
    # 检查uv是否安装
    if not check_uv_installed():
        print("请先安装uv后再运行此脚本")
        sys.exit(1)
    
    # 选择打包模式
    print("请选择打包模式:")
    print("1. 单文件模式 (onefile) - 体积小，适合分发")
    print("2. 目录模式 (dir) - 体积大，但兼容性更好")
    print("3. 两种模式都生成")
    
    while True:
        try:
            choice = input("请输入选择 (1/2/3): ").strip()
            if choice == '1':
                pack_modes = ['onefile']
                break
            elif choice == '2':
                pack_modes = ['dir']
                break
            elif choice == '3':
                pack_modes = ['onefile', 'dir']
                break
            else:
                print("无效选择，请重新输入")
        except KeyboardInterrupt:
            print("\n用户中断操作")
            sys.exit(1)
    
    try:
        # 1. 创建虚拟环境
        create_virtual_environment()
        
        # 2. 安装依赖
        install_dependencies()
        
        # 3. 安装PyInstaller
        install_pyinstaller()
        
        # 4. 为每种模式打包应用程序
        for pack_mode in pack_modes:
            print(f"\n=== 开始{pack_mode}模式打包 ===")
            
            # 清理之前的构建文件
            cleanup_build_files()
            
            # 4.1 打包应用程序
            build_application(pack_mode)
            
            # 4.2 准备分发文件
            prepare_distribution(pack_mode)
            
            # 4.3 创建ZIP压缩包
            create_zip_archive(pack_mode)
            
            print(f"\n=== {pack_mode}模式打包完成 ===")
            if pack_mode == 'onefile':
                print(f"可执行文件: {os.path.abspath('dist/SecRandom.exe')}")
            else:
                print(f"可执行文件: {os.path.abspath('dist/SecRandom/SecRandom.exe')}")
            print(f"ZIP压缩包: {os.path.abspath(f'zip/SecRandom-Windows-*-{pack_mode}.zip')}")
        
        print("\n=== 所有打包完成 ===")
        
    except KeyboardInterrupt:
        print("\n用户中断打包过程")
    except Exception as e:
        print(f"\n打包过程中发生错误: {e}")
        sys.exit(1)
    finally:
        # 询问是否清理临时文件
        try:
            response = input("\n是否清理临时文件? (y/N): ").strip().lower()
            if response == 'y':
                cleanup()
        except KeyboardInterrupt:
            pass


if __name__ == '__main__':
    main()