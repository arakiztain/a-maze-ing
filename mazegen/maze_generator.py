from __future__ import annotations
from typing import Iterator, TypeAlias, Callable
from enum import Enum
import random
import sys
import time
from itertools import cycle
import shutil
from functools import wraps
from mazegen.maze_config import MazeConfig

Coor: TypeAlias = tuple[int, int]
Solution: TypeAlias = tuple[
    tuple["MazeGenerator.Moves", ...],
    tuple[Coor, ...]]
Solutions: TypeAlias = set[Solution]
MazeGrid: TypeAlias = list[list[str]]
Maze: TypeAlias = dict[Coor, list[int]]


def enough_space(func: Callable[..., None]) -> Callable[..., None]:
    """Decorator to check if the terminal has enough space
    to render the maze.
    If not, it will print a message with the maximum
    allowed size and the current size."""
    @wraps(func)
    def wrapper(self: "MazeGenerator") -> None:
        term_cols: int
        term_lines: int
        term_cols, term_lines = shutil.get_terminal_size()
        maze_cols: int = len(self.maze_grid[0])
        maze_lines: int = len(self.maze_grid)

        if term_lines >= maze_lines and term_cols >= maze_cols:
            func(self)
        elif self.first_frame and not self.no_space_printed:
            self.max_size()
            self.print_no_space()
            self.no_space_printed = True

        return None

    return wrapper


class MazeGenerator:
    """A maze generator that creates, renders and solves mazes using recursive
      backtracking.

        This class generates random mazes with configurable
        dimensions, entry/exit points, and an optional '42' pattern of
        isolated cells. It supports ASCII terminal rendering with optional
        colour and animation, as well as exporting the maze structure to a
        bitmask output file.

        The maze is represented internally as a dictionary mapping (x, y)
        coordinates to a list of 4 wall states [N, E, S, W], where 1 means
        the wall is closed and 0 means it is open. The generator uses a
        depth-first search algorithm with random shuffling to ensure full
        connectivity and no isolated cells (except those forming the
        '42' pattern).

        Attributes:
            entry: Entry point coordinates as (x, y).
            exit_coor: Exit point coordinates as (x, y).
            width: Width of the maze in cells.
            height: Height of the maze in cells.
            unique_sol: If True, alternative paths are created (imperfect maze).
            path: List of coordinates visited during generation.
            no_exit: List of dead-end coordinates reached during generation.
            solution_path: Tuple of coordinates forming the first found
            solution.
            maze: Dictionary mapping (x, y) coordinates to wall state lists.
            solutions: Set of all solutions found, each as (moves, path) tuples.
            isolated: List of coordinates belonging to the '42' pattern.
            shortest_sol: The shortest solution as a (moves, path) tuple.
            maze_grid: 2D character grid used for ASCII rendering.
            parsed_coor: Mapping of coordinates to rendered corner characters.
            first_frame: Whether the next print is the first frame
            (no cursor up).
            show_animation: Whether to animate the generation step by step.
            solution_hidden: Whether the solution path is currently hidden.
            colour: ANSI escape code for the current wall colour.
            output: String content to write to the maze output file.
            seed: The random seed used for this generation.
            enough_space: Whether the terminal is large enough
            to render the maze.

        Example:
            >>> from mazegen.MazeGenerator import MazeGenerator
            >>> maze = MazeGenerator()
            >>> maze.generate(
            ...     width=12, height=12, unique_sol=True, seed=1234,
            ...     entry=(0, 0), exit_coor=(11, 11), output_file="maze.txt"
            ... )
            >>> print(maze.seed)
            1234
            >>> print(maze.shortest_sol[0])  # moves tuple
        """

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
    no_space_printed: bool = False
    output_filename: str
    no_print_msg: str = ("\nThe maze is too large to render "
                         "in the terminal. "
                         "Try resizing the window.\n")
    max_size_print: tuple[int, int]

    class Moves(Enum):
        """Cardinal directions for maze movement."""

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
    colour_iter: Iterator[str] = cycle(COLOURS)

    PATTERN_COLOURS: tuple[str, ...] = (
        "\033[101m",
        "\033[102m",
        "\033[103m",
        "\033[104m",
        "\033[105m",
        "\033[106m"
    )

    pattern_colour_iter: Iterator[str] = cycle(PATTERN_COLOURS)

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

    def _move(self, coordinates: Coor, move: Moves) -> Coor:
        """Calculate the next coordinate after applying a move.

        Args:
            coordinates: Current position as (x, y).
            move: Direction to move.

        Returns:
            New position as (x, y).
        """
        deltas: dict[MazeGenerator.Moves, tuple[int, int]] = {
            self.Moves.N: (0, -1),
            self.Moves.E: (1, 0),
            self.Moves.S: (0, 1),
            self.Moves.W: (-1, 0)
        }
        dx, dy = deltas[move]
        x, y = coordinates
        return x + dx, y + dy

    def _valid_move(self, coordinates: Coor, move: Moves) -> bool:
        """Check if a move is valid (no wall blocking).

        Args:
            coordinates: Current position as (x, y).
            move: Direction to check.

        Returns:
            True if the move is valid, False otherwise.
        """
        move_index: dict[MazeGenerator.Moves, int] = {
            self.Moves.N: 0,
            self.Moves.E: 1,
            self.Moves.S: 2,
            self.Moves.W: 3
        }
        x, y = coordinates
        return self.maze[x, y][move_index[move]] == 0

    def solve_maze(self, curr_coor: Coor,
                   exit_coor: Coor, move: Moves | None = None,
                   movs: tuple[Moves, ...] = (),
                   path: tuple[Coor, ...] = ()) -> None:
        """Recursively find all solutions from current position to exit.

        Args:
            curr_coor: Current position.
            exit_coor: Target exit position.
            move: Move that led to this position.
            movs: Tuple of moves taken so far.
            path: Tuple of coordinates visited so far.
        """
        if curr_coor == exit_coor:
            if (movs[:-1], path) not in self.solutions:
                self.solutions.add((movs[:-1], path))
            return

        if move is not None:
            if not self._valid_move(curr_coor, move):
                return
            curr_coor = self._move(curr_coor, move)
            if curr_coor in path or curr_coor not in self.maze:
                return

        for move in list(self.Moves):
            self.solve_maze(curr_coor, exit_coor, move, movs + (move,),
                            path + (curr_coor,))

    def _maze_generation(self) -> None:
        """Generate the maze using a recursive backtracking algorithm."""

        def add_walls(coor: Coor, mov: MazeGenerator.Moves | None) -> None:
            """Add or update walls for a cell.

            Args:
                coor: Cell coordinates.
                mov: Direction of the opening to create, or None.
            """
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
                self._animate()

        def remove_walls(coor: Coor, mov: MazeGenerator.Moves | None) -> None:
            """Remove walls between two adjacent cells.

            Args:
                coor: Cell coordinates.
                mov: Direction of the wall to remove.
            """
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
            """Create alternative paths for imperfect mazes."""
            celds = list(self.solution_path)
            random.shuffle(celds)
            count = 0
            for celd in celds:
                for mov in list(self.Moves):
                    if valid_move(celd, mov, [], True):
                        remove_walls(celd, mov)
                        if self.show_animation:
                            self._animate()
                        count += 1
                        break
                if count == 2:
                    break

        def valid_celd(coor: Coor) -> bool:
            """Check if coordinates are within maze bounds.

            Args:
                coor: Coordinates to check.

            Returns:
                True if within bounds, False otherwise.
            """
            return bool(
                0 <= coor[0] <= self.width - 1
                and 0 <= coor[1] <= self.height - 1
                )

        def valid_move(curr: Coor, mov: MazeGenerator.Moves,
                       path: list[Coor], alt_path: bool = False) -> bool:
            """Check if a move is valid during generation.

            Args:
                curr: Current position.
                mov: Direction to move.
                path: Already visited positions.
                alt_path: Whether to avoid solution path cells.

            Returns:
                True if the move is valid, False otherwise.
            """
            next_coor = self._move(curr, mov)
            alt_path_valid = (next_coor not in self.solution_path
                              if alt_path else True)
            return bool(
                next_coor not in path and valid_celd(next_coor)
                and next_coor not in self.no_exit and alt_path_valid and
                next_coor not in self.isolated
                )

        def path_generation(curr: Coor,
                            solution: tuple[MazeGenerator.Moves, ...] = (),
                            path: tuple[Coor, ...] = (self.entry,)) -> None:
            """Recursively generate the maze path.

            Args:
                curr: Current position.
                solution: Moves taken so far.
                path: Coordinates visited so far.
            """
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
                    next_coor = self._move(curr, mov)
                    self.path.append(next_coor)
                    path_generation(next_coor, solution + (mov,),
                                    path + (next_coor,))

            if no_moves:
                add_walls(curr, None)
                self.no_exit.append(curr)

        path_generation(self.entry)
        if not self.unique_sol:
            create_alt_path()

    def _shortest_solution(self) -> None:
        """Find and store the shortest solution from all found solutions."""
        if not self.solutions:
            return
        self.shortest_sol = min(self.solutions,
                                key=lambda sol: len(sol[0]))

    def _add_42_pattern(self) -> None:
        """Add the '42' pattern of isolated cells to the maze.

        Raises:
            ValueError: If entry or exit is inside the 42 pattern.
        """
        pattern_width: int = 7
        pattern_height: int = 5
        start_x: int = (self.width - pattern_width) // 2
        start_y: int = (self.height - pattern_height) // 2

        def isolate_celds(coor: Coor) -> None:
            """Isolate a cell by surrounding it with walls.

            Args:
                coor: Coordinates of the cell to isolate.
            """
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

    def _create_grid(self) -> None:
        """Create the initial empty ASCII grid for rendering."""
        self.maze_grid = [[' '] * ((self.width + 1) + (self.width * 3))
                          for _ in range(self.height * 2 + 1)]
        self.maze_grid[(self.entry[1] * 2) + 1][(self.entry[0] * 4) + 2] = 'E'
        self.maze_grid[
            (self.exit_coor[1] * 2) + 1
        ][(self.exit_coor[0] * 4) + 2] = 'X'

    def _add_char(self, char: str, coor: Coor, maze_grid: MazeGrid) -> None:
        """Place a character at a cell position in the grid.

        Args:
            char: Character to place.
            coor: Cell coordinates.
            maze_grid: The grid to modify.
        """
        maze_grid[(coor[1] * 2) + 1][(coor[0] * 4) + 2] = char

    def _add_chars(self, coords: Maze | tuple[Coor, ...] | set[Coor],
                   char: str, maze_grid: MazeGrid,
                   animation: bool = False) -> None:
        """Place a character at multiple cell positions.

        Args:
            coords: Iterable of cell coordinates.
            char: Character to place.
            maze_grid: The grid to modify.
            animation: If True, animate step by step.
        """
        for coor in coords:
            if (coor != self.entry and coor != self.exit_coor
                    and coor not in self.isolated):
                self._add_char(char, coor, maze_grid)
                if animation:
                    self._print_maze(maze_grid, self.first_frame)
                    time.sleep(0.01)

    @enough_space
    def show_hide_solution(self) -> None:
        """Toggle the visibility of the solution path in the ASCII render."""
        maze_grid: MazeGrid = self.maze_grid

        def add_remove_arrows(path: tuple[Coor, ...],
                              movs: tuple[MazeGenerator.Moves, ...],
                              remove: bool = False,
                              animation: bool = False) -> None:
            """Add or remove direction arrows along the solution path.

            Args:
                path: Coordinates of the solution path.
                movs: Moves corresponding to the path.
                remove: If True, remove arrows instead of adding.
                animation: If True, animate step by step.
            """
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
                    self._print_maze(maze_grid, self.first_frame)
                    time.sleep(0.01)

        if self.solution_hidden:
            self.solution_hidden = False
            animation: bool = False

            if self.show_animation:
                animation = True

                self._add_chars(self.maze, '◦', maze_grid, animation=animation)
                self._add_chars(self.shortest_sol[1], '○', maze_grid,
                                animation=animation)
            add_remove_arrows(self.shortest_sol[1], self.shortest_sol[0],
                              animation=animation)
            self._add_chars(self.shortest_sol[1], '•', maze_grid,
                            animation=animation)
            self._add_chars(set(self.maze)
                            .difference(set(self.shortest_sol[1])),
                            ' ', maze_grid)

            self._print_maze(maze_grid, self.first_frame)

        else:
            self.solution_hidden = True
            self._add_chars(self.maze, ' ', maze_grid)
            add_remove_arrows(self.shortest_sol[1],
                              self.shortest_sol[0], True)
            self._print_maze(maze_grid, self.first_frame)

    def _parse_vertices(self) -> None:
        """Parse maze cells into vertex characters for ASCII rendering."""
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

    @enough_space
    def _render_maze(self) -> None:
        """Render the full maze to the ASCII grid and print it."""
        maze_grid: MazeGrid = self.maze_grid
        self._parse_vertices()
        for coor in self.parsed_coor:
            x, y = coor
            x_ = x * 4
            y_ = y * 2
            maze_grid[y * 2][x * 4] = self.parsed_coor[coor]
            if coor in self.maze:
                if self.maze[x, y][0] == 1:
                    for w in range(1, 4):
                        maze_grid[y_][x_ + w] = self.colour + '─' + self.RESET
                if self.maze[x, y][1] == 1:
                    maze_grid[y_ + 1][x_ + 4] = self.colour + '│' + self.RESET
                if self.maze[x, y][2] == 1:
                    for w in range(1, 4):
                        maze_grid[y_ + 2][x_ + w] = (
                            self.colour + '─' + self.RESET
                            )
                if self.maze[x, y][3] == 1:
                    maze_grid[y_ + 1][x_] = self.colour + '│' + self.RESET

        self._print_maze(maze_grid, self.first_frame)
        self.first_frame = False

    @enough_space
    def _animate(self) -> None:
        """Animate the maze generation by updating the grid incrementally."""
        maze_grid: MazeGrid = self.maze_grid
        coords: Maze = self.maze

        for coor in coords:
            x, y = coor
            x_mapped: int = x * 4
            y_mapped: int = y * 2

            if self.solutions:
                maze_grid[y * 2][x * 4] = self.parsed_coor[coor]

            if coor in self.maze:
                if self.maze[x, y][0] == 1:
                    for w in range(1, 4):
                        maze_grid[y_mapped][x_mapped + w] = '─'
                else:
                    for w in range(1, 4):
                        maze_grid[y_mapped][x_mapped + w] = ' '
                if self.maze[x, y][1] == 1:
                    maze_grid[y_mapped + 1][x_mapped + 4] = '│'
                else:
                    maze_grid[y_mapped + 1][x_mapped + 4] = ' '
                if self.maze[x, y][2] == 1:
                    for w in range(1, 4):
                        maze_grid[y_mapped + 2][x_mapped + w] = '─'
                else:
                    for w in range(1, 4):
                        maze_grid[y_mapped + 2][x_mapped + w] = ' '
                if self.maze[x, y][3] == 1:
                    maze_grid[y_mapped + 1][x_mapped] = '│'
                else:
                    maze_grid[y_mapped + 1][x_mapped] = ' '
            self._print_maze(maze_grid, self.first_frame)
            if self.first_frame:
                self.first_frame = False

    def _print_maze(self, maze: MazeGrid, first_frame: bool) -> None:
        """Print the maze grid to stdout, overwriting the previous frame.

        Args:
            maze: The 2D grid to print.
            first_frame: If True, print without moving the cursor up.
        """
        if not first_frame:
            sys.stdout.write("\033[F" * len(maze))
        for row in maze:
            sys.stdout.write("".join(row) + '\n')
        sys.stdout.flush()
        self.first_frame = False

    @enough_space
    def change_walls_colour(self) -> None:
        """Cycle to the next wall colour and re-render the maze."""
        self.colour = next(self.colour_iter)
        self._parse_vertices()
        self._render_maze()

    @enough_space
    def change_pattern_colour(self) -> None:
        """Cycle to the next pattern colour and re-render the maze."""
        colour: str = next(self.pattern_colour_iter)
        char: str = colour + ' ' + "\033[0m"
        maze_grid: MazeGrid = self.maze_grid
        for coor in self.isolated:
            self._add_char(char, coor, maze_grid)
        self._print_maze(maze_grid, self.first_frame)

    def bitmask_output(self) -> None:
        """Generate the bitmask string output for the maze file."""
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
                   # f"{self.seed}"
                   )
        self.output = result

    def max_size(self) -> None:
        """Generate a message indicating the max allowed maze size."""
        term_cols, term_lines = shutil.get_terminal_size()
        max_width: int = (term_cols - 1) // 4
        max_height: int = ((term_lines - 1) // 2) - 1
        self.max_size_print = (max_width, max_height)

    def print_no_space(self) -> None:
        """Print a message indicating that the maze cannot
        be rendered due to size constraints."""
        max_width, max_height = self.max_size_print

        print(self.no_print_msg,
              f"Max allowed size: "
              f"{max_width}x{max_height}\n"
              f"Current size: "
              f"{self.width}x{self.height}\n",
              sep='\n')

    def _validate_state(self) -> None:
        """Validate the initial state of the maze generator."""
        config = MazeConfig(
            width=self.width,
            height=self.height,
            entry=self.entry,
            exit=self.exit_coor,
            output_file=self.output_filename,
            perfect=self.unique_sol,
            animation=self.show_animation,
            seed=self.seed,
            user_set_seed=False
        )

        self.width = config.width
        self.height = config.height
        self.entry = config.entry
        self.exit_coor = config.exit
        self.output_filename = config.output_file
        self.unique_sol = config.perfect
        self.animation = config.animation
        self.seed = config.seed

    def generate(self, width: int, height: int, unique_sol: bool,
                 seed: int, entry: Coor, exit_coor: Coor,
                 output_file: str,
                 show_animation: bool = False) -> None:
        """Generate a maze with the given parameters.

        Args:
            width: Width of the maze in cells.
            height: Height of the maze in cells.
            unique_sol: If True, creates alternative paths (imperfect maze).
            seed: Random seed for reproducibility.
            entry: Entry coordinates.
            exit_coor: Exit coordinates.
            output_file: Path to write the maze output file.
            show_animation: If True, animate the generation process.
        """
        self.entry = entry
        self.exit_coor = exit_coor
        self.width = width
        self.height = height
        self.unique_sol = unique_sol
        self.seed = seed
        self.show_animation = show_animation
        self.no_exit = []
        self.solution_path = ()
        self.maze = {}
        self.solutions = set()
        self.isolated = []
        self.parsed_coor = {}
        self.solution_hidden = True
        self.colour = ""
        self.first_frame = True
        self.output_filename = output_file
        self.no_space_printed = False

        self._validate_state()

        self.path = [self.entry]
        if self.width >= 8 and self.height >= 6:
            self._add_42_pattern()
        sys.setrecursionlimit(self.width * self.height * 10)
        random.seed(seed)
        self._create_grid()
        self._maze_generation()
        self._render_maze()
        self.solve_maze(self.entry, self.exit_coor)
        self._shortest_solution()
        self.bitmask_output()

        try:
            with open(self.output_filename, "w") as f:
                f.write(self.output)
        except OSError as e:
            print(f"Cannot write output file '{self.output_filename}': {e}")
        except Exception as e:
            print(f"Error: {e}")
