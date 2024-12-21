import socket
import sys
import threading
import time
from utils import generate_key, encrypt, decrypt, generate_mac
from concurrent.futures import ThreadPoolExecutor
from multimethod import multimethod

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
        self.session_key = None
        self.socket = None

    def start(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.host, self.port))
        self.socket.listen(self.backlog)
        print(f"Server started on {self.host}:{self.port}")

    def stop(self):
        self.running = False
        with self.lock:
            for conn, _ in self.connected_clients:
                self.disconnect_client(conn)
        if self.socket:
            self.socket.close()
        print("Server stopped.")

    def accept_clients(self):
        with ThreadPoolExecutor(max_workers=self.backlog) as executor:
            while self.running:
                try:
                    conn, addr = self.socket.accept()
                    with self.lock:
                        self.connected_clients.append((conn, addr))
                    executor.submit(self.handle_client, conn, addr)
                except Exception as e:
                    print(f"Error accepting clients: {e}")
                    break

    def handle_client(self, conn, addr):
        with conn:
            print(f"New connection from {addr}")
            self.server_hello(conn)
            while True:
                data = conn.recv(self.buf_size)
                if not data:
                    break
                mac, encrypted_msg = self.separate_data(data)
                if generate_mac(encrypted_msg.encode("ascii"), self.session_key) != mac:
                    print(f"MAC verification failed for client {addr}")
                    response = "ERROR: MAC verification failed"
                else:
                    decrypted_msg = decrypt(encrypted_msg, self.session_key)
                    print(f"Message from {addr}: {decrypted_msg}")
                    if decrypted_msg == "exit":
                        response = encrypt("exit", self.session_key)
                        print(f"Connection closed with {addr}")
                        conn.sendall(str.encode(response))
                        break
                    else:
                        response = encrypt(f"ACK: {addr} received", self.session_key)
                conn.sendall(str.encode(response))
            self.disconnect_client(conn, addr)

    def disconnect_client(self, conn, addr):
        conn.close()
        with self.lock:
            self.connected_clients.remove((conn, addr))

    def disconnect_client_by_index(self, index):
        response = encrypt("exit", self.session_key)
        self.connected_clients[index][0].sendall(str.encode(response))
        time.sleep(1)
        self.connected_clients[index][0].close()
        with self.lock:
            self.connected_clients.pop(index)

    def server_hello(self, conn):
        secret_key = generate_key()
        client_key = conn.recv(self.buf_size).decode("ascii")
        conn.sendall(str.encode(self.public_key))
        common_key = self.public_key + client_key
        common_encoded = encrypt(common_key, secret_key)
        conn.sendall(str.encode(common_encoded))
        encoded_client = conn.recv(self.buf_size).decode("ascii")
        self.session_key = encrypt(encoded_client, secret_key)

    def separate_data(self, data):
        mac = data[:32]
        encrypted_msg = data[32:].decode("ascii")
        return mac, encrypted_msg

    def get_connected_clients(self):
        return self.connected_clients


class ServerUI:
    def __init__(self, server: Server):
        self.server = server

    def display_menu(self):
        print("\nServer Menu:")
        print("1. Manage connections")
        print("2. Stop server")

    def run(self):
        try:
            self.server.start()
            server_thread = threading.Thread(
                target=self.server.accept_clients, daemon=True
            )
            server_thread.start()

            while self.server.running:
                self.display_menu()
                choice = input("Choose an option: ").strip()
                if choice == "1":
                    self.disconnect_client()
                elif choice == "2":
                    print("Stopping server...")
                    self.server.stop()
                    break
                else:
                    print("Invalid choice. Please try again.")
        except Exception as e:
            print(f"Error running server UI: {e}")

    def show_connected_clients(self):
        clients = self.server.get_connected_clients()
        if not clients:
            print("No clients to disconnect.")
            return
        else:
            print("Connected clients:")
            for index, params in enumerate(clients):
                print(f"{index}: {params[1]}")

    def disconnect_client(self):
        clients = self.server.get_connected_clients()
        self.show_connected_clients()
        try:
            if len(clients) > 0:
                index = int(input("Enter the client index to disconnect: ").strip())
                if 0 <= index < len(clients):
                    self.server.disconnect_client_by_index(index)
                    print(f"Client {index} disconnected.")
                else:
                    print("Invalid index.")
        except ValueError:
            print("Invalid input. Please enter a number.")


if __name__ == "__main__":
    host = sys.argv[1]
    port = int(sys.argv[2])
    server_logic = Server(host, port)
    server_ui = ServerUI(server_logic)
    server_ui.run()
