from importlib.resources import files
from pathlib import Path

CORE_PACKAGE_PATH = Path(__file__).resolve().parent.parent
SRC_DIRECTORY_PATH = CORE_PACKAGE_PATH.parent
PROJECT_ROOT_PATH = SRC_DIRECTORY_PATH.parent
LOGS_DIRECTORY_PATH = PROJECT_ROOT_PATH / "logs"
DEFAULT_LOG_FILE_PATH = LOGS_DIRECTORY_PATH / "application.log"
ARTIFACTS_DIRECTORY_PATH = PROJECT_ROOT_PATH / "artifacts"
CONFIG_DIRECTORY_PATH = files("core_examples.config")
CONFIG_FILE_PATH = CONFIG_DIRECTORY_PATH.joinpath("config.yml")
CONFIG_LOGGING_FILE_PATH = CONFIG_DIRECTORY_PATH.joinpath("config_logging.yml")
CONFIG_NODES_FILE_PATH = CONFIG_DIRECTORY_PATH.joinpath("config_nodes.yml")

