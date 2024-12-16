from filesharingpro import settings
from cryptography.fernet import Fernet


def encrypt_url(file_id):
    key = settings.ENCRYPTION_KEY
    cipher_suite = Fernet(key)
    encrypted_url = cipher_suite.encrypt(str(file_id).encode()).decode()
    return encrypted_url

def decrypt_url(encrypted_url):
    key = settings.ENCRYPTION_KEY
    cipher_suite = Fernet(key)
    try:
        decrypted_url = cipher_suite.decrypt(encrypted_url.encode()).decode()
        return int(decrypted_url)
    except:
        return None