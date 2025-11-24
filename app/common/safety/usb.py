import json
import string
import ctypes
from pathlib import Path
import os
import platform

from app.tools.path_utils import get_config_path, get_settings_path, ensure_dir, open_file, file_exists

def _secrets_path():
    return get_settings_path("secrets.json")

def _legacy_path():
    return get_config_path("security", "secrets.json")

def _read():
    p = _secrets_path()
    if file_exists(p):
        with open_file(p, "r", encoding="utf-8") as f:
            return json.load(f)
    lp = _legacy_path()
    if file_exists(lp):
        with open_file(lp, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def _write(d):
    ensure_dir(_secrets_path().parent)
    with open_file(_secrets_path(), "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=4)

def list_removable_drives():
    if platform.system() == "Windows":
        letters = []
        GetDriveTypeW = ctypes.windll.kernel32.GetDriveTypeW
        for ch in string.ascii_uppercase:
            root = f"{ch}:\\"
            p = Path(root)
            if p.exists():
                t = GetDriveTypeW(root)
                if t == 2:
                    letters.append(ch)
        return letters
    return []

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
    return f"{vol_serial.value:08X}"

def bind(volume_serial: str):
    d = _read()
    rec = d.get("usb") or {}
    arr = rec.get("volume_serials") or []
    if volume_serial not in arr:
        arr.append(volume_serial)
    rec["volume_serials"] = arr
    d["usb"] = rec
    _write(d)

def unbind(volume_serial: str | None = None):
    d = _read()
    rec = d.get("usb") or {}
    arr = rec.get("volume_serials") or []
    if volume_serial is None:
        arr = []
    else:
        arr = [s for s in arr if s != volume_serial]
    rec["volume_serials"] = arr
    d["usb"] = rec
    _write(d)

def is_bound_connected() -> bool:
    d = _read()
    rec = d.get("usb") or {}
    arr = rec.get("volume_serials") or []
    if not arr:
        return False
    if platform.system() == "Windows":
        for lt in list_removable_drives():
            try:
                if get_volume_serial(lt) in arr:
                    return True
            except Exception:
                pass
        return False
    ids = _linux_usb_ids()
    for s in arr:
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
            for lt in list_removable_drives():
                try:
                    if get_volume_serial(lt) == serial:
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
