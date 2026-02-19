from icecream import ic
from typing import Callable
from enum import Enum


class MazeGenerator:
    maze: dict[tuple, list[int]] = {
        (0,0): [1,0,0,1], (1,0): [1,0,1,0], (2,0): [1,1,0,0], (3,0): [1,0,1,1], (4,0): [1,0,1,0], (5,0): [1,0,0,0], (6,0): [1,1,0,0], (7,0): [1,1,0,1],
        (0,1): [0,1,0,1], (1,1): [1,0,0,1], (2,1): [0,1,1,0], (3,1): [1,0,0,1], (4,1): [1,1,0,0], (5,1): [0,1,1,0], (6,1): [0,0,1,1], (7,1): [0,1,1,1],
        (0,2): [0,0,0,1], (1,2): [0,1,1,0], (2,2): [1,0,0,1], (3,2): [0,1,1,0], (4,2): [0,0,1,1], (5,2): [1,0,0,0], (6,2): [1,1,0,0], (7,2): [1,1,0,1],
        (0,3): [0,1,0,1], (1,3): [1,0,0,1], (2,3): [0,1,1,0], (3,3): [1,0,0,1], (4,3): [1,0,0,0], (5,3): [0,1,1,0], (6,3): [0,0,1,1], (7,3): [0,1,0,1],
        (0,4): [0,0,0,1], (1,4): [0,1,0,0], (2,4): [0,0,0,1], (3,4): [0,1,1,0], (4,4): [0,1,0,1], (5,4): [1,0,0,1], (6,4): [0,1,0,0], (7,4): [0,1,1,1],
        (0,5): [0,1,0,1], (1,5): [0,0,0,0], (2,5): [0,1,0,0], (3,5): [1,0,0,1], (4,5): [0,1,0,0], (5,5): [0,1,1,1], (6,5): [0,0,1,1], (7,5): [1,1,0,1],
        (0,6): [0,0,0,1], (1,6): [0,1,1,0], (2,6): [0,1,1,1], (3,6): [0,0,0,1], (4,6): [0,1,1,0], (5,6): [1,1,0,1], (6,6): [0,1,1,0], (7,6): [0,1,0,1],
        (0,7): [0,1,1,1], (1,7): [1,0,1,1], (2,7): [1,1,1,0], (3,7): [0,0,1,1], (4,7): [1,0,1,0], (5,7): [0,0,1,0], (6,7): [1,0,1,0], (7,7): [1,1,1,0],
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

        ic(path)
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


maze_gen = MazeGenerator()
ic(maze_gen.solve_maze((0, 0), (7, 7)))
