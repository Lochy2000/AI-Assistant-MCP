from agents.base import Agent
from tools.file_tool import FileTool
from utils.logger import log_event

class CodeAgent(Agent):
    def __init__(self):
        self.file_tool = FileTool()

    def run(self, input_text):
        # 🔧 Placeholder for actual LLM-generated code
        simulated_code = f"""// Auto-generated placeholder code for: {input_text}

function hello() {{
    console.log("Hello, world!");
}}
"""

        # We'll write to a generic file for now
        filename = "generated_code.js"

        result = self.file_tool.execute(
            action="write",
            path=filename,
            content=simulated_code
        )

        print(f"[CodeAgent] {result}")
        print(f"[CodeAgent] Saved code to {filename}")

        log_event("CodeAgent", input_text, f"Saved to {filename}")
