# Socket server for tic-tac-toe game
import socket
import argparse
import pickle
import logging
import signal
import threading
import time
from authentication import Authentication
from GameServer import GameServer
from GameGrid import GameGrid

class Server():

    def __init__(self) -> None:
        self.keep_running = True
        self.players = {}  # List of players
        self.viewers = []  # List of viewers
        self.game_server = None  # Add the waiting logic
        self.server_socket = None  # Server socket
        self.client_status = ""  # Players status ok/quit
        self.game = GameGrid()  # The game
        self.timeout = 0  # server timeout value


    def handle_shutdown(self):
        '''
        Shutdown the server

        '''
        logging.info("Shutting down the server ....")
        self.keep_running = False
        if self.server_socket:
            self.server_socket.close()


    def handle_shutdown_key(self, sig, frame):
        self.handle_shutdown()


    def client_authenticate(self, client_socket):
        '''
        Client authentication

        client_socket: Client socket
        return: True if client password is ok
        '''
        # Start the authentication DB
        authenticate_db = Authentication()
        logging.debug("Authentication")
        # Send authentication request to client
        reply = 'Enter username: '
        client_socket.sendall(pickle.dumps(reply))
        username = pickle.loads(client_socket.recv(2028))
        logging.debug(f"Username: {username}")
        reply = 'Enter password: '
        client_socket.send(pickle.dumps(reply))
        password = pickle.loads(client_socket.recv(2028))
        logging.debug(f"password: {password}")
        if authenticate_db.register_user(username, password):
            logging.info("User added")

        # Check if username and password are correct
        if authenticate_db.authenticate_user(username, password):
            reply = 'Authentication successful.'
            client_socket.send(pickle.dumps(reply))
            if authenticate_db:
                authenticate_db.close_database()
            return True
        else:
            reply = 'Authentication failed.'
            client_socket.send(pickle.dumps(reply))
            if authenticate_db:
                authenticate_db.close_database()
            return False


    def handle_client(self, client_socket, player_ID):
        '''
        Handler for incoming clients

        client_socket: client socket
        player_ID: the ID of player
        '''
        client_socket.sendall(pickle.dumps('Welcome'))
        if (self.client_authenticate(client_socket)):
            while True:
                try:
                    client_socket.sendall(
                            pickle.dumps(f'status:{str(self.game.slots)}:{str(self.game.get_winner())}'))
                    if self.game.get_winner() != 0:
                        time.sleep(5)
                        self.game = GameGrid()
                    else:
                        if (len(self.players) < 2):
                            client_socket.sendall(
                                pickle.dumps('102: Waiting for opponent...'))
                            logging.debug(f"Player {player_ID} is waiting")
                            time.sleep(0.2)
                        elif self.game_server.player_turn(player_ID):
                            self.game_server.player_turn_start(player_ID)
                            client_socket.sendall(
                                pickle.dumps(f'100: Your turn. Click to place "{self.game.get_player_marker(player_ID)}".'))
                            data = pickle.loads(client_socket.recv(2028))
                            if not data:
                                logging.info("Disconnected from player")
                            else:
                                self.game.set_slot(int(data), player_ID)
                            self.game_server.player_turn_end(player_ID)
                        else:
                            client_socket.sendall(
                                pickle.dumps('102: Waiting for opponent move...'))
                            logging.debug(f"Player {player_ID} is waiting")
                            time.sleep(0.2)
                except Exception as e:
                    logging.error(f"Error handling player_client {player_ID}: {e}")
                    break
        logging.info("Lost connection to player")
        # Remove player from players
        self.players.pop(player_ID)
        self.game_server.remove_player(player_ID)
        if (len(self.players) == 0) and self.keep_running:
            # Set timeout if the is no player and shutdown if there is no viewer
            logging.debug(f"Player {player_ID} set timeout")
            time.sleep(self.timeout)
            if (len(self.viewers) == 0):
                self.handle_shutdown()
        client_socket.close()


    def handle_viewer(self, client_socket):
        '''
        Handle viewer socket

        client_socket: client socket
        '''
        client_socket.sendall(pickle.dumps('Welcome'))
        game_data = ""
        while True:
            try:
                if (len(self.players) < 2):
                    client_socket.sendall(pickle.dumps(f'102: Waiting for {2-len(self.players)} player(s).'))
                else:
                    game_data = (f'status:{str(self.game.slots)}:{str(self.game.get_winner())}')
                    logging.debug(f"Sending: {game_data}")
                    client_socket.sendall(pickle.dumps(game_data))
                    if self.game.get_winner() != 0:
                        if self.game.get_winner() == 3: # check if there is a tie 
                            client_socket.sendall(
                                pickle.dumps(f'Tie game. New game starting soon.'))
                        else:
                            client_socket.sendall(
                                pickle.dumps(f'103: Player {self.game.get_winner()} won! New game starting soon.'))
                    else:
                        client_socket.sendall(pickle.dumps(f'102: Player {self.game_server.get_player_turn()} turn'))
                time.sleep(0.2)
            except Exception as e:
                logging.error(f"Error handling viewer_client: {e}")
                break
            time.sleep(1)
        logging.info("Lost connection to viewer")
        client_socket.close()


    def run_server(self, address='localhost', port=8080, timeout=10):
        '''
        Run main server for clients

        address: server address
        port: server listen port
        timeout: server socket timeout value
        '''
        # Create TCP socket
        self.game_server = GameServer()
        self.timeout = timeout
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Bind the socket to address and port
        server_address = (address, port)
        self.server_socket.bind(server_address)

        # Listen for incoming connections
        self.server_socket.listen(5)
        logging.info(f"Server is listening for connections from {port}")
        try:
            while self.keep_running:
                client_socket, client_address = self.server_socket.accept()
                logging.info(f"Connection from {client_address}")
                client_socket.sendall(pickle.dumps('choose'))
                response = pickle.loads(client_socket.recv(2028))

                # Handle client request
                if (response == "player"):
                    if (len(self.players) < 2):
                        player_ID = len(self.players)+1
                        player = threading.Thread(target=self.handle_client,
                                                args=(client_socket, player_ID))
                        self.game_server.add_player(player)
                        self.players[player_ID] = player
                        player.start()
                    else:
                        client_socket.sendall(pickle.dumps("Game is full"))
                elif (response == "viewer"):
                    viewer = threading.Thread(target=self.handle_viewer,
                                            args=(client_socket,))
                    self.viewers.append(viewer)
                    viewer.start()
        except socket.timeout:
            logging.error("Server timeout")
        except socket.error as e:
            logging.error(e)
        finally:
            # Close the connection
            self.handle_shutdown()


def input_tread(server):
    '''
    Handler for command line inputs

    '''
    while server.keep_running:
        try:
            cmd = input("Enter command: ")
            if cmd == "quit":
                print("Shutdown...")
                server.handle_shutdown()
            elif cmd == "status":
                print(f"Running: {server.keep_running}")
                print(f"Players: {len(server.players)}")
                print(f"viewers: {len(server.viewers)}")
            elif cmd == "help":
                print("To shutdown the server enter 'quit'")
                print("To check the status enter 'status' ")
            else:
                print("Error: not a command, enter "
                      + "'help' for more information about commands")
        except EOFError:
            break



if __name__ == "__main__":

    server = Server()
    # Register the signal handler for SIGINT (Ctrl+C)
    # and SIGTERM (termination signal)
    signal.signal(signal.SIGINT, server.handle_shutdown_key)
    signal.signal(signal.SIGTERM, server.handle_shutdown_key)

    parser = argparse.ArgumentParser("Tic-tac-toe: server.py")

    # Arguments
    parser.add_argument('--address', type=str, help="Server ip address", default='localhost')
    parser.add_argument('--port', type=int, help="Server port", default=8080)
    parser.add_argument('--timeout', type=int, help="Server timeout",default=10)
    parser.add_argument('--log-level', choices=['DEBUG', 'INFO'],
                        default='INFO', help="Logging level")

    # Parse the command-line arguments
    args = parser.parse_args()

    # Configure logging
    logging.basicConfig(filename='server.log', filemode='w',
                        level=args.log_level,
                        format='%(asctime)s - %(levelname)s - %(message)s')

    # Configure server arguments
    address = args.address
    port = args.port
    timeout = args.timeout

    # Start the server
    server_tread = threading.Thread(target=server.run_server,
                                    args=(address, port, timeout))
    server_tread.start()
    input_tread(server)
