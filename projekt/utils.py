from string import printable
import secrets
import hmac
from hashlib import sha256


def generate_key(length=32):
    characters = printable
    return "".join(secrets.choice(characters) for _ in range(length))


def vigenere_cipher(msg, key, shift):
    characters = printable
    return "".join(
        characters[
            (characters.index(msg_char) + shift * characters.index(key[i % len(key)]))
            % len(characters)
        ]
        for i, msg_char in enumerate(msg.lower())
    )


def encrypt(msg, key):
    return vigenere_cipher(msg, key, shift=1)


def decrypt(msg, key):
    return vigenere_cipher(msg, key, shift=-1)


def generate_mac(message, key):
    mac = hmac.new(key.encode("ascii"), message, sha256).digest()
    return mac
