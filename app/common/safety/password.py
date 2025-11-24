import json
import os
import base64
import hmac
import hashlib

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

def is_configured():
    d = _read()
    rec = d.get("password")
    return isinstance(rec, dict) and bool(rec.get("hash")) and bool(rec.get("salt"))

def set_password(plain: str):
    salt = os.urandom(16)
    iterations = 200000
    dk = hashlib.pbkdf2_hmac("sha256", plain.encode("utf-8"), salt, iterations)
    rec = {
        "algorithm": "pbkdf2_sha256",
        "iterations": iterations,
        "salt": base64.b64encode(salt).decode("ascii"),
        "hash": base64.b64encode(dk).decode("ascii"),
    }
    d = _read()
    d["password"] = rec
    _write(d)

def verify_password(plain: str) -> bool:
    d = _read()
    rec = d.get("password")
    if not rec:
        return False
    try:
        salt = base64.b64decode(rec.get("salt", ""))
        iterations = int(rec.get("iterations", 200000))
        expected = base64.b64decode(rec.get("hash", ""))
    except Exception:
        return False
    dk = hashlib.pbkdf2_hmac("sha256", plain.encode("utf-8"), salt, iterations)
    return hmac.compare_digest(dk, expected)

def clear_password():
    d = _read()
    if "password" in d:
        del d["password"]
    _write(d)
