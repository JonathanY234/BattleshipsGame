"""
Runs the full game with the flask GUI
"""
import copy
from flask import Flask, render_template, request, jsonify

from mp_game_engine import AI_opponent, players, generate_attack
from game_engine import attack
import components

import logging
from components import configure_logging
configure_logging()

app = Flask(__name__)

def setup_game():
    """
    Sets all game variables to their default state
    Is called when a new game is started like when the browser is refreshed
    This means you can play many games of battleships without restarting the python backend
    """
    AI_opponent.reset_ai()#the AIs data needs clearing to restart a new game
    board = components.initialise_board()
    battleships = components.create_battleships()
    board = components.place_battleships(board, battleships, algorithm='random')
    players['opponent'] = [board, battleships]
    players['player'] = copy.deepcopy(players['playercopy'])#this can be restored when player restarts


@app.route('/placement', methods=['GET', 'POST'])
def placement_interface():
    """
    Provides the interface with the placement webpage
    """
    if request.method == 'GET':
        return render_template('placement.html', ships=components.create_battleships() , board_size=10)
    elif request.method == 'POST':
        try:
            data = request.get_json()
            logging.info('server recieved valid ships')
        except ValueError:
            logging.info('invalid ships sent to server')
            response = jsonify({"message": "You didnt place all the ships idiot"}), 400
            return response
        board = components.initialise_board()
        battleships = components.create_battleships()
        board = components.place_battleships(board, battleships, algorithm='custom', shipdata=data)
        players['playercopy'] = [board, battleships]#allow for restarting the game
        return jsonify({'message': 'Received'}), 200

@app.route('/', methods=['GET'])
def root():
    """
    Starts the main game
    """
    if request.method == 'GET':

        setup_game()
        logging.info('starting main game')
        return render_template('main.html', player_board=players['player'][0])

@app.route('/attack', methods=['GET'])
def process_attack():
    """
    Recives the player attacks from flask and passes to the 'attack' function
    Then calls generate_attack to make AI generate an attack
    Then passes the AIs attack to the 'attack' function

    Returns the result of the players attack (True/False) and the location of the AIs attack to flask
    Finally if one player has completed the game it also passes that to flask
    """
    x = int(request.args.get('x'))
    y = int(request.args.get('y'))
    #opponent attack player
    target = generate_attack()
    result = attack(target, players['player'][0],players['player'][1])
    AI_opponent.input_result(result, target)

    opponents_target = (int(target[0]), int(target[1]))#save this in order to return to template
    #player attack opponent
    target = (x,y)
    result = attack(target, players['opponent'][0],players['opponent'][1])

    #check for game over
    if len(players['player'][1]) == 0:
        return jsonify({'hit': result, 'AI_Turn': opponents_target, 'finished': 'Game Over Opponent wins'})
    #elif players['opponent'][1] == True:
    elif len(players['opponent'][1]) == 0:
        return jsonify({'hit': result, 'AI_Turn': opponents_target, 'finished': 'Game Over Player wins'})
    else:
        return jsonify({'hit': result, 'AI_Turn': opponents_target})

if __name__ == "__main__":
    app.run()
