from string import printable
import secrets
import hmac
from hashlib import sha256


def generate_key(length=32):
    """
    Generate a random key of the given length using only printable characters.

    Args:
        length (int): The length of the key to generate.

    Returns:
        str: A randomly generated key of the specified length.
    """
    characters = printable
    return "".join(secrets.choice(characters) for _ in range(length))


def vigenere_cipher(msg, key, shift):
    """
    Encrypt or decrypt a message using the Vigenere cipher.
    Uses same set of characters as generate_key.

    Args:
        msg (str): The message to encrypt or decrypt.
        key (str): Cipher's key.
        shift (int): The shift to apply to the message. (1 for encryption, -1 for decryption)

    Returns:
        str: Encrypted or decrypted message.
    """

    characters = printable
    return "".join(
        characters[
            (characters.index(msg_char) + shift * characters.index(key[i % len(key)]))
            % len(characters)
        ]
        for i, msg_char in enumerate(msg)
    )


def encrypt(msg, key):
    return vigenere_cipher(msg, key, shift=1)


def decrypt(msg, key):
    return vigenere_cipher(msg, key, shift=-1)


def generate_mac(message, key):
    # Generate a MAC for the message using the given key.
    return hmac.new(key.encode("ascii"), message, sha256).digest()
