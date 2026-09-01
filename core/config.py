import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = BASE_DIR / "assets"
DATA_DIR = BASE_DIR / "data"
BACKUP_DIR = DATA_DIR / "backups"

ASSETS_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)
BACKUP_DIR.mkdir(exist_ok=True)

DB_PATH = DATA_DIR / "staffroot.db"

APP_NAME = "StaffRoot"
APP_VERSION = "0.11.0"
APP_ICON = ASSETS_DIR / "staffroot.ico"

LOCAL_CONFIG_PATH = BASE_DIR / "staffroot.local.json"

DEFAULT_LOCAL_CONFIG = {
    "identity_provider_name": "",
    "identity_base_url": "",
    "identity_api_token": "",
    "identity_sync_enabled": False,
}

LEGACY_CONFIG_KEYS = {
    "admin_center_base_url": "identity_base_url",
    "admin_center_api_key": "identity_api_token",
    "sync_enabled": "identity_sync_enabled",
}


def normalize_local_config(data: dict | None) -> dict:
    source = dict(data or {})
    for legacy, current in LEGACY_CONFIG_KEYS.items():
        if current not in source and legacy in source:
            source[current] = source[legacy]
    return {key: source.get(key, default) for key, default in DEFAULT_LOCAL_CONFIG.items()}


def ensure_local_config() -> dict:
    if not LOCAL_CONFIG_PATH.exists():
        config = dict(DEFAULT_LOCAL_CONFIG)
        LOCAL_CONFIG_PATH.write_text(json.dumps(config, indent=2), encoding="utf-8")
        return config
    try:
        data = json.loads(LOCAL_CONFIG_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, TypeError):
        data = {}
    return normalize_local_config(data)


def save_local_config(data: dict) -> None:
    config = normalize_local_config(data)
    temporary = LOCAL_CONFIG_PATH.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(config, indent=2), encoding="utf-8")
    temporary.replace(LOCAL_CONFIG_PATH)
