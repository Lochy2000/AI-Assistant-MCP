# 🧠 AI Assistant MCP (Master Control Platform)

A modular AI assistant system inspired by Claude Desktop and Cursor, designed to route tasks to local agents/tools using local LLMs (via Ollama) or future cloud backends.

## 📌 Project Overview

This assistant is built around a modular architecture where:

- The Controller (core logic) routes user input to various agents.
- Agents handle specific domains like code generation or diagnostics.
- Tools are utilities agents can use (file access, shell commands, system specs, webhooks).
- A local or remote LLM handles reasoning and generation (via wrappers).
- The CLI interface lets you interact with the system easily.

## 🔄 Recent Architectural Enhancements

The system has recently undergone significant architectural improvements to establish a more robust foundation:

### 1. Event-Based Communication System
- Implemented an event bus for inter-component communication
- Added event subscription and publishing capabilities 
- Components can now respond to system events without tight coupling

### 2. Session Management
- Created a session system to track user interactions over time
- Implemented context storage within sessions for state management
- Added session history tracking for better user experience

### 3. Enhanced Component Architecture
- Redesigned base classes for agents and tools with metadata support
- Added capability and dependency management for components
- Created a more powerful registry system with categorization

### 4. Asynchronous Operations
- Added support for async/await patterns throughout the system
- Implemented non-blocking operations for better performance
- Created a middleware pipeline for processing commands

### 5. Robust Error Handling
- Improved error detection and reporting
- Added graceful dependency management
- Enhanced logging system for better diagnostics

### 6. Memory & State Management
- Added persistent memory for agents between executions
- Implemented structured data storage for components
- Created history tracking for operations

## 🧱 File Structure

ai_assistant_mcp/
├── main.py                    # 🔹 Entry point of the app
│
├── config/
│   └── mcp_config.json        # 🌐 Claude-style config for agents/tools
│
├── core/                      # 🧠 Core system logic
│   ├── controller.py          # Enhanced controller with event system and sessions
│   ├── registry.py            # Improved registry with metadata and discovery
│   ├── events.py              # Event bus for inter-component communication
│   ├── adapters.py            # Adapters for legacy components
│   └── mcp_loader.py          # Loads and parses config
│
├── llm/                       # 🧠 LLM Wrappers (local/cloud)
│   ├── base.py                # LLM interface
│   ├── ollama_wrapper.py      # Wrapper for local models (via Ollama)
│   └── openai_wrapper.py      # (optional) API-based fallback
│
├── agents/                    # 🤖 Modular AI agents
│   ├── base.py                # Enhanced agent base with metadata and memory
│   ├── code_agent.py          # Improved code agent with project capabilities
│   ├── diagnostics_agent.py   # System diagnostics agent
│   └── help_agent.py          # Help and documentation agent
│
├── tools/                     # 🛠️ Plug-in utilities
│   ├── base.py                # Enhanced tool base with metadata and async support
│   ├── file_tool.py           # Advanced file operations tool
│   ├── command_tool.py        # Shell command execution tool
│   ├── specs_tool.py          # System specifications tool
│   └── n8n_tool.py            # Workflow automation trigger (placeholder)
│
├── ui/
│   └── cli.py                 # 💬 CLI interaction layer
│
└── utils/                     # ⚙️ General helpers
    ├── helpers.py             # Argument parsing utilities
    └── logger.py              # Enhanced logging with structured events

## 🚀 Setup Instructions

### 1. Clone the repo and navigate into it:

```bash
git clone <repo-url>
cd ai_assistant_mcp
```

### 2. Set up a virtual environment (optional but recommended):

```bash
python -m venv venv
.env\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

### 3. Install dependencies:

```bash
# Core dependencies (minimal functionality)
pip install -e .

# Optional: for full functionality with system diagnostics
pip install psutil
```

### 4. Install and run Ollama:

Download from https://ollama.com

```bash
ollama run deepseek-coder
```

### 5. Run the CLI interface:

```bash
python main.py
```

Or with debug mode:

```bash
python main.py --debug
```

### 6. Try commands like:

```bash
# Basic commands
help
list agents
list tools

# Getting help on specific topics
run help code
run help diagnostics
run help tools

# Code generation
run code create a python calculator
run code create a new project for a react todo app
run code add a file called styles.css to add styling for the todo app

# System diagnostics
run diagnostics check cpu
run diagnostics check ram
run diagnostics check os

# Direct tool usage
use tool file action=read path=readme.md
use tool file action=write path=test.txt content="hello world"
use tool command raw_input="echo Hello from terminal"
```

## ⚙️ How It Works

### Enhanced Architecture

1. **Event-Based Communication**:
   - Components communicate via events
   - Events can be published and subscribed to
   - Components react to system state changes

2. **Session Management**:
   - User interactions are tracked in sessions
   - Sessions maintain context between commands
   - Session history tracks user activities

3. **Component System**:
   - Components declare capabilities and dependencies
   - Registry manages and categorizes components
   - Metadata provides discoverability and documentation

4. **Agents**:
   - Agents use declarative metadata
   - Memory provides state between executions
   - Structured error handling and dependency checking

5. **Tools**:
   - Tools provide parameter validation and schemas
   - Asynchronous operation for better performance
   - Progress tracking for long-running operations

## 📍 Implementation Roadmap

Phase 1: **Core Infrastructure** ✅
- ✅ Refactor registry and controller for dependency injection
- ✅ Implement event bus system
- ✅ Create standardized message formats
- ✅ Enhance error handling and logging

Phase 2: **Agent Framework Enhancement** 🔄
- ✅ Implement agent communication protocol
- ✅ Add persistent memory capabilities
- ✅ Create agent lifecycle management
- ⏳ Develop agent capability discovery mechanism

Phase 3: **Tool System Upgrades** 🔄
- ✅ Enhance tool interface with capability descriptors
- ✅ Implement permission system for tools
- ⏳ Create tool dependency resolution
- ⏳ Add progress reporting for long-running operations

Phase 4: **System Integration** ⏳
- ⏳ VSCode extension integration framework
- ⏳ File system monitoring capabilities
- ⏳ Process management enhancements
- ⏳ Project scaffolding system

Phase 5: **API Layer** ⏳
- ⏳ REST API for system interaction
- ⏳ WebSocket support for real-time communication
- ⏳ Authentication and authorization layer
- ⏳ API documentation and client libraries

Phase 6: **GUI Development** ⏳
- ⏳ Web-based interface
- ⏳ Real-time updates and notifications
- ⏳ Project management UI
- ⏳ Settings and configuration interface

## 💡 Long-Term Vision

- Frontend GUI using Flask or Tauri
- Memory/plan management agent
- Multi-agent task delegation
- Cloud fallback to OpenAI or GitHub Models
- VSCode extension integration
- Vector DB integration (RAG)