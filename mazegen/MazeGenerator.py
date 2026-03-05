from __future__ import annotations
from typing import Iterator, TypeAlias, Iterable
from enum import Enum
import random
import sys
import time
from itertools import cycle

Coor: TypeAlias = tuple[int, int]
Solution: TypeAlias = tuple[
    tuple["MazeGenerator.Moves", ...],
    tuple[Coor, ...]]
Solutions: TypeAlias = set[Solution]
MazeGrid: TypeAlias = list[list[str]]
Maze: TypeAlias = dict[Coor, list[int]]


class MazeGenerator:
    entry: Coor
    exit_coor: Coor
    width: int
    height: int
    unique_sol: bool
    path: list[Coor]
    no_exit: list[Coor]
    solution_path: tuple[Coor, ...]
    maze: Maze
    solutions: Solutions
    isolated: list[Coor]
    shortest_sol: Solution
    maze_grid: MazeGrid
    parsed_coor: dict[Coor, str]
    first_frame: bool
    show_animation: bool
    solution_hidden: bool
    colour: str
    output: str
    seed: int

    class Moves(Enum):
        N = 'N'
        E = 'E'
        S = 'S'
        W = 'W'

    COLOURS: tuple[str, ...] = (
        "\033[91m",
        "\033[92m",
        "\033[93m",
        "\033[94m",
        "\033[95m",
        "\033[96m",
    )
    RESET: str = "\033[0m"

    colour_iter: Iterator = cycle(COLOURS)

    MAZE_CHARS: dict[tuple[int, int, int, int], str] = {
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

    def move(self, coordinates: Coor,
             move: Moves) -> Coor:
        deltas: dict[MazeGenerator.Moves, tuple] = {
            self.Moves.N: (0, -1),
            self.Moves.E: (1, 0),
            self.Moves.S: (0, 1),
            self.Moves.W: (-1, 0)
        }
        x: int
        y: int
        dx: int
        dy: int

        dx, dy = deltas[move]
        x, y = coordinates
        return x + dx, y + dy

    def valid_move(self, coordinates: tuple, move: Moves) -> bool:
        move_index: dict[MazeGenerator.Moves, int] = {
            self.Moves.N: 0,
            self.Moves.E: 1,
            self.Moves.S: 2,
            self.Moves.W: 3
        }

        x: int
        y: int
        x, y = coordinates
        return self.maze[x, y][move_index[move]] == 0

    def solve_maze(self, curr_coor: Coor,
                   exit_coor: Coor, move: Moves | None = None,
                   movs: tuple[Moves, ...] = (),
                   path: tuple[Coor, ...] = ()) -> None:

        if curr_coor == exit_coor:
            if movs[:-1] not in self.solutions:
                self.solutions.add((movs[:-1], path))
            return
        if move is not None:
            if not self.valid_move(curr_coor, move):
                return

            curr_coor = self.move(curr_coor, move)

            if curr_coor in path or curr_coor not in self.maze:
                return

        for move in list(self.Moves):
            self.solve_maze(curr_coor, exit_coor, move, movs + (move,),
                            path + (curr_coor,))
        return

    def maze_generation(self) -> None:
        def add_walls(coor: Coor, mov: MazeGenerator.Moves | None) -> None:
            if coor not in self.maze:
                walls: list[int] = [-1] * 4
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
                    case self.Moves.N:
                        walls[0] = 0
                    case self.Moves.E:
                        walls[1] = 0
                    case self.Moves.S:
                        walls[2] = 0
                    case self.Moves.W:
                        walls[3] = 0

            for i, wall in enumerate(walls):
                if wall == -1:
                    walls[i] = 1

            self.maze[coor] = walls
            if self.show_animation:
                self.animate()

        def remove_walls(coor: Coor, mov: MazeGenerator.Moves | None) -> None:
            x: int
            y: int
            x, y = coor
            match mov:
                case self.Moves.N:
                    self.maze[coor][0] = 0
                    self.maze[x, y - 1][2] = 0
                case self.Moves.E:
                    self.maze[coor][1] = 0
                    self.maze[x + 1, y][3] = 0
                case self.Moves.S:
                    self.maze[coor][2] = 0
                    self.maze[x, y + 1][0] = 0
                case self.Moves.W:
                    self.maze[coor][3] = 0
                    self.maze[x - 1, y][1] = 0

        def create_alt_path() -> None:
            celds = list(self.solution_path)
            random.shuffle(celds)
            count = 0
            for celd in celds:
                for mov in list(self.Moves):
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

        def path_generation(curr: Coor,
                            solution: tuple[MazeGenerator.Moves, ...] = (),
                            path: tuple[Coor, ...]
                            = (self.entry,)) -> None:

            if curr == self.exit_coor:
                add_walls(curr, None)
                self.solution_path = path
                return

            moves: list[MazeGenerator.Moves] = list(self.Moves)
            random.shuffle(moves)

            no_moves: bool = True
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

        path_generation(self.entry)
        if self.unique_sol:
            create_alt_path()

    def shortest_solution(self) -> None:
        if not self.solutions:
            return
        self.shortest_sol = min(self.solutions,
                                key=lambda sol: len(sol[0]))

    def add_42_pattern(self) -> None:
        pattern_width: int = 7
        pattern_height: int = 5
        start_x: int = (self.width - pattern_width) // 2
        start_y: int = (self.height - pattern_height) // 2

        def isolate_celds(coor):
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

        errors: list[str] = []
        if self.entry in self.isolated:
            errors.append("entry")

        if self.exit_coor in self.isolated:
            errors.append("exit")

        if errors:
            raise ValueError(
                f"Error: {', '.join(errors)} inside the 42's pattern"
            )

    # def change_42_colour(self) -> None:
    #     self.colour_42 = next(self.colour_42_iter)
    #     self.render_maze()

    def create_grid(self) -> None:
        self.maze_grid = [[' '] * ((self.width + 1) + (self.width * 3))
                          for _ in range(self.height * 2 + 1)]

        self.maze_grid[(self.entry[1] * 2) + 1][(self.entry[0] * 4) + 2] = 'E'
        self.maze_grid[
            (self.exit_coor[1] * 2) + 1
            ][(self.exit_coor[0] * 4) + 2] = 'X'

    def show_hide_solution(self) -> None:
        maze_grid: MazeGrid = self.maze_grid

        def add_remove_arrows(path, movs, remove: bool = False,
                              animation: bool = False) -> None:
            for coor, mov in zip(path, movs):
                match mov:
                    case self.Moves.N:
                        arrow = '↑'
                        x = (coor[0] * 4) + 2
                        y = (coor[1] * 2)
                    case self.Moves.E:
                        arrow = '→'
                        x = (coor[0] * 4) + 4
                        y = (coor[1] * 2) + 1
                    case self.Moves.S:
                        arrow = '↓'
                        x = (coor[0] * 4) + 2
                        y = (coor[1] * 2) + 2
                    case self.Moves.W:
                        arrow = '←'
                        x = (coor[0] * 4)
                        y = (coor[1] * 2) + 1

                maze_grid[y][x] = arrow if not remove else ' '
                if animation:
                    self.print_maze(maze_grid, self.first_frame)
                    time.sleep(0.01)
            if not animation:
                self.print_maze(maze_grid, self.first_frame)

        def add_char(char: str, coor: Coor,
                     maze_grid: MazeGrid) -> None:
            maze_grid[(coor[1] * 2) + 1][(coor[0] * 4) + 2] = char

        def add_chars(coords: Iterable, char: str, maze_grid: MazeGrid,
                      animation: bool = False):
            for coor in coords:
                if (coor != self.entry and coor != self.exit_coor
                        and coor not in self.isolated):
                    add_char(char, coor, maze_grid)
                    if animation:
                        self.print_maze(maze_grid, self.first_frame)
                        time.sleep(0.01)
            if not animation:
                self.print_maze(maze_grid, self.first_frame)

        if self.solution_hidden:
            self.solution_hidden = False
            animation: bool = False

            if self.show_animation:
                animation = True

                add_chars(self.maze, '◦', maze_grid, animation=animation)
                add_chars(self.shortest_sol[1], '○', maze_grid,
                          animation=animation)
            add_remove_arrows(self.shortest_sol[1], self.shortest_sol[0],
                              animation=animation)
            add_chars(self.shortest_sol[1], '•', maze_grid,
                      animation=animation)
            add_chars(set(self.maze).difference(set(self.shortest_sol[1])),
                      ' ', maze_grid)

        else:
            self.solution_hidden = True

            add_chars(self.maze, ' ', maze_grid)
            add_remove_arrows(self.shortest_sol[1], self.shortest_sol[0], True)

    def parse_vertices(self) -> None:
        maze: Maze = self.maze
        width: int = self.width
        height: int = self.height
        vertices: dict[Coor, tuple[int, int, int, int]] = {}

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
        parsed_coor: dict[Coor, str] = {}
        for coor in vertices:
            key = vertices[coor]
            parsed_coor[coor] = (self.colour + self.MAZE_CHARS[key]
                                 + self.RESET
                                 if key in self.MAZE_CHARS else ' ')

        self.parsed_coor = parsed_coor

    def render_maze(self) -> None:
        maze_grid: MazeGrid = self.maze_grid
        self.parse_vertices()
        for coor in self.parsed_coor:
            x, y = coor
            x_ = x * 4
            y_ = y * 2

            maze_grid[y * 2][x * 4] = self.parsed_coor[coor]

            if coor in self.maze:
                if self.maze[x, y][0] == 1:
                    for w in range(1, 3 + 1):
                        maze_grid[y_][x_ + w] = self.colour + '─' + self.RESET
                if self.maze[x, y][1] == 1:
                    maze_grid[y_ + 1][x_ + 4] = self.colour + '│' + self.RESET
                if self.maze[x, y][2] == 1:
                    for w in range(1, 3 + 1):
                        maze_grid[y_ + 2][x_ + w] = (self.colour + '─'
                                                     + self.RESET)
                if self.maze[x, y][3] == 1:
                    maze_grid[y_ + 1][x_] = self.colour + '│' + self.RESET
        for coor in self.isolated:
            x, y = coor
            self.maze_grid[(y * 2) + 1][(x * 4) + 2] = "\033[45m \033[0m"
        self.print_maze(maze_grid, self.first_frame)
        self.first_frame = False

    def animate(self) -> None:
        maze_grid: MazeGrid = self.maze_grid
        coords: Maze = self.maze

        for coor in coords:
            x: int
            y: int
            x, y = coor
            x_mapped: int = x * 4
            y_mapped: int = y * 2

            if self.solutions:
                maze_grid[y * 2][x * 4] = self.parsed_coor[coor]

            if coor in self.maze:
                if self.maze[x, y][0] == 1:
                    for w in range(1, 3 + 1):
                        maze_grid[y_mapped][x_mapped + w] = '─'
                else:
                    for w in range(1, 3 + 1):
                        maze_grid[y_mapped][x_mapped + w] = ' '
                if self.maze[x, y][1] == 1:
                    maze_grid[y_mapped + 1][x_mapped + 4] = '│'
                else:
                    maze_grid[y_mapped + 1][x_mapped + 4] = ' '
                if self.maze[x, y][2] == 1:
                    for w in range(1, 3 + 1):
                        maze_grid[y_mapped + 2][x_mapped + w] = '─'
                else:
                    for w in range(1, 3 + 1):
                        maze_grid[y_mapped + 2][x_mapped + w] = ' '
                if self.maze[x, y][3] == 1:
                    maze_grid[y_mapped + 1][x_mapped] = '│'
                else:
                    maze_grid[y_mapped + 1][x_mapped] = ' '
            self.print_maze(maze_grid, self.first_frame)
            if self.first_frame:
                self.first_frame = False

    def print_maze(self, maze: list, first_frame: bool) -> None:
        if not first_frame:
            sys.stdout.write("\033[F" * len(maze))
        for row in maze:
            sys.stdout.write("".join(row) + '\n')
        sys.stdout.flush()
        self.first_frame = False

    def change_walls_colour(self) -> None:
        self.colour = next(self.colour_iter)
        self.parse_vertices()
        self.render_maze()

    def bitmask_output(self) -> None:
        result: str = ""
        sorted_maze: Maze = dict(
            sorted(self.maze.items(),
                   key=lambda item: (item[0][1], item[0][0]))
            )

        for coor, walls in sorted_maze.items():
            mask: int = (
                (walls[0] << 0) |
                (walls[1] << 1) |
                (walls[2] << 2) |
                (walls[3] << 3)
            )

            result += format(mask, 'X')

            if coor[0] == self.width - 1:
                result += '\n'
        result += (f"\n{self.entry[0]},{self.entry[1]}\n"
                   f"{self.exit_coor[0]},{self.exit_coor[1]}\n"
                   f"{''.join(mov.value for mov in self.shortest_sol[0])}\n"
                   f"{self.seed}"
                   )

        self.output = result

    def generate(self, width: int, height: int, unique_sol: bool, seed: int,
                 entry: Coor, exit_coor: Coor, output_file: str,
                 show_animation: bool = False):
        sys.setrecursionlimit(width * height * 10)
        self.entry = entry
        self.exit_coor = exit_coor
        self.width = width
        self.height = height
        self.unique_sol = unique_sol
        self.seed = seed
        self.path = []
        self.path.append(entry)
        self.show_animation = show_animation
        self.no_exit = []
        self.solution_path = ()
        self.maze = {}
        self.solutions = set()
        self.isolated = []
        self.parsed_coor = {}
        self.solution_hidden = True
        self.colour = ""
        self.first_frame: bool = True

        if self.width >= 8 and self.height >= 6:
            self.add_42_pattern()
        random.seed(seed)
        self.create_grid()
        self.print_maze(self.maze_grid, self.first_frame)  # pinta el grid vacío
        self.first_frame = False    
        self.maze_generation()
        self.render_maze()
        self.solve_maze(entry, exit_coor)
        self.shortest_solution()
        self.bitmask_output()
        with open(output_file, "w") as f:
            f.write(self.output)
