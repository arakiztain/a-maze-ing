from mlx import Mlx
import sys
from maze.config_parser import parse_config
import maze.generator as generator

CELL = 40

FLOOR_COLOR = 0xFFFFFF
ENTRY_COLOR = 0x00FF00
EXIT_COLOR = 0xFF0000
PATH_COLOR = 0x0000FF
COLOR_42 = 0xFF0000

UI_HEIGHT = 130
UI_BG_COLOR = 0x202020
UI_TEXT_COLOR = 0xFFFFFF
SEPARATOR_COLOR = 0x555555


def load_maze(path: str):
    """Carga el laberinto desde el txt generado por generator.py"""
    with open(path) as f:
        lines = [line.strip() for line in f if line.strip()]

    maze_lines = lines[:-3]
    entry_line = lines[-3]
    exit_line = lines[-2]
    path_line = lines[-1]

    maze = [[int(c, 16) for c in row] for row in maze_lines]
    entry = tuple(map(int, entry_line.split(',')))
    exit_ = tuple(map(int, exit_line.split(',')))
    path = list(path_line.strip())
    return maze, entry, exit_, path


def load_42_cells(path: str):
    """Carga las celdas del 42 desde el TXT si existen"""
    with open(path) as f:
        lines = [line.strip() for line in f]
    if "42_cells:" not in lines:
        return []
    index = lines.index("42_cells:") + 1
    cells = []
    while index < len(lines):
        line = lines[index]
        if not line or ',' not in line:
            break
        x, y = map(int, line.split(','))
        cells.append((x, y))
        index += 1
    return cells


def put_pixel(buf, bpp, size_line, x, y, color, format):
    bytes_per_pixel = bpp // 8
    index = y * size_line + x * bytes_per_pixel

    r = (color >> 16) & 0xFF
    g = (color >> 8) & 0xFF
    b = color & 0xFF
    a = 0xFF

    if format == 0:
        buf[index]     = b
        buf[index + 1] = g
        buf[index + 2] = r
        buf[index + 3] = a
    else:
        buf[index]     = a
        buf[index + 1] = r
        buf[index + 2] = g
        buf[index + 3] = b


def draw_cell(buf, bpp, size_line, x0, y0, cell_value,
              wall_color, fill_color, format=0):
    WALL_THICK = 6

    # Relleno
    for y in range(CELL):
        for x in range(CELL):
            put_pixel(buf, bpp, size_line, x0 + x, y0 + y, fill_color, format)

    t = WALL_THICK
    # Paredes
    if cell_value & 1:  # top
        for dy in range(t):
            for dx in range(CELL):
                put_pixel(buf, bpp, size_line, x0 + dx, y0 + dy, wall_color, format)
    if cell_value & 2:  # right
        for dy in range(CELL):
            for dx in range(t):
                put_pixel(buf, bpp, size_line, x0 + CELL - dx - 1, y0 + dy, wall_color, format)
    if cell_value & 4:  # bottom
        for dy in range(t):
            for dx in range(CELL):
                put_pixel(buf, bpp, size_line, x0 + dx, y0 + CELL - dy - 1, wall_color, format)
    if cell_value & 8:  # left
        for dy in range(CELL):
            for dx in range(t):
                put_pixel(buf, bpp, size_line, x0 + dx, y0 + dy, wall_color, format)


def path_to_coords(entry, path):
    x, y = entry
    coords = [(x, y)]
    move = {'N': (0, -1), 'E': (1, 0), 'S': (0, 1), 'W': (-1, 0)}
    for step in path:
        dx, dy = move[step]
        x += dx
        y += dy
        coords.append((x, y))
    return coords


def main():
    maze, entry, exit_, path = load_maze("maze.txt")
    rows = len(maze)
    cols = len(maze[0])
    coords_path = path_to_coords(entry, path)

    mlx = Mlx()
    mlx_ptr = mlx.mlx_init()

    width = cols * CELL
    height = rows * CELL + UI_HEIGHT

    win = mlx.mlx_new_window(mlx_ptr, width, height, "Maze")
    img = mlx.mlx_new_image(mlx_ptr, width, height)
    buf, bpp, size_line, format = mlx.mlx_get_data_addr(img)
    buf = buf.cast('B')

    state = {
        "maze": maze,
        "entry": entry,
        "exit": exit_,
        "coords": coords_path,
        "rows": rows,
        "cols": cols,
        "show_path": True,
        "show_entry_exit": True,
        "anim_step": 0,
        "frame": 0,
        "wall_colors": [0x000000, 0x333333, 0x880000, 0x004488],
        "wall_index": 0,
    }

    def draw_base():
        wall_color = state["wall_colors"][state["wall_index"]]

        ui_start = rows * CELL
        for y in range(ui_start, ui_start + UI_HEIGHT):
            for x in range(width):
                put_pixel(buf, bpp, size_line, x, y, UI_BG_COLOR, format)

        for x in range(width):
            put_pixel(buf, bpp, size_line, x, ui_start, SEPARATOR_COLOR, format)

        for y in range(rows):
            for x in range(cols):
                draw_cell(buf, bpp, size_line, x * CELL, y * CELL,
                          maze[y][x], wall_color, FLOOR_COLOR, format)

        if state["show_entry_exit"]:
            ex, ey = state["entry"]
            draw_cell(buf, bpp, size_line, ex * CELL, ey * CELL, maze[ey][ex], wall_color, ENTRY_COLOR, format)

            ex, ey = state["exit"]
            draw_cell(buf, bpp, size_line, ex * CELL, ey * CELL, maze[ey][ex], wall_color, EXIT_COLOR, format)

        mlx.mlx_put_image_to_window(mlx_ptr, win, img, 0, 0)
        draw_ui()

    def draw_ui():
        status = "ON" if state["show_path"] else "OFF"
        ui_start = rows * CELL
        mlx.mlx_string_put(mlx_ptr, win, 15, ui_start + 20, UI_TEXT_COLOR, "=== A-Maze-ing ===")
        mlx.mlx_string_put(mlx_ptr, win, 15, ui_start + 35, UI_TEXT_COLOR, "1. Re-generate a new maze")
        mlx.mlx_string_put(mlx_ptr, win, 15, ui_start + 50, UI_TEXT_COLOR, f"2. Show/Hide path from entry to exit: {status}")
        mlx.mlx_string_put(mlx_ptr, win, 15, ui_start + 65, UI_TEXT_COLOR, "3. Rotate maze colors")
        mlx.mlx_string_put(mlx_ptr, win, 15, ui_start + 80, UI_TEXT_COLOR, "4. Quit")
        mlx.mlx_string_put(mlx_ptr, win, 15, ui_start + 95, UI_TEXT_COLOR, "Choice (1-4):")

    def loop_hook(param):
        state["frame"] += 1
        if state["show_path"] and state["anim_step"] < len(state["coords"]):
            if state["frame"] % 3 == 0:
                x, y = state["coords"][state["anim_step"]]
                draw_cell(buf, bpp, size_line, x * CELL, y * CELL,
                          maze[y][x], state["wall_colors"][state["wall_index"]], PATH_COLOR, format)
                state["anim_step"] += 1
        mlx.mlx_put_image_to_window(mlx_ptr, win, img, 0, 0)
        draw_ui()
        return 0

    def key_hook(keycode, param):
        ESC = 65307
        KEY_1 = 49
        KEY_2 = 50
        KEY_3 = 51
        KEY_4 = 52

        if keycode == ESC or keycode == KEY_4:
            mlx.mlx_destroy_window(mlx_ptr, win)
            sys.exit(0)
        elif keycode == KEY_1:
            r = parse_config(sys.argv[1])
            generator.main(**vars(r))
            maze, entry, exit_, path = load_maze("maze.txt")
            state.update({
                "maze": maze,
                "entry": entry,
                "exit": exit_,
                "coords": path_to_coords(entry, path),
                "anim_step": 0
            })
            draw_base()
        elif keycode == KEY_2:
            state["show_path"] = not state["show_path"]
            state["show_entry_exit"] = state["show_path"]
            state["anim_step"] = 0
            draw_base()
        elif keycode == KEY_3:
            state["wall_index"] = (state["wall_index"] + 1) % len(state["wall_colors"])
            state["anim_step"] = 0
            draw_base()
        return 0

    draw_base()
    mlx.mlx_key_hook(win, key_hook, None)
    mlx.mlx_loop_hook(mlx_ptr, loop_hook, None)
    mlx.mlx_loop(mlx_ptr)


if __name__ == "__main__":
    main()