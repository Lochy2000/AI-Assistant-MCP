# core/registry.py
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
