import sys
from icecream import ic
from typing import Callable, Any
from maze.config_parser import parse_config
import maze.generator as generator
import maze.render_mazeMLX as maze_render


def main() -> None:
    err_message: str = "No config txt file provided"
    try:
        if (len(sys.argv) != 2 or
                not isinstance(sys.argv[1], str) or
                not sys.argv[1].lower().endswith(".txt")):
            raise Exception(err_message)

        r = parse_config(sys.argv[1])
        # vars convert a NameSpace to a dict
        generator.main(**vars(r))
        maze_render.main()

    except FileNotFoundError as e:
        print(e)
    except IndexError:
        print("")
    except (ValueError, TypeError) as e:
        print(e)
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
