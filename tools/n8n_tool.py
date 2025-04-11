import logging
from tools.base import Tool, ToolMetadata
from utils.logger import log_event

# Configure logging
logger = logging.getLogger('mcp.tools.n8n')

class N8nTool(Tool):
    """
    Tool for interacting with n8n workflows via webhooks
    """
    
    def __init__(self, webhook_url: str = None):
        super().__init__()
        self.webhook_url = webhook_url or "http://localhost:5678/webhook/task"
    
    def _initialize_metadata(self) -> ToolMetadata:
        """Initialize tool metadata"""
        return ToolMetadata(
            name="n8n",
            description="Triggers n8n workflows via webhooks",
            version="1.0.0",
            parameters={
                "action": {
                    "type": "string",
                    "description": "Action to perform (trigger, status, etc.)",
                    "required": True
                },
                "workflow": {
                    "type": "string",
                    "description": "Workflow name or ID to target",
                    "required": False
                },
                "payload": {
                    "type": "object",
                    "description": "JSON payload to send to the webhook",
                    "required": False
                }
            },
            tags=["automation", "workflow", "n8n"]
        )
    
    def _execute(self, **kwargs) -> str:
        """Execute n8n operations"""
        action = kwargs.get("action", "trigger")
        workflow = kwargs.get("workflow", "default")
        payload = kwargs.get("payload", {})
        
        if action == "trigger":
            return self._trigger_workflow(workflow, payload)
        else:
            return f"[N8nTool] Unknown action: {action}. Try 'trigger'."
    
    def _trigger_workflow(self, workflow: str, payload: dict) -> str:
        """Simulate triggering an n8n workflow via webhook"""
        # Just simulate the webhook call since we're not actually using n8n
        logger.info(f"[N8nTool] Would trigger workflow '{workflow}' with payload: {payload}")
        log_event("N8nTool", f"trigger workflow '{workflow}'", "Simulated webhook call")
        
        return f"[N8nTool] Successfully triggered workflow '{workflow}' (simulated)"
