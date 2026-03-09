*This project has been created as part of the 42 curriculum by garakizt, imunoz-a.*

# A-Maze-ing
```
   ░███            ░███     ░███                                          ░██                      
  ░██░██           ░████   ░████                                                                   
 ░██  ░██          ░██░██ ░██░██  ░██████   ░█████████  ░███████          ░██░████████   ░████████ 
░█████████ ░██████ ░██ ░████ ░██       ░██       ░███  ░██    ░██ ░██████ ░██░██    ░██ ░██    ░██ 
░██    ░██         ░██  ░██  ░██  ░███████     ░███    ░█████████         ░██░██    ░██ ░██    ░██ 
░██    ░██         ░██       ░██ ░██   ░██   ░███      ░██                ░██░██    ░██ ░██   ░███ 
░██    ░██         ░██       ░██  ░█████░██ ░█████████  ░███████          ░██░██    ░██  ░█████░██ 
                                                                                               ░██ 
                                                                                         ░███████  
                                                                                                   
```
## Description

A-Maze-ing is a Python project that generates, solves and visually renders random mazes. The goal is to produce valid, reproducible mazes from a configuration file, export them in a bitmask format, and display them either in the terminal via ASCII rendering or graphically using the MiniLibX (MLX) library.

Each maze contains a visible **"42" pattern** formed by isolated cells, configurable entry and exit points, and a computed shortest solution path. Mazes can be perfect (one unique path between any two points) or imperfect (with alternative routes).

The maze generator is also packaged as a standalone, reusable Python library (`mazegen`) that can be installed via `pip`.

---

## Instructions

### Requirements

- Python 3.10 or later
- MiniLibX (included in `mlx_CLXV/`)

### Installation

```bash
make install
```

This will:
1. Compile the MiniLibX shared library from source.
2. Install the MLX Python wheel.
3. Install the project and all dev dependencies via `pip install -e ".[dev]"`.

### Running

```bash
make run
```

To use a custom config file:

```bash
python3 a_maze_ing.py my_config.txt
```

### Debug mode

```bash
make debug
```

### CLI Options

Once running, the interactive menu provides:

| Key | Action |
|-----|--------|
| `1` | Re-generate a new maze (new random seed if not fixed) |
| `2` | Show / hide the shortest solution path |
| `3` | Rotate maze wall colours |
| `4` | Launch the MLX graphical display |
| `5` | Exit |

### MLX Window Controls

| Key | Action |
|-----|--------|
| `ESC` | Close the window |

### Linting

```bash
make lint         # flake8 + mypy with recommended flags
make lint-strict  # flake8 + mypy --strict
```

### Cleaning

```bash
make clean    # Remove Python caches (__pycache__, .mypy_cache, etc.)
```

---

## Config File Format

The configuration file uses a simple `KEY = VALUE` format. Lines starting with `#` are treated as comments and ignored.

```
# Maze dimensions (min: 2, max: 46)
WIDTH = 12
HEIGHT = 12

# Entry and exit coordinates as x,y (0-indexed, within bounds)
ENTRY = 0,0
EXIT = 11,11

# Output file path for the bitmask maze (must not be a reserved filename)
OUTPUT_FILE = maze.txt

# Perfect maze: true = one unique path, false = alternative paths added
PERFECT = true

# Animate the maze generation in the terminal
ANIMATION = false

# Seed for reproducibility (omit or set to none for a random seed)
SEED = none
```

A default example config is available at `config/config_example.txt`.

---

## Maze Generation Algorithm

This project uses the **Recursive Backtracking** algorithm (also known as Randomized Depth-First Search) to generate mazes.

### How it works

1. Start from the entry cell and mark it as visited.
2. Randomly shuffle the four possible directions (N, E, S, W).
3. For each direction, if the neighbouring cell is unvisited and within bounds, carve a passage (remove the wall) and recurse into that cell.
4. If no valid moves exist (dead end), backtrack to the previous cell.
5. Repeat until all cells have been visited.

The "42" pattern cells are pre-isolated before generation begins, so the algorithm navigates around them naturally.

For imperfect mazes (`PERFECT = false`), after the main generation is complete, up to 2 additional walls are removed along the solution path to create alternative routes.

### Why this algorithm?

Recursive backtracking was chosen because:

- It is straightforward to implement and reason about.
- It guarantees full connectivity — every cell is reachable from every other cell.
- It produces mazes with long, winding corridors that are visually interesting and non-trivial to solve.
- It integrates naturally with the custom entry/exit and isolated cell constraints of this project.
- It supports reproducibility via a seed passed to `random.seed()`.

The main trade-off is that for very large mazes it requires deep recursion, which is mitigated by calling `sys.setrecursionlimit(width * height * 10)` at generation time.

---

## Reusable Module

The `MazeGenerator` class is packaged as a standalone installable Python library: `mazegen`.

### What is reusable

The entire `mazegen/MazeGenerator.py` module, including:
- Maze generation with configurable size, seed, entry, exit and perfect/imperfect mode.
- Solution finding and shortest path computation.
- ASCII terminal rendering with colour support.
- Bitmask output file generation.

### Building and installing the package

```bash
# Create a clean virtual environment
python3 -m venv venv
source venv/bin/activate

# Install build tools
pip install build

# Build the package
python -m build

# Install the generated wheel
pip install dist/mazegen-1.0.0-py3-none-any.whl
```

### Basic usage example

```python
from mazegen.MazeGenerator import MazeGenerator

maze = MazeGenerator()
maze.generate(
    width=12,
    height=12,
    unique_sol=True,   # True = perfect maze, False = imperfect
    seed=1234,
    entry=(0, 0),
    exit_coor=(11, 11),
    output_file="maze.txt"
)

# Access the maze structure
print(maze.maze)           # dict[(x,y)] -> [N, E, S, W] wall states
print(maze.shortest_sol)   # (moves_tuple, coords_tuple)
print(maze.seed)           # seed used
```

### Passing custom parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `width` | `int` | Number of columns |
| `height` | `int` | Number of rows |
| `unique_sol` | `bool` | `True` for perfect maze |
| `seed` | `int` | Random seed |
| `entry` | `tuple[int,int]` | Entry coordinates |
| `exit_coor` | `tuple[int,int]` | Exit coordinates |
| `output_file` | `str` | Path to output file |
| `show_animation` | `bool` | Animate generation |

### Accessing the solution

```python
moves, path = maze.shortest_sol
print([m.value for m in moves])  # ['N', 'E', 'S', ...]
print(path)                       # ((0,0), (0,1), ...)
```

---

## Resources

### Algorithm references

- [Maze Generation Algorithms — Wikipedia](https://en.wikipedia.org/wiki/Maze_generation_algorithm)
- [Recursive Backtracking — Jamis Buck](https://weblog.jamisbuck.org/2010/12/27/maze-generation-recursive-backtracking)
- [Backtracking Algorithms — GeeksForGeeks](https://www.geeksforgeeks.org/dsa/backtracking-algorithms/)
- [Maze Generation with Recursive Backtracking — Medium](https://aryanab.medium.com/maze-generation-recursive-backtracking-5981bc5cc766)
- [Maze Generation Algorithms — datagenetics.com](http://datagenetics.com/blog/november22015/index.html)

### Libraries and tools used

**Standard library:**
- `sys` — recursion limit, stdout writing
- `os` — subprocess and process management
- `random` — maze generation randomness and seed control
- `shutil` — terminal size detection
- `itertools` — colour cycling with `cycle`
- `time` — animation delays
- `enum` — direction enum (`Moves`)
- `typing` — type hints (`TypeAlias`, `Iterator`, `Iterable`, `Tuple`)

**Third party:**
- [Pydantic](https://docs.pydantic.dev/) — Config validation with `@pydantic_dataclass` and `model_validator`
- [MiniLibX](https://github.com/codam-coding-college/MLX42) — Graphical window and pixel rendering
- [mypy](https://mypy.readthedocs.io/) — Static type checking
- [flake8](https://flake8.pycqa.org/) — Code style enforcement

### AI usage

Claude (Anthropic) was used throughout the project, primarily for:
- Understanding the MiniLibX Python bindings, hook system and pixel buffer format.
- Debugging terminal rendering issues (ANSI escape sequences, cursor positioning).
- Setting up the `pyproject.toml` packaging configuration.
- Adding type hints and docstrings across the codebase.
- Reviewing and fixing `mypy` and `flake8` errors.

---

## Team & Project Management

### Team members

| Login | Role |
|-------|------|
| `imunoz-a` | Maze generation algorithm, bitmask output format, solution finding |
| `garakizt` | Config parser, ASCII terminal rendering, MLX integration, CLI loop |

### Planning

The project started with understanding the subject requirements and breaking them into phases:

1. **Config parsing** — Implementing `MazeConfig` with Pydantic for robust validation.
2. **Algorithm** — Understanding and implementing recursive backtracking, including the "42" pattern isolation and solution finding.
3. **ASCII rendering** — Building the grid renderer with ANSI colours, animation, and solution path display.
4. **MLX integration** — Learning the MiniLibX hook system and pixel buffer format to build the graphical display.
5. **Packaging** — Wrapping `MazeGenerator` as an installable `pip` package.

The main deviation from the initial plan was the significant time spent debugging terminal rendering edge cases (cursor positioning, terminal size constraints) and MLX subprocess management.

### What worked well

- Pydantic for config validation — clean, concise, and catches errors early.
- The recursive backtracking algorithm — relatively straightforward to implement and produces good-looking mazes.
- Separating the generator into a standalone module made it easy to package and reuse.
- The bitmask format for the output file is compact and easy to parse.

### What could be improved

- **Larger terminal mazes** — the ASCII renderer is limited by terminal size. A `curses`-based implementation would allow proper rendering of larger mazes without visual artefacts.
- **42 pattern colour** — the ability to independently change the colour of the "42" pattern cells was partially implemented but removed due to ANSI rendering conflicts.
- **Imperfect maze quality** — `create_alt_path` only opens a small number of walls; a more thorough implementation would guarantee more visible alternative routes.
- **MLX as primary display** — moving the full CLI interface into the MLX window was explored but ran into pixel buffer and text rendering complexity.

### Tools used

- **VSCode** — main development environment
- **Git / GitHub** — version control and pull request workflow
- **Claude (Anthropic)** — AI assistant for debugging, documentation and MLX guidance
- **mypy + flake8** — static analysis and code style enforcement
- **Pydantic** — runtime config validation