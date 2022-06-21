import binascii
import hashlib

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from passlib.utils.pbkdf2 import pbkdf1

class Cryptor:
    def __init__(self, salt: str, passphrase: str, block_size=128):
        self.salt = salt
        self.block_size = block_size
        self.cipher = self._get_cipher(salt=salt, passphrase=passphrase)

    # Based on 'decent implementation' here:
    # https://gist.github.com/tly1980/b6c2cc10bb35cb4446fb6ccf5ee5efbc
    @staticmethod
    def _openssl_kdf(passphrase, salt, key_size=32, iv_size=16):
        temp = pbkdf1(passphrase, salt, 1, 16, 'md5')
        fd = temp

        while len(fd) < key_size + iv_size:
            h = hashlib.md5()
            h.update(temp + passphrase + salt)
            temp = h.digest()
            fd += temp

        key = fd[0:key_size]
        iv = fd[key_size:key_size + iv_size]

        return key, iv

    def _get_cipher(self, salt: str, passphrase: str) -> Cipher:
        key, iv = self._openssl_kdf(passphrase.encode(), salt.encode())

        return Cipher(algorithms.AES(key), modes.CBC(iv))

    def encrypt(self, clear_text: str) -> bytes:
        encryptor = self.cipher.encryptor()
        padder = padding.PKCS7(self.block_size).padder()
        padded_text = padder.update(clear_text.encode())
        padded_text += padder.finalize()

        cipher_text = (
            encryptor.update(padded_text) + encryptor.finalize()
        )

        salted_cipher_text = f'Salted__{self.salt}'.encode() + cipher_text

        return salted_cipher_text

    def encrypt_hex(self, clear_text: str) -> str:
        cipher_text = self.encrypt(clear_text)

        return binascii.hexlify(cipher_text).decode('ascii').lower()

    def decrypt(self, cipher_text: bytes) -> str:
        decryptor = self.cipher.decryptor()

        # Remove openssl "Salted__xxxxxxxx" (16 bytes) header
        cipher_text_no_header = cipher_text[16:]

        padded_text = (
            decryptor.update(cipher_text_no_header) + decryptor.finalize()
        )

        unpadder = padding.PKCS7(self.block_size).unpadder()

        clear_text = (
            unpadder.update(padded_text) + unpadder.finalize()
        ).decode("ascii")

        return clear_text

    def decrypt_hex(self, hex_cipher_text: str) -> str:
        return self.decrypt(
            binascii.unhexlify(hex_cipher_text)
        )
