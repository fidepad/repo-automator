import base64

from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from django.conf import settings
from django.utils.encoding import force_bytes

backend = default_backend()
info = b"django-fernet-fields"
# We need reproducible key derivation, so we can't use a random salt
salt = b"django-fernet-fields-hkdf-salt"


class Crypt:
    """Encryptor class for encrypting and decrypting."""

    def __init__(self):
        self.key = settings.SECRET_KEY
        self.fernet = Fernet(self.derive_fernet_key(self.key))

    def derive_fernet_key(self, key):
        """
        Salt key for fernet
        """
        hkdf = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            info=info,
            backend=backend,
        )
        return base64.urlsafe_b64encode(hkdf.derive(force_bytes(key)))

    def encrypt(self, message):
        """This function encrypts the message."""
        if message:
            message_bytes = message.encode()
            encrypted_message = self.fernet.encrypt(message_bytes)
            return encrypted_message.decode()
        return None

    def decrypt(self, encrypted_message):
        """This function decrypts the function."""
        if encrypted_message:
            encrypted_message_bytes = encrypted_message.encode()
            decrypted_message = self.fernet.decrypt(encrypted_message_bytes)
            return decrypted_message.decode()
        return None

    def multi_decrypt(self, messages: dict):
        """This method returns the decrypted versions of information sent to it in a dictionary."""
        for key, value in messages.items():
            if value:
                messages[key] = self.decrypt(value)

        return messages
