from cryptography.fernet import Fernet # cifrado simetrico aes-256
from app.config import ENCRYPTION_KEY # llave de encriptacion desde config

# inicializa el cifrador fernet con la llave
fernet = Fernet(ENCRYPTION_KEY.encode()) # crea el cifrador


def encrypt(text: str) -> str: # cifra un texto
    if not text: # si esta vacio, retorna vacio
        return ""
    encrypted = fernet.encrypt(text.encode()) # cifra el texto
    return encrypted.decode() # retorna como string


def decrypt(encrypted_text: str) -> str: # descifra un texto
    if not encrypted_text: # si esta vacio, retorna vacio
        return ""
    decrypted = fernet.decrypt(encrypted_text.encode()) # descifra el texto
    return decrypted.decode() # retorna como string
