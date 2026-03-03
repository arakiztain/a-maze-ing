from pydantic.dataclasses import dataclass as pydantic_dataclass
from pydantic import Field, model_validator
from typing import Tuple
import random


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
    seed: int | None = Field(default=None)
    user_set_seed: bool = Field(default=False)

    @model_validator(mode="after")
    def entry_validator(self):
        entry_x, entry_y = self.entry
        exit_x, exit_y = self.exit

        errors = []

        if (entry_x >= self.width or entry_y >= self.height):
            errors.append(
                f"Entry {self.entry} out of the limits:"
                f" ({self.width}, {self.height})"
                )
        if (exit_x >= self.width or exit_y >= self.height):
            errors.append(
                f"Exit {self.exit} out of the limits:"
                f" ({self.width}, {self.height})"
                )

        if errors:
            raise ConfigError("; ".join(errors))
        

        if self.seed is None:
            self.seed = random.randint(0, 999999)
        else:
            self.user_set_seed = True

        return self


def parse_config(path: str) -> MazeConfig:
    try:
        with open(path, "r") as f:
            data = f.read().splitlines()
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return None

    config_dict = {}
    for line in data:
        if not line.strip() or line.startswith("#"):
            continue
        key, value = line.split("=", 1)
        key = key.strip().upper()
        value = value.strip()

        if key in ["WIDTH", "HEIGHT"]:
            value = int(value)
        elif key in ["ENTRY", "EXIT"]:
            value = tuple(map(int, value.split(",")))
        elif key == "PERFECT":
            value = value.lower() == "true"
        elif key == "SEED":
            value = (
                int(value) if value.strip() and
                value.lower() != "none" else None
                )
        config_dict[key.lower()] = value

    return MazeConfig(**config_dict)
