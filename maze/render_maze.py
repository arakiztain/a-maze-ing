from mlx import Mlx
import time

CELL = 40
WALL_COLOR = 0x000000
FLOOR_COLOR = 0xFFFFFF
ENTRY_COLOR = 0x00FF00
EXIT_COLOR = 0xFF0000
PATH_COLOR = 0x0000FF


def load_maze(path):
    with open(path) as f:
        lines = [line.strip() for line in f if line.strip()]

    maze_lines = lines[:-3]
    entry_line = lines[-3]
    exit_line = lines[-2]
    path_line = lines[-1]

    maze = [[int(c,16) for c in row] for row in maze_lines]
    entry = tuple(map(int, entry_line.split(',')))
    exit_ = tuple(map(int, exit_line.split(',')))
    path = list(path_line.strip())
    return maze, entry, exit_, path


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

def draw_cell(buf, bpp, size_line, x0, y0, cell_value, color=None, format=0):
    if color is None:
        color = FLOOR_COLOR

    for y in range(CELL):
        for x in range(CELL):
            put_pixel(buf, bpp, size_line, x0+x, y0+y, color, format)

    if cell_value & 1:
        for dx in range(CELL):
            put_pixel(buf, bpp, size_line, x0+dx, y0, WALL_COLOR, format)
    if cell_value & 2:
        for dy in range(CELL):
            put_pixel(buf, bpp, size_line, x0+CELL-1, y0+dy, WALL_COLOR, format)
    if cell_value & 4:
        for dx in range(CELL):
            put_pixel(buf, bpp, size_line, x0+dx, y0+CELL-1, WALL_COLOR, format)
    if cell_value & 8:
        for dy in range(CELL):
            put_pixel(buf, bpp, size_line, x0, y0+dy, WALL_COLOR, format)


def path_to_coords(entry, path):
    x, y = entry
    coords = [(x, y)]
    move = {'N': (0,-1), 'E':(1,0), 'S':(0,1), 'W':(-1,0)}
    for step in path:
        dx, dy = move[step]
        x += dx
        y += dy
        coords.append((x,y))
    return coords

def main() -> None:
	maze, entry, exit_, path = load_maze("maze.txt")
	rows = len(maze)
	cols = len(maze[0])
	coords = path_to_coords(entry, path)


	mlx = Mlx()
	mlx_ptr = mlx.mlx_init()
	width = cols*CELL
	height = rows*CELL
	win = mlx.mlx_new_window(mlx_ptr, width, height, "Maze")
	img = mlx.mlx_new_image(mlx_ptr, width, height)
	buf, bpp, size_line, format = mlx.mlx_get_data_addr(img)
	buf = buf.cast('B')


	for y in range(rows):
		for x in range(cols):
			draw_cell(buf, bpp, size_line, x*CELL, y*CELL, maze[y][x], format=format)


	ex, ey = entry
	draw_cell(buf, bpp, size_line, ex*CELL, ey*CELL, maze[ey][ex], ENTRY_COLOR, format=format)
	ex, ey = exit_
	draw_cell(buf, bpp, size_line, ex*CELL, ey*CELL, maze[ey][ex], EXIT_COLOR, format=format)

	# animation
	current_step = [0]
	def loop_hook(param):
		if current_step[0] >= len(coords):
			return 0
		x, y = coords[current_step[0]]
		draw_cell(buf, bpp, size_line, x*CELL, y*CELL, maze[y][x], PATH_COLOR, format=format)
		mlx.mlx_sync(mlx_ptr, 1, img)
		mlx.mlx_put_image_to_window(mlx_ptr, win, img, 0, 0)
		mlx.mlx_sync(mlx_ptr, 3, win)
		current_step[0] += 1
		time.sleep(0.05)
		return 0

	mlx.mlx_loop_hook(mlx_ptr, loop_hook, None)
	mlx.mlx_loop(mlx_ptr)
     
if "__name__" == "__main__":
     main()
