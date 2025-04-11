"""
Enhanced Controller Module for MCP
Provides advanced orchestration with event system and dependency management
"""
import asyncio
import uuid
import logging
from typing import Dict, List, Any, Callable, Type, Optional
from datetime import datetime

from core.registry import Registry
from core.events import EventBus, Event

# Configure logging
logger = logging.getLogger('mcp.controller')

class Session:
    """Represents a user interaction session"""
    def __init__(self, session_id: str = None):
        self.session_id = session_id or str(uuid.uuid4())
        self.created_at = datetime.now()
        self.context: Dict[str, Any] = {}
        self.history: List[Dict[str, Any]] = []
    
    def add_to_history(self, entry: Dict[str, Any]):
        """Add an entry to session history"""
        entry['timestamp'] = datetime.now()
        self.history.append(entry)
    
    def get_context(self, key: str, default=None) -> Any:
        """Get a value from session context"""
        return self.context.get(key, default)
    
    def set_context(self, key: str, value: Any):
        """Set a value in session context"""
        self.context[key] = value
        return self


class Controller:
    """
    Enhanced controller with advanced orchestration capabilities
    
    Improvements:
    - Event-based communication between components
    - Session management
    - Async operation support
    - Enhanced error handling
    - Plugin system for modules
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.registry = Registry()
        self.config = config
        self.event_bus = EventBus()
        self.sessions: Dict[str, Session] = {}
        self.current_session = self._create_session()
        self._middleware_pipeline: List[Callable] = []
        self._load_modules()
        
    def _create_session(self) -> Session:
        """Create and register a new session"""
        session = Session()
        self.sessions[session.session_id] = session
        return session
        
    def register_middleware(self, middleware: Callable):
        """Register middleware to process commands"""
        self._middleware_pipeline.append(middleware)
        return self
        
    async def process_command(self, command: str, args: str) -> str:
        """Process a command through middleware and route to handler"""
        context = {
            'command': command,
            'args': args,
            'session': self.current_session,
            'response': None,
            'error': None
        }
        
        # Run command through middleware pipeline
        try:
            for middleware in self._middleware_pipeline:
                await middleware(context)
                if context.get('error'):
                    break
            
            # If no middleware handled it and no error, process command
            if not context.get('response') and not context.get('error'):
                context['response'] = await self._route_command(command, args)
                
        except Exception as e:
            context['error'] = str(e)
            # Publish error event
            self.event_bus.publish(Event('error', {
                'message': str(e),
                'command': command,
                'args': args
            }))
        
        # Add to session history
        self.current_session.add_to_history({
            'command': command,
            'args': args,
            'response': context.get('response'),
            'error': context.get('error')
        })
        
        # Return result or error
        return context.get('response') or f"Error: {context.get('error')}"
    
    async def _route_command(self, command: str, args: str) -> str:
        """Route command to appropriate handler"""
        if command == "run":
            parts = args.split(maxsplit=1)
            if len(parts) < 1:
                return "Usage: run <agent> <args>"
            
            agent_name = parts[0].lower()
            agent_args = parts[1] if len(parts) > 1 else ""
            
            agent = self.registry.get_agent(agent_name)
            if not agent:
                return f"Unknown agent: {agent_name}"
            
            # Publish event before running agent
            self.event_bus.publish(Event('agent.before_run', {
                'agent': agent_name,
                'args': agent_args
            }))
            
            try:
                # Check if agent supports async
                if hasattr(agent, 'run_async') and callable(agent.run_async):
                    result = await agent.run_async(agent_args)
                else:
                    # Run synchronously if no async support
                    result = agent.run(agent_args)
                    
                # Publish success event
                self.event_bus.publish(Event('agent.after_run', {
                    'agent': agent_name,
                    'args': agent_args,
                    'result': result
                }))
                
                return result
            except Exception as e:
                # Publish failure event
                self.event_bus.publish(Event('agent.error', {
                    'agent': agent_name,
                    'args': agent_args,
                    'error': str(e)
                }))
                raise
                
        elif command == "use":
            parts = args.split(maxsplit=2)
            if len(parts) < 2 or parts[0] != "tool":
                return "Usage: use tool <toolname> <args>"
            
            tool_name = parts[1].lower()
            tool_args = parts[2] if len(parts) > 2 else ""
            
            tool = self.registry.get_tool(tool_name)
            if not tool:
                return f"Unknown tool: {tool_name}"
            
            # Publish event before using tool
            self.event_bus.publish(Event('tool.before_use', {
                'tool': tool_name,
                'args': tool_args
            }))
            
            try:
                # Process args and execute tool
                from utils.helpers import parse_kwargs
                kwargs = parse_kwargs(tool_args)
                
                # Fallback to raw_input if no key=value found
                if not kwargs and tool_args:
                    kwargs = {"raw_input": tool_args}
                
                # Check if tool supports async
                if hasattr(tool, 'execute_async') and callable(tool.execute_async):
                    result = await tool.execute_async(**kwargs)
                else:
                    # Run synchronously if no async support
                    result = tool.execute(**kwargs)
                
                # Publish success event
                self.event_bus.publish(Event('tool.after_use', {
                    'tool': tool_name,
                    'args': tool_args,
                    'result': result
                }))
                
                return result
            except Exception as e:
                # Publish failure event
                self.event_bus.publish(Event('tool.error', {
                    'tool': tool_name,
                    'args': tool_args,
                    'error': str(e)
                }))
                raise
                
        else:
            return f"Unknown command: {command}"
    
    async def run_async(self):
        """Run the controller asynchronously"""
        print("MCP is ready. Type a command like `run code` or `use tool`:")
        
        while True:
            user_input = input("» ").strip()
            if not user_input:
                print("Please enter a command. Type `help` or `?`.")
                continue
                
            if user_input.lower() in ["exit", "quit"]:
                break
                
            parts = user_input.split(maxsplit=1)
            command = parts[0].lower()
            args = parts[1] if len(parts) > 1 else ""
            
            if command in ["help", "?"]:
                self._print_help()
            elif command == "list":
                self._handle_list_command(args)
            else:
                result = await self.process_command(command, args)
                print(result)
    
    def run(self):
        """Run the controller synchronously by starting an event loop"""
        loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(self.run_async())
        except KeyboardInterrupt:
            print("\nExiting...")
        finally:
            loop.close()
    
    def _handle_list_command(self, args: str):
        """Handle the list command"""
        if not args:
            print("Usage: list agents | list tools")
            return
            
        target = args.lower()
        if target == "agents":
            print("Available agents:", ", ".join(self.registry.get_names('agent')))
        elif target == "tools":
            print("Available tools:", ", ".join(self.registry.get_names('tool')))
        else:
            print(f"Unknown list option: {target}. Try: list agents | list tools")
    
    def _print_help(self):
        """Print help information"""
        print("""
🧠 MCP Help Menu

Commands:
  run <agent> <input>         → Run an agent (e.g. run code build a React app)
  use tool <tool> <input>     → Use a tool directly (e.g. use tool command echo hi)
  list agents                 → Show all available agents
  list tools                  → Show all available tools
  help / ?                    → Show this help menu
  exit / quit                 → Exit the assistant

Special Commands:
  session new                 → Start a new session
  session list                → List all sessions
  session switch <id>         → Switch to an existing session
""")

    def _load_modules(self):
        """Load modules based on config"""
        # Load agents
        try:
            from agents.code_agent import CodeAgent
            self.registry.register_agent("code", CodeAgent())
            logger.info("Registered CodeAgent")
        except ImportError as e:
            logger.warning(f"Could not load CodeAgent: {str(e)}")

        try:
            from agents.diagnostics_agent import DiagnosticsAgent
            self.registry.register_agent("diagnostics", DiagnosticsAgent())
            logger.info("Registered DiagnosticsAgent")
        except ImportError as e:
            logger.warning(f"Could not load DiagnosticsAgent: {str(e)}")

        try:
            from agents.help_agent import HelpAgent
            self.registry.register_agent("help", HelpAgent())
            logger.info("Registered HelpAgent")
        except ImportError as e:
            logger.warning(f"Could not load HelpAgent: {str(e)}")

        # Load tools
        try:
            from tools.file_tool import FileTool
            self.registry.register_tool("file", FileTool())
            logger.info("Registered FileTool")
        except ImportError as e:
            logger.warning(f"Could not load FileTool: {str(e)}")

        try:
            from tools.command_tool import CommandTool
            self.registry.register_tool("command", CommandTool())
            logger.info("Registered CommandTool")
        except ImportError as e:
            logger.warning(f"Could not load CommandTool: {str(e)}")

        try:
            from tools.specs_tool import SpecsTool
            self.registry.register_tool("specs", SpecsTool())
            logger.info("Registered SpecsTool")
        except ImportError as e:
            logger.warning(f"Could not load SpecsTool: {str(e)}")

        try:
            from tools.n8n_tool import N8nTool
            self.registry.register_tool("n8n", N8nTool())
            logger.info("Registered N8nTool")
        except ImportError as e:
            logger.warning(f"Could not load N8nTool: {str(e)}")
