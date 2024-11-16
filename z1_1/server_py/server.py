import socket
import sys
from utils import seperate_data

START_BUF_SIZE = 5


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
            # receive datagram from UDP socket
            data_address = s.recvfrom(bufsize)

            # extract the data and client's address
            data = data_address[0]
            address = data_address[1]

            # error receiving datagram
            if not data:
                print("Error in datagram?")
                break

            msg_len, checksum, msg = seperate_data(data)

            # log received data headers
            print(f"Datagram length: {msg_len}")
            print(f"Checksum: {checksum}")
            print(f"Client IP Address: {address}")

            # send back the datagram header
            s.sendto(data[:4], address)
            print("sending dgram #", bufsize - 4, "\n")
            bufsize += 1
