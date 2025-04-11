"""
Enhanced Agent Base Module
Provides an improved base class for all MCP agents with additional capabilities
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Set
import asyncio
import json
import uuid
import logging
from datetime import datetime

# Configure logging
logger = logging.getLogger('mcp.agents')

class AgentMetadata:
    """Metadata for agent capabilities and requirements"""
    
    def __init__(self, 
                 name: str,
                 description: str,
                 version: str = "1.0.0",
                 required_tools: List[str] = None,
                 capabilities: List[str] = None):
        self.name = name
        self.description = description
        self.version = version
        self.required_tools = required_tools or []
        self.capabilities = capabilities or []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary"""
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "required_tools": self.required_tools,
            "capabilities": self.capabilities
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentMetadata':
        """Create metadata from dictionary"""
        return cls(
            name=data.get("name", "unknown"),
            description=data.get("description", ""),
            version=data.get("version", "1.0.0"),
            required_tools=data.get("required_tools", []),
            capabilities=data.get("capabilities", [])
        )


class AgentMemory:
    """Memory store for agent state between runs"""
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.data: Dict[str, Any] = {}
        self.context: Dict[str, Any] = {}
        self.history: List[Dict[str, Any]] = []
    
    def store(self, key: str, value: Any) -> None:
        """Store a value in memory"""
        self.data[key] = value
    
    def retrieve(self, key: str, default: Any = None) -> Any:
        """Retrieve a value from memory"""
        return self.data.get(key, default)
    
    def has_key(self, key: str) -> bool:
        """Check if key exists in memory"""
        return key in self.data
    
    def add_to_history(self, entry_type: str, data: Dict[str, Any]) -> None:
        """Add an entry to history"""
        entry = {
            "type": entry_type,
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        self.history.append(entry)
        
        # Keep history at a reasonable size
        if len(self.history) > 100:
            self.history.pop(0)
    
    def get_history(self, entry_type: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Get history entries, optionally filtered by type"""
        if entry_type:
            filtered = [e for e in self.history if e["type"] == entry_type]
            return filtered[-limit:]
        else:
            return self.history[-limit:]


class Agent(ABC):
    """
    Enhanced base agent with improved capabilities
    
    - Metadata for discovery and requirements
    - Memory for persistent state
    - Asynchronous operation support
    - Structured error handling
    - Tool dependency management
    """
    
    def __init__(self):
        self.id = str(uuid.uuid4())
        self.metadata = self._initialize_metadata()
        self.memory = AgentMemory(self.id)
        self.tools = {}
        self._dependencies_checked = False
    
    @abstractmethod
    def _initialize_metadata(self) -> AgentMetadata:
        """Initialize agent metadata"""
        pass
    
    def register_tool(self, name: str, tool_instance: Any) -> None:
        """Register a tool for the agent to use"""
        self.tools[name] = tool_instance
    
    def check_dependencies(self) -> bool:
        """Check if all required tools are available"""
        missing_tools = []
        
        for tool_name in self.metadata.required_tools:
            if tool_name not in self.tools:
                missing_tools.append(tool_name)
        
        if missing_tools:
            logger.warning(f"Agent {self.metadata.name} is missing required tools: {', '.join(missing_tools)}")
            return False
        
        self._dependencies_checked = True
        return True
    
    def run(self, input_text: str) -> str:
        """
        Run the agent synchronously
        
        This is a wrapper around the abstract _execute method that adds
        dependency checking and error handling.
        """
        # Check dependencies first
        if not self._dependencies_checked and not self.check_dependencies():
            return f"Error: Agent {self.metadata.name} is missing required dependencies"
        
        try:
            # Add to history
            self.memory.add_to_history("run", {"input": input_text})
            
            # Execute agent logic
            result = self._execute(input_text)
            
            # Update history with result
            self.memory.add_to_history("result", {"output": result})
            
            return result
        except Exception as e:
            error_msg = f"Error in agent {self.metadata.name}: {str(e)}"
            logger.error(error_msg)
            
            # Add error to history
            self.memory.add_to_history("error", {"error": str(e), "input": input_text})
            
            return error_msg
    
    async def run_async(self, input_text: str) -> str:
        """
        Run the agent asynchronously
        
        This is a wrapper around the _execute_async method that adds
        dependency checking and error handling.
        """
        # Check dependencies first
        if not self._dependencies_checked and not self.check_dependencies():
            return f"Error: Agent {self.metadata.name} is missing required dependencies"
        
        try:
            # Add to history
            self.memory.add_to_history("run", {"input": input_text})
            
            # Check if agent implements async execution
            if hasattr(self, '_execute_async') and callable(getattr(self, '_execute_async')):
                result = await self._execute_async(input_text)
            else:
                # Fall back to synchronous execution in a thread
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(None, self._execute, input_text)
            
            # Update history with result
            self.memory.add_to_history("result", {"output": result})
            
            return result
        except Exception as e:
            error_msg = f"Error in agent {self.metadata.name}: {str(e)}"
            logger.error(error_msg)
            
            # Add error to history
            self.memory.add_to_history("error", {"error": str(e), "input": input_text})
            
            return error_msg
    
    @abstractmethod
    def _execute(self, input_text: str) -> str:
        """
        Execute agent logic
        
        This is the main method that agents should implement to process input
        and return results.
        """
        pass
    
    def get_capabilities(self) -> List[str]:
        """Get list of agent capabilities"""
        return self.metadata.capabilities
    
    def has_capability(self, capability: str) -> bool:
        """Check if agent has a specific capability"""
        return capability in self.metadata.capabilities

# For backward compatibility
EnhancedAgent = Agent
