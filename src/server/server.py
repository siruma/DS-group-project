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

keep_running = True
players = {}
viewers = []
game_server = None
server_socket = None
client_status = ""
game = None


def handle_shutdown():
    '''
    Shutdown the server

    '''
    global keep_running
    logging.info("Shutting down the server ....")
    keep_running = False
    if server_socket:
        server_socket.close()


def handle_shutdown_key(sig, frame):
    handle_shutdown()


def client_authenticate(client_socket):
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


def handle_client(client_socket, player_ID, timeout):
    '''
    Handler for incoming clients

    client_socket: client socket
    player_ID: the ID of player
    timeout: server timeout value
    '''
    global players, game, client_status
    client_socket.sendall(pickle.dumps('Welcome'))
    reply = ""
    
    if (client_authenticate(client_socket)):
        while True:
            try:
                if (len(players) < 2):
                    # Waiting second player
                    client_socket.sendall(
                        pickle.dumps('102: Waiting for opponent...'))
                    logging.debug(f"Player {player_ID} is waiting")
                    time.sleep(10)
                elif game_server.player_turn(player_ID):
                    # Player turn
                    game_server.player_turn_start(player_ID)
                    act_player, game_round, game_fin, grid = game.game_status()
                    logging.debug(f"{game_fin}, {grid}")
                    if (game_fin):
                        # Send the game result if game has been ended
                        reply = game.check_for_winner()
                        client_socket.sendall(pickle.dump(reply))
                        break
                    else:
                        # Send turn info and grid, recv move data
                        logging.debug("Sending: 100: Player "
                                      + f"{player_ID} turn.")
                        client_socket.sendall(
                            pickle.dumps(f'100: Player {player_ID} turn.'))
                        time.sleep(1)
                        client_socket.sendall(pickle.dumps(grid))
                        logging.debug(f"Grid sent to player {player_ID}")
                        data = pickle.loads(client_socket.recv(2028))
                        logging.debug(f"Received: {data}")
                        if not isinstance(data, int):
                            # Wrong data
                            logging.info("Wrong data from player "
                                         + f"{player_ID}")
                        else:
                            # Adding the mark
                            reply = game.add_mark_to_slot(data)
                            logging.debug(f"Sending : {reply}")
                            client_socket.sendall(pickle.dumps(reply))
                            client_status = pickle.loads(
                                        client_socket.recv(2028))
                    game_server.player_turn_end(player_ID)
                    logging.debug(f"Player {player_ID} game status:"
                                  + f" {client_status}")
                    if (client_status == 'quit' or
                                         not isinstance(data, int) or
                                         not keep_running):
                        # Sleep to wait client finish 
                        time.sleep(20)
                        break
                else:
                    # Waiting your turn
                    if (client_status == 'quit'):
                        # Sleep to wait client finish 
                        time.sleep(20)
                        break
                    client_socket.sendall(
                        pickle.dumps('102: Waiting for opponent move...'))
                    logging.debug(f"Player {player_ID} is waiting")
                    time.sleep(10)
            except Exception as e:
                logging.error(f"Error handling player_client {player_ID}: {e}")
                break
    logging.info("Lost connection to player")
    # Remove player from players
    players.pop(player_ID)
    game_server.remove_player(player_ID)
    if (len(players) == 0) and keep_running:
        # Set timeout if the is no player and shutdown if there is no viewer
        logging.debug(f"Player {player_ID} set timeout")
        time.sleep(timeout)
        if (len(viewers) == 0):
            handle_shutdown()
    game.reset_game()
    client_socket.close()


def handle_viewer(client_socket):
    '''
    Handle viewer socket

    client_socket: client socket
    '''
    client_socket.sendall(pickle.dumps('Welcome'))
    game_data = ""
    while True:
        try:
            if (len(players) < 2):
                client_socket.sendall(pickle.dumps('Waiting for opponents...'))
            else:
                game_data = "server: "  # replace with real game data
                logging.debug(f"Sending: {game_data}")
                client_socket.sendall(pickle.dumps(game_data))
                viewer_reply = pickle.loads(client_socket.recv(2028))
                logging.debug(f"Received: {viewer_reply}")
        except Exception as e:
            logging.error(f"Error handling viewer_client: {e}")
            break
    logging.info("Lost connection to viewer")
    client_socket.close()


def run_server(address='localhost', port=8080, timeout=10):
    '''
    Run main server for clients

    address: server address
    port: server listen port
    timeout: server socket timeout value
    '''
    # Create TCP socket
    global server_socket, players, viewers, game_server, game
    game_server = GameServer()
    logging.info("Start the game")
    game = TictacGame()
    game.start_game()
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind the socket to address and port
    server_address = (address, port)
    server_socket.bind(server_address)

    # Listen for incoming connections
    server_socket.listen(5)
    logging.info(f"Server is listening for connections from {port}")
    try:
        while keep_running:
            client_socket, client_address = server_socket.accept()
            logging.info(f"Connection from {client_address}")

            # Handle client request
            if (len(players) < 2):
                player_ID = len(players)+1
                player = threading.Thread(target=handle_client,
                                          args=(client_socket, player_ID,
                                                timeout)).start()
                game_server.add_player(player)
                players[player_ID] = player
            else:
                viewer = threading.Thread(target=handle_viewer,
                                          args=(client_socket,)).start()
                viewers.append(viewer)
    except socket.timeout:
        logging.error("Server timeout")
    except socket.error as e:
        logging.error(e)
    finally:
        # Close the connection
        handle_shutdown()


def input_tread():
    '''
    Handler for command line inputs

    '''
    while keep_running:
        try:
            cmd = input("Enter command: ")
            if cmd == "quit":
                handle_shutdown()
            elif cmd == "help":
                print("To shutdown the server enter 'quit'")
            else:
                print("Error: not a command, enter "
                      + "'help' for more information")
        except EOFError:
            break


if __name__ == "__main__":

    # Register the signal handler for SIGINT (Ctrl+C)
    # and SIGTERM (termination signal)
    signal.signal(signal.SIGINT, handle_shutdown_key)
    signal.signal(signal.SIGTERM, handle_shutdown_key)

    parser = argparse.ArgumentParser("Tic-tac-toe server")

    # Arguments
    parser.add_argument('--address', type=str, help="Server ip address")
    parser.add_argument('--port', type=int, help="Server port")
    parser.add_argument('--timeout', type=int, help="Server timeout")
    parser.add_argument('--log-level', choices=['DEBUG', 'INFO'],
                        default='INFO', help="Logging level")

    # Parse the command-line arguments
    args = parser.parse_args()

    # Configure logging
    logging.basicConfig(filename='server.log', filemode='w',
                        level=args.log_level,
                        format='%(asctime)s - %(levelname)s - %(message)s')

    # Configure server arguments
    address = 'localhost'
    port = 8080
    timeout = 10

    if args.address is not None:
        address = args.address
    if args.port is not None:
        port = args.port
    if args.timeout is not None:
        timeout = args.timeout

    server_tread = threading.Thread(target=run_server,
                                    args=(address, port, timeout))
    server_tread.start()
    input_tread()
