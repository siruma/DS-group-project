# Test the server functions
import pytest
import pickle
import socket
import threading
import time
from server import run_server

# Define constants for test configuration
TEST_HOST = 'localhost'
TEST_PORT = 8080

# Define test cases
def test_server_connection():
    # Start the server in a separate thread
    server_thread = threading.Thread(target=run_server, args=(TEST_HOST, TEST_PORT))
    server_thread.start()
    time.sleep(1) 
    
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_addr =  (TEST_HOST, TEST_PORT)
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
        for i in range(0,10):
            reply = f'Data for game {i}'
            client_socket.sendall(pickle.dumps(reply))
            response = pickle.loads(client_socket.recv(2048))
            print(response)
    except Exception as e:
        print("Error:", e)

    finally:
        # Close the socket
        client_socket.close()
        server_thread.join(10)  # Wait for the server thread to finish


if __name__ == "__main__":
    pytest.main(['-v'])