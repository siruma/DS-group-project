import pygame
import pickle
import socket
import signal
import argparse
import logging

# Configure the game client
SERVER_ADDRESS = '' #LOCAL ID HERE
SERVER_PORT = 8080
client_socket = None
slots = [0,0,0,0,0,0,0,0,0]

def handle_shutdown():
    '''
    Shutdown the server

    '''
    global keep_running
    # logging.info("Shutting down the client ....")
    keep_running = False
    if client_socket:
        client_socket.close()


def handle_shutdown_key(sig, frame):
    handle_shutdown()

def update_grid_status(status):
    '''
    Draw empty tic-tac-toe game area

    '''
    global slots
    try:
       new_slots = status.strip()[1:-1].split(',')
       if (new_slots != slots):
           integer_list = [int(x) for x in new_slots]
           logging.info(f'New status: {sum(integer_list)}')
       slots = new_slots
    except Exception as e:
        logging.error(f'Error in updating the game status: {e}')

def viewer_screen(server_addr):
    '''
     Mimic the viewer screen

    '''
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(server_addr)
    response = pickle.loads(client_socket.recv(2048))
    client_socket.sendall(pickle.dumps("viewer"))
    response = pickle.loads(client_socket.recv(2048))
    stay_viewer = True
    clock = pygame.time.Clock()
    while stay_viewer:
        clock.tick(60)
        try:
            response = pickle.loads(client_socket.recv(2048)).split(':')
            tag = response[0]
            message = response[1]
            winner = 0
            # Server is sending the game status, update it
            if tag == 'status':
                update_grid_status(message)
        except:
            pygame.time.delay(1000)


def menu_screen():
    '''
    Main loop, shows the game menu

    '''

    signal.signal(signal.SIGINT, handle_shutdown_key)
    signal.signal(signal.SIGTERM, handle_shutdown_key)

    parser = argparse.ArgumentParser("Tic-tac-toe client")

    # Arguments
    parser.add_argument('--address', type=str, help="Server ip address")
    parser.add_argument('--port', type=int, help="Server port")
    parser.add_argument('--log-level', choices=['DEBUG', 'INFO'],
                        default='INFO', help="Logging level")

    # Parse the command-line arguments
    args = parser.parse_args()

    with open("config.txt", "r+") as f:
        client_index = int(f.read().strip())
        f.seek(0)
        f.write(str(client_index + 1))
        f.truncate()

    logging.basicConfig(filename=f'client{str(client_index)}.log', filemode='w',
                        level=args.log_level,
                        format='%(asctime)s - %(levelname)s - %(message)s')

    # Configure server arguments
    address = SERVER_ADDRESS
    port = SERVER_PORT

    if args.address is not None:
        address = args.address
    if args.port is not None:
        port = args.port
    server_addr = (address, port)

    viewer_screen(server_addr)

while True:
    menu_screen()