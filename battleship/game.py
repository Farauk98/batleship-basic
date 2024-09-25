import random
from battleship.ship import Ship
from battleship.strategy import (Strategy, RandomStrategy, HuntAndTargetStrategy,
                                  ProbabilityBetterStrategy, ProbabilityBetterChessboardStrategy,
                                  ProbabilityBetterSmallerSquareStrategy)


class Game:
    def __init__(self, board_size=10, strategy=None):
        self.board_size = board_size
        self.board = [[" " for _ in range(board_size)] for _ in range(board_size)]
        self.ships = []
        self.shot_count = 0
        self.strategy = (strategy(self) if strategy else RandomStrategy(self))
        self.shots = []

    def display_board(self, reveal=False):
        header = "  " + " ".join(map(str, range(self.board_size)))
        print(header)
        for i in range(self.board_size):
            row = " ".join(self.board[i] if reveal else ["S" if x == "S" else x for x in self.board[i]])
            print(f"{i} {row}")

    def add_ship(self, size):
        ship = Ship(size)
        while not ship.place_ship(self.board, *self.random_position(), random.choice(["H", "V"])):
            pass
        self.ships.append(ship)

    def random_position(self):
        return random.randint(0, self.board_size - 1), random.randint(0, self.board_size - 1)

    def take_shot(self, row, col):
        if not self.is_within_bounds(row, col) or self.is_already_shot(row, col):
            return False, False

        hit, is_sunk = self.check_hit(row, col)
        self.board[row][col] = "X" if hit else "O"
        return hit, is_sunk

    def is_within_bounds(self, row, col):
        return 0 <= row < self.board_size and 0 <= col < self.board_size

    def is_already_shot(self, row, col):
        return self.board[row][col] in ["X", "O"]

    def check_hit(self, row, col):
        for ship in self.ships:
            if ship.is_hit(row, col):
                self.last_hit = (row, col)
                return True, ship.is_sunk()
        return False, False

    def is_game_over(self):
        return all(ship.is_sunk() for ship in self.ships)

    def start_game(self, ship_sizes):
        for size in ship_sizes:
            self.add_ship(size)

        while not self.is_game_over():
            self.strategy.take_turn()