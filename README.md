import time
import matplotlib.pyplot as plt
import numpy as np

from battleship.game import Game
from battleship.strategy import RandomStrategy, HuntAndTargetStrategy, ProbabilityStrategy, ProbabilityChessboardStrategy, ProbabilitySmallerRectangleStrategy


import matplotlib.pyplot as plt

# Define your strategies
strategies = {}
counter=0

for divisor in range(2, 10):
    for remainder in range(0,divisor):
        for block in range(20,80):
            strategies[(divisor,remainder,block)]=lambda game: ProbabilityChessboardStrategy(game, divisor=divisor, remainder=remainder, block=block)
table_of_results = {}  # To store results for each strategy
# Loop through each strategy
for strategy in strategies:
    results = []  # Initialize a list to count shots needed to finish the game
    for _ in range(1000):  # Simulate 10,000 games
        game = Game(board_size=10, strategy=strategies[strategy])  # Initialize the game with a 10x10 board
        game.start_game([2, 3, 3, 4, 5])  # Start the game with given parameters
        results.append(game.shot_count)  # Increment the count for the number of shots taken
    print(strategy)
    print(results)  # Print results for debugging
    table_of_results[strategy]=results
    counter+=1
    # # Plotting the results
    # plt.figure(figsize=(10, 6))
    # plt.plot(results, marker='o', linestyle='-', color='b')
    # plt.title('Histogram of 10,000 Games with Probability Strategy')
    # plt.xlabel('Number of Moves Needed to End the Game')
    # plt.ylabel('Number of Games Finished in That Many Moves')
    # plt.grid(True)
    # plt.show()
