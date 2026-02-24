import random
from collections import deque


def read_config(path):
    config = {}
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            key, value = line.split("=")
            config[key] = value

    config["WIDTH"] = int(config["WIDTH"])
    config["HEIGHT"] = int(config["HEIGHT"])
    config["ENTRY"] = tuple(map(int, config["ENTRY"].split(",")))
    config["EXIT"] = tuple(map(int, config["EXIT"].split(",")))
    config["PERFECT"] = config["PERFECT"].lower() == "true"
    config["OUTPUT_FILE"] = config["OUTPUT_FILE"]
    return config


def generate_perfect_maze(width, height):
    maze = [[0b1111 for _ in range(width)] for _ in range(height)]
    visited = [[False]*width for _ in range(height)]

    def neighbors(x, y):
        dirs = [
            (0, -1, 1, 4),  # N
            (1, 0, 2, 8),   # E
            (0, 1, 4, 1),   # S
            (-1, 0, 8, 2)   # W
        ]
        random.shuffle(dirs)
        for dx, dy, wall, opp in dirs:
            nx, ny = x + dx, y + dy
            if 0 <= nx < width and 0 <= ny < height and not visited[ny][nx]:
                yield nx, ny, wall, opp

    def carve(x, y):
        visited[y][x] = True
        for nx, ny, wall, opp in neighbors(x, y):
            if not visited[ny][nx]:
                maze[y][x] &= ~wall
                maze[ny][nx] &= ~opp
                carve(nx, ny)

    carve(*config["ENTRY"])
    return maze

# Algortihm
def bfs_path(maze, entry, exit_):
    width, height = len(maze[0]), len(maze)
    q = deque()
    q.append((entry, []))
    visited = [[False]*width for _ in range(height)]
    visited[entry[1]][entry[0]] = True

    dirs = [(0,-1,'N',1),(1,0,'E',2),(0,1,'S',4),(-1,0,'W',8)]
    while q:
        (x,y), path = q.popleft()
        if (x,y) == exit_:
            return "".join(path)
        for dx, dy, letter, wall in dirs:
            nx, ny = x+dx, y+dy
            if 0 <= nx < width and 0 <= ny < height:
                if not (maze[y][x] & wall) and not visited[ny][nx]:
                    visited[ny][nx] = True
                    q.append(((nx,ny), path+[letter]))
    return ""


def save_maze(maze, entry, exit_, path, out_file):
    with open(out_file, "w") as f:
        for row in maze:
            f.write("".join(format(c,'X') for c in row) + "\n")
        f.write("\n")
        f.write(f"{entry[0]},{entry[1]}\n")
        f.write(f"{exit_[0]},{exit_[1]}\n")
        f.write(path + "\n")


def main():
    global config
    config = read_config("config/config.txt")

    maze = generate_perfect_maze(config["WIDTH"], config["HEIGHT"])

    entry = config["ENTRY"]
    exit_ = config["EXIT"]

    maze[entry[1]][entry[0]] &= 0b1110
    maze[exit_[1]][exit_[0]] &= 0b1110

    path = bfs_path(maze, entry, exit_)

    save_maze(maze, entry, exit_, path, config["OUTPUT_FILE"])
    print("Maze generado en:", config["OUTPUT_FILE"])

if __name__ == "__main__":
    main()
