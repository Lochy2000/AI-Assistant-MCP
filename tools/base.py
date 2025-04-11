"""
Enhanced Tool Base Module
Provides an improved base class for all MCP tools with additional capabilities
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Callable
import asyncio
import uuid
import logging
from datetime import datetime

# Configure logging
logger = logging.getLogger('mcp.tools')

class ToolMetadata:
    """Metadata for tool capabilities and requirements"""
    
    def __init__(self, 
                 name: str,
                 description: str,
                 version: str = "1.0.0",
                 parameters: Dict[str, Dict[str, Any]] = None,
                 required_permissions: List[str] = None,
                 supports_progress: bool = False,
                 tags: List[str] = None):
        self.name = name
        self.description = description
        self.version = version
        self.parameters = parameters or {}
        self.required_permissions = required_permissions or []
        self.supports_progress = supports_progress
        self.tags = tags or []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary"""
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "parameters": self.parameters,
            "required_permissions": self.required_permissions,
            "supports_progress": self.supports_progress,
            "tags": self.tags
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ToolMetadata':
        """Create metadata from dictionary"""
        return cls(
            name=data.get("name", "unknown"),
            description=data.get("description", ""),
            version=data.get("version", "1.0.0"),
            parameters=data.get("parameters", {}),
            required_permissions=data.get("required_permissions", []),
            supports_progress=data.get("supports_progress", False),
            tags=data.get("tags", [])
        )


class ProgressTracker:
    """Track progress of long-running operations"""
    
    def __init__(self, total_steps: int = 100):
        self.total_steps = total_steps
        self.current_step = 0
        self.status_message = ""
        self.callbacks: List[Callable[[int, str], None]] = []
    
    def update(self, step: int, message: str = "") -> None:
        """Update progress"""
        self.current_step = min(step, self.total_steps)
        self.status_message = message
        
        # Notify callbacks
        for callback in self.callbacks:
            callback(self.current_step, message)
    
    def increment(self, steps: int = 1, message: str = "") -> None:
        """Increment progress by steps"""
        self.update(self.current_step + steps, message)
    
    def add_callback(self, callback: Callable[[int, str], None]) -> None:
        """Add a callback to be notified of progress updates"""
        self.callbacks.append(callback)
    
    @property
    def percentage(self) -> float:
        """Get progress as percentage"""
        return (self.current_step / self.total_steps) * 100


class Tool(ABC):
    """
    Enhanced base tool with improved capabilities
    
    - Metadata for discovery and requirements
    - Asynchronous operation support
    - Structured error handling
    - Progress tracking for long operations
    - Permission requirements
    """
    
    def __init__(self):
        self.id = str(uuid.uuid4())
        self.metadata = self._initialize_metadata()
        self.permissions_checked = False
        self.execution_history: List[Dict[str, Any]] = []
        self.max_history_size = 50
    
    @abstractmethod
    def _initialize_metadata(self) -> ToolMetadata:
        """Initialize tool metadata"""
        pass
    
    def check_permissions(self, granted_permissions: List[str]) -> bool:
        """Check if all required permissions are available"""
        missing_permissions = []
        
        for permission in self.metadata.required_permissions:
            if permission not in granted_permissions:
                missing_permissions.append(permission)
        
        if missing_permissions:
            logger.warning(f"Tool {self.metadata.name} is missing required permissions: {', '.join(missing_permissions)}")
            return False
        
        self.permissions_checked = True
        return True
    
    def execute(self, **kwargs) -> Any:
        """
        Execute the tool synchronously
        
        This is a wrapper around the abstract _execute method that adds
        error handling and execution logging.
        """
        # Create execution record
        execution_id = str(uuid.uuid4())
        execution_record = {
            "id": execution_id,
            "timestamp": datetime.now().isoformat(),
            "parameters": kwargs,
            "status": "started"
        }
        
        # Add to history
        self._add_to_history(execution_record)
        
        try:
            # Create progress tracker if supported
            progress_tracker = None
            if self.metadata.supports_progress:
                progress_tracker = ProgressTracker()
                kwargs['progress_tracker'] = progress_tracker
            
            # Execute tool logic
            result = self._execute(**kwargs)
            
            # Update execution record
            execution_record["status"] = "completed"
            execution_record["result"] = str(result) if result is not None else None
            execution_record["completed_at"] = datetime.now().isoformat()
            self._update_history_record(execution_id, execution_record)
            
            return result
        except Exception as e:
            error_msg = f"Error in tool {self.metadata.name}: {str(e)}"
            logger.error(error_msg)
            
            # Update execution record with error
            execution_record["status"] = "failed"
            execution_record["error"] = str(e)
            execution_record["completed_at"] = datetime.now().isoformat()
            self._update_history_record(execution_id, execution_record)
            
            raise
    
    async def execute_async(self, **kwargs) -> Any:
        """
        Execute the tool asynchronously
        
        This is a wrapper around the _execute_async method that adds
        error handling and execution logging.
        """
        # Create execution record
        execution_id = str(uuid.uuid4())
        execution_record = {
            "id": execution_id,
            "timestamp": datetime.now().isoformat(),
            "parameters": kwargs,
            "status": "started"
        }
        
        # Add to history
        self._add_to_history(execution_record)
        
        try:
            # Create progress tracker if supported
            progress_tracker = None
            if self.metadata.supports_progress:
                progress_tracker = ProgressTracker()
                kwargs['progress_tracker'] = progress_tracker
            
            # Check if tool implements async execution
            if hasattr(self, '_execute_async') and callable(getattr(self, '_execute_async')):
                result = await self._execute_async(**kwargs)
            else:
                # Fall back to synchronous execution in a thread
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(None, lambda: self._execute(**kwargs))
            
            # Update execution record
            execution_record["status"] = "completed"
            execution_record["result"] = str(result) if result is not None else None
            execution_record["completed_at"] = datetime.now().isoformat()
            self._update_history_record(execution_id, execution_record)
            
            return result
        except Exception as e:
            error_msg = f"Error in tool {self.metadata.name}: {str(e)}"
            logger.error(error_msg)
            
            # Update execution record with error
            execution_record["status"] = "failed"
            execution_record["error"] = str(e)
            execution_record["completed_at"] = datetime.now().isoformat()
            self._update_history_record(execution_id, execution_record)
            
            raise
    
    def _add_to_history(self, record: Dict[str, Any]) -> None:
        """Add execution record to history"""
        self.execution_history.append(record)
        
        # Keep history at a reasonable size
        if len(self.execution_history) > self.max_history_size:
            self.execution_history.pop(0)
    
    def _update_history_record(self, execution_id: str, updated_record: Dict[str, Any]) -> None:
        """Update an existing history record"""
        for i, record in enumerate(self.execution_history):
            if record.get("id") == execution_id:
                self.execution_history[i] = updated_record
                break
    
    @abstractmethod
    def _execute(self, **kwargs) -> Any:
        """
        Execute tool logic
        
        This is the main method that tools should implement to process input
        and return results.
        """
        pass
    
    def get_parameter_schema(self) -> Dict[str, Dict[str, Any]]:
        """Get parameter schema for the tool"""
        return self.metadata.parameters
    
    def validate_parameters(self, parameters: Dict[str, Any]) -> List[str]:
        """Validate parameters against schema"""
        errors = []
        schema = self.get_parameter_schema()
        
        # Check required parameters
        for param_name, param_info in schema.items():
            if param_info.get("required", False) and param_name not in parameters:
                errors.append(f"Missing required parameter: {param_name}")
        
        return errors

# For backward compatibility
EnhancedTool = Tool
