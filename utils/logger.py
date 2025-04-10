import datetime

LOG_PATH = "mcp.log"

def log_event(source, action, result=None):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] [{source}] {action}"

    if result:
        log_line += f" => {result[:100]}..." if len(result) > 100 else f" => {result}"

    with open(LOG_PATH, "a") as f:
        f.write(log_line + "\n")
