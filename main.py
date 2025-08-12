import socket
import threading

# building a class to parse the RESP stuff, trying 2 keep everything in bytes
class RESPParser:
    def __init__(self):
        self.buffer = b""
    
    def feed(self, data: bytes):
        self.buffer += data

    def _read_line(self, pos):
        end = self.buffer.find(b'\r\n', pos)
        if end == -1:
            return None, pos # not enough data to read a line
        return self.buffer[pos:end], end + 2

    # we're only doing simple commands for now
    def parse_next(self):
        if not self.buffer.startswith(b'*'):
            return None

        line, pos = self._read_line(1)
        if line is None:
            return "not enough data"
        try:
            num_items = int(line)
        except ValueError:
            return "invalid number of items"
        
        items = []
        for _ in range(num_items):
            if pos >= len(self.buffer) or self.buffer[pos:pos+1] != b'$':
                return None
            
            line, pos = self._read_line(pos + 1)
            
            if line is None:
                return None
            
            bulk_length = int(line)

            # check for complete strings
            if pos + bulk_length + 2 > len(self.buffer):
                return None
            
            item = self.buffer[pos:pos + bulk_length]
            items.append(item)
            pos += bulk_length + 2
        
        self.buffer = self.buffer[pos:]  # remove processed data
        return items

def main():
    server_socket = socket.create_server(("localhost", 6379), reuse_port=True)
    RESP_parser = RESPParser()
    
    # create general functions to handle client connections
    def handle_client(client_socket):
        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            RESP_parser.feed(data)

            # now lets handle the commands
            while True:
                command = RESP_parser.parse_next()
                if command is None:
                    break
                print(f"Received command: {command}")

                # echo
                if command[0] == b'ECHO':
                    msg = command[1]
                    client_socket.sendall(b"$" + str(len(msg)).encode() + b"\r\n" + msg + b"\r\n")

                # ping
                if command[0] == b'PING':
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
