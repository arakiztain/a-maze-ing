import sys
import random
from maze.config_parser import parse_config
from mazegen.MazeGenerator import MazeGenerator


def clear():
    sys.stdout.write("\033[2J\033[H")
    sys.stdout.flush()


def run_once(config):
    maze = MazeGenerator(config)
    solved = maze.solve_maze(config.entry, config.exit)

    print()
    print("Solved:", solved)
    maze.render_maze(maze.maze, config.width, config.height)

def run_multiple(config, times=5):
    for i in range(times):
        seed = random.randint(0, 100_000)
        config.seed = seed
        random.seed(seed)

        maze = MazeGenerator(config)
        solved = maze.solve_maze(config.entry, config.exit)

        print()
        print(f"Run {i+1}")
        print("Seed:", seed)
        print("Solved:", solved)

        maze.render_maze(maze.maze, config.width, config.height)

def main():
    clear()
    if len(sys.argv) != 2 or not sys.argv[1].lower().endswith(".txt"):
        print("Usage: python a_maze_ing.py config.txt")
        sys.exit(1)

    config_file = f"config/{sys.argv[1]}"

    try:
        config = parse_config(config_file)
    except Exception as e:
        print(f"Error loading config: {e}")
        sys.exit(1)

    while True:
        print()
        print("=== A-MAZE-ING CLI ===")
        print("1) Run once")
        print("2) Run multiple seeds")
        print("3) Exit")

        choice = input("> ").strip()

        if choice == "1":
            run_once(config)

        elif choice == "2":
            try:
                times = int(input("How many runs? ").strip())
            except ValueError:
                times = 5
            run_multiple(config, times)

        elif choice == "3":
            print("Bye!")
            break

        else:
            print("Invalid option. Try again.")

if __name__ == "__main__":
    main()