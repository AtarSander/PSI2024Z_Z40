import socket
import sys
import io

from utils import generate_msg, fletcher16, seperate_data

HOST = "0.0.0.0"
START_BUF_SIZE = 5


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise Exception
    port = int(sys.argv[1])
    # port = 8000

    bufsize = START_BUF_SIZE

    for msg in generate_msg(100):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            binary_stream = io.BytesIO()
            len_bin = len(msg).to_bytes(2)

            checksum = fletcher16(msg)
            checksum_bytes = checksum.to_bytes(2)

            binary_stream.write(len_bin)
            binary_stream.write(checksum_bytes)
            binary_stream.write(msg.encode("ascii"))
            binary_stream.seek(0)
            stream_data = binary_stream.read()
            s.sendto(stream_data, (HOST, port))
            data = s.recv(START_BUF_SIZE)
            new_msg_len, new_checksum, _ = seperate_data(data)

            if new_msg_len == len(msg) and new_checksum == checksum:
                print("Communication Successful")
            else:
                print("Communication Error")

            bufsize += 1

    print("Client finished.")
