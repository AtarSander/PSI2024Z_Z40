import socket
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from queue import Queue
from utils import generate_key, encrypt, decrypt, generate_mac
import base64


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
        self.session_keys = {}
        self.socket = None

        self.log_queue = Queue()
        self.real_time = False

        self.executor = None

    def start(self):
        # Create a socket
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
        # Bind the socket to address and port
        self.socket.bind((self.host, self.port))

        # Enable accepting connections on server's socket
        self.socket.listen(self.backlog)

        # logging
        print(f"Server started on {self.host}:{self.port}")

    def accept_clients(self):
        # Create a thread pool to handle incoming connections
        self.executor = ThreadPoolExecutor(max_workers=self.backlog)

        while self.running:
            try:
                # Accept a new connection
                conn, addr = self.socket.accept()
            except OSError:
                break

            # Add the new connection to the list of connected clients
            # with a lock to prevent race conditions
            with self.lock:
                self.connected_clients.append((conn, addr))

            # Handle the new connection in a separate thread
            self.executor.submit(self.handle_client, conn, addr)

        # Shutdown the executor when the server is stopped
        self.executor.shutdown(wait=True, cancel_futures=False)

    def handle_client(self, conn, addr):
        with conn:
            self.log(f"New connection from {addr}")
            
            # Session key exchange
            self.server_hello(conn)

            while self.running:
                # Receive data from connected client
                data = conn.recv(self.buf_size)
                if not data:
                    break
                
                # Separate MAC and encoded message
                mac, encoded_msg = self.separate_data(data)
                time.sleep(0.5)

                # Verify MAC and decrypt message
                if (
                    generate_mac(encoded_msg, self.session_keys[conn])
                    != mac
                ):
                    self.log(f"MAC verification failed for client {addr}")
                    response = "ERROR: MAC verification failed"
                else:
                    # Decode the message from bytes to string
                    decoded_msg = encoded_msg.decode('ascii')
                    # Decrypt the message
                    decrypted_msg = decrypt(decoded_msg, self.session_keys[conn])

                    self.log(f"Message from {addr}: {decrypted_msg}")

                    # Check if the client wants to exit
                    if decrypted_msg == "exit":
                        response = encrypt("exit", self.session_keys[conn])
                        self.log(f"Connection closed with {addr}")
                        conn.sendall(str.encode(response))
                        break
                    else:
                        # Create response message
                        response = encrypt(
                            f"ACK: {addr} received", self.session_keys[conn]
                        )

                # Send the response to the client
                conn.sendall(str.encode(response))

            # Disconnect the client
            self.disconnect_client(conn, addr)

    def server_hello(self, conn):
        # Receive client's public key
        client_key = conn.recv(self.buf_size).decode("ascii")
        print(f"[RECEIVED] Client_key", client_key, "length: ", len(client_key))

        # Send server's public key
        conn.sendall(str.encode(self.public_key))
        print(f"[SENT] Server_key", str.encode(self.public_key), "length: ", len(str.encode(self.public_key)))

        # Create a common key by concatenating server's and client's public keys
        common_key = self.public_key + client_key
    
        # Generate a secret key
        secret_key = generate_key()
        # Encrypt the common key with the secret key
        common_encrypted = encrypt(common_key, secret_key)
        # Send the encrypted common key to the client
        conn.sendall(str.encode(common_encrypted))
        print(f"[SENT] Common_encrypted", str.encode(common_encrypted), "length: ", len(str.encode(common_encrypted)))
        time.sleep(0.1)

        # Receive the encrypted client's common key
        encrypted_client = conn.recv(self.buf_size).decode("ascii")
        print(f"[RECEIVED] Encrypted_client", encrypted_client, "length: ", len(encrypted_client))
    
        # Store the session key for the client
        with self.lock:
            # Encrypt the client's common key with the secret key
            self.session_keys[conn] = encrypt(encrypted_client, secret_key)


    def stop(self):
        # Change the server state to stop
        self.running = False
        
        if self.socket:
            # Close the server socket
            self.socket.close()
        
        while self.connected_clients:
            # Disconnect all connected clients
            self.disconnect_client_by_index(0)
        
        if self.executor:
            # Shutdown the thread executor
            self.executor.shutdown(wait=False, cancel_futures=True)
        
        # Logging
        print("Server stopped.")

    def disconnect_client(self, conn, addr):
        # Close the connection with the client
        conn.close()
        with self.lock:
            # Remove the client from the list of connected clients
            if (conn, addr) in self.connected_clients:
                self.connected_clients.remove((conn, addr))
                self.session_keys.pop(conn)

    def disconnect_client_by_index(self, index):
        with self.lock:
            if 0 <= index < len(self.connected_clients):
                # Disconnect the client at the specified index
                conn, addr = self.connected_clients[index]

                # Send exit message to the client
                exit_msg = encrypt("exit", self.session_keys[conn])
                conn.sendall(str.encode(exit_msg))

                # Wait for the client to close the connection
                time.sleep(1)

                # Close the connection and remove the client from the list
                conn.close()
                self.connected_clients.pop(index)
                self.session_keys.pop(conn)

                # Logging
                self.log(f"Client {addr} disconnected.")

    def separate_data(self, data):
        mac = data[:32]
        encoded_msg = data[32:]
        return mac, encoded_msg

    def get_connected_clients(self):
        return self.connected_clients

    def log(self, message: str):
        # Log the message in real-time or queue it for later
        if self.real_time:
            print(message)
        else:
            self.log_queue.put(message)

    def flush_and_print_logs(self):
        # Print all queued log messages
        while not self.log_queue.empty():
            msg = self.log_queue.get()
            print(msg)
        self.real_time = True

    def disable_real_time(self):
        self.real_time = False


class ServerUI:
    def __init__(self, server: Server):
        self.server = server
        self.show_menu = True

    def display_menu(self):
        print("\nServer Menu:")
        print("1. Connection logs")
        print("2. Manage connections")
        print("3. Stop server")
        print("Choose an option: ")

    def run(self):
        try:
            self.server.start()
            server_thread = threading.Thread(
                target=self.server.accept_clients, daemon=True
            )
            server_thread.start()

            while self.server.running:
                if self.show_menu:
                    self.display_menu()
                choice = input().strip()

                if choice == "1":
                    self.show_menu = False
                    print("Enter 'm' to return to the main menu.\n")
                    self.server.flush_and_print_logs()

                elif choice == "2":
                    self.server.disable_real_time()
                    self.disconnect_client()

                elif choice == "3":
                    print("Stopping server...")
                    self.server.stop()
                    break
                elif choice == "m":
                    self.show_menu = True
                    self.server.disable_real_time()
                else:
                    print("Invalid choice. Please try again.")
        except Exception as e:
            print(f"Error running server UI: {e}")

    def show_connected_clients(self):
        clients = self.server.get_connected_clients()
        if not clients:
            print("No clients connected.")
        else:
            print("Connected clients:")
            for index, (_, addr) in enumerate(clients):
                print(f"{index}: {addr}")

    def disconnect_client(self):
        clients = self.server.get_connected_clients()
        self.show_connected_clients()
        if not clients:
            return

        try:
            index = int(input("Enter the client index to disconnect: ").strip())
            if 0 <= index < len(clients):
                self.server.disconnect_client_by_index(index)
            else:
                print("Invalid index.")
        except ValueError:
            print("Invalid input. Please enter a number.")


if __name__ == "__main__":
    backlog = BACKLOG
    if len(sys.argv) >= 4:
        backlog = int(sys.argv[3])
    if len(sys.argv) >= 3:
        host = sys.argv[1]
        port = int(sys.argv[2])
    else:
        host = "0.0.0.0"
        port = 8000

    server_logic = Server(host, port, backlog=backlog)
    server_ui = ServerUI(server_logic)
    server_ui.run()
