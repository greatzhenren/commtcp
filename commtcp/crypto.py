from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.padding import PKCS7


class Aes:
    def __init__(self, key, iv):
        self._key = key
        self._iv = iv
        self._cipher = Cipher(algorithms.AES(self._key), modes.CBC(self._iv), default_backend())

    def encrypt(self, data):
        if type(data) == str:
            plaintext = data.encode('utf-8')
        elif type(data) == bytes:
            plaintext = data
        else:
            raise ValueError('data must be str or bytes')
        padder = PKCS7(128).padder()
        pad_data = padder.update(plaintext) + padder.finalize()
        encryptor = self._cipher.encryptor()
        ciphertext = encryptor.update(pad_data) + encryptor.finalize()
        return ciphertext

    def decrypt(self, data):
        decryptor = self._cipher.decryptor()
        raw = decryptor.update(data) + decryptor.finalize()
        unpadder = PKCS7(128).unpadder()
        plaintext = unpadder.update(raw) + unpadder.finalize()
        return plaintext
