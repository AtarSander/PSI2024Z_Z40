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
    return "".join(next(it) for _ in range(length))


def data_to_binarystream(binary_stream, *args, message=""):
    # write the data to binary stream
    for arg in args:
        binary_stream.write(arg)
    binary_stream.seek(0)
    return binary_stream.read()
