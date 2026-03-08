import sys
from maze.config_parser import parse_config, MazeConfig
from mazegen.MazeGenerator import MazeGenerator
import os


def cli_loop(
    maze_gen: MazeGenerator,
    config: MazeConfig,
    config_path: str,
    user_set_seed: bool
) -> None:
    """Run the CLI loop for the maze generator.

    Args:
        maze_gen: The maze generator instance.
        config: The parsed maze configuration.
        config_path: Path to the configuration file.
        user_set_seed: Whether the user provided a seed.
    """
    print()
    print("=== A-Maze-ing ===")
    while True:
        seed_status = (
            f"seed: {maze_gen.seed} (fixed)" if user_set_seed else
            f"seed: {maze_gen.seed} (random)"
        )
        print(f"1. Re-generate a new maze {seed_status}")
        print("2. Show/hide path from entry to exit")
        print("3. Rotate maze colors")
        print("4. Run mlx display")
        print("5. Exit")

        choice: str = input("Choice? (1-5): ").strip()

        match choice:
            case "1":
                config = parse_config(config_path)
                maze_gen = MazeGenerator()
                assert config.seed is not None
                maze_gen.generate(
                    width=config.width,
                    height=config.height,
                    unique_sol=config.perfect,
                    seed=config.seed,
                    entry=config.entry,
                    exit_coor=config.exit,
                    output_file=config.output_file,
                    show_animation=config.animation or False
                )
            case "2":
                maze_gen.first_frame = True
                maze_gen.show_hide_solution()
            case "3":
                maze_gen.first_frame = True
                maze_gen.change_walls_colour()
            case "4":
                os.system("python3 maze/render_mazeMLX.py &")
                print("\n Generating maze with mlx...")
                input("\nPress enter to return to menu...")
            case "5":
                print("Bye!")
                sys.exit(0)
            case _:
                print("Invalid option.\n")


def main() -> None:
    """Entry point for the A-Maze-ing program.

    Parses the config file, generates the maze and starts the CLI loop.
    """
    err_message: str = "No config txt file provided"
    try:
        if (len(sys.argv) != 2 or
                not isinstance(sys.argv[1], str) or
                not sys.argv[1].lower().endswith(".txt")):
            raise Exception(err_message)

        r: MazeConfig = parse_config(sys.argv[1])
        user_set_seed: bool = r.user_set_seed
        maze_gen: MazeGenerator = MazeGenerator()
        maze_gen.no_print_msg = ("\nThe maze is too large "
                                 "to render in the terminal. "
                                 "Use the MLX library "
                                 "instead (press 4), "
                                 "or resize the window.\n\n")
        assert r.seed is not None
        maze_gen.generate(
            width=r.width,
            height=r.height,
            unique_sol=r.perfect,
            seed=r.seed,
            entry=r.entry,
            exit_coor=r.exit,
            output_file=r.output_file,
            show_animation=r.animation or False
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
