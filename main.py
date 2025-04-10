# === main.py ===
# Entry point for the AI Assistant
from core.controller import Controller
from core.mcp_loader import load_mcp_config

def main():
    config = load_mcp_config("config/mcp_config.json")
    controller = Controller(config)
    controller.run()

if __name__ == "__main__":
    main()