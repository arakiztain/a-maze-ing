from icecream import ic
from typing import Callable
from enum import Enum
import random
import time
import sys


class MazeGenerator:
    def __init__(self):
        self.last_move = None
        self.base_weight = 1
        self.boost = 3
        self.entry = None
        self.exit = None
        self.curr_coor = self.entry
        self.width = None
        self.height = None
        self.unique_sol = None
        self.path: list[tuple[int, int]] = []
        self.no_exit = []
        self.exit_found: bool = False
        self.perfect: bool = False
        self.solution_path: tuple[tuple[int, int]] = ()
        self.solution_movs: tuple[MazeGenerator.MOVES] = ()

    maze: dict[tuple, list[int]] = {}

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

    def maze_generation(self, width: int, height: int, unique_sol: bool,
                        entry: tuple, exit: tuple):

        self.entry = entry
        self.exit = exit
        self.width = width
        self.height = height
        self.unique_sol = unique_sol
        self.path.append(entry)

        def add_walls(coor: tuple, mov: MazeGenerator.MOVES | None) -> None:
            if coor not in self.maze:
                walls: list[int | None] = [None, None, None, None]
                x, y = coor
                if (x, y - 1) in self.maze:
                    walls[0] = self.maze[x, y - 1][2]
                if (x + 1, y) in self.maze:
                    walls[1] = self.maze[x + 1, y][3]
                if (x, y + 1) in self.maze:
                    walls[2] = self.maze[x, y + 1][0]
                if (x - 1, y) in self.maze:
                    walls[3] = self.maze[x - 1, y][1]
            else:
                walls = self.maze[coor]

            if mov:
                match mov:
                    case self.MOVES.N:
                        walls[0] = 0
                    case self.MOVES.E:
                        walls[1] = 0
                    case self.MOVES.S:
                        walls[2] = 0
                    case self.MOVES.W:
                        walls[3] = 0

            for i, wall in enumerate(walls):
                if wall is None:
                    walls[i] = 1

            self.maze[coor] = walls

        def valid_celd(coor: tuple) -> bool:
            return (0 <= coor[0] <= self.width - 1 and
                    0 <= coor[1] <= self.height - 1)

        def valid_move(curr, mov, path):
            next_coor = self.move(curr, mov)
            return (next_coor not in path and valid_celd(next_coor)
                    and next_coor not in self.no_exit)

        def path_generation(curr: tuple[int, int],
                            solution: tuple[MazeGenerator.MOVES] = (),
                            path: tuple[tuple[int, int], ...]
                            = (entry,)) -> None:

            if curr == self.exit:
                add_walls(curr, None)
                self.exit_found = True
                self.solution_path = path
                self.solution_movs = solution
                return

            moves: list = list(self.MOVES)
            random.shuffle(moves)

            no_moves = True
            for mov in moves:
                if valid_move(curr, mov, self.path):
                    no_moves = False
                    add_walls(curr, mov)
                    next_coor = self.move(curr, mov)
                    self.path.append(next_coor)
                    path_generation(next_coor, solution + (mov,),
                                    path + (next_coor,))

            if no_moves:
                add_walls(curr, None)
                self.no_exit.append(curr)

            return

        path_generation(entry)

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

        red_sqr = "\033[31m⬛\033[0m"
        maze_grid[(self.entry[1] * 2) + 1][(self.entry[0] * 4) + 2] = 'E'
        maze_grid[(self.exit[1] * 2) + 1][(self.exit[0] * 4) + 2] = 'X'

        first_frame = True
        #ic(parsed_coor)
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

maze_gen.maze_generation(16, 16, True, (0, 0), (12, 12))
maze_gen.render_maze(MazeGenerator.maze, 16, 16)
