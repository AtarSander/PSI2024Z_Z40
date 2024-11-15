import itertools
import string


def fletcher16(data):
    sum1 = 0
    sum2 = 0

    for byte in data:
        sum1 = (sum1 + ord(byte)) % 255
        sum2 = (sum2 + sum1) % 255

    checksum = (sum2 << 8) | sum1
    return checksum


def generate_msg(length):
    it = itertools.cycle(string.ascii_uppercase)
    msg = ""
    for _ in range(length):
        msg += next(it)
        yield msg


def seperate_data(data):
    msg_len = int.from_bytes(data[:2], byteorder="big")
    checksum = int.from_bytes(data[2:4], byteorder="big")
    msg = data[4:].decode("ascii")

    return msg_len, checksum, msg
