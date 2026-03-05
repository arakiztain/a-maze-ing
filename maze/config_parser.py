from pydantic.dataclasses import dataclass as pydantic_dataclass
from pydantic import Field, model_validator
from typing import Tuple, Any
import random
import os


class ConfigError(Exception):
    """Raised when the configuration file contains invalid values."""

    pass


SENSITIVE_FILES: frozenset[str] = frozenset({
    "Makefile", "makefile", "config.txt", "pyproject.toml",
    "README.md", "readme.md", ".env", ".gitignore"
})


@pydantic_dataclass
class MazeConfig:
    """Validated configuration for the maze generator.

    Parses and validates all parameters needed to generate a maze.
    Entry and exit coordinates are checked to be within maze bounds.
    If no seed is provided, a random one is generated automatically.

    Attributes:
        width: Number of columns in the maze. Must be between 2 and 46.
        height: Number of rows in the maze. Must be between 2 and 46.
        entry: Entry point coordinates as (x, y).
        exit: Exit point coordinates as (x, y).
        output_file: Path to write the maze bitmask output file.
        perfect: If True, the maze is perfect (one unique path).
            If False, alternative paths are added.
        animation: If True, animate the maze generation in the terminal.
        seed: Random seed for reproducibility. Auto-generated if None.
        user_set_seed: True if the seed was explicitly set by the user.

    Raises:
        ConfigError: If entry or exit are out of bounds, or if the
            output file name is reserved.

    Example config file::

        WIDTH = 12
        HEIGHT = 12
        ENTRY = 0,0
        EXIT = 11,11
        OUTPUT_FILE = maze.txt
        PERFECT = true
        ANIMATION = false
        SEED = 1234
    """

    width: int = Field(..., ge=2, le=46)
    height: int = Field(..., ge=2, le=46)
    entry: Tuple[int, int] = Field(...)
    exit: Tuple[int, int] = Field(...)
    output_file: str = Field(...)
    perfect: bool = Field(default=True)
    animation: bool | None = Field(default=False)
    seed: int | None = Field(default=None)
    user_set_seed: bool = Field(default=False)

    @model_validator(mode="after")
    def entry_validator(self) -> "MazeConfig":
        """Validate entry, exit coordinates and output file name.

        Checks that entry and exit are within maze bounds, and that
        the output file is not a reserved name. Also generates a random
        seed if none was provided, and sets user_set_seed accordingly.

        Returns:
            The validated MazeConfig instance.

        Raises:
            ConfigError: If any validation check fails.
        """
        entry_x, entry_y = self.entry
        exit_x, exit_y = self.exit

        errors: list[str] = []

        if entry_x >= self.width or entry_y >= self.height:
            errors.append(
                f"Entry {self.entry} out of the limits:"
                f" ({self.width}, {self.height})"
            )

        if exit_x >= self.width or exit_y >= self.height:
            errors.append(
                f"Exit {self.exit} out of the limits:"
                f" ({self.width}, {self.height})"
            )

        if self.output_file in SENSITIVE_FILES:
            errors.append(
                f"Output file name '{self.output_file}' is reserved."
            )

        if ".." in self.output_file or self.output_file.startswith("/"):
            errors.append(
                f"Output file path '{self.output_file}' is not allowed."
            )

        if os.path.basename(self.output_file) in SENSITIVE_FILES:
            errors.append(
                f"Output file name '{self.output_file}' is reserved."
            )

        if errors:
            raise ConfigError("; ".join(errors))

        if self.seed is None:
            self.seed = random.randint(0, 999999)
        else:
            self.user_set_seed = True

        return self


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
    for line in data:
        if not line.strip() or line.startswith("#"):
            continue
        key, value = line.split("=", 1)
        key = key.strip().upper()
        value = value.strip()

        if key in ["WIDTH", "HEIGHT"]:
            config_dict[key.lower()] = int(value)
        elif key in ["ENTRY", "EXIT"]:
            config_dict[key.lower()] = tuple(map(int, value.split(",")))
        elif key == "PERFECT":
            config_dict[key.lower()] = value.lower() == "true"
        elif key == "ANIMATION":
            config_dict[key.lower()] = value.lower() == "true"
        elif key == "SEED":
            config_dict[key.lower()] = (
                int(value) if value.strip() and
                value.lower() != "none" else None
            )
        else:
            config_dict[key.lower()] = value

    return MazeConfig(**config_dict)
