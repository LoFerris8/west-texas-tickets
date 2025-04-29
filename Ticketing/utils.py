import uuid
import random
import string
import hashlib
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from django.conf import settings
import os


def generate_barcode():
    """Generate a unique barcode for tickets."""
    # Generate a UUID and convert to string
    random_uuid = str(uuid.uuid4())
    
    # Create a shorter version by using part of the UUID and adding a prefix
    short_uuid = 'WTT' + random_uuid.replace('-', '')[:12].upper()
    
    return short_uuid

def generate_ticket_id():
    """Generate a readable ticket ID."""
    # Create a random string of letters and numbers
    letters = ''.join(random.choices(string.ascii_uppercase, k=3))
    numbers = ''.join(random.choices(string.digits, k=5))
    
    return f"{letters}-{numbers}"

def hash_password(password):
    """Create a secure hash of the password."""
    return hashlib.sha256(password.encode()).hexdigest()

# Add to Ticketing/utils.py

def encrypt_payment_data(payment_data):

    # Convert payment data dict to string
    payment_str = str(payment_data)
    
    # Create a key using SECRET_KEY as password
    # In production, you should use a separate encryption key, not the Django SECRET_KEY
    password = settings.SECRET_KEY.encode()
    salt = os.urandom(16)
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    key = base64.urlsafe_b64encode(kdf.derive(password))
    
    # Encrypt the data
    f = Fernet(key)
    encrypted_data = f.encrypt(payment_str.encode())
    
    # Return both salt and encrypted data for storage
    return base64.b64encode(salt).decode() + ":" + encrypted_data.decode()