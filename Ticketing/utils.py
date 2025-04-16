import uuid
import random
import string
import hashlib

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