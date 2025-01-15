import socket
import sys
import io
import threading
from utils import generate_key, encrypt, decrypt, generate_mac
import time

HOST = "127.0.0.1"
BUF_SIZE = 1024


class Client:
    def __init__(self, host, port, buf_size=BUF_SIZE):
        self.host = host
        self.port = port
        self.buf_size = buf_size
        self.public_key = generate_key()
        self.stop_event = threading.Event()

    def connect(self):
        # Create a socket
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Connect to the server
        self.socket.connect((self.host, self.port))

        # Session key exchange
        self.client_hello()

    def client_hello(self):
        # Send public key to server
        self.socket.sendall(str.encode(self.public_key))
        print(f"[SENT] Client_key", str.encode(self.public_key), "length: ", len(str.encode(self.public_key)))
        
        # Receive server's public key
        server_key = self.socket.recv(self.buf_size).decode("ascii")
        print(f"[RECEIVED] Server_key", server_key, "length: ", len(server_key))
        
        # Create a common key by concatenating server's public key with client's
        common_key = server_key + self.public_key

        # Generate a secret key
        secret_key = generate_key()
        # Encrypt the common key with the secret key
        common_encrypted = encrypt(common_key, secret_key)
        # Send the encrypted common key to the server
        self.socket.sendall(str.encode(common_encrypted))
        print(f"[SENT] Common_encrypted", str.encode(common_encrypted), "length: ", len(str.encode(common_encrypted)))

        # Receive the encrypted server key
        encrypted_server = self.socket.recv(self.buf_size).decode("ascii")
        print(f"[RECEIVED] encrypted_server", encrypted_server, "length: ", len(encrypted_server))

        # Store the session key
        self.session_key = encrypt(encrypted_server, secret_key)

    def send_message(self, message):
        # Encrypt the message
        encrypted_message = encrypt(message, self.session_key)
        # Encode the message
        encoded_message = encrypted_message.encode("ascii")
        # Generate a MAC
        mac = generate_mac(encoded_message, self.session_key)
        time.sleep(0.5)
        # Prepare the message to be sent
        binary_stream = io.BytesIO()
        binary_stream.write(mac)
        binary_stream.write(encoded_message)
        binary_stream.seek(0)

        # Send the message
        self.socket.sendall(binary_stream.read())

    def receive_message(self):
        # Wait for the server to send a message
        data = self.socket.recv(self.buf_size)
        if not data:
            raise ConnectionError("Server closed connection.")
        # Decode the message
        decoded_response = data.decode("ascii")
        # Decrypt the message
        decrypted_response = decrypt(decoded_response, self.session_key)
    
        return decrypted_response

    def close(self):
        # Close the connection
        self.stop_event.set()
        self.socket.close()


class ClientUI:
    def __init__(self, client: Client):
        self.client = client

    def run(self):
        print("Establishing connection...")
        try:
            self.client.connect()
            print("Key exchange successful. Enter your messages below.")
        except Exception as e:
            print(f"Failed to connect: {e}")
            return

        listen_thread = threading.Thread(
            target=self.listen_for_server_messages, daemon=True
        )
        listen_thread.start()

        while not self.client.stop_event.is_set():
            try:
                message = input()
                self.client.send_message(message)
                if message.lower() == "exit":
                    self.is_exiting = True
                    print("Client closing connection...")
                    break
            except Exception as e:
                print(f"Error: {e}")
                break

        self.client.stop_event.set()
        listen_thread.join()
        print("Client UI exiting.")

    def listen_for_server_messages(self):
        while not self.client.stop_event.is_set():
            try:
                response = self.client.receive_message()
                print(f"\nServer response: {response}")
                if response.lower() == "exit":
                    print("Server closed connection.")
                    if not self.is_exiting:
                        print("Press enter to exit.")
                    self.client.stop_event.set()
                    break
            except Exception as e:
                print(f"Press enter to exit.")
                self.client.stop_event.set()
                break


if __name__ == "__main__":
    host = sys.argv[1]
    port = int(sys.argv[2])
    client_logic = Client(host, port)
    client_ui = ClientUI(client_logic)
    client_ui.run()
