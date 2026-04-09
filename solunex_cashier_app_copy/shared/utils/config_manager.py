# -*- coding: utf-8 -*-
# shared/utils/config_manager.py

import json
import os
from pathlib import Path

class ConfigManager:
    """Manages local Cashier App settings (e.g. Server IP)"""
    
    CONFIG_FILE = Path(os.path.expanduser("~")) / ".iande_cashier_config.json"

    @classmethod
    def load_config(cls) -> dict:
        if not cls.CONFIG_FILE.exists():
            return {}
        try:
            with open(cls.CONFIG_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return {}

    @classmethod
    def save_config(cls, config: dict):
        try:
            current = cls.load_config()
            current.update(config)
            with open(cls.CONFIG_FILE, "w") as f:
                json.dump(current, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")

    @classmethod
    def get_server_ip(cls) -> str:
        return cls.load_config().get("server_ip", "http://localhost:8000")
