import socket
import sys
import io

from utils import generate_msg, fletcher16, seperate_data, data_to_binarystream

START_BUF_SIZE = 5


def communicate(message):
    binary_stream = io.BytesIO()
    # calculate length of the message and add 4 bytes reserved for
    # datagram length and checksum
    len_bin = (len(message) + 4).to_bytes(2)
    # calculate checksum based on message
    checksum = fletcher16(message)
    checksum_bytes = checksum.to_bytes(2)

    stream_data = data_to_binarystream(binary_stream, len_bin, checksum_bytes, message)

    # send the UDP datagram
    send_datagram(stream_data, message)
    data = s.recv(START_BUF_SIZE)
    received_message_len, received_checksum, _ = seperate_data(data)
    response_validation(received_checksum, checksum)


def send_datagram(stream_data, message):
    try:
        s.sendto(stream_data, (HOST, port))
    except OSError:
        print(f"Message of length {len(message)} too long")
        return -1


def response_validation(received_checksum, checksum):
    # validate the response
    if received_checksum == checksum:
        print(f"Communication Successful #{len(msg)}")
    else:
        print("Communication Error")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        raise Exception
    HOST = sys.argv[1]
    port = int(sys.argv[2])

    print(f"Client started with hostname: {HOST} and port {port}")

    bufsize = START_BUF_SIZE
    # create socket
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        # generate messages from size 1 to size 100000
        for msg in generate_msg(100000):
            if communicate(msg) == -1:
                break
            bufsize += 1  # increment the buffer size for the next message
    print("Client finished.")  # log when all messages have been sent.
