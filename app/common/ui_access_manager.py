# ================================================== ✧*｡٩(ˊᗜˋ*)و✧*｡
# UIAccess权限管理模块 🔮
# ================================================== ✧*｡٩(ˊᗜˋ*)و✧*｡

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
    
    SE_DEBUG_NAME = "SeDebugPrivilege"
    SE_TCB_NAME = "SeTcbPrivilege"
    SE_IMPERSONATE_NAME = "SeImpersonatePrivilege"
    
    ERROR_SUCCESS = 0
    ERROR_ACCESS_DENIED = 5
    ERROR_PRIVILEGE_NOT_HELD = 1314
    
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
            
            # 获取当前进程令牌
            current_process = UIAccessManager._GetCurrentProcess()
            h_token = wintypes.HANDLE()
            
            if not UIAccessManager._OpenProcessToken(current_process, 
                                                   UIAccessManager.TOKEN_QUERY | UIAccessManager.TOKEN_DUPLICATE,
                                                   ctypes.byref(h_token)):
                error_code = UIAccessManager._GetLastError()
                logger.error(f"无法打开进程令牌，错误代码: {error_code}")
                return error_code
            
            try:
                # 尝试启用调试权限
                if not UIAccessManager._enable_privilege(h_token, UIAccessManager.SE_DEBUG_NAME):
                    logger.warning("无法启用调试权限")
                
                # 尝试启用TCB权限
                if not UIAccessManager._enable_privilege(h_token, UIAccessManager.SE_TCB_NAME):
                    logger.warning("无法启用TCB权限")
                
                # 尝试启用模拟权限
                if not UIAccessManager._enable_privilege(h_token, UIAccessManager.SE_IMPERSONATE_NAME):
                    logger.warning("无法启用模拟权限")
                
                logger.info("UIAccess权限准备完成")
                return UIAccessManager.ERROR_SUCCESS
                
            finally:
                UIAccessManager._CloseHandle(h_token)
                
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