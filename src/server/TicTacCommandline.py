'''
    run start_game() to start new game or reset active game
    game_status() can be delivered to clients to update them?
    original tic-tac-toe in python by krishkamani on github
    https://github.com/krishkamani/Tic-Tac-Toe-Game-In-Python/tree/master
'''

import logging


class GameGrid():
    def __init__(self):
        '''
        Game grid slots
        The value 0 equals the character O
        The value 1 equals the character X
        The value 2 equals empty slot
        The grid is arranged left to right, top to bottom:
         0 1 2
         3 4 5
         6 7 8
        '''
        self.slots = [
            2, 2, 2,
            2, 2, 2,
            2, 2, 2
        ]
        self.empty_marker = "_"
        self.player1_marker = "X"
        self.player2_marker = "O"
        logging.info("game grid and markers initiated")

    def slot(self, slot_number):
        return self.slots[slot_number]

    def set_slot(self, slot_number, new_value):
        self.slots[slot_number] = new_value

    def slot_as_marker(self, slot_number):
        slot_value = self.slots[slot_number]
        if slot_value == 2:
            slot_value = self.empty_marker
        if slot_value == 1:
            slot_value = self.player1_marker
        if slot_value == 0:
            slot_value = self.player2_marker
        return slot_value

    def print_ascii(self):
        logging.info(f"{self.slot_as_marker(0)}"
                     + f"{self.slot_as_marker(1)}"
                     + f"{self.slot_as_marker(2)}")

        logging.info(f"{self.slot_as_marker(3)}"
                     + f"{self.slot_as_marker(4)}"
                     + f" {self.slot_as_marker(5)}")

        logging.info(f"{self.slot_as_marker(6)}"
                     + f" {self.slot_as_marker(7)}"
                     + f" {self.slot_as_marker(8)}")


class TictacGame():
    def __init__(self):
        logging.info("game initiating")
        self.active_player = 1     # player 1 always starts
        self.game_round = 0        # game length max 9 rounds (=grid size)
        self.game_finished = True  # game is inactive (True) when it's finished
        self.grid = GameGrid()

    def reset_game(self):
        logging.info("resetting game status...")
        self.active_player = 1
        self.game_round = 0
        self.game_finished = False
        self.grid = GameGrid()
        # self.run_game()

    def forfeit_game(self, player_id):
        logging.warning(f"forfeit by player {player_id} due to disconnection"
                        + "or lack of input...")
        self.start_game()

    def start_game(self):
        logging.info("(re)start game...")
        self.reset_game()

    def game_status(self):
        logging.info("this is the game status, to be delivered "
                     + "to connected clients")
        logging.info("contains: active_player, game_round, game_finished,"
                     + " grid_slots 1-9[index starts at 0])")
        return (self.active_player, self.game_round,
                self.game_finished, self.grid)

    def run_game(self):
        while not self.game_finished:
            self.print_status()
            # TODO client to handle input properly,
            # now command line plays all turns and accepts int or crashes
            picked_slot = int(input())
            self.add_mark_to_slot(picked_slot)

    def print_status(self):
        logging.info(f"##### TIC TAC TOE, round {self.game_round+1}/ 9 #####")
        if not self.game_finished:
            logging.info(f"##### waiting on player: {self.active_player}")
        self.grid.print_ascii()
        logging.info("#####")

    def add_mark_to_slot(self, picked_slot):
        logging.info(f"picked slot: {picked_slot}")
        logging.info(f"active_player {self.active_player}")

        if (self.grid.slot(picked_slot) == 2):  # if picked_slot is free/unused
            self.grid.set_slot(picked_slot, self.active_player)
            if self.active_player == 1:
                self.active_player = 0
            else:
                self.active_player = 1
            self.game_round += 1
        else:
            logging.error("failed to find a case for marking the grid.")
        self.check_for_winner()

    def check_for_winner(self):
        logging.info("checking for winner...")
        if ( 
            # Horizontal line
            self.grid.slot(0) == 1 and self.grid.slot(1) == 1 and self.grid.slot(2) == 1 or
            self.grid.slot(3) == 1 and self.grid.slot(4) == 1 and self.grid.slot(5) == 1 or
            self.grid.slot(6) == 1 and self.grid.slot(7) == 1 and self.grid.slot(8) == 1 or
            # Vertical line
            self.grid.slot(0) == 1 and self.grid.slot(3) == 1 and self.grid.slot(6) == 1 or
            self.grid.slot(1) == 1 and self.grid.slot(4) == 1 and self.grid.slot(7) == 1 or
            self.grid.slot(2) == 1 and self.grid.slot(5) == 1 and self.grid.slot(8) == 1 or
            # Diagonal line
            self.grid.slot(0) == 1 and self.grid.slot(4) == 1 and self.grid.slot(8) == 1 or
            self.grid.slot(2) == 1 and self.grid.slot(4) == 1 and self.grid.slot(6) == 1):
            self.declare_winner(1)
        elif (
            # Horizontal line
            self.grid.slot(0) == 0 and self.grid.slot(1) == 0 and self.grid.slot(2) == 0 or
            self.grid.slot(3) == 0 and self.grid.slot(4) == 0 and self.grid.slot(5) == 0 or
            self.grid.slot(6) == 0 and self.grid.slot(7) == 0 and self.grid.slot(8) == 0 or
            # Vertical line
            self.grid.slot(0) == 0 and self.grid.slot(3) == 0 and self.grid.slot(6) == 0 or
            self.grid.slot(1) == 0 and self.grid.slot(4) == 0 and self.grid.slot(7) == 0 or
            self.grid.slot(2) == 0 and self.grid.slot(5) == 0 and self.grid.slot(8) == 0 or
            # Diagonal line
            self.grid.slot(0) == 0 and self.grid.slot(4) == 0 and self.grid.slot(8) == 0 or
            self.grid.slot(2) == 0 and self.grid.slot(4) == 0 and self.grid.slot(6) == 0):
            self.declare_winner(2)
        elif self.game_round == 9:
            self.declare_winner(0)  # Draw
        else:
            logging.info("no winner yet...")
            self.declare_winner(None)

    def declare_winner(self, player):
        if player == 0:
            self.game_finished = True
            logging.info("DRAW")
            return "200: DRAW"
        elif player == 1 or player == 2:
            self.game_finished = True
            logging.info(f"WINNER IS PLAYER {player}")
            return f"200: WINNER IS PLAYER {player}"
        return "no winner yet..."
        # TODO: replace console print with updating game status to clients
        # self.print_status()


# example of running game
# Uncomment to see info logs in command line during testing
# logging.getLogger().setLevel(logging.INFO)
# tictac = TictacGame()
# tictac.start_game()
