import socket
import sys
import io
import threading
from utils import generate_key, encrypt, decrypt, generate_mac

HOST = "127.0.0.1"
BUF_SIZE = 1024


class Client:
    def __init__(self, host, port, buf_size=BUF_SIZE):
        self.host = host
        self.port = port
        self.buf_size = buf_size
        self.public_key = generate_key()
        self.stop_event = threading.Event()

    def client_loop(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as self.socket:
            print("Establishing connection...")
            self.socket.connect((self.host, self.port))
            self.client_hello()
            print("Key exchange successful. Enter your message below.")
            listener_thread = threading.Thread(
                target=self.listen_for_server_messages, daemon=True
            )
            listener_thread.start()

            while not self.stop_event.is_set():
                message = input()

                binary_stream = io.BytesIO()
                encoded_message = encrypt(message, self.session_key).encode("ascii")
                mac = generate_mac(encoded_message, self.session_key)
                binary_stream.write(mac)
                binary_stream.write(encoded_message)
                binary_stream.seek(0)
                try:
                    self.socket.sendall(binary_stream.read())
                    if message.lower() == "exit":
                        print("Client closing connection...")
                        break
                except socket.error:
                    print("Error sending message. Connection may have been closed.")
                    break

            self.stop_event.set()
            listener_thread.join()
            print("Client loop exiting.")

    def listen_for_server_messages(self):
        while not self.stop_event.is_set():
            try:
                data = self.socket.recv(self.buf_size)
                if not data:
                    print("Server closed connection.")
                    self.stop_event.set()
                    break

                response = decrypt(data.decode("ascii"), self.session_key)
                print(f"\nServer response: {response}")

                if response.lower() == "exit":
                    print("Server closed connection. Press enter to exit.")
                    self.stop_event.set()
                    break

            except socket.error:
                print("Error receiving message from server. Press enter to exit.")
                self.stop_event.set()
                break

    def client_hello(self):
        secret_key = generate_key()
        self.socket.sendall(str.encode(self.public_key))

        server_key = self.socket.recv(self.buf_size).decode("ascii")

        common_key = server_key + self.public_key
        common_encoded = encrypt(common_key, secret_key)
        self.socket.sendall(str.encode(common_encoded))

        encoded_server = self.socket.recv(self.buf_size).decode("ascii")
        self.session_key = encrypt(encoded_server, secret_key)


if __name__ == "__main__":
    host = sys.argv[1]
    port = int(sys.argv[2])
    client = Client(host, port)
    client.client_loop()
