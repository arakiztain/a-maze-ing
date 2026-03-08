from mazegen.MazeGenerator import MazeGenerator
import random
from output_validator import validate_output
from icecream import ic


mg = MazeGenerator()
outputs = []

for _ in range(20):
    width = random.randint(2, 40)
    height = random.randint(2, 30)
    entry = (random.randint(0, width - 1), random.randint(0, height - 1))
    exit_coor = (random.randint(0, width - 1), random.randint(0, height - 1))
    ic(width, height, )
    mg.generate(
        width,
        height,
        random.choice([True, False]),
        random.randint(0, 999999),
        (0, 0),
        (width - 1, height - 1),
        "maze.txt"
    )
    outputs.append(mg.output)


for output in outputs:
    with open("maze.txt", 'w') as f:
        f.write(output)
    ic(validate_output("maze.txt"))
