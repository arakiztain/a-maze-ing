from mlx import Mlx
import time
import os
from typing import Any

CELL: int = 40
WALL_COLOR: int = 0x000000
FLOOR_COLOR: int = 0xFFFFFF
ENTRY_COLOR: int = 0x00FF00
EXIT_COLOR: int = 0xFF0000
PATH_COLOR: int = 0x0000FF


def load_maze(path: str) -> tuple[
    list[list[int]], tuple[int, int], tuple[int, int], list[str]
        ]:
    """Load and parse a maze from a bitmask output file.

    Reads the maze grid, entry, exit and solution path from the file.
    The file format expects the maze bitmask rows first, followed by
    an empty line, then entry coordinates, exit coordinates, path moves
    and seed on separate lines.

    Args:
        path: Path to the maze output file.

    Returns:
        A tuple containing:
            - maze: 2D list of bitmask integers per cell.
            - entry: Entry coordinates as (x, y).
            - exit_: Exit coordinates as (x, y).
            - path: List of move characters ('N', 'E', 'S', 'W').
    """
    with open(path) as f:
        lines = [line.strip() for line in f if line.strip()]
    path_line = lines[-2]
    exit_line = lines[-3]
    entry_line = lines[-4]
    maze_lines = lines[:-4]
    maze = [[int(c, 16) for c in row] for row in maze_lines]
    entry = tuple(map(int, entry_line.split(',')))
    exit_ = tuple(map(int, exit_line.split(',')))
    path = list(path_line.strip())
    return maze, entry, exit_, path  # type: ignore


def put_pixel(buf: Any, bpp: int, size_line: int,
              x: int, y: int, color: int, fmt: int) -> None:
    """Write a single pixel to the image buffer.

    Supports two pixel formats depending on the fmt value:
    format 0 stores pixels as BGRA, format 1 as ARGB.

    Args:
        buf: The raw image buffer cast to bytes.
        bpp: Bits per pixel.
        size_line: Number of bytes per image row.
        x: Pixel x coordinate.
        y: Pixel y coordinate.
        color: Color as a 24-bit RGB integer (0xRRGGBB).
        fmt: Pixel format (0 for BGRA, 1 for ARGB).
    """
    bytes_per_pixel: int = bpp // 8
    index: int = y * size_line + x * bytes_per_pixel
    r: int = (color >> 16) & 0xFF
    g: int = (color >> 8) & 0xFF
    b: int = color & 0xFF
    if fmt == 0:
        buf[index] = b
        buf[index + 1] = g
        buf[index + 2] = r
        buf[index + 3] = 0xFF
    else:
        buf[index] = 0xFF
        buf[index + 1] = r
        buf[index + 2] = g
        buf[index + 3] = b


def draw_cell(buf: Any, bpp: int, size_line: int,
              x0: int, y0: int, cell_value: int,
              color: int | None = None, fmt: int = 0) -> None:
    """Draw a single maze cell to the image buffer including its walls.

    Fills the cell area with the given color, then draws closed walls
    on the corresponding edges based on the bitmask value. Walls are
    drawn as black lines on the cell borders.

    Bitmask bits: 0=North, 1=East, 2=South, 3=West.

    Args:
        buf: The raw image buffer cast to bytes.
        bpp: Bits per pixel.
        size_line: Number of bytes per image row.
        x0: Top-left pixel x coordinate of the cell.
        y0: Top-left pixel y coordinate of the cell.
        cell_value: Bitmask integer encoding which walls are closed.
        color: Fill color as 0xRRGGBB. Defaults to FLOOR_COLOR.
        fmt: Pixel format (0 for BGRA, 1 for ARGB).
    """
    if color is None:
        color = FLOOR_COLOR
    for y in range(CELL):
        for x in range(CELL):
            put_pixel(buf, bpp, size_line, x0 + x, y0 + y, color, fmt)
    if cell_value & 1:
        for dx in range(CELL):
            put_pixel(buf, bpp, size_line, x0 + dx, y0, WALL_COLOR, fmt)
    if cell_value & 2:
        for dy in range(CELL):
            put_pixel(buf, bpp, size_line,
                      x0 + CELL - 1, y0 + dy, WALL_COLOR, fmt)
    if cell_value & 4:
        for dx in range(CELL):
            put_pixel(buf, bpp, size_line,
                      x0 + dx, y0 + CELL - 1, WALL_COLOR, fmt)
    if cell_value & 8:
        for dy in range(CELL):
            put_pixel(buf, bpp, size_line, x0, y0 + dy, WALL_COLOR, fmt)


def path_to_coords(entry: tuple[int, int],
                   path: list[str]) -> list[tuple[int, int]]:
    """Convert a list of move characters into a list of coordinates.

    Starting from the entry point, applies each move to compute the
    sequence of cell coordinates that form the solution path.

    Args:
        entry: Starting coordinates as (x, y).
        path: List of move characters ('N', 'E', 'S', 'W').

    Returns:
        List of (x, y) coordinates from entry to exit inclusive.
    """
    x, y = entry
    coords: list[tuple[int, int]] = [(x, y)]
    move: dict[str, tuple[int, int]] = {
        'N': (0, -1), 'E': (1, 0), 'S': (0, 1), 'W': (-1, 0)
    }
    for step in path:
        dx, dy = move[step]
        x += dx
        y += dy
        coords.append((x, y))
    return coords


def main() -> None:
    """Launch the MLX window and render the maze with animated solution path.

    Loads the maze from maze.txt, initializes the MLX window, draws all
    cells with their walls, marks entry and exit, then animates the solution
    path step by step using the loop hook. Pressing ESC or closing the window
    exits the program.
    """
    maze, entry, exit_, path = load_maze("maze.txt")
    rows: int = len(maze)
    cols: int = len(maze[0])
    coords: list[tuple[int, int]] = path_to_coords(entry, path)

    mlx = Mlx()
    mlx_ptr = mlx.mlx_init()
    width: int = cols * CELL
    height: int = rows * CELL
    win = mlx.mlx_new_window(mlx_ptr, width, height, "Maze")
    img = mlx.mlx_new_image(mlx_ptr, width, height)
    buf, bpp, size_line, fmt = mlx.mlx_get_data_addr(img)
    buf = buf.cast('B')

    for y in range(rows):
        for x in range(cols):
            draw_cell(buf, bpp, size_line,
                      x * CELL, y * CELL, maze[y][x], fmt=fmt)

    ex, ey = entry
    draw_cell(buf, bpp, size_line,
              ex * CELL, ey * CELL, maze[ey][ex], ENTRY_COLOR, fmt=fmt)
    ex, ey = exit_
    draw_cell(buf, bpp, size_line,
              ex * CELL, ey * CELL, maze[ey][ex], EXIT_COLOR, fmt=fmt)

    current_step: list[int] = [0]

    def loop_hook(param: Any) -> int:
        """Animate the solution path one step per loop iteration.

        Args:
            param: Unused MLX hook parameter.

        Returns:
            Always 0.
        """
        if current_step[0] >= len(coords):
            return 0
        x, y = coords[current_step[0]]
        draw_cell(buf, bpp, size_line,
                  x * CELL, y * CELL, maze[y][x], PATH_COLOR, fmt=fmt)
        mlx.mlx_sync(mlx_ptr, 1, img)
        mlx.mlx_put_image_to_window(mlx_ptr, win, img, 0, 0)
        mlx.mlx_sync(mlx_ptr, 3, win)
        current_step[0] += 1
        time.sleep(0.05)
        return 0

    def key_hook(keycode: int, param: Any) -> int:
        """Handle keyboard events, closing the window on ESC.

        Args:
            keycode: The keycode of the pressed key.
            param: Unused MLX hook parameter.

        Returns:
            Always 0.
        """
        if keycode == 65307:
            mlx.mlx_destroy_window(mlx_ptr, win)
            os._exit(0)
        return 0

    def close_hook(param: Any) -> None:
        """Handle window close event.

        Args:
            param: Unused MLX hook parameter.
        """
        os._exit(0)

    mlx.mlx_key_hook(win, key_hook, None)
    mlx.mlx_hook(win, 17, 0, close_hook, None)
    mlx.mlx_loop_hook(mlx_ptr, loop_hook, None)
    mlx.mlx_loop(mlx_ptr)


if __name__ == "__main__":
    main()
