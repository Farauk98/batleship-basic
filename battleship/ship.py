import random

class Ship:
    def __init__(self, size):
        """
        Inicjalizuje statek.

        Parameters
        ----------
        size : int
            Rozmiar statku.
        """
        self.size = size
        self.positions = []
        self.hits = 0

    def place_ship(self, board, start_row, start_col, direction):
        """
        Umieszcza statek na planszy.

        Parameters
        ----------
        board : list
            Plansza, na której ma zostać umieszczony statek.
        start_row : int
            Wiersz, w którym statek ma się rozpocząć.
        start_col : int
            Kolumna, w której statek ma się rozpocząć.
        direction : str
            Kierunek umieszczenia statku, "H" dla poziomego, "V" dla pionowego.

        Returns
        -------
        bool
            Zwraca True, jeśli statek został pomyślnie umieszczony, w przeciwnym razie False.
        """
        if direction == "H":
            if start_col + self.size > len(board[0]):
                return False
            for i in range(self.size):
                if board[start_row][start_col + i] != " ":
                    return False
            for i in range(self.size):
                board[start_row][start_col + i] = "S"
                self.positions.append((start_row, start_col + i))
        else:  # Direction is vertical
            if start_row + self.size > len(board):
                return False
            for i in range(self.size):
                if board[start_row + i][start_col] != " ":
                    return False
            for i in range(self.size):
                board[start_row + i][start_col] = "S"
                self.positions.append((start_row + i, start_col))
        return True

    def is_hit(self, row, col):
        """
        Zwraca True, jeśli statek został trafiony.

        Parameters
        ----------
        row : int
            Wiersz, w którym sprawdzamy trafienie.
        col : int
            Kolumna, w której sprawdzamy trafienie.

        Returns
        -------
        bool
            Zwraca True, jeśli statek został trafiony, w przeciwnym razie False.
        """
        if (row, col) in self.positions:
            self.hits += 1
            return True
        return False

    def is_sunk(self):
        """
        Zwraca True, jeśli statek został zatopiony.

        Returns
        -------
        bool
            Zwraca True, jeśli statek został zatopiony, w przeciwnym razie False.
        """
        return self.hits == self.size

    def is_damaged(self):
        """
        Zwraca True, jeśli statek został uszkodzony.

        Returns
        -------
        bool
            Zwraca True, jeśli statek został uszkodzony (nie zatopiony, ale trafiony), w przeciwnym razie False.
        """
        if self.hits < self.size and self.hits != 0:
            return True
        return False
