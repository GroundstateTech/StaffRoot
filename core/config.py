import json
import os
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
APP_VERSION = "0.10.0"
APP_ICON = ASSETS_DIR / "staffroot.ico"

LOCAL_CONFIG_PATH = BASE_DIR / "staffroot.local.json"

DEFAULT_LOCAL_CONFIG = {
    "admin_center_base_url": "http://127.0.0.1:8000",
    "admin_center_api_key": "",
    "sync_enabled": False,
}

def ensure_local_config() -> dict:
    if not LOCAL_CONFIG_PATH.exists():
        LOCAL_CONFIG_PATH.write_text(json.dumps(DEFAULT_LOCAL_CONFIG, indent=2), encoding="utf-8")
        return dict(DEFAULT_LOCAL_CONFIG)
    try:
        data = json.loads(LOCAL_CONFIG_PATH.read_text(encoding="utf-8"))
    except Exception:
        data = dict(DEFAULT_LOCAL_CONFIG)
    merged = dict(DEFAULT_LOCAL_CONFIG)
    merged.update(data)
    return merged

def save_local_config(data: dict) -> None:
    merged = dict(DEFAULT_LOCAL_CONFIG)
    merged.update(data or {})
    LOCAL_CONFIG_PATH.write_text(json.dumps(merged, indent=2), encoding="utf-8")
