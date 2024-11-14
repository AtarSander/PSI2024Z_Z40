import socket
import sys
import io
import functools


HOST = "0.0.0.0"
START_BUF_SIZE = 3


def generate_msg(length):
    msg = "A"
    for _ in range(length):
        yield msg
        msg += chr((ord(msg[-1]) + 1 - 65) % 26 + 65)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise Exception
    port = int(sys.argv[1])

    bufsize = START_BUF_SIZE

    for msg in generate_msg(100000):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            binary_stream = io.BytesIO()
            len_bin = bin(len(msg))
            if len(len_bin) < 16:
                len_bin = (16 - len(len_bin)) * "0" + len_bin
            binary_stream.write((len_bin + msg).encode("ascii"))
            binary_stream.seek(0)
            stream_data = binary_stream.read()
            s.sendto(stream_data, (HOST, port))
            data = s.recv(bufsize)
            print("Received data=", repr(data), " size= ", len(data))
            print("Client finished.")
            bufsize += 1


a = generate_msg(30)
print(a)
