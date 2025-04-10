from tools.base import Tool

class N8nTool(Tool):
    def execute(self, **kwargs):
        print("[N8nTool] Sending task to n8n webhook")
