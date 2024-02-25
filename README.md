# Battleships

Play Battleships aginst computer and give me high marks for this project.

## Introduction

Battleships program where you play against an AI using a flask web interface.

## Notable Features

AI:
This Version of battleships has a sophisticated AI opponent that tries to combine the best of human and machines abilities to make for a tough opponent (although this is still a game with a lot of luck)
It does not cheat at all and will make assumptions about the state of the game (which ships were sink etc) and these assuptions are sometimes incorrect (but is made to continue working when there are issues). There are a lot of rare edge cases but the code is setup to handle these.
It has 4 modes:
    'random':
        chooses random coordinates to stop the algorithm being deterministic
    'hunt':
        creates a matrix of all possible ship positions to find the most likely spot for a ship to be
        and chooses the highest value
    'target':
        once a ship is found this mode will activate. It attacks the 4 cardinal directions, once a second hit is made it will continue the chain until a hit and destroyed
    'sus':
        When ships are placed next to each other this causes many issues. In some cases it is best to activate 'sus' mode
        This will attack all locations that are next to a the ship/ships that are currently being destryed so no ship parts survive

This AI can complete the game in an average of 50.1 moves. This is calculated by the function test_the_ai(1000) in mp_game_engine.py which runs 1000 games against random boards and prints the mean number of moves to win. It is useful to evaluate if changes to the AI actually improve it.

Automatic Reset:
If the user presses the refresh button in their browser the game will automatically resart so a new game can be played. 
If they return to the placement page they can even change the locations of their ship and restart. All without touching the python backend.

## Getting Started
### Prerequisites

Install python3
Install Dependencies
    pip install flask
    pip install numpy
The lastest version should work but if not see the requirements.txt file

### Installation and Running

Download the battleships_project.zip
Extract the archive
Open terminal at the folder 'battleships_project' or use 'cd' to navigate there
Run: 'python -m main'
Open Web Browser and go to http://127.0.0.1:5000/placement
Start playing Battleships

## Usage / battleships Rules

In the game of battleships both players place 5 battleships on their own 10x10 grid, ships cannot overlap.
They then take turns guessing coordinates shooting the unseen location and the opponent responds 'hit' if the shpt
contains a battleship, 'hit and destroyed' if all parts of a ship have been shot and 'miss' if there is no battleship.
Once 1 players battleships have all been 'hit and destroyed' the game is over and the other player is the winner

Start by placing the ships using the mouse: Left click to place, R to rotate ship
Once all Ships are placed press 'send game' and start making attacks on the larger board, red represents 'hit' and blue is 'miss',
the opponent will make their own random ship board and take turns attacking your board. The game will end when there is a winner.

# testing

Install pytest: pip install pytest
To run tests open terminal in battleships_project folder and run pytest tests/
I wanted to setup my project with the proper package structure but it broke the tests and as I cant modify your extra tests I had to revert back to the improper structure.

## Acknowledgements

Exter University ECM1400
Especially Matt Collison and Billy

## License

This project is licensed under the terms of the [MIT License](LICENCE) - see the LICENCE file for details.
