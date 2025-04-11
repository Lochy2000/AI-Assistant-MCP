import datetime
import logging
import os
import json
from typing import Dict, Any, Optional

# Default log file path
DEFAULT_LOG_PATH = "mcp.log"

# Configure logger
logger = logging.getLogger('mcp')

def setup_logging(level=logging.INFO, log_file=None, console=True):
    """
    Set up logging configuration
    
    Args:
        level: Logging level (DEBUG, INFO, etc.)
        log_file: Path to log file (if None, uses DEFAULT_LOG_PATH)
        console: Whether to also log to console
    """
    logger.setLevel(level)
    
    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create formatters
    file_formatter = logging.Formatter(
        '[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    console_formatter = logging.Formatter(
        '[%(levelname)s] %(message)s'
    )
    
    # File handler
    if log_file:
        file_path = log_file
    else:
        file_path = DEFAULT_LOG_PATH
    
    # Ensure log directory exists
    log_dir = os.path.dirname(file_path)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)
    
    file_handler = logging.FileHandler(file_path)
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    # Console handler (optional)
    if console:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
    
    logger.info(f"Logging initialized at level {logging.getLevelName(level)}")
    return logger

def log_event(source, action, result=None):
    """
    Log an event to the event log file
    
    This is a simpler logging function for backward compatibility
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] [{source}] {action}"

    if result:
        log_line += f" => {result[:100]}..." if len(result) > 100 else f" => {result}"

    with open(DEFAULT_LOG_PATH, "a") as f:
        f.write(log_line + "\n")
    
    # Also log to structured logger
    if isinstance(result, Exception):
        logger.error(f"{source}: {action} - {str(result)}")
    else:
        logger.info(f"{source}: {action}")

class EventLogger:
    """Enhanced structured event logger"""
    
    def __init__(self, log_file="events.jsonl"):
        self.log_file = log_file
        
        # Ensure directory exists
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
    
    def log(self, 
            event_type: str, 
            source: str, 
            action: str, 
            metadata: Optional[Dict[str, Any]] = None,
            status: str = "success",
            message: Optional[str] = None) -> None:
        """
        Log a structured event
        
        Args:
            event_type: Type of event (e.g., 'agent', 'tool', 'system')
            source: Source of the event (e.g., 'CodeAgent', 'FileTool')
            action: Action performed (e.g., 'generate_code', 'read_file')
            metadata: Additional metadata as dictionary
            status: Status of the event ('success', 'failed', 'warning', etc.)
            message: Optional message describing the event
        """
        event = {
            "timestamp": datetime.datetime.now().isoformat(),
            "event_type": event_type,
            "source": source,
            "action": action,
            "status": status
        }
        
        if metadata:
            event["metadata"] = metadata
        
        if message:
            event["message"] = message
        
        # Write to JSON Lines file
        with open(self.log_file, "a") as f:
            f.write(json.dumps(event) + "\n")
        
        # Also log to standard logger
        log_message = f"{source}.{action} - {message or status}"
        if status == "success":
            logger.info(log_message)
        elif status == "failed":
            logger.error(log_message)
        else:
            logger.warning(log_message)
