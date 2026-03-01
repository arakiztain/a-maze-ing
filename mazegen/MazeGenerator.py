from icecream import ic
from typing import Callable
from enum import Enum
import random
import sys
import time


class MazeGenerator:
    def __init__(self):
        self.entry = None
        self.exit = None
        self.width = None
        self.height = None
        self.unique_sol = None
        self.path: list[tuple[int, int]] = []
        self.no_exit = []
        self.perfect: bool = False
        self.solution_path: tuple[tuple[int, int]] = ()
        self.maze: dict[tuple, list[int]] = {}
        self.solutions: set[tuple] = set()
        self.exit_found = False
        self.isolated = []
        self.shortest_sol: tuple[tuple, tuple] = None
        self.maze_grid = None
        self.parsed_coor = {}
        self.first_frame = True
        self.show_animation: bool = True
        self.solution_hidden = True

    class MOVES(Enum):
        N = 'N'
        E = 'E'
        S = 'S'
        W = 'W'

    maze_chars: dict[tuple, str] = {
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
            if movs[:-1] not in self.solutions:
                self.solutions.add((movs[:-1], path))
            return
        if move is not None:
            if not self.valid_move(curr_coor, move):
                return False

            curr_coor: tuple[int, int] = self.move(curr_coor, move)

            if curr_coor in path or curr_coor not in self.maze:
                return False

        for move in list(self.MOVES):
            self.solve_maze(curr_coor, exit, move, movs + (move,),
                            path + (curr_coor,))
        return

    def maze_generation(self):
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
            if self.show_animation:
                self.animate()

        def remove_walls(coor: tuple, mov: MazeGenerator.MOVES | None):
            x, y = coor
            match mov:
                case self.MOVES.N:
                    self.maze[coor][0] = 0
                    self.maze[x, y - 1][2] = 0
                case self.MOVES.E:
                    self.maze[coor][1] = 0
                    self.maze[x + 1, y][3] = 0
                case self.MOVES.S:
                    self.maze[coor][2] = 0
                    self.maze[x, y + 1][0] = 0
                case self.MOVES.W:
                    self.maze[coor][3] = 0
                    self.maze[x - 1, y][1] = 0

        def create_alt_path():
            celds = list(self.solution_path)
            random.shuffle(celds)
            count = 0
            for celd in celds:
                for mov in list(self.MOVES):
                    if valid_move(celd, mov, [], True):
                        remove_walls(celd, mov)
                        if self.show_animation:
                            self.animate()
                        count += 1
                        break
                if count == 2:
                    break

        def valid_celd(coor: tuple) -> bool:
            return (0 <= coor[0] <= self.width - 1 and
                    0 <= coor[1] <= self.height - 1)

        def valid_move(curr, mov, path, alt_path: bool = False):
            next_coor = self.move(curr, mov)

            alt_path_valid = (next_coor not in self.solution_path
                              if alt_path else True)
            return (next_coor not in path and valid_celd(next_coor)
                    and next_coor not in self.no_exit and alt_path_valid and
                    next_coor not in self.isolated)

        def path_generation(curr: tuple[int, int],
                            solution: tuple[MazeGenerator.MOVES] = (),
                            path: tuple[tuple[int, int], ...]
                            = (self.entry,)) -> None:

            if curr == self.exit:
                add_walls(curr, None)
                self.solution_path = path
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

        def shortest_sol() -> None:
            if not self.solutions:
                return
            self.shortest_sol = min(self.solutions,
                                    key=lambda sol: len(sol[0]))

        path_generation(self.entry)
        if not self.unique_sol:
            create_alt_path()
        self.solve_maze(self.entry, self.exit)
        shortest_sol()

    def add_42_pattern(self):
        pattern_width: int = 7
        pattern_height: int = 5
        start_x = (self.width - pattern_width) // 2
        start_y = (self.height - pattern_height) // 2

        def isolate_celds(coor):
            if coor != self.entry and coor != self.exit:
                self.maze[coor] = [1, 1, 1, 1]
                self.isolated.append(coor)

        isolate_celds((start_x, start_y))
        isolate_celds((start_x, start_y + 1))
        isolate_celds((start_x, start_y + 2))
        isolate_celds((start_x + 1, start_y + 2))
        isolate_celds((start_x + 2, start_y + 1))
        isolate_celds((start_x + 2, start_y + 2))
        isolate_celds((start_x + 2, start_y + 3))
        isolate_celds((start_x + 2, start_y + 4))
        isolate_celds((start_x + 4, start_y))
        isolate_celds((start_x + 5, start_y))
        isolate_celds((start_x + 6, start_y))
        isolate_celds((start_x + 6, start_y + 1))
        isolate_celds((start_x + 6, start_y + 2))
        isolate_celds((start_x + 5, start_y + 2))
        isolate_celds((start_x + 4, start_y + 2))
        isolate_celds((start_x + 4, start_y + 3))
        isolate_celds((start_x + 4, start_y + 4))
        isolate_celds((start_x + 5, start_y + 4))
        isolate_celds((start_x + 6, start_y + 4))

        self.maze[start_x + 1, start_y + 1] = [0, 1, 1, 1]
        self.maze[start_x + 5, start_y + 1] = [1, 1, 1, 0]
        self.maze[start_x + 5, start_y + 3] = [1, 0, 1, 1]

    def create_grid(self):
        self.maze_grid = [[' '] * ((self.width + 1) + (self.width * 3))
                          for _ in range(self.height * 2 + 1)]

        self.maze_grid[(self.entry[1] * 2) + 1][(self.entry[0] * 4) + 2] = 'E'
        self.maze_grid[(self.exit[1] * 2) + 1][(self.exit[0] * 4) + 2] = 'X'

    def show_hide_solution(self) -> None:
        maze_grid = self.maze_grid

        def add_arrows(path, movs, remove: bool = False) -> None:
            for coor, mov in zip(path, movs):
                match mov:
                    case self.MOVES.N:
                        arrow = '↑'
                        x = (coor[0] * 4) + 2
                        y = (coor[1] * 2)
                    case self.MOVES.E:
                        arrow = '→'
                        x = (coor[0] * 4) + 4
                        y = (coor[1] * 2) + 1
                    case self.MOVES.S:
                        arrow = '↓'
                        x = (coor[0] * 4) + 2
                        y = (coor[1] * 2) + 2
                    case self.MOVES.W:
                        arrow = '←'
                        x = (coor[0] * 4)
                        y = (coor[1] * 2) + 1

                maze_grid[y][x] = arrow if not remove else ' '
                self.print_maze(maze_grid, self.first_frame)
                time.sleep(0.01)

        def add_char(char: str, coor: tuple[int, int],
                     maze_grid: dict) -> None:
            maze_grid[(coor[1] * 2) + 1][(coor[0] * 4) + 2] = char

        if self.solution_hidden:
            self.solution_hidden = False
            self.first_frame = False
            for coor in self.shortest_sol[1]:
                if coor != self.entry and coor != self.exit:
                    add_char('•', coor, maze_grid)
                    self.print_maze(maze_grid, self.first_frame)
                    time.sleep(0.01)

            add_arrows(self.shortest_sol[1], self.shortest_sol[0])

            # for coor in set(self.maze).difference(set(self.shortest_sol[1])):
            #     if (coor != self.entry and coor != self.exit
            #             and coor not in self.isolated):
            #         add_char('◦', coor, maze_grid)
        else:
            self.solution_hidden = True
            for coor in self.shortest_sol[1]:
                if coor != self.entry and coor != self.exit:
                    add_char(' ', coor, maze_grid)
            add_arrows(self.shortest_sol[1], self.shortest_sol[0], True)
            self.print_maze(maze_grid, self.first_frame)

    def parse_vertices(self):
        maze: dict = self.maze
        width: int = self.width
        height: int = self.height
        vertices: dict[tuple[int, int], list[int]] = {}
        for y in range(height):
            for x in range(width):
                N = maze[x, y - 1][3] if y - 1 >= 0 else 0
                E = maze[x, y][0]
                S = maze[x, y][3]
                W = maze[x - 1, y][0] if x - 1 >= 0 else 0

                vertices[x, y] = (N, E, S, W)

        for x in range(width):
            N = maze[x, height - 1][3]
            E = 1
            S = 0
            W = 1 if x != 0 else 0

            vertices[x, height] = (N, E, S, W)

        for y in range(height):
            N = 1 if y != 0 else 0
            E = 0
            S = 1
            W = maze[width - 1, y][0]

            vertices[width, y] = (N, E, S, W)

        vertices[width, height] = (1, 0, 0, 1)
        parsed_coor = {}
        for coor in vertices:
            key = vertices[coor]
            parsed_coor[coor] = (self.maze_chars[key]
                                 if key in self.maze_chars else ' ')
        self.parsed_coor = parsed_coor
        return parsed_coor

    def render_maze(self):
        maze_grid = self.maze_grid
        for coor in self.parse_vertices():
            x, y = coor
            x_ = x * 4
            y_ = y * 2

            maze_grid[y * 2][x * 4] = self.parsed_coor[coor]

            if coor in self.maze:
                if self.maze[x, y][0] == 1:
                    for w in range(1, 3 + 1):
                        maze_grid[y_][x_ + w] = '─'
                if self.maze[x, y][1] == 1:
                    maze_grid[y_ + 1][x_ + 4] = '│'
                if self.maze[x, y][2] == 1:
                    for w in range(1, 3 + 1):
                        maze_grid[y_ + 2][x_ + w] = '─'
                if self.maze[x, y][3] == 1:
                    maze_grid[y_ + 1][x_] = '│'
        self.print_maze(maze_grid, self.first_frame)

    def animate(self):
        maze_grid = self.maze_grid
        coords = self.maze

        for coor in coords:
            x, y = coor
            x_ = x * 4
            y_ = y * 2

            if self.solutions:
                maze_grid[y * 2][x * 4] = self.parsed_coor[coor]

            if coor in self.maze:
                if self.maze[x, y][0] == 1:
                    for w in range(1, 3 + 1):
                        maze_grid[y_][x_ + w] = '─'
                else:
                    for w in range(1, 3 + 1):
                        maze_grid[y_][x_ + w] = ' '
                if self.maze[x, y][1] == 1:
                    maze_grid[y_ + 1][x_ + 4] = '│'
                else:
                    maze_grid[y_ + 1][x_ + 4] = ' '
                if self.maze[x, y][2] == 1:
                    for w in range(1, 3 + 1):
                        maze_grid[y_ + 2][x_ + w] = '─'
                else:
                    for w in range(1, 3 + 1):
                        maze_grid[y_ + 2][x_ + w] = ' '
                if self.maze[x, y][3] == 1:
                    maze_grid[y_ + 1][x_] = '│'
                else:
                    maze_grid[y_ + 1][x_] = ' '
            self.print_maze(maze_grid, self.first_frame)
            if self.first_frame:
                self.first_frame = False

    def print_maze(self, maze: list, first_frame: bool) -> None:

        if not first_frame:
            sys.stdout.write("\033[F" * (len(maze)))

        for row in maze:
            sys.stdout.write("".join(row) + '\n')

        sys.stdout.flush()

    def generate(self, width: int, height: int, unique_sol: bool,
                 entry: tuple, exit: tuple, show_animation: bool = False):
        # Add this to a setter?
        self.entry = entry
        self.exit = exit
        self.width = width
        self.height = height
        self.unique_sol = unique_sol
        self.path.append(entry)
        self.show_animation = show_animation

        if self.width >= 8 and self.height >= 6:
            self.add_42_pattern()
        self.create_grid()
        self.maze_generation()
        self.render_maze()
        time.sleep(3)
        self.show_hide_solution()
        time.sleep(3)
        self.show_hide_solution()

        # Restore to default the instance attributes once finished to be reusable


maze_gen = MazeGenerator()
maze_gen.generate(12, 12, False, (0, 0), (7, 7), True)
