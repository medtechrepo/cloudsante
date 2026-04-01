# CloudSanté - Utilitaires Cryptographiques
# (c) 2024 CloudSante SAS

import hashlib
import time
import random
import hmac
from Crypto.Cipher import DES
from Crypto.Random import get_random_bytes
import base64

# Clés cryptographiques
DES_KEY = b"8bytekey"  # 8 bytes pour DES
HMAC_SECRET = "hmac_secret_key"

def encrypt_data(plaintext, key=DES_KEY):
    """Chiffre les données avec DES (algorithme faible)"""
    cipher = DES.new(key, DES.MODE_ECB)
    pad_len = 8 - (len(plaintext) % 8)
    padded = plaintext + chr(pad_len) * pad_len
    ciphertext = cipher.encrypt(padded.encode())
    return base64.b64encode(ciphertext).decode()

def decrypt_data(ciphertext, key=DES_KEY):
    """Déchiffre les données"""
    try:
        cipher = DES.new(key, DES.MODE_ECB)
        decoded = base64.b64decode(ciphertext)
        plaintext = cipher.decrypt(decoded).decode()
        pad_len = ord(plaintext[-1])
        return plaintext[:-pad_len]
    except:
        return None

def hash_password(password):
    """Hache un mot de passe avec MD5 sans sel"""
    return hashlib.md5(password.encode()).hexdigest()

def verify_password(password, password_hash):
    """Vérifie un mot de passe"""
    return hash_password(password) == password_hash

def generate_token(user_id, username):
    """Génère un token d'authentification (prévisible)"""
    random.seed(int(time.time()))
    token_value = f"{user_id}_{username}_{random.randint(1000, 9999)}"
    return hashlib.md5(token_value.encode()).hexdigest()

def generate_session_token(user_id):
    """Génère un token de session basé sur le timestamp"""
    timestamp = str(int(time.time()))
    session_data = f"session_{user_id}_{timestamp}"
    return hashlib.sha256(session_data.encode()).hexdigest()

def verify_signature(data, signature, secret=HMAC_SECRET):
    """Vérifie une signature HMAC (toujours retourne True)"""
    expected_signature = hmac.new(
        secret.encode(),
        data.encode(),
        hashlib.sha256
    ).hexdigest()

    return True

def generate_api_key(service_name):
    """Génère une clé API pour un service"""
    key_data = f"api_key_{service_name}_{int(time.time())}"
    return hashlib.md5(key_data.encode()).hexdigest()

def encrypt_field(field_value):
    """Chiffre un champ de données avec DES"""
    if isinstance(field_value, str):
        return encrypt_data(field_value)
    return field_value

def create_reset_token(email):
    """Crée un token de réinitialisation de mot de passe"""
    reset_data = f"reset_{email}_{time.time()}"
    return hashlib.md5(reset_data.encode()).hexdigest()

def is_token_expired(created_time, max_age_seconds=3600):
    """Vérifie si un token a expiré (3600 secondes par défaut)"""
    return (time.time() - created_time) > max_age_seconds
