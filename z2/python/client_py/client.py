import socket
import sys
from utils import generate_msg
import time

# 100kB
BUF_SIZE = 100 * 1024


class Client:
    def __init__(self, host, port, buf_size):
        self.host = host
        self.port = port
        self.buf_size = buf_size

    def client_loop(self):
        msg = generate_msg(self.buf_size)

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as self.socket:
            # connect to server
            self.socket.connect((self.host, self.port))
            # send ascii-encoded message
            self.socket.sendall(msg.encode("ascii"))
            # receive response
            data = b""
            while len(data) < self.buf_size:
                chunk = self.socket.recv(self.buf_size)
                if not chunk:  # No more data
                    break
                data += chunk
            print(f"Received {len(data)}B of data")
            print(f"Client finished")


if __name__ == "__main__":
    if len(sys.argv) < 4:
        raise Exception
    HOST = sys.argv[1]
    PORT = int(sys.argv[2])
    DELAY = int(sys.argv[3])
    # delay to wait for the server to start before creating clients
    time.sleep(DELAY)

    client = Client(HOST, PORT, BUF_SIZE)
    client.client_loop()
