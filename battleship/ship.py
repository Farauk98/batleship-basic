import random

class Ship:
    def __init__(self, size):
        self.size = size
        self.positions = []
        self.hits = 0

    def place_ship(self, board, start_row, start_col, direction):
        """Umieszcza statek na planszy"""
        if direction == "H":
            if start_col + self.size > len(board[0]):
                return False
            for i in range(self.size):
                if board[start_row][start_col + i] != " ":
                    return False
            for i in range(self.size):
                board[start_row][start_col + i] = "S"
                self.positions.append((start_row, start_col + i))
        else:
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
        """Zwraca True, jeśli statek został trafiony"""
        if (row, col) in self.positions:
            self.hits += 1
            return True
        return False

    def is_sunk(self):
        """Zwraca True, jeśli statek został zatopiony"""
        return self.hits == self.size

    def is_demaged(self):
        """Zwraca True, jeśli statek został zatopiony"""
        if self.hits < self.size and self.hits != 0:
            return True
        else:
            return False