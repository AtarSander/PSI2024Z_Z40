import socket
import sys
import io
from time import perf_counter
from utils import generate_msg, fletcher16, data_to_binarystream

BUF_SIZE = 512
START_ALTERNATING_BIT = 0b00000000
TIMEOUT = 5


class Client:
    def __init__(self, host, port, buf_size, start_abp, timeout):
        self.host = host
        self.port = port
        self.buf_size = buf_size
        self.alternating_bit = start_abp
        self.timeout = timeout

    def client_loop(self, num_of_datagrams):
        msg = generate_msg(self.buf_size - 5)
        # create socket
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as self.socket:
            print(
                f"Client communicating with servername: {self.host} and server port: {self.port}"
            )
            for i in range(num_of_datagrams):
                print(f"Sending message #{i}")
                while self.communicate(msg) == -1:
                    print(f"Resending message #{i}")
        print("Client finished.")  # log when all messages have been sent.

    def communicate(self, message):
        binary_stream = io.BytesIO()
        # calculate length of the message and add 4 bytes reserved for
        # datagram length and checksum
        len_bin = (len(message) + 4).to_bytes(2)

        # calculate checksum based on message
        checksum = fletcher16(message)
        checksum_bytes = checksum.to_bytes(2)

        abp = self.alternating_bit.to_bytes(1)

        stream_data = data_to_binarystream(
            binary_stream, abp, len_bin, checksum_bytes, message.encode("ascii")
        )

        # send the UDP datagram
        send_time = perf_counter()
        self.send_datagram(stream_data, message)
        # wait for response, if timeout occurs return -1 signalizing lost packet
        try:
            self.socket.settimeout(self.timeout)
            data = self.socket.recv(self.buf_size)
            delta_time = perf_counter() - send_time
            received_abp, _ = self.seperate_data(data)
            response_code = self.response_validation(received_abp)
            if response_code == 0:
                print(f"recv OK, communication time: {delta_time}")
            return response_code
        except socket.timeout:
            print("Timeout occurred while waiting for response.")
            return -1
        except Exception as e:
            print(f"Unexpected error: {e}")
            return -1

    def send_datagram(self, stream_data, message):
        try:
            self.socket.sendto(stream_data, (self.host, self.port))
        except OSError:
            print(f"Message of length {len(message)} too long")
            return -1

    def response_validation(self, received_abp):
        # validate the response
        if received_abp == self.alternating_bit:
            self.alternating_bit = self.alternating_bit ^ 0b00000001
            return 0
        else:
            return -1

    def seperate_data(self, data):
        abp = data[0]
        msg_len = int.from_bytes(data[1:3], byteorder="big")

        return abp, msg_len


if __name__ == "__main__":
    if len(sys.argv) < 4:
        raise Exception
    HOST = sys.argv[1]
    PORT = int(sys.argv[2])
    num_of_datagrams = int(sys.argv[3])

    client = Client(HOST, PORT, BUF_SIZE, START_ALTERNATING_BIT, TIMEOUT)
    client.client_loop(num_of_datagrams)
