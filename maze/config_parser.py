from typing import Any
from mazegen.maze_config import MazeConfig


def parse_config(path: str) -> MazeConfig:
    """Parse a maze configuration file and return a validated MazeConfig.

    Reads a plain text config file with key=value pairs, one per line.
    Lines starting with '#' and blank lines are ignored. Keys are
    case-insensitive. The parsed values are validated by MazeConfig.

    Supported keys:
        WIDTH, HEIGHT: Integer dimensions of the maze.
        ENTRY, EXIT: Comma-separated coordinates e.g. '0,0'.
        OUTPUT_FILE: Path string for the output file.
        PERFECT: Boolean ('true'/'false').
        ANIMATION: Boolean ('true'/'false').
        SEED: Integer or 'none' for a random seed.

    Args:
        path: Path to the configuration file.

    Returns:
        A validated MazeConfig instance.

    Raises:
        FileNotFoundError: If the config file does not exist.
        ConfigError: If the config values fail validation.
    """
    try:
        with open(path, "r") as f:
            data = f.read().splitlines()
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return None  # type: ignore

    config_dict: dict[str, Any] = {}
    user_set_seed: bool = False
    for line in data:
        if not line.strip() or line.startswith("#"):
            continue
        key, value = line.split("=", 1)
        key = key.strip().upper()
        value = value.strip()

        if key == "SEED" and value and value.lower() != "none":
            user_set_seed = True
        if key in {"ENTRY", "EXIT"}:
            config_dict[key.lower()] = value.split(",")
        elif value:
            config_dict[key.lower()] = value

    return MazeConfig(**config_dict, user_set_seed=user_set_seed)
