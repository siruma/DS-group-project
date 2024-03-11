# Class for handle turn in game.
import logging


class GameServer:

    def __init__(self) -> None:
        self.player1 = None
        self.player2 = None
        self.current_turn = 1

    '''
    Add player to class

    player_thread: thread
    '''
    def add_player(self, player_thread):
        if (self.player1 is None):
            self.player1 = player_thread
            logging.debug("GameServer: adding player 1")
        elif (self.player2 is None):
            self.player2 = player_thread
            logging.debug("GameServer: adding player 2")
        else:
            logging.error("GameServer: Player queue is full.")

    '''
    Remove_player

    player_ID: ID of the player
    '''
    def remove_player(self, player_ID):
        if (player_ID == 1):
            self.player1 = None
        elif (player_ID == 2):
            self.player2 = None
        else:
            logging.error(f"GameServer: Player {player_ID} not found.")
        self.current_turn = 1
        logging.debug("GameServer: Game has restarted.")

    '''
    Start player turn

    player_ID: ID of the player
    '''
    def player_turn_start(self, player_ID):
        if (player_ID == 1):
            logging.info(f"GameServer: Player {player_ID} start.")
        elif (player_ID == 2):
            logging.info(f"GameServer: Player {player_ID} start.")

    '''
    End the player turn

    player_ID: ID of the player
    '''
    def player_turn_end(self, player_ID):
        if (player_ID == 1):
            logging.info(f"GameServer: Player {player_ID} end.")
            self.current_turn = 2
        elif (player_ID == 2):
            logging.info(f"GameServer: Player {player_ID} end.")
            self.current_turn = 1

    '''
    Check players turns

    player_ID: ID of the player
    '''
    def player_turn(self, player_ID):
        if (self.player1 is None and self.player2 is None):
            if (player_ID == self.current_turn):
                logging.debug(f"GameServer: Player {player_ID} turn")
                return True
        logging.debug(f"GameServer: Player {player_ID}, current {self.current_turn} ")
        return False
