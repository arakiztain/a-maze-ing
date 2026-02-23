import sys
import random
from maze.config_parser import parse_config
from mazegen.MazeGenerator import MazeGenerator

def generate_maze(config):
    maze = MazeGenerator(config)
    maze = maze.generate()
    return maze

def main():
    if len(sys.argv) != 2 or not sys.argv[1].lower().endswith(".txt"):
        print("Usage: python3 a_maze_ing.py config.txt")
        sys.exit(1)

    config_file = f"config/{sys.argv[1]}"

    try:
        config = parse_config(config_file)
    except Exception as e:
        print(f"Error loading config: {e}")
        sys.exit(1)

    while True:
        print()
        print("=== A-Maze-Ing ===")
        print("1. Re-generate a new maze")
        print("2. Show/Hide path from entry to exit")
        print("3. Rotate maze colors")
        print("4. Quit")
        print("Choice? (1-4):")

        choice = input("> ").strip()

        if choice == "1":
            maze = MazeGenerator(config)
            maze.render_maze(config)
        elif choice == "2":
            ...
        elif choice == "3":
            ...
        elif choice == "4":
            print("Bye!")
            break

        else:
            print("Invalid option. Try again.")


if __name__ == "__main__":
    main()
