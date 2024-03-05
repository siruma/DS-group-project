# Socket server for tic-tac-toe game
import socket
import argparse
import pickle
import logging
import signal
import threading

keep_running = True
server_socket = None

def handle_shutdown():
    global keep_running
    logging.info("Shutting down the server ....")
    keep_running = False
    if server_socket:
        server_socket.close()

def handle_shutdown_key(sig, frame):
    handle_shutdown()
    

def authenticate(client_socket):
    logging.debug("Authentication")
    # Send authentication request to client
    USERNAME = 'user'
    PASSWORD = 'password'
    reply = 'Enter username: '
    client_socket.sendall(pickle.dumps(reply))
    username = pickle.loads(client_socket.recv(2028))
    logging.debug("Username: {username}")
    reply = 'Enter password: '
    client_socket.send(pickle.dumps(reply))
    password = pickle.loads(client_socket.recv(2028))

    # Check if username and password are correct
    if username == USERNAME and password == PASSWORD:
        reply = 'Authentication successful.'
        client_socket.send(pickle.dumps(reply))
        return True
    else:
        reply = 'Authentication failed.'
        client_socket.send(pickle.dumps(reply))
        return False

def handle_client(client_socket):
    client_socket.sendall(pickle.dumps('Welcome'))
    reply = ""
    if(authenticate(client_socket)):
        while True: 
            try:
                data = pickle.loads(client_socket.recv(2028))
                if not data:
                    logging.info("Disconnected from player")
                else:
                    reply = "server: "  + data # replace with real game data
                    logging.debug(f"Received: {data}")
                    logging.debug(f"Sending : {reply}")
                    client_socket.sendall(pickle.dumps(reply))
            except Exception as e:
                logging.error("Error handling client: %s", e)
                break
    logging.info("Lost connection")
    client_socket.close()

def run_server(address='localhost', port=8080):
    # Create TCP socket
    global server_socket
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
            threading.Thread(target=handle_client, args=(client_socket,)).start()
    except socket.error as e:
        logging.error(e)
    finally:
        # Close the connection
        server_socket.close()

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
    parser.add_argument('--log-level', choices=['DEBUG', 'INFO'], default='INFO', help="Logging level")
    
    # Parse the command-line arguments
    args = parser.parse_args()

    # Configure logging
    logging.basicConfig(filename='server.log', filemode='w',level=args.log_level,
                         format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Configure server arguments
    address = 'localhost'
    port = 8080

    if args.address is not None:
        address = args.address
    if args.port is not None:
        port = args.port
    
    server_tread = threading.Thread(target=run_server,args=(address,port))
    server_tread.start()
    input_tread()
    
    