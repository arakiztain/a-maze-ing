from icecream import ic
from typing import Callable
from enum import Enum
import time
import sys
import random


class MazeGenerator:

    COLORS = [
        "\033[91m",
        "\033[92m",
        "\033[93m",
        "\033[94m",
        "\033[95m",
        "\033[96m",
    ]

    class MOVES(Enum):
        N = 'N'
        E = 'E'
        S = 'S'
        W = 'W'

    OPPOSITE: dict[MOVES, MOVES] = {
        MOVES.N: MOVES.S,
        MOVES.S: MOVES.N,
        MOVES.E: MOVES.W,
        MOVES.W: MOVES.E,
    }

    def __init__(self, config):
        self.width = config.width
        self.height = config.height
        self.entry = config.entry
        self.exit = config.exit
        self.perfect = config.perfect
        self.seed = getattr(config, "seed", None)

        self.maze = {(x, y): [1, 1, 1, 1]
                     for y in range(self.height)
                     for x in range(self.width)}

        self.generate()

    def generate(self):
        if self.seed is not None:
            random.seed(self.seed)

        stack = [self.entry]
        visited = {self.entry}

        DIRS = [("N", (0, -1)), ("E", (1, 0)), ("S", (0, 1)), ("W", (-1, 0))]
        OPPOSITE = {"N": "S", "S": "N", "E": "W", "W": "E"}
        INDEX = {"N": 0, "E": 1, "S": 2, "W": 3}

        while stack:
            x, y = stack[-1]
            neighbors = [
                (d, (x + dx, y + dy))
                for d, (dx, dy) in DIRS
                if 0 <= x + dx < self.width and 0 <= y + dy < self.height
                and (x + dx, y + dy) not in visited
            ]

            if neighbors:
                d, (nx, ny) = random.choice(neighbors)
                self.maze[(x, y)][INDEX[d]] = 0
                self.maze[(nx, ny)][INDEX[OPPOSITE[d]]] = 0
                visited.add((nx, ny))
                stack.append((nx, ny))
            else:
                stack.pop()

    def move(self, coordinates: tuple[int, int],
             move: MOVES) -> tuple[int, int]:
        MOVE: dict[str, Callable] = {
            self.MOVES.N: lambda x, y: (x, y - 1),
            self.MOVES.E: lambda x, y: (x + 1, y),
            self.MOVES.S: lambda x, y: (x, y + 1),
            self.MOVES.W: lambda x, y: (x - 1, y)
        }
        x, y = coordinates
        return MOVE[move](x, y)

    def valid_move(self, coordinates: tuple, move: MOVES) -> bool:
        VALID_MOVES: dict[str, Callable] = {
            self.MOVES.N: lambda x, y: self.maze[(x, y)][0] == 0,
            self.MOVES.E: lambda x, y: self.maze[(x, y)][1] == 0,
            self.MOVES.S: lambda x, y: self.maze[(x, y)][2] == 0,
            self.MOVES.W: lambda x, y: self.maze[(x, y)][3] == 0,
        }
        x, y = coordinates
        return VALID_MOVES[move](x, y)

    def solve_maze(self, curr_coor: tuple[int, int],
                   exit: tuple[int, int], move: MOVES | None = None,
                   movs: tuple[str, ...] = (),
                   path: tuple[tuple, ...] = ()) -> bool:

        if curr_coor == exit:
            return True
        if move is not None:
            if not self.valid_move(curr_coor, move):
                return False
            curr_coor = self.move(curr_coor, move)
            if curr_coor in path or curr_coor not in self.maze:
                return False

        moves: list[MazeGenerator.MOVES] = list(self.MOVES)

        return any(
            self.solve_maze(curr_coor, exit, move, movs + (move,),
                            path + (curr_coor,))
            for move in moves
        )

    def render_maze(self, maze: dict[tuple, list[int]], width: int,
                    height: int) -> None:
        maze_chars: dict = {
            (0, 0, 0, 0): ' ',
            (0, 0, 1, 1): '┐',
            (0, 1, 1, 0): '┌',
            (1, 1, 0, 0): '└',
            (1, 0, 0, 1): '┘',
            (0, 1, 1, 1): '┬',
            (1, 1, 0, 1): '┴',
            (1, 0, 1, 0): '│',
            (0, 1, 0, 1): '─',
            (1, 0, 1, 1): '┤',
            (1, 1, 1, 0): '├',
            (1, 1, 1, 1): '┼'
        }


        def print_maze(maze: list[str], first_frame: bool) -> None:
            for row in maze:
                time.sleep(0.0002)
                sys.stdout.write("".join(row) + '\n')
            sys.stdout.flush()

        parse_coor: dict[tuple[int, int], list[int]] = {}
        for y in range(height):
            for x in range(width):
                N = self.maze[x, y - 1][3] if y - 1 >= 0 else 0
                E = self.maze[x, y][0]
                S = self.maze[x, y][3]
                W = self.maze[x - 1, y][0] if x - 1 >= 0 else 0
                parse_coor[x, y] = (N, E, S, W)

        for x in range(width):
            N = maze[x, height - 1][3]
            E = 1
            S = 0
            W = 1 if x != 0 else 0
            parse_coor[x, height] = (N, E, S, W)

        for y in range(height):
            N = 1 if y != 0 else 0
            E = 0
            S = 1
            W = maze[width - 1, y][0]
            parse_coor[width, y] = (N, E, S, W)

        parse_coor[width, height] = (1, 0, 0, 1)

        parsed_coor = {}
        for coor in parse_coor:
            key = parse_coor[coor]
            parsed_coor[coor] = maze_chars[key] if key in maze_chars else ' '

        maze_grid: list[str] = [[' '] * ((width + 1) + (width * 3))
                                for _ in range(height * 2 + 1)]

        first_frame = True
        for coor in parsed_coor:
            x, y = coor
            x_ = x * 4
            y_ = y * 2
            maze_grid[y * 2][x * 4] = parsed_coor[coor]

            if coor in maze:
                if maze[x, y][0] == 1:
                    for w in range(1, 4):
                        maze_grid[y_][x_ + w] = '─'
                if maze[x, y][1] == 1:
                    maze_grid[y_ + 1][x_ + 4] = '│'
                if maze[x, y][2] == 1:
                    for w in range(1, 4):
                        maze_grid[y_ + 2][x_ + w] = '─'
                if maze[x, y][3] == 1:
                    maze_grid[y_ + 1][x_] = '│'
            print_maze(maze_grid, first_frame)
            first_frame = False
