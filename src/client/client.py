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
pygame.font.init()
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tic-tac-toe")
client_socket = None
slots = [0,0,0,0,0,0,0,0,0]


class Button:
    def __init__(self, text, x, y, color):
        self.text = text
        self.x = x
        self.y = y
        self.color = color
        self.width = 150
        self.height = 100

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

# Function to draw the grid
def draw_empty_grid():
    for i in range(GRID_SIZE+1):
        pygame.draw.line(win, (0, 0, 0), ((100 + i * CELL_SIZE), 100), ((100 + i * CELL_SIZE), 500), LINE_WIDTH)
        pygame.draw.line(win, (0, 0, 0), (100, (100 + i * CELL_SIZE)), (500, (100 + i * CELL_SIZE)), LINE_WIDTH)

# Function to draw the grid based on the game status from the server
def draw_grid_status(status=None):
    global slots
    if status:
       slots = status.strip()[1:-1].split(',')
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


# Function to get the index of clicked cell
def get_clicked_cell(pos):
    x, y = pos
    cell_x = x // CELL_SIZE - 1
    cell_y = y // CELL_SIZE - 1
    return cell_x, cell_y

# Initialize used buttons
btns = [Button("Continue", 220, 400, (0,0,0))]

# Main loop: 
def main():
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

    global slots
    runGame = False
    authenticate = True
    my_turn = False
    auth_status = 0
    clock = pygame.time.Clock()
    while True:
        text_input = ''
        secret_input = ''
        text_input_2 = ''
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
                            run = False
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
                                runGame = True
                                authenticate = False
                                auth_status = 0
                            else:
                                secret_input += event.unicode
                                text_input_2 += '*'
                        elif event.type == pygame.MOUSEBUTTONDOWN:
                            pos = pygame.mouse.get_pos()
                            if btns[0].click(pos):
                                runGame = True
                                authenticate = False
                                auth_status = 0
            # Handle the authentication with the server when user has set credentials
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect(server_addr)
            response = pickle.loads(client_socket.recv(2048))
            response = pickle.loads(client_socket.recv(2048))
            logging.info(f'Response from the server: {response}')
            reply = text_input
            client_socket.sendall(pickle.dumps(reply))
            response = pickle.loads(client_socket.recv(2048))
            logging.info(f'Response from the server: {response}')
            reply = hashlib.sha256(secret_input.encode()).hexdigest()
            client_socket.sendall(pickle.dumps(reply))
            response = pickle.loads(client_socket.recv(2048))
            logging.info(f'Response from the server: {response}')
        except:
            win.fill((128,128,128))
            font = pygame.font.SysFont(None, 40)
            text = font.render("Authentication failed!", 1, (255, 0, 0))
            win.blit(text, (WIDTH/2 - text.get_width()/2, HEIGHT/2 - text.get_height()/2))
            logging.info("User authentication failed")
            runGame = False
            authenticate = True
            pygame.display.update()
            pygame.time.delay(1500)
        # Updates the game view according to information from the server
        while runGame:
            clock.tick(60)
            win.fill((128,128,128))
            draw_empty_grid()
            try:
                response = pickle.loads(client_socket.recv(2048))
                [tag, message] = response.split(':')
                if tag == 'status':
                    draw_grid_status(message)
                else:
                    draw_grid_status()
                    font = pygame.font.SysFont(None, 40)
                    text = font.render(message, 1, (0, 0, 0))
                    win.blit(text, (WIDTH/2 - text.get_width()/2, HEIGHT/10 - text.get_height()/10))
            except:
                pygame.time.delay(1000)

            pygame.display.update()
            pygame.time.delay(2)

            # If it's this player's turn, wait for the move to send it to the server
            if tag == '100':
                my_turn = True
                while my_turn:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                        if event.type == pygame.MOUSEBUTTONDOWN:
                            pos = pygame.mouse.get_pos()
                            clicked_cell = get_clicked_cell(pos)
                            grid_index = clicked_cell[1] * 3 + clicked_cell[0]
                            if my_turn and clicked_cell[0] < 3 and clicked_cell[1] < 3 and int(slots[grid_index]) == 0:
                                client_socket.sendall(pickle.dumps(str(grid_index)))
                                my_turn = False
                                break
            else:
                my_turn = False
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()

while True:
    main()