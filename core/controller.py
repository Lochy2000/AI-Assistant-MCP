# === core/controller.py ===
from core.registry import Registry
from agents.code_agent import CodeAgent
from agents.diagnostics_agent import DiagnosticsAgent
from tools.file_tool import FileTool
from tools.command_tool import CommandTool
from tools.specs_tool import SpecsTool
from tools.n8n_tool import N8nTool

class Controller:
    def __init__(self, config):
        self.registry = Registry()
        self.config = config
        self._load_modules()

    def _load_modules(self):
        # Register agents
        self.registry.register_agent("code", CodeAgent())
        self.registry.register_agent("diagnostics", DiagnosticsAgent())

        # Register tools
        self.registry.register_tool("file", FileTool())
        self.registry.register_tool("command", CommandTool())
        self.registry.register_tool("specs", SpecsTool())
        self.registry.register_tool("n8n", N8nTool())

    def run(self):
        print("MCP is ready. Type a command like `run code` or `run diagnostics`:")
        while True:
            user_input = input("» ").strip()
            if user_input.lower() in ["exit", "quit"]:
                break

            if user_input.startswith("run"):
                _, agent_name, *args = user_input.split()
                agent = self.registry.get_agent(agent_name)
                if agent:
                    agent.run(" ".join(args))
                else:
                    print(f"[MCP] Unknown agent: {agent_name}")
            else:
                print("[MCP] Command not recognized. Use `run <agent>`.")

