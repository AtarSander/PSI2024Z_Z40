import socket
import sys
import io

from utils import generate_msg, fletcher16, seperate_data

START_BUF_SIZE = 5


if __name__ == "__main__":
    if len(sys.argv) < 3:
        raise Exception
    HOST = sys.argv[1]
    port = int(sys.argv[2])

    print(f"Client started with hostname: {HOST} and port {port}")

    bufsize = START_BUF_SIZE
    # generate messages from size 1 to size 100000
    for msg in generate_msg(100000):
        # create socket
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            binary_stream = io.BytesIO()
            # calculate length of the message and add 4 bytes reserved for
            # datagram length and checksum
            len_bin = (len(msg) + 4).to_bytes(2)

            # calculate checksum based on message
            checksum = fletcher16(msg)
            checksum_bytes = checksum.to_bytes(2)

            # write the data to binary stream
            binary_stream.write(len_bin)
            binary_stream.write(checksum_bytes)
            binary_stream.write(msg.encode("ascii"))
            binary_stream.seek(0)
            stream_data = binary_stream.read()

            # send the UDP datagram
            s.sendto(stream_data, (HOST, port))
            data = s.recv(START_BUF_SIZE)
            new_msg_len, new_checksum, _ = seperate_data(data)

            # validate the response
            if new_msg_len == len(stream_data) and new_checksum == checksum:
                print(f"Communication Successful #{len(msg)}")
            else:
                print("Communication Error")

            bufsize += 1  # increment the buffer size for the next message

    print("Client finished.")  # log when all messages have been sent.
