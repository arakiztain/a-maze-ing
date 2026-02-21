from icecream import ic
from typing import Callable
from enum import Enum
import time
import sys


class MazeGenerator:
    maze: dict[tuple, list[int]] = {
        (0,0): [1,0,0,1], (1,0): [1,0,1,0], (2,0): [1,1,0,0], (3,0): [1,0,1,1], (4,0): [1,0,1,0], (5,0): [1,0,0,0], (6,0): [1,1,0,0], (7,0): [1,1,0,1],
        (0,1): [0,1,0,1], (1,1): [1,0,0,1], (2,1): [0,1,1,0], (3,1): [1,0,0,1], (4,1): [1,0,0,0], (5,1): [0,1,1,0], (6,1): [0,0,1,1], (7,1): [0,1,1,1],
        (0,2): [0,0,0,1], (1,2): [0,1,1,0], (2,2): [1,0,0,1], (3,2): [0,1,1,0], (4,2): [0,0,1,1], (5,2): [1,0,0,0], (6,2): [1,1,0,0], (7,2): [1,1,0,1],
        (0,3): [0,1,0,1], (1,3): [1,0,0,1], (2,3): [0,1,0,0], (3,3): [1,0,0,1], (4,3): [1,0,0,0], (5,3): [0,1,1,0], (6,3): [0,0,0,1], (7,3): [0,1,0,1],
        (0,4): [0,0,0,1], (1,4): [0,1,0,0], (2,4): [0,0,0,1], (3,4): [0,1,1,0], (4,4): [0,1,0,1], (5,4): [1,0,0,1], (6,4): [0,1,0,0], (7,4): [0,1,1,1],
        (0,5): [0,0,0,1], (1,5): [0,0,0,0], (2,5): [0,1,0,0], (3,5): [1,0,0,1], (4,5): [0,1,0,0], (5,5): [0,1,1,1], (6,5): [0,0,0,1], (7,5): [1,1,0,1],
        (0,6): [0,0,0,1], (1,6): [0,1,1,0], (2,6): [0,1,1,1], (3,6): [0,0,0,1], (4,6): [0,1,1,0], (5,6): [1,0,0,1], (6,6): [0,1,1,0], (7,6): [0,1,0,1],
        (0,7): [0,1,1,1], (1,7): [1,0,1,1], (2,7): [1,1,1,0], (3,7): [0,0,1,1], (4,7): [1,0,1,0], (5,7): [0,0,1,0], (6,7): [1,0,1,0], (7,7): [1,1,1,0],
    }

    maze1 = {
        (0, 0): [1, 1, 0, 1],
        (1, 0): [1, 1, 0, 1],
        (0, 1): [0, 0, 1, 1],
        (1, 1): [0, 1, 1, 0]
    }

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

    def move(self, coordinates: tuple[int, int],
             move: MOVES) -> tuple[int, int]:
        MOVE: dict[str, Callable] = {
            self.MOVES.N: lambda x, y: (x, y - 1),
            self.MOVES.E: lambda x, y: (x + 1, y),
            self.MOVES.S: lambda x, y: (x, y + 1),
            self.MOVES.W: lambda x, y: (x - 1, y)
        }
        x: int
        y: int
        x, y = coordinates
        return MOVE[move](x, y)

    def valid_move(self, coordinates: tuple, move: MOVES) -> bool:
        VALID_MOVES: dict[str, Callable] = {
            self.MOVES.N: lambda x, y: self.maze[(x, y)][0] == 0,
            self.MOVES.E: lambda x, y: self.maze[(x, y)][1] == 0,
            self.MOVES.S: lambda x, y: self.maze[(x, y)][2] == 0,
            self.MOVES.W: lambda x, y: self.maze[(x, y)][3] == 0,
        }
        x: int
        y: int
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

            curr_coor: tuple[int, int] = self.move(curr_coor, move)

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

            if not first_frame:
                sys.stdout.write("\033[F" * (len(maze)))

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
                    for w in range(1, 3 + 1):
                        maze_grid[y_][x_ + w] = '─'
                if maze[x, y][1] == 1:
                    maze_grid[y_ + 1][x_ + 4] = '│'
                if maze[x, y][2] == 1:
                    for w in range(1, 3 + 1):
                        maze_grid[y_ + 2][x_ + w] = '─'
                if maze[x, y][3] == 1:
                    maze_grid[y_ + 1][x_] = '│'
            print_maze(maze_grid, first_frame)
            first_frame = False

maze_gen = MazeGenerator()
ic(maze_gen.solve_maze((0, 0), (7, 7)))
#ic(maze_gen.solve_maze((0, 0), (1, 1)))
maze_gen.render_maze(MazeGenerator.maze, 8, 8)
#maze_gen.render_maze(MazeGenerator.maze, 2, 2)
