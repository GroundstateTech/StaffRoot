from decimal import Decimal, InvalidOperation
import re

def to_decimal(value, minimum=None, maximum=None) -> Decimal:
    try:
        d = Decimal(str(value).strip())
    except (InvalidOperation, AttributeError):
        raise ValueError(f"Invalid numeric value: {value!r}")
    if minimum is not None and d < Decimal(str(minimum)):
        raise ValueError(f"Value must be >= {minimum}")
    if maximum is not None and d > Decimal(str(maximum)):
        raise ValueError(f"Value must be <= {maximum}")
    return d

def validate_email(email: str) -> bool:
    if not email:
        return True
    return re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email) is not None

def ssn_last4_valid(value: str) -> bool:
    if not value:
        return True
    return value.isdigit() and len(value) == 4
