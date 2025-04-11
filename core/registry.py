"""
Enhanced Registry Module for MCP
Provides an improved component registry with metadata and discovery features
"""
from typing import Dict, List, Any, Optional, Type, Union
import logging
import uuid

# Configure logging
logger = logging.getLogger('mcp.registry')

class RegistryEntry:
    """Registry entry containing component and metadata"""
    
    def __init__(self, component_id: str, component: Any, category: str, metadata: Dict[str, Any] = None):
        self.id = component_id
        self.component = component
        self.category = category
        self.metadata = metadata or {}
        self.created_at = None  # Will be set by registry
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert entry to dictionary (excluding component instance)"""
        return {
            "id": self.id,
            "category": self.category,
            "metadata": self.metadata,
            "created_at": self.created_at
        }


class Registry:
    """
    Enhanced component registry with improved capabilities
    
    - Component categorization
    - Metadata storage and querying
    - Versioning support
    - Dynamic component discovery
    """
    
    def __init__(self):
        self.components: Dict[str, RegistryEntry] = {}
        self.categories: Dict[str, Dict[str, str]] = {}  # category -> {name -> id}
        # For backward compatibility
        self.agents: Dict[str, Any] = {}
        self.tools: Dict[str, Any] = {}
    
    def register(self, category: str, name: str, component: Any, 
                 metadata: Dict[str, Any] = None, component_id: str = None) -> str:
        """
        Register a component in the registry
        
        Args:
            category: Component category (e.g., 'agent', 'tool')
            name: Component name (used for lookups)
            component: The component instance
            metadata: Optional metadata about the component
            component_id: Optional custom ID (generated if not provided)
            
        Returns:
            The component ID
        """
        # Generate component ID if not provided
        component_id = component_id or str(uuid.uuid4())
        
        # Create and store entry
        entry = RegistryEntry(component_id, component, category, metadata)
        self.components[component_id] = entry
        
        # Initialize category if not exists
        if category not in self.categories:
            self.categories[category] = {}
        
        # Add to category index with name
        self.categories[category][name] = component_id
        
        # For backward compatibility
        if category == 'agent':
            self.agents[name] = component
        elif category == 'tool':
            self.tools[name] = component
        
        logger.info(f"Registered {category} '{name}' with ID {component_id}")
        return component_id
    
    def unregister(self, component_id: str) -> bool:
        """
        Unregister a component from the registry
        
        Args:
            component_id: ID of component to unregister
            
        Returns:
            True if component was unregistered, False if not found
        """
        if component_id not in self.components:
            return False
        
        # Get the entry
        entry = self.components[component_id]
        
        # Remove from category index
        if entry.category in self.categories:
            for name, cid in list(self.categories[entry.category].items()):
                if cid == component_id:
                    # For backward compatibility
                    if entry.category == 'agent' and name in self.agents:
                        del self.agents[name]
                    elif entry.category == 'tool' and name in self.tools:
                        del self.tools[name]
                    
                    del self.categories[entry.category][name]
                    break
        
        # Remove from components
        del self.components[component_id]
        
        logger.info(f"Unregistered component with ID {component_id}")
        return True
    
    def get(self, component_id: str) -> Optional[Any]:
        """
        Get a component by ID
        
        Args:
            component_id: ID of component to retrieve
            
        Returns:
            Component instance or None if not found
        """
        entry = self.components.get(component_id)
        return entry.component if entry else None
    
    def get_by_name(self, category: str, name: str) -> Optional[Any]:
        """
        Get a component by category and name
        
        Args:
            category: Component category
            name: Component name
            
        Returns:
            Component instance or None if not found
        """
        if category not in self.categories or name not in self.categories[category]:
            return None
        
        component_id = self.categories[category][name]
        return self.get(component_id)
    
    def get_metadata(self, component_id: str) -> Optional[Dict[str, Any]]:
        """
        Get component metadata by ID
        
        Args:
            component_id: ID of component
            
        Returns:
            Component metadata or None if not found
        """
        entry = self.components.get(component_id)
        return entry.metadata if entry else None
    
    def get_all(self, category: str = None) -> Dict[str, Any]:
        """
        Get all components, optionally filtered by category
        
        Args:
            category: Optional category filter
            
        Returns:
            Dictionary of {id: component}
        """
        result = {}
        
        if category:
            # Get only components of the specified category
            if category in self.categories:
                for name, component_id in self.categories[category].items():
                    entry = self.components.get(component_id)
                    if entry:
                        result[component_id] = entry.component
        else:
            # Get all components
            for component_id, entry in self.components.items():
                result[component_id] = entry.component
        
        return result
    
    def get_names(self, category: str) -> List[str]:
        """
        Get all registered names for a category
        
        Args:
            category: Component category
            
        Returns:
            List of component names
        """
        if category not in self.categories:
            return []
        
        return list(self.categories[category].keys())
    
    def search(self, query: str, category: str = None) -> List[Dict[str, Any]]:
        """
        Search for components by metadata or name
        
        Args:
            query: Search query string
            category: Optional category to restrict search
            
        Returns:
            List of matching component entries (as dictionaries)
        """
        results = []
        query = query.lower()
        
        for component_id, entry in self.components.items():
            # Apply category filter if specified
            if category and entry.category != category:
                continue
            
            # Check name match in category index
            name_match = False
            if entry.category in self.categories:
                for name, cid in self.categories[entry.category].items():
                    if cid == component_id and query in name.lower():
                        name_match = True
                        break
            
            # Check metadata match
            metadata_match = any(
                isinstance(v, str) and query in v.lower()
                for v in entry.metadata.values()
                if isinstance(v, str)
            )
            
            if name_match or metadata_match:
                results.append(entry.to_dict())
        
        return results
    
    # Convenience methods for agent registration
    def register_agent(self, name: str, agent: Any, metadata: Dict[str, Any] = None) -> str:
        """Register an agent component"""
        # If agent has its own metadata, use it
        if hasattr(agent, 'metadata') and hasattr(agent.metadata, 'to_dict'):
            metadata = agent.metadata.to_dict()
        
        return self.register('agent', name, agent, metadata)
    
    # Convenience methods for tool registration
    def register_tool(self, name: str, tool: Any, metadata: Dict[str, Any] = None) -> str:
        """Register a tool component"""
        # If tool has its own metadata, use it
        if hasattr(tool, 'metadata') and hasattr(tool.metadata, 'to_dict'):
            metadata = tool.metadata.to_dict()
            
        return self.register('tool', name, tool, metadata)
    
    # Convenience methods for retrieving agents and tools
    def get_agent(self, name: str) -> Optional[Any]:
        """Get an agent by name"""
        return self.get_by_name('agent', name)
    
    def get_tool(self, name: str) -> Optional[Any]:
        """Get a tool by name"""
        return self.get_by_name('tool', name)
    
    def get_all_agents(self) -> Dict[str, Any]:
        """Get all registered agents"""
        return self.get_all('agent')
    
    def get_all_tools(self) -> Dict[str, Any]:
        """Get all registered tools"""
        return self.get_all('tool')
