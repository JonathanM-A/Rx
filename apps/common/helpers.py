from django.utils.crypto import get_random_string
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

def generate_redis_key(client_id):
    return f"client_cart:{client_id}"


def generate_secure_password(length=16):
    characters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()_+"
    while True:
        password = get_random_string(length, characters)
        try:
            validate_password(password)
            return password
        except ValidationError:
            continue