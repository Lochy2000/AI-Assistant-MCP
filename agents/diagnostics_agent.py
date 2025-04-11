import logging
from agents.base import Agent, AgentMetadata
from tools.specs_tool import SpecsTool
from tools.command_tool import CommandTool
from utils.logger import log_event

# Configure logging
logger = logging.getLogger('mcp.agents.diagnostics')

class DiagnosticsAgent(Agent):
    def __init__(self):
        super().__init__()
        self.specs_tool = SpecsTool()
        self.command_tool = CommandTool()
    
    def _initialize_metadata(self) -> AgentMetadata:
        """Initialize agent metadata"""
        return AgentMetadata(
            name="diagnostics",
            description="Provides system information and diagnostic capabilities",
            version="1.0.0",
            required_tools=["specs", "command"],
            capabilities=[
                "system_info",
                "resource_monitoring",
                "command_execution"
            ]
        )
    
    def _execute(self, input_text: str) -> str:
        """Execute diagnostic commands"""
        input_text = input_text.lower().strip()
        logger.info(f"[DiagnosticsAgent] Processing: {input_text}")

        if "check disk" in input_text:
            result = self.specs_tool.execute(info_type="disk")

        elif "check cpu" in input_text:
            result = self.specs_tool.execute(info_type="cpu")

        elif "check ram" in input_text:
            result = self.specs_tool.execute(info_type="ram")
            
        elif "check os" in input_text:
            result = self.specs_tool.execute(info_type="os")

        elif input_text.startswith("run "):
            command = input_text.replace("run ", "", 1)
            result = self.command_tool.execute(raw_input=command)

        else:
            result = "[DiagnosticsAgent] Unrecognized command. Try: check disk, check cpu, check ram, run echo test"

        logger.info(f"[DiagnosticsAgent] Result: {result}")
        log_event("DiagnosticsAgent", input_text, result)
        return result
