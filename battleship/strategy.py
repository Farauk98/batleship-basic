from abc import ABC, abstractmethod
import random

class Strategy(ABC):
    def __init__(self, game):
        self.game = game

    @abstractmethod
    def take_turn(self):
        pass

    def select_random_shot(self):
        while True:
            row = random.randint(0, self.game.board_size - 1)
            col = random.randint(0, self.game.board_size - 1)
            if (row, col) not in self.game.shots:
                return row, col

    def add_adjacent_targets(self, row, col):
        """Adds adjacent targets to the target stack."""
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]  # Right, left, down, up
        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            if (0 <= new_row < self.game.board_size and 0 <= new_col < self.game.board_size and
                    (new_row, new_col) not in self.game.shots and (new_row, new_col) not in self.target_stack):
                self.target_stack.append((new_row, new_col))

    def perform_shot(self, row, col):
        self.game.shots.append((row, col))
        hit, is_sunk = self.game.take_shot(row, col)
        self.game.shot_count += 1
        return hit, is_sunk

class RandomStrategy(Strategy):
    def take_turn(self,x):
        row, col = self.select_random_shot()
        self.perform_shot(row, col)

class HuntAndTargetStrategy(RandomStrategy):
    def __init__(self, game):
        super().__init__(game)
        self.hunt_mode = True
        self.target_stack = []

    def take_turn(self):
        if self.hunt_mode:
            row, col = self.select_random_shot()
            hit, _ = self.perform_shot(row, col)
            if hit:
                self.add_adjacent_targets(row, col)
                self.hunt_mode = False
        else:
            self.target_shot()

    def target_shot(self):
        if self.target_stack:
            row, col = self.target_stack.pop()
            if (row, col) not in self.game.shots:
                hit, is_sunk = self.perform_shot(row, col)
                if hit:
                    self.add_adjacent_targets(row, col)

                if is_sunk:
                    self.target_stack.clear()
                    self.hunt_mode = True
                elif not self.target_stack:
                    self.hunt_mode = True

class ProbabilityBetterStrategy(Strategy):
    
    def __init__(self, game):
        super().__init__(game)
        self.hunt_mode = True
        self.target_stack = []
        self.probability_grid = [[0 for _ in range(self.game.board_size)] for _ in range(self.game.board_size)]
        self.last_hitted = []

    def display_probability_grid(self):        
        print("  " + " ".join([str(i) for i in range(self.game.board_size)]))
        for i in range(self.game.board_size):
            print(str(i) + " " + " ".join([str(self.probability_grid[i][j]) for j in range(self.game.board_size)]))
        
    def check_tuples(self,lst):
        first_positions = {t[0] for t in lst}  # Zbiór wartości pierwszej pozycji
        second_positions = {t[1] for t in lst}  # Zbiór wartości drugiej pozycji
        return len(first_positions) == 1 or len(second_positions) == 1

    def update_probability_grid(self):
        if any(ship.is_demaged() for ship in self.game.ships):
            # print("ship.is_demaged")
            self.update_probability_grid_hitted_ship()
            return
        else:
            self.last_hitted = []
            # print("ship.is_not_demaged")
            self.update_probability_grid_not_hitted_ship()

    def update_probability_grid_not_hitted_ship(self):
        self.probability_grid = [[0 for _ in range(self.game.board_size)] for _ in range(self.game.board_size)]
        for ship in self.game.ships:
            if not ship.is_sunk():
                size = ship.size
                # Check horizontal placements
                for row in range(self.game.board_size):
                    for col in range(self.game.board_size - size + 1):
                        if all(self.game.board[row][col + i] in [" ", "S"] for i in range(size)):
                            for i in range(size):
                                self.probability_grid[row][col + i] += 1
                # Check vertical placements
                for row in range(self.game.board_size - size + 1):
                    for col in range(self.game.board_size):
                        if all(self.game.board[row + i][col] in [" ", "S"] for i in range(size)):
                            for i in range(size):
                                self.probability_grid[row + i][col] += 1

    def update_probability_grid_hitted_ship(self):
        self.probability_grid = [[0 for _ in range(self.game.board_size)] for _ in range(self.game.board_size)]
        # print(self.last_hitted)
        if self.check_tuples(self.last_hitted):
            for ship in self.game.ships:
                if not ship.is_sunk():
                    size = ship.size
                    # Check horizontal placements
                    for row in range(self.game.board_size):
                        for col in range(self.game.board_size - size + 1):
                            if all(j in [(row, col + i) for i in range(size)] for j in self.last_hitted) and all(self.game.board[row][col + i] in [" ", "S", "X"] for i in range(size)):
                                for i in range(size):
                                    if self.game.board[row][col +i ] != "X":
                                        self.probability_grid[row][col + i] += 1

                    # Check vertical placements
                    for row in range(self.game.board_size - size + 1):
                        for col in range(self.game.board_size):
                            if all(j in [(row+i, col ) for i in range(size)] for j in self.last_hitted) and all (self.game.board[row + i][col] in [" ", "S", "X"] for i in range(size)):
                                for i in range(size):
                                    if self.game.board[row + i][col] != "X":
                                        self.probability_grid[row + i][col] += 1
        else:
            for ship in self.game.ships:
                if not ship.is_sunk():
                    size = ship.size

                    # Check horizontal placements
                    for row in range(self.game.board_size):
                        for col in range(self.game.board_size - size + 1):
                            if any((row, col + i) in self.last_hitted for i in range(size)) and all(self.game.board[row][col + i] in [" ", "S", "X"] for i in range(size)):
                                for i in range(size):
                                    self.probability_grid[row][col + i] += 1
                    
                    # Check vertical placements
                    for row in range(self.game.board_size - size + 1):
                        for col in range(self.game.board_size):
                            if any((row+i, col) in self.last_hitted for i in range(size)) and all (self.game.board[row + i][col] in [" ", "S", "X"] for i in range(size)):
                                for i in range(size):
                                    self.probability_grid[row + i][col] += 1

    def probability_shot(self):
        max_prob = -1
        target_cell = None
        
        for row in range(self.game.board_size):
            for col in range(self.game.board_size):
                if (row, col) not in self.game.shots and self.probability_grid[row][col] > max_prob:
                    max_prob = self.probability_grid[row][col]
                    target_cell = (row, col)
        
        if target_cell:
            row, col = target_cell
            hit, _ = self.perform_shot(row, col)
            if hit:
                self.last_hitted.append((row, col))
            return hit

    def take_turn(self):
        self.update_probability_grid()
        self.probability_shot()

class ProbabilityBetterChessboardStrategy(ProbabilityBetterStrategy):
    
    def __init__(self, game, divisor, remainder, block):
        super().__init__(game)
        self.block = block
        self.divisor = divisor
        self.remainder = remainder

    def check_remainder(self, divisor, remainder, num1, num2):
        # Calculate the sum of the two numbers
        total = num1 + num2
        
        # Calculate the remainder of the sum divided by the divisor
        total_remainder = total % divisor
        
        # Check if the calculated remainder is equal to the provided remainder
        if total_remainder == remainder:
            return True
        else:
            return False

    def update_probability_grid_not_hitted_ship(self):
        self.probability_grid = [[0 for _ in range(self.game.board_size)] for _ in range(self.game.board_size)]
        
        # First phase, apply chessboard strategy based on divisor and remainder
        if self.game.shot_count < self.block:
            for ship in self.game.ships:
                if not ship.is_sunk():
                    size = ship.size
                    # Check horizontal placements
                    for row in range(self.game.board_size):
                        for col in range(self.game.board_size - size + 1):
                            if all(self.game.board[row][col + i] in [" ", "S"] for i in range(size)):
                                for i in range(size):
                                    if self.check_remainder(self.divisor, self.remainder, row, (col + i)):
                                        self.probability_grid[row][col + i] += 1
                                        
                    # Check vertical placements
                    for row in range(self.game.board_size - size + 1):
                        for col in range(self.game.board_size):
                            if all(self.game.board[row + i][col] in [" ", "S"] for i in range(size)):
                                for i in range(size):
                                    if self.check_remainder(self.divisor, self.remainder, (row + i), col):
                                        self.probability_grid[row + i][col] += 1
        # Second phase, apply the normal strategy
        else:
            super().update_probability_grid_not_hitted_ship()

class ProbabilityBetterSmallerSquareStrategy(ProbabilityBetterStrategy):
    
    def __init__(self, game, top_left_corner, lower_right_corner, block):
        super().__init__(game)
        self.block = block
        self.top_left_corner = top_left_corner
        self.lower_right_corner = lower_right_corner

    def check_requirements(self, top_left_corner, lower_right_corner, position):
        x1, y1 = top_left_corner
        x2, y2 = lower_right_corner
        x3, y3 = position

        return x1 < x3 < x2 and y1 < y3 < y2

    def update_probability_grid_not_hitted_ship(self):
        self.probability_grid = [[0 for _ in range(self.game.board_size)] for _ in range(self.game.board_size)]
        
        # First phase, apply chessboard strategy based on divisor and remainder
        if self.game.shot_count < self.block:
            for ship in self.game.ships:
                if not ship.is_sunk():
                    size = ship.size
                    # Check horizontal placements
                    for row in range(self.game.board_size):
                        for col in range(self.game.board_size - size + 1):
                            if all(self.game.board[row][col + i] in [" ", "S"] for i in range(size)):
                                for i in range(size):
                                    if self.check_requirements(self.top_left_corner, self.lower_right_corner, (row,col+i)):
                                        self.probability_grid[row][col + i] += 1
                                        
                    # Check vertical placements
                    for row in range(self.game.board_size - size + 1):
                        for col in range(self.game.board_size):
                            if all(self.game.board[row + i][col] in [" ", "S"] for i in range(size)):
                                for i in range(size):
                                    if self.check_requirements(self.top_left_corner, self.lower_right_corner, (row + i,col)):
                                        self.probability_grid[row + i][col] += 1
        # Second phase, apply the normal strategy
        else:
            super().update_probability_grid_not_hitted_ship()