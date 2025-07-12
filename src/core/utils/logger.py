import os
import sys
import logging

def setup_logging(config: dict) -> None:
    log_dir = "logs"
    log_filepath = os.path.join(log_dir, config['logging']['log_file'])
    os.makedirs(log_dir, exist_ok=True)
    
    logging.basicConfig(
        level= logging.INFO,
        format= config['logging']['format'],
        datefmt=config['logging']['datefmt'],
        handlers=[
            logging.FileHandler(log_filepath),
            logging.StreamHandler(sys.stdout),
        ]
    )