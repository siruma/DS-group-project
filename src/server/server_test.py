# Test the server functions

import random
import pytest
import pickle
import socket
import threading
import time
import hashlib
import server
from authentication import Authentication

# Define constants for test configuration
TEST_HOST = 'localhost'
TEST_PORT = 8080
TIMEOUT = 1
USER = 'user'
PASSWORD = 'password'


def randomize_string(str):
    chars = list(str)
    random.shuffle(chars)
    return ''.join(chars)


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
    moves = [0, 1, 2, 3, 4, 5, 6, 7, 8]
    while True:
        response = pickle.loads(client_socket.recv(2048))
        response_code = response[:3]
        print(f"{ID}: {response}")
        if (response_code == '100'):
            print(f"{ID}: Wait the game grid")
            game_grid = pickle.loads(client_socket.recv(2048))
            random_move = random.choice(moves)
            moves.remove(random_move)
            print(f"{ID} move: {random_move}")
            client_socket.sendall(pickle.dumps(random_move))
            response = pickle.loads(client_socket.recv(2048))
            print(f"{ID}: {response}")
            index += 1
            if (index < 4):
                print(f"{ID}: index: {index}, ok")
                client_socket.sendall(pickle.dumps('ok'))
            else:
                print(f"{ID}: quit")
                client_socket.sendall(pickle.dumps('quit'))
                time.sleep(10)
                break
        elif (response_code == '200'):
            break
        else:
            print(f"{ID} Sleep")
            time.sleep(10)
    client_socket.close()


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


# Define test cases
#@pytest.mark.skip("Not working in GitHub")  # Comment this if running locally
def test_server_connection_with_two_client():
    print("\nStart test")
    threads = []
    game_server = server.Server()
    # Start the server in a separate thread
    server_thread = threading.Thread(name="server",
                                     target=game_server.run_server,
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


# Test server authentication
#@pytest.mark.skip("Not working in GitHub")  # Comment this if running locally
def test_server_connection():
    print("\nStart test")
    # Start the server in a separate thread
    game_server = server.Server()
    server_thread = threading.Thread(target=game_server.run_server,
                                     args=(TEST_HOST, TEST_PORT, TIMEOUT),
                                     daemon=True)
    server_thread.start()
    time.sleep(1)

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_addr = (TEST_HOST, TEST_PORT)
    try:
        client_socket.connect(server_addr)
        response = pickle.loads(client_socket.recv(2048))
        print("Response from server:", response)
        response = pickle.loads(client_socket.recv(2048))
        print(response)
        reply = 'user'
        client_socket.sendall(pickle.dumps(reply))
        response = pickle.loads(client_socket.recv(2048))
        print(response)
        reply = 'password'
        client_socket.sendall(pickle.dumps(reply))
        response = pickle.loads(client_socket.recv(2048))
        print(response)
    except Exception as e:
        print("Error:", e)
    finally:
        # Close the socket
        client_socket.close()
        server_thread.join()  # Wait for the server thread to finish


if __name__ == "__main__":
    pytest.main(['-v'])
