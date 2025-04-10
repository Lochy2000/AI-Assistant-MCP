from agents.base import Agent

class CodeAgent(Agent):
    def run(self, input_text: str):
        print(f"[CodeAgent] Running with input: {input_text}")
