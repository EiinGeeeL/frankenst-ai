from pathlib import Path

p1 = Path('src/core/config/config.yml')
CONFIG_FILE_PATH = next(
    (Path(*p1.parts[i:]) for i in range(len(p1.parts)) if Path(*p1.parts[i:]).exists()),
    p1
)

p2 = Path('src/core/config/config_nodes.yml')
CONFIG_NODES_FILE_PATH = next(
    (Path(*p2.parts[i:]) for i in range(len(p2.parts)) if Path(*p2.parts[i:]).exists()),
    p2
)
