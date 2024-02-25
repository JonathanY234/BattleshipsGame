"""
This module provides the functions required for the one player game
And the command line version of the game 'simple_game_loop()'
"""
import components

def read_value(array: list, coords: tuple) -> list:
    """
    This provides a unified way to access 2D arrays
    Note: 
    Originally, this function had additional features, but they were removed, leaving it somewhat redundant.
    """
    #I would like to use numpy arrays but it seems the specification doesnt like that
    column, row = coords
    return array[row][column]
def write_value(array: list, coords: tuple, new_value):
    """
    This also provides a unified way to access 2D arrays
    Note: 
    Originally, this function had additional features, but they were removed, leaving it somewhat redundant.
    """
    column, row = coords
    array[row][column] = new_value
def in_range(tup):
    return all(0 <= element <= 9 for element in tup)
def attack(coordinates: tuple, board: list, ships: dict) -> bool:
    """
    Checks if the coordinates attacked contain a ship.
    Returns:
        bool: True for a hit, False for a miss.
    Note:
        If it's a hit, the function will also remove the ship part that was hit.
    """
    #input validation
    if not isinstance(coordinates, tuple) or len(coordinates) != 2:
        raise ValueError('coordinates must be a tuple with two elements')
    if not in_range(coordinates):
        raise ValueError('coordinates out of range, should be 0 to 9')
    if not isinstance(board, list) and len(board) != 10:
        raise ValueError('board must be a list of length 10')
    for i in board:
        try:
            if len(i) != 10:
                raise ValueError('sub lists of board must be list of length 10')
        except Exception as exc:
            raise ValueError('board must be list of lists') from exc
    if not isinstance(ships, dict):
        raise ValueError(f'ships must be a dictionary, received {type(ships).__name__}')
    for key, value in ships.items():
        if not isinstance(key, str) or not isinstance(value, int) or key is None or value is None:
            raise ValueError('ships dictionary must have str keys and int values and not be None')

    location = read_value(board, coordinates)
    if location is not None:
        write_value(board, coordinates, None)
        ships[location] -= 1
        if ships[location] == 0:
            del ships[location]
            components.hit_and_destroyed = True
            #global variable hack to add this essential battleships feature whilst fitting the spec
        else:
            components.hit_and_destroyed = False
        return True#hit
    return False#Missed

def cli_coordinates_input() -> tuple:
    """
    Requests user input in the form of coordinates
    Contains error handling for an invalid input
    Returns:
        coordinates in the form of a tuple
    """
    while True:
        try:
            coords = input('enter coordinates: ')
            coords = coords.split(',', maxsplit=1)
            coords = (int(coords[0])-1, int(coords[1])-1)
            if 0 <= coords[0] <= 9 and 0 <= coords[1] <= 9:
                return coords
            else:
                print('Invalid Input: Out of Range')
        except ValueError:
            print('Invalid Input: Please enter valid coordinates')
        except IndexError:
            print("Invalid Input: Please enter coordinates in the format 'row,col'")

def hit_or_missed(result):
    """
    Converts True/False inputs to battleships terminology for player
    Also provides 'Hit and Destroyed' output depending on the global variable components.hit_and_destroyed
    Returns:
        str: Human understandable result message
    """
    if result:
        if components.hit_and_destroyed:
            return 'Hit and Destroyed'
        else:
            return 'Hit'
    return 'Missed'
def simple_game_loop():
    """
    Provides working one player command line battleships game

    Player makes guesses against a random opponent board
    Game ends when they destroy all battleships

    There is no opponents guesses or players board because this is single player version
    """
    print("Captain, we are engaged in combat with the enemy fleet. "
        "Choose your target coordinates wisely, and we'll unleash "
        "a devastating salvo upon their position.")
    opponent_board = components.initialise_board()
    opponent_ships = components.create_battleships()
    opponent_board = components.place_battleships(opponent_board, opponent_ships, algorithm='random')
    while opponent_ships:#ends when enemy_ships is false (empty)
        print('your turn____________________________________________')
        result = attack(cli_coordinates_input(), opponent_board, opponent_ships)
        print(hit_or_missed(result))
        components.display_board(opponent_board)
    print('victory')

if __name__ == '__main__':
    simple_game_loop()
