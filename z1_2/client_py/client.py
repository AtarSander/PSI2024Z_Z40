import socket
import sys
import io

from utils import generate_msg, fletcher16, data_to_binarystream

BUF_SIZE = 512
START_ALTERNATING_BIT = 0b00000000


class Client:
    def __init__(self, buf_size, start_apb):
        self.buf_size = buf_size
        self.alternating_bit = start_apb

    def communicate(self, message):
        binary_stream = io.BytesIO()
        # calculate length of the message and add 4 bytes reserved for
        # datagram length and checksum

        len_bin = (len(message) + 4).to_bytes(2)
        # calculate checksum based on message
        checksum = fletcher16(message)
        checksum_bytes = checksum.to_bytes(2)
        apb = self.alternating_bit.to_bytes(1)

        stream_data = data_to_binarystream(
            binary_stream, apb, len_bin, checksum_bytes, message.encode("ascii")
        )

        # send the UDP datagram
        self.send_datagram(stream_data, message)
        data = s.recv(self.buf_size)
        received_APB, _ = self.seperate_data(data)
        return self.response_validation(received_APB)

    def send_datagram(self, stream_data, message):
        try:
            s.sendto(stream_data, (HOST, port))
        except OSError:
            print(f"Message of length {len(message)} too long")
            return -1

    def response_validation(self, received_apb):
        # validate the response
        if received_apb == self.alternating_bit:
            self.alternating_bit = self.alternating_bit ^ 0b00000001
            return 0
        else:
            return -1

    def seperate_data(self, data):
        apb = data[0]
        msg_len = int.from_bytes(data[1:3], byteorder="big")

        return apb, msg_len


if __name__ == "__main__":
    if len(sys.argv) < 4:
        raise Exception
    HOST = sys.argv[1]
    port = int(sys.argv[2])
    num_of_datagrams = int(sys.argv[3])
    msg = generate_msg(BUF_SIZE - 5)
    print(f"Client started with hostname: {HOST} and port {port}")
    client = Client(BUF_SIZE, START_ALTERNATING_BIT)
    # create socket
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        # generate messages from size 1 to size 100000
        for i in range(num_of_datagrams):
            while client.communicate(msg) == -1:
                print(f"Resending message #{i}")
    print("Client finished.")  # log when all messages have been sent.
