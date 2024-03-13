import logging

class GameGrid():
    def __init__(self):
        # game grid slots
        # value 0 means empty slot
        # value 1 means X
        # value 2 means O
        # grid is arranged left to right, top to bottom:
        # 0 1 2
        # 3 4 5
        # 6 7 8
        #
        self.slots = [
            0,0,0,
            0,0,0,
            0,0,0
        ]
        self.win_conditions = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Rows
            [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Columns
            [0, 4, 8], [2, 4, 6]              # Diagonals
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
        if slot_value == 0:
            slot_value = self.empty_marker
        if slot_value == 1:
            slot_value = self.player1_marker
        if slot_value == 2:
            slot_value = self.player2_marker
        return slot_value
    
    def get_player_marker(self, player_number):
        if player_number == 1:
            player_marker = self.player1_marker
        if player_number == 2:
            player_marker = self.player2_marker
        return player_marker
    
    def get_winner(self):
        for condition in self.win_conditions:
            if all(self.slots[i] == 1 for i in condition):
                return 1
            if all(self.slots[i] == 2 for i in condition):
                return 2
        return 0
    
    def print_ascii(self):
        logging.info(f"{self.slot_as_marker(0)} {self.slot_as_marker(1)} {self.slot_as_marker(2)}")
        logging.info(f"{self.slot_as_marker(3)} {self.slot_as_marker(4)} {self.slot_as_marker(5)}")
        logging.info(f"{self.slot_as_marker(6)} {self.slot_as_marker(7)} {self.slot_as_marker(8)}")