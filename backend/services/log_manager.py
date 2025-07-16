import os, logging, glob, time
from typing import List, Optional
from backend.config import settings

class LogManager:
    """
    Handles logging, log storage, cleanup, purging, and log rotation.
    Tracks space freed and supports log level filtering.
    """
    def __init__(self):
        self.log_dir = settings.LOG_DIR
        os.makedirs(self.log_dir, exist_ok=True)
        self.log_file = os.path.join(self.log_dir, "aidalneo.log")
        self.logger = logging.getLogger("Aid-al-Neo")
        self.logger.setLevel(logging.INFO)
        if not self.logger.handlers:
            handler = logging.FileHandler(self.log_file)
            formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def log_request(self, data: dict):
        self.logger.info(f"REQUEST: {data}")

    def log_response(self, data: dict):
        self.logger.info(f"RESPONSE: {data}")

    def cleanup_logs(self, older_than_days: int = 30, keep_latest_files: int = 100, log_levels: Optional[List[str]] = None) -> dict:
        files = sorted(glob.glob(os.path.join(self.log_dir, "*.log")), key=os.path.getmtime, reverse=True)
        now = time.time()
        removed = 0
        space_freed = 0
        # Remove old files
        for f in files[keep_latest_files:]:
            age_days = (now - os.path.getmtime(f)) / 86400
            if age_days > older_than_days:
                size = os.path.getsize(f)
                os.remove(f)
                removed += 1
                space_freed += size
        return {"files_removed": removed, "space_freed": space_freed} 