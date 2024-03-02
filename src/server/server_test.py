# Test the server functions
import socket

def run():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_addr =  ('localhost', 8080)
    try:
        client_socket.connect(server_addr)
        response = client_socket.recv(2048).decode()
        print("Response from server:", response)
    except Exception as e:
        print("Error:", e)

    finally:
        # Close the socket
        client_socket.close()


if __name__ == "__main__":
    run()