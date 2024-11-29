import socket
import sys
from concurrent.futures import ThreadPoolExecutor
import threading
import time

BUF_SIZE = 100 * 1024
BACKLOG = 5


class Server:
    def handle_client(self, conn, addr, buf_size):

        # sleep added, because socket.accept was taking more time than handling connection
        time.sleep(3)

        # for presentation purpose
        thread_name = threading.current_thread().name
        thread_id = threading.get_ident()

        with conn:
            print(
                f"Connect from {addr} handled by thread with name {thread_name} and id {thread_id}"
            )
            i = 1
            while True:
                # receive data
                data = conn.recv(buf_size)
                if not data:
                    break
                # resend data as an answer
                conn.sendall(data)
            print("sending buffer #", i)
            i += 1
            conn.close()
        print("Connection closed by client")
        return 0

    def __init__(self, host, port, buf_size=BUF_SIZE, backlog=BACKLOG):
        self.host = host
        self.port = port
        self.buf_size = buf_size
        self.backlog = backlog

    def server_loop(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as self.socket:
            print(f"Server started with hostname {self.host} on port {self.port}")
            # binds local address to socket
            self.socket.bind((self.host, self.port))
            # put the socket in listening mode
            self.socket.listen(self.backlog)
            self.communicate()

    def communicate(self):
        # main communication loop
        with ThreadPoolExecutor(max_workers=self.backlog) as executor:
            while True:
                # accept connections
                conn, addr = self.socket.accept()
                # create a thread for handling the client connection
                executor.submit(self.handle_client, conn, addr, self.buf_size)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        raise Exception
    HOST = sys.argv[1]
    PORT = int(sys.argv[2])

    server = Server(HOST, PORT)
    server.server_loop()
