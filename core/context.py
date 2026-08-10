import os
import json
from config import config
from core.db import ScanDB


class ScanContext:
    """扫描上下文，管理单次扫描的状态和路径"""

    def __init__(self, domain: str, db: ScanDB):
        self.domain = domain
        self.db = db
        self.scan_record = db.get_scan(domain)

        if not self.scan_record:
            scan_id = db.create_scan(domain)
            self.scan_record = db.get_scan(domain)
        else:
            scan_id = self.scan_record["id"]

        self.scan_id = scan_id
        self.cache_dir = os.path.join(config.CACHE_DIR, domain)
        os.makedirs(self.cache_dir, exist_ok=True)

        # 状态文件
        self.state_file = os.path.join(self.cache_dir, "state.json")
        self._state = self._load_state()

    def _load_state(self) -> dict:
        if os.path.exists(self.state_file):
            with open(self.state_file) as f:
                return json.load(f)
        return {"steps_done": [], "last_step": None}

    def _save_state(self):
        with open(self.state_file, "w") as f:
            json.dump(self._state, f, indent=2)

    @property
    def steps_done(self) -> list[str]:
        return self._state.get("steps_done", [])

    def mark_step_done(self, step: str):
        if step not in self._state["steps_done"]:
            self._state["steps_done"].append(step)
        self._state["last_step"] = step
        self._save_state()
        self.db.update_scan_status(self.scan_id, f"done:{step}")

    def is_step_done(self, step: str) -> bool:
        return step in self._state["steps_done"]

    # 缓存文件路径
    @property
    def amass_json(self) -> str:
        return os.path.join(self.cache_dir, "amass.json")

    @property
    def ips_file(self) -> str:
        return os.path.join(self.cache_dir, "ips")

    @property
    def hosts_file(self) -> str:
        return os.path.join(self.cache_dir, "hosts")

    @property
    def masscan_json(self) -> str:
        return os.path.join(self.cache_dir, "masscan.json")

    @property
    def nmap_fast_json(self) -> str:
        return os.path.join(self.cache_dir, "nmap_fast.json")

    @property
    def nmap_service_json(self) -> str:
        return os.path.join(self.cache_dir, "nmap_service.json")
