##
## run start_game() to start new game or reset active game
## game_status() can be delivered to clients to update them?
##

## original tic-tac-toe in python by krishkamani on github https://github.com/krishkamani/Tic-Tac-Toe-Game-In-Python/tree/master

class tictac_game():
    def __init__(self):
        print("game initiating")
        self.active_player=1 #player 1 always starts
        self.game_round=0    #game length max 9 rounds (=grid size)
        self.game_finished=1 #game is inactive (1) when it's finished
        self.grid_slot1 = 2
        self.grid_slot2 = 2
        self.grid_slot3 = 2
        self.grid_slot4 = 2
        self.grid_slot5 = 2
        self.grid_slot6 = 2
        self.grid_slot7 = 2
        self.grid_slot8 = 2
        self.grid_slot9 = 2
    
    def reset_game(self):
        print("resetting game status...")
        self.active_player=1
        self.game_round=0
        self.game_finished=0
        self.run_game()
        
        # game grid slots
        # value 0 means O        
        # value 1 means X        
        # value 2 means empty slot
        # grid is arranged left to right, top to bottom:
        # 1 2 3
        # 4 5 6
        # 7 8 9
        self.grid_slot1 = 2
        self.grid_slot2 = 2
        self.grid_slot3 = 2
        self.grid_slot4 = 2
        self.grid_slot5 = 2
        self.grid_slot6 = 2
        self.grid_slot7 = 2
        self.grid_slot8 = 2
        self.grid_slot9 = 2
        

    def forfeit_game(self, player_id):
        print("forfeit by player ", player_id, "due to disconnection or lack of input...")
        self.start_game()
    
    def start_game(self):
        print("(re)start game...")
        self.reset_game()
        
    def game_status(self):
        print("this is the game status, to be delivered to connected clients")
        print("contains: active_player, game_round, game_finished, grid_slots 1-9)")
        return(self.active_player, self.game_round, self.game_finished, 
        self.grid_slot1, self.grid_slot2, self.grid_slot3, 
        self.grid_slot4, self.grid_slot5, self.grid_slot6, 
        self.grid_slot7, self.grid_slot8, self.grid_slot9 )
        
    def run_game(self):
        while self.game_finished < 1:
            self.print_ascii_status()
            
            #TODO client to handle input properly,
            # now command line plays all turns and accepts int or crashes
            picked_slot = int(input())
            self.add_mark_to_slot(picked_slot)
        
        
    def print_ascii_status(self):
        print("#####")
        print("##### TIC TAC TOE ",self.game_round, "/9#####")
        if self.game_finished==0:
            print("##### waiting on player: ", self.active_player)
        print(self.grid_slot1, self.grid_slot2, self.grid_slot3)
        print(self.grid_slot4, self.grid_slot5, self.grid_slot6)
        print(self.grid_slot7, self.grid_slot8, self.grid_slot9)
        print("#####")
        print("#####")
        
    def add_mark_to_slot(self, picked_slot):
        print("picked slot:", picked_slot)
        print("active_player", self.active_player)
        
        #for player 1 turn
        if picked_slot==1 and self.grid_slot1==2 and self.active_player==1:
            self.grid_slot1=1
            self.active_player=0
            self.game_round+=1
        if picked_slot==2 and self.grid_slot2==2 and self.active_player==1:
            self.grid_slot2=1
            self.active_player=0
            self.game_round+=1
        if picked_slot==3 and self.grid_slot3==2 and self.active_player==1:
            self.grid_slot3=1
            self.active_player=0
            self.game_round+=1
        if picked_slot==4 and self.grid_slot4==2 and self.active_player==1:
            self.grid_slot4=1
            self.active_player=0
            self.game_round+=1
        if picked_slot==5 and self.grid_slot5==2 and self.active_player==1:
            self.grid_slot5=1
            self.active_player=0
            self.game_round+=1
        if picked_slot==6 and self.grid_slot6==2 and self.active_player==1:
            self.grid_slot6=1
            self.active_player=0
            self.game_round+=1
        if picked_slot==7 and self.grid_slot7==2 and self.active_player==1:
            self.grid_slot7=1
            self.active_player=0
            self.game_round+=1
        if picked_slot==8 and self.grid_slot8==2 and self.active_player==1:
            self.grid_slot8=1
            self.active_player=0
            self.game_round+=1
        if picked_slot==9 and self.grid_slot9==2 and self.active_player==1:
            self.grid_slot9=1
            self.active_player=0
            self.game_round+=1
        
        #for player 2 turn
        if picked_slot==1 and self.grid_slot1==2 and self.active_player==0:
            self.grid_slot1=0
            self.active_player=1
            self.game_round+=1
        if picked_slot==2 and self.grid_slot2==2 and self.active_player==0:
            self.grid_slot2=0
            self.active_player=1
            self.game_round+=1
        if picked_slot==3 and self.grid_slot3==2 and self.active_player==0:
            self.grid_slot3=0
            self.active_player=1
            self.game_round+=1
        if picked_slot==4 and self.grid_slot4==2 and self.active_player==0:
            self.grid_slot4=0
            self.active_player=1
            self.game_round+=1
        if picked_slot==5 and self.grid_slot5==2 and self.active_player==0:
            self.grid_slot5=0
            self.active_player=1
            self.game_round+=1
        if picked_slot==6 and self.grid_slot6==2 and self.active_player==0:
            self.grid_slot6=0
            self.active_player=1
            self.game_round+=1
        if picked_slot==7 and self.grid_slot7==2 and self.active_player==0:
            self.grid_slot7=0
            self.active_player=1
            self.game_round+=1
        if picked_slot==8 and self.grid_slot8==2 and self.active_player==0:
            self.grid_slot8=0
            self.active_player=1
            self.game_round+=1
        if picked_slot==9 and self.grid_slot9==2 and self.active_player==0:
            self.grid_slot9=0
            self.active_player=1
            self.game_round+=1
        self.check_for_winner()
            
    def check_for_winner(self):
        print("checking for winner...")
        if( self.grid_slot1==1 and self.grid_slot2==1 and self.grid_slot3==1 or
            self.grid_slot4==1 and self.grid_slot5==1 and self.grid_slot6==1 or
            self.grid_slot7==1 and self.grid_slot8==1 and self.grid_slot9==1 or
            self.grid_slot1==1 and self.grid_slot4==1 and self.grid_slot7==1 or
            self.grid_slot2==1 and self.grid_slot5==1 and self.grid_slot8==1 or
            self.grid_slot3==1 and self.grid_slot6==1 and self.grid_slot9==1 or
            self.grid_slot1==1 and self.grid_slot5==1 and self.grid_slot9==1 or
            self.grid_slot3==1 and self.grid_slot5==1 and self.grid_slot7==1):
                self.declare_winner(1)
        elif( self.grid_slot1==0 and self.grid_slot2==0 and self.grid_slot3==0 or
            self.grid_slot4==0 and self.grid_slot5==0 and self.grid_slot6==0 or
            self.grid_slot7==0 and self.grid_slot8==0 and self.grid_slot9==0 or
            self.grid_slot1==0 and self.grid_slot4==0 and self.grid_slot7==0 or
            self.grid_slot2==0 and self.grid_slot5==0 and self.grid_slot8==0 or
            self.grid_slot3==0 and self.grid_slot6==0 and self.grid_slot9==0 or
            self.grid_slot1==0 and self.grid_slot5==0 and self.grid_slot9==0 or
            self.grid_slot3==0 and self.grid_slot5==0 and self.grid_slot7==0):
                self.declare_winner(2)
        elif self.game_round==9:
                self.declare_winner(0) #draw
        else:
            print("no winner yet...")
                
    def declare_winner(self, player):
        self.game_finished = 1
        if player==0:
            print("DRAW")
        else:
            print("WINNER IS PLAYER ", player)
        
        self.print_ascii_status
    
    
# example of running game
tictac = tictac_game()
tictac.start_game()
#print(tictac.game_status())
