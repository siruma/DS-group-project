# Socket server for tic-tac-toe game
import socket
from _thread import *

def handle_client(client_socket):
    client_socket.send(b'Welcome')
    client_socket.close()

def run(port=8080):
    # Create TCP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind the socket to address and port
    server_address = ('localhost', port)
    server_socket.bind(server_address)

    # Listen for incoming connections
    server_socket.listen(5)
    print(f"Server is listening for connections from {port}") 

    try:
        while True:
            client_socket, client_address = server_socket.accept()
            print(f"Connection from {client_address}")

            # Handle client request
            start_new_thread(handle_client, (client_socket,))
    finally:
        # Close the connection
        server_socket.close()



if __name__ == "__main__":
    run()