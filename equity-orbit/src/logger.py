import logging
import os
import sys
from datetime import datetime

def setup_run_logging():
    """
    Sets up a run-specific logging directory and configures the logger.
    Returns:
        tuple: (logger, run_dir)
        - logger: The configured logger instance.
        - run_dir: Path to the directory created for this run (e.g., logs/20260213_145000).
    """
    # Define the run ID based on current time
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create the logs root dir if it doesn't exist (relative to CWD usually, or project root)
    # Assuming main.py runs from project root
    project_root = os.getcwd()
    logs_root = os.path.join(project_root, "logs")
    run_dir = os.path.join(logs_root, timestamp)
    
    os.makedirs(run_dir, exist_ok=True)
    
    # Define log file path
    log_file = os.path.join(run_dir, "run.log")
    
    # Configure logging
    # Level INFO to capture "post work done" messages
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    logger = logging.getLogger("EquityOrbit")
    
    return logger, run_dir
