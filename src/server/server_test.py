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
TIMEOUT = 10
USER = 'user'
PASSWORD = 'password'


def randomize_string(str):
    chars = list(str)
    random.shuffle(chars)
    return ''.join(chars)


def test_authentication():
    print("\nStart authentication test")
    authen = Authentication()
    authen.register_user(USER, PASSWORD)
    assert authen.authenticate_user(USER, PASSWORD)
    authen.close_database()


def test_authentication_multi():
    print("\nStart authentication with multiple user test")
    authen = Authentication()
    authen.register_user(USER, PASSWORD)
    authen.register_user(randomize_string(USER), randomize_string(PASSWORD))
    authen.register_user(randomize_string(USER), randomize_string(PASSWORD))
    authen.register_user(randomize_string(USER), randomize_string(PASSWORD))
    assert authen.authenticate_user(USER, PASSWORD)
    authen.close_database()


# Helper function for clients
def client(server_addr, ID):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(server_addr)
    response = pickle.loads(client_socket.recv(2048))
    print(f"{ID}: Response from server:{response}")
    response = pickle.loads(client_socket.recv(2048))
    print(f"{ID}: {response}")
    reply = f'user_test{ID}'
    client_socket.sendall(pickle.dumps(reply))
    response = pickle.loads(client_socket.recv(2048))
    print(f"{ID}: {response}")
    reply = hashlib.sha256('password123'.encode()).hexdigest()
    client_socket.sendall(pickle.dumps(reply))
    response = pickle.loads(client_socket.recv(2048))
    print(f"{ID}: {response}")
    response_code = '100'
    index = 0
    while True:
        if (index == 4):
            break
        response = pickle.loads(client_socket.recv(2048))
        response_code = response[:3]
        print(f"{ID}: {response}")
        if (response_code == '100'):
            reply = f'Data for game {index}'
            client_socket.sendall(pickle.dumps(reply))
            response = pickle.loads(client_socket.recv(2048))
            print(f"{ID}: {response}")
            index += 1
        else:
            time.sleep(10)
    client_socket.close()


# Define test cases
def test_server_connection():
    print("\nStart test")
    threads = []
    # Start the server in a separate thread
    server_thread = threading.Thread(name="server", target=run_server,
                                     args=(TEST_HOST, TEST_PORT, TIMEOUT),
                                     daemon=True)
    server_thread.start()
    threads.append(server_thread)
    assert len(threads) == 1

    time.sleep(1)

    server_addr = (TEST_HOST, TEST_PORT)
    # Start the clients in a separate threads
    try:
        for i in range(2):
            client_thread = threading.Thread(name=f'client{i}', target=client,
                                             args=(server_addr, i+1))
            client_thread.start()
            threads.append(client_thread)
            time.sleep(1)
    except Exception as e:
        print("Error:", e)
    finally:
        # Close the socket
        assert len(threads) == 3
        print("Wait the sockets")
        for thread in threads:
            thread.join()  # Wait for all threads to finish


if __name__ == "__main__":
    pytest.main(['-vs'])
