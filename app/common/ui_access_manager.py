# ================================================== ✧*｡٩(ˊᗜˋ*)و✧*｡
# UIAccess权限管理模块 🔮
# ================================================== ✧*｡٩(ˊᗜˋ*)و✧*｡

"""
UIAccess权限管理模块

本模块实现了多种方式获取UIAccess权限的功能，可以让程序窗口获得更高的Z序，
比如高于任务管理器等，与屏幕键盘同层。用于解决制作屏幕标记/录制工具时窗口被遮挡的问题。

主要功能：
    1. 直接设置TokenUIAccess权限（推荐）
       - 通过SetTokenInformation API直接在当前进程令牌中设置TokenUIAccess权限
       - 可以绕过数字签名和指定安装路径的限制
       - 无需创建新进程，更加高效
    
    2. 通过System令牌创建新进程（备用方案）
       - 获取winlogon.exe的System令牌
       - 创建具有UIAccess权限的新进程并退出当前进程
       - 需要数字签名和受信任位置安装

使用方法：
    1. 在程序开头调用 UIAccessManager.prepare_for_ui_access()
    2. 如果返回 ERROR_SUCCESS，表示UIAccess权限获取成功
    3. 在窗口类中混入 UIAccessMixin 类，获得窗口置顶功能
    
注意事项：
    - 程序需要以管理员权限运行
    - 直接设置TokenUIAccess权限方法可以绕过数字签名和安装路径限制
    - System令牌方法需要数字签名和受信任位置安装（如Program Files）
    
效果对比：
    - 未启用UIAccess：窗口Z序低于任务管理器等系统工具
    - 启用UIAccess：窗口Z序高于任务管理器等系统工具
    
技术原理：
    - TokenUIAccess是进程令牌的一个属性，控制进程的UI访问级别
    - 通过SetTokenInformation API可以动态修改此属性
    - 启用后，进程的窗口将获得更高的Z序，能够显示在系统工具之上
"""

# ✨ 系统自带魔法道具 ✨
import ctypes
import os
import sys
from ctypes import wintypes
from loguru import logger

# 手动定义SECURITY_ATTRIBUTES结构体
class SECURITY_ATTRIBUTES(ctypes.Structure):
    _fields_ = [
        ("nLength", wintypes.DWORD),
        ("lpSecurityDescriptor", wintypes.LPVOID),
        ("bInheritHandle", wintypes.BOOL)
    ]

# 手动定义LUID结构体
class LUID(ctypes.Structure):
    _fields_ = [
        ("LowPart", wintypes.DWORD),
        ("HighPart", wintypes.LONG)
    ]

# 手动定义LUID_AND_ATTRIBUTES结构体
class LUID_AND_ATTRIBUTES(ctypes.Structure):
    _fields_ = [
        ("Luid", LUID),
        ("Attributes", wintypes.DWORD)
    ]

# 手动定义TOKEN_PRIVILEGES结构体
class TOKEN_PRIVILEGES(ctypes.Structure):
    _fields_ = [
        ("PrivilegeCount", wintypes.DWORD),
        ("Privileges", LUID_AND_ATTRIBUTES * 1)
    ]

# 手动定义CREATE_PROCESS结构体
class CREATE_PROCESS(ctypes.Structure):
    _fields_ = [
        ("cb", wintypes.DWORD),
        ("lpReserved", wintypes.LPWSTR),
        ("lpDesktop", wintypes.LPWSTR),
        ("lpTitle", wintypes.LPWSTR),
        ("dwX", wintypes.DWORD),
        ("dwY", wintypes.DWORD),
        ("dwXSize", wintypes.DWORD),
        ("dwYSize", wintypes.DWORD),
        ("dwXCountChars", wintypes.DWORD),
        ("dwYCountChars", wintypes.DWORD),
        ("dwFillAttribute", wintypes.DWORD),
        ("dwFlags", wintypes.DWORD),
        ("wShowWindow", wintypes.WORD),
        ("cbReserved2", wintypes.WORD),
        ("lpReserved2", wintypes.LPBYTE),
        ("hStdInput", wintypes.HANDLE),
        ("hStdOutput", wintypes.HANDLE),
        ("hStdError", wintypes.HANDLE)
    ]

# 手动定义STARTUPINFO结构体
class STARTUPINFO(ctypes.Structure):
    _fields_ = [
        ("cb", wintypes.DWORD),
        ("lpReserved", wintypes.LPWSTR),
        ("lpDesktop", wintypes.LPWSTR),
        ("lpTitle", wintypes.LPWSTR),
        ("dwX", wintypes.DWORD),
        ("dwY", wintypes.DWORD),
        ("dwXSize", wintypes.DWORD),
        ("dwYSize", wintypes.DWORD),
        ("dwXCountChars", wintypes.DWORD),
        ("dwYCountChars", wintypes.DWORD),
        ("dwFillAttribute", wintypes.DWORD),
        ("dwFlags", wintypes.DWORD),
        ("wShowWindow", wintypes.WORD),
        ("cbReserved2", wintypes.WORD),
        ("lpReserved2", wintypes.LPBYTE),
        ("hStdInput", wintypes.HANDLE),
        ("hStdOutput", wintypes.HANDLE),
        ("hStdError", wintypes.HANDLE)
    ]

# 手动定义PROCESS_INFORMATION结构体
class PROCESS_INFORMATION(ctypes.Structure):
    _fields_ = [
        ("hProcess", wintypes.HANDLE),
        ("hThread", wintypes.HANDLE),
        ("dwProcessId", wintypes.DWORD),
        ("dwThreadId", wintypes.DWORD)
    ]

# ================================================== (^・ω・^ )
# UIAccess权限管理类 ⭐
# ================================================== (^・ω・^ )

class UIAccessManager:
    """UIAccess权限管理器 - 通过System令牌获取UIAccess权限以解决窗口被系统工具遮挡的问题"""
    
    # Windows API常量定义
    TOKEN_QUERY = 0x0008
    TOKEN_DUPLICATE = 0x0002
    TOKEN_ASSIGN_PRIMARY = 0x0001
    TOKEN_ALL_ACCESS = 0xF01FF
    TOKEN_IMPERSONATE = 0x0004
    TOKEN_QUERY_SOURCE = 0x0010
    TOKEN_ADJUST_PRIVILEGES = 0x0020
    TOKEN_ADJUST_DEFAULT = 0x0080
    
    SE_DEBUG_NAME = "SeDebugPrivilege"
    SE_TCB_NAME = "SeTcbPrivilege"
    SE_IMPERSONATE_NAME = "SeImpersonatePrivilege"
    SE_ASSIGNPRIMARYTOKEN_NAME = "SeAssignPrimaryTokenPrivilege"
    
    ERROR_SUCCESS = 0
    ERROR_ACCESS_DENIED = 5
    ERROR_PRIVILEGE_NOT_HELD = 1314
    ERROR_NOT_FOUND = 1168
    ERROR_INVALID_PARAMETER = 87
    
    # Token信息类型
    TokenUIAccess = 26
    
    # 进程访问权限
    PROCESS_QUERY_INFORMATION = 0x0400
    PROCESS_VM_READ = 0x0010
    PROCESS_DUP_HANDLE = 0x0040
    
    # 创建进程标志
    CREATE_UNICODE_ENVIRONMENT = 0x00000400
    CREATE_NEW_CONSOLE = 0x00000010
    CREATE_NO_WINDOW = 0x08000000
    DETACHED_PROCESS = 0x00000008
    
    # Windows API函数原型定义
    _kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
    _advapi32 = ctypes.WinDLL('advapi32', use_last_error=True)
    _user32 = ctypes.WinDLL('user32', use_last_error=True)
    
    # 函数原型定义
    _OpenProcessToken = _advapi32.OpenProcessToken
    _OpenProcessToken.argtypes = [wintypes.HANDLE, wintypes.DWORD, ctypes.POINTER(wintypes.HANDLE)]
    _OpenProcessToken.restype = wintypes.BOOL
    
    _GetTokenInformation = _advapi32.GetTokenInformation
    _GetTokenInformation.argtypes = [wintypes.HANDLE, wintypes.DWORD, ctypes.c_void_p, wintypes.DWORD, ctypes.POINTER(wintypes.DWORD)]
    _GetTokenInformation.restype = wintypes.BOOL
    
    _DuplicateTokenEx = _advapi32.DuplicateTokenEx
    _DuplicateTokenEx.argtypes = [wintypes.HANDLE, wintypes.DWORD, ctypes.POINTER(SECURITY_ATTRIBUTES), wintypes.DWORD, wintypes.DWORD, ctypes.POINTER(wintypes.HANDLE)]
    _DuplicateTokenEx.restype = wintypes.BOOL
    
    _LookupPrivilegeValueW = _advapi32.LookupPrivilegeValueW
    _LookupPrivilegeValueW.argtypes = [wintypes.LPCWSTR, wintypes.LPCWSTR, ctypes.POINTER(LUID)]
    _LookupPrivilegeValueW.restype = wintypes.BOOL
    
    _AdjustTokenPrivileges = _advapi32.AdjustTokenPrivileges
    _AdjustTokenPrivileges.argtypes = [wintypes.HANDLE, wintypes.BOOL, ctypes.POINTER(TOKEN_PRIVILEGES), wintypes.DWORD, ctypes.POINTER(TOKEN_PRIVILEGES), ctypes.POINTER(wintypes.DWORD)]
    _AdjustTokenPrivileges.restype = wintypes.BOOL
    
    _CreateProcessWithTokenW = _advapi32.CreateProcessWithTokenW
    _CreateProcessWithTokenW.argtypes = [wintypes.HANDLE, wintypes.DWORD, wintypes.LPCWSTR, wintypes.LPCWSTR, wintypes.DWORD, ctypes.POINTER(CREATE_PROCESS), wintypes.LPCWSTR, ctypes.POINTER(STARTUPINFO), ctypes.POINTER(PROCESS_INFORMATION)]
    _CreateProcessWithTokenW.restype = wintypes.BOOL
    
    _SetTokenInformation = _advapi32.SetTokenInformation
    _SetTokenInformation.argtypes = [wintypes.HANDLE, wintypes.DWORD, ctypes.c_void_p, wintypes.DWORD]
    _SetTokenInformation.restype = wintypes.BOOL
    
    _OpenProcess = _kernel32.OpenProcess
    _OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    _OpenProcess.restype = wintypes.HANDLE
    
    _Process32First = None
    _Process32Next = None
    _CreateToolhelp32Snapshot = None
    _CloseHandle = _kernel32.CloseHandle
    _CloseHandle.argtypes = [wintypes.HANDLE]
    _CloseHandle.restype = wintypes.BOOL
    
    _GetLastError = _kernel32.GetLastError
    _GetLastError.argtypes = []
    _GetLastError.restype = wintypes.DWORD
    
    _GetCurrentProcess = _kernel32.GetCurrentProcess
    _GetCurrentProcess.argtypes = []
    _GetCurrentProcess.restype = wintypes.HANDLE
    
    _CloseHandle = _kernel32.CloseHandle
    _CloseHandle.argtypes = [wintypes.HANDLE]
    _CloseHandle.restype = wintypes.BOOL
    
    _GetLastError = _kernel32.GetLastError
    _GetLastError.argtypes = []
    _GetLastError.restype = wintypes.DWORD
    
    @staticmethod
    def prepare_for_ui_access():
        """通过System令牌获取UIAccess权限
        
        Returns:
            int: 错误代码，0表示成功
        """
        try:
            # 检查是否为Windows系统
            import platform
            if platform.system() != 'Windows':
                logger.info("非Windows系统，跳过UIAccess权限初始化")
                return UIAccessManager.ERROR_SUCCESS
            
            # 检查是否为管理员权限运行
            is_admin = ctypes.windll.shell32.IsUserAnAdmin()
            if not is_admin:
                logger.warning("程序未以管理员权限运行，无法获取UIAccess权限")
                return UIAccessManager.ERROR_ACCESS_DENIED
            
            # 检查是否已经具有UIAccess权限
            if UIAccessManager._has_ui_access():
                logger.info("已经具有UIAccess权限")
                return UIAccessManager.ERROR_SUCCESS
            
            # 首先尝试直接设置当前进程的TokenUIAccess权限
            result = UIAccessManager._set_current_process_ui_access()
            if result == UIAccessManager.ERROR_SUCCESS:
                logger.info("通过SetTokenInformation成功设置UIAccess权限")
                return result
            
            logger.info("直接设置UIAccess权限失败，尝试通过System令牌方式")
            
            # 初始化ToolHelp32 API
            UIAccessManager._init_toolhelp32()
            
            # 获取winlogon.exe进程令牌
            winlogon_token = UIAccessManager._get_winlogon_token()
            if not winlogon_token:
                logger.error("无法获取winlogon.exe进程令牌")
                return UIAccessManager.ERROR_NOT_FOUND
            
            try:
                # 创建具有UIAccess权限的新进程
                result = UIAccessManager._create_ui_access_process(winlogon_token)
                return result
                
            finally:
                UIAccessManager._CloseHandle(winlogon_token)
                
        except Exception as e:
            logger.error(f"UIAccess权限准备过程中发生异常: {e}")
            return UIAccessManager._GetLastError() if hasattr(UIAccessManager, '_GetLastError') else -1
    
    @staticmethod
    def _enable_privilege(h_token, privilege_name):
        """启用指定权限
        
        Args:
            h_token: 令牌句柄
            privilege_name: 权限名称
            
        Returns:
            bool: 是否成功启用权限
        """
        try:
            # 查找权限值
            luid = LUID()
            if not UIAccessManager._LookupPrivilegeValueW(None, privilege_name, ctypes.byref(luid)):
                return False
            
            # 设置权限状态
            privileges = TOKEN_PRIVILEGES()
            privileges.PrivilegeCount = 1
            privileges.Privileges[0].Luid = luid
            privileges.Privileges[0].Attributes = 0x00000002  # SE_PRIVILEGE_ENABLED
            
            # 调整权限
            if not UIAccessManager._AdjustTokenPrivileges(h_token, False, ctypes.byref(privileges), 0, None, None):
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"启用权限 {privilege_name} 时发生异常: {e}")
            return False
    
    @staticmethod
    def _has_ui_access():
        """检查当前进程是否具有UIAccess权限
        
        Returns:
            bool: 是否具有UIAccess权限
        """
        try:
            current_process = UIAccessManager._GetCurrentProcess()
            h_token = wintypes.HANDLE()
            
            if not UIAccessManager._OpenProcessToken(current_process, UIAccessManager.TOKEN_QUERY, ctypes.byref(h_token)):
                return False
            
            try:
                # 查询TokenUIAccess
                ui_access = wintypes.DWORD()
                return_size = wintypes.DWORD()
                
                if UIAccessManager._GetTokenInformation(h_token, UIAccessManager.TokenUIAccess, 
                                                      ctypes.byref(ui_access), ctypes.sizeof(ui_access), 
                                                      ctypes.byref(return_size)):
                    return ui_access.value != 0
                
                return False
                
            finally:
                UIAccessManager._CloseHandle(h_token)
                
        except Exception as e:
            logger.error(f"检查UIAccess权限时发生异常: {e}")
            return False
    
    @staticmethod
    def _init_toolhelp32():
        """初始化ToolHelp32 API"""
        try:
            # 动态加载kernel32.dll中的ToolHelp32函数
            kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
            
            # 定义PROCESSENTRY32结构体
            class PROCESSENTRY32(ctypes.Structure):
                _fields_ = [
                    ("dwSize", wintypes.DWORD),
                    ("cntUsage", wintypes.DWORD),
                    ("th32ProcessID", wintypes.DWORD),
                    ("th32DefaultHeapID", wintypes.ULONG),
                    ("th32ModuleID", wintypes.DWORD),
                    ("cntThreads", wintypes.DWORD),
                    ("th32ParentProcessID", wintypes.DWORD),
                    ("pcPriClassBase", wintypes.LONG),
                    ("dwFlags", wintypes.DWORD),
                    ("szExeFile", wintypes.CHAR * 260)
                ]
            
            # 设置函数原型
            UIAccessManager._CreateToolhelp32Snapshot = kernel32.CreateToolhelp32Snapshot
            UIAccessManager._CreateToolhelp32Snapshot.argtypes = [wintypes.DWORD, wintypes.DWORD]
            UIAccessManager._CreateToolhelp32Snapshot.restype = wintypes.HANDLE
            
            UIAccessManager._Process32First = kernel32.Process32First
            UIAccessManager._Process32First.argtypes = [wintypes.HANDLE, ctypes.POINTER(PROCESSENTRY32)]
            UIAccessManager._Process32First.restype = wintypes.BOOL
            
            UIAccessManager._Process32Next = kernel32.Process32Next
            UIAccessManager._Process32Next.argtypes = [wintypes.HANDLE, ctypes.POINTER(PROCESSENTRY32)]
            UIAccessManager._Process32Next.restype = wintypes.BOOL
            
            # 存储结构体类
            UIAccessManager.PROCESSENTRY32 = PROCESSENTRY32
            
        except Exception as e:
            logger.error(f"初始化ToolHelp32 API失败: {e}")
            raise
    
    @staticmethod
    def _get_winlogon_token():
        """获取同一Session下winlogon.exe的令牌
        
        Returns:
            wintypes.HANDLE: winlogon.exe的令牌句柄，失败返回None
        """
        try:
            # 获取当前进程ID
            current_pid = os.getpid()
            
            # 创建进程快照
            TH32CS_SNAPPROCESS = 0x00000002
            h_snapshot = UIAccessManager._CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)
            if h_snapshot == -1:  # INVALID_HANDLE_VALUE
                return None
            
            try:
                # 枚举进程
                process_entry = UIAccessManager.PROCESSENTRY32()
                process_entry.dwSize = ctypes.sizeof(UIAccessManager.PROCESSENTRY32)
                
                # 获取第一个进程
                if not UIAccessManager._Process32First(h_snapshot, ctypes.byref(process_entry)):
                    return None
                
                # 获取当前进程的Session ID
                current_session = UIAccessManager._get_process_session_id(current_pid)
                
                while True:
                    # 检查是否为winlogon.exe且在同一Session
                    process_name = process_entry.szExeFile.decode('ascii', errors='ignore').lower()
                    if process_name == 'winlogon.exe':
                        process_session = UIAccessManager._get_process_session_id(process_entry.th32ProcessID)
                        if process_session == current_session:
                            # 获取winlogon.exe的令牌
                            token = UIAccessManager._get_process_token(process_entry.th32ProcessID)
                            if token:
                                return token
                    
                    # 获取下一个进程
                    if not UIAccessManager._Process32Next(h_snapshot, ctypes.byref(process_entry)):
                        break
                
                return None
                
            finally:
                UIAccessManager._CloseHandle(h_snapshot)
                
        except Exception as e:
            logger.error(f"获取winlogon.exe令牌时发生异常: {e}")
            return None
    
    @staticmethod
    def _get_process_session_id(process_id):
        """获取进程的Session ID
        
        Args:
            process_id: 进程ID
            
        Returns:
            int: Session ID
        """
        try:
            # 动态加载WtsApi32.dll
            wtsapi32 = ctypes.WinDLL('wtsapi32', use_last_error=True)
            
            # 定义ProcessIdToSessionId函数
            ProcessIdToSessionId = wtsapi32.ProcessIdToSessionId
            ProcessIdToSessionId.argtypes = [wintypes.DWORD, ctypes.POINTER(wintypes.DWORD)]
            ProcessIdToSessionId.restype = wintypes.BOOL
            
            # 调用函数获取Session ID
            session_id = wintypes.DWORD()
            if ProcessIdToSessionId(process_id, ctypes.byref(session_id)):
                return session_id.value
            else:
                # 如果失败，返回当前进程的Session ID
                return UIAccessManager._get_current_session_id()
                
        except Exception as e:
            logger.warning(f"获取进程Session ID失败: {e}")
            return UIAccessManager._get_current_session_id()
    
    @staticmethod
    def _get_current_session_id():
        """获取当前进程的Session ID
        
        Returns:
            int: 当前Session ID
        """
        try:
            # 动态加载kernel32.dll
            kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
            
            # 定义WTSGetActiveConsoleSessionId函数
            WTSGetActiveConsoleSessionId = kernel32.WTSGetActiveConsoleSessionId
            WTSGetActiveConsoleSessionId.argtypes = []
            WTSGetActiveConsoleSessionId.restype = wintypes.DWORD
            
            return WTSGetActiveConsoleSessionId()
            
        except Exception as e:
            logger.warning(f"获取当前Session ID失败: {e}")
            return 0  # 默认返回Session 0
    
    @staticmethod
    def _get_process_token(process_id):
        """获取指定进程的令牌
        
        Args:
            process_id: 进程ID
            
        Returns:
            wintypes.HANDLE: 进程令牌句柄，失败返回None
        """
        try:
            # 打开进程
            h_process = UIAccessManager._OpenProcess(
                UIAccessManager.PROCESS_QUERY_INFORMATION | UIAccessManager.PROCESS_DUP_HANDLE,
                False, process_id)
            
            if not h_process:
                return None
            
            try:
                # 获取进程令牌
                h_token = wintypes.HANDLE()
                if UIAccessManager._OpenProcessToken(h_process, 
                                                   UIAccessManager.TOKEN_QUERY | UIAccessManager.TOKEN_DUPLICATE,
                                                   ctypes.byref(h_token)):
                    return h_token
                
                return None
                
            finally:
                UIAccessManager._CloseHandle(h_process)
                
        except Exception as e:
            logger.error(f"获取进程令牌时发生异常: {e}")
            return None
    
    @staticmethod
    def _set_current_process_ui_access():
        """直接设置当前进程的TokenUIAccess权限
        
        此方法通过SetTokenInformation API直接在当前进程的令牌中设置TokenUIAccess权限，
        可以绕过数字签名和指定安装路径的限制。
        
        Returns:
            int: 错误代码，0表示成功
        """
        try:
            # 获取当前进程句柄
            current_process = UIAccessManager._GetCurrentProcess()
            
            # 打开当前进程的令牌
            h_token = wintypes.HANDLE()
            if not UIAccessManager._OpenProcessToken(current_process, 
                                                   UIAccessManager.TOKEN_QUERY | UIAccessManager.TOKEN_ADJUST_PRIVILEGES | UIAccessManager.TOKEN_ADJUST_DEFAULT,
                                                   ctypes.byref(h_token)):
                error_code = UIAccessManager._GetLastError()
                logger.error(f"打开当前进程令牌失败，错误代码: {error_code}")
                return error_code
            
            try:
                # 启用必要的权限
                if not UIAccessManager._enable_privilege(h_token, UIAccessManager.SE_DEBUG_NAME):
                    logger.warning("启用SeDebugPrivilege权限失败")
                
                if not UIAccessManager._enable_privilege(h_token, UIAccessManager.SE_TCB_NAME):
                    logger.warning("启用SeTcbPrivilege权限失败")
                
                if not UIAccessManager._enable_privilege(h_token, UIAccessManager.SE_IMPERSONATE_NAME):
                    logger.warning("启用SeImpersonatePrivilege权限失败")
                
                # 设置UIAccess权限
                ui_access = wintypes.DWORD(1)
                if not UIAccessManager._SetTokenInformation(h_token, UIAccessManager.TokenUIAccess, 
                                                          ctypes.byref(ui_access), ctypes.sizeof(ui_access)):
                    error_code = UIAccessManager._GetLastError()
                    logger.error(f"设置TokenUIAccess权限失败，错误代码: {error_code}")
                    
                    # 记录详细的错误信息
                    if error_code == UIAccessManager.ERROR_ACCESS_DENIED:
                        logger.error("访问被拒绝，可能需要更高的权限或系统限制")
                    elif error_code == UIAccessManager.ERROR_PRIVILEGE_NOT_HELD:
                        logger.error("权限不足，无法修改令牌信息")
                    elif error_code == UIAccessManager.ERROR_INVALID_PARAMETER:
                        logger.error("参数无效，TokenUIAccess可能不被支持")
                    
                    return error_code
                
                logger.info("成功设置当前进程的TokenUIAccess权限")
                
                # 验证设置是否成功
                if UIAccessManager._has_ui_access():
                    logger.info("UIAccess权限验证成功")
                    return UIAccessManager.ERROR_SUCCESS
                else:
                    logger.warning("UIAccess权限设置成功但验证失败")
                    return UIAccessManager.ERROR_SUCCESS
                
            finally:
                UIAccessManager._CloseHandle(h_token)
                
        except Exception as e:
            logger.error(f"设置当前进程UIAccess权限时发生异常: {e}")
            return UIAccessManager._GetLastError() if hasattr(UIAccessManager, '_GetLastError') else -1
    
    @staticmethod
    def _create_ui_access_process(source_token):
        """使用源令牌创建具有UIAccess权限的新进程
        
        Args:
            source_token: 源令牌句柄
            
        Returns:
            int: 错误代码，0表示成功
        """
        try:
            # 复制令牌
            sa = SECURITY_ATTRIBUTES()
            sa.nLength = ctypes.sizeof(SECURITY_ATTRIBUTES)
            sa.lpSecurityDescriptor = None
            sa.bInheritHandle = False
            
            h_dup_token = wintypes.HANDLE()
            if not UIAccessManager._DuplicateTokenEx(source_token, 
                                                   UIAccessManager.TOKEN_ALL_ACCESS,
                                                   ctypes.byref(sa),
                                                   2,  # SecurityImpersonation
                                                   1,  # TokenPrimary
                                                   ctypes.byref(h_dup_token)):
                error_code = UIAccessManager._GetLastError()
                logger.error(f"复制令牌失败，错误代码: {error_code}")
                return error_code
            
            try:
                # 启用必要的权限
                UIAccessManager._enable_privilege(h_dup_token, UIAccessManager.SE_DEBUG_NAME)
                UIAccessManager._enable_privilege(h_dup_token, UIAccessManager.SE_TCB_NAME)
                UIAccessManager._enable_privilege(h_dup_token, UIAccessManager.SE_IMPERSONATE_NAME)
                UIAccessManager._enable_privilege(h_dup_token, UIAccessManager.SE_ASSIGNPRIMARYTOKEN_NAME)
                
                # 设置UIAccess权限
                ui_access = wintypes.DWORD(1)
                if not UIAccessManager._SetTokenInformation(h_dup_token, UIAccessManager.TokenUIAccess, 
                                                          ctypes.byref(ui_access), ctypes.sizeof(ui_access)):
                    error_code = UIAccessManager._GetLastError()
                    logger.error(f"设置UIAccess权限失败，错误代码: {error_code}")
                    return error_code
                
                # 创建新进程
                return UIAccessManager._create_process_with_token(h_dup_token)
                
            finally:
                UIAccessManager._CloseHandle(h_dup_token)
                
        except Exception as e:
            logger.error(f"创建UIAccess进程时发生异常: {e}")
            return UIAccessManager._GetLastError() if hasattr(UIAccessManager, '_GetLastError') else -1
    
    @staticmethod
    def _create_process_with_token(h_token):
        """使用令牌创建新进程
        
        Args:
            h_token: 令牌句柄
            
        Returns:
            int: 错误代码，0表示成功
        """
        try:
            # 获取当前程序路径
            current_exe = sys.executable
            if not current_exe:
                current_exe = os.path.abspath(sys.argv[0])
            
            # 检查程序路径是否存在
            if not os.path.exists(current_exe):
                logger.error(f"程序路径不存在: {current_exe}")
                return UIAccessManager.ERROR_NOT_FOUND
            
            # 准备启动信息
            startup_info = STARTUPINFO()
            startup_info.cb = ctypes.sizeof(STARTUPINFO)
            startup_info.lpDesktop = None
            startup_info.lpTitle = None
            startup_info.dwFlags = 0
            startup_info.wShowWindow = 0
            startup_info.cbReserved2 = 0
            startup_info.lpReserved2 = None
            
            # 准备进程信息
            process_info = PROCESS_INFORMATION()
            
            # 创建进程
            LOGON_WITH_PROFILE = 0x00000001
            if UIAccessManager._CreateProcessWithTokenW(h_token, LOGON_WITH_PROFILE, None, 
                                                      current_exe, UIAccessManager.CREATE_UNICODE_ENVIRONMENT,
                                                      None, None, ctypes.byref(startup_info), 
                                                      ctypes.byref(process_info)):
                # 关闭句柄
                UIAccessManager._CloseHandle(process_info.hProcess)
                UIAccessManager._CloseHandle(process_info.hThread)
                
                logger.info("成功创建具有UIAccess权限的新进程")
                
                # 退出当前进程
                os._exit(0)
                
                return UIAccessManager.ERROR_SUCCESS
            else:
                error_code = UIAccessManager._GetLastError()
                logger.error(f"创建进程失败，错误代码: {error_code}")
                
                # 如果是权限不足，尝试使用其他方法
                if error_code == UIAccessManager.ERROR_ACCESS_DENIED:
                    logger.info("尝试使用备用方法创建进程")
                    return UIAccessManager._create_process_with_token_alternative(h_token)
                
                return error_code
                
        except Exception as e:
            logger.error(f"创建进程时发生异常: {e}")
            return UIAccessManager._GetLastError() if hasattr(UIAccessManager, '_GetLastError') else -1
    
    @staticmethod
    def _create_process_with_token_alternative(h_token):
        """使用备用方法创建进程
        
        Args:
            h_token: 令牌句柄
            
        Returns:
            int: 错误代码，0表示成功
        """
        try:
            # 获取当前程序路径
            current_exe = sys.executable
            if not current_exe:
                current_exe = os.path.abspath(sys.argv[0])
            
            # 检查程序路径是否存在
            if not os.path.exists(current_exe):
                logger.error(f"程序路径不存在: {current_exe}")
                return UIAccessManager.ERROR_NOT_FOUND
            
            # 准备启动信息
            startup_info = STARTUPINFO()
            startup_info.cb = ctypes.sizeof(STARTUPINFO)
            startup_info.lpDesktop = None
            startup_info.lpTitle = None
            startup_info.dwFlags = 0
            startup_info.wShowWindow = 0
            startup_info.cbReserved2 = 0
            startup_info.lpReserved2 = None
            
            # 准备进程信息
            process_info = PROCESS_INFORMATION()
            
            # 使用不同的标志创建进程
            CREATE_NEW_PROCESS_GROUP = 0x00000200
            flags = UIAccessManager.CREATE_UNICODE_ENVIRONMENT | UIAccessManager.CREATE_NEW_CONSOLE | CREATE_NEW_PROCESS_GROUP
            
            LOGON_WITH_PROFILE = 0x00000001
            if UIAccessManager._CreateProcessWithTokenW(h_token, LOGON_WITH_PROFILE, None, 
                                                      current_exe, flags,
                                                      None, None, ctypes.byref(startup_info), 
                                                      ctypes.byref(process_info)):
                # 关闭句柄
                UIAccessManager._CloseHandle(process_info.hProcess)
                UIAccessManager._CloseHandle(process_info.hThread)
                
                logger.info("使用备用方法成功创建具有UIAccess权限的新进程")
                
                # 退出当前进程
                os._exit(0)
                
                return UIAccessManager.ERROR_SUCCESS
            else:
                error_code = UIAccessManager._GetLastError()
                logger.error(f"备用方法创建进程失败，错误代码: {error_code}")
                return error_code
                
        except Exception as e:
            logger.error(f"备用方法创建进程时发生异常: {e}")
            return UIAccessManager._GetLastError() if hasattr(UIAccessManager, '_GetLastError') else -1


class UIAccessMixin:
    """UIAccess权限混入类 - 为窗口类提供UIAccess权限支持"""
    
    def _init_ui_access(self):
        """初始化UIAccess权限"""
        self.ui_access_enabled = False
        
        # 检查是否为Windows系统
        import platform
        if platform.system() != 'Windows':
            logger.info("非Windows系统，跳过UIAccess权限初始化")
            return
        
        # 检查是否为管理员权限运行
        try:
            import ctypes
            is_admin = ctypes.windll.shell32.IsUserAnAdmin()
            if not is_admin:
                logger.warning("程序未以管理员权限运行，无法获取UIAccess权限")
                return
        except Exception as e:
            logger.warning(f"检查管理员权限失败: {e}")
            return
        
        # 使用UIAccessManager尝试获取UIAccess权限
        try:
            result = UIAccessManager.prepare_for_ui_access()
            if result == UIAccessManager.ERROR_SUCCESS:
                self.ui_access_enabled = True
                logger.info("UIAccess权限获取成功，窗口将能够显示在系统工具之上")
            else:
                logger.warning(f"UIAccess权限获取失败，错误代码: {result}")
        except Exception as e:
            logger.error(f"UIAccess权限初始化异常: {e}")
    
    def _apply_ui_access_window_styles(self, enable_topmost=True):
        """应用UIAccess权限相关的窗口样式
        
        Args:
            enable_topmost (bool): 是否启用窗口置顶，默认为True
        """
        # UIAccess权限获取成功后，根据参数决定是否设置窗口置顶
        if hasattr(self, 'ui_access_enabled') and self.ui_access_enabled:
            if enable_topmost:
                # 使用Windows API设置窗口置顶到最高层级（高于任务管理器）
                try:
                    import win32gui
                    import win32con
                    hwnd = self.winId()
                    # 设置窗口置顶到最高层级
                    win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, 
                                         win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_NOACTIVATE)
                    logger.info("UIAccess权限已启用，窗口已置顶到最高层级")
                except ImportError:
                    logger.warning("win32gui或win32con模块未安装，无法设置窗口置顶")
                except Exception as e:
                    logger.warning(f"设置窗口置顶失败: {e}")
            else:
                # UIAccess权限启用但不置顶窗口
                logger.info("UIAccess权限已启用，窗口保持普通层级")
    
    def toggle_topmost(self, enable_topmost=None):
        """切换窗口置顶状态
        
        Args:
            enable_topmost (bool, optional): 指定置顶状态，None表示切换当前状态
        
        Returns:
            bool: 切换后的置顶状态
        """
        if not hasattr(self, 'ui_access_enabled') or not self.ui_access_enabled:
            logger.warning("UIAccess权限未启用，无法控制窗口置顶")
            return False
        
        try:
            # 检查win32gui和win32con是否可用
            import win32gui
            import win32con
            
            hwnd = self.winId()
            
            # 获取当前窗口状态
            current_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
            is_currently_topmost = bool(current_style & win32con.WS_EX_TOPMOST)
            
            # 确定目标状态
            if enable_topmost is None:
                # 切换状态
                target_topmost = not is_currently_topmost
            else:
                # 设置指定状态
                target_topmost = enable_topmost
            
            # 应用新的置顶状态
            if target_topmost:
                win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, 
                                     win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_NOACTIVATE)
                logger.info("窗口已置顶到最高层级")
            else:
                win32gui.SetWindowPos(hwnd, win32con.HWND_NOTOPMOST, 0, 0, 0, 0, 
                                     win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_NOACTIVATE)
                logger.info("窗口已取消置顶")
            
            return target_topmost
            
        except ImportError:
            logger.warning("win32gui或win32con模块未安装，无法控制窗口置顶")
            return False
        except Exception as e:
            logger.error(f"切换窗口置顶状态失败: {e}")
            return False


# ================================================== (๑•̀ㅂ•́)و✧
# 使用示例 📝
# ================================================== (๑•̀ㅂ•́)و✧

def example_usage():
    """UIAccess权限管理模块使用示例"""
    
    # 1. 在程序开头初始化UIAccess权限
    # 模块会自动尝试以下两种方法（按优先级顺序）：
    #   a) 直接设置TokenUIAccess权限（推荐）
    #      - 通过SetTokenInformation API直接修改当前进程令牌
    #      - 可以绕过数字签名和安装路径限制
    #      - 无需创建新进程，更加高效
    #   b) 通过System令牌创建新进程（备用方案）
    #      - 获取winlogon.exe的System令牌
    #      - 创建具有UIAccess权限的新进程
    #      - 需要数字签名和受信任位置安装
    
    result = UIAccessManager.prepare_for_ui_access()
    if result == UIAccessManager.ERROR_SUCCESS:
        logger.info("UIAccess权限获取成功！")
        logger.info("窗口现在可以显示在系统工具（如任务管理器）之上")
    else:
        logger.error(f"UIAccess权限获取失败，错误代码: {result}")
        logger.error("请确保程序以管理员权限运行")
        return
    
    # 2. 在窗口类中使用UIAccessMixin
    class MyWindow(UIAccessMixin):
        def __init__(self):
            # 初始化UIAccess权限
            self._init_ui_access()
            
            # 应用UIAccess窗口样式
            self._apply_ui_access_window_styles(enable_topmost=True)
        
        def toggle_window_topmost(self):
            """切换窗口置顶状态"""
            return self.toggle_topmost()
    
    # 3. 创建窗口实例
    window = MyWindow()
    
    # 4. 切换窗口置顶状态
    is_topmost = window.toggle_window_topmost()
    print(f"窗口置顶状态: {is_topmost}")


if __name__ == "__main__":
    """直接运行此文件进行测试"""
    example_usage()