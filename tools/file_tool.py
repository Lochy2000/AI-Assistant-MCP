from tools.base import Tool
from utils.logger import log_event

class FileTool(Tool):
    def execute(self, action=None, path=None, content=None, **kwargs):
        if action == "write" and path and content:
            try:
                with open(path, "w") as f:
                    f.write(content)
                result = f"[FileTool] Wrote to {path}"
                log_event("FileTool", f"{action} {path}", result)  # ✅ Log here
                return result
            except Exception as e:
                result = f"[FileTool Error] {str(e)}"
                log_event("FileTool", f"{action} {path}", result)
                return result

        elif action == "read" and path:
            try:
                with open(path, "r") as f:
                    result = f.read()
                log_event("FileTool", f"{action} {path}", result)
                return result
            except Exception as e:
                result = f"[FileTool Error] {str(e)}"
                log_event("FileTool", f"{action} {path}", result)
                return result

        # Only hits this if the args are invalid
        result = "[FileTool] Invalid arguments. Try: action=write path=... content=..."
        log_event("FileTool", f"{action} {path}", result)
        return result
