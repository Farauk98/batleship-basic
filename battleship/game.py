import random

from battleship.ship import Ship
from battleship.strategy import Strategy, RandomStrategy, HuntAndTargetStrategy, ProbabilityBetterStrategy, ProbabilityBetterChessboardStrategy, ProbabilityBetterSmallerSquareStrategy

class Game:
    def __init__(self, board_size=10, strategy=None):
        self.board_size = board_size
        self.board = [[" " for _ in range(board_size)] for _ in range(board_size)]
        self.ships = []
        self.shot_count = 0
        self.strategy = strategy(self) if strategy else RandomStrategy(self)
        self.shots = []

    def display_board(self,reveal=False):
        print("  " + " ".join([str(i) for i in range(self.board_size)]))
        for i in range(self.board_size):
            if reveal:
                print(str(i) + " " + " ".join(self.board[i]))
            else:
                print(str(i) + " " + " ".join(["S" if x == "S" else x for x in self.board[i]]))

    def add_ship(self, size):
        ship = Ship(size)
        placed = False
        while not placed:
            direction = random.choice(["H", "V"])
            start_row = random.randint(0, self.board_size - 1)
            start_col = random.randint(0, self.board_size - 1)
            placed = ship.place_ship(self.board, start_row, start_col, direction)
        self.ships.append(ship)

    def take_shot(self, row, col):
        if row < 0 or row >= self.board_size or col < 0 or col >= self.board_size:
            #print("Poza planszą!")
            return False, False

        if self.board[row][col] == "X" or self.board[row][col] == "O":
            #print("Już tutaj strzelałeś!")
            return False, False

        hit = False
        is_sunk = False
        for ship in self.ships:
            if ship.is_hit(row, col):
                #print("Trafiony!")
                self.board[row][col] = "X"
                hit = True
                self.last_hit = (row, col)  # Ustaw ostatnie trafienie
                if ship.is_sunk():
                    is_sunk = True
                break

        if not hit:
            self.board[row][col] = "O"

        return hit, is_sunk

    def is_game_over(self):
        return all(ship.is_sunk() for ship in self.ships)

    def start_game(self, ship_sizes):
        for size in ship_sizes:
            self.add_ship(size)

        while not self.is_game_over():
            self.strategy.take_turn()
            # self.display_board(reveal=True)
            # self.display_board()
        
        # self.display_board(reveal=True)
        # print("ENDGASME")