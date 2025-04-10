from agents.base import Agent
from tools.specs_tool import SpecsTool
from tools.command_tool import CommandTool
from utils.logger import log_event

class DiagnosticsAgent(Agent):
    def __init__(self):
        self.specs_tool = SpecsTool()
        self.command_tool = CommandTool()

    def run(self, input_text):
        input_text = input_text.lower().strip()

        if "check disk" in input_text:
            result = self.specs_tool.execute(info_type="disk")

        elif "check cpu" in input_text:
            result = self.specs_tool.execute(info_type="cpu")

        elif "check ram" in input_text:
            result = self.specs_tool.execute(info_type="ram")

        elif input_text.startswith("run "):
            command = input_text.replace("run ", "", 1)
            result = self.command_tool.execute(raw_input=command)

        else:
            result = "[DiagnosticsAgent] Unrecognized command. Try: check disk, check cpu, run echo test"

        print(f"[DiagnosticsAgent] {result}")
        log_event("DiagnosticsAgent", input_text, result)
