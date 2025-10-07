from qfluentwidgets import *
from qfluentwidgets import FluentIcon as FIF
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

import json
import os
import time
from loguru import logger
import hashlib
import pyotp
from io import BytesIO
import pyqrcode
import re
import secrets
import ctypes
import wmi
import random
import string
from Crypto.Cipher import AES

from app.common.config import get_theme_icon, load_custom_font
from app.common.path_utils import path_manager, open_file

def create_hidden_folder(path):
    """创建隐藏文件夹"""
    try:
        if not path_manager.file_exists(path):
            os.makedirs(path)
        
        # 无论文件夹是否已存在，都设置隐藏属性
        if os.name == 'nt':
            # 确保路径是绝对路径并转换为正确的Unicode字符串格式
            abs_path = os.path.abspath(path)
            # 将路径转换为Unicode字符串
            if not isinstance(abs_path, str):
                abs_path = str(abs_path)
            ctypes.windll.kernel32.SetFileAttributesW(abs_path, 2)
        return
    except Exception as e:
        logger.error(f"创建隐藏文件夹失败: {e}")
        return

def set_system_hidden_file(file_path):
    """设置文件为普通隐藏"""
    try:
        if os.path.exists(file_path):
            if os.name == 'nt':
                # FILE_ATTRIBUTE_HIDDEN = 2 (仅隐藏属性)
                abs_path = os.path.abspath(file_path)
                # 确保路径是正确的Unicode字符串格式
                if not isinstance(abs_path, str):
                    abs_path = str(abs_path)
                ctypes.windll.kernel32.SetFileAttributesW(abs_path, 2)
                logger.info(f"已设置文件为隐藏: {file_path}")
            else:
                # 在非Windows系统上，尝试设置隐藏属性
                import stat
                current_mode = os.stat(file_path).st_mode
                os.chmod(file_path, current_mode & ~stat.S_IALLUGO)
                logger.info(f"已设置文件为隐藏: {file_path}")
        else:
            logger.error(f"文件不存在，无法设置隐藏属性: {file_path}")
    except Exception as e:
        logger.error(f"设置文件隐藏属性失败: {e}")

# 获取应用根目录并构建SecRandom文件夹路径
secrandom_dir = path_manager._get_app_root()

def generate_qr_code(secret, username):
    """生成二维码"""
    try:
        totp = pyotp.TOTP(secret)
        uri = totp.provisioning_uri(
            name=username,
            issuer_name="SecRandom"
        )
        qr = pyqrcode.create(uri, error='L', version=5, mode='binary')
        buffer = BytesIO()
        qr.png(buffer, scale=10, module_color=[0, 0, 0, 255], background=[255, 255, 255, 255])
        pixmap = QPixmap()
        pixmap.loadFromData(buffer.getvalue())
        pixmap = pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        return pixmap
    except Exception as e:
        logger.error(f"生成二维码失败: {e}")
        return None

# USB相关工具函数
def generate_usb_key(length=16):
    """生成随机密钥字符串"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def encrypt_key_data(key_data, encryption_key):
    """使用AES加密密钥数据"""
    try:
        # 确保密钥是16字节
        if len(encryption_key) > 16:
            encryption_key = encryption_key[:16]
        elif len(encryption_key) < 16:
            encryption_key = encryption_key.ljust(16, '0')
        
        key_bytes = encryption_key.encode('utf-8')
        data_bytes = key_data.encode('utf-8')
        
        cipher = AES.new(key_bytes, AES.MODE_EAX)
        nonce = cipher.nonce
        ciphertext, tag = cipher.encrypt_and_digest(data_bytes)
        
        # 返回nonce + ciphertext用于存储
        return nonce + ciphertext
    except Exception as e:
        logger.error(f"AES加密失败: {e}")
        return None

def decrypt_key_data(encrypted_data, encryption_key):
    """使用AES解密密钥数据"""
    try:
        # 确保密钥是16字节
        if len(encryption_key) > 16:
            encryption_key = encryption_key[:16]
        elif len(encryption_key) < 16:
            encryption_key = encryption_key.ljust(16, '0')
        
        key_bytes = encryption_key.encode('utf-8')
        
        # 从加密数据中提取nonce和ciphertext
        nonce = encrypted_data[:16]
        ciphertext = encrypted_data[16:]
        
        cipher = AES.new(key_bytes, AES.MODE_EAX, nonce=nonce)
        plaintext = cipher.decrypt(ciphertext)
        
        return plaintext.decode('utf-8')
    except Exception as e:
        logger.error(f"AES解密失败: {e}")
        return None

def get_usb_drives():
    """获取所有 USB 存储设备信息"""
    try:
        # 在线程中调用WMI前需要初始化COM组件
        import pythoncom
        pythoncom.CoInitialize()
        
        c = wmi.WMI()
        usb_drives = []
        # 优化：使用更高效的WMI查询，只查询必要的字段
        for disk in c.Win32_DiskDrive(InterfaceType="USB"):
            usb_drives.append({
                "设备ID": disk.DeviceID,
                "型号": disk.Model,
                "接口": disk.InterfaceType,
                "序列号": getattr(disk, "SerialNumber", "未知"),
                "大小(字节)": int(disk.Size) if disk.Size else None
            })
        return usb_drives
    except Exception as e:
        logger.error(f"获取USB设备失败: {e}")
        return []
    finally:
        # 确保释放COM资源
        try:
            import pythoncom
            pythoncom.CoUninitialize()
        except:
            pass

def get_usb_devices():
    """获取所有 USB 存储设备信息（兼容旧接口）"""
    try:
        drives = get_usb_drives()
        devices = []
        for drive in drives:
            devices.append({
                "DeviceID": drive["设备ID"],
                "Model": drive["型号"],
                "SerialNumber": drive["序列号"]
            })
        return devices
    except Exception as e:
        logger.error(f"获取USB设备失败: {e}")
        return []

def get_usb_drive_letter(device_id):
    """根据设备ID获取U盘盘符"""
    try:
        # 在线程中调用WMI前需要初始化COM组件
        import pythoncom
        pythoncom.CoInitialize()
        
        c = wmi.WMI()
        logger.info(f"开始获取设备ID {device_id} 的盘符")
        
        # 方法1：通过磁盘驱动器索引查找
        for disk_drive in c.Win32_DiskDrive():
            if disk_drive.DeviceID == device_id:
                logger.info(f"找到磁盘驱动器: {disk_drive.DeviceID}, 索引: {disk_drive.Index}")
                
                # 获取该磁盘的所有分区
                partitions = c.Win32_DiskPartition(DiskIndex=disk_drive.Index)
                logger.info(f"找到 {len(partitions)} 个分区")
                
                # 遍历分区，查找对应的逻辑磁盘
                for partition in partitions:
                    logger.info(f"检查分区: {partition.DeviceID}")
                    
                    # 使用关联查询获取该分区对应的逻辑磁盘
                    try:
                        # 获取分区到逻辑磁盘的关联
                        for assoc in partition.associators("Win32_LogicalDiskToPartition"):
                            if hasattr(assoc, 'DeviceID'):
                                logical_disk = assoc
                                logger.info(f"找到逻辑磁盘: {logical_disk.DeviceID}, 类型: {logical_disk.DriveType}")
                                
                                # 检查是否为可移动磁盘 (DriveType = 2) 或其他可能的USB设备
                                if logical_disk.DriveType == 2:
                                    logger.info(f"确认U盘盘符: {logical_disk.DeviceID}")
                                    return logical_disk.DeviceID
                                # 如果不是DriveType=2，但设备是USB设备，也尝试返回
                                elif hasattr(disk_drive, 'InterfaceType') and "USB" in str(disk_drive.InterfaceType).upper():
                                    logger.info(f"USB设备但DriveType不为2，盘符: {logical_disk.DeviceID}")
                                    return logical_disk.DeviceID
                    except Exception as e:
                        logger.error(f"关联查询失败: {e}")
        
        # 方法2：通过PNPDeviceID匹配
        logger.info("方法1失败，尝试通过PNPDeviceID匹配")
        target_disk = None
        for disk_drive in c.Win32_DiskDrive():
            if disk_drive.DeviceID == device_id:
                target_disk = disk_drive
                break
        
        if target_disk and hasattr(target_disk, 'PNPDeviceID'):
            logger.info(f"目标磁盘PNPDeviceID: {target_disk.PNPDeviceID}")
            # 查找所有逻辑磁盘
            for logical_disk in c.Win32_LogicalDisk():
                # 优先检查可移动磁盘
                if logical_disk.DriveType == 2:
                    logger.info(f"找到可移动磁盘: {logical_disk.DeviceID}")
                    logger.info(f"通过方法2确认U盘盘符: {logical_disk.DeviceID}")
                    return logical_disk.DeviceID
                # 如果没有可移动磁盘，检查是否有USB设备对应的逻辑磁盘
                elif hasattr(target_disk, 'InterfaceType') and "USB" in str(target_disk.InterfaceType).upper():
                    # 检查这个逻辑磁盘是否属于目标磁盘
                    try:
                        # 获取逻辑磁盘对应的分区
                        for partition_assoc in logical_disk.associators("Win32_LogicalDiskToPartition"):
                            if hasattr(partition_assoc, 'Antecedent') and hasattr(partition_assoc, 'Dependent'):
                                # 从依赖项中获取分区信息
                                partition_info = partition_assoc.Dependent
                                if "Disk #" + str(target_disk.Index) in partition_info:
                                    logger.info(f"找到USB设备对应的逻辑磁盘: {logical_disk.DeviceID}")
                                    logger.info(f"通过方法2确认U盘盘符: {logical_disk.DeviceID}")
                                    return logical_disk.DeviceID
                    except Exception as e:
                        logger.error(f"检查逻辑磁盘关联失败: {e}")
        
        # 方法3：直接查找所有逻辑磁盘并尝试匹配USB设备
        logger.info("方法2失败，尝试直接查找所有逻辑磁盘")
        removable_disks = []
        usb_logical_disks = []
        
        for logical_disk in c.Win32_LogicalDisk():
            if hasattr(logical_disk, 'DeviceID'):
                # 优先收集可移动磁盘
                if logical_disk.DriveType == 2:
                    removable_disks.append(logical_disk.DeviceID)
                    logger.info(f"找到可移动磁盘: {logical_disk.DeviceID}")
                
                # 同时收集所有逻辑磁盘，用于后续USB设备匹配
                usb_logical_disks.append(logical_disk.DeviceID)
                logger.info(f"找到逻辑磁盘: {logical_disk.DeviceID}, 类型: {logical_disk.DriveType}")
        
        # 优先返回可移动磁盘
        if len(removable_disks) == 1:
            logger.info(f"通过方法3确认U盘盘符: {removable_disks[0]}")
            return removable_disks[0]
        elif len(removable_disks) > 1:
            logger.info(f"找到多个可移动磁盘，返回第一个: {removable_disks[0]}")
            return removable_disks[0]
        
        # 如果没有可移动磁盘，尝试找到目标USB设备对应的逻辑磁盘
        if target_disk and hasattr(target_disk, 'Index'):
            logger.info(f"尝试匹配磁盘索引 {target_disk.Index} 对应的逻辑磁盘")
            for disk_letter in usb_logical_disks:
                # 检查这个逻辑磁盘是否属于目标磁盘
                try:
                    for logical_disk in c.Win32_LogicalDisk(DeviceID=disk_letter):
                        for partition_assoc in logical_disk.associators("Win32_LogicalDiskToPartition"):
                            if hasattr(partition_assoc, 'Dependent'):
                                partition_info = partition_assoc.Dependent
                                if "Disk #" + str(target_disk.Index) in partition_info:
                                    logger.info(f"找到目标磁盘对应的逻辑磁盘: {disk_letter}")
                                    logger.info(f"通过方法3确认U盘盘符: {disk_letter}")
                                    return disk_letter
                except Exception as e:
                    logger.error(f"检查逻辑磁盘 {disk_letter} 失败: {e}")
        
        # 最后的备选方案：如果有USB设备且只有一个逻辑磁盘，返回它
        if len(usb_logical_disks) == 1:
            logger.info(f"只有一个逻辑磁盘，返回: {usb_logical_disks[0]}")
            return usb_logical_disks[0]
        # 如果有多个逻辑磁盘，返回第一个
        elif len(usb_logical_disks) > 1:
            logger.info(f"有多个逻辑磁盘，返回第一个: {usb_logical_disks[0]}")
            return usb_logical_disks[0]
        
        logger.error(f"未找到设备ID {device_id} 对应的U盘盘符")
        return None
    except Exception as e:
        logger.error(f"获取U盘盘符失败: {e}")
        return None
    finally:
        # 确保释放COM资源
        try:
            import pythoncom
            pythoncom.CoUninitialize()
        except:
            pass

def bind_usb_device(selected_device, usb_mount_path, require_key_file=True):
    """绑定U盘
    
    Args:
        selected_device (dict): 选中的USB设备信息
        usb_mount_path (str): U盘挂载路径
        require_key_file (bool): 是否需要.key文件验证，默认为True
    
    Returns:
        bool: 绑定是否成功
    """
    try:
        # 添加调试日志
        logger.info(f"开始绑定U盘，selected_device: {selected_device}, 类型: {type(selected_device)}")
        logger.info(f"usb_mount_path: {usb_mount_path}")
        
        # 检查selected_device是否为字典类型
        if not isinstance(selected_device, dict):
            logger.error(f"selected_device类型错误，期望字典，实际得到: {type(selected_device)}")
            return False
        
        # 根据require_key_file参数决定是否生成.key文件
        if require_key_file:
            key = generate_usb_key()
            # 确保路径格式正确（添加反斜杠）
            if not usb_mount_path.endswith('\\'):
                usb_mount_path += '\\'
            key_path = os.path.join(usb_mount_path, ".key")
            
            # 检查U盘路径是否存在且可写
            if not os.path.exists(usb_mount_path):
                logger.error(f"U盘路径不存在: {usb_mount_path}")
                return False
            
            if not os.access(usb_mount_path, os.W_OK):
                logger.error(f"U盘路径没有写入权限: {usb_mount_path}")
                return False
            
            # 生成加密密钥（使用设备ID和序列号的组合作为加密密钥）
            try:
                encryption_key = selected_device["设备ID"] + selected_device["序列号"]
                logger.info(f"生成加密密钥成功")
            except Exception as e:
                logger.error(f"生成加密密钥失败: {e}")
                logger.error(f"selected_device内容: {selected_device}")
                raise
            
            # 加密密钥数据
            encrypted_key_data = encrypt_key_data(key, encryption_key)
            if encrypted_key_data is None:
                logger.error("密钥加密失败")
                return False
            
            # 检查.key文件是否已存在，如果存在则先删除
            if os.path.exists(key_path):
                try:
                    os.remove(key_path)
                    logger.info(f"已删除已存在的密钥文件: {key_path}")
                except PermissionError as e:
                    logger.error(f"权限错误，无法删除已存在的密钥文件: {key_path}, 错误: {e}")
                    logger.error(f"请检查文件是否被占用或是否有管理员权限")
                    return False
                except Exception as e:
                    logger.error(f"删除已存在的密钥文件失败: {key_path}, 错误: {e}")
                    return False
            
            # 以二进制模式写入加密后的密钥数据
            try:
                with open(key_path, "wb") as f:
                    f.write(encrypted_key_data)
                logger.info(f"成功写入密钥文件: {key_path}")
            except PermissionError as e:
                logger.error(f"权限错误，无法写入密钥文件: {key_path}, 错误: {e}")
                logger.error(f"请检查U盘是否被写保护或是否有管理员权限")
                return False
            except Exception as e:
                logger.error(f"写入密钥文件失败: {key_path}, 错误: {e}")
                return False
            
            # 设置.key文件为系统级别隐藏
            set_system_hidden_file(key_path)
        else:
            # 不需要.key文件，生成一个空的key值
            key = "no_key_file_required"
            key_path = None
        
        # 保存绑定信息到enc_set.json文件
        enc_set_file = path_manager.get_enc_set_path()
        
        # 读取现有设置
        existing_settings = {}
        if os.path.exists(enc_set_file):
            try:
                with open(enc_set_file, "r", encoding='utf-8') as f:
                    existing_settings = json.load(f)
            except json.JSONDecodeError:
                existing_settings = {}
        
        # 添加USB绑定信息（保存原始密钥值用于验证）
        usb_config = {
            "DeviceID": selected_device["设备ID"],
            "SerialNumber": selected_device["序列号"],
            "Model": selected_device.get("型号", "未知型号"),  # 保存型号信息
            "RequireKeyFile": require_key_file,  # 添加是否需要.key文件的标记
            "KeyFile": ".key" if require_key_file else None,
            "KeyValue": key,
            "bind_time": int(time.time())  # 添加绑定时间
        }
        
        # 添加调试日志
        # logger.debug(f"创建USB配置: {usb_config}, 类型: {type(usb_config)}")
        
        # 如果不存在usb_binding数组，则创建
        if "usb_binding" not in existing_settings:
            existing_settings["usb_binding"] = []
            logger.info("创建新的usb_binding数组")
        
        # 检查现有usb_binding数组的数据类型
        # logger.debug(f"现有usb_binding数组: {existing_settings['usb_binding']}, 类型: {type(existing_settings['usb_binding'])}")
        # for i, existing_usb in enumerate(existing_settings["usb_binding"]):
            # logger.debug(f"现有usb_binding[{i}]: {existing_usb}, 类型: {type(existing_usb)}")
        
        # 检查是否已经绑定过相同的设备
        device_exists = False
        for existing_usb in existing_settings["usb_binding"]:
            if isinstance(existing_usb, dict):
                if (existing_usb.get("DeviceID") == usb_config["DeviceID"] and 
                    existing_usb.get("SerialNumber") == usb_config["SerialNumber"]):
                    device_exists = True
                    break
            else:
                logger.error(f"现有usb_binding数组包含非字典类型的数据: {type(existing_usb)}")
        
        if not device_exists:
            existing_settings["usb_binding"].append(usb_config)
            logger.info(f"成功添加USB配置到绑定列表")
        else:
            logger.error("该U盘已经绑定过，不能重复绑定")
            return False
        
        # 保存到enc_set.json文件
        try:
            os.makedirs(os.path.dirname(enc_set_file), exist_ok=True)
            with open(enc_set_file, "w", encoding='utf-8') as f:
                json.dump(existing_settings, f, indent=4, ensure_ascii=False)
            logger.info(f"成功保存配置到文件: {enc_set_file}")
        except Exception as e:
            logger.error(f"保存配置文件失败: {e}")
            return False
        
        logger.info(f"U盘绑定成功{'，加密密钥文件生成在 ' + key_path if require_key_file else '（无需.key文件）'}")
        return True
    except Exception as e:
        logger.error(f"U盘绑定失败: {e}")
        return False



def unbind_usb(device_id=None, serial_number=None, model=None):
    """解绑U盘（无需插入U盘，直接从绑定列表中移除）
    
    Args:
        device_id (str, optional): 要解绑的设备ID，如果为None则解绑所有U盘
        serial_number (str, optional): 要解绑的序列号，如果device_id提供则此参数可选
        model (str, optional): 要解绑的设备型号，用于更精确的匹配
    
    Returns:
        bool: 解绑是否成功
    """
    try:
        enc_set_file = path_manager.get_enc_set_path()
        if os.path.exists(enc_set_file):
            # 读取现有设置
            with open(enc_set_file, "r", encoding='utf-8') as f:
                settings = json.load(f)
            
            # 如果存在USB绑定信息
            if "usb_binding" in settings and settings["usb_binding"]:
                unbound_count = 0
                unbound_with_key_count = 0  # 需要.key文件的U盘数量
                unbound_without_key_count = 0  # 无需.key文件的U盘数量
                remaining_bindings = []
                pending_deletions = settings.get("usb_pending_deletion", [])
                
                # 遍历所有绑定的U盘
                for usb_binding in settings["usb_binding"]:
                    # 检查是否匹配要解绑的U盘
                    should_unbind = False
                    if device_id is None:
                        # 如果没有指定设备ID，解绑所有U盘
                        should_unbind = True
                    elif usb_binding["DeviceID"] == device_id:
                        # 指定了设备ID且匹配
                        should_unbind = True
                        if serial_number and usb_binding["SerialNumber"] != serial_number:
                            # 如果还指定了序列号但不匹配，不解绑
                            should_unbind = False
                        elif model and usb_binding.get("Model", "") != model:
                            # 如果还指定了型号但不匹配，不解绑
                            should_unbind = False
                    
                    if should_unbind:
                        # 根据RequireKeyFile标记决定是否需要删除.key文件
                        require_key_file = usb_binding.get("RequireKeyFile", True)
                        
                        if require_key_file:
                            # 需要.key文件，添加到待删除列表等待删除密钥文件
                            deletion_info = {
                                "DeviceID": usb_binding["DeviceID"],
                                "SerialNumber": usb_binding["SerialNumber"],
                                "Model": usb_binding.get("Model", ""),
                                "KeyFile": ".key"
                            }
                            pending_deletions.append(deletion_info)
                            logger.info(f"已从绑定列表中移除U盘并添加到待删除列表: {usb_binding['DeviceID']}, 型号: {usb_binding.get('Model', '')}")
                            unbound_with_key_count += 1
                        else:
                            # 不需要.key文件，直接移除，无需删除文件
                            logger.info(f"已从绑定列表中直接移除U盘（无需删除.key文件）: {usb_binding['DeviceID']}, 型号: {usb_binding.get('Model', '')}")
                            unbound_without_key_count += 1
                        
                        unbound_count += 1
                    else:
                        # 保留不需要解绑的U盘
                        remaining_bindings.append(usb_binding)
                
                # 更新绑定列表和待删除列表
                settings["usb_binding"] = remaining_bindings
                settings["usb_pending_deletion"] = pending_deletions
                
                # 保存更新后的设置
                with open(enc_set_file, "w", encoding='utf-8') as f:
                    json.dump(settings, f, indent=4, ensure_ascii=False)
                
                if unbound_count > 0:
                    if unbound_with_key_count > 0 and unbound_without_key_count > 0:
                        logger.info(f"成功解绑 {unbound_count} 个U盘（{unbound_with_key_count} 个需要删除.key文件，{unbound_without_key_count} 个无需.key文件）")
                    elif unbound_with_key_count > 0:
                        logger.info(f"成功解绑 {unbound_count} 个U盘，已添加到待删除列表")
                    else:
                        logger.info(f"成功解绑 {unbound_count} 个U盘（均为无需.key文件的U盘）")
                    return True
                else:
                    logger.error("没有找到匹配的U盘进行解绑")
                    return False
            else:
                logger.error("没有找到绑定的U盘")
                return False
        return False
    except Exception as e:
        logger.error(f"U盘解绑失败: {e}")
        return False

def check_and_delete_pending_usb():
    """检查并删除待删除列表中的U盘文件（仅处理需要.key文件的U盘绑定）"""
    try:
        enc_set_file = path_manager.get_enc_set_path()
        if not os.path.exists(enc_set_file):
            return False
            
        # 读取现有设置
        with open(enc_set_file, "r", encoding='utf-8') as f:
            settings = json.load(f)
        
        # 检查是否有待删除的U盘
        if "usb_pending_deletion" not in settings or not settings["usb_pending_deletion"]:
            return False
            
        # 获取当前所有USB设备
        current_usb_devices = get_usb_drives()
        deleted_count = 0
        
        # 遍历待删除列表
        pending_deletions = settings["usb_pending_deletion"]
        remaining_deletions = []
        
        for deletion_info in pending_deletions:
            device_found = False
            
            # 检查当前USB设备中是否有匹配的设备
            for usb_device in current_usb_devices:
                if (usb_device["设备ID"] == deletion_info["DeviceID"] and 
                    usb_device["序列号"] == deletion_info["SerialNumber"] and
                    (not deletion_info.get("Model") or usb_device.get("型号", "") == deletion_info.get("Model", ""))):
                    device_found = True
                    logger.info(f"找到匹配的USB设备进行删除: {deletion_info['DeviceID']}, 型号: {deletion_info.get('Model', '未知')}")
                    
                    # 获取U盘盘符
                    usb_drive_letter = get_usb_drive_letter(deletion_info["DeviceID"])
                    if usb_drive_letter:
                        # 构建密钥文件路径
                        key_path = os.path.join(usb_drive_letter, deletion_info["KeyFile"])
                        
                        # 删除密钥文件
                        if os.path.exists(key_path):
                            try:
                                os.remove(key_path)
                                logger.info(f"已删除U盘密钥文件: {key_path}")
                                deleted_count += 1
                            except Exception as e:
                                logger.error(f"删除密钥文件失败: {key_path}, 错误: {e}")
                                # 删除失败，保留在待删除列表
                                remaining_deletions.append(deletion_info)
                        else:
                            logger.error(f"密钥文件不存在: {key_path}")
                            # 文件不存在，认为已删除
                            deleted_count += 1
                    else:
                        logger.error(f"无法获取U盘盘符: {deletion_info['DeviceID']}")
                        # 无法获取盘符，保留在待删除列表
                        remaining_deletions.append(deletion_info)
                    break
            
            # 如果设备未找到，保留在待删除列表
            if not device_found:
                # logger.debug(f"未找到匹配的USB设备进行删除: {deletion_info['DeviceID']}, 序列号: {deletion_info['SerialNumber']}, 型号: {deletion_info.get('Model', '未知')}")
                remaining_deletions.append(deletion_info)
        
        # 更新待删除列表，如果列表为空则删除该字段
        if remaining_deletions:
            settings["usb_pending_deletion"] = remaining_deletions
        else:
            # 所有待删除项都已处理完成，清除该字段
            if "usb_pending_deletion" in settings:
                del settings["usb_pending_deletion"]
                logger.info("所有U盘密钥文件已删除完成，清除待删除列表")
        
        # 保存更新后的设置
        with open(enc_set_file, "w", encoding='utf-8') as f:
            json.dump(settings, f, indent=4, ensure_ascii=False)
        
        if deleted_count > 0:
            logger.info(f"已删除 {deleted_count} 个U盘密钥文件")
            return True
        
        return False
    except Exception as e:
        logger.error(f"检查并删除待删除U盘文件失败: {e}")
        return False

def is_usb_bound():
    """检查是否已绑定U盘（使用设备ID、序列号和型号进行多重验证）"""
    enc_set_file = path_manager.get_enc_set_path()
    try:
        if os.path.exists(enc_set_file):
            with open(enc_set_file, "r", encoding='utf-8') as f:
                settings = json.load(f)
            
            if "usb_binding" not in settings or not settings["usb_binding"]:
                return False
            
            usb_bindings = settings["usb_binding"]
            
            # 获取当前所有USB设备信息
            current_usb_devices = get_usb_drives()
            
            # 遍历所有绑定的U盘，只要有一个验证通过就返回True
            for usb_binding in usb_bindings:
                device_id = usb_binding["DeviceID"]
                serial_number = usb_binding["SerialNumber"]
                model = usb_binding.get("Model", "")
                
                # 首先验证当前插入的USB设备是否与绑定信息匹配
                device_matched = False
                for current_device in current_usb_devices:
                    # 使用设备ID、序列号和型号进行多重验证
                    if (current_device["设备ID"] == device_id and 
                        current_device["序列号"] == serial_number and
                        (not model or current_device.get("型号", "") == model)):
                        device_matched = True
                        # logger.debug(f"找到匹配的USB设备: {device_id}, 型号: {model}")
                        break
                
                if not device_matched:
                    # logger.debug(f"未找到匹配的USB设备: {device_id}, 序列号: {serial_number}, 型号: {model}")
                    continue
                
                # 根据RequireKeyFile标记决定是否验证.key文件
                require_key_file = usb_binding.get("RequireKeyFile", True)
                
                if require_key_file:
                    # 获取U盘盘符
                    usb_drive_letter = get_usb_drive_letter(device_id)
                    if not usb_drive_letter:
                        logger.info(f"未找到绑定的U盘设备: {device_id}")
                        continue
                    
                    # 检查.key文件是否存在
                    key_path = os.path.join(usb_drive_letter, ".key")
                    if not os.path.exists(key_path):
                        logger.info(f"U盘中的密钥文件不存在: {key_path}")
                        continue
                    
                    # 读取并解密密钥文件
                    decrypted_key = read_encrypted_key_file(key_path, device_id, serial_number)
                    if decrypted_key is None:
                        logger.info(f"密钥文件解密失败: {key_path}")
                        continue
                    
                    # 验证解密后的密钥是否与保存的密钥值匹配
                    if decrypted_key == usb_binding["KeyValue"]:
                        # logger.info(f"U盘绑定验证成功: {device_id}, 型号: {model}")
                        return True
                    else:
                        logger.info(f"U盘绑定验证失败，密钥不匹配: {device_id}")
                        continue
                else:
                    # 不需要.key文件验证，直接检查key值是否为特殊标记
                    if usb_binding["KeyValue"] == "no_key_file_required":
                        # logger.info(f"U盘绑定验证成功（无需.key文件）: {device_id}, 型号: {model}")
                        return True
                    else:
                        logger.info(f"U盘绑定验证失败，key值不匹配: {device_id}")
                        continue
            
            # 所有U盘都验证失败
            logger.error("没有找到验证通过的U盘")
            return False
        
        return False
    except Exception as e:
        logger.error(f"检查USB绑定状态失败: {e}")
        return False

def read_encrypted_key_file(key_path, device_id, serial_number):
    """读取并解密.key文件内容"""
    try:
        if not os.path.exists(key_path):
            logger.error(f"密钥文件不存在: {key_path}")
            return None
        
        # 生成加密密钥（使用设备ID和序列号的组合作为加密密钥）
        encryption_key = device_id + serial_number
        
        # 读取加密的密钥数据
        with open(key_path, "rb") as f:
            encrypted_data = f.read()
        
        # 解密密钥数据
        decrypted_key = decrypt_key_data(encrypted_data, encryption_key)
        if decrypted_key is None:
            logger.error("密钥解密失败")
            return None
        
        return decrypted_key
    except Exception as e:
        logger.error(f"读取加密密钥文件失败: {e}")
        return None

class UsernameInputDialog(MessageBoxBase):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.titleLabel = SubtitleLabel('输入用户名')
        self.titleLabel.setFont(QFont(load_custom_font(), 12))
        self.usernameLineEdit = LineEdit()

        self.usernameLineEdit.setPlaceholderText('请输入用于2FA的用户名(仅限英文大小写字母和数字)')
        self.usernameLineEdit.setClearButtonEnabled(True)
        self.usernameLineEdit.setFont(QFont(load_custom_font(), 12))
        self.usernameLineEdit.returnPressed.connect(self.accept)

        # 设置输入验证器，只允许英文大小写字母
        regex = QRegExp("[A-Za-z0-9]+")
        validator = QRegExpValidator(regex, self.usernameLineEdit)
        self.usernameLineEdit.setValidator(validator)

        self.warningLabel = CaptionLabel("用户名只能包含英文大小写字母、数字且不能为空")
        self.warningLabel.setTextColor("#cf1010", QColor(255, 28, 32))

        # 将组件添加到布局中
        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(self.usernameLineEdit)
        self.viewLayout.addWidget(self.warningLabel)
        self.warningLabel.hide()

        self.widget.setMinimumWidth(500)

    def validate(self):
        """ 重写验证表单数据的方法 """
        isValid = bool(re.match(r'^[A-Za-z0-9]+$', self.usernameLineEdit.text()))
        self.warningLabel.setHidden(isValid)
        return isValid

class TwoFactorAuthDialog(MessageBoxBase):
    """ 2FA设置对话框 """
    def __init__(self, parent=None, pixmap=None, secret=None):
        super().__init__(parent)
        self.secret = secret

        # 添加说明文本
        self.titleLabel = SubtitleLabel("请扫描二维码或输入密钥到Authenticator应用程序中", self)
        self.titleLabel.setAlignment(Qt.AlignCenter)
        self.titleLabel.setFont(QFont(load_custom_font(), 12))
        self.viewLayout.addWidget(self.titleLabel)

        # 创建水平布局容器
        hLayout = QHBoxLayout()
        hLayout.setSpacing(5)
        hLayout.setContentsMargins(0, 0, 0, 0)
        
        # 添加二维码图像
        self.qrLabel = ImageLabel()
        self.qrLabel.setFixedSize(150, 150)
        if pixmap and not pixmap.isNull():
            self.qrLabel.setPixmap(pixmap)
        else:
            logger.error('生成二维码图片失败，无法设置到标签上')
            raise ValueError('生成二维码图片失败')
        self.qrLabel.setAlignment(Qt.AlignCenter)
        hLayout.addWidget(self.qrLabel)

        # 创建垂直布局容器，用于放置密钥文本和验证码输入框
        vLayout = QVBoxLayout()
        vLayout.setSpacing(5)
        vLayout.setContentsMargins(0, 0, 0, 0)

        # 添加密钥文本
        self.secretLabel = BodyLabel(f"密钥: {self.secret}", self)
        self.secretLabel.setAlignment(Qt.AlignLeft)
        self.secretLabel.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.secretLabel.setFont(QFont(load_custom_font(), 12))
        # 允许文本自动换行
        self.secretLabel.setWordWrap(True)
        vLayout.addWidget(self.secretLabel)

        # 添加验证码输入框
        self.otpInput = LineEdit(self)
        self.otpInput.setFixedSize(200, 40)
        self.otpInput.setPlaceholderText("请输入验证码")
        self.otpInput.setFont(QFont(load_custom_font(), 12))
        self.otpInput.returnPressed.connect(self.accept)
        vLayout.addWidget(self.otpInput)

        # 将垂直布局添加到水平布局中
        hLayout.addLayout(vLayout)
        hLayout.addStretch(1)

        # 将水平布局添加到主布局
        container = QWidget()
        container.setLayout(hLayout)
        self.viewLayout.addWidget(container)

        # 使用MessageBoxBase的确认按钮
        self.yesButton.setText("验证")
        self.yesButton.clicked.disconnect()
        self.yesButton.clicked.connect(self.verify_otp)
        self.cancelButton.hide()
        self.buttonLayout.insertStretch(1)

    def verify_otp(self):
        """ 验证TOTP码 """
        otp = self.otpInput.text()
        totp = pyotp.TOTP(self.secret)
        if totp.verify(otp):
            self.accept()
        else:
            InfoBar.warning(
                title="警告",
                content="验证码错误，请重新输入",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )
            self.otpInput.setFocus()

    def validate(self):
        """ 重写验证方法 """
        return True

class SimpleTwoFactorAuthDialog(MessageBoxBase):
    """ 2FA验证对话框 """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.titleLabel = SubtitleLabel('2FA验证', self)
        self.titleLabel.setFont(QFont(load_custom_font(), 12))
        self.codeLineEdit = LineEdit(self)
        self.warningLabel = CaptionLabel("验证码错误")
        self.warningLabel.setTextColor("#cf1010", QColor(255, 28, 32))

        # 设置输入框属性
        self.codeLineEdit.setPlaceholderText("请输入验证码")
        self.codeLineEdit.setClearButtonEnabled(True)
        self.codeLineEdit.setFont(QFont(load_custom_font(), 12))
        self.codeLineEdit.returnPressed.connect(self.accept)

        # 添加组件到布局
        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(self.codeLineEdit)
        self.viewLayout.addWidget(self.warningLabel)
        self.warningLabel.hide()

        # 设置对话框最小宽度
        self.widget.setMinimumWidth(350)

    def validate(self):
        """ 验证验证码 """
        code = self.codeLineEdit.text()
        
        # 从设置文件中获取2FA密钥和用户名
        settings_file = path_manager.get_enc_set_path()
        if settings_file.exists():
            with open_file(settings_file, 'r', encoding='utf-8') as f:
                try:
                    settings = json.load(f)
                    secret = settings.get("hashed_set", {}).get("2fa_secret")
                    encrypted_username = settings.get("hashed_set", {}).get("encrypted_username")
                    
                    # 检查用户名是否存在
                    if not encrypted_username:
                        self.warningLabel.setText("2FA用户名未设置，请先设置用户名")
                        self.warningLabel.setHidden(False)
                        return False
                    
                    if secret:
                        totp = pyotp.TOTP(secret)
                        isValid = totp.verify(code)
                        self.warningLabel.setHidden(isValid)
                        return isValid
                except json.JSONDecodeError:
                    pass
        
        self.warningLabel.setHidden(False)
        return False

class PasswordInputDialog(MessageBoxBase):
    """ 密码输入对话框 """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.titleLabel = SubtitleLabel('设置密码', self)
        self.titleLabel.setFont(QFont(load_custom_font(), 12))
        self.passwordLineEdit = LineEdit(self)
        self.confirmLineEdit = LineEdit(self)
        self.warningLabel = CaptionLabel("两次密码不一致")
        self.warningLabel.setTextColor("#cf1010", QColor(255, 28, 32))

        # 设置输入框属性
        self.passwordLineEdit.setEchoMode(QLineEdit.Password)
        self.passwordLineEdit.setPlaceholderText("请输入密码")
        self.passwordLineEdit.setClearButtonEnabled(True)
        self.passwordLineEdit.setFont(QFont(load_custom_font(), 12))
        self.passwordLineEdit.returnPressed.connect(self.confirmLineEdit.setFocus)
        
        self.confirmLineEdit.setEchoMode(QLineEdit.Password)
        self.confirmLineEdit.setPlaceholderText("请确认密码")
        self.confirmLineEdit.setClearButtonEnabled(True)
        self.confirmLineEdit.setFont(QFont(load_custom_font(), 12))
        self.confirmLineEdit.returnPressed.connect(self.accept)

        # 添加组件到布局
        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(self.passwordLineEdit)
        self.viewLayout.addWidget(self.confirmLineEdit)
        self.viewLayout.addWidget(self.warningLabel)
        self.warningLabel.hide()

        # 设置对话框最小宽度
        self.widget.setMinimumWidth(350)

    def validate(self):
        """ 验证密码是否一致 """
        password = self.passwordLineEdit.text()
        confirm = self.confirmLineEdit.text()
        
        isValid = password == confirm
        self.warningLabel.setHidden(isValid)
        return isValid

class PasswordDialog(MessageBoxBase):
    """ 密码对话框 """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.titleLabel = SubtitleLabel('输入密码')
        self.titleLabel.setFont(QFont(load_custom_font(), 12))
        self.passwordLineEdit = LineEdit(self)
        self.warningLabel = CaptionLabel("密码错误")
        self.warningLabel.setTextColor("#cf1010", QColor(255, 28, 32))

        # 设置输入框属性
        self.passwordLineEdit.setEchoMode(QLineEdit.Password)
        self.passwordLineEdit.setPlaceholderText("请输入密码")
        self.passwordLineEdit.setClearButtonEnabled(True)
        self.passwordLineEdit.setFont(QFont(load_custom_font(), 12))
        self.passwordLineEdit.returnPressed.connect(self.accept)

        # 添加组件到布局
        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(self.passwordLineEdit)
        self.viewLayout.addWidget(self.warningLabel)
        self.warningLabel.hide()

        # 设置对话框最小宽度
        self.widget.setMinimumWidth(350)

    def validate(self):
        """ 验证密码 """
        # 从设置文件中获取密码
        settings_file = path_manager.get_enc_set_path()
        if path_manager.file_exists(settings_file):
            with open_file(settings_file, 'r', encoding='utf-8') as f:
                try:
                    settings = json.load(f)
                    hashed_password = settings.get("hashed_set", {}).get("hashed_password")
                    salt = settings.get("hashed_set", {}).get("password_salt")
                    if hashed_password and salt:
                        password = self.passwordLineEdit.text()
                        isValid = hashed_password == hashlib.md5((password + salt).encode()).hexdigest()
                        self.warningLabel.setHidden(isValid)
                        return isValid
                except json.JSONDecodeError:
                    pass
        
        self.warningLabel.setHidden(False)
        return False

class ChangePasswordDialog(MessageBoxBase):
    """ 修改密码对话框 """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.titleLabel = SubtitleLabel('修改密码')
        self.titleLabel.setFont(QFont(load_custom_font(), 12))
        
        # 当前密码输入框
        self.currentPasswordLabel = BodyLabel('当前密码:')
        self.currentPasswordLabel.setFont(QFont(load_custom_font(), 12))
        self.currentPasswordLineEdit = LineEdit(self)
        self.currentPasswordLineEdit.setEchoMode(QLineEdit.Password)
        self.currentPasswordLineEdit.setPlaceholderText("请输入当前密码")
        self.currentPasswordLineEdit.setClearButtonEnabled(True)
        self.currentPasswordLineEdit.setFont(QFont(load_custom_font(), 12))
        
        # 新密码输入框
        self.newPasswordLabel = BodyLabel('新密码:')
        self.newPasswordLabel.setFont(QFont(load_custom_font(), 12))
        self.newPasswordLineEdit = LineEdit(self)
        self.newPasswordLineEdit.setEchoMode(QLineEdit.Password)
        self.newPasswordLineEdit.setPlaceholderText("请输入新密码")
        self.newPasswordLineEdit.setClearButtonEnabled(True)
        self.newPasswordLineEdit.setFont(QFont(load_custom_font(), 12))
        
        # 确认新密码输入框
        self.confirmPasswordLabel = BodyLabel('确认新密码:')
        self.confirmPasswordLabel.setFont(QFont(load_custom_font(), 12))
        self.confirmPasswordLineEdit = LineEdit(self)
        self.confirmPasswordLineEdit.setEchoMode(QLineEdit.Password)
        self.confirmPasswordLineEdit.setPlaceholderText("请确认新密码")
        self.confirmPasswordLineEdit.setClearButtonEnabled(True)
        self.confirmPasswordLineEdit.setFont(QFont(load_custom_font(), 12))
        
        self.warningLabel = CaptionLabel("")
        self.warningLabel.setTextColor("#cf1010", QColor(255, 28, 32))

        # 设置输入框回车键切换焦点
        self.currentPasswordLineEdit.returnPressed.connect(self.newPasswordLineEdit.setFocus)
        self.newPasswordLineEdit.returnPressed.connect(self.confirmPasswordLineEdit.setFocus)
        self.confirmPasswordLineEdit.returnPressed.connect(self.accept)

        # 添加组件到布局
        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(self.currentPasswordLabel)
        self.viewLayout.addWidget(self.currentPasswordLineEdit)
        self.viewLayout.addWidget(self.newPasswordLabel)
        self.viewLayout.addWidget(self.newPasswordLineEdit)
        self.viewLayout.addWidget(self.confirmPasswordLabel)
        self.viewLayout.addWidget(self.confirmPasswordLineEdit)
        self.viewLayout.addWidget(self.warningLabel)
        self.warningLabel.hide()

        # 设置对话框最小宽度
        self.widget.setMinimumWidth(400)

    def validate(self):
        """ 验证密码修改 """
        current_password = self.currentPasswordLineEdit.text()
        new_password = self.newPasswordLineEdit.text()
        confirm_password = self.confirmPasswordLineEdit.text()
        
        # 检查新密码和确认密码是否一致
        if new_password != confirm_password:
            self.warningLabel.setText("两次输入的新密码不一致")
            self.warningLabel.show()
            return False
        
        # 检查新密码是否为空
        if not new_password:
            self.warningLabel.setText("新密码不能为空")
            self.warningLabel.show()
            return False
        
        # 检查新密码是否与当前密码相同
        if new_password == current_password:
            self.warningLabel.setText("新密码不能与当前密码相同")
            self.warningLabel.show()
            return False
        
        # 验证当前密码是否正确
        settings_file = path_manager.get_enc_set_path()
        if path_manager.file_exists(settings_file):
            with open_file(settings_file, 'r', encoding='utf-8') as f:
                try:
                    settings = json.load(f)
                    hashed_password = settings.get("hashed_set", {}).get("hashed_password")
                    salt = settings.get("hashed_set", {}).get("password_salt")
                    if hashed_password and salt:
                        is_current_valid = hashed_password == hashlib.md5((current_password + salt).encode()).hexdigest()
                        if not is_current_valid:
                            self.warningLabel.setText("当前密码错误")
                            self.warningLabel.show()
                            return False
                except json.JSONDecodeError:
                    self.warningLabel.setText("设置文件损坏")
                    self.warningLabel.show()
                    return False
        
        self.warningLabel.hide()
        return True

class ChangeUsernameDialog(MessageBoxBase):
    """ 修改2FA用户名对话框 """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.titleLabel = SubtitleLabel('修改2FA用户名')
        self.titleLabel.setFont(QFont(load_custom_font(), 12))
        
        # 当前用户名显示
        self.currentUsernameLabel = BodyLabel('当前用户名:')
        self.currentUsernameLabel.setFont(QFont(load_custom_font(), 12))
        self.currentUsernameValue = BodyLabel('')
        self.currentUsernameValue.setFont(QFont(load_custom_font(), 12))
        
        # 新用户名输入框
        self.newUsernameLabel = BodyLabel('新用户名:')
        self.newUsernameLabel.setFont(QFont(load_custom_font(), 12))
        self.newUsernameLineEdit = LineEdit(self)
        self.newUsernameLineEdit.setPlaceholderText('请输入新的2FA用户名(仅限英文大小写字母和数字)')
        self.newUsernameLineEdit.setClearButtonEnabled(True)
        self.newUsernameLineEdit.setFont(QFont(load_custom_font(), 12))
        self.newUsernameLineEdit.returnPressed.connect(self.accept)
        
        # 设置输入验证器，只允许英文大小写字母
        regex = QRegExp("[A-Za-z0-9]+")
        validator = QRegExpValidator(regex, self.newUsernameLineEdit)
        self.newUsernameLineEdit.setValidator(validator)
        
        self.warningLabel = CaptionLabel("用户名只能包含英文大小写字母、数字且不能为空")
        self.warningLabel.setTextColor("#cf1010", QColor(255, 28, 32))

        # 添加组件到布局
        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(self.currentUsernameLabel)
        self.viewLayout.addWidget(self.currentUsernameValue)
        self.viewLayout.addWidget(self.newUsernameLabel)
        self.viewLayout.addWidget(self.newUsernameLineEdit)
        self.viewLayout.addWidget(self.warningLabel)
        self.warningLabel.hide()

        # 设置对话框最小宽度
        self.widget.setMinimumWidth(500)
        
        # 加载当前用户名
        self._load_current_username()
    
    def _load_current_username(self):
        """加载当前用户名"""
        settings_file = path_manager.get_enc_set_path()
        if path_manager.file_exists(settings_file):
            try:
                with open_file(settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    encrypted_username = settings.get("hashed_set", {}).get("encrypted_username")
                    if encrypted_username:
                        salt = 'SecRandomSalt'
                        # 这里无法直接解密，因为MD5是单向哈希
                        # 显示为已加密状态
                        self.currentUsernameValue.setText("[已加密存储]")
                    else:
                        self.currentUsernameValue.setText("[未设置]")
            except json.JSONDecodeError:
                self.currentUsernameValue.setText("[设置文件损坏]")
        else:
            self.currentUsernameValue.setText("[设置文件不存在]")

    def validate(self):
        """ 验证用户名修改 """
        new_username = self.newUsernameLineEdit.text()
        
        # 检查用户名格式
        isValid = bool(re.match(r'^[A-Za-z0-9]+$', new_username))
        if not isValid:
            self.warningLabel.setText("用户名只能包含英文大小写字母、数字且不能为空")
            self.warningLabel.show()
            return False
        
        self.warningLabel.hide()
        return True

class USBDeviceListWidget(ListWidget):
    """USB设备列表控件"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFont(QFont(load_custom_font(), 10))
        self.setMinimumHeight(150)
        self.refresh_devices()
    
    def refresh_devices(self):
        """刷新USB设备列表"""
        self.clear()
        drives = get_usb_drives()
        if not drives:
            self.addItem("未检测到USB存储设备")
            return
        
        # 获取已绑定的设备信息
        bound_device_id = None
        enc_set_file = path_manager.get_enc_set_path()
        bound_devices = []  # 存储所有已绑定的完整设备信息
        try:
            if os.path.exists(enc_set_file):
                with open(enc_set_file, "r", encoding='utf-8') as f:
                    settings = json.load(f)
                    usb_bindings = settings.get("usb_binding", [])
                    logger.info(f"从配置文件读取到usb_bindings: {usb_bindings}, 类型: {type(usb_bindings)}")
                    if usb_bindings:
                        # 收集所有已绑定的完整设备信息
                        if isinstance(usb_bindings, dict):
                            # 如果usb_bindings是字典，直接从中获取设备信息
                            device_id = usb_bindings.get("DeviceID")
                            serial_number = usb_bindings.get("SerialNumber")
                            model = usb_bindings.get("Model")
                            if device_id and serial_number:
                                bound_devices.append({
                                    "DeviceID": device_id,
                                    "SerialNumber": serial_number,
                                    "Model": model
                                })
                                logger.info(f"从字典中添加设备到绑定列表: {device_id}")
                            else:
                                logger.error("usb_bindings字典中缺少必要的设备信息")
                        elif isinstance(usb_bindings, list):
                            # 如果usb_bindings是列表，遍历处理每个元素
                            for i, usb_binding in enumerate(usb_bindings):
                                logger.info(f"处理usb_binding[{i}]: {usb_binding}, 类型: {type(usb_binding)}")
                                if isinstance(usb_binding, dict):
                                    device_id = usb_binding.get("DeviceID")
                                    serial_number = usb_binding.get("SerialNumber")
                                    model = usb_binding.get("Model")
                                    if device_id and serial_number:
                                        bound_devices.append({
                                            "DeviceID": device_id,
                                            "SerialNumber": serial_number,
                                            "Model": model
                                        })
                                        logger.info(f"添加设备到绑定列表: {device_id}")
                                    else:
                                        logger.error(f"usb_binding[{i}]中缺少必要的设备信息")
                                else:
                                    logger.error(f"usb_binding[{i}]类型错误，期望字典，实际得到: {type(usb_binding)}")
                        else:
                            logger.error(f"usb_bindings类型错误，期望字典或列表，实际得到: {type(usb_bindings)}")
        except Exception as e:
            logger.error(f"获取绑定设备信息失败: {e}")
        
        for i, drive in enumerate(drives):
            # 添加调试日志
            size_info = f"{drive['大小(字节)'] // (1024*1024*1024)}GB" if drive['大小(字节)'] else "未知大小"
            
            # 使用三重验证检查设备是否已绑定
            is_bound = False
            for bound_device in bound_devices:
                if (drive["设备ID"] == bound_device["DeviceID"] and 
                    drive["序列号"] == bound_device["SerialNumber"] and
                    (not bound_device.get("Model") or drive.get("型号", "") == bound_device.get("Model", ""))):
                    is_bound = True
                    logger.info(f"设备 {drive['设备ID']} 通过三重验证，标记为已绑定")
                    break
            
            bound_status = " [已绑定]" if is_bound else ""
            device_info = f"{i+1}. {drive['型号']} | 序列号: {drive['序列号']} | {size_info}{bound_status}"
            self.addItem(device_info)
            # 确保存储的是字典类型
            if isinstance(drive, dict):
                self.item(i).setData(Qt.UserRole, drive)
                logger.info(f"成功存储设备数据到列表项 {i}")
            else:
                logger.error(f"设备数据类型错误，无法存储到列表项 {i}: {type(drive)}")
    
    def get_selected_device(self):
        """获取选中的设备"""
        current_item = self.currentItem()
        if current_item:
            device_data = current_item.data(Qt.UserRole)
            # 添加调试日志
            logger.info(f"获取选中的设备数据: {device_data}, 类型: {type(device_data)}")
            # 确保返回的是字典类型
            if isinstance(device_data, dict):
                return device_data
            else:
                logger.error(f"设备数据类型错误，期望字典，实际得到: {type(device_data)}")
                return None
        return None

class USBBindDialog(MessageBoxBase):
    """U盘绑定对话框"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.titleLabel = SubtitleLabel('绑定U盘')
        self.titleLabel.setFont(QFont(load_custom_font(), 12))
        
        # USB设备列表
        self.deviceListLabel = BodyLabel('选择要绑定的U盘:')
        self.deviceListLabel.setFont(QFont(load_custom_font(), 12))
        self.deviceListWidget = USBDeviceListWidget()
        
        # 是否需要.key文件选项
        self.requireKeyFileCheckBox = CheckBox('需要.key文件验证')
        self.requireKeyFileCheckBox.setFont(QFont(load_custom_font(), 10))
        self.requireKeyFileCheckBox.setChecked(True)  # 默认需要.key文件
        
        # 刷新按钮
        self.refreshButton = PushButton('刷新设备列表')
        self.refreshButton.setFont(QFont(load_custom_font(), 10))
        self.refreshButton.clicked.connect(self.refresh_devices)
        
        # 继续绑定选项
        self.continueCheckBox = CheckBox('继续绑定其他设备')
        self.continueCheckBox.setFont(QFont(load_custom_font(), 10))
        self.continueCheckBox.setChecked(False)  # 默认不继续
        
        self.warningLabel = CaptionLabel("")
        self.warningLabel.setTextColor("#cf1010", QColor(255, 28, 32))
        
        # 添加组件到布局中
        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(self.deviceListLabel)
        self.viewLayout.addWidget(self.deviceListWidget)
        self.viewLayout.addWidget(self.requireKeyFileCheckBox)
        self.viewLayout.addWidget(self.continueCheckBox)
        self.viewLayout.addWidget(self.refreshButton)
        self.viewLayout.addWidget(self.warningLabel)
        self.warningLabel.hide()
        
        # 设置对话框最小宽度
        self.widget.setMinimumWidth(500)
        
        # 初始刷新设备列表
        self.refresh_devices()
    
    def refresh_devices(self):
        """刷新设备列表"""
        self.deviceListWidget.refresh_devices()
        self.warningLabel.hide()
    
    def validate(self):
        """验证绑定信息"""
        selected_device = self.deviceListWidget.get_selected_device()
        # 添加调试日志
        logger.info(f"绑定对话框获取选中的设备: {selected_device}, 类型: {type(selected_device)}")
        if not selected_device:
            self.warningLabel.setText("请选择要绑定的U盘")
            self.warningLabel.show()
            return False
        
        # 自动获取盘符
        try:
            drive_letter = get_usb_drive_letter(selected_device["设备ID"])
            logger.info(f"获取到盘符: {drive_letter}")
        except Exception as e:
            logger.error(f"获取盘符时发生错误: {e}")
            self.warningLabel.setText("获取U盘盘符时发生错误")
            self.warningLabel.show()
            return False
            
        if not drive_letter:
            self.warningLabel.setText("无法获取U盘盘符，请确保U盘已正确连接")
            self.warningLabel.show()
            return False
        
        # 获取是否需要.key文件的选项
        require_key_file = self.requireKeyFileCheckBox.isChecked()
        logger.info(f"用户选择是否需要.key文件: {require_key_file}")
        
        # 执行绑定
        try:
            if bind_usb_device(selected_device, drive_letter, require_key_file=require_key_file):
                self.warningLabel.hide()
                
                # 检查是否继续绑定其他设备
                if self.continueCheckBox.isChecked():
                    # 刷新设备列表并清空选择，让用户继续选择其他设备
                    self.refresh_devices()
                    self.deviceListWidget.clearSelection()
                    self.warningLabel.setText("绑定成功！请选择下一个要绑定的U盘")
                    self.warningLabel.setTextColor("#009688", QColor(0, 150, 136))
                    self.warningLabel.show()
                    # 返回False防止对话框关闭
                    return False
                else:
                    return True
            else:
                self.warningLabel.setText("U盘绑定失败")
                self.warningLabel.show()
                return False
        except Exception as e:
            logger.error(f"绑定过程中发生错误: {e}")
            self.warningLabel.setText("U盘绑定过程中发生错误")
            self.warningLabel.show()
            return False



class BoundUSBDeviceListWidget(ListWidget):
    """已绑定USB设备列表控件"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFont(QFont(load_custom_font(), 10))
        self.setMinimumHeight(150)
        self.refresh_devices()
    
    def refresh_devices(self):
        """刷新已绑定的USB设备列表"""
        self.clear()
        
        # 获取已绑定的设备信息
        bound_devices = []
        enc_set_file = path_manager.get_enc_set_path()
        try:
            if os.path.exists(enc_set_file):
                with open(enc_set_file, "r", encoding='utf-8') as f:
                    settings = json.load(f)
                    usb_bindings = settings.get("usb_binding", [])
                    if usb_bindings:
                        # 处理绑定设备列表
                        if isinstance(usb_bindings, dict):
                            # 如果usb_bindings是字典，直接添加
                            device_id = usb_bindings.get("DeviceID")
                            if device_id:
                                bound_devices.append({
                                    "设备ID": device_id,
                                    "序列号": usb_bindings.get("SerialNumber", "未知"),
                                    "型号": usb_bindings.get("Model", "未知型号")
                                })
                        elif isinstance(usb_bindings, list):
                            # 如果usb_bindings是列表，遍历处理每个元素
                            for usb_binding in usb_bindings:
                                if isinstance(usb_binding, dict):
                                    device_id = usb_binding.get("DeviceID")
                                    if device_id:
                                        bound_devices.append({
                                            "设备ID": device_id,
                                            "序列号": usb_binding.get("SerialNumber", "未知"),
                                            "型号": usb_binding.get("Model", "未知型号")
                                        })
        except Exception as e:
            logger.error(f"获取绑定设备信息失败: {e}")
        
        if not bound_devices:
            self.addItem("未找到已绑定的U盘")
            return
        
        for i, device in enumerate(bound_devices):
            device_info = f"{i+1}. {device['型号']} | 设备ID: {device['设备ID']} | 序列号: {device['序列号']}"
            self.addItem(device_info)
            # 存储设备数据
            self.item(i).setData(Qt.UserRole, device)
    
    def get_selected_device(self):
        """获取选中的设备"""
        current_item = self.currentItem()
        if current_item:
            device_data = current_item.data(Qt.UserRole)
            if isinstance(device_data, dict):
                return device_data
        return None

class USBUnbindDialog(MessageBoxBase):
    """U盘解绑对话框"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.titleLabel = SubtitleLabel('解绑U盘')
        self.titleLabel.setFont(QFont(load_custom_font(), 12))
        
        # USB设备列表
        self.deviceListLabel = BodyLabel('选择要解绑的U盘:')
        self.deviceListLabel.setFont(QFont(load_custom_font(), 12))
        self.deviceListWidget = BoundUSBDeviceListWidget()
        
        # 刷新按钮
        self.refreshButton = PushButton('刷新设备列表')
        self.refreshButton.setFont(QFont(load_custom_font(), 10))
        self.refreshButton.clicked.connect(self.refresh_devices)
        
        # 继续解绑选项
        self.continueCheckBox = CheckBox('继续解绑其他设备')
        self.continueCheckBox.setFont(QFont(load_custom_font(), 10))
        self.continueCheckBox.setChecked(False)  # 默认不继续
        
        self.warningLabel = CaptionLabel("")
        self.warningLabel.setTextColor("#cf1010", QColor(255, 28, 32))
        
        # 添加组件到布局中
        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(self.deviceListLabel)
        self.viewLayout.addWidget(self.deviceListWidget)
        self.viewLayout.addWidget(self.continueCheckBox)
        self.viewLayout.addWidget(self.refreshButton)
        self.viewLayout.addWidget(self.warningLabel)
        self.warningLabel.hide()
        
        # 设置对话框最小宽度
        self.widget.setMinimumWidth(500)
        
        # 设置按钮文本
        self.yesButton.setText('确认解绑')
        self.cancelButton.setText('取消')
        
        # 初始刷新设备列表
        self.refresh_devices()
    
    def refresh_devices(self):
        """刷新设备列表"""
        self.deviceListWidget.refresh_devices()
        self.warningLabel.hide()
    
    def validate(self):
        """验证解绑操作"""
        selected_device = self.deviceListWidget.get_selected_device()
        if not selected_device:
            self.warningLabel.setText("请选择要解绑的U盘")
            self.warningLabel.show()
            return False
        
        # 检查是否为已绑定的设备
        if not self.is_device_bound(selected_device):
            self.warningLabel.setText("该U盘未绑定，无需解绑")
            self.warningLabel.show()
            return False
        
        # 执行解绑（无需插入U盘，直接从绑定列表移除）
        if unbind_usb(selected_device["设备ID"], selected_device["序列号"]):
            self.warningLabel.hide()
            
            # 检查是否继续解绑其他设备
            if self.continueCheckBox.isChecked():
                # 刷新设备列表并清空选择，让用户继续选择其他设备
                self.refresh_devices()
                self.deviceListWidget.clearSelection()
                self.warningLabel.setText("解绑成功！请选择下一个要解绑的U盘")
                self.warningLabel.setTextColor("#009688", QColor(0, 150, 136))
                self.warningLabel.show()
                # 返回False防止对话框关闭
                return False
            else:
                return True
        else:
            self.warningLabel.setText("U盘解绑失败")
            self.warningLabel.show()
            return False
    
    def is_device_bound(self, device):
        """检查设备是否已绑定"""
        try:
            # 获取设备ID，处理不同的数据格式
            device_id = None
            if isinstance(device, dict):
                device_id = device.get("设备ID")
            elif isinstance(device, str):
                device_id = device
            else:
                logger.error(f"设备数据类型错误: {type(device)}, 值: {device}")
                return False
            
            if not device_id:
                logger.error("无法获取设备ID")
                return False
                
            enc_set_file = path_manager.get_enc_set_path()
            if os.path.exists(enc_set_file):
                with open(enc_set_file, "r", encoding='utf-8') as f:
                    settings = json.load(f)
                    usb_bindings = settings.get("usb_binding", [])
                    if usb_bindings:
                        # 检查设备是否在已绑定的U盘列表中
                        for usb_binding in usb_bindings:
                            if isinstance(usb_binding, dict) and usb_binding.get("DeviceID") == device_id:
                                return True
                            elif isinstance(usb_binding, str) and usb_binding == device_id:
                                return True
            return False
        except Exception as e:
            logger.error(f"检查设备绑定状态失败: {e}, 设备类型: {type(device)}, 设备值: {device}")
            return False

class password_SettingsCard(GroupHeaderCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("密码设置")
        self.setBorderRadius(8)
        create_hidden_folder(secrandom_dir / "app" / "SecRandom")
        self.settings_file = path_manager.get_enc_set_path()
        self.secret_dir = secrandom_dir
        self.default_settings = {
            "start_password_enabled": False,
            "encrypt_setting_enabled": False,
            "two_factor_auth": False,
            "exit_verification_enabled": False,
            "restart_verification_enabled": False,
            "show_hide_verification_enabled": False,
            "usb_auth_enabled": False
        }

        # 密码功能开关
        self.start_password_switch = SwitchButton()
        self.start_password_switch.setOnText("开启")
        self.start_password_switch.setOffText("关闭")
        self.start_password_switch.checkedChanged.connect(self.start_password_switch_checked)
        self.start_password_switch.setFont(QFont(load_custom_font(), 12))

        # 设置是否启用加密相关设置/名单文件开关
        self.encrypt_setting_switch = SwitchButton()
        self.encrypt_setting_switch.setOnText("开启")
        self.encrypt_setting_switch.setOffText("关闭")
        self.encrypt_setting_switch.checkedChanged.connect(lambda: self.verify_password_for_action('加密设置', 'encrypt'))
        self.encrypt_setting_switch.setFont(QFont(load_custom_font(), 12))

        # 设置2FA开关
        self.two_factor_switch = SwitchButton()
        self.two_factor_switch.setOnText("启用")
        self.two_factor_switch.setOffText("关闭")
        self.two_factor_switch.checkedChanged.connect(self.on_2fa_changed)
        self.two_factor_switch.setFont(QFont(load_custom_font(), 12))

        # 导出密钥按钮
        self.export_key_button = PushButton('导出密钥')
        self.export_key_button.setFont(QFont(load_custom_font(), 12))
        self.export_key_button.clicked.connect(self.export_key_file)

        # 设置密码按钮
        self.set_password_button = PushButton('设置/修改密码')
        self.set_password_button.setFont(QFont(load_custom_font(), 12))
        self.set_password_button.clicked.connect(self.show_password_dialog)
        
        # 修改2FA用户名按钮
        self.change_username_button = PushButton('修改2FA用户名')
        self.change_username_button.setFont(QFont(load_custom_font(), 12))
        self.change_username_button.clicked.connect(self.show_change_username_dialog)

        # 退出软件是否需要验证密码开关
        self.exit_verification_switch = SwitchButton()
        self.exit_verification_switch.setOnText("开启")
        self.exit_verification_switch.setOffText("关闭")
        self.exit_verification_switch.checkedChanged.connect(lambda: self.verify_password_for_action('退出软件需要密码', 'exit'))
        self.exit_verification_switch.setFont(QFont(load_custom_font(), 12))

        # 重启软件是否需要验证密码开关
        self.restart_verification_switch = SwitchButton()
        self.restart_verification_switch.setOnText("开启")
        self.restart_verification_switch.setOffText("关闭")
        self.restart_verification_switch.checkedChanged.connect(lambda: self.verify_password_for_action('重启软件需要密码', 'restart'))
        self.restart_verification_switch.setFont(QFont(load_custom_font(), 12))

        # 暂时显示/隐藏悬浮窗是否需要验证密码开关
        self.show_hide_verification_switch = SwitchButton()
        self.show_hide_verification_switch.setOnText("开启")
        self.show_hide_verification_switch.setOffText("关闭")
        self.show_hide_verification_switch.checkedChanged.connect(lambda: self.verify_password_for_action('显示/隐藏悬浮窗需要密码', 'show_hide'))
        self.show_hide_verification_switch.setFont(QFont(load_custom_font(), 12))

        # U盘认证开关
        self.usb_auth_switch = SwitchButton()
        self.usb_auth_switch.setOnText("启用")
        self.usb_auth_switch.setOffText("关闭")
        self.usb_auth_switch.checkedChanged.connect(lambda: self.on_usb_auth_changed())
        self.usb_auth_switch.setFont(QFont(load_custom_font(), 12))

        # 绑定U盘按钮
        self.bind_usb_button = PushButton('绑定U盘')
        self.bind_usb_button.setFont(QFont(load_custom_font(), 12))
        self.bind_usb_button.clicked.connect(self.show_bind_usb_dialog)

        # 解绑U盘按钮
        self.unbind_usb_button = PushButton('解绑U盘')
        self.unbind_usb_button.setFont(QFont(load_custom_font(), 12))
        self.unbind_usb_button.clicked.connect(self.show_unbind_usb_dialog)

        # 添加组件到分组中
        self.addGroup(get_theme_icon("ic_fluent_person_passkey_20_filled"), "密码功能", "启用密码保护功能，提升软件安全性", self.start_password_switch)
        self.addGroup(get_theme_icon("ic_fluent_password_20_filled"), "设置/修改密码", "创建或更改SecRandom的登录密码", self.set_password_button)
        self.addGroup(get_theme_icon("ic_fluent_document_key_20_filled"), '密钥导出', '导出加密密钥文件用于验证', self.export_key_button)
        self.addGroup(get_theme_icon("ic_fluent_certificate_20_filled"), "双重认证", "启用双因素认证(2FA)增强安全性", self.two_factor_switch)
        self.addGroup(get_theme_icon("ic_fluent_person_20_filled"), "修改用户名", "更改双因素认证的标识用户名", self.change_username_button)
        self.addGroup(get_theme_icon("ic_fluent_tv_usb_20_filled"), "U盘认证", "启用U盘作为身份验证设备，增强软件安全性", self.usb_auth_switch)
        self.addGroup(get_theme_icon("ic_fluent_usb_stick_20_filled"), "绑定U盘", "选择并绑定U盘作为专属验证设备", self.bind_usb_button)
        self.addGroup(get_theme_icon("ic_fluent_usb_plug_20_filled"), "解绑U盘", "移除已绑定的U盘验证设备（支持设备不存在解绑）", self.unbind_usb_button)
        # self.addGroup(FIF.VPN, "数据加密", "加密设置和名单文件", self.encrypt_setting_switch)
        self.addGroup(get_theme_icon("ic_fluent_arrow_reset_20_filled"), "重启软件验证", "重启软件时需要验证身份", self.restart_verification_switch)
        self.addGroup(get_theme_icon("ic_fluent_arrow_exit_20_filled"), "退出软件验证", "退出软件时需要验证身份", self.exit_verification_switch)
        self.addGroup(get_theme_icon("ic_fluent_window_ad_20_filled"), "悬浮窗验证", "显示/隐藏悬浮窗时需要验证身份", self.show_hide_verification_switch)


        self.load_settings()
        
        # 初始化USB监控线程属性
        self.usb_monitor_thread = None
    
    def __del__(self):
        """析构函数，确保USB监控线程正确停止"""
        try:
            if hasattr(self, 'usb_monitor_thread') and self.usb_monitor_thread:
                self.usb_monitor_thread.stop()
                self.usb_monitor_thread = None
        except Exception as e:
            logger.error(f"停止USB监控线程时出错: {e}")

    def show_info_bar(self, status, title, content, duration=3000, parent=None):
        """
        :param status: 状态类型，'success'或'warning'或'error'
        :param title: 标题
        :param content: 内容
        :param duration: 显示时长(毫秒)
        :param parent: 父窗口
        """
        if status == 'success':
            InfoBar.success(
                title=title,
                content=content,
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=duration,
                parent=parent or self
            )
        elif status == 'error':
            InfoBar.error(
                title=title,
                content=content,
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=duration,
                parent=parent or self
            )
        elif status == 'warning':
            InfoBar.warning(
                title=title,
                content=content,
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=duration,
                parent=parent or self
            )

    def verify_password_for_action(self, action_type, type):
        """验证密码和2FA"""
        if not path_manager.file_exists(self.settings_file):
            return False

        try:
            with open_file(self.settings_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                hashed_set = settings.get("hashed_set", {})
                if hashed_set.get("verification_start") == True:
                    if not hashed_set.get("hashed_password") or not hashed_set.get("password_salt"):
                        self.show_info_bar('error', '错误', '请先设置密码', 3000, self)
                        # 阻止开关状态改变，恢复到原始状态
                        if type == 'exit':
                            original_state = hashed_set.get("exit_verification_enabled", False)
                            self.exit_verification_switch.blockSignals(True)
                            self.exit_verification_switch.setChecked(original_state)
                            self.exit_verification_switch.blockSignals(False)
                        elif type == 'restart':
                            original_state = hashed_set.get("restart_verification_enabled", False)
                            self.restart_verification_switch.blockSignals(True)
                            self.restart_verification_switch.setChecked(original_state)
                            self.restart_verification_switch.blockSignals(False)
                        elif type == 'show_hide':
                            original_state = hashed_set.get("show_hide_verification_enabled", False)
                            self.show_hide_verification_switch.blockSignals(True)
                            self.show_hide_verification_switch.setChecked(original_state)
                            self.show_hide_verification_switch.blockSignals(False)
                        elif type == 'encrypt':
                            original_state = hashed_set.get("encrypt_setting_enabled", False)
                            self.encrypt_setting_switch.blockSignals(True)
                            self.encrypt_setting_switch.setChecked(original_state)
                            self.encrypt_setting_switch.blockSignals(False)
                        return False

                    dialog = PasswordDialog(self)
                    dialog.yesButton.setText("确认")
                    dialog.cancelButton.setText("取消")
                    if dialog.exec_() != QDialog.Accepted:
                        # 用户取消密码验证，恢复到原始状态
                        if type == 'exit':
                            original_state = hashed_set.get("exit_verification_enabled", False)
                            self.exit_verification_switch.blockSignals(True)
                            self.exit_verification_switch.setChecked(original_state)
                            self.exit_verification_switch.blockSignals(False)
                            self.show_info_bar('warning', '警告', f'{action_type}功能设置已取消', 3000, self)
                        elif type == 'restart':
                            original_state = hashed_set.get("restart_verification_enabled", False)
                            self.restart_verification_switch.blockSignals(True)
                            self.restart_verification_switch.setChecked(original_state)
                            self.restart_verification_switch.blockSignals(False)
                            self.show_info_bar('warning', '警告', f'{action_type}功能设置已取消', 3000, self)
                        elif type == 'show_hide':
                            original_state = hashed_set.get("show_hide_verification_enabled", False)
                            self.show_hide_verification_switch.blockSignals(True)
                            self.show_hide_verification_switch.setChecked(original_state)
                            self.show_hide_verification_switch.blockSignals(False)
                            self.show_info_bar('warning', '警告', f'{action_type}功能设置已取消', 3000, self)
                        elif type == 'encrypt':
                            original_state = hashed_set.get("encrypt_setting_enabled", False)
                            self.encrypt_setting_switch.blockSignals(True)
                            self.encrypt_setting_switch.setChecked(original_state)
                            self.encrypt_setting_switch.blockSignals(False)
                            self.show_info_bar('warning', '警告', f'{action_type}功能设置已取消', 3000, self)
                        return False

                    if hashed_set.get("two_factor_auth", False):
                        dialog = SimpleTwoFactorAuthDialog(self)
                        dialog.yesButton.setText("确认")
                        dialog.cancelButton.setText("取消")
                        if dialog.exec_() != QDialog.Accepted:
                            # 用户取消2FA验证，恢复到原始状态
                            if type == 'exit':
                                original_state = hashed_set.get("exit_verification_enabled", False)
                                self.exit_verification_switch.blockSignals(True)
                                self.exit_verification_switch.setChecked(original_state)
                                self.exit_verification_switch.blockSignals(False)
                                self.show_info_bar('warning', '警告', f'{action_type}功能设置已取消', 3000, self)
                            elif type == 'restart':
                                original_state = hashed_set.get("restart_verification_enabled", False)
                                self.restart_verification_switch.blockSignals(True)
                                self.restart_verification_switch.setChecked(original_state)
                                self.restart_verification_switch.blockSignals(False)
                                self.show_info_bar('warning', '警告', f'{action_type}功能设置已取消', 3000, self)
                            elif type == 'show_hide':
                                original_state = hashed_set.get("show_hide_verification_enabled", False)
                                self.show_hide_verification_switch.blockSignals(True)
                                self.show_hide_verification_switch.setChecked(original_state)
                                self.show_hide_verification_switch.blockSignals(False)
                                self.show_info_bar('warning', '警告', f'{action_type}功能设置已取消', 3000, self)
                            elif type == 'encrypt':
                                original_state = hashed_set.get("encrypt_setting_enabled", False)
                                self.encrypt_setting_switch.blockSignals(True)
                                self.encrypt_setting_switch.setChecked(original_state)
                                self.encrypt_setting_switch.blockSignals(False)
                                self.show_info_bar('warning', '警告', f'{action_type}功能设置已取消', 3000, self)
                            return False

                    # 验证成功，更新对应的开关状态
                    if type == 'exit':
                        # 获取开关当前状态
                        current_state = self.exit_verification_switch.isChecked()
                        hashed_set['exit_verification_enabled'] = current_state
                    elif type == 'restart':
                        # 获取开关当前状态
                        current_state = self.restart_verification_switch.isChecked()
                        hashed_set['restart_verification_enabled'] = current_state
                    elif type == 'show_hide':
                        # 获取开关当前状态
                        current_state = self.show_hide_verification_switch.isChecked()
                        hashed_set['show_hide_verification_enabled'] = current_state
                    elif type == 'encrypt':
                        # 获取开关当前状态
                        current_state = self.encrypt_setting_switch.isChecked()
                        hashed_set['encrypt_setting_enabled'] = current_state
                    
                    # 保存更新后的设置
                    with open_file(self.settings_file, 'w', encoding='utf-8') as f:
                        json.dump(settings, f, indent=4)
                    
                    self.show_info_bar('success', '功能设置成功', f'{action_type}功能设置成功', 3000, self)
                    return True

        except Exception as e:
            logger.error(f"验证失败: {e}")
            return False

    def show_password_dialog(self):
        if not path_manager.file_exists(self.settings_file):
            self.show_info_bar('error', '错误', '设置文件不存在', 3000, self)
            return

        try:
            with open_file(self.settings_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                hashed_set = settings.get("hashed_set", {})
                if hashed_set.get("verification_start") == True:
                    with open_file(self.settings_file, 'r', encoding='utf-8') as f:
                        settings = json.load(f)
                        hashed_set = settings.get("hashed_set", {})
                        if not hashed_set.get("hashed_password") or not hashed_set.get("password_salt"):
                            dialog = PasswordInputDialog(self)
                            dialog.yesButton.setText("确认")
                            dialog.cancelButton.setText("取消")
                            if dialog.exec():
                                self.validate_and_save_password(dialog, dialog.passwordLineEdit, dialog.confirmLineEdit)
                        elif hashed_set.get("hashed_password") and hashed_set.get("password_salt"):
                            dialog = PasswordDialog(self)
                            dialog.yesButton.setText("确认")
                            dialog.cancelButton.setText("取消")
                            if dialog.exec_() == QDialog.Accepted:
                                if hashed_set.get("two_factor_auth") == True:
                                    dialog = SimpleTwoFactorAuthDialog(self)
                                    dialog.yesButton.setText("确认")
                                    dialog.cancelButton.setText("取消")
                                    if dialog.exec_() == QDialog.Accepted:
                                        dialog = PasswordInputDialog(self)
                                        dialog.yesButton.setText("确认")
                                        dialog.cancelButton.setText("取消")
                                        if dialog.exec():
                                            self.validate_and_save_password(dialog, dialog.passwordLineEdit, dialog.confirmLineEdit)
                                        return
                                    else:
                                        self.show_info_bar('warning', '警告', '密码设置已取消', 3000, self)
                                        return
                                else:
                                    dialog = PasswordInputDialog(self)
                                    dialog.yesButton.setText("确认")
                                    dialog.cancelButton.setText("取消")
                                    if dialog.exec():
                                        self.validate_and_save_password(dialog, dialog.passwordLineEdit, dialog.confirmLineEdit)
                                    return
                            else:
                                self.show_info_bar('warning', '警告', '密码设置已取消', 3000, self)
                                return
        except json.JSONDecodeError as e:
            self.show_info_bar('error', '错误', '设置文件损坏', 3000, self)
            return

    def show_change_username_dialog(self):
        """显示修改2FA用户名对话框"""
        if not path_manager.file_exists(self.settings_file):
            self.show_info_bar('error', '错误', '设置文件不存在', 3000, self)
            return

        try:
            with open_file(self.settings_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                hashed_set = settings.get("hashed_set", {})

            # 检查是否启用了密码功能
            if hashed_set.get("verification_start") != True:
                self.show_info_bar('warning', '提示', '请先启用密码功能', 3000, self)
                return

            # 检查是否启用了2FA
            if not hashed_set.get("two_factor_auth", False):
                self.show_info_bar('warning', '提示', '请先启用2FA功能', 3000, self)
                return

            # 验证当前密码
            dialog = PasswordDialog(self)
            dialog.yesButton.setText("确认")
            dialog.cancelButton.setText("取消")
            if dialog.exec_() != QDialog.Accepted:
                return

            # 验证2FA
            dialog = SimpleTwoFactorAuthDialog(self)
            dialog.yesButton.setText("确认")
            dialog.cancelButton.setText("取消")
            if dialog.exec_() != QDialog.Accepted:
                return

            # 显示修改用户名对话框
            dialog = ChangeUsernameDialog(self)
            dialog.yesButton.setText("确认")
            dialog.cancelButton.setText("取消")
            if dialog.exec():
                if dialog.validate():
                    new_username = dialog.usernameLineEdit.text().strip()
                    if self.update_username(new_username):
                        self.show_info_bar('success', '用户名修改成功', '2FA用户名已成功修改', 3000, self)
                    else:
                        self.show_info_bar('error', '用户名修改失败', '2FA用户名修改失败', 3000, self)

        except Exception as e:
            logger.error(f"修改用户名对话框显示失败: {e}")
            self.show_info_bar('error', '错误', f'修改用户名对话框显示失败: {str(e)}', 3000, self)

    def update_username(self, new_username):
        """更新2FA用户名"""
        if not path_manager.file_exists(self.settings_file):
            self.show_info_bar('error', '错误', '设置文件不存在', 3000, self)
            return False

        try:
            with open_file(self.settings_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                hashed_set = settings.get("hashed_set", {})

            # 生成新的用户名哈希（使用固定盐值）
            username_salt = 'SecRandomSalt'
            hashed_username = hashlib.md5((new_username + username_salt).encode('utf-8')).hexdigest()

            # 更新设置
            hashed_set['encrypted_username'] = hashed_username

            settings['hashed_set'] = hashed_set

            with open_file(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=4)

            return True

        except Exception as e:
            logger.error(f"用户名修改失败: {e}")
            return False

    def validate_and_save_password(self, dialog, password_input, confirm_password_input):
        password = password_input.text()
        confirm_password = confirm_password_input.text()

        if password != confirm_password:
            self.show_info_bar('error', '错误', "两次输入的密码不一致", 3000, self)
            return

        # 生成随机盐值
        salt = secrets.token_hex(16)
        hashed_password = hashlib.md5((password + salt).encode()).hexdigest()

        # 保存密码和盐值到设置文件
        existing_settings = {}
        if path_manager.file_exists(self.settings_file):
            try:
                with open_file(self.settings_file, 'r', encoding='utf-8') as f:
                    existing_settings = json.load(f)
            except json.JSONDecodeError:
                existing_settings = {}

        if "hashed_set" not in existing_settings:
            existing_settings["hashed_set"] = {}
        existing_settings["hashed_set"]["hashed_password"] = hashed_password
        existing_settings["hashed_set"]["password_salt"] = salt

        with open_file(self.settings_file, 'w', encoding='utf-8') as f:
            json.dump(existing_settings, f, indent=4)

        logger.info("密码设置成功")
        self.show_info_bar('success', '成功', "密码设置成功", 3000, self)
        dialog.accept()

    def start_password_switch_checked(self):
        if not path_manager.file_exists(self.settings_file):
            self.show_info_bar('error', '错误', '设置文件不存在', 3000, self)
            self.start_password_switch.setChecked(False)
            return

        try:
            with open_file(self.settings_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                hashed_set = settings.get("hashed_set", {})
                if hashed_set.get("verification_start") == True:
                    with open_file(self.settings_file, 'r', encoding='utf-8') as f:
                        settings = json.load(f)
                        hashed_set = settings.get("hashed_set", {})
                        if not hashed_set.get("hashed_password") or not hashed_set.get("password_salt"):
                            self.show_info_bar('warning', '警告', '请先设置密码', 3000, self)
                            self.start_password_switch.setChecked(False)
                            return
                        elif hashed_set.get("hashed_password") and hashed_set.get("password_salt"):
                            dialog = PasswordDialog(self)
                            dialog.yesButton.setText("确认")
                            dialog.cancelButton.setText("取消")
                            if dialog.exec_() == QDialog.Accepted:
                                if hashed_set.get("two_factor_auth") == True:
                                    dialog = SimpleTwoFactorAuthDialog(self)
                                    dialog.yesButton.setText("确认")
                                    dialog.cancelButton.setText("取消")
                                    if dialog.exec_() == QDialog.Accepted:
                                        self.save_settings()
                                        return
                                    else:
                                        # 用户取消2FA验证，恢复开关状态
                                        original_state = hashed_set.get("start_password_enabled", False)
                                        self.start_password_switch.blockSignals(True)
                                        self.start_password_switch.setChecked(original_state)
                                        self.start_password_switch.blockSignals(False)
                                        self.show_info_bar('warning', '警告', '启动设置需密码已取消', 3000, self)
                                        return
                                else:
                                    self.save_settings()
                                    return
                            else:
                                # 用户取消密码验证，恢复开关状态
                                original_state = hashed_set.get("start_password_enabled", False)
                                self.start_password_switch.blockSignals(True)
                                self.start_password_switch.setChecked(original_state)
                                self.start_password_switch.blockSignals(False)
                                self.show_info_bar('warning', '警告', '启动设置需密码已取消', 3000, self)
                                return
        except json.JSONDecodeError as e:
            self.show_info_bar('error', '错误', '设置文件损坏', 3000, self)
            self.start_password_switch.setChecked(False)
            return

    def on_2fa_changed(self):
        if not path_manager.file_exists(self.settings_file):
            self.show_info_bar('error', '错误', '设置文件不存在', 3000, self)
            self.two_factor_switch.blockSignals(True)
            self.two_factor_switch.setChecked(False)
            self.two_factor_switch.blockSignals(False)
            return

        try:
            with open_file(self.settings_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                hashed_set = settings.get("hashed_set", {})
                if hashed_set.get("verification_start") == True:
                    if not hashed_set.get("hashed_password") or not hashed_set.get("password_salt"):
                        self.show_info_bar('warning', '警告', '请先设置密码', 3000, self)
                        self.two_factor_switch.blockSignals(True)
                        self.two_factor_switch.setChecked(False)
                        self.two_factor_switch.blockSignals(False)
                        self.save_settings()
                        return
                    elif hashed_set.get("hashed_password") and hashed_set.get("password_salt"):
                        dialog = PasswordDialog(self)
                        dialog.yesButton.setText("确认")
                        dialog.cancelButton.setText("取消")
                        if dialog.exec_() == QDialog.Accepted:
                            if hashed_set.get("two_factor_auth") == True:
                                # 关闭2FA
                                dialog = SimpleTwoFactorAuthDialog(self)
                                dialog.yesButton.setText("确认")
                                dialog.cancelButton.setText("取消")
                                if dialog.exec_() == QDialog.Accepted:
                                    # 验证成功，删除2FA相关设置
                                    existing_settings = {}
                                    try:
                                        with open_file(self.settings_file, 'r', encoding='utf-8') as f:
                                            existing_settings = json.load(f)
                                    except json.JSONDecodeError:
                                        existing_settings = {}
                                    
                                    if "hashed_set" in existing_settings:
                                        existing_settings["hashed_set"].pop("encrypted_username", None)
                                        existing_settings["hashed_set"].pop("2fa_secret", None)
                                    
                                    with open_file(self.settings_file, 'w', encoding='utf-8') as f:
                                        json.dump(existing_settings, f, indent=4)
                                    
                                    self.save_settings()
                                    self.show_info_bar('success', '成功', '2FA已关闭', 3000, self)
                                else:
                                    # 用户取消验证，恢复开关状态
                                    original_state = hashed_set.get("two_factor_auth", False)
                                    self.two_factor_switch.blockSignals(True)
                                    self.two_factor_switch.setChecked(original_state)
                                    self.two_factor_switch.blockSignals(False)
                                    self.show_info_bar('warning', '警告', '2FA关闭已取消', 3000, self)
                                    return
                            else:
                                # 开启2FA
                                existing_settings = {}
                                try:
                                    with open_file(self.settings_file, 'r', encoding='utf-8') as f:
                                        existing_settings = json.load(f)
                                except json.JSONDecodeError:
                                    existing_settings = {}
                                
                                if "hashed_set" not in existing_settings or "2fa_secret" not in existing_settings["hashed_set"]:
                                    self.setup_2fa()
                                    # setup_2fa方法中已经处理了保存和状态设置
                                else:
                                    self.save_settings()
                                return
                        else:
                            # 用户取消密码验证，恢复开关状态
                            original_state = hashed_set.get("two_factor_auth", False)
                            self.two_factor_switch.blockSignals(True)
                            self.two_factor_switch.setChecked(original_state)
                            self.two_factor_switch.blockSignals(False)
                            self.show_info_bar('warning', '警告', '2FA设置已取消', 3000, self)
                            return
        except json.JSONDecodeError as e:
            self.show_info_bar('error', '错误', '设置文件损坏', 3000, self)
            self.two_factor_switch.blockSignals(True)
            self.two_factor_switch.setChecked(False)
            self.two_factor_switch.blockSignals(False)
            return

    def setup_2fa(self):
        """初始化2FA设置"""
        global username
        try:
            dialog = UsernameInputDialog(self)
            dialog.yesButton.setText("确认")
            dialog.cancelButton.setText("取消")
            if dialog.exec():
                username = dialog.usernameLineEdit.text()
                if not username:
                    self.show_info_bar('warning', '警告', '用户名不能为空', 3000, self)
                    self.two_factor_switch.blockSignals(True)
                    self.two_factor_switch.setChecked(False)
                    self.two_factor_switch.blockSignals(False)
                    return
            else:
                # 用户取消用户名输入，重置开关状态
                self.show_info_bar('warning', '警告', '2FA设置已取消', 3000, self)
                self.two_factor_switch.blockSignals(True)
                self.two_factor_switch.setChecked(False)
                self.two_factor_switch.blockSignals(False)
                return

            salt = 'SecRandomSalt'
            hashed_username = hashlib.md5((username + salt).encode()).hexdigest()

            os.makedirs(self.secret_dir, exist_ok=True)

            existing_settings = {}
            try:
                with open_file(self.settings_file, 'r', encoding='utf-8') as f:
                    existing_settings = json.load(f)
            except json.JSONDecodeError:
                existing_settings = {}

            if "hashed_set" not in existing_settings:
                existing_settings["hashed_set"] = {}
            existing_settings["hashed_set"]["encrypted_username"] = hashed_username

            with open_file(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(existing_settings, f, indent=4)

            # 生成密钥但暂不保存，等待用户验证成功后再保存
            self.secret = pyotp.random_base32()
            pixmap = generate_qr_code(self.secret, username)
            
            if pixmap:
                # 创建自定义2FA对话框
                dialog = TwoFactorAuthDialog(self, pixmap, self.secret)
                dialog.yesButton.setText("确认")
                dialog.cancelButton.setText("取消")
                if dialog.exec():
                    # 用户验证成功，才保存密钥到设置文件
                    try:
                        with open_file(self.settings_file, 'r', encoding='utf-8') as f:
                            existing_settings = json.load(f)
                        
                        if "hashed_set" not in existing_settings:
                            existing_settings["hashed_set"] = {}
                        existing_settings["hashed_set"]["2fa_secret"] = self.secret

                        with open_file(self.settings_file, 'w', encoding='utf-8') as f:
                            json.dump(existing_settings, f, indent=4)
                            
                        self.show_info_bar('success', '成功', '2FA设置成功', 3000, self)
                    except Exception as e:
                        logger.error(f"保存2FA密钥失败: {e}")
                        self.show_info_bar('error', '错误', '2FA密钥保存失败', 3000, self)
                        self.two_factor_switch.setChecked(False)
                else:
                    # 用户取消验证，不保存密钥，重置开关状态
                    self.show_info_bar('warning', '警告', '2FA设置已取消', 3000, self)
                    self.two_factor_switch.blockSignals(True)
                    self.two_factor_switch.setChecked(False)
                    self.two_factor_switch.blockSignals(False)
            else:
                self.show_info_bar('error', '错误', "2FA设置失败", 3000, self)
                self.two_factor_switch.blockSignals(True)
                self.two_factor_switch.setChecked(False)
                self.two_factor_switch.blockSignals(False)
        except Exception as e:
            self.show_info_bar('error', '错误', f"2FA设置失败: {str(e)}", 3000, self)
            self.two_factor_switch.blockSignals(True)
            self.two_factor_switch.setChecked(False)
            self.two_factor_switch.blockSignals(False)
            return

    def export_key_file(self):
        if not path_manager.file_exists(self.settings_file):
            self.show_info_bar('error', '错误', '设置文件不存在', 3000, self)
            return

        try:
            with open_file(self.settings_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                hashed_set = settings.get("hashed_set", {})
                if not hashed_set.get("hashed_password") or not hashed_set.get("password_salt"):
                    self.show_info_bar('warning', '警告', '请先设置密码', 3000, self)
                    return
                elif hashed_set.get("hashed_password") and hashed_set.get("password_salt"):
                    dialog = PasswordDialog(self)
                    dialog.yesButton.setText("确认")
                    dialog.cancelButton.setText("取消")
                    if dialog.exec_() == QDialog.Accepted:
                        if hashed_set.get("two_factor_auth") == True:
                            dialog = SimpleTwoFactorAuthDialog(self)
                            dialog.yesButton.setText("确认")
                            dialog.cancelButton.setText("取消")
                            if dialog.exec_() == QDialog.Accepted:
                                path = QFileDialog.getSaveFileName(self, '保存密钥文件', 'SecRandom', 'Key Files (*.key)')[0]
                                if path:
                                    hashed_password = settings.get("hashed_set", {}).get("hashed_password")
                                    if hashed_password:
                                        self._save_key_file(path, hashed_password)
                                    else:
                                        self.show_info_bar('error', '错误', '未找到密码', 3000, self)
                            else:
                                self.show_info_bar('warning', '警告', '导出密钥已取消', 3000, self)
                                return
                        else:
                            path = QFileDialog.getSaveFileName(self, '保存密钥文件', 'SecRandom', 'Key Files (*.key)')[0]
                            if path:
                                hashed_password = settings.get("hashed_set", {}).get("hashed_password")
                                if hashed_password:
                                    self._save_key_file(path, hashed_password)
                                else:
                                    self.show_info_bar('error', '错误', '未找到密码', 3000, self)
                        return
                    else:
                        return
        except json.JSONDecodeError as e:
            self.show_info_bar('error', '错误', f'设置文件损坏: {e}', 3000, self)
            return

    def _save_key_file(self, path, hashed_password):
        try:
            with open_file(path, 'w') as f:
                f.write(hashed_password)
        except Exception as e:
            self.show_info_bar('error', '错误', f"密钥导出失败: {str(e)}", 3000, self)


    def on_usb_auth_changed(self):
        """U盘认证开关状态改变处理"""
        if not path_manager.file_exists(self.settings_file):
            self.show_info_bar('error', '错误', '设置文件不存在', 3000, self)
            self.usb_auth_switch.blockSignals(True)
            self.usb_auth_switch.setChecked(False)
            self.usb_auth_switch.blockSignals(False)
            return

        try:
            with open_file(self.settings_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                hashed_set = settings.get("hashed_set", {})
                usb_bindings = settings.get("usb_binding", [])
                if hashed_set.get("verification_start") == True:
                    if not hashed_set.get("hashed_password") or not hashed_set.get("password_salt"):
                        self.show_info_bar('warning', '警告', '请先设置密码', 3000, self)
                        self.usb_auth_switch.blockSignals(True)
                        self.usb_auth_switch.setChecked(False)
                        self.usb_auth_switch.blockSignals(False)
                        self.save_settings()
                        return
                    elif hashed_set.get("hashed_password") and hashed_set.get("password_salt"):
                        dialog = PasswordDialog(self)
                        dialog.yesButton.setText("确认")
                        dialog.cancelButton.setText("取消")
                        if dialog.exec_() == QDialog.Accepted:
                            if self.usb_auth_switch.isChecked():
                                # 开启U盘认证
                                if not usb_bindings:
                                    self.show_info_bar('warning', '警告', '请先绑定U盘', 3000, self)
                                    self.usb_auth_switch.blockSignals(True)
                                    self.usb_auth_switch.setChecked(False)
                                    self.usb_auth_switch.blockSignals(False)
                                    return
                                self.save_settings()
                                self.show_info_bar('success', '成功', 'U盘认证已启用', 3000, self)
                            else:
                                # 关闭U盘认证
                                self.save_settings()
                                self.show_info_bar('success', '成功', 'U盘认证已关闭', 3000, self)
                        else:
                            # 用户取消密码验证，恢复开关状态
                            original_state = hashed_set.get("usb_auth_enabled", False)
                            self.usb_auth_switch.blockSignals(True)
                            self.usb_auth_switch.setChecked(original_state)
                            self.usb_auth_switch.blockSignals(False)
                            self.show_info_bar('warning', '警告', 'U盘认证设置已取消', 3000, self)
                            return
        except json.JSONDecodeError as e:
            self.show_info_bar('error', '错误', '设置文件损坏', 3000, self)
            self.usb_auth_switch.blockSignals(True)
            self.usb_auth_switch.setChecked(False)
            self.usb_auth_switch.blockSignals(False)
            return

    def show_bind_usb_dialog(self):
        """显示U盘绑定对话框"""
        if not path_manager.file_exists(self.settings_file):
            self.show_info_bar('error', '错误', '设置文件不存在', 3000, self)
            return

        try:
            with open_file(self.settings_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                hashed_set = settings.get("hashed_set", {})
                if hashed_set.get("verification_start") == True:
                    if not hashed_set.get("hashed_password") or not hashed_set.get("password_salt"):
                        self.show_info_bar('warning', '警告', '请先设置密码', 3000, self)
                        return
                    elif hashed_set.get("hashed_password") and hashed_set.get("password_salt"):
                        dialog = PasswordDialog(self)
                        dialog.yesButton.setText("确认")
                        dialog.cancelButton.setText("取消")
                        if dialog.exec_() == QDialog.Accepted:
                            bind_dialog = USBBindDialog(self)
                            bind_dialog.yesButton.setText("确认绑定")
                            bind_dialog.cancelButton.setText("取消")
                            if bind_dialog.exec_() == QDialog.Accepted:
                                self.show_info_bar('success', '成功', 'U盘绑定成功', 3000, self)
                        else:
                            self.show_info_bar('warning', '警告', 'U盘绑定已取消', 3000, self)
        except json.JSONDecodeError as e:
            self.show_info_bar('error', '错误', '设置文件损坏', 3000, self)



    def show_unbind_usb_dialog(self):
        """显示U盘解绑对话框"""
        if not path_manager.file_exists(self.settings_file):
            self.show_info_bar('error', '错误', '设置文件不存在', 3000, self)
            return

        try:
            with open_file(self.settings_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                hashed_set = settings.get("hashed_set", {})
                usb_bindings = settings.get("usb_binding", [])
                if hashed_set.get("verification_start") == True:
                    if not hashed_set.get("hashed_password") or not hashed_set.get("password_salt"):
                        self.show_info_bar('warning', '警告', '请先设置密码', 3000, self)
                        return
                    elif hashed_set.get("hashed_password") and hashed_set.get("password_salt"):
                        dialog = PasswordDialog(self)
                        dialog.yesButton.setText("确认")
                        dialog.cancelButton.setText("取消")
                        if dialog.exec_() == QDialog.Accepted:
                            unbind_dialog = USBUnbindDialog(self)
                            if unbind_dialog.exec_() == QDialog.Accepted:
                                self.show_info_bar('success', '成功', 'U盘解绑成功', 3000, self)
                                # 如果U盘认证已启用，自动关闭
                                if self.usb_auth_switch.isChecked() and not usb_bindings:
                                    self.usb_auth_switch.blockSignals(True)
                                    self.usb_auth_switch.setChecked(False)
                                    self.usb_auth_switch.blockSignals(False)
                                    self.save_settings()
                                    self.show_info_bar('warning', '警告', 'U盘认证已自动关闭', 3000, self)
                        else:
                            self.show_info_bar('warning', '警告', 'U盘解绑已取消', 3000, self)
        except json.JSONDecodeError as e:
            self.show_info_bar('error', '错误', '设置文件损坏', 3000, self)

    def load_settings(self):
        try:
            # 使用缓存避免重复读取文件
            if hasattr(self, '_settings_cache') and self._settings_cache:
                settings = self._settings_cache
            else:
                if path_manager.file_exists(self.settings_file):
                    with open_file(self.settings_file, 'r', encoding='utf-8') as f:
                        settings = json.load(f)
                        # 缓存设置以避免重复读取
                        self._settings_cache = settings
                else:
                    settings = {"hashed_set": {}, "usb_binding": []}
                    self._settings_cache = settings
            
            hashed_set_settings = settings.get("hashed_set", {})
            usb_bindings = settings.get("usb_binding", [])

            # 批量设置开关状态，减少UI更新次数
            self.start_password_switch.blockSignals(True)
            self.encrypt_setting_switch.blockSignals(True)
            self.two_factor_switch.blockSignals(True)
            self.exit_verification_switch.blockSignals(True)
            self.restart_verification_switch.blockSignals(True)
            self.show_hide_verification_switch.blockSignals(True)
            self.usb_auth_switch.blockSignals(True)

            self.start_password_switch.setChecked(
                hashed_set_settings.get("start_password_enabled", self.default_settings["start_password_enabled"])
            )
            self.encrypt_setting_switch.setChecked(
                hashed_set_settings.get("encrypt_setting_enabled", self.default_settings["encrypt_setting_enabled"])
            )
            self.two_factor_switch.setChecked(
                hashed_set_settings.get("two_factor_auth", self.default_settings["two_factor_auth"])
            )
            self.exit_verification_switch.setChecked(
                hashed_set_settings.get("exit_verification_enabled", self.default_settings["exit_verification_enabled"])
            )
            self.restart_verification_switch.setChecked(
                hashed_set_settings.get("restart_verification_enabled", self.default_settings["restart_verification_enabled"])
            )
            self.show_hide_verification_switch.setChecked(
                hashed_set_settings.get("show_hide_verification_enabled", self.default_settings["show_hide_verification_enabled"])
            )
            
            usb_auth_enabled = settings.get("usb_auth_enabled", self.default_settings["usb_auth_enabled"])
            # 检查是否有绑定的U盘，如果没有则关闭U盘认证开关
            if not usb_bindings and usb_auth_enabled:
                usb_auth_enabled = False
                logger.info("没有绑定的U盘，已自动关闭U盘认证开关")
            
            self.usb_auth_switch.setChecked(usb_auth_enabled)

            # 恢复信号连接
            self.start_password_switch.blockSignals(False)
            self.encrypt_setting_switch.blockSignals(False)
            self.two_factor_switch.blockSignals(False)
            self.exit_verification_switch.blockSignals(False)
            self.restart_verification_switch.blockSignals(False)
            self.show_hide_verification_switch.blockSignals(False)
            self.usb_auth_switch.blockSignals(False)
            
            logger.info("安全设置加载完成")
            
            # 如果U盘认证已启用，启动监控线程
            if usb_auth_enabled:
                self.start_usb_monitoring()
                
        except Exception as e:
            logger.error(f"加载设置时出错: {e}")
            # 出错时使用默认设置
            self._apply_default_settings()

    def _apply_default_settings(self):
        """应用默认设置"""
        self.start_password_switch.setChecked(self.default_settings["start_password_enabled"])
        self.encrypt_setting_switch.setChecked(self.default_settings["encrypt_setting_enabled"])
        self.two_factor_switch.setChecked(self.default_settings["two_factor_auth"])
        self.exit_verification_switch.setChecked(self.default_settings["exit_verification_enabled"])
        self.restart_verification_switch.setChecked(self.default_settings["restart_verification_enabled"])
        self.show_hide_verification_switch.setChecked(self.default_settings["show_hide_verification_enabled"])
        self.usb_auth_switch.setChecked(self.default_settings["usb_auth_enabled"])
        logger.info("已应用默认安全设置")

    def save_settings(self):
        # 先读取现有设置
        _existing_settings = {}
        try:
            if path_manager.file_exists(self.settings_file):
                with open_file(self.settings_file, 'r', encoding='utf-8') as f:
                    _existing_settings = json.load(f)
        except json.JSONDecodeError:
            _existing_settings = {}

        # 更新hashed_set部分的所有设置
        if "hashed_set" not in _existing_settings:
            _existing_settings["hashed_set"] = {}

        # 移除自动重置开关状态的逻辑，让各个方法自行管理开关状态
        # 这样可以避免与已经正确实现的blockSignals机制产生冲突

        _existing_settings["hashed_set"].update({
            "start_password_enabled": self.start_password_switch.isChecked(),
            "encrypt_setting_enabled": self.encrypt_setting_switch.isChecked(),
            "two_factor_auth": self.two_factor_switch.isChecked(),
            "exit_verification_enabled": self.exit_verification_switch.isChecked(),
            "restart_verification_enabled": self.restart_verification_switch.isChecked(),
            "show_hide_verification_enabled": self.show_hide_verification_switch.isChecked()
        })
        
        # 更新U盘认证设置（存储在根级别，不在hashed_set中）
        _existing_settings["usb_auth_enabled"] = self.usb_auth_switch.isChecked()

        os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)

        with open_file(self.settings_file, 'w', encoding='utf-8') as f:
            json.dump(_existing_settings, f, indent=4)

    def start_usb_monitoring(self):
        """启动USB监控线程"""
        try:
            # 如果已有线程在运行，先停止它
            if hasattr(self, 'usb_monitor_thread') and self.usb_monitor_thread and self.usb_monitor_thread.isRunning():
                self.usb_monitor_thread.stop()
                self.usb_monitor_thread.usb_removed.disconnect()
                self.usb_monitor_thread = None
            
            # 创建新线程，但不立即启动，使用QTimer延迟启动以避免阻塞主线程
            self.usb_monitor_thread = USBMonitorThread(self)
            self.usb_monitor_thread.usb_removed.connect(self.on_usb_removed)
            # 使用QTimer.singleShot异步启动线程，避免阻塞主线程
            QTimer.singleShot(100, self.usb_monitor_thread.start)
            logger.info("USB监控线程已异步启动")
        except Exception as e:
            logger.error(f"启动USB监控线程时出错: {e}")

    def on_usb_removed(self):
        """USB设备被移除时的处理"""
        self.show_info_bar('warning', '警告', '绑定的U盘已被移除', 3000, self)
        try:
            with open_file(self.settings_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                usb_bindings = settings.get("usb_binding", [])
                if not usb_bindings and self.usb_auth_switch.isChecked():
                    self.usb_auth_switch.blockSignals(True)
                    self.usb_auth_switch.setChecked(False)
                    self.usb_auth_switch.blockSignals(False)
                    self.save_settings()
                    self.show_info_bar('warning', '警告', 'U盘认证已自动关闭', 3000, self)
        except json.JSONDecodeError as e:
            self.show_info_bar('error', '错误', '设置文件损坏', 3000, self)
            self.usb_auth_switch.blockSignals(True)
            self.usb_auth_switch.setChecked(False)
            self.usb_auth_switch.blockSignals(False)
            return


class USBMonitorThread(QThread):
    """USB监控线程，用于监控绑定的U盘是否被移除"""
    usb_removed = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.running = True
        self._force_stop = False
        self.check_interval = 2000  # 每2秒检查一次
        self.setTerminationEnabled(True)  # 允许强制终止
        
    def run(self):
        """线程运行方法"""
        try:
            while self.running and not self._force_stop:
                if not is_usb_bound():
                    self.usb_removed.emit()
                    break
                self.msleep(self.check_interval)
        except Exception as e:
            logger.error(f"USB监控线程异常: {e}")
    
    def stop(self):
        """停止线程"""
        self.running = False
        self._force_stop = True
        if self.isRunning():
            # 先尝试优雅退出
            self.quit()
            if not self.wait(1500):  # 等待最多1.5秒
                # 如果优雅退出失败，强制终止
                self.terminate()
                self.wait(1000)  # 等待终止完成
                if self.isRunning():
                    logger.error("USB监控线程强制终止失败")
    
    def __del__(self):
        """析构函数，确保线程正确停止"""
        try:
            self.stop()
        except:
            pass  # 析构函数中忽略所有异常