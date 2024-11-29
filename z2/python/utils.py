import itertools
import string


def generate_msg(length):
    it = itertools.cycle(string.ascii_uppercase)
    return "".join(next(it) for _ in range(length))
