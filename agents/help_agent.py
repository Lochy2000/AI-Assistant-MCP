from agents.base import Agent

class HelpAgent(Agent):
    def run(self, input_text):
        topic = input_text.strip().lower()

        if not topic:
            return self.general_help()

        elif topic == "code":
            return self.code_help()

        elif topic == "diagnostics":
            return self.diagnostics_help()

        elif topic == "tools":
            return self.tools_help()

        return f"[HelpAgent] Unknown topic '{topic}'. Try: code, diagnostics, tools"

    def general_help(self):
        return """
[MCP HelpAgent] Available commands:

run help code            → Show how to use the CodeAgent
run help diagnostics     → Show system check commands
run help tools           → Show how to use tools directly
list agents              → List all registered agents
list tools               → List all available tools
use tool <name> ...      → Run a tool directly
"""

    def code_help(self):
        return """
[HelpAgent] CodeAgent Help:

run code <task>          → Generates placeholder code and saves to file
Examples:
  run code build a countdown timer
  run code create a react component
"""

    def diagnostics_help(self):
        return """
[HelpAgent] DiagnosticsAgent Help:

run diagnostics check cpu
run diagnostics check ram
run diagnostics check disk
run diagnostics run <shell command>
"""

    def tools_help(self):
        return """
[HelpAgent] Tool Help (via `use tool`):

use tool file action=write path=hello.txt content="hi"
use tool file action=read path=hello.txt

use tool command raw_input="echo Hello"
use tool specs info_type=ram
"""
