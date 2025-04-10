# === core/mcp_loader.py ===
import json

def load_mcp_config(path):
    with open(path, "r") as f:
        return json.load(f)


# === core/registry.py ===
class Registry:
    def __init__(self):
        self.agents = {}
        self.tools = {}

    def register_agent(self, name, agent):
        self.agents[name] = agent

    def register_tool(self, name, tool):
        self.tools[name] = tool

    def get_agent(self, name):
        return self.agents.get(name)

    def get_tool(self, name):
        return self.tools.get(name)