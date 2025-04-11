import platform
import logging
from tools.base import Tool, ToolMetadata
from utils.logger import log_event

# Configure logging
logger = logging.getLogger('mcp.tools.specs')

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    logger.warning("psutil not installed - some functionality will be limited")

class SpecsTool(Tool):
    """
    Tool for retrieving system specifications and resource information
    """
    
    def __init__(self):
        super().__init__()
    
    def _initialize_metadata(self) -> ToolMetadata:
        """Initialize tool metadata"""
        return ToolMetadata(
            name="specs",
            description="Provides system information and resource usage",
            version="1.0.0",
            parameters={
                "info_type": {
                    "type": "string",
                    "description": "Type of information to retrieve (cpu, ram, disk, os, all)",
                    "required": True
                },
                "detailed": {
                    "type": "boolean",
                    "description": "Whether to include detailed information",
                    "required": False
                }
            },
            tags=["system", "diagnostics", "monitoring"]
        )
    
    def _execute(self, **kwargs) -> str:
        """Get system information based on requested type"""
        info_type = kwargs.get("info_type", "").lower()
        detailed = kwargs.get("detailed", False)
        
        logger.info(f"[SpecsTool] Getting info for: {info_type}, detailed={detailed}")
        
        try:
            if not PSUTIL_AVAILABLE and info_type in ["cpu", "ram", "disk", "all"]:
                return "[SpecsTool] Error: psutil module not installed. Please install with 'pip install psutil' for full functionality."
                
            if info_type == "cpu":
                result = self._get_cpu_info(detailed)
            elif info_type == "ram":
                result = self._get_ram_info(detailed)
            elif info_type == "disk":
                result = self._get_disk_info(detailed)
            elif info_type == "os":
                result = self._get_os_info(detailed)
            elif info_type == "all":
                result = self._get_all_info(detailed)
            else:
                result = "[SpecsTool] Invalid info_type. Try: cpu, ram, disk, os, all"
                logger.warning(f"[SpecsTool] Invalid info_type: {info_type}")
            
            log_event("SpecsTool", f"info_type={info_type}", result)
            return result
            
        except Exception as e:
            error_msg = f"[SpecsTool] Error getting {info_type} info: {str(e)}"
            logger.error(error_msg)
            log_event("SpecsTool", f"info_type={info_type}", f"Error: {str(e)}")
            return error_msg
    
    def _get_cpu_info(self, detailed: bool) -> str:
        """Get CPU information"""
        if not PSUTIL_AVAILABLE:
            return f"CPU: {platform.processor()}, Architecture: {platform.machine()}"
            
        if detailed:
            cpu_freq = psutil.cpu_freq()
            cpu_freq_str = f", Frequency: {cpu_freq.current:.2f} MHz" if cpu_freq else ""
            cpu_percent = psutil.cpu_percent(interval=0.1)
            
            result = (
                f"CPU: {platform.processor()}\n"
                f"Architecture: {platform.machine()}\n"
                f"Physical cores: {psutil.cpu_count(logical=False)}\n"
                f"Logical cores: {psutil.cpu_count()}{cpu_freq_str}\n"
                f"Current usage: {cpu_percent}%"
            )
        else:
            result = f"CPU: {platform.processor()}, Cores: {psutil.cpu_count(logical=False)}, Threads: {psutil.cpu_count()}"
        
        return result
    
    def _get_ram_info(self, detailed: bool) -> str:
        """Get RAM information"""
        if not PSUTIL_AVAILABLE:
            return "RAM: Unable to retrieve RAM information without psutil"
            
        mem = psutil.virtual_memory()
        
        if detailed:
            result = (
                f"Total RAM: {self._format_bytes(mem.total)}\n"
                f"Available: {self._format_bytes(mem.available)} ({mem.percent}% used)\n"
                f"Used: {self._format_bytes(mem.used)}\n"
                f"Free: {self._format_bytes(mem.free)}"
            )
        else:
            result = f"RAM: {round(mem.total / (1024**3), 2)} GB total, {round(mem.available / (1024**3), 2)} GB available"
        
        return result
    
    def _get_disk_info(self, detailed: bool) -> str:
        """Get disk usage information"""
        if not PSUTIL_AVAILABLE:
            return "Disk: Unable to retrieve disk information without psutil"
            
        if detailed:
            result = ["Disk Usage:"]
            for part in psutil.disk_partitions(all=False):
                if part.mountpoint:
                    usage = psutil.disk_usage(part.mountpoint)
                    result.append(
                        f"Partition: {part.mountpoint} ({part.device})\n"
                        f"  Filesystem: {part.fstype}\n"
                        f"  Total: {self._format_bytes(usage.total)}\n"
                        f"  Used: {self._format_bytes(usage.used)} ({usage.percent}%)\n"
                        f"  Free: {self._format_bytes(usage.free)}"
                    )
            return "\n".join(result)
        else:
            disk = psutil.disk_usage("/")
            return f"Disk: {round(disk.total / (1024**3), 2)} GB total, {round(disk.free / (1024**3), 2)} GB free"
    
    def _get_os_info(self, detailed: bool) -> str:
        """Get operating system information"""
        if detailed:
            result = (
                f"OS: {platform.system()} {platform.release()}\n"
                f"Version: {platform.version()}\n"
                f"Platform: {platform.platform()}\n"
                f"Python: {platform.python_version()}"
            )
        else:
            result = f"OS: {platform.system()} {platform.release()}"
        
        return result
    
    def _get_all_info(self, detailed: bool) -> str:
        """Get all system information"""
        sections = [
            self._get_os_info(detailed),
            self._get_cpu_info(detailed),
        ]
        
        if PSUTIL_AVAILABLE:
            sections.extend([
                self._get_ram_info(detailed),
                self._get_disk_info(detailed)
            ])
        else:
            sections.append("Note: Install psutil for RAM and disk information")
        
        return "\n\n".join(sections)
    
    def _format_bytes(self, bytes: int) -> str:
        """Format bytes as human-readable size"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes < 1024 or unit == 'TB':
                return f"{bytes:.2f} {unit}" if unit != 'B' else f"{bytes} {unit}"
            bytes /= 1024
