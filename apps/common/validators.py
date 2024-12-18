import re
from django.core.validators import RegexValidator


phone_number_regex = r"^\+?1?\d{9,15}$"

phone_validator = RegexValidator(
    regex=phone_number_regex,
    message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.",
)