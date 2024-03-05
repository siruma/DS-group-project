# Test the server functions
import pickle
import socket

def run():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_addr =  ('localhost', 8080)
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


if __name__ == "__main__":
    run()