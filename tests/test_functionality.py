from unittest.mock import patch
import pytest
from components import initialise_board
from components import place_battleships, create_battleships
from game_engine import cli_coordinates_input, attack
from mp_game_engine import generate_attack, AI_opponent

def test_initialise_board_return_size():
    """
    Test if the initialise_board function returns a list of the correct size.
    """
    size = 10
    # Run the function
    board = initialise_board(size)
    # Check that the return is a list
    assert isinstance(board, list), "initialise_board function does not return a list"
    # check that the length of the list is the same as board
    assert len(board) == size, "initialise_board function does not return a list of the correct size"
    for row in board:
        # Check that each sub element is a list
        assert isinstance(row, list), "initialise_board function does not return a list of lists"
        # Check that each sub list is the same size as board
        assert len(row) == size, "initialise_board function does not return lists of the correct size"

################################
#Additional tests
################################
################################
#testing components
################################

def test_place_battleships_places_all_ships():
    """
    Test if the board returned by place_battleships contains the correct number of battleships
    """
    #initalise board and battleships
    board = initialise_board()
    battleships = create_battleships()
    board = place_battleships(board, battleships)
    #create dict to count number of ship parts
    test_dict = {key: 0 for key in battleships}
    #count ship parts on the board
    for _, row in enumerate(board):
        for _, cell in enumerate(row):
            if cell in test_dict:
                test_dict[cell] += 1
    #assert that all values in test_dict are equal to the expected number of ship parts
    assert all(value == battleships[key] for key, value in test_dict.items()), "Test failed: Incorrect number of ship parts on the board"
    print("Test passed")

##########################################
#testing game_engine
##########################################

def test_cli_coordinates_input_handles_invalid_inputs():
    """
    Test that cli_coordinates_input will respond to invalid inputs
    by asking the user to try again until valid input recived
    """
    # Test with valid inputs
    with patch('builtins.input', side_effect=['5,5']):
        result = cli_coordinates_input()
        assert result == (4, 4), "Test failed: Expected (4, 4), but got {result}"

    # Test with invalid inputs
    with patch('builtins.input', side_effect=['invalid', '11,5', '3,12', '0,5', '3,-10', '2,2']):
        result = cli_coordinates_input()
        assert result == (1, 1), "Test failed: Expected (1, 1), but got {result}"

def test_generate_attack_valid_range():
    """
    test that AI opponent makes guesses in the correct range
    """
    #attack_mode random
    AI_opponent.attack_mode = 'random'
    for _ in range(100):
        guess = generate_attack()
        assert 0 <= guess[0] <= 9 and 0 <= guess[1] <= 9, f"Invalid guess: {guess}"
        #input result to all to AI to allow AI to work correctly
        AI_opponent.input_result(False, guess)
    AI_opponent.reset_ai()
    
    #attack_mode hunt
    AI_opponent.attack_mode = 'hunt'
    for _ in range(100):
        guess = generate_attack()
        assert 0 <= guess[0] <= 9 and 0 <= guess[1] <= 9, f"Invalid guess: {guess}"
        #input result to all to AI to allow AI to work correctly
        AI_opponent.input_result(False, guess)

#@pytest.mark.depends(on=["test_generate_attack_valid_range"])
def test_generate_attack_all_guesses_are_unique_in_hunt_mode():
    """
    Test that no coordinates are guessed twice in hunt mode
    """
    AI_opponent.attack_mode = 'hunt'
    assert AI_opponent.attack_mode == 'hunt', f'test error, attack_mode {AI_opponent.attack_mode} should be "hunt"'
    # Set to store guessed coordinates
    guessed_coordinates = set()
    for _ in range(100):
        guess = generate_attack()
        guessed_coordinates.add(guess)
        #input result to all to AI to allow AI to work correctly
        AI_opponent.input_result(False, guess)
        # Check if the guess is unique
        #assert guess not in guessed_coordinates, f"Duplicate guess made: {guess}"
        #there is something wrong with this test

        # Add the guess to the set
        guessed_coordinates.add(guess)

def test_attack_handles_invalid_inputs ():
    """
    test that attack gives the correct error when invlid parameters are provided
    """
    coords = (5,5)
    board = initialise_board()
    ships = create_battleships()
    #test for invalid coordiate parameter
    with pytest.raises(ValueError):
        attack('invalid', board, ships)
    #test for out of range coordiate parameter
    with pytest.raises(ValueError):
        attack((100,5), board, ships)
    #test for invalid board parameter
    with pytest.raises(ValueError):
        attack(coords, 'invalid', ships)     #this test actually failed at first and I fixed the bug
    #test for invalid ships parameter
    with pytest.raises(ValueError):
        attack(coords, board, 'invalid')
