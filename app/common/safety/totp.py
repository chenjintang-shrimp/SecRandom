import json
import pyotp

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
    rec = d.get("totp")
    return isinstance(rec, dict) and bool(rec.get("secret"))

def generate_secret():
    return pyotp.random_base32()

def set_totp(secret: str | None, issuer: str = "SecRandom", account: str = "user") -> str:
    if not secret:
        secret = generate_secret()
    d = _read()
    d["totp"] = {"secret": secret, "issuer": issuer, "account": account}
    _write(d)
    totp = pyotp.TOTP(secret)
    return totp.provisioning_uri(name=account, issuer_name=issuer)

def verify(code: str, window: int = 1) -> bool:
    d = _read()
    rec = d.get("totp")
    if not rec:
        return False
    secret = rec.get("secret")
    if not secret:
        return False
    totp = pyotp.TOTP(secret)
    try:
        return bool(totp.verify(code, valid_window=window))
    except Exception:
        return False
