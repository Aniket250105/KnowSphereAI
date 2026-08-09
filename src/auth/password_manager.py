import bcrypt

def hash_password(password: str) -> str:
    # Hash a password for the first time
    # (Using bcrypt, the salt is saved into the hash itself)
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(password: str, hashed_password: str) -> bool:
    # Check hashed password. Using bcrypt, the salt is saved into the hash itself
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
