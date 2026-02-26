import random
from collections import deque
from typing import Tuple, List


def generate_perfect_maze(width: int, height: int, entry: int) -> List:
    maze = [[0b1111 for _ in range(width)] for _ in range(height)]
    visited = [[False]*width for _ in range(height)]

    def neighbors(x: int, y: int) -> None:
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

    def carve(x: int, y: int) -> None:
        visited[y][x] = True
        for nx, ny, wall, opp in neighbors(x, y):
            if not visited[ny][nx]:
                maze[y][x] &= ~wall
                maze[ny][nx] &= ~opp
                carve(nx, ny)

    carve(entry[0], entry[1])
    return maze


# Algortihm
def bfs_path(
        maze: List,
        entry: Tuple[float, float],
        exit: Tuple[float, float]
        ) -> str:
    width, height = len(maze[0]), len(maze)
    q = deque()
    q.append((entry, []))
    visited = [[False]*width for _ in range(height)]
    visited[entry[1]][entry[0]] = True

    dirs = [(0, -1, 'N', 1), (1, 0, 'E', 2), (0, 1, 'S', 4), (-1, 0, 'W', 8)]
    while q:
        (x, y), path = q.popleft()
        if (x, y) == exit:
            return "".join(path)
        for dx, dy, letter, wall in dirs:
            nx, ny = x+dx, y+dy
            if 0 <= nx < width and 0 <= ny < height:
                if not (maze[y][x] & wall) and not visited[ny][nx]:
                    visited[ny][nx] = True
                    q.append(((nx, ny), path+[letter]))
    return ""


def save_maze(
        maze: List,
        entry: Tuple[float, float],
        exit: Tuple[float, float],
        path: str,
        out_file: str
        ) -> None:
    with open(out_file, "w") as f:
        for row in maze:
            f.write("".join(format(c, 'X') for c in row) + "\n")
        f.write("\n")
        f.write(f"{entry[0]}, {entry[1]}\n")
        f.write(f"{exit[0]}, {exit[1]}\n")
        f.write(path + "\n")


def main(
        width: int,
        height: int,
        entry: Tuple[float, float],
        exit: Tuple[float, float],
        output_file: str,
        perfect: bool
        ) -> None:

    maze = generate_perfect_maze(width, height, entry)

    maze[entry[1]][entry[0]] &= 0b1110
    maze[exit[1]][exit[0]] &= 0b1110

    path = bfs_path(maze, entry, exit)

    save_maze(maze, entry, exit, path, output_file)
    print("Maze generated at:", output_file)


if __name__ == "__main__":
    main()
