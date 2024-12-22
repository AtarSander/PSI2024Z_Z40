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

    def connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))
        self.client_hello()

    def client_hello(self):
        secret_key = generate_key()
        self.socket.sendall(str.encode(self.public_key))
        print("sent public key \n")
        server_key = self.socket.recv(self.buf_size).decode("ascii")
        print("received server_key", server_key)
        common_key = server_key + self.public_key
        common_encoded = encrypt(common_key, secret_key)
        self.socket.sendall(str.encode(common_encoded))
        print("sent common encoded \n")

        encoded_server = self.socket.recv(self.buf_size).decode("ascii")
        print("received encoded_server", encoded_server)
        self.session_key = encrypt(encoded_server, secret_key)

    def send_message(self, message):
        encoded_message = encrypt(message, self.session_key).encode("ascii")
        mac = generate_mac(encoded_message, self.session_key)

        binary_stream = io.BytesIO()
        binary_stream.write(mac)
        binary_stream.write(encoded_message)
        binary_stream.seek(0)

        self.socket.sendall(binary_stream.read())

    def receive_message(self):
        data = self.socket.recv(self.buf_size)
        if not data:
            raise ConnectionError("Server closed connection.")
        response = decrypt(data.decode("ascii"), self.session_key)
        return response

    def close(self):
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
