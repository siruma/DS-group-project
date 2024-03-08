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

keep_running = True
players = {}
viewers = []
game_server = None
server_socket = None

'''
Shutdown the server
'''
def handle_shutdown():
    global keep_running
    logging.info("Shutting down the server ....")
    keep_running = False
    if server_socket:
        server_socket.close()
    

def handle_shutdown_key(sig, frame):
    handle_shutdown()
    

'''
Client authentication

client_socket: Client socket
return: True if client password is ok
'''
def client_authenticate(client_socket):
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
    if authenticate_db.register_user(username,password):
        logging.info("User added")
    
    # Check if username and password are correct
    if authenticate_db.authenticate_user(username,password):
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


'''
Handler for incoming clients

client_socket: client socket
player_ID: the ID of player
timeout: server timeout value
'''
def handle_client(client_socket, player_ID, timeout):
    global players
    client_socket.sendall(pickle.dumps('Welcome'))
    reply = ""
    if(client_authenticate(client_socket)):
        while True: 
            try:
                if(len(players) < 2):
                    client_socket.sendall(pickle.dumps('102: Waiting for opponent...'))
                    logging.debug(f"Player {player_ID} is waiting")
                    time.sleep(10)
                elif game_server.player_turn(player_ID):
                    game_server.player_turn_start(player_ID)
                    client_socket.sendall(pickle.dumps(f'100: Player {player_ID} turn.'))
                    data = pickle.loads(client_socket.recv(2028))
                    if not data:
                        logging.info("Disconnected from player")
                    else:
                        reply = "server: "  + data # replace with real game data
                        logging.debug(f"Received: {data}")
                        logging.debug(f"Sending : {reply}")
                        client_socket.sendall(pickle.dumps(reply))
                    game_server.player_turn_end(player_ID)
                else:
                    client_socket.sendall(pickle.dumps('102: Waiting for opponent move...'))
                    logging.debug(f"Player {player_ID} is waiting")
                    time.sleep(10)
            except Exception as e:
                logging.error(f"Error handling player_client {player_ID}: {e}")
                break
    logging.info("Lost connection to player")
    # remove player from players
    players.pop(player_ID)
    game_server.remove_player(player_ID)
    if(len(players) == 0 ):
        # Set timeout if the is no player and shutdown if there is no viewer
        logging.debug(f"Player {player_ID} set timeout")
        time.sleep(timeout)
        if(len(viewers) == 0):
            handle_shutdown()
    client_socket.close()

'''
Handle viewer socket

client_socket: client socket
'''
def handle_viewer(client_socket):
    client_socket.sendall(pickle.dumps('Welcome'))
    game_data = ""
    while True:
        try:
            if(len(players) < 2):
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

'''
Run main server for clients

address: server address
port: server listen port
timeout: server socket timeout value
'''
def run_server(address='localhost', port=8080,timeout=10):
    # Create TCP socket
    global server_socket, players, viewers, game_server
    game_server = GameServer()
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
            if(len(players) < 2):
                player_ID = len(players)+1
                player = threading.Thread(target=handle_client, args=(client_socket,player_ID,timeout)).start()
                game_server.add_player(player)
                players[player_ID] = player
            else:
                viewer = threading.Thread(target=handle_viewer, args=(client_socket,)).start()
                viewers.append(viewer)
            

    except socket.timeout:
        logging.error("Server timeout")
    except socket.error as e:
        logging.error(e)
    finally:
        # Close the connection
        handle_shutdown()

'''
Handler for command line inputs
'''
def input_tread():
    while keep_running:
        try:
            cmd = input("Enter command: ")
            if cmd == "quit":
                handle_shutdown()
            elif cmd == "help":
                print("To shutdown the server enter 'quit'")
            else:
                print("Error: not a command, enter 'help' for more information")
        except EOFError:
            break



if __name__ == "__main__":
    
    # Register the signal handler for SIGINT (Ctrl+C) and SIGTERM (termination signal)
    signal.signal(signal.SIGINT, handle_shutdown_key)
    signal.signal(signal.SIGTERM, handle_shutdown_key)
    

    parser = argparse.ArgumentParser("Tic-tac-toe server")

    # Arguments
    parser.add_argument('--address', type=str, help="Server ip address")
    parser.add_argument('--port', type=int, help="Server port")
    parser.add_argument('--timeout', type=int, help="Server timeout")
    parser.add_argument('--log-level', choices=['DEBUG', 'INFO'], default='INFO', help="Logging level")
    
    # Parse the command-line arguments
    args = parser.parse_args()

    # Configure logging
    logging.basicConfig(filename='server.log', filemode='w',level=args.log_level,
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
    
    server_tread = threading.Thread(target=run_server,args=(address,port,timeout))
    server_tread.start()
    input_tread()
    
    