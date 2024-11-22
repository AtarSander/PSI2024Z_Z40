import socket
import sys
from utils import data_to_binarystream, fletcher16
import io

BUF_SIZE = 512
RESPONSE_LENGTH = 3


class Server:
    def __init__(self, host, port, buf_size, response_len):
        self.host = host
        self.port = port
        self.buf_size = buf_size
        self.response_len = response_len

    def server_loop(self):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as self.socket:
            # start listening on socket
            print(f"Server started with hostname {self.host} on port {self.port}")
            self.socket.bind((self.host, self.port))
            while server.communicate() != -1:
                pass

    def communicate(self):
        # receive datagram from UDP
        received_data = self.socket.recvfrom(self.buf_size)

        # extract the data and client's address
        data, address = received_data

        # error receiving datagram
        if not data:
            print("Error in datagram?")
            return -1

        alternating_bit, _, checksum, msg = self.seperate_data(data)
        # signalize lost packet by changing alternating bit
        if not self.verify_checksum(msg, checksum):
            alternating_bit = self.change_abp(alternating_bit)
        # create data to send back
        stream_data = self.create_response(self.response_len, alternating_bit)

        # log received data headers
        self.log_data(address, alternating_bit)

        # send back the datagram header
        self.send_response(stream_data, address)
        return 0

    def verify_checksum(self, message, checksum):
        received_msg_checksum = fletcher16(message)
        if checksum != received_msg_checksum:
            return False
        return True

    def change_abp(self, alternating_bit):
        return alternating_bit ^ 0b00000001

    def create_response(self, datagram_length, alternating_bit):
        received_datagram_len = datagram_length.to_bytes(2)
        binary_stream = io.BytesIO()

        return data_to_binarystream(
            binary_stream,
            alternating_bit.to_bytes(1),
            received_datagram_len,
        )

    def extract_abp_bit_value(self, abp):
        bit_position = 0
        mask = 1 << bit_position
        return (abp & mask) >> bit_position

    def log_data(self, address, abp):
        print(f"Client IP Address: {address}")
        print(f"Alternating bit: {self.extract_abp_bit_value(abp)}")

    def send_response(self, stream_data, address):
        self.socket.sendto(stream_data, address)

    def seperate_data(self, data):
        abp = data[0]
        msg_len = int.from_bytes(data[1:3], byteorder="big")
        checksum = int.from_bytes(data[3:5], byteorder="big")
        msg = data[5:].decode("ascii")

        return abp, msg_len, checksum, msg


if __name__ == "__main__":
    if len(sys.argv) < 3:
        raise Exception
    HOST = sys.argv[1]
    PORT = int(sys.argv[2])

    server = Server(HOST, PORT, BUF_SIZE, RESPONSE_LENGTH)
    server.server_loop()
