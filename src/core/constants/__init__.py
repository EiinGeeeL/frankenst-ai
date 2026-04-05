from pathlib import Path

CORE_PACKAGE_PATH = Path(__file__).resolve().parent.parent
CONFIG_DIRECTORY_PATH = CORE_PACKAGE_PATH / "config"
CONFIG_FILE_PATH = CONFIG_DIRECTORY_PATH / "config.yml"
CONFIG_NODES_FILE_PATH = CONFIG_DIRECTORY_PATH / "config_nodes.yml"

