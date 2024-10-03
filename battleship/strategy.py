from abc import ABC, abstractmethod
import random
import sys
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
    # Metoda take_turn jest odpowiedzialna za wykonanie ruchu w grze.
    def take_turn(self):
        # Wybiera losowy strzal, zwracajac wspolrzedne w postaci krotki (wiersz, kolumna).
        row, col = self.select_random_shot()
        # Wykonuje strzal na podstawie wybranych wspolrzednych.
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

class ProbabilityStrategy(Strategy):
    
    def __init__(self, game):
        super().__init__(game)
        self.probability_grid = [[0 for _ in range(self.game.board_size)] for _ in range(self.game.board_size)]
        self.last_hitted = []

    def display_probability_grid(self):        
        print("  " + " ".join([str(i) for i in range(self.game.board_size)]))
        for i in range(self.game.board_size):
            print(str(i) + " " + " ".join([str(self.probability_grid[i][j]) for j in range(self.game.board_size)]))
        

    def update_probability_grid(self):
        # Sprawdza, czy jakikolwiek statek w grze jest uszkodzony.
        if any(ship.is_damaged() for ship in self.game.ships):
            # Aktualizuje macierz, gdy chociaż jeden statek zostal uszkodzony.
            self.update_probability_grid_hitted_ship()
        else:
            # Resetuje liste pol uszkodzonych statków.
            self.last_hitted = []
            # Aktualizuje macierz, gdy zaden statek nie zostal uszkodzone.
            self.update_probability_grid_not_hitted_ship()

    def update_probability_grid_not_hitted_ship(self):
        # Inicjalizuje macierz jako dwuwymiarowa lista zer
        self.probability_grid = [[0 for _ in range(self.game.board_size)] for _ in range(self.game.board_size)]
        # Iteruje przez wszystkie statki w grze
        for ship in self.game.ships:
            # Sprawdza, czy statek nie jest zatopiony
            if not ship.is_sunk():
                size = ship.size
                # Sprawdza poziome umiejscowienia statku
                for row in range(self.game.board_size):
                    for col in range(self.game.board_size - size + 1):
                        # Sprawdza, czy w danej pozycji mozna umiescic statek
                        if all(self.game.board[row][col + i] in [" ", "S"] for i in range(size)):
                            # Zwieksza wartości w macierzy dla kazdej pozycji statku
                            for i in range(size):
                                self.probability_grid[row][col + i] += 1
                # Sprawdza pionowe umiejscowienia statku
                for row in range(self.game.board_size - size + 1):
                    for col in range(self.game.board_size):
                        # Sprawdza, czy w danej pozycji mozna umiescic statek
                        if all(self.game.board[row + i][col] in [" ", "S"] for i in range(size)):
                            # Zwieksza wartości w macierzy dla kazdej pozycji statku
                            for i in range(size):
                                self.probability_grid[row + i][col] += 1

    def update_probability_grid_hitted_ship(self):
        # Inicjalizuje macierz jako dwuwymiarowa lista zer
        self.probability_grid = [[0 for _ in range(self.game.board_size)] for _ in range(self.game.board_size)]
        flag = True
        # Iteruje przez wszystkie statki w grze
        for ship in self.game.ships:
            # Sprawdza, czy statek nie jest zatopiony
            if not ship.is_sunk():
                size = ship.size
                # Sprawdza poziome umiejscowienia statku
                for row in range(self.game.board_size):
                    for col in range(self.game.board_size - size + 1):
                        # Sprawdza, czy ostatnio trafione wspolrzedne sa w danym umiejscowieniu
                        if all(j in [(row, col + i) for i in range(size)] for j in self.last_hitted) and all(self.game.board[row][col + i] in [" ", "S", "X"] for i in range(size)):
                            for i in range(size):
                                # Zwieksza prawdopodobienstwo w macierzy, jesli miejsce nie jest juz trafione
                                if self.game.board[row][col + i] != "X":
                                    self.probability_grid[row][col + i] += 1
                                    flag = False
                # Sprawdza pionowe umiejscowienia statku
                for row in range(self.game.board_size - size + 1):
                    for col in range(self.game.board_size):
                        # Sprawdza, czy ostatnio trafione wspolrzedne sa w danym umiejscowieniu
                        if all(j in [(row + i, col) for i in range(size)] for j in self.last_hitted) and all(self.game.board[row + i][col] in [" ", "S", "X"] for i in range(size)):
                            for i in range(size):
                                # Zwieksza prawdopodobienstwo w macierzy, jesli miejsce nie jest juz trafione
                                if self.game.board[row + i][col] != "X":
                                    self.probability_grid[row + i][col] += 1
                                    flag = False
        # Sprawdza, czy nie bylo zmian w macierzy
        if flag:
            # Ponownie iteruje przez wszystkie statki w grze
            for ship in self.game.ships:
                # Sprawdza, czy statek nie jest zatopiony
                if not ship.is_sunk():
                    size = ship.size

                    # Sprawdza poziome umiejscowienia statku
                    for row in range(self.game.board_size):
                        for col in range(self.game.board_size - size + 1):
                            # Sprawdza, czy ostatnio trafione wspolrzedne sa w danym umiejscowieniu
                            if any((row, col + i) in self.last_hitted for i in range(size)) and all(self.game.board[row][col + i] in [" ", "S", "X"] for i in range(size)):
                                for i in range(size):
                                    # Zwieksza prawdopodobienstwo w macierzy
                                    self.probability_grid[row][col + i] += 1
                    
                    # Sprawdza pionowe umiejscowienia statku
                    for row in range(self.game.board_size - size + 1):
                        for col in range(self.game.board_size):
                            # Sprawdza, czy ostatnio trafione wspolrzedne sa w danym umiejscowieniu
                            if any((row + i, col) in self.last_hitted for i in range(size)) and all(self.game.board[row + i][col] in [" ", "S", "X"] for i in range(size)):
                                for i in range(size):
                                    # Zwieksza prawdopodobienstwo w macierzy
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
        # self.display_probability_grid()
        self.probability_shot()

class ProbabilityChessboardStrategy(ProbabilityStrategy):
    
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
        # Inicjalizacja macierzy na zerowe wartosci
        self.probability_grid = [[0 for _ in range(self.game.board_size)] for _ in range(self.game.board_size)]
        
        # Pierwsza faza, zastosowanie strategii szachownicy na podstawie dzielnika i reszty
        if self.game.shot_count < self.block:
            for ship in self.game.ships:
                # Sprawdzenie, czy statek nie jest zatopiony
                if not ship.is_sunk():
                    size = ship.size
                    # Sprawdzenie poziomych ustawien
                    for row in range(self.game.board_size):
                        for col in range(self.game.board_size - size + 1):
                            # Sprawdzenie, czy wszystkie pola sa puste lub zajete przez statek
                            if all(self.game.board[row][col + i] in [" ", "S"] for i in range(size)):
                                for i in range(size):
                                    # Sprawdzenie reszty dla danego pola
                                    if self.check_remainder(self.divisor, self.remainder, row, (col + i)):
                                        self.probability_grid[row][col + i] += 1
                                        
                    # Sprawdzenie pionowych ustawien
                    for row in range(self.game.board_size - size + 1):
                        for col in range(self.game.board_size):
                            # Sprawdzenie, czy wszystkie pola sa puste lub zajete przez statek
                            if all(self.game.board[row + i][col] in [" ", "S"] for i in range(size)):
                                for i in range(size):
                                    # Sprawdzenie reszty dla danego pola
                                    if self.check_remainder(self.divisor, self.remainder, (row + i), col):
                                        self.probability_grid[row + i][col] += 1
        # Druga faza, zastosowanie normalnej strategii probabilistycznej
        else:
            super().update_probability_grid_not_hitted_ship()


class ProbabilitySmallerRectangleStrategy(ProbabilityStrategy):
    
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