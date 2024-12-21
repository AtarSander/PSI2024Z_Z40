import socket
import sys
import time
import threading
from utils import generate_key, encrypt, decrypt, generate_mac
from concurrent.futures import ThreadPoolExecutor

HOST = "127.0.0.1"
BUF_SIZE = 512
BACKLOG = 10


class Server:
    def __init__(self, host, port, buf_size=BUF_SIZE, backlog=BACKLOG):
        self.host = host
        self.port = port
        self.buf_size = buf_size
        self.backlog = backlog
        self.public_key = generate_key()
        self.connected_clients = []
        self.lock = threading.Lock()
        self.running = True

    def server_hello(self, conn):
        secret_key = generate_key()
        client_key = conn.recv(self.buf_size).decode("ascii")
        conn.sendall(str.encode(self.public_key))
        common_key = self.public_key + client_key
        common_encoded = encrypt(common_key, secret_key)
        conn.sendall(str.encode(common_encoded))
        encoded_client = conn.recv(self.buf_size).decode("ascii")
        self.session_key = encrypt(encoded_client, secret_key)

    def server_loop(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as self.socket:
            print(f"Server started with hostname {self.host} on port {self.port}")
            self.socket.bind((self.host, self.port))
            self.socket.listen(self.backlog)
            self.communicate()

    def communicate(self):
        with ThreadPoolExecutor(max_workers=self.backlog) as executor:
            while self.running:
                # accept connections
                conn, addr = self.socket.accept()
                with self.lock:
                    self.connected_clients.append((conn, addr))
                executor.submit(self.handle_client, conn, addr)

    def handle_client(self, conn, addr):
        time.sleep(0.5)
        thread_name = threading.current_thread().name
        thread_id = threading.get_ident()
        with conn:
            print(
                f"Connect from {addr} handled by thread with name {thread_name} and id {thread_id}"
            )
            self.server_hello(conn)
            while True:
                data = conn.recv(self.buf_size)
                if not data:
                    break
                mac, encrypted_msg = self.seperate_data(data)
                if generate_mac(encrypted_msg.encode("ascii"), self.session_key) != mac:
                    print(f"MAC verification failed for message from {addr}")
                    response = "ERROR: MAC verification failed"
                else:
                    decrypted_msg = decrypt(encrypted_msg, self.session_key)
                    print(f"Received message from {addr}: {decrypted_msg}")
                    if decrypted_msg == "exit":
                        response = encrypt(
                            f"exit",
                            self.session_key,
                        )
                        break
                    else:
                        response = encrypt(
                            f"ACK: Communication successful with {addr}",
                            self.session_key,
                        )
                conn.sendall(str.encode(response))
        conn.close()
        with self.lock:
            self.connected_clients.remove((conn, addr))
        print(f"Connection closed by client {addr}")

    def seperate_data(self, data):
        mac = data[:32]
        encrypted_msg = data[32:].decode("ascii")
        return mac, encrypted_msg

    def print_connected(self):
        if not self.connected_clients:
            print("No clients connected.")
        else:
            print("Connected clients:")
            for idx, client in enumerate(self.connected_clients):
                print(f"{idx}. {client[1]}")

    def manage_connections(self):
        self.print_connected()
        if not self.connected_clients:
            return
        try:
            chosen = int(
                input("Enter the index of the client you want to disconnect: ")
            )
            if 0 <= chosen < len(self.connected_clients):
                self.close_client_connection(self.connected_clients[chosen][0], chosen)
                print(f"Disconnected client {chosen}")
            else:
                print("Invalid client index")
        except ValueError:
            print("Invalid input. Please enter a valid number.")

    def close_server(self):
        self.running = False
        with self.lock:
            for i, conn, _ in enumerate(self.connected_clients):
                self.close_client_connection(conn, i)
        print("Server is shutting down.")

    def close_client_connection(self, conn, chosen):
        with self.lock:
            self.connected_clients.pop(chosen)
        response = encrypt(
            "exit",
            self.session_key,
        )
        conn.sendall(str.encode(response))
        conn.close()


def display_menu():
    print("\nServer Menu:")
    print("1. Connection logs")
    print("2. Manage connections")
    print("3. Close server")


def terminal_menu(server):
    while True:
        display_menu()
        choice = input("Select an option: ")
        if choice == "1":
            pass
        elif choice == "2":
            server.manage_connections()
        elif choice == "3":
            print("Exiting program...")
            server.close_server()
            break
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    host = sys.argv[1]
    port = int(sys.argv[2])
    server = Server(host, port)

    server_thread = threading.Thread(target=server.server_loop)
    server_thread.daemon = True
    server_thread.start()
    terminal_menu(server)
