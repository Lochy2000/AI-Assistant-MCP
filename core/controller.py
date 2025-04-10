# === core/controller.py ===
from core.registry import Registry
from agents.code_agent import CodeAgent
from agents.diagnostics_agent import DiagnosticsAgent
from tools.file_tool import FileTool
from tools.command_tool import CommandTool
from tools.specs_tool import SpecsTool
from tools.n8n_tool import N8nTool
from utils.helpers import parse_kwargs
from agents.help_agent import HelpAgent


class Controller:
    def __init__(self, config):
        self.registry = Registry()
        self.config = config
        self._load_modules()

    def _load_modules(self):
        # Register agents
        self.registry.register_agent("code", CodeAgent())
        self.registry.register_agent("diagnostics", DiagnosticsAgent())
        self.registry.register_agent("help", HelpAgent())

        # Register tools
        self.registry.register_tool("file", FileTool())
        self.registry.register_tool("command", CommandTool())
        self.registry.register_tool("specs", SpecsTool())
        self.registry.register_tool("n8n", N8nTool())

    def run(self):
        print("MCP is ready. Type a command like `run code` or `run diagnostics`:")
        while True:
            user_input = input("» ").strip()
            if not user_input:
                print("[MCP] Please enter a command. Type `help` or `?`.")
                continue

            if user_input.lower() in ["exit", "quit"]:
                break

            parts = user_input.split()
            command = parts[0].lower()

            if command == "help" or command == "?":
                self._print_help()

            elif command == "list":
                if len(parts) < 2:
                    print("[MCP] Usage: list agents | list tools")
                    continue
                target = parts[1].lower()
                if target == "agents":
                    print("Available agents:", ", ".join(self.registry.agents.keys()))
                elif target == "tools":
                    print("Available tools:", ", ".join(self.registry.tools.keys()))
                else:
                    print("[MCP] Unknown list option. Try: list agents | list tools")

            elif command == "run":
                if len(parts) < 2:
                    print("[MCP] Usage: run <agent> <args>")
                    continue
                agent_name = parts[1].lower()
                args = " ".join(parts[2:])
                agent = self.registry.get_agent(agent_name)
                if agent:
                    result = agent.run(args)
                    if result:
                        print(result)
                else:
                    print(f"[MCP] Unknown agent: {agent_name}")

            elif command == "use":
                if len(parts) < 3 or parts[1] != "tool":
                    print("[MCP] Usage: use tool <toolname> <args>")
                    continue
                tool_name = parts[2].lower()
                args = " ".join(parts[3:])
                tool = self.registry.get_tool(tool_name)

                if tool:
                    kwargs = parse_kwargs(args)

                    # Fallback to raw_input if no key=value found
                    if not kwargs and args:
                        kwargs = {"raw_input": args}

                    try:
                        result = tool.execute(**kwargs)
                        print(f"[Tool Output] {result}")
                    except Exception as e:
                        print(f"[MCP] Tool execution failed: {str(e)}")
                else:
                    print(f"[MCP] Unknown tool: {tool_name}")

            else:
                print("[MCP] Command not recognized. Type `help` or `?`.")

    def _print_help(self):
        print("""
    🧠 MCP Help Menu

    run <agent> <input>         → Run an agent (e.g. run code build a React app)
    use tool <tool> <input>     → Use a tool directly (e.g. use tool command echo hi)
    list agents                 → Show all available agents
    list tools                  → Show all available tools
    help / ?                    → Show this help menu
    exit / quit                 → Exit the assistant
""")
