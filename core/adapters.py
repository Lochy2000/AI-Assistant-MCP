"""
Adapter Module
Provides adapters to make existing components compatible with the enhanced architecture
"""
from typing import Dict, List, Any, Optional
import logging

from agents.base import EnhancedAgent, AgentMetadata
from tools.base import EnhancedTool, ToolMetadata

# Configure logging
logger = logging.getLogger('mcp.adapters')

class LegacyAgentAdapter(EnhancedAgent):
    """
    Adapter for legacy agents to work with the enhanced architecture
    
    This adapter wraps a legacy agent instance and makes it compatible
    with the enhanced agent interface.
    """
    
    def __init__(self, legacy_agent, name: str, description: str = "", capabilities: List[str] = None):
        super().__init__()
        self.legacy_agent = legacy_agent
        self.name = name
        self.description = description
        self.agent_capabilities = capabilities or []
    
    def _initialize_metadata(self) -> AgentMetadata:
        """Initialize agent metadata based on provided values"""
        return AgentMetadata(
            name=self.name,
            description=self.description,
            version="1.0.0",  # Assume version for legacy agents
            capabilities=self.agent_capabilities
        )
    
    def _execute(self, input_text: str) -> str:
        """Call the legacy agent's run method"""
        logger.info(f"[{self.name}Adapter] Executing legacy agent")
        
        # Call the legacy agent's run method
        result = self.legacy_agent.run(input_text)
        
        # Store in agent memory
        self.memory.add_to_history("legacy_run", {
            "input": input_text,
            "result": result
        })
        
        return result


class LegacyToolAdapter(EnhancedTool):
    """
    Adapter for legacy tools to work with the enhanced architecture
    
    This adapter wraps a legacy tool instance and makes it compatible
    with the enhanced tool interface.
    """
    
    def __init__(self, legacy_tool, name: str, description: str = "", parameters: Dict[str, Dict[str, Any]] = None):
        super().__init__()
        self.legacy_tool = legacy_tool
        self.name = name
        self.description = description
        self.tool_parameters = parameters or {}
    
    def _initialize_metadata(self) -> ToolMetadata:
        """Initialize tool metadata based on provided values"""
        return ToolMetadata(
            name=self.name,
            description=self.description,
            version="1.0.0",  # Assume version for legacy tools
            parameters=self.tool_parameters
        )
    
    def _execute(self, **kwargs) -> Any:
        """Call the legacy tool's execute method"""
        logger.info(f"[{self.name}Adapter] Executing legacy tool")
        
        # Call the legacy tool's execute method
        return self.legacy_tool.execute(**kwargs)


def adapt_legacy_agent(agent, name: str, description: str = "", capabilities: List[str] = None) -> EnhancedAgent:
    """Create an adapted version of a legacy agent"""
    return LegacyAgentAdapter(agent, name, description, capabilities)


def adapt_legacy_tool(tool, name: str, description: str = "", parameters: Dict[str, Dict[str, Any]] = None) -> EnhancedTool:
    """Create an adapted version of a legacy tool"""
    return LegacyToolAdapter(tool, name, description, parameters)
