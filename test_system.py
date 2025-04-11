"""
Test script for MCP system
"""
import os
import sys
import logging
from core.controller import Controller
from core.registry import Registry
from core.mcp_loader import load_mcp_config
from agents.code_agent import CodeAgent
from agents.diagnostics_agent import DiagnosticsAgent
from agents.help_agent import HelpAgent
from tools.file_tool import FileTool
from tools.command_tool import CommandTool
from tools.specs_tool import SpecsTool
from tools.n8n_tool import N8nTool
from utils.logger import setup_logging

# Set up logging
setup_logging(level=logging.INFO)
logger = logging.getLogger('mcp.test')

def test_registry():
    """Test registry functionality"""
    print("Testing Registry...")
    registry = Registry()
    
    # Register test components
    registry.register_agent("test_agent", "test_agent_instance")
    registry.register_tool("test_tool", "test_tool_instance")
    
    # Test retrieval
    assert registry.get_agent("test_agent") == "test_agent_instance"
    assert registry.get_tool("test_tool") == "test_tool_instance"
    
    # Test listing
    assert "test_agent" in registry.get_names("agent")
    assert "test_tool" in registry.get_names("tool")
    
    print("Registry test passed!")

def test_agent_creation():
    """Test creating agents"""
    print("Testing agent creation...")
    
    # Create agents
    code_agent = CodeAgent()
    diagnostics_agent = DiagnosticsAgent()
    help_agent = HelpAgent()
    
    # Check if metadata is initialized
    assert code_agent.metadata is not None
    assert diagnostics_agent.metadata is not None
    assert help_agent.metadata is not None
    
    # Check capabilities
    assert "code_generation" in code_agent.get_capabilities()
    assert "system_info" in diagnostics_agent.get_capabilities()
    assert "documentation" in help_agent.get_capabilities()
    
    print("Agent creation test passed!")

def test_tool_creation():
    """Test creating tools"""
    print("Testing tool creation...")
    
    # Create tools
    file_tool = FileTool()
    command_tool = CommandTool()
    
    try:
        specs_tool = SpecsTool()
        assert specs_tool.metadata is not None
    except ImportError:
        print("Warning: SpecsTool requires psutil which is not installed - skipping this test")
    
    n8n_tool = N8nTool()
    
    # Check if metadata is initialized
    assert file_tool.metadata is not None
    assert command_tool.metadata is not None
    assert n8n_tool.metadata is not None
    
    print("Tool creation test passed!")

def test_controller_setup():
    """Test controller initialization"""
    print("Testing controller setup...")
    
    # Create mock config
    config = {"test": "config"}
    
    # Initialize controller
    controller = Controller(config)
    
    # Check if registry is initialized
    assert controller.registry is not None
    
    # Check if agents and tools are registered
    assert "code" in controller.registry.get_names("agent")
    assert "diagnostics" in controller.registry.get_names("agent")
    assert "help" in controller.registry.get_names("agent")
    
    assert "file" in controller.registry.get_names("tool")
    assert "command" in controller.registry.get_names("tool")
    
    # These may fail depending on dependencies, so we don't assert them
    print(f"Tools registered: {controller.registry.get_names('tool')}")
    
    print("Controller setup test passed!")

def test_file_tool():
    """Test file operations"""
    print("Testing file tool...")
    
    file_tool = FileTool()
    test_file = "test_file_tool.txt"
    test_content = "Hello, World!"
    
    # Write file
    result = file_tool.execute(action="write", path=test_file, content=test_content)
    print(f"  Write result: {result}")
    
    # Read file
    result = file_tool.execute(action="read", path=test_file)
    print(f"  Read result: {result}")
    assert result == test_content
    
    # Get file info
    result = file_tool.execute(action="info", path=test_file)
    print(f"  Info result: {result}")
    
    # Delete file
    result = file_tool.execute(action="delete", path=test_file)
    print(f"  Delete result: {result}")
    
    print("File tool test passed!")

def run_tests():
    """Run all tests"""
    print("=== Running MCP System Tests ===")
    
    try:
        test_registry()
        test_agent_creation()
        test_tool_creation()
        test_controller_setup()
        test_file_tool()
        
        print("\n✅ All tests passed! The MCP system is working correctly.")
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(run_tests())
