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
from TicTacCommandline import TictacGame


class Server():

    def __init__(self) -> None:
        self.keep_running = True
        self.players = {}  # List of players
        self.viewers = []  # List of viewers
        self.game_server = None  # Add the waiting logic
        self.server_socket = None  # Server socket
        self.client_status = ""  # Players status ok/quit
        self.game = None  # The game
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
        reply = ""

        if (self.client_authenticate(client_socket)):
            while True:
                try:
                    player_turn = self.game_server.player_turn(player_ID)
                    if (len(self.players) < 2):
                        # Waiting second player
                        client_socket.sendall(pickle.dumps('102: Waiting for opponent...'))
                        logging.debug(f"Player {player_ID} is waiting an opponent")
                        time.sleep(10)
                    elif player_turn:
                        # Player turn
                        self.game_server.player_turn_start(player_ID)
                        act_player, game_round, game_fin, grid = self.game.game_status()
                        logging.debug(f"{game_fin}, {grid}")
                        if (game_fin):
                            # Send the game result if game has been ended
                            reply = self.game.check_for_winner()
                            client_socket.sendall(pickle.dump(reply))
                            break
                        else:
                            # Send turn info and grid, recv move data
                            logging.debug(f"Sending: 100: Player {player_ID} turn.")
                            client_socket.sendall( pickle.dumps(f'100: Player {player_ID} turn.'))
                            time.sleep(1)  # Sleep 1 sec before sending another message
                            client_socket.sendall(pickle.dumps(grid))
                            logging.debug(f"Grid sent to player {player_ID}")
                            data = pickle.loads(client_socket.recv(2028))  # Get the move
                            logging.debug(f"Received: {data}")
                            if not isinstance(data, int):
                                # Wrong data
                                logging.info("Wrong data from player {player_ID}")
                            else:
                                # Adding the mark and sending the result
                                reply = self.game.add_mark_to_slot(data)
                                logging.debug(f"Sending : {reply}")
                                client_socket.sendall(pickle.dumps(reply))
                                self.client_status = pickle.loads(client_socket.recv(2028))
                        self.game_server.player_turn_end(player_ID)  # Receive player status ok/quit
                        logging.debug(f"Player {player_ID} game status:"
                                      + f" {self.client_status}")
                        if (self.client_status == 'quit' or not isinstance(data, int) or not self.keep_running):
                            # Sleep to wait client finish 
                            time.sleep(20)
                            break
                    else:
                        # Waiting your turn
                        if (self.client_status == 'quit'):
                            # Sleep to wait client finish 
                            time.sleep(20)
                            break
                        client_socket.sendall(pickle.dumps('102: Waiting for opponent move...'))
                        logging.debug(f"Player {player_ID} is waiting turn, turn status: {player_turn}")
                        time.sleep(10)
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
        self.game.reset_game()
        client_socket.close()

    def handle_viewer(self, client_socket):
        '''
        Handle viewer socket

        client_socket: client socket
        '''
        client_socket.sendall(pickle.dumps('Welcome'))
        game_data = {}
        while True:
            try:
                if (len(self.players) < 2):
                    client_socket.sendall(
                        pickle.dumps('Waiting for opponents...'))
                else:
                    act_player, game_round, game_fin, grid = self.game.game_status()
                    if (game_fin):
                        # Send the game result if game has been ended
                        reply = self.game.check_for_winner()
                        client_socket.sendall(pickle.dump(reply))
                        break
                    else:
                        game_data['act_player'] = act_player
                        game_data['game_round'] = game_round
                        game_data['game_fin'] = game_fin
                        game_data['grid'] = grid
                        logging.debug(f"Sending: {game_data}")
                        client_socket.sendall(pickle.dumps(game_data))
                        viewer_reply = pickle.loads(client_socket.recv(2028))
                        logging.debug(f"Received: {viewer_reply}")
            except Exception as e:
                logging.error(f"Error handling viewer_client: {e}")
                break
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
        logging.info("Start the game server")
        self.game_server = GameServer()
        self.game = TictacGame()
        self.game.start_game()
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.timeout = timeout

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

                # Handle client request
                if (len(self.players) < 2):
                    player_ID = len(self.players) + 1
                    player = threading.Thread(target=self.handle_client, args=(client_socket, player_ID))
                    self.game_server.add_player(player)
                    self.players[player_ID] = player
                    player.start()
                else:
                    viewer = threading.Thread(target=self.handle_viewer, args=(client_socket,))
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
