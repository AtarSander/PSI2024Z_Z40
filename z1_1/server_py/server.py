import socket
import sys
from utils import seperate_data, data_to_binarystream, fletcher16
import io

START_BUF_SIZE = 5


def communicate(socket, buffer_size):
    # receive datagram from UDP socket
    received_data = socket.recvfrom(buffer_size)

    # extract the data and client's address
    data, address = seperate_received_data(received_data)

    # error receiving datagram
    if not data:
        print("Error in datagram?")
        return -1

    msg_len, checksum, msg = seperate_data(data)

    # create data to send back
    stream_data = create_response(msg, 4)

    # log received data headers
    log_data(msg_len, checksum, address)

    # send back the datagram header
    send_response(socket, stream_data, address, buffer_size)


def seperate_received_data(data):
    return data[0], data[1]


def create_response(message, datagram_length):
    received_datagram_len = datagram_length.to_bytes(2)
    received_msg_checksum = fletcher16(message).to_bytes(2)
    binary_stream = io.BytesIO()

    return data_to_binarystream(
        binary_stream, received_datagram_len, received_msg_checksum
    )


def log_data(msg_len, checksum, address):
    print(f"Datagram length: {msg_len}")
    print(f"Checksum: {checksum}")
    print(f"Client IP Address: {address}")


def send_response(socket, stream_data, address, buffer_size):
    socket.sendto(stream_data, address)
    print("sending dgram #", buffer_size - 4, "\n")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        raise Exception
    HOST = sys.argv[1]
    PORT = int(sys.argv[2])

    print(f"Server started with hostname {HOST} on port {PORT}")

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        # start listening on socket
        s.bind((HOST, PORT))
        bufsize = START_BUF_SIZE

        while True:
            if communicate(s, bufsize) == -1:
                break
            bufsize += 1
