import logging
from agents.base import Agent, AgentMetadata

# Configure logging
logger = logging.getLogger('mcp.agents.help')

class HelpAgent(Agent):
    def __init__(self):
        super().__init__()
    
    def _initialize_metadata(self) -> AgentMetadata:
        """Initialize agent metadata"""
        return AgentMetadata(
            name="help",
            description="Provides help and documentation on MCP usage",
            version="1.0.0",
            capabilities=[
                "documentation",
                "help_topics",
                "command_reference"
            ]
        )
    
    def _execute(self, input_text: str) -> str:
        """Provide help on various topics"""
        topic = input_text.strip().lower()
        logger.info(f"[HelpAgent] Providing help for: {topic}")

        if not topic:
            return self.general_help()

        elif topic == "code":
            return self.code_help()

        elif topic == "diagnostics":
            return self.diagnostics_help()

        elif topic == "tools":
            return self.tools_help()
            
        elif topic == "session":
            return self.session_help()

        return f"[HelpAgent] Unknown topic '{topic}'. Try: code, diagnostics, tools, session"

    def general_help(self):
        return """
[MCP HelpAgent] Available commands:

run help code            → Show how to use the CodeAgent
run help diagnostics     → Show system check commands
run help tools           → Show how to use tools directly
run help session         → Show session management commands
list agents              → List all registered agents
list tools               → List all available tools
use tool <toolname> ...  → Run a tool directly
"""

    def code_help(self):
        return """
[HelpAgent] CodeAgent Help:

run code <task>          → Generates code based on your description

Project Management:
run code create a new project for <description>  → Creates a multi-file project
run code add a file called <filename> to <description> → Adds to current project
run code modify <filename> to <description> → Updates existing file

Examples:
  run code build a countdown timer
  run code create a python web scraper
  run code create a new project for a react todo app
  run code add a file called utils.js to add utility functions
  run code modify main.py to fix the bug in the calculation
"""

    def diagnostics_help(self):
        return """
[HelpAgent] DiagnosticsAgent Help:

System Information:
run diagnostics check cpu    → Show CPU information
run diagnostics check ram    → Show memory usage
run diagnostics check disk   → Show disk space
run diagnostics check os     → Show operating system details

Command Execution:
run diagnostics run <shell command>  → Execute a system command

Examples:
  run diagnostics check cpu
  run diagnostics run echo "Hello World"
  run diagnostics run dir
"""

    def tools_help(self):
        return """
[HelpAgent] Tool Help (via `use tool`):

File Operations:
use tool file action=write path=hello.txt content="hello world"
use tool file action=read path=hello.txt
use tool file action=append path=hello.txt content="more content"
use tool file action=delete path=hello.txt
use tool file action=list path=.
use tool file action=search path=. pattern=*.py
use tool file action=info path=hello.txt

Command Execution:
use tool command raw_input="echo Hello"

System Information:
use tool specs info_type=ram
use tool specs info_type=cpu
use tool specs info_type=disk
use tool specs info_type=os
"""

    def session_help(self):
        return """
[HelpAgent] Session Management:

session new              → Start a new session
session list             → List all active sessions
session switch <id>      → Switch to a different session
session info             → Show current session details

Sessions allow you to maintain separate contexts for different tasks.
Each session has its own memory and state.
"""
