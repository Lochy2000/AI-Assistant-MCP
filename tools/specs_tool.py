import platform
import psutil
from tools.base import Tool
from utils.logger import log_event

class SpecsTool(Tool):
    def execute(self, info_type=None, **kwargs):
        info_type = (info_type or "").lower()

        if info_type == "cpu":
            result = f"CPU: {platform.processor()}, Cores: {psutil.cpu_count(logical=False)}, Threads: {psutil.cpu_count()}"
            log_event("SpecsTool", f"info_type={info_type}", result)
            return result

        elif info_type == "ram":
            mem = psutil.virtual_memory()
            result = f"RAM: {round(mem.total / (1024**3), 2)} GB total, {round(mem.available / (1024**3), 2)} GB available"
            log_event("SpecsTool", f"info_type={info_type}", result)
            return result

        elif info_type == "disk":
            disk = psutil.disk_usage("/")
            result = f"Disk: {round(disk.total / (1024**3), 2)} GB total, {round(disk.free / (1024**3), 2)} GB free"
            log_event("SpecsTool", f"info_type={info_type}", result)
            return result

        elif info_type == "os":
            result = f"OS: {platform.system()} {platform.release()}"
            log_event("SpecsTool", f"info_type={info_type}", result)
            return result

        result = "[SpecsTool] Invalid info_type. Try: info_type=cpu, ram, disk, os"
        log_event("SpecsTool", f"info_type={info_type}", result)
        return result
