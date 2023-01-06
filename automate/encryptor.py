from cryptography.fernet import Fernet

from django.conf import settings


class Encryptor:
    def __init__(self, key):
        self.key = settings.SECRET_KEY
        self.fernet = Fernet(key)

    def encrypt(self, message):
        message_bytes = message.encode()
        encrypted_message = self.fernet.encrypt(message_bytes)
        return encrypted_message.decode()

    def decrypt(self, encrypted_message):
        encrypted_message_bytes = encrypted_message.encode()
        decrypted_message = self.fernet.decrypt(encrypted_message_bytes)
        return decrypted_message.decode()
