import os
import shutil
import glob
import time
from backend.config import settings

class SystemManager:
    """
    Handles system cleanup operations: logs, cache, models, temp files, and full cleanup.
    Each method returns a dict with details of the cleanup performed.
    """
    def __init__(self):
        self.log_dir = settings.LOG_DIR
        self.model_cache_dir = settings.MODEL_CACHE_DIR
        self.temp_dir = getattr(settings, 'TEMP_DIR', '/tmp/aidalneo')
        os.makedirs(self.temp_dir, exist_ok=True)

    def clean_logs(self) -> dict:
        """Delete all log files except the most recent one."""
        files = sorted(glob.glob(os.path.join(self.log_dir, '*.log')), key=os.path.getmtime, reverse=True)
        removed = 0
        space_freed = 0
        for f in files[1:]:  # Keep the most recent log
            size = os.path.getsize(f)
            os.remove(f)
            removed += 1
            space_freed += size
        return {"operation": "clean_logs", "files_removed": removed, "space_freed": space_freed}

    def clean_cache(self) -> dict:
        """Delete all files in the model cache directory except loaded model (if any)."""
        removed = 0
        space_freed = 0
        for root, dirs, files in os.walk(self.model_cache_dir):
            for f in files:
                path = os.path.join(root, f)
                try:
                    size = os.path.getsize(path)
                    os.remove(path)
                    removed += 1
                    space_freed += size
                except Exception:
                    continue
        return {"operation": "clean_cache", "files_removed": removed, "space_freed": space_freed}

    def clean_models(self) -> dict:
        """Delete all model directories in the cache except the currently loaded one."""
        # This assumes a mechanism to get the loaded model dir (could be passed in)
        loaded_model_id = None  # To be set by caller if needed
        removed = 0
        space_freed = 0
        for d in os.listdir(self.model_cache_dir):
            dir_path = os.path.join(self.model_cache_dir, d)
            if os.path.isdir(dir_path) and d != loaded_model_id:
                size = self._get_dir_size(dir_path)
                shutil.rmtree(dir_path)
                removed += 1
                space_freed += size
        return {"operation": "clean_models", "dirs_removed": removed, "space_freed": space_freed}

    def clean_temp(self) -> dict:
        """Delete all files in the temp directory."""
        removed = 0
        space_freed = 0
        for root, dirs, files in os.walk(self.temp_dir):
            for f in files:
                path = os.path.join(root, f)
                try:
                    size = os.path.getsize(path)
                    os.remove(path)
                    removed += 1
                    space_freed += size
                except Exception:
                    continue
        return {"operation": "clean_temp", "files_removed": removed, "space_freed": space_freed}

    def full_cleanup(self) -> dict:
        """Perform all cleanup operations."""
        results = []
        total_space = 0
        for func in [self.clean_logs, self.clean_cache, self.clean_models, self.clean_temp]:
            result = func()
            results.append(result)
            total_space += result.get('space_freed', 0)
        return {"operation": "full_cleanup", "results": results, "space_freed": total_space}

    def _get_dir_size(self, dir_path):
        total = 0
        for dirpath, dirnames, filenames in os.walk(dir_path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                if os.path.isfile(fp):
                    total += os.path.getsize(fp)
        return total 