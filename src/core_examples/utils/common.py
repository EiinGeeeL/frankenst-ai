import yaml
from importlib import import_module, resources
from importlib.resources.abc import Traversable
from pathlib import Path
from typing import Dict, Optional

from langgraph.graph.state import CompiledStateGraph
from langgraph.types import RunnableConfig

def _parse_yaml(data: Dict) -> Dict:
    """
    Replace $() expressions in a dictionary with their resolved values.

    Args:
        data (Dict): The dictionary containing the data with $() references.

    Returns:
        Dict: The dictionary with all $() expressions replaced.
    """

    def resolve_value(value, context):
        """
        Recursively resolve $() expressions in a value.

        Args:
            value: The value to resolve, which may be a string, list, or dict.
            context: The dictionary context to use for resolving $() references.

        Returns:
            The resolved value.
        """
        if isinstance(value, str) and '$(' in value:
            while '$(' in value:
                start_index = value.find('$(')
                end_index = value.find(')', start_index)
                if end_index == -1:
                    raise ValueError(f"Unmatched $() in value: {value}")

                # Extract the reference key
                ref_key = value[start_index + 2:end_index]

                # Resolve the reference key from the context
                ref_value = get_nested_value(context, ref_key.split('.'))
                if ref_value is None:
                    raise KeyError(f"Reference '{ref_key}' not found in the context.")

                # Replace $() with the resolved value
                value = value[:start_index] + str(ref_value) + value[end_index + 1:]
            return value
        elif isinstance(value, dict):
            return {k: resolve_value(v, context) for k, v in value.items()}
        elif isinstance(value, list):
            return [resolve_value(v, context) for v in value]
        else:
            return value

    def get_nested_value(data, keys):
        """Retrieve a nested value from a dictionary given a list of keys."""
        for key in keys:
            if not isinstance(data, dict) or key not in data:
                return None
            data = data[key]
        return data

    return resolve_value(data, data)


def _read_text_resource(resource_path: str | Path | Traversable, encoding: str = "utf-8") -> str:
    if isinstance(resource_path, Traversable):
        return resource_path.read_text(encoding=encoding)

    return Path(resource_path).expanduser().read_text(encoding=encoding)


def read_yaml(path_to_yaml: str | Path | Traversable) -> Optional[Dict]:
    """
    Read and parse a YAML file.

    Args:
        path_to_yaml (Path): A Path object representing the location of the YAML file.

    Returns:
        Optional[Dict]: A dictionary containing the parsed YAML data if successful,
                        or None if the file is empty or contains invalid YAML.

    Raises:
        FileNotFoundError: If the specified YAML file doesn't exist or isn't accessible.
        yaml.YAMLError: If there's an error parsing the YAML content.
        Exception: For any other unexpected errors.
    """

    try:
        yaml_content = yaml.safe_load(_read_text_resource(path_to_yaml))
        parsed_yaml_context = _parse_yaml(yaml_content)
        return parsed_yaml_context
    except FileNotFoundError:
        raise FileNotFoundError(f"The configuration file '{path_to_yaml}' does not exist.")
    except yaml.YAMLError as e:
        raise yaml.YAMLError(f"Error parsing YAML file {e}")
    except Exception as e:
        raise Exception(f"An unexpected error occurred {e}")
    
def load_node_registry(path_to_yaml: str | Path | Traversable) -> dict[str, dict]:
    """Read config_nodes.yml and return a dict keyed by node ``id``.

    The returned structure mirrors the old ``read_yaml`` output so that layout
    access patterns such as ``CONFIG_NODES["OAKLANG_NODE"]["name"]`` are
    unchanged.

    Args:
        path_to_yaml (Path): Path to a node registry YAML file with a top-level
            ``nodes`` list where each entry has at least an ``id`` field.

    Returns:
        dict[str, dict]: Mapping from node id to the remaining node fields
            (``name``, ``type``, ``description``, ``route``, …).

    Raises:
        FileNotFoundError: If the file does not exist.
        yaml.YAMLError: If the file cannot be parsed as YAML.
        KeyError: If any node entry is missing the ``id`` field.
    """
    try:
        data = yaml.safe_load(_read_text_resource(path_to_yaml))
        return {
            node["id"]: {k: v for k, v in node.items() if k != "id"}
            for node in data["nodes"]
        }
    except FileNotFoundError:
        raise FileNotFoundError(f"The configuration file '{path_to_yaml}' does not exist.")
    except yaml.YAMLError as e:
        raise yaml.YAMLError(f"Error parsing YAML file {e}")


def resolve_package_resource(package: str, *relative_parts: str) -> Traversable:
    """Resolve a package resource without relying on filesystem-relative module paths."""

    resource = resources.files(package)
    for part in relative_parts:
        resource = resource.joinpath(part)
    return resource


def _get_core_constants_module():
    try:
        return import_module("core_examples.constants")
    except ImportError:
        return None


def get_project_root_path() -> Path:
    """Return the configured project root or fall back to the repository root."""

    fallback = Path(__file__).resolve().parents[3]
    constants_module = _get_core_constants_module()
    configured_path = getattr(constants_module, "PROJECT_ROOT_PATH", None) if constants_module else None

    return Path(configured_path).expanduser().resolve() if configured_path else fallback


def get_default_artifacts_directory() -> Path:
    """Return the default artifacts directory, using constants only when available."""

    project_root_path = get_project_root_path()
    constants_module = _get_core_constants_module()
    configured_path = getattr(constants_module, "ARTIFACTS_DIRECTORY_PATH", None) if constants_module else None

    return Path(configured_path).expanduser().resolve() if configured_path else project_root_path / "artifacts"


def get_default_logs_directory() -> Path:
    """Return the default logs directory, using constants only when available."""

    project_root_path = get_project_root_path()
    constants_module = _get_core_constants_module()
    configured_path = getattr(constants_module, "LOGS_DIRECTORY_PATH", None) if constants_module else None

    return Path(configured_path).expanduser().resolve() if configured_path else project_root_path / "logs"


def resolve_configured_path(path_value: str | Path, base_dir: str | Path) -> Path:
    """Resolve an absolute or base-dir-relative path from configuration."""

    path = Path(path_value).expanduser()
    if path.is_absolute():
        return path

    return Path(base_dir).expanduser().resolve() / path


def load_and_clean_text_file(file_path: str | Path | Traversable, remove_empty_lines: bool = False) -> str:
    try:
        content = _read_text_resource(file_path)
        if remove_empty_lines:
            content = "\n".join(line.strip() for line in content.splitlines() if line.strip())
        else:
            content = content.strip()
        return content
    except FileNotFoundError:
        raise FileNotFoundError(f"Not found the file <{file_path}>.")
    
def save_text_to_artifact(
    content: str,
    filename: str | None = None,
    artifacts_dir: str | Path | None = None,
) -> Path:
    project_root_path = get_project_root_path()
    target_dir = resolve_configured_path(
        artifacts_dir if artifacts_dir is not None else get_default_artifacts_directory(),
        project_root_path,
    )
    target_dir.mkdir(parents=True, exist_ok=True)

    if filename is None:
        filename = f"artifact_{project_root_path.name}.txt"
    elif not filename.endswith('.txt'):
        filename += '.txt'

    file_path = target_dir / filename

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

    return file_path

async def print_process_astream(graph: CompiledStateGraph, message_input: dict, runnable_config: Optional[RunnableConfig] = None):
    events = []
    async for event in graph.astream(message_input, runnable_config, stream_mode="updates"):
        events.append(event)
        print(event)
        print("\n")

    return events[-1]