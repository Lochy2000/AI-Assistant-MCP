from abc import ABC, abstractmethod

class Tool(ABC):
    @abstractmethod
    def execute(self, **kwargs):
        pass
