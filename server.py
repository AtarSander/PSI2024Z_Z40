import socket
import sys

HOST = "127.0.0.1"
START_BUF_SIZE = 5
# port = int(sys.argv[1])
port = 8000


if __name__ == "__main__":
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.bind((HOST, port))
        bufsize = START_BUF_SIZE
        while True:
            data_address = s.recvfrom(bufsize)
            data = data_address[0]
            address = data_address[1]
            print(f"Message from Client: {data.decode("ascii")}")
            print(f"Client IP Address: {address}")
            if not data:
                print("Error in datagram?")
                break
            # echo back data
            s.sendto(data, address)
            print("sending dgram #", bufsize - 4)
            bufsize += 1
