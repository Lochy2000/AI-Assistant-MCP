from agents.base import Agent

class DiagnosticsAgent(Agent):
    def run(self, input_text: str):
        print(f"[DiagnosticsAgent] Running with input: {input_text}")
