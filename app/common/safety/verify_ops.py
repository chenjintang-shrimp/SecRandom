from app.tools.settings_access import readme_settings_async
from app.common.safety.password import is_configured as password_is_configured
from app.page_building.security_window import create_verify_password_window


def should_require_password(op: str) -> bool:
    if not password_is_configured():
        return False
    if not readme_settings_async("basic_safety_settings", "safety_switch"):
        return False
    key_map = {
        "show_hide_floating_window": "show_hide_floating_window_switch",
        "restart": "restart_switch",
        "exit": "exit_switch",
    }
    k = key_map.get(op)
    if not k:
        return False
    return bool(readme_settings_async("basic_safety_settings", k))


def require_and_run(op: str, parent, func):
    if not should_require_password(op):
        func()
        return
    create_verify_password_window(on_verified=func)

