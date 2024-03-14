import pygame
import pickle
import socket
import signal
import argparse
import logging
import hashlib

# Configure the game client
SERVER_ADDRESS = 'localhost'
SERVER_PORT = 8080
WIDTH = 600
HEIGHT = 600
LINE_WIDTH = 5
GRID_SIZE = 3
CELL_SIZE = 400 // GRID_SIZE
BLACK = (0,0,0)
pygame.font.init()
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tic-tac-toe")
client_socket = None
slots = [0,0,0,0,0,0,0,0,0]
info_text = ''


class Button:
    def __init__(self, text, x, y, color, w=220, h=100):
        self.text = text
        self.x = x
        self.y = y
        self.color = color
        self.width = w
        self.height = h

    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.height))
        font = pygame.font.SysFont(None, 40)
        text = font.render(self.text, 1, (255,255,255))
        win.blit(text, (self.x + round(self.width/2) - round(text.get_width()/2), self.y + round(self.height/2) - round(text.get_height()/2)))

    def click(self, pos):
        x1 = pos[0]
        y1 = pos[1]
        if self.x <= x1 <= self.x + self.width and self.y <= y1 <= self.y + self.height:
            return True
        else:
            return False

def handle_shutdown():
    '''
    Shutdown the server

    '''
    global keep_running
    logging.info("Shutting down the client ....")
    keep_running = False
    if client_socket:
        client_socket.close()


def handle_shutdown_key(sig, frame):
    handle_shutdown()

def draw_empty_grid():
    '''
    Draw empty tic-tac-toe game area

    '''
    logging.debug("Drawing empty grid.")
    for i in range(GRID_SIZE+1):
        pygame.draw.line(win, (0, 0, 0), ((100 + i * CELL_SIZE), 100), ((100 + i * CELL_SIZE), 500), LINE_WIDTH)
        pygame.draw.line(win, (0, 0, 0), (100, (100 + i * CELL_SIZE)), (500, (100 + i * CELL_SIZE)), LINE_WIDTH)

def draw_game_window():
    '''
    Draw the game grid with the latest game status received from the server

    '''
    global slots, info_text
    for i in range(len(slots)):
        if int(slots[i]) == 1:
            font = pygame.font.SysFont(None, 50)
            text_surface = font.render("X", True, (0, 0, 0))
            x = 100 + CELL_SIZE/2 - text_surface.get_width()/2 + (i % 3) * CELL_SIZE
            y = 100 + CELL_SIZE/2 - text_surface.get_height()/2 + (int(i/3)) * CELL_SIZE
            win.blit(text_surface, (x, y))
        elif int(slots[i]) == 2:
            font = pygame.font.SysFont(None, 50)
            text_surface = font.render("O", True, (0, 0, 0))
            x = 100 + CELL_SIZE/2 - text_surface.get_width()/2 + (i % 3) * CELL_SIZE
            y = 100 + CELL_SIZE/2 - text_surface.get_height()/2 + (int(i/3)) * CELL_SIZE
            win.blit(text_surface, (x, y))
    font = pygame.font.SysFont(None, 40)
    text = font.render(info_text, 1, (0, 0, 0))
    win.blit(text, (WIDTH/2 - text.get_width()/2, HEIGHT/10 - text.get_height()/10))
    pygame.display.update()
    logging.info("Game window re-drawn.")
    pygame.time.delay(2)

def update_grid_status(status):
    '''
    Draw empty tic-tac-toe game area

    '''
    global slots
    try:
       slots = status.strip()[1:-1].split(',')
    except Exception as e:
        logging.error(f'Error in updating the game status: {e}')

def show_warning(message):
    '''
    Shows a message in the window for 3 seconds.

    message: The message to show
    '''
    win.fill((128,128,128))
    logging.debug(f"Showing message on screen: {message} for 3 seconds.")
    font = pygame.font.SysFont(None, 40)
    text_surface = font.render(message, True, (0, 0, 0))
    win.blit(text_surface, (WIDTH/2 - text_surface.get_width()/2, HEIGHT/2 - text_surface.get_height()/2))
    pygame.display.update()
    pygame.time.delay(3000)

def update_info_text(message):
    '''
    Update the text shown on top of the game area.

    message: The message to show
    '''
    global info_text
    info_text = message
    logging.info(f"Info text updated: {message}")

def get_clicked_cell(pos):
    '''
    Return the position (x,y) of the shell in game grid, that the user clicks

    pos: Position of the mouse click action
    '''
    x, y = pos
    cell_x = x // CELL_SIZE - 1
    cell_y = y // CELL_SIZE - 1
    return cell_x, cell_y

def login_screen(server_addr):
    '''
    Draw the login screen to let the user to enter credentials and log in to the server

    server_addr: Server address (address, port)
    '''
    global client_socket
    text_input = ''
    secret_input = ''
    text_input_2 = ''
    clock = pygame.time.Clock()
    authenticate = True
    auth_status = 0
    try:
        # Ask username and password from the user via GUI
        while authenticate:
            clock.tick(60)
            win.fill((128,128,128))
            if auth_status == 0:
                font = pygame.font.SysFont(None, 40)
                text = font.render("Enter username: ", 1, (0, 0, 0))
                win.blit(text, (WIDTH/2 - text.get_width()/2, HEIGHT/3 - text.get_height()/3))

                font = pygame.font.SysFont(None, 22)
                text_surface = font.render(text_input, True, (0, 0, 0))
                win.blit(text_surface, (WIDTH/2 - text_surface.get_width()/2, HEIGHT/2 - text_surface.get_height()/2))

                btns[0].draw(win)
                pygame.display.update()
                pygame.time.delay(10)

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()

                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_BACKSPACE:
                            text_input = text_input[:-1]
                        elif event.key == pygame.K_RETURN:
                            auth_status = 1
                        else:
                            text_input += event.unicode

                    if event.type == pygame.MOUSEBUTTONDOWN:
                        pos = pygame.mouse.get_pos()
                        if btns[0].click(pos):
                            auth_status = 1
            elif auth_status == 1:
                font = pygame.font.SysFont(None, 40)
                text = font.render("Enter password: ", 1, (0, 0, 0))
                win.blit(text, (WIDTH/2 - text.get_width()/2, HEIGHT/3 - text.get_height()/3))

                font = pygame.font.SysFont(None, 22)
                text_surface = font.render(text_input_2, True, (0, 0, 0))
                win.blit(text_surface, (WIDTH/2 - text_surface.get_width()/2, HEIGHT/2 - text_surface.get_height()/2))

                btns[0].draw(win)
                pygame.display.update()
                pygame.time.delay(10)

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        run = False
                        pygame.quit()
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_BACKSPACE:
                            secret_input = secret_input[:-1]
                            text_input_2 = text_input_2[:-1]
                        elif event.key == pygame.K_RETURN:
                            authenticate = False
                            auth_status = 0
                        else:
                            secret_input += event.unicode
                            text_input_2 += '*'
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        pos = pygame.mouse.get_pos()
                        if btns[0].click(pos):
                            authenticate = False
                            auth_status = 0
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(server_addr)
        response = pickle.loads(client_socket.recv(2048))
        client_socket.sendall(pickle.dumps("player"))
        response = pickle.loads(client_socket.recv(2048))
        logging.info(f'Response from the server: {response}')
        if (response == "Game is full"):
            show_warning("Game is full")
            return False
        else:
            response = pickle.loads(client_socket.recv(2048))
            reply = text_input
            client_socket.sendall(pickle.dumps(reply))
            response = pickle.loads(client_socket.recv(2048))
            logging.info(f'Response from the server: {response}')
            reply = hashlib.sha256(secret_input.encode()).hexdigest()
            client_socket.sendall(pickle.dumps(reply))
            response = pickle.loads(client_socket.recv(2048))
            logging.info(f'Response from the server: {response}')
            return True
    except:
        pygame.time.delay(1500)
        return False

def player_screen():
    '''
     Draw the player screen

    '''
    global slots
    clock = pygame.time.Clock()
    runGame = True
    my_turn = False
    while runGame:
        clock.tick(60)
        win.fill((128,128,128))
        btns[3].draw(win)
        draw_empty_grid()
        try:
            response = pickle.loads(client_socket.recv(2048)).split(':')
            tag = response[0]
            message = response[1]
            winner = 0
            # Server is sending the game status, update it
            if tag == 'status':
                update_grid_status(message)
                if (len(response)>2):
                    winner = int(response[2])
                # Check if game is ended
                if (winner != 0):
                    if (winner == 1):
                        update_info_text('Player 1 won! New game starting soon.')
                    elif (winner == 2):
                        update_info_text('Player 2 won! New game starting soon.')
                    elif (winner == 3):
                        update_info_text('Tie game. New game starting soon.')
            else:
                update_info_text(message)
            draw_game_window()
            # If it's this player's turn, wait for the move to send it to the server
            if tag == '100':
                my_turn = True
                while my_turn:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                        if event.type == pygame.MOUSEBUTTONDOWN:
                            pos = pygame.mouse.get_pos()
                            if btns[3].click(pos):
                                runGame = False
                                break
                            clicked_cell = get_clicked_cell(pos)
                            grid_index = clicked_cell[1] * 3 + clicked_cell[0]
                            if my_turn and clicked_cell[0] < 3 and clicked_cell[1] < 3 and int(slots[grid_index]) == 0:
                                client_socket.sendall(pickle.dumps(str(grid_index)))
                                my_turn = False
                                break
            else:
                my_turn = False
        except:
            pygame.time.delay(1000)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if btns[3].click(pos):
                    runGame = False
                    break

def viewer_screen(server_addr):
    '''
     Draw the viewer screen

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
        win.fill((128,128,128))
        btns[3].draw(win)
        draw_empty_grid()
        try:
            response = pickle.loads(client_socket.recv(2048)).split(':')
            tag = response[0]
            message = response[1]
            winner = 0
            # Server is sending the game status, update it
            if tag == 'status':
                update_grid_status(message)
                if (len(response)>2):
                    winner = int(response[2])
                # Check if game is ended
                if (winner != 0):
                    if (winner == 1):
                        update_info_text('Player 1 won! New game starting soon.')
                    elif (winner == 2):
                        update_info_text('Player 2 won! New game starting soon.')
                    elif (winner == 3):
                        update_info_text('Tie game. New game starting soon.')
            else:
                update_info_text(message)
            draw_game_window()
        except:
            pygame.time.delay(1000)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if btns[3].click(pos):
                    stay_viewer = False
                    break

# Initialize used buttons
btns = [Button("Continue", 200, 400, BLACK), Button("Join as a player", 200, 250, BLACK), Button("Join as a viewer", 200, 400, BLACK), Button("Exit to menu", 200, 520, (255,0,0), 220, 60)]

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

    # Configure logging
    logging.basicConfig(filename='client.log', filemode='w',
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

    run = True
    clock = pygame.time.Clock()

    while run:
        clock.tick(60)
        win.fill((128, 128, 128))
        font = pygame.font.SysFont(None, 60)
        text = font.render("Tic-tac-toe game", 1, BLACK)
        win.blit(text, (120,100))
        btns[1].draw(win)
        btns[2].draw(win)
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if btns[1].click(pos):
                    logging.info("'Join as a player' selected.")
                    if (login_screen(server_addr)):
                        player_screen()
                        break
                    else:
                        break
                elif btns[2].click(pos):
                    logging.info("'Join as a viewer' selected.")
                    viewer_screen(server_addr)
                    break

while True:
    menu_screen()