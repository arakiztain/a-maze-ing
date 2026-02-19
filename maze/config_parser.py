from dataclasses import dataclass
from pydantic.dataclasses import dataclass as pydantic_dataclass
from pydantic import Field, model_validator
from typing import Tuple


class ConfigError(Exception):
    """Raised when configuration file is invalid."""
    pass


@pydantic_dataclass
class MazeConfig:
    width: int = Field(..., ge=0, le=10000)
    height: int = Field(..., ge=0, le=10000)
    entry: Tuple[int, int] = Field(...)
    exit: Tuple[int, int] = Field(...)
    output_file: str = Field(...)
    perfect: bool = Field(default=True)

    @model_validator(mode="after")
    def entry_validator(self):
        entry_x, entry_y = self.entry
        exit_x, exit_y = self.exit

        errors = []

        if (entry_x > self.width or entry_y > self.height):
            errors.append(f"Entry {self.entry} out of the limits: ({self.width}, {self.height})")
        if (exit_x > self.width or exit_y > self.height):
            errors.append(f"Exit {self.exit} out of the limits: ({self.width}, {self.height})")

        if errors:
            raise ConfigError("; ".join(errors))

        return self


def parse_config(path: str) -> MazeConfig:
    try:
        with open(path, "r") as f:
            data = f.read().splitlines()
    except FileNotFoundError:
        print("Error....")

    config_dict = {}
    for line in data:
        if not line.strip() or line.startswith("#"):
            continue
        key, value = line.split("=")
        key.strip().upper()
        value = value.strip()
        
        if key in ["WIDTH", "HEIGHT"]:
            value = int(value)
        elif key in ["ENTRY", "EXIT"]:
            value = tuple(map(int, value.split(",")))
        elif key == "PERFECT":
            value = value.lower() == "true"

        
        config_dict[key.lower()] = value
        
    print(config_dict)
    return MazeConfig(**config_dict)


parse_config("config.txt")