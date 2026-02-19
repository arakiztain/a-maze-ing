import sys
from icecream import ic
from typing import Callable, Any


if __name__ == "__main__":
    err_message: str = "No config txt file provided"
    try:
        if (len(sys.argv) != 2 or
                not isinstance(sys.argv[1], str) or
                not sys.argv[1].lower().endswith(".txt")):
            raise Exception(err_message)

        with open(sys.argv[1]) as f:
            content: str = f.read()
            ic(content)
            config: dict[str, str] = {}
            for line in content.splitlines():
                if not line.startswith("#") and '=' in line:
                    key = line.split('=', 1)[0].strip()
                    val = line.split('=', 1)[1].strip()
                    config[key] = val
            ic(config)

            if not config:
                raise ValueError("Invalid config file")
            if any(k == "" or v == "" for k, v in config.items()):
                raise ValueError("Invalid config file: it contains "
                                 "empty keys or values")
            if any(not k.isupper() for k in config.keys()):
                raise ValueError("All config keys must be uppercase")

            REQUIRED: set[str] = {"WIDTH", "HEIGHT", "ENTRY", "EXIT",
                                  "OUTPUT_FILE", "PERFECT"}
            OPTIONAL: set[str] = {"SEED"}

            missing: set[str] = REQUIRED - config.keys()
            if missing:
                raise ValueError(f"Missing required config keys: {missing}")

            unknown: set = config.keys() - REQUIRED - OPTIONAL
            if unknown:
                raise ValueError(f"Unknown config keys: {unknown}")

            def cast_bool(v: Any):
                try:
                    return {"True": True, "False": False}[v]
                except KeyError:
                    raise TypeError(f"Invalid boolean value: {v}")

            CASTS: dict[str, Callable] = {
                "WIDTH": int,
                "HEIGHT": int,
                "ENTRY": lambda v: tuple(map(int, v.split(','))),
                "EXIT": lambda v: tuple(map(int, v.split(','))),
                "PERFECT": cast_bool
            }
            try:
                parsed_config: dict[str, int | str | bool] = {
                    k: CASTS.get(k, lambda x: x)(v) for k, v in config.items()}
            except TypeError:
                raise TypeError("")

            ic(parsed_config)

    except FileNotFoundError as e:
        print(e)
    except IndexError:
        print("")
    except (ValueError, TypeError) as e:
        print(e)
    except Exception as e:
        print(f"Error: {e}")
