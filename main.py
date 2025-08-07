import socket
import threading


def main():
    server_socket = socket.create_server(("localhost", 6379), reuse_port=True)
    
    # create general functions to handle client connections
    def handle_client(client_socket):
        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            client_socket.sendall(b"+PONG\r\n")



    while True:
        # accept a new client connection
        print("Waiting for client connection...")
        server_socket.listen(1)
        # accept the connection
        connection, _ = server_socket.accept() # wait for client
        print("Client connected")

        # start a new thread to handle the client
        client_thread = threading.Thread(target=handle_client, args=(connection,))
        client_thread.start()


if __name__ == "__main__":
    main()
