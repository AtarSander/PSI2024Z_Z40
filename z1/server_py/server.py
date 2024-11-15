import socket
import sys
from utils import seperate_data

HOST = "127.0.0.1"
PORT = int(sys.argv[1])
START_BUF_SIZE = 5


if __name__ == "__main__":
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.bind((HOST, PORT))
        bufsize = START_BUF_SIZE
        while True:
            data_address = s.recvfrom(bufsize)
            # print(f"data_address: {data_address}")
            data = data_address[0]
            address = data_address[1]

            if not data:
                print("Error in datagram?")
                break

            msg_len, checksum, msg = seperate_data(data)

            print(f"Message length: {msg_len}")
            print(f"Checksum: {checksum}")
            print(f"Message from Client: {msg}")
            print(f"Client IP Address: {address}")

            # send back the datagram header
            s.sendto(data[:4], address)
            print("sending dgram #", bufsize - 4, "\n")
            bufsize += 1
