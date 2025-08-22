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
from app.common.path_utils import path_manager, open_file


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
    """使用PyInstaller打包应用程序（跨平台支持）
    
    Args:
        pack_mode: 打包模式，'onefile'为单文件模式，'dir'为目录模式
    """
    print(f"开始打包应用程序（{pack_mode}模式）...")
    
    system = platform.system()
    
    # 检查必要文件
    required_files = ['main.py', 'LICENSE']
    
    # 根据平台添加特定文件检查
    if system == 'Windows':
        required_files.append('resources/SecRandom.ico')
    elif system == 'Linux':
        # Linux可以使用PNG图标或没有图标
        icon_file = 'resources/SecRandom.png'
        if os.path.exists(icon_file):
            required_files.append(icon_file)
    
    for file in required_files:
        if not os.path.exists(file):
            print(f"错误: 缺少必要文件 {file}")
            sys.exit(1)
    
    # 检查version_info.txt文件
    version_file = path_manager.get_project_path('version_info.txt')
    if not os.path.exists(version_file):
        print(f"警告: version_info.txt 不存在，将跳过版本信息")
        version_option = ''
    else:
        version_option = f'--version-file={version_file}'
    
    # 构建PyInstaller命令基础参数
    cmd = [
        'pyinstaller', path_manager.get_project_path('main.py'),
        '-n', 'SecRandom',  # 应用程序名称
        '--add-data', f'{path_manager.get_resource_path()}:app/resource',
        '--add-data', f'{path_manager.get_project_path("LICENSE")}:.'
    ]
    
    # 根据平台添加特定参数
    if system == 'Windows':
        cmd.extend(['-w', '-i', path_manager.get_project_path('resources/SecRandom.ico')])  # 无控制台窗口，Windows图标
        cmd.extend(['--hidden-import=psutil._psutil_windows'])
    elif system == 'Linux':
        # Linux平台参数
        cmd.extend(['--hidden-import=psutil._psutil_linux'])
        # 如果有PNG图标，添加图标参数
        icon_path = path_manager.get_project_path('resources/SecRandom.png')
        if os.path.exists(icon_path):
            cmd.extend(['-i', icon_path])
        else:
            print("警告: 未找到Linux图标文件，将使用默认图标")
    else:
        # 其他平台默认参数
        cmd.append('-w')  # 无控制台窗口
    
    # 添加通用的hidden imports
    hidden_imports = [
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
    cmd.extend(hidden_imports)
    
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
    
    # 构建命令字符串
    if system == 'Windows':
        # Windows上使用PowerShell语法，正确处理空格
        cmd_parts = []
        for item in cmd:
            if ' ' in item:
                cmd_parts.append(f'"{item}"')
            else:
                cmd_parts.append(item)
        cmd_str = ' '.join(cmd_parts)
    else:
        # Linux/Unix系统直接连接
        cmd_str = ' '.join(cmd)
    
    run_command(cmd_str)
    print(f"应用程序打包完成（{pack_mode}模式）")


def prepare_distribution(pack_mode='onefile'):
    """准备分发文件（跨平台支持）
    
    Args:
        pack_mode: 打包模式，'onefile'为单文件模式，'dir'为目录模式
    """
    print(f"准备分发文件（{pack_mode}模式）...")
    
    system = platform.system()
    
    # 创建zip_dist目录
    zip_dist_dir = 'zip_dist/SecRandom'
    if os.path.exists('zip_dist'):
        shutil.rmtree('zip_dist')
    
    os.makedirs(zip_dist_dir, exist_ok=True)
    
    # 根据平台确定可执行文件名
    if system == 'Windows':
        executable_name = 'SecRandom.exe'
    elif system == 'Linux':
        executable_name = 'SecRandom'
    else:
        executable_name = 'SecRandom'
    
    # 根据打包模式复制不同的文件
    if pack_mode == 'onefile':
        # 单文件模式：复制可执行文件
        executable_path = os.path.join('dist', executable_name)
        if os.path.exists(executable_path):
            shutil.copy2(executable_path, os.path.join(zip_dist_dir, executable_name))
            print(f"复制可执行文件: {executable_path}")
        else:
            print(f"错误: 未找到可执行文件 {executable_path}")
            return
    elif pack_mode == 'dir':
        # 目录模式：复制SecRandom文件夹内容
        app_dir = 'dist/SecRandom'
        if os.path.exists(app_dir):
            for item in os.listdir(app_dir):
                src = os.path.join(app_dir, item)
                dst = os.path.join(zip_dist_dir, item)
                if os.path.isdir(src):
                    shutil.copytree(src, dst)
                else:
                    shutil.copy2(src, dst)
            print(f"复制应用程序目录: {app_dir}")
        else:
            print(f"错误: 未找到应用程序目录 {app_dir}")
            return
    else:
        print(f"错误: 不支持的打包模式 {pack_mode}")
        return
    
    # 复制app/resource文件夹
    app_dir = os.path.dirname(os.path.abspath(__file__))
    resource_src = os.path.join(app_dir, 'app', 'resource')
    if os.path.exists(resource_src):
        resource_dst = os.path.join(zip_dist_dir, 'app', 'resource')
        os.makedirs(os.path.dirname(resource_dst), exist_ok=True)
        shutil.copytree(resource_src, resource_dst)
    
    # 复制LICENSE文件
    license_path = path_manager.get_project_path('LICENSE')
    if os.path.exists(license_path):
        shutil.copy2(license_path, os.path.join(zip_dist_dir, 'LICENSE'))
    
    print(f"分发文件准备完成（{pack_mode}模式）")


def create_zip_archive(pack_mode='onefile'):
    """创建ZIP压缩包（跨平台支持）
    
    Args:
        pack_mode: 打包模式，'onefile'为单文件模式，'dir'为目录模式
    """
    print(f"创建ZIP压缩包（{pack_mode}模式）...")
    
    # 创建zip目录
    os.makedirs('zip', exist_ok=True)
    
    # 获取版本信息
    version = "latest"
    version_file = path_manager.get_project_path('version_info.txt')
    if os.path.exists(version_file):
        try:
            with open_file(version_file, 'r', encoding='utf-8') as f:
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
    
    # 获取系统信息
    system = platform.system()
    arch = platform.machine().lower()
    
    # 标准化架构名称
    if arch == 'amd64':
        arch = 'x64'
    elif arch == 'x86_64':
        arch = 'x64'
    elif arch == 'x86':
        arch = 'x86'
    elif arch == 'aarch64':
        arch = 'arm64'
    
    # 标准化系统名称
    if system == 'Windows':
        system_name = 'Windows'
    elif system == 'Linux':
        system_name = 'Linux'
    else:
        system_name = system
    
    # 添加打包模式到文件名
    pack_mode_name = 'onefile' if pack_mode == 'onefile' else 'dir'
    zip_name = f"SecRandom-{system_name}-{version}-{arch}-{pack_mode_name}.zip"
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
            
            # 根据平台显示可执行文件路径
            system = platform.system()
            if system == 'Windows':
                executable_name = 'SecRandom.exe'
            elif system == 'Linux':
                executable_name = 'SecRandom'
            else:
                executable_name = 'SecRandom'
            
            if pack_mode == 'onefile':
                executable_path = os.path.join('dist', executable_name)
                print(f"可执行文件: {os.path.abspath(executable_path)}")
            else:
                executable_path = os.path.join('dist', 'SecRandom', executable_name)
                print(f"可执行文件: {os.path.abspath(executable_path)}")
            
            # 显示ZIP压缩包路径
            system_name = 'Windows' if system == 'Windows' else 'Linux' if system == 'Linux' else system
            zip_pattern = f"zip/SecRandom-{system_name}-*-{pack_mode}.zip"
            print(f"ZIP压缩包: {os.path.abspath(zip_pattern)}")
        
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