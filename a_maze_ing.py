import sys
from icecream import ic
from typing import Callable, Any
from maze.config_parser import parse_config
from mazegen.MazeGenerator import MazeGenerator
# from maze.render_mazeMLX import main as maze_render

def cli_loop(maze_gen: MazeGenerator, config, config_path: str, user_set_seed: bool) -> None:
    print()
    print("=== A-Maze-ing ===")
    while True:
        seed_status = f"seed: {maze_gen.seed} (fixed)" if user_set_seed else f"seed: {maze_gen.seed} (random)"
        print(f"1. Re-generate a new maze {seed_status}")
        print("2. Show/hide path from entry to exit")
        print("3. Rotate maze colors")
        print("4. Run mlx display")
        print("5. Exit")

        choice = input("Choice? (1-5): ").strip()

        match choice:
            case "1":
                config = parse_config(config_path)
                maze_gen.__init__()
                maze_gen.generate(
                    width=config.width,
                    height=config.height,
                    unique_sol=not config.perfect,
                    seed=config.seed,
                    entry=config.entry,
                    exit_coor=config.exit,
                    output_file=config.output_file,
                )
            case "2":
                maze_gen.first_frame = True
                maze_gen.show_hide_solution()
            case "3":
                maze_gen.first_frame = True
                maze_gen.change_walls_colour()
            case "4":
                from maze.render_mazeMLX import main as maze_render
                maze_render()
            case "5":
                print("Bye!")
                sys.exit(0)
            case _:
                print("Invalid option.")

    
def main() -> None:
    err_message: str = "No config txt file provided"
    try:
        if (len(sys.argv) != 2 or
                not isinstance(sys.argv[1], str) or
                not sys.argv[1].lower().endswith(".txt")):
            raise Exception(err_message)

        r = parse_config(sys.argv[1])
        user_set_seed = r.user_set_seed
        # vars convert a NameSpace to a dict
        # generator.main(**vars(r))
        # maze_render()
        maze_gen = MazeGenerator()
        maze_gen.generate(
			width=r.width,
			height=r.height,
			unique_sol=not r.perfect,
			seed=r.seed,
			entry=r.entry,
			exit_coor=r.exit,
            output_file=r.output_file,
		)

        cli_loop(maze_gen, r, sys.argv[1], user_set_seed)

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
