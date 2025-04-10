import subprocess
import platform
import shlex
from tools.base import Tool
from utils.logger import log_event

class CommandTool(Tool):
    def execute(self, raw_input=None, **kwargs):
        if not raw_input:
            result = "[CommandTool] No 'raw_input' provided."
            log_event("CommandTool", "None", result)
            return result

        banned = {"rm", "del", "shutdown", "format", "mkfs"}

        try:
            tokens = shlex.split(raw_input)
        except ValueError:
            tokens = raw_input.lower().split()

        if any(token.lower() in banned for token in tokens):
            result = "[CommandTool] Command blocked for safety."
            log_event("CommandTool", raw_input, result)
            return result

        try:
            is_windows = platform.system().lower() == "windows"
            result_obj = subprocess.run(
                raw_input,
                shell=is_windows,
                capture_output=True,
                text=True
            )

            if result_obj.returncode != 0:
                result = f"[CommandTool] Error:\n{result_obj.stderr.strip()}"
            else:
                result = result_obj.stdout.strip()

        except Exception as e:
            result = f"[CommandTool Error] {str(e)}"

        log_event("CommandTool", raw_input, result)
        return result
