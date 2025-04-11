import subprocess
import platform
import shlex
import logging
from tools.base import Tool, ToolMetadata
from utils.logger import log_event

# Configure logging
logger = logging.getLogger('mcp.tools.command')

class CommandTool(Tool):
    """
    Tool for executing system commands
    """
    
    def __init__(self):
        super().__init__()
    
    def _initialize_metadata(self) -> ToolMetadata:
        """Initialize tool metadata"""
        return ToolMetadata(
            name="command",
            description="Executes system commands with safety restrictions",
            version="1.0.0",
            parameters={
                "raw_input": {
                    "type": "string",
                    "description": "Command to execute",
                    "required": True
                }
            },
            required_permissions=["command_execution"],
            tags=["system", "command", "shell"]
        )
    
    def _execute(self, **kwargs) -> str:
        """Execute a system command"""
        raw_input = kwargs.get("raw_input")
        
        if not raw_input:
            result = "[CommandTool] No 'raw_input' provided."
            logger.warning(result)
            log_event("CommandTool", "None", result)
            return result

        # Security check - block dangerous commands
        banned = {"rm", "del", "rmdir", "deltree", "rd", "format", 
                 "mkfs", "shutdown", "reboot", "halt", "poweroff"}

        try:
            tokens = shlex.split(raw_input)
        except ValueError:
            tokens = raw_input.lower().split()

        if any(banned_cmd in token.lower() for token in tokens for banned_cmd in banned):
            result = "[CommandTool] Command blocked for safety."
            logger.warning(f"[CommandTool] Blocked command: {raw_input}")
            log_event("CommandTool", raw_input, result)
            return result

        try:
            is_windows = platform.system().lower() == "windows"
            result_obj = subprocess.run(
                raw_input,
                shell=is_windows,
                capture_output=True,
                text=True,
                timeout=10  # Add timeout for safety
            )

            if result_obj.returncode != 0:
                result = f"[CommandTool] Error:\n{result_obj.stderr.strip()}"
                logger.error(f"[CommandTool] Command failed: {raw_input}")
            else:
                result = result_obj.stdout.strip()
                logger.info(f"[CommandTool] Successfully executed: {raw_input}")

        except subprocess.TimeoutExpired:
            result = "[CommandTool] Command timed out after 10 seconds."
            logger.warning(f"[CommandTool] Command timeout: {raw_input}")
        except Exception as e:
            result = f"[CommandTool] Error: {str(e)}"
            logger.error(f"[CommandTool] Exception: {str(e)}")

        log_event("CommandTool", raw_input, result)
        return result
