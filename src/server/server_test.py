# Test the server functions

import random
import pytest
import pickle
import socket
import threading
import time
import hashlib
from server import run_server
from authentication import Authentication

# Define constants for test configuration
TEST_HOST = 'localhost'
TEST_PORT = 8080
TIMEOUT = 5
USER = 'user'
PASSWORD = 'password'

def randomize_string(str):
    chars = list(str)
    random.shuffle(chars)
    return ''.join(chars)

def test_authentication():
    authen = Authentication()
    authen.register_user(USER,PASSWORD)
    assert authen.authenticate_user(USER,PASSWORD) == True
    authen.close_database()

def test_authentication_multi():
    authen = Authentication()
    authen.register_user(USER,PASSWORD)
    authen.register_user(randomize_string(USER),randomize_string(PASSWORD))
    authen.register_user(randomize_string(USER),randomize_string(PASSWORD))
    authen.register_user(randomize_string(USER),randomize_string(PASSWORD))
    assert authen.authenticate_user(USER,PASSWORD) == True
    authen.close_database()

# Define test cases
def test_server_connection():
    print("Start test")
    # Start the server in a separate thread
    server_thread = threading.Thread(target=run_server, args=(TEST_HOST, TEST_PORT, TIMEOUT),daemon=True)
    server_thread.start()
    time.sleep(1) 
    
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.settimeout(TIMEOUT+10)
    server_addr =  (TEST_HOST, TEST_PORT)
    try:
        client_socket.connect(server_addr)
        response = pickle.loads(client_socket.recv(2048))
        print("Response from server:", response)
        response = pickle.loads(client_socket.recv(2048))
        print(response)
        reply = 'user_test'
        client_socket.sendall(pickle.dumps(reply))
        response = pickle.loads(client_socket.recv(2048))
        print(response)
        reply = hashlib.sha256('password123'.encode()).hexdigest()
        client_socket.sendall(pickle.dumps(reply))
        response = pickle.loads(client_socket.recv(2048))
        print(response)
        for i in range(0,10):
            reply = f'Data for game {i}'
            client_socket.sendall(pickle.dumps(reply))
            response = pickle.loads(client_socket.recv(2048))
            print(response)
    except Exception as e:
        print("Error:", e)

    finally:
        # Close the socket
        print("Closing socket")
        client_socket.close()
        server_thread.join(5)  # Wait for the server thread to finish



if __name__ == "__main__":
    pytest.main(['-vs'])