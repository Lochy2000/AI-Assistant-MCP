# 🧠 AI Assistant MCP (Master Control Platform)

A modular AI assistant system inspired by Claude Desktop and Cursor, designed to route tasks to local agents/tools using local LLMs (via Ollama) or future cloud backends.

## 📌 Project Overview

This assistant is built around a modular architecture where:

- The Controller (core logic) routes user input to various agents.
- Agents handle specific domains like code generation or diagnostics.
- Tools are utilities agents can use (file access, shell commands, system specs, webhooks).
- A local or remote LLM handles reasoning and generation (via wrappers).
- The CLI interface lets you interact with the system easily.

## 🧱 File Structure (as of now)

ai_assistant_mcp/
├── main.py                    # 🔹 Entry point of the app
│
├── config/
│   └── mcp_config.json        # 🌐 Claude-style config for agents/tools
│
├── core/                      # 🧠 Core system logic
│   ├── controller.py          # Routes input → agents/tools
│   ├── registry.py            # Registers and stores modules
│   └── mcp_loader.py          # Loads and parses config
│
├── llm/                       # 🧠 LLM Wrappers (local/cloud)
│   ├── base.py                # LLM interface
│   ├── ollama_wrapper.py      # Wrapper for local models (via Ollama)
│   └── openai_wrapper.py      # (optional) API-based fallback
│
├── agents/                    # 🤖 Modular AI agents
│   ├── base.py                # Agent interface
│   ├── code_agent.py          # Generates code from user input
│   └── diagnostics_agent.py   # Uses SpecsTool & CommandTool to analyze system
│
├── tools/                     # 🛠️ Plug-in utilities
│   ├── base.py                # Tool interface
│   ├── file_tool.py           # Read/write files (structured via kwargs)
│   ├── command_tool.py        # Run shell commands (supports raw_input)
│   ├── specs_tool.py          # Get CPU/RAM/disk info
│   └── n8n_tool.py            # Trigger n8n automation
│
├── ui/
│   └── cli.py                 # 💬 CLI interaction layer
│
└── utils/                     # ⚙️ General helpers
    ├── helpers.py             # `parse_kwargs()` to extract key=value args
    └── logger.py              # Logging utilities (TBD)

## 🚀 Setup Instructions

### 1. Clone the repo and navigate into it:

```bash
git clone <repo-url>
cd ai_assistant_mcp
```

### 2. Set up a virtual environment (optional but recommended):

```bash
python -m venv venv
.env\Scriptsctivate  # Windows
```

### 3. Install dependencies:

There are no dependencies yet. Future ones will be added to requirements.txt.

### 4. Install and run Ollama:

Download from https://ollama.com

```bash
ollama run deepseek-coder
```

### 5. Run the CLI interface:

```bash
python main.py
```

Then try commands like:

```bash
run code create a react app
run diagnostics check disk
use tool file action=write path=test.txt content="hello world"
use tool file action=read path=test.txt
use tool command raw_input="echo Hello from terminal"
```

## ⚙️ How It Works

### main.py

- Loads the MCP config and starts the controller loop.

### config/mcp_config.json

- Defines external modules (e.g. n8n, file access paths) in Claude-compatible format.

### core/controller.py

- Central brain of the project. It:
  - Loads all agents/tools from their classes
  - Listens for user input
  - Parses commands like `run` or `use tool`
  - Uses `parse_kwargs()` to convert CLI args into structured kwargs

### utils/helpers.py

- `parse_kwargs()` converts `key=value` strings into `**kwargs` dicts.

### agents/*_agent.py

- Each agent handles one responsibility (code, diagnostics, etc.)
- Can call tools under the hood for extended capabilities

### tools/*_tool.py

- Tools do low-level work like reading files, calling commands, or hitting APIs.

## 📍 Next Milestones

- ✅ Add key=value parsing and CLI fallback system
- 🔄 Add fallback to raw_input when no key=value args are given
- 🧪 Wire `DiagnosticsAgent` to call SpecsTool and CommandTool with structured args
- 🔧 Connect CodeAgent to local LLM via Ollama
- 🧰 Add `--debug` and CLI flags to cli.py
- 🧠 Optional: add a HelpAgent that suggests actions

## 💡 Long-Term Vision

- Frontend GUI using Flask or Tauri
- Memory/plan management agent
- Multi-agent task delegation
- Cloud fallback to OpenAI or GitHub Models
- VSCode extension integration
- Vector DB integration (RAG)