import random
from battleship.ship import Ship
from battleship.strategy import (Strategy, RandomStrategy, HuntAndTargetStrategy,
                                  ProbabilityStrategy, ProbabilityChessboardStrategy,
                                  ProbabilitySmallerRectangleStrategy)

class Game:
    def __init__(self, board_size=10, strategy=None):
        """
        Inicjalizuje grę.

        Parameters
        ----------
        board_size : int, optional
            Rozmiar planszy (domyślnie 10).
        strategy : Strategy, optional
            Strategia używana w grze (domyślnie RandomStrategy).
        """
        self.board_size = board_size
        self.board = [[" " for _ in range(board_size)] for _ in range(board_size)]
        self.ships = []
        self.shot_count = 0
        self.strategy = strategy(self) if strategy else RandomStrategy(self)
        self.shots = []

    def display_board(self, reveal=False):
        """
        Wyświetla planszę gry.

        Parameters
        ----------
        reveal : bool, optional
            Jeśli True, pokazuje wszystkie statki; jeśli False, ukrywa statki (domyślnie False).
        """
        header = "  " + " ".join(map(str, range(self.board_size)))
        print(header)
        for i in range(self.board_size):
            row = " ".join(self.board[i] if reveal else ["S" if x == "S" else x for x in self.board[i]])
            print(f"{i} {row}")

    def add_ship(self, size):
        """
        Dodaje statek do planszy.

        Parameters
        ----------
        size : int
            Rozmiar statku do dodania.
        """
        ship = Ship(size)
        while not ship.place_ship(self.board, *self.random_position(), random.choice(["H", "V"])):
            pass
        self.ships.append(ship)

    def random_position(self):
        """
        Generuje losową pozycję na planszy.

        Returns
        -------
        tuple
            Krotka z wierszem i kolumną.
        """
        return random.randint(0, self.board_size - 1), random.randint(0, self.board_size - 1)

    def take_shot(self, row, col):
        """
        Wykonuje strzał w podanej pozycji.

        Parameters
        ----------
        row : int
            Wiersz, w którym wykonano strzał.
        col : int
            Kolumna, w której wykonano strzał.

        Returns
        -------
        tuple
            Zwraca krotkę (hit, is_sunk), gdzie hit oznacza, czy strzał trafił,
            a is_sunk, czy statek został zatopiony.
        """
        if not self.is_within_bounds(row, col) or self.is_already_shot(row, col):
            return False, False

        hit, is_sunk = self.check_hit(row, col)
        self.board[row][col] = "X" if hit else "O"
        return hit, is_sunk

    def is_within_bounds(self, row, col):
        """
        Sprawdza, czy podana pozycja jest w obrębie planszy.

        Parameters
        ----------
        row : int
            Wiersz do sprawdzenia.
        col : int
            Kolumna do sprawdzenia.

        Returns
        -------
        bool
            Zwraca True, jeśli pozycja jest w obrębie planszy, w przeciwnym razie False.
        """
        return 0 <= row < self.board_size and 0 <= col < self.board_size

    def is_already_shot(self, row, col):
        """
        Sprawdza, czy w podanej pozycji już oddano strzał.

        Parameters
        ----------
        row : int
            Wiersz do sprawdzenia.
        col : int
            Kolumna do sprawdzenia.

        Returns
        -------
        bool
            Zwraca True, jeśli strzał został już oddany w tej pozycji, w przeciwnym razie False.
        """
        return self.board[row][col] in ["X", "O"]

    def check_hit(self, row, col):
        """
        Sprawdza, czy strzał trafił w jakiś statek.

        Parameters
        ----------
        row : int
            Wiersz, w którym wykonano strzał.
        col : int
            Kolumna, w której wykonano strzał.

        Returns
        -------
        tuple
            Zwraca krotkę (hit, is_sunk), gdzie hit oznacza, czy strzał trafił,
            a is_sunk, czy statek został zatopiony.
        """
        for ship in self.ships:
            if ship.is_hit(row, col):
                self.last_hit = (row, col)
                return True, ship.is_sunk()
        return False, False

    def is_game_over(self):
        """
        Sprawdza, czy gra się skończyła.

        Returns
        -------
        bool
            Zwraca True, jeśli wszystkie statki zostały zatopione, w przeciwnym razie False.
        """
        return all(ship.is_sunk() for ship in self.ships)

    def start_game(self, ship_sizes):
        """
        Rozpoczyna grę z zadanymi rozmiarami statków.

        Parameters
        ----------
        ship_sizes : list
            Lista rozmiarów statków do dodania do planszy.
        """
        for size in ship_sizes:
            self.add_ship(size)

        while not self.is_game_over():
            # self.display_board(reveal=True)
            self.strategy.take_turn()
        # print(f'end {self.shot_count}')
