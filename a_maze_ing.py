import sys
from icecream import ic
from typing import Callable, Any
from maze.config_parser import parse_config



if __name__ == "__main__":
    err_message: str = "No config txt file provided"
    try:
        if (len(sys.argv) != 2 or
                not isinstance(sys.argv[1], str) or
                not sys.argv[1].lower().endswith(".txt")):
            raise Exception(err_message)

        parse_config(sys.argv[1])

    except FileNotFoundError as e:
        print(e)
    except IndexError:
        print("")
    except (ValueError, TypeError) as e:
        print(e)
    except Exception as e:
        print(f"Error: {e}")
