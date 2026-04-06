import sys
import logging
from pathlib import Path

from core_examples.utils.common import (
    get_default_logs_directory,
    get_project_root_path,
    resolve_configured_path,
)

def setup_logging(config: dict, log_dir: str | Path | None = None) -> Path:
    project_root_path = get_project_root_path()
    log_dir = resolve_configured_path(
        log_dir if log_dir is not None else get_default_logs_directory(),
        project_root_path,
    )
    log_dir.mkdir(parents=True, exist_ok=True)
    log_filepath = log_dir / config['logging']['log_file']
    
    logging.basicConfig(
        level= logging.INFO,
        format= config['logging']['format'],
        datefmt=config['logging']['datefmt'],
        handlers=[
            logging.FileHandler(log_filepath),
            logging.StreamHandler(sys.stdout),
        ],
        force=True,
    )

    return log_filepath