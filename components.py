"""
This module defines some functions used in other modules.
Functions relating to initialising the players.
"""
import random
import json
import logging

def configure_logging(logfile='logfile.txt'):
    """
    Configures logging settings and redirects logs to a file.
    """
    logging.getLogger().setLevel(logging.DEBUG)

    # Create a FileHandler and set its formatter
    file_handler = logging.FileHandler(logfile)
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    # Add the FileHandler to the root logger
    logging.getLogger().addHandler(file_handler)
configure_logging()

def display_board(grid):
    for i in grid:
        print(i)
def initialise_board(size=10):
    return [[None] * size for i in range(size)]
def create_battleships(filename='battleships.txt'):
    ships_dict = {}
    with open(filename, 'r', encoding='utf-8') as file:
        for line in file:
            ship_type, length = line.strip().split(':')
            ships_dict[ship_type] = int(length)
    return ships_dict

def place_battleships(board: list, ships: dict, algorithm='custom', shipdata: str=None) -> list:
    """
    Places the battleships on the board provided
    according to the algorithm selected by 'algorithm' parameter
    """
    #input validation
    if not isinstance(board, list):
        raise ValueError('board must be a list of lists')
    if len(board) != 10:
        raise ValueError("invalid board, Board must have 10 rows")
    for row in board:
        if not isinstance(row, list) or len(row) != 10:
            raise ValueError("invalid board, each row must be a list of 10 columns")
    if not isinstance(ships, dict):
        raise ValueError(f'ships must be a dictionary, received {type(ships).__name__}')
    for key, value in ships.items():
        if not isinstance(key, str) or not isinstance(value, int) or key is None or value is None:
            raise ValueError('ships dictionary must have str keys and int values and not be None')

    if algorithm == 'custom':
        if shipdata is None:
            with open('placement.json', 'r', encoding='utf-8') as file:
                shipdata = json.load(file)

        for ship in ships:
            data = shipdata[ship]
            x = int(data[0])
            y = int(data[1])
            direction = data[2]
            for i in range(ships[ship]):
                if direction == 'h':
                    board[y][x+i] = ship
                elif direction == 'v':
                    board[y+i][x] = ship
                else:
                    raise ValueError("its supposed to be 'v' or 'h'")

    elif algorithm == 'random':
        #I dont belive in the statagy of not letting ships touch, if you can fool players
        #  into leaving part of a ship alive you have basically won the game
        # and even if they do touch players are not really any more likely to find the touching ship
        for ship in ships:
            try_again = True
            while try_again:
                row = random.randint(0, len(board[0]) - 1)
                column = random.randint(0, len(board[0]) - 1)#choose a random start point and direction
                direction = random.randint(0, 2)

                if direction == 0:#across
                    #first check if there is space for the ship
                    if column + ships[ship] <= len(board[0])-1:#bounds check
                        for i in range(ships[ship]):#check for ships in the way
                            if board[row][column+i] is not None:
                                break
                        else:
                            #if loop finds that there is space for the ship in the chosen location add the ship
                            for i in range(ships[ship]):
                                board[row][column+i] = ship
                            try_again = False
                if direction == 1:#down
                    #first check if there is space for the ship
                    if row + ships[ship] <= len(board[0])-1:#bounds check
                        for i in range(ships[ship]):#check for ships in the way
                            if board[row+i][column] is not None:
                                break
                        else:
                            #if loop finds that there is space for the ship in the chosen location add the ship
                            for i in range(ships[ship]):
                                board[row+i][column] = ship
                            try_again = False
    else:
        raise ValueError('invalid algorithm selected')
    return board
if __name__ == '__main__':
    test = initialise_board()
    battleships = create_battleships()
    place_battleships(test, battleships)
    display_board(test)


# pylint: disable=invalid-name
#this is not a constant but pylint thinks it is
hit_and_destroyed = False
