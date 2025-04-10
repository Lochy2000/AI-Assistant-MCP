# 🧠 AI Assistant MCP (Master Control Platform)

A modular AI assistant system inspired by Claude Desktop and Cursor, designed to route tasks to local agents/tools using local LLMs (via Ollama) or future cloud backends.

## 📌 Project Overview

This assistant is built around a modular architecture where:

The Controller (core logic) routes user input to various agents.

Agents handle specific domains like code generation or diagnostics.

Tools are utilities agents can use (file access, shell commands, system specs, webhooks).

A local or remote LLM handles reasoning and generation (via wrappers).

The CLI interface lets you interact with the system easily.

## 🧱 File Structure (as of now)

ai_assistant_mcp/
├── main.py                    # Entry point of the app
├── config/
│   └── mcp_config.json        # MCP config using Claude-style structure
├── core/
│   ├── controller.py          # Routes commands to agents/tools
│   ├── registry.py            # Registers and stores agents/tools
│   └── mcp_loader.py          # Loads MCP config from JSON
├── llm/
│   ├── base.py                # Abstract base for LLMs
│   ├── ollama_wrapper.py      # Interface to local LLMs via Ollama
│   └── openai_wrapper.py      # Future cloud fallback wrapper
├── agents/
│   ├── base.py                # Abstract base for agents
│   ├── code_agent.py          # Code generation agent
│   └── diagnostics_agent.py   # System diagnostics agent
├── tools/
│   ├── base.py                # Abstract base for tools
│   ├── file_tool.py           # File I/O operations
│   ├── command_tool.py        # Shell command execution
│   ├── specs_tool.py          # System spec fetcher (CPU, RAM, Disk)
│   └── n8n_tool.py            # Trigger n8n workflows via webhook
├── ui/
│   └── cli.py                 # CLI interface to test the system
└── utils/
    ├── helpers.py             # Misc utility functions
    └── logger.py              # Logging wrapper (not yet implemented)

## 🚀 Setup Instructions

### 1. Clone the repo and navigate into it:

git clone <repo-url>
cd ai_assistant_mcp

#### 2. Set up a virtual environment (optional but recommended):

python -m venv venv
.\venv\Scripts\activate  # Windows

### 3. Install dependencies:
There are no dependencies yet. Future ones will be added to requirements.txt.

### 4. Install and run Ollama:
Download from https://ollama.com

ollama run deepseek-coder

### 5. Run the CLI interface:

python main.py

Then try commands like:

run code create a react app
run diagnostics check system

## ⚙️ How It Works

### main.py

- Loads the MCP config and starts the controller loop.

### config/mcp_config.json

- Defines external modules (e.g. n8n, file access paths) in Claude-compatible format.

### core/mcp_loader.py

- Reads and parses the MCP config JSON.

### core/registry.py

- Keeps track of all available agents and tools in dictionaries.

### core/controller.py

 Central brain of the project. It:

- Loads all agents/tools from their classes

- Listens for user input

- Routes run <agent> commands to the correct agent with arguments

### agents/base.py

- Defines an abstract Agent class with a run(input_text) method.

### tools/base.py

- Defines an abstract Tool class with an execute(**kwargs) method.

### agents/code_agent.py

- Currently prints back received input. Will later call LLM (via Ollama wrapper) to generate code.

### agents/diagnostics_agent.py

- Currently prints back input. Later will use SpecsTool and CommandTool.

### tools/*_tool.py

These are tools for file access, CLI execution, specs gathering, and automation:

FileTool → read/write files

- CommandTool → run bash/cmd commands

- SpecsTool → get CPU/RAM/Disk/OS info

- n8nTool → send requests to local n8n workflows

### llm/ollama_wrapper.py

- Will provide a class to talk to your local LLM models (like Deepseek-Coder, Mistral).

📍 Next Milestones

Implement Tool base class and wire tools into agents

Build OllamaLLM wrapper

Add real logic inside CodeAgent and DiagnosticsAgent

Expand controller.py to handle use tool commands

Add tests and CLI options (like --debug or --agent) in cli.py

Optional: Add logging in logger.py

💡 Long-Term Vision

Frontend GUI using Flask or Tauri

Memory/plan management agent

Multi-agent task delegation

Cloud fallback to OpenAI or GitHub Models

VSCode extension integration

Vector DB integration (RAG)