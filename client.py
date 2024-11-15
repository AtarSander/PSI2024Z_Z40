import socket
import sys
import io
from utils import generate_msg, fletcher16

HOST = "0.0.0.0"
START_BUF_SIZE = 5


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise Exception
    port = int(sys.argv[1])

    bufsize = START_BUF_SIZE

    for msg in generate_msg(1):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            binary_stream = io.BytesIO()
            len_bin = bin(len(msg))
            len_bin = len_bin.zfill(16 - len(len_bin))

            checksum = bin(fletcher16(msg))
            checksum = checksum.zfill(16 - len(checksum))

            binary_stream.write((len_bin + checksum + msg).encode("ascii"))
            binary_stream.seek(0)
            stream_data = binary_stream.read()
            s.sendto(stream_data, (HOST, port))
            data = s.recv(bufsize)
            print("Received data=", repr(data), " size= ", len(data))
            print("Client finished.")
            bufsize += 1
