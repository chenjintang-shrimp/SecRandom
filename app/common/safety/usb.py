import json
import string
import ctypes
from pathlib import Path
import os
import platform
import warnings
from loguru import logger

from app.tools.path_utils import get_config_path, get_settings_path, ensure_dir, open_file, file_exists
from app.tools.secure_store import read_secrets, write_secrets
import hashlib
import base64
import zlib
import uuid
try:
    from Cryptodome.Cipher import AES  # pycryptodome
except Exception:
    try:
        from Crypto.Cipher import AES  # legacy name
    except Exception:
        AES = None

def _secrets_path():
    return get_settings_path("secrets.json")

def _legacy_path():
    return get_config_path("security", "secrets.json")

def _read():
    return read_secrets()

def _write(d):
    write_secrets(d)

def _get_logical_drive_strings() -> list:
    try:
        GetLogicalDriveStringsW = ctypes.windll.kernel32.GetLogicalDriveStringsW
        # 先获取需要的缓冲区大小
        size = GetLogicalDriveStringsW(0, None)
        if size <= 0:
            return []
        buf = ctypes.create_unicode_buffer(size)
        GetLogicalDriveStringsW(size, buf)
        drives = buf.value.split("\x00")
        return [d for d in drives if d]
    except Exception:
        return []

def _candidate_letters() -> list:
    letters = []
    try:
        for lt in list_usb_drive_letters_wmi():
            letters.append(lt)
    except Exception:
        pass
    try:
        for lt in list_removable_drives():
            letters.append(lt)
    except Exception:
        pass
    try:
        for root in _get_logical_drive_strings():
            if root and len(root) >= 1:
                letters.append(root[0])
    except Exception:
        pass
    out = sorted(list(set([ch for ch in letters if isinstance(ch, str) and len(ch) == 1])))
    logger.debug(f"候选盘符数量：{len(out)}")
    return out

def list_removable_drives():
    if platform.system() == "Windows":
        letters = []
        GetDriveTypeW = ctypes.windll.kernel32.GetDriveTypeW
        for root in _get_logical_drive_strings():
            try:
                t = GetDriveTypeW(root)
                if t == 2:  # DRIVE_REMOVABLE
                    # 进一步确认介质就绪（存在有效卷序列号）
                    letter = root[0]
                    try:
                        serial = get_volume_serial(letter)
                        if serial and serial != "00000000":
                            letters.append(letter)
                    except Exception:
                        # 无法获取序列号时也视为存在
                        letters.append(letter)
            except Exception:
                pass
        # 去重
        out = sorted(list(set(letters)))
        logger.debug(f"可移动盘符数量：{len(out)}")
        return out
    return []

def list_usb_drive_letters_wmi() -> list:
    if platform.system() != "Windows":
        return []
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", SyntaxWarning)
            import wmi
            import pythoncom
    except Exception:
        return []
    letters = []
    try:
        pythoncom.CoInitialize()
        c = wmi.WMI()
        for disk in c.Win32_DiskDrive(InterfaceType="USB"):
            try:
                parts = c.Win32_DiskPartition(DiskIndex=disk.Index)
                for part in parts:
                    try:
                        for assoc in part.associators("Win32_LogicalDiskToPartition"):
                            if hasattr(assoc, "DeviceID"):
                                did = assoc.DeviceID  # e.g. 'E:'
                                if isinstance(did, str) and len(did) >= 2:
                                    letters.append(did[0])
                    except Exception:
                        pass
            except Exception:
                pass
        out = sorted(list(set(letters)))
        logger.debug(f"WMI 枚举USB盘符数量：{len(out)}")
        return out
    except Exception:
        logger.warning("WMI 枚举USB盘符失败")
        return []
    finally:
        try:
            pythoncom.CoUninitialize()
        except Exception:
            pass


def is_drive_removable(letter: str) -> bool:
    try:
        t = ctypes.windll.kernel32.GetDriveTypeW(f"{letter}:\\")
        return t == 2
    except Exception:
        return False

def get_volume_serial(letter: str) -> str:
    buf_name = ctypes.create_unicode_buffer(256)
    vol_serial = ctypes.c_uint()
    max_comp_len = ctypes.c_uint()
    fs_flags = ctypes.c_uint()
    fs_name = ctypes.create_unicode_buffer(256)
    ctypes.windll.kernel32.GetVolumeInformationW(
        f"{letter}:\\",
        buf_name,
        ctypes.sizeof(buf_name),
        ctypes.byref(vol_serial),
        ctypes.byref(max_comp_len),
        ctypes.byref(fs_flags),
        fs_name,
        ctypes.sizeof(fs_name),
    )
    if vol_serial.value:
        return f"{vol_serial.value:08X}"
    # 尝试获取卷GUID作为备用唯一标识
    try:
        buf = ctypes.create_unicode_buffer(64)
        ok = ctypes.windll.kernel32.GetVolumeNameForVolumeMountPointW(f"{letter}:\\", buf, ctypes.sizeof(buf))
        if ok:
            guid = buf.value  # 形如 "\\\\?\Volume{GUID}\\"
            return guid.strip().upper()
    except Exception:
        pass
    # 最终回退：QueryDosDevice 映射路径的哈希
    try:
        size = 256
        buf = ctypes.create_unicode_buffer(size)
        ok = ctypes.windll.kernel32.QueryDosDeviceW(f"{letter}:", buf, size)
        if ok:
            path = buf.value
            h = hashlib.sha256(path.encode("utf-8", errors="ignore")).hexdigest().upper()
            return f"DEV-{h}"
    except Exception:
        pass
    return "00000000"

def get_volume_label(letter: str) -> str:
    buf_name = ctypes.create_unicode_buffer(256)
    vol_serial = ctypes.c_uint()
    max_comp_len = ctypes.c_uint()
    fs_flags = ctypes.c_uint()
    fs_name = ctypes.create_unicode_buffer(256)
    try:
        ctypes.windll.kernel32.GetVolumeInformationW(
            f"{letter}:\\",
            buf_name,
            ctypes.sizeof(buf_name),
            ctypes.byref(vol_serial),
            ctypes.byref(max_comp_len),
            ctypes.byref(fs_flags),
            fs_name,
            ctypes.sizeof(fs_name),
        )
        return buf_name.value
    except Exception:
        return ""

def bind(volume_serial: str):
    d = _read()
    rec = d.get("usb") or {}
    arr = rec.get("volume_serials") or []
    if volume_serial not in arr:
        arr.append(volume_serial)
    rec["volume_serials"] = arr
    d["usb"] = rec
    _write(d)
    logger.debug("绑定序列号成功")

def bind_with_options(volume_serial: str, require_key_file: bool = False, key_value: str | None = None, name: str | None = None):
    d = _read()
    rec = d.get("usb") or {}
    # 兼容旧字段
    arr = rec.get("volume_serials") or []
    if volume_serial not in arr:
        arr.append(volume_serial)
    rec["volume_serials"] = arr
    # 新增绑定列表
    bindings = rec.get("bindings") or []
    exists = False
    for b in bindings:
        if isinstance(b, dict) and b.get("serial") == volume_serial:
            exists = True
            b["require_key_file"] = bool(require_key_file)
            if require_key_file:
                b["key_value"] = key_value or b.get("key_value")
            break
    if not exists:
        bindings.append({
            "serial": volume_serial,
            "require_key_file": bool(require_key_file),
            "key_value": key_value if require_key_file else None,
            "name": name,
        })
    rec["bindings"] = bindings
    d["usb"] = rec
    _write(d)
    logger.debug("绑定设备记录已更新")

def get_bindings() -> list:
    d = _read()
    rec = d.get("usb") or {}
    return rec.get("bindings") or []

def has_binding() -> bool:
    try:
        d = _read()
        rec = d.get("usb") or {}
        arr = rec.get("volume_serials") or []
        bindings = rec.get("bindings") or []
        if arr:
            logger.debug("存在绑定序列号")
            return True
        for b in bindings:
            if isinstance(b, dict) and b.get("serial"):
                logger.debug("存在绑定设备记录")
                return True
        return False
    except Exception:
        logger.warning("读取绑定信息失败")
        return False

def get_serial_volume_label(serial: str) -> str | None:
    try:
        for root in _get_logical_drive_strings():
            letter = root[0]
            vid = get_volume_serial(letter)
            if vid == serial:
                name = get_volume_label(letter)
                if name:
                    return f"{name} ({letter}:)"
                return f"({letter}:)"
        return None
    except Exception:
        return None

def _read_key_file(letter: str) -> str | None:
    try:
        p = f"{letter}:\\SecRandom_safety.key"
        if not os.path.exists(p):
            return None
        with open(p, "rb") as f:
            data = f.read()
        # 解密或解码
        try:
            if data[:3] == b"SK1":
                # AES-EAX
                nonce = data[3:19]
                ct = data[19:]
                key = _derive_key_for_keyfile(letter)
                cipher = AES.new(key, AES.MODE_EAX, nonce=nonce) if AES else None
                if cipher is None:
                    return None
                token = cipher.decrypt(ct)
                return token.decode("utf-8", errors="ignore")
            elif data[:3] == b"SK0":
                b64 = data[3:]
                raw = base64.b64decode(b64)
                key = _derive_key_for_keyfile(letter)
                stream = hashlib.sha256(key).digest()
                out = bytes(b ^ stream[i % len(stream)] for i, b in enumerate(raw))
                return out.decode("utf-8", errors="ignore")
            else:
                return data.decode("utf-8", errors="ignore")
        except Exception:
            return None
    except Exception:
        return None

def write_key_file(letter: str, token: str) -> bool:
    try:
        p = f"{letter}:\\SecRandom_safety.key"
        try:
            if os.path.exists(p):
                os.remove(p)
            # 清理旧文件名兼容
            old = f"{letter}:\\.key"
            if os.path.exists(old):
                os.remove(old)
        except Exception:
            pass
        key = _derive_key_for_keyfile(letter)
        payload = None
        if AES:
            nonce = os.urandom(16)
            cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)
            ct = cipher.encrypt(token.encode("utf-8"))
            payload = b"SK1" + nonce + ct
        else:
            stream = hashlib.sha256(key).digest()
            raw = token.encode("utf-8")
            obf = bytes(b ^ stream[i % len(stream)] for i, b in enumerate(raw))
            payload = b"SK0" + base64.b64encode(obf)
        with open(p, "wb") as f:
            f.write(payload)
        _set_hidden(p)
        logger.debug(f"写入U盘密钥文件成功：{letter}:")
        return True
    except Exception:
        logger.warning(f"写入U盘密钥文件失败：{letter}:")
        return False

def unbind(volume_serial: str | None = None):
    d = _read()
    rec = d.get("usb") or {}
    arr = rec.get("volume_serials") or []
    if volume_serial is None:
        arr = []
    else:
        arr = [s for s in arr if s != volume_serial]
    rec["volume_serials"] = arr
    bindings = rec.get("bindings") or []
    if volume_serial is None:
        bindings = []
    else:
        bindings = [b for b in bindings if b.get("serial") != volume_serial]
    rec["bindings"] = bindings
    d["usb"] = rec
    _write(d)
    logger.debug("解绑操作已执行")

def remove_key_file(letter: str) -> bool:
    try:
        p = f"{letter}:\\SecRandom_safety.key"
        if os.path.exists(p):
            os.remove(p)
            logger.debug(f"删除U盘密钥文件：{letter}:")
            return True
        # 兼容旧文件名
        old = f"{letter}:\\.key"
        if os.path.exists(old):
            os.remove(old)
            logger.debug(f"删除旧密钥文件：{letter}:")
            return True
    except Exception:
        pass
    return False

def remove_key_file_for_serial(serial: str) -> bool:
    removed = False
    try:
        for root in _get_logical_drive_strings():
            letter = root[0]
            try:
                vid = get_volume_serial(letter)
                if vid == serial:
                    if remove_key_file(letter):
                        removed = True
            except Exception:
                pass
    except Exception:
        pass
    if removed:
        logger.debug("按序列号删除密钥文件成功")
    return removed

def is_bound_connected() -> bool:
    d = _read()
    rec = d.get("usb") or {}
    arr = rec.get("volume_serials") or []
    bindings = rec.get("bindings") or []
    if not arr and not bindings:
        return False
    serials = set(arr)
    for b in bindings:
        try:
            s = b.get("serial")
            if s:
                serials.add(s)
        except Exception:
            pass
    if platform.system() == "Windows":
        for letter in _candidate_letters():
            try:
                vid = get_volume_serial(letter)
                if not vid or vid not in serials:
                    continue
                need_key = False
                key_expected = None
                for b in bindings:
                    try:
                        if b.get("serial") == vid and b.get("require_key_file"):
                            need_key = True
                            key_expected = b.get("key_value")
                            break
                    except Exception:
                        pass
                if not need_key:
                    logger.debug("检测到绑定设备已连接")
                    return True
                key_actual = _read_key_file(letter)
                if key_actual and key_expected and key_actual == key_expected:
                    logger.debug("检测到绑定设备及密钥文件匹配")
                    return True
            except Exception:
                pass
        return False
    ids = _linux_usb_ids()
    for s in serials:
        if s in ids:
            return True
    return False

def is_bound_present() -> bool:
    d = _read()
    rec = d.get("usb") or {}
    arr = rec.get("volume_serials") or []
    bindings = rec.get("bindings") or []
    if not arr and not bindings:
        return False
    serials = set(arr)
    for b in bindings:
        try:
            s = b.get("serial")
            if s:
                serials.add(s)
        except Exception:
            pass
    if platform.system() == "Windows":
        for letter in _candidate_letters():
            try:
                vid = get_volume_serial(letter)
                if vid and vid in serials:
                    logger.debug("检测到绑定设备存在")
                    return True
            except Exception:
                pass
        return False
    ids = _linux_usb_ids()
    for s in serials:
        if s in ids:
            return True
    return False

def get_bound_serials() -> list:
    d = _read()
    rec = d.get("usb") or {}
    arr = rec.get("volume_serials") or []
    return list(arr)

def is_serial_connected(serial: str) -> bool:
    if platform.system() == "Windows":
        try:
            for letter in _candidate_letters():
                try:
                    vid = get_volume_serial(letter)
                    if vid != serial:
                        continue
                    bindings = get_bindings()
                    need_key = False
                    key_expected = None
                    for b in bindings:
                        try:
                            if b.get("serial") == serial and b.get("require_key_file"):
                                need_key = True
                                key_expected = b.get("key_value")
                                break
                        except Exception:
                            pass
                    if not need_key:
                        logger.debug("序列号设备已连接")
                        return True
                    key_actual = _read_key_file(letter)
                    if key_actual and key_expected and key_actual == key_expected:
                        logger.debug("序列号设备及密钥匹配")
                        return True
                except Exception:
                    pass
        except Exception:
            pass
        return False
    try:
        return serial in _linux_usb_ids()
    except Exception:
        return False

def _linux_usb_ids() -> set:
    ids = set()
    base = "/dev/disk/by-id"
    try:
        if os.path.isdir(base):
            for name in os.listdir(base):
                if name.startswith("usb-"):
                    ids.add(name)
    except Exception:
        pass
    return ids

def _set_hidden(path: str) -> None:
    try:
        if platform.system() == "Windows":
            FILE_ATTRIBUTE_HIDDEN = 0x2
            FILE_ATTRIBUTE_SYSTEM = 0x4
            ctypes.windll.kernel32.SetFileAttributesW(path, FILE_ATTRIBUTE_HIDDEN | FILE_ATTRIBUTE_SYSTEM)
    except Exception:
        pass

def _get_machine_guid() -> str:
    if platform.system() == "Windows":
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Cryptography")
            val, _ = winreg.QueryValueEx(key, "MachineGuid")
            winreg.CloseKey(key)
            return str(val)
        except Exception:
            pass
    try:
        return str(uuid.getnode())
    except Exception:
        return "SecRandom"

def _platform_key() -> bytes:
    base = _get_machine_guid() + str(get_settings_path(""))
    return hashlib.sha256(base.encode("utf-8")).digest()[:16]

def _encrypt_payload(data: bytes, key: bytes) -> bytes:
    if AES:
        nonce = os.urandom(16)
        cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)
        ct = cipher.encrypt(data)
        return nonce + ct
    stream = hashlib.sha256(key).digest()
    obf = bytes(b ^ stream[i % len(stream)] for i, b in enumerate(data))
    return base64.b64encode(obf)

def _decrypt_payload(payload: bytes, key: bytes) -> bytes:
    if AES:
        nonce = payload[:16]
        ct = payload[16:]
        cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)
        return cipher.decrypt(ct)
    raw = base64.b64decode(payload)
    stream = hashlib.sha256(key).digest()
    data = bytes(b ^ stream[i % len(stream)] for i, b in enumerate(raw))
    return data

def _derive_key_for_keyfile(letter: str) -> bytes:
    serial = get_volume_serial(letter) or ""
    base = serial + _get_machine_guid()
    return hashlib.sha256(base.encode("utf-8")).digest()[:16]
