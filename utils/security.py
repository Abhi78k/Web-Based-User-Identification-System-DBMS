from werkzeug.security import generate_password_hash, check_password_hash

def hash_password(password):
    """Hash a password using werkzeug's secure hashing."""
    return generate_password_hash(password)

def verify_password(stored_hash, provided_password):
    """Verify a password against its hash."""
    return check_password_hash(stored_hash, provided_password)

def validate_password_strength(password):
    """Basic password strength validation."""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter"
    if not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter"
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one number"
    return True, "Password is valid"

