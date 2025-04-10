from abc import ABC, abstractmethod

class Agent(ABC):
    @abstractmethod
    def run(self, input_text: str):
        pass
