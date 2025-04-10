from abc import ABC, abstractmethod

#tools/base.py

class Tool(ABC):
    @abstractmethod
    def execute(self, **kwargs):
        pass
