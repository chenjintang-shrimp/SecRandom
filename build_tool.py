#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SecRandom 应用程序打包工具
此工具用于在不同Windows平台上打包SecRandom应用程序
"""

import os
import sys
import subprocess
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import platform
import re
from pathlib import Path


class BuildApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SecRandom 打包工具")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # 设置应用图标
        try:
            if os.path.exists("./resources/secrandom-icon-paper.ico"):
                self.root.iconbitmap("./resources/secrandom-icon-paper.ico")
        except:
            pass
        
        # 创建主框架和滚动条
        self.canvas = tk.Canvas(self.root)
        self.scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.canvas.yview)
        self.main_frame = ttk.Frame(self.canvas, padding="10")
        
        # 配置滚动
        self.canvas.configure(yscrollcommand=self.scrollbar.set, yscrollincrement=20)  # 设置滚动增量
        self.canvas_frame = self.canvas.create_window((0, 0), window=self.main_frame, anchor="nw")
        
        # 绑定事件
        self.main_frame.bind("<Configure>", self.on_frame_configure)
        self.canvas.bind("<Configure>", self.on_canvas_configure)
        # 绑定鼠标滚轮事件到整个窗口
        self.root.bind("<MouseWheel>", self.on_mousewheel)
        self.root.bind("<Button-4>", self.on_mousewheel)  # Linux上向上滚动
        self.root.bind("<Button-5>", self.on_mousewheel)  # Linux上向下滚动
        
        # 布局
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # 创建标题
        title_label = ttk.Label(
            self.main_frame, 
            text="SecRandom 应用程序打包工具", 
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=(0, 10))
        
        # 创建说明文本
        info_text = "注意：此工具需要在克隆仓库后使用，确保所有依赖文件都存在。"
        info_label = ttk.Label(self.main_frame, text=info_text, foreground="blue")
        info_label.pack(pady=(0, 10))
        
        # 创建平台选择框架
        platform_frame = ttk.LabelFrame(self.main_frame, text="选择目标平台", padding="10")
        platform_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 创建平台选择变量
        self.os_version_var = tk.StringVar(value="win10_plus")
        self.architecture_var = tk.StringVar(value="x64")
        self.pip_mirror_var = tk.StringVar(value="https://pypi.tuna.tsinghua.edu.cn/simple")
        
        # 创建操作系统版本选择框架
        os_frame = ttk.LabelFrame(platform_frame, text="操作系统版本", padding="5")
        os_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Win10及以上版本选项
        self.win10_plus_radio = ttk.Radiobutton(
            os_frame, 
            text="Windows 10 及以上版本", 
            variable=self.os_version_var, 
            value="win10_plus"
        )
        self.win10_plus_radio.pack(anchor=tk.W, pady=2)
        
        # Win7到Win10版本选项
        self.win7_to_win10_radio = ttk.Radiobutton(
            os_frame, 
            text="Windows 7 到 Windows 10 (不包括Win10)", 
            variable=self.os_version_var, 
            value="win7_to_win10"
        )
        self.win7_to_win10_radio.pack(anchor=tk.W, pady=2)
        
        # 创建架构选择框架
        arch_frame = ttk.LabelFrame(platform_frame, text="处理器架构", padding="5")
        arch_frame.pack(fill=tk.X, pady=(0, 5))
        
        # x64选项
        self.x64_radio = ttk.Radiobutton(
            arch_frame, 
            text="x64 (64位)", 
            variable=self.architecture_var, 
            value="x64"
        )
        self.x64_radio.pack(anchor=tk.W, pady=2)
        
        # x86选项
        self.x86_radio = ttk.Radiobutton(
            arch_frame, 
            text="x86 (32位)", 
            variable=self.architecture_var, 
            value="x86"
        )
        self.x86_radio.pack(anchor=tk.W, pady=2)
        
        # 创建Python版本信息标签
        self.python_version_label = ttk.Label(
            platform_frame, 
            text="", 
            foreground="green"
        )
        self.python_version_label.pack(anchor=tk.W, pady=5)
        
        # 创建pip镜像源选择框架
        mirror_frame = ttk.LabelFrame(self.main_frame, text="pip镜像源设置", padding="10")
        mirror_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 创建镜像源选择变量
        mirror_options = [
            ("清华大学", "https://pypi.tuna.tsinghua.edu.cn/simple"),
            ("默认源", "default"),
            ("阿里云", "https://mirrors.aliyun.com/pypi/simple"),
            ("中国科技大学", "https://pypi.mirrors.ustc.edu.cn/simple"),
            ("豆瓣", "https://pypi.douban.com/simple"),
            ("华为云", "https://mirrors.huaweicloud.com/repository/pypi/simple")
        ]
        
        # 创建镜像源选择单选按钮
        for text, value in mirror_options:
            radio = ttk.Radiobutton(
                mirror_frame, 
                text=text, 
                variable=self.pip_mirror_var, 
                value=value
            )
            radio.pack(anchor=tk.W, pady=2)
        
        # 创建操作按钮框架
        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 创建检查环境按钮
        self.check_env_button = ttk.Button(
            button_frame, 
            text="检查环境", 
            command=self.check_environment
        )
        self.check_env_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # 创建创建虚拟环境按钮
        self.create_venv_button = ttk.Button(
            button_frame, 
            text="创建虚拟环境", 
            command=self.create_virtual_environment
        )
        self.create_venv_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # 创建安装依赖按钮
        self.install_deps_button = ttk.Button(
            button_frame, 
            text="安装依赖", 
            command=self.install_dependencies
        )
        self.install_deps_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # 创建开始打包按钮
        self.build_button = ttk.Button(
            button_frame, 
            text="开始打包", 
            command=self.start_build
        )
        self.build_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # 创建一键执行按钮
        self.one_click_button = ttk.Button(
            button_frame, 
            text="一键执行", 
            command=self.one_click_execute
        )
        self.one_click_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # 创建日志显示区域
        log_frame = ttk.LabelFrame(self.main_frame, text="打包日志", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, height=15)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # 初始化状态变量
        self.venv_created = False
        self.deps_installed = False
        self.env_checked = False
        
        # 初始检查
        self.log("欢迎使用 SecRandom 打包工具！")
        self.log("请先检查环境，然后按照步骤操作。")
        
        # 检查当前Python版本并设置选项状态
        self.check_python_version_and_set_options()
        
    def on_frame_configure(self, event=None):
        """当框架大小改变时更新滚动区域"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        # 确保滚动条在需要时显示
        bbox = self.canvas.bbox("all")
        if bbox:
            canvas_height = self.canvas.winfo_height()
            content_height = bbox[3] - bbox[1]
            if content_height > canvas_height:
                self.scrollbar.pack(side="right", fill="y")
            else:
                self.scrollbar.pack_forget()
        
    def on_canvas_configure(self, event=None):
        """当画布大小改变时调整框架宽度"""
        # 获取画布宽度
        canvas_width = event.width
        # 设置框架宽度为画布宽度
        self.canvas.itemconfig(self.canvas_frame, width=canvas_width)
        
    def on_mousewheel(self, event):
        """处理鼠标滚轮事件"""
        # 根据事件类型确定滚动方向和步长
        if event.num == 4:  # Linux上向上滚动
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5:  # Linux上向下滚动
            self.canvas.yview_scroll(1, "units")
        else:  # Windows系统
            # Windows系统上滚轮事件的delta值是120的倍数
            # 向上滚动是正值，向下滚动是负值
            # 增加滚动步长，使滚动更明显
            scroll_units = int(-1*(event.delta/60))  # 增加滚动步长
            self.canvas.yview_scroll(scroll_units, "units")
            
            # 确保画布获得焦点，以便滚轮事件能够正常工作
            self.canvas.focus_set()
        
    def log(self, message):
        """添加日志消息"""
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        
    def check_python_version_and_set_options(self):
        """检查Python版本并根据版本设置选项状态"""
        python_version = sys.version_info
        version_str = f"{python_version.major}.{python_version.minor}.{python_version.micro}"
        self.log(f"当前Python版本: {version_str}")
        
        # 更新Python版本标签
        self.python_version_label.config(text=f"当前Python版本: {version_str}")
        
        # 检查Python版本是否为3.8.10
        is_python_3_8_10 = (python_version.major == 3 and 
                          python_version.minor == 8 and 
                          python_version.micro == 10)
        
        # 检查Python版本是否大于3.8.10
        is_python_above_3_8_10 = (python_version.major > 3 or 
                                  (python_version.major == 3 and python_version.minor > 8) or
                                  (python_version.major == 3 and python_version.minor == 8 and python_version.micro > 10))
        
        if is_python_3_8_10:
            # Python 3.8.10可以选择任意选项
            self.log("Python 3.8.10：可以选择任意目标平台")
            self.win10_plus_radio.config(state="normal")
            self.win7_to_win10_radio.config(state="normal")
            self.x64_radio.config(state="normal")
            self.x86_radio.config(state="normal")
            self.log(f"检测到Python {version_str}，可以选择所有平台和架构选项")
        elif is_python_above_3_8_10:
            # Python 3.8.10以上版本只能选择Win10及以上版本
            self.log("Python 3.8.10以上版本：只能选择Windows 10及以上版本")
            self.win10_plus_radio.config(state="normal")
            self.win7_to_win10_radio.config(state="disabled")
            self.x64_radio.config(state="normal")
            self.x86_radio.config(state="normal")
            # 自动选择Win10及以上版本
            self.os_version_var.set("win10_plus")
            self.log(f"检测到Python {version_str}，只能选择Windows 10及以上版本")
        else:
            # Python 3.8.10以下版本可以选择任意选项
            self.log("Python 3.8.10以下版本：可以选择任意目标平台")
            self.win10_plus_radio.config(state="normal")
            self.win7_to_win10_radio.config(state="normal")
            self.x64_radio.config(state="normal")
            self.x86_radio.config(state="normal")
            self.log(f"检测到Python {version_str}，可以选择所有平台和架构选项")
        
    def run_command(self, command, cwd=None, callback=None):
        """异步运行命令并通过回调函数返回输出"""
        self.log(f"执行命令: {command}")
        
        def execute_command():
            try:
                # 使用subprocess运行命令
                process = subprocess.Popen(
                    command,
                    shell=True,
                    cwd=cwd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                    universal_newlines=True
                )
                
                # 实时读取输出
                output = ""
                for line in process.stdout:
                    output += line
                    # 使用root.after确保在主线程中更新UI
                    self.root.after(0, lambda l=line.strip(): self.log(l))
                
                # 等待命令完成
                process.wait()
                
                # 使用root.after确保在主线程中调用回调
                if callback:
                    self.root.after(0, lambda: callback(output, process.returncode))
                    
                return output, process.returncode
            except Exception as e:
                error_msg = f"执行命令时出错: {str(e)}"
                self.root.after(0, lambda: self.log(error_msg))
                if callback:
                    self.root.after(0, lambda: callback("", -1))
                return "", -1
        
        # 在新线程中执行命令
        thread = threading.Thread(target=execute_command)
        thread.daemon = True
        thread.start()
        return thread
            
    def check_environment(self):
        """检查环境"""
        self.log("开始检查环境...")
        
        # 检查Python版本
        python_version = sys.version_info
        self.log(f"Python版本: {python_version.major}.{python_version.minor}.{python_version.micro}")
        
        # 检查pip是否可用
        try:
            subprocess.run([sys.executable, "-m", "pip", "--version"], check=True, capture_output=True)
            self.log("pip 可用")
        except:
            self.log("错误: pip 不可用")
            return False
            
        # 检查必要文件是否存在
        required_files = [
            "main.py",
            "requirements-windows.txt",
            "requirements-windows-win7_x64_x86.txt",
            "version_info.txt",
            "LICENSE",
            "./resources/secrandom-icon-paper.ico"
        ]
        
        missing_files = []
        for file in required_files:
            if not os.path.exists(file):
                missing_files.append(file)
                
        if missing_files:
            self.log(f"错误: 缺少必要文件: {', '.join(missing_files)}")
            return False
        else:
            self.log("所有必要文件存在")
            
        # 检查虚拟环境是否已存在
        venv_path = os.path.join(os.getcwd(), "venv")
        if os.path.exists(venv_path):
            self.log("虚拟环境已存在")
            self.venv_created = True
        else:
            self.log("虚拟环境不存在")
            self.venv_created = False
            
        self.env_checked = True
        self.log("环境检查完成")
        return True
        
    def create_virtual_environment(self, callback=None):
        """创建虚拟环境"""
        if not self.env_checked:
            self.log("请先检查环境")
            if callback:
                callback(False)
            return
            
        # 如果虚拟环境已存在，询问用户是否要重新创建
        venv_path = os.path.join(os.getcwd(), "venv")
        if os.path.exists(venv_path):
            result = messagebox.askyesno("确认", "虚拟环境已存在，是否要重新创建？\n这将删除现有的虚拟环境。")
            if result:
                self.log("删除现有虚拟环境...")
                try:
                    import shutil
                    shutil.rmtree(venv_path)
                    self.log("虚拟环境删除成功")
                except Exception as e:
                    self.log(f"删除虚拟环境失败: {str(e)}")
                    if callback:
                        callback(False)
                    return
            else:
                self.log("使用现有虚拟环境")
                self.venv_created = True
                if callback:
                    callback(True)
                return
            
        self.log("开始创建虚拟环境...")
        
        # 创建虚拟环境
        command = f"{sys.executable} -m venv {venv_path}"
        
        # 定义回调函数处理虚拟环境创建完成后的操作
        def venv_created_callback(output, return_code):
            if return_code == 0:
                self.log("虚拟环境创建成功")
                self.venv_created = True
                
                # 在虚拟环境中安装pip
                self.log("在虚拟环境中安装pip...")
                if platform.system() == "Windows":
                    python_path = os.path.join(venv_path, "Scripts", "python.exe")
                else:
                    python_path = os.path.join(venv_path, "bin", "python")
                    
                # 使用get-pip.py脚本安装pip
                import tempfile
                import urllib.request
                
                try:
                    # 下载get-pip.py
                    get_pip_url = "https://bootstrap.pypa.io/get-pip.py"
                    temp_dir = tempfile.mkdtemp()
                    get_pip_path = os.path.join(temp_dir, "get-pip.py")
                    
                    self.log("下载get-pip.py...")
                    urllib.request.urlretrieve(get_pip_url, get_pip_path)
                    
                    # 定义回调函数处理pip安装完成后的操作
                    def pip_installed_callback(output, return_code):
                        if return_code == 0:
                            self.log("pip安装成功")
                            
                            # 配置pip镜像源
                            mirror_url = self.pip_mirror_var.get()
                            if mirror_url != "default":
                                self.log(f"配置pip镜像源: {mirror_url}")
                                config_cmd = f"{python_path} -m pip config set global.index-url {mirror_url}"
                                
                                # 定义回调函数处理镜像源配置完成后的操作
                                def mirror_configured_callback(output, return_code):
                                    if return_code == 0:
                                        self.log("pip镜像源配置成功")
                                    else:
                                        self.log("pip镜像源配置失败，但pip已安装")
                                    
                                    # 调用外部回调函数
                                    if callback:
                                        callback(True)
                                
                                self.run_command(config_cmd, callback=mirror_configured_callback)
                            else:
                                self.log("使用默认pip源")
                                # 调用外部回调函数
                                if callback:
                                    callback(True)
                        else:
                            self.log("pip安装失败，但虚拟环境已创建")
                            # 调用外部回调函数
                            if callback:
                                callback(False)
                            
                        # 清理临时文件
                        try:
                            os.remove(get_pip_path)
                            os.rmdir(temp_dir)
                        except:
                            pass
                            
                    # 安装pip
                    command = f"{python_path} {get_pip_path}"
                    self.run_command(command, callback=pip_installed_callback)
                    
                except Exception as e:
                    self.log(f"安装pip时出现异常: {str(e)}")
                    if callback:
                        callback(False)
            else:
                self.log("虚拟环境创建失败")
                if callback:
                    callback(False)
        
        # 异步执行创建虚拟环境命令
        self.run_command(command, callback=venv_created_callback)
            
    def install_dependencies(self, callback=None):
        """安装依赖"""
        if not self.venv_created:
            self.log("请先创建虚拟环境")
            if callback:
                callback(False)
            return
            
        self.log("开始安装依赖...")
        
        # 确定要使用的requirements文件
        if self.os_version_var.get() == "win10_plus":
            requirements_file = "requirements-windows.txt"
        else:
            requirements_file = "requirements-windows-win7_x64_x86.txt"
            
        self.log(f"使用依赖文件: {requirements_file}")
        
        # 获取虚拟环境中的python路径
        python_path = os.path.join(os.getcwd(), "venv", "Scripts", "python.exe")
        
        # 检查pip是否可用
        self.log("检查pip是否可用...")
        check_pip_cmd = f"{python_path} -c \"import pip; print('pip可用')\""
        
        # 定义回调函数处理pip检查完成后的操作
        def pip_checked_callback(output, return_code):
            if return_code != 0:
                self.log("错误: 虚拟环境中的pip不可用或已损坏")
                result = messagebox.askyesno("错误", "虚拟环境中的pip不可用或已损坏。\n是否要重新创建虚拟环境？")
                if result:
                    # 重置虚拟环境状态
                    self.venv_created = False
                    self.env_checked = False
                    # 调用创建虚拟环境的方法，并传递回调函数
                    self.create_virtual_environment(callback=lambda success: self.install_dependencies(callback) if success else None)
                else:
                    self.log("用户选择不重新创建虚拟环境，无法继续安装依赖")
                    if callback:
                        callback(False)
                return
            
            # 尝试升级pip，但不强制要求成功
            try:
                self.log("尝试升级pip到最新版本...")
                # 使用python -m pip而不是直接使用pip.exe，避免文件锁定问题
                # 获取用户选择的镜像源
                mirror_url = self.pip_mirror_var.get()
                if mirror_url != "default":
                    upgrade_cmd = f"{python_path} -m pip install --upgrade pip -i {mirror_url}"
                    self.log(f"使用镜像源: {mirror_url}")
                else:
                    upgrade_cmd = f"{python_path} -m pip install --upgrade pip"
                    self.log("使用默认pip源")
                
                # 定义回调函数处理pip升级完成后的操作
                def pip_upgraded_callback(output, return_code):
                    if return_code == 0:
                        self.log("pip升级成功")
                    else:
                        self.log("pip升级失败，但继续尝试安装依赖")
                    
                    # 使用python -m pip而不是直接使用pip.exe，确保pip可用
                    # 获取用户选择的镜像源
                    mirror_url = self.pip_mirror_var.get()
                    if mirror_url != "default":
                        command = f"{python_path} -m pip install -r {requirements_file} -i {mirror_url}"
                        self.log(f"使用镜像源: {mirror_url}")
                    else:
                        command = f"{python_path} -m pip install -r {requirements_file}"
                        self.log("使用默认pip源")
                    
                    # 定义回调函数处理依赖安装完成后的操作
                    def deps_installed_callback(output, return_code):
                        if return_code == 0:
                            self.log("依赖安装成功")
                            self.deps_installed = True
                            if callback:
                                callback(True)
                        else:
                            self.log("依赖安装失败")
                            if callback:
                                callback(False)
                    
                    # 异步执行安装依赖命令
                    self.run_command(command, callback=deps_installed_callback)
                
                # 异步执行升级pip命令
                self.run_command(upgrade_cmd, callback=pip_upgraded_callback)
                
            except Exception as e:
                self.log(f"pip升级过程中出现异常: {str(e)}")
                if callback:
                    callback(False)
        
        # 异步执行检查pip命令
        self.run_command(check_pip_cmd, callback=pip_checked_callback)
            
    def start_build(self, callback=None):
        """开始打包"""
        if not self.venv_created:
            self.log("请先创建虚拟环境")
            if callback:
                callback(False)
            return
            
        if not self.deps_installed:
            self.log("请先安装依赖")
            if callback:
                callback(False)
            return
            
        # 在新线程中执行打包操作，避免界面卡死
        threading.Thread(target=lambda: self._build_app(callback)).start()
        
    def _build_app(self, callback=None):
        """实际执行打包操作"""
        self.log("开始打包应用程序...")
        
        # 获取选择的平台和架构
        os_version = self.os_version_var.get()
        architecture = self.architecture_var.get()
        
        # 获取虚拟环境中的python路径
        if platform.system() == "Windows":
            python_path = os.path.join(os.getcwd(), "venv", "Scripts", "python.exe")
            pyinstaller_path = os.path.join(os.getcwd(), "venv", "Scripts", "pyinstaller.exe")
        else:
            python_path = os.path.join(os.getcwd(), "venv", "bin", "python")
            pyinstaller_path = os.path.join(os.getcwd(), "venv", "bin", "pyinstaller")
            
        # 定义继续打包操作的函数
        def continue_build():
            # 确定要使用的requirements文件
            if os_version == "win7_to_win10":
                requirements_file = "requirements-windows-win7_x64_x86.txt"
            else:
                requirements_file = "requirements-windows.txt"
                
            self.log(f"使用依赖文件: {requirements_file}")
            
            # 从requirements文件中获取命令
            with open(requirements_file, "r", encoding="utf-8") as f:
                content = f.read()
                
            # 提取PyInstaller命令
            match = re.search(r"# pyinstaller (.+)", content)
            if match:
                pyinstaller_cmd = match.group(1)
                self.log("使用预定义的PyInstaller命令")
            else:
                # 如果没有找到预定义命令，使用默认命令
                pyinstaller_cmd = (
                    "main.py -w -D -i ./resources/secrandom-icon-paper.ico -n SecRandom "
                    "--add-data ./app/resource:app/resource --add-data LICENSE:. "
                    "--version-file=version_info.txt "
                    "--hidden-import=psutil._psutil_windows "
                    "--hidden-import=pandas._libs.interval "
                    "--hidden-import=pandas._libs.ops "
                    "--hidden-import=pandas._libs.tslibs "
                    "--hidden-import=pandas._libs.lib "
                    "--hidden-import=pandas._libs.testing "
                    "--hidden-import=pandas._libs.window "
                    "--hidden-import=pandas._libs.missing "
                    "--hidden-import=pandas._libs.hashtable "
                    "--hidden-import=pandas._libs.skiplist "
                    "--hidden-import=pandas._libs.hashing "
                    "--hidden-import=pandas._libs.writers "
                    "--hidden-import=pandas._libs.json "
                    "--hidden-import=pandas._libs.parsers "
                    "--hidden-import=pandas._libs.properties "
                    "--hidden-import=pandas._libs.reshape "
                    "--hidden-import=pandas._libs.sparse "
                    "--hidden-import=pandas._libs.groupby "
                    "--hidden-import=pandas._libs.join "
                    "--hidden-import=pandas._libs.reduction "
                    "--hidden-import=pandas._libs.algos "
                    "--hidden-import=pandas._libs.ops_dispatch "
                    "--hidden-import=pandas._libs.arrays "
                    "--hidden-import=pandas._libs.internals "
                    "--hidden-import=pandas._libs.tslibs.base "
                    "--hidden-import=pandas._libs.tslibs.dtypes "
                    "--hidden-import=pandas._libs.tslibs.conversion "
                    "--hidden-import=pandas._libs.tslibs.nattype "
                    "--hidden-import=pandas._libs.tslibs.np_datetime "
                    "--hidden-import=pandas._libs.tslibs.period "
                    "--hidden-import=pandas._libs.tslibs.strptime "
                    "--hidden-import=pandas._libs.tslibs.timestamps "
                    "--hidden-import=pandas._libs.tslibs.timedeltas "
                    "--hidden-import=pandas._libs.tslibs.timezones "
                    "--hidden-import=pandas._libs.tslibs.tzconversion "
                    "--hidden-import=pandas._libs.tslibs.vectorized "
                    "--hidden-import=numpy "
                    "--hidden-import=numpy.core._dtype_ctypes "
                    "--hidden-import=numpy.core._exceptions "
                    "--hidden-import=numpy.core._internal "
                    "--hidden-import=numpy.core._methods "
                    "--hidden-import=numpy.core._string_helpers "
                    "--hidden-import=numpy.core._type_aliases "
                    "--hidden-import=numpy.core._ufunc_config "
                    "--hidden-import=numpy.linalg "
                    "--hidden-import=numpy.linalg.linalg "
                    "--hidden-import=numpy.linalg._umath_linalg "
                    "--hidden-import=numpy.fft "
                    "--hidden-import=numpy.fft._pocketfft_internal "
                    "--hidden-import=numpy.random "
                    "--hidden-import=numpy.random.bit_generator "
                    "--hidden-import=numpy.random._common "
                    "--hidden-import=numpy.random._pickle "
                    "--hidden-import=numpy.random._mt19937 "
                    "--hidden-import=numpy.random._philox "
                    "--hidden-import=numpy.random._pcg64 "
                    "--hidden-import=numpy.random._sfc64 "
                    "--hidden-import=numpy.random._generator "
                    "--hidden-import=numpy.random._bounded_integers "
                    "--hidden-import=numpy.random.mtrand "
                    "--hidden-import=numpy.lib "
                    "--hidden-import=numpy.lib.scimath "
                    "--hidden-import=numpy.lib.stride_tricks "
                    "--hidden-import=numpy.core._multiarray_umath "
                    "--hidden-import=numpy.core._multiarray_tests "
                    "--hidden-import=numpy.polynomial "
                    "--hidden-import=numpy.testing "
                    "--hidden-import=numpy.distutils "
                    "--hidden-import=numpy.f2py "
                    "--hidden-import=numpy.ma "
                    "--hidden-import=numpy.matrixlib "
                    "--hidden-import=numpy.compat "
                    "--hidden-import=numpy.ctypeslib "
                    "--collect-data=pandas "
                    "--collect-data=numpy "
                    "--collect-submodules=numpy "
                    "--collect-submodules=pandas "
                    "--exclude-module=numpy.f2py.tests "
                    "--exclude-module=numpy.testing "
                    "--exclude-module=pandas.tests"
                )
                self.log("使用默认的PyInstaller命令")
                
            # 根据架构调整命令
            if architecture == "x86":
                # 对于x86架构，可能需要添加特定参数
                pyinstaller_cmd = pyinstaller_cmd.replace(" -D ", " -D --target-arch x86 ")
            else:
                # 对于x64架构，确保使用64位Python
                pyinstaller_cmd = pyinstaller_cmd.replace(" -D ", " -D --target-arch x64 ")
            
            # 执行PyInstaller命令
            command = f"{pyinstaller_path} {pyinstaller_cmd}"
            
            # 定义回调函数处理打包完成后的操作
            def build_completed_callback(output, return_code):
                if return_code == 0:
                    # 根据架构重命名输出目录
                    output_dir = f"dist/SecRandom_{os_version}_{architecture}"
                    if os.path.exists("dist/SecRandom"):
                        if os.path.exists(output_dir):
                            import shutil
                            shutil.rmtree(output_dir)
                        os.rename("dist/SecRandom", output_dir)
                        self.log(f"打包成功！输出目录: {output_dir}")
                    else:
                        self.log("打包成功！但未找到输出目录")
                    self.root.after(0, lambda: messagebox.showinfo("成功", "应用程序打包成功！"))
                    if callback:
                        callback(True)
                else:
                    self.log("打包失败")
                    self.root.after(0, lambda: messagebox.showerror("失败", "应用程序打包失败！"))
                    if callback:
                        callback(False)
            
            # 异步执行PyInstaller命令
            self.run_command(command, callback=build_completed_callback)
            
        # 检查pyinstaller是否已安装
        if not os.path.exists(pyinstaller_path):
            self.log("PyInstaller未安装，正在安装...")
            # 获取用户选择的镜像源
            mirror_url = self.pip_mirror_var.get()
            if mirror_url != "default":
                command = f"{python_path} -m pip install pyinstaller -i {mirror_url}"
                self.log(f"使用镜像源: {mirror_url}")
            else:
                command = f"{python_path} -m pip install pyinstaller"
                self.log("使用默认pip源")
            
            # 定义回调函数处理PyInstaller安装完成后的操作
            def pyinstaller_installed_callback(output, return_code):
                if return_code != 0:
                    self.log("PyInstaller安装失败")
                    if callback:
                        callback(False)
                    return
                
                # 继续执行打包操作
                continue_build()
            
            # 异步执行安装PyInstaller命令
            self.run_command(command, callback=pyinstaller_installed_callback)
        else:
            # 继续执行打包操作
            continue_build()


    def one_click_execute(self):
        """一键执行所有步骤：检查环境、创建虚拟环境、安装依赖和开始打包"""
        self.log("开始一键执行所有步骤...")
        
        # 禁用所有按钮，防止重复操作
        self.check_env_button.config(state="disabled")
        self.create_venv_button.config(state="disabled")
        self.install_deps_button.config(state="disabled")
        self.build_button.config(state="disabled")
        self.one_click_button.config(state="disabled")
        
        # 定义环境检查完成后的回调函数
        def env_check_callback(success):
            if not success:
                self.log("环境检查失败，停止执行")
                self.enable_all_buttons()
                return
            
            self.log("环境检查完成，开始创建虚拟环境...")
            self.create_virtual_environment(venv_created_callback)
        
        # 定义虚拟环境创建完成后的回调函数
        def venv_created_callback(success):
            if not success:
                self.log("虚拟环境创建失败，停止执行")
                self.enable_all_buttons()
                return
            
            self.log("虚拟环境创建完成，开始安装依赖...")
            self.install_dependencies(deps_installed_callback)
        
        # 定义依赖安装完成后的回调函数
        def deps_installed_callback(success):
            if not success:
                self.log("依赖安装失败，停止执行")
                self.enable_all_buttons()
                return
            
            self.log("依赖安装完成，开始打包...")
            self.start_build(build_completed_callback)
        
        # 定义打包完成后的回调函数
        def build_completed_callback(output, return_code):
            success = return_code == 0
            if success:
                self.log("一键执行所有步骤完成！")
            else:
                self.log("打包失败，一键执行未完成")
            self.enable_all_buttons()
        
        # 开始执行第一步：检查环境
        self.check_environment()
        
        # 由于check_environment是同步的，我们需要直接调用下一步
        if self.env_checked:
            self.log("环境检查完成，开始创建虚拟环境...")
            self.create_virtual_environment(venv_created_callback)
        else:
            self.log("环境检查失败，停止执行")
            self.enable_all_buttons()
    
    def enable_all_buttons(self):
        """启用所有按钮"""
        self.check_env_button.config(state="normal")
        self.create_venv_button.config(state="normal")
        self.install_deps_button.config(state="normal")
        self.build_button.config(state="normal")
        self.one_click_button.config(state="normal")
            
def main():
    """主函数"""
    root = tk.Tk()
    app = BuildApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()