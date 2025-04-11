# === main.py ===
# Entry point for the AI Assistant MCP
import os
import sys
import argparse
import logging
import asyncio

from core.controller import Controller
from core.mcp_loader import load_mcp_config
from utils.logger import setup_logging

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="AI Assistant MCP")
    
    # Mode selection
    parser.add_argument("--debug", action="store_true", help="Run in debug mode")
    parser.add_argument("--async", action="store_true", dest="async_mode", help="Run with async support")
    parser.add_argument("--config", default="config/mcp_config.json", help="Path to config file")
    
    # Logging options
    parser.add_argument("--log-level", choices=["DEBUG", "INFO", "WARNING", "ERROR"], default="INFO", help="Set logging level")
    parser.add_argument("--log-file", help="Log to file instead of console")
    
    return parser.parse_args()

async def run_async(config, debug=False):
    """Run the controller asynchronously"""
    controller = Controller(config)
    await controller.run_async()

def run_sync(config, debug=False):
    """Run the controller synchronously"""
    controller = Controller(config)
    controller.run()

def main():
    """Main entry point"""
    # Parse command line arguments
    args = parse_arguments()
    
    # Set up logging
    log_level = getattr(logging, args.log_level)
    setup_logging(level=log_level, log_file=args.log_file)
    
    # Load configuration
    config = load_mcp_config(args.config)
    
    # Add command line args to config
    config["runtime"] = {
        "debug": args.debug,
        "async_mode": args.async_mode,
        "log_level": args.log_level
    }
    
    print(f"🧠 AI Assistant MCP starting...")
    
    if args.debug:
        print("Debug mode enabled")
    
    try:
        if args.async_mode:
            # Run with asyncio
            print("Running in async mode")
            asyncio.run(run_async(config, args.debug))
        else:
            # Run synchronously
            run_sync(config, args.debug)
    except KeyboardInterrupt:
        print("\nExiting MCP...")
    except Exception as e:
        print(f"Error: {str(e)}")
        if args.debug:
            import traceback
            traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
