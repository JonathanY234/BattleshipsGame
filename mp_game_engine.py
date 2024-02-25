"""
Provides command line two player battleships game ai_opponent_game_loop()
AIOpponent class to store methods and attributes to make advanced battleships AI
THE AI DOES NOT CHEAT

Contains function test_the_ai(x) that runs x games
and prints the mean guesses to win to test the capability of the AI
"""
import copy
import random
import logging
import numpy as np
import components
from game_engine import read_value, write_value, hit_or_missed, cli_coordinates_input
from game_engine import attack, in_range

from components import configure_logging
configure_logging()
# pylint: disable=attribute-defined-outside-init
# disabling warning because class variables deliberately defined in reset_ai
# so the class can be reset on game replay
class AIOpponent():
    """
    Contains all methods and attributes to make best the battleships guesses
    Will make guesses about the state of the game based on the information it has
    and these guesses are not always coorect

    input_result() informs the AI of the result of its last 'attack' to update internal attributes
    reset_ai() sets AI to base state to make guesses for a new game
    choose_attack() returns the coordinates of the next guess
    The other methods support the main methods
    """
    def __init__(self):
        self.reset_ai()
    def reset_ai(self):
        """
        Sets all attributes to base state
        Should be called when starting a new game
        """
        self.estimated_attack_record = [[0] * 10 for _ in range(10)]
        self.attack_mode = 'random'
        self.estimated_ships_remaining = components.create_battleships()
        self.injured_ship = []
        logging.info("AI opponent restarted")
    def input_result(self, result: bool, location: tuple) -> None:
        """
        Recives result and updates internal attributes:
        attack_mode
        injured_ship: list of spaces hit but not destroyed
        estimated_attack_record: record of previous hits and their result
            -1 is missed
            -2 is hit
            -3 is hit and destroyed (assumed)
            0 is not attacked yet
        """
        if result:
            if components.hit_and_destroyed and self.attack_mode != 'sus':
                self.injured_ship.append(location)
                if len(self.injured_ship) > max(self.estimated_ships_remaining.values()):
                    logging.info("something sus happened ship is too long")
                    # I found through testing it is best not to enter 'sus' mode in this situation
                    # as the normal mechanism does better on average
                for i in self.injured_ship:
                    write_value(self.estimated_attack_record, i, -3)
                self.attack_mode = 'hunt'
                logging.debug("entering hunt mode")
                self.injured_ship = []
            else:#hit but not destroyed
                self.injured_ship.append(location)
                write_value(self.estimated_attack_record, location, -2)
                if self.attack_mode != 'sus':
                    self.attack_mode = 'target'
                    logging.debug("entering target mode")
        else:#missed
            write_value(self.estimated_attack_record, location, -1)

    def get_ship_surroundings(self):
        """
        This is used only choose attack when in 'sus' mode
        returns a list of coordinates surrounding previous hits
        """
        matrix = copy.deepcopy(self.estimated_attack_record)
        rows = 10
        columns = 10
        #Define possible moves (up, down, left, right)
        moves = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        result = []
        for i in range(rows):
            for j in range(columns):
                if matrix[i][j] == -2:
                    for move in moves:
                        new_i, new_j = i + move[0], j + move[1]
                        # Check if the new coords are within the matrix bounds and have a value of 0
                        if 0 <= new_i < rows and 0 <= new_j < columns and matrix[new_i][new_j] == 0:
                            #add the location to the return list
                            result.append((new_j, new_i))
        return result

    def increment_ship_probability(self, ship_probability_array, coordinates):
        new_value = read_value(ship_probability_array, coordinates) + 1
        write_value(ship_probability_array, coordinates, new_value)
        return ship_probability_array
    def check_for_obstruction(self, ship_length, row, column, direction, ship_probability_array):
        if direction == 0:#vertical
            if column+ship_length > 10:#confirm ship wont go off the edge of grid
                return False
            for j in range(ship_length):#check for obstructions of previous attacks
                if read_value(ship_probability_array, (row, column+j)) < 0:
                    return False
        elif direction == 1:#horizontal
            if row+ship_length > 10:#confirm ship wont go off the edge of grid
                return False
            for j in range(ship_length):#check for obstructions of previous attacks
                if read_value(ship_probability_array, (row+j, column)) < 0:
                    return False
        return True
    def make_ship_probability_array(self, set_blank: list = None) -> list:
        """
        This function will find all valid placements for all the opponents ships estimated
        to be still alive and increment each location where a valid ship can be placed
        thus ship_probability_array is formed, showing the most and least likely location for a 
        ship to be in.

        Optional 'set_blank' sets specified locations to O before main part of function
        this is used when ships should not be obstructed by themselves.
        set_black in a list of tuples

        In ship_probability_array negative numbers represent:
        -1 is miss
        -2 is hit
        -3 is hit and destroyed (assumed)
        positive numbers are number of different ships that can be placed there

        Returns:
            list: ship_probability_array (2D list)
        """
        if len(self.estimated_ships_remaining) == 0:
            #fixes edge case: self.estimated_ships_remaining can be incorrect
            #this stops this causing major issues
            logging.info("AI estimated all ships sunk, but that must be incorrect, but situation handled")
            self.estimated_ships_remaining['extra_ship'] = 2

        #start from copy of the record of previous attacks
        ship_probability_array = copy.deepcopy(self.estimated_attack_record)

        if set_blank is not None:
            for location in set_blank:
                write_value(ship_probability_array, location, 0)

        for row in range(10):
            for column in range(10):
                #ships vertical
                for ship_length in self.estimated_ships_remaining.values():
                    if self.check_for_obstruction(ship_length, row, column, 0, ship_probability_array):
                        for i in range(ship_length):
                            ship_probability_array = self.increment_ship_probability(ship_probability_array, (row, column+i))
                #ships horizontal
                for ship_length in self.estimated_ships_remaining.values():
                    if self.check_for_obstruction(ship_length, row, column, 1, ship_probability_array):
                        for i in range(ship_length):
                            ship_probability_array = self.increment_ship_probability(ship_probability_array, (row+i, column))
        #components.display_board(ship_probability_array)
        return ship_probability_array
    def choose_attack(self) -> tuple[int, int]:
        """
        This function will return the AIs next guess as a tuple
        it is only called by the wrapper function 'generate_attack()'

        Working depend on attribute 'attack_mode':
        - 'random': Used for the first few turns, makes random guesses to avoid determinism
        - 'hunt': Used to find ships, returns the highest probability location from make_ship_probability_array()
        - 'target': Used to finish off ships once they are found, searches cardinal directions 
                around the first hit, once a second hit is made it will continue attacking 
                in that direction until hit and destroyed
        - 'sus': ships placed next to each other causes all sorts of issues for battleships AI
                Activated when a ship chain does not end with hit_and_destroyed.
                Attacks all spaces next to a previous hit using method get_ship_surroundings()
        """
        match self.attack_mode:
            case 'random':
                if random.randint(0,2) == 0:
                    self.attack_mode = 'hunt'
                    logging.info("entering 'hunt' mode")
                return tuple(np.random.randint(0, 10, size=2))
                #this stops the AI being deterministic and therefore easy to beat
            case 'hunt':
                ship_probability_array = self.make_ship_probability_array()
                numpy_array = np.array(ship_probability_array)
                max_index = np.unravel_index(np.argmax(numpy_array), numpy_array.shape)
                max_index = (max_index[1], max_index[0])
                return max_index
                #chooses the most likly spot to have a ship given past shots
            case 'target':
                #when got one hit try to find the rest of the ship
                if len(self.injured_ship) == 1:#choose the most likly of the 4 cardinal directions from original hit
                    a, b = self.injured_ship[0]
                    neighbors = [(a, b + 1),
                                 (a, b - 1),
                                 (a + 1, b),
                                 (a - 1, b)]
                    ship_probability_array = self.make_ship_probability_array(set_blank=[(a,b)])

                    valid_neighbors = [(x, y) for x, y in neighbors if 0 <= x <= 9 and 0 <= y <= 9]
                    max_coordinates = max(valid_neighbors, key=lambda coords: read_value(ship_probability_array, coords))

                    max_value = read_value(ship_probability_array, max_coordinates)
                    #print('max_coordinates', max_coordinates)
                    #print('max value:', read_value(ship_probability_array, max_coordinates))
                    if max_value < 0:#this is for edge case when finding part of damaged ship
                        min_coordinates = min(valid_neighbors, key=lambda coords: read_value(ship_probability_array, coords))
                        self.injured_ship.append(min_coordinates)

                        return AI_opponent.choose_attack()

                    return max_coordinates
                else:#compare first hit with the last one and continue in that direction
                    a = np.sign(self.injured_ship[-1][0] - self.injured_ship[0][0])
                    b = np.sign(self.injured_ship[-1][1] - self.injured_ship[0][1])#calculates direction of injured ship

                    #normal case
                    target = (self.injured_ship[-1][0]+a, self.injured_ship[-1][1]+b)
                    if in_range(target) and read_value(self.estimated_attack_record, target) == 0:
                        return target

                    #edge case: a hit is blocking a ship but it may be part of current ship
                    #need to hit the next spot along
                    target = (self.injured_ship[-1][0]+2*a, self.injured_ship[-1][1]+2*b)
                    if in_range(target) and read_value(self.estimated_attack_record, target) == -3:
                        return target

                    #next spot obstructed need to try the other end of the ship
                    #normal case
                    target = (self.injured_ship[0][0]-a, self.injured_ship[0][1]-b)
                    if in_range(target) and read_value(self.estimated_attack_record, target) == 0:
                        return target
                    
                    #edge case: a hit is blocking a ship but it may be part of current ship
                    #need to hit the next spot along
                    target = (self.injured_ship[-1][0]-2*a, self.injured_ship[-1][1]-2*b)
                    if in_range(target) and read_value(self.estimated_attack_record, target) == -3:
                        return target
                    
                    #both ends obstructed
                    self.attack_mode = 'sus'
                    logging.info('entering sus mode')
                    #this is info intentionally as sus mode is more rare and inportant
                    return AI_opponent.choose_attack()

            case 'sus':
                positions = self.get_ship_surroundings()
                if len(positions) == 0:#empty
                    self.attack_mode = 'hunt'
                    logging.debug('entering hunt mode')
                    for i in self.injured_ship:
                        write_value(self.estimated_attack_record, i, -3)
                    return AI_opponent.choose_attack()
                else:#at least one value in 'positions'
                    ship_probability_array = self.make_ship_probability_array(set_blank=positions)
                    highest_probability = -4
                    best_coordinate = None
                    for position in positions:
                        # Calculate the value in self.ship_probability_array using read_value
                        probability = read_value(ship_probability_array, position)
                        # Update if the current probability is higher than the highest recorded
                        if probability > highest_probability:
                            highest_probability = probability
                            best_coordinate = position
                    return best_coordinate

def generate_attack() -> tuple:
    """
    this is a wrapper function to ensure the code fits the very specific specification whilst using
    a class to enable acccess to specific variables enabling the function to be more intelligent

    If this funtion is failing automated tests its likely that the class has not been instantiated

    It returns the coordinates of the AI opponents guess
    """
    return AI_opponent.choose_attack()

def ai_opponent_game_loop():
    """
    Runs full command line battleships game
    With player vs AI opponent
    """
    number_of_guesses = 0

    board = components.initialise_board()
    battleships = components.create_battleships()
    board = components.place_battleships(board, battleships, algorithm='custom')
    players['player'] = [board, battleships]
    board = components.initialise_board()
    battleships = components.create_battleships()
    board = components.place_battleships(board, battleships, algorithm='random')
    players['opponent'] = [board, battleships]
    print("Captain, we are engaged in combat with the enemy fleet. "
        "Choose your target coordinates wisely, and we'll unleash "
        "a devastating salvo upon their position.")
    while players['opponent'][1] and players['player'][1]:#ends when either ships is false (empty)
        print('your turn____________________________________________')
        target = cli_coordinates_input()
        result = attack(target, players['opponent'][0],players['opponent'][1])
        print(hit_or_missed(result))
        print('enemy turn____________________________________________')
        target = generate_attack()
        result = attack(target, players['player'][0],players['player'][1])
        #opponent.input_result(result, target)
        AI_opponent.input_result(result, target)
        print('AI attacked', (target[0]+1, target[1]+1))
        print(hit_or_missed(result))
        #components.display_board(opponent.attack_record)
        number_of_guesses += 1
    print('victory')
    print('guesses', number_of_guesses)
    components.display_board(AI_opponent.estimated_attack_record)

def test_the_ai(times: int):
    """
    Makes the AI play play battleships against random boards
    'times' controls the number of games run
    Records the number of guesses required to win and prints the mean
    Used to evaluate if changes to the AI actually improve it
    """
    games = []
    for _ in range(times):
        number_of_guesses = 0
        board = components.initialise_board()
        battleships = components.create_battleships()
        board = components.place_battleships(board, battleships, algorithm='random')
        players['player'] = [board, battleships]
        AI_opponent.reset_ai()
        while len(players['player'][1]) > 0:
            target = generate_attack()
            result = attack(target, players['player'][0],players['player'][1])
            AI_opponent.input_result(result, target)
            number_of_guesses += 1
        games.append(number_of_guesses)
    print(games)
    print(sum(games)/times)

players = {}#why do you make me do it this way??
AI_opponent = AIOpponent()


if __name__ == '__main__':
    #ai_opponent_game_loop()
    test_the_ai(1000)


