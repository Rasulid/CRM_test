import base64
import os

from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from core.config import settings


class CypherPassword:
    password = settings.secret_key
    key = None

    @staticmethod
    def generate_encryption_key(password: str):
        password_provided = password
        password = password_provided.encode()

        salt = settings.encrypt_key.encode()

        kdf = PBKDF2HMAC(algorithm=hashes.SHA256(),
                         length=32,
                         salt=salt,
                         iterations=100000,
                         backend=default_backend())

        key = base64.urlsafe_b64encode(kdf.derive(password))
        return key

    key = generate_encryption_key(password)

    def encrypt_pass(self, pass_data: str):
        f = Fernet(self.key)
        return f.encrypt(pass_data.encode(encoding="UTF-8"))

    def decrypt_pass(self, byte_data: bytes):
        f = Fernet(self.key)
        return f.decrypt(byte_data)


cypher = CypherPassword()
