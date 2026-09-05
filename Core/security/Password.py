import bcrypt

class PasswordSecurity:
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a plain text password using bcrypt."""
        if not password:
            raise ValueError("Password cannot be empty")
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
        return hashed.decode("utf-8")

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a plain text password against a stored bcrypt hash."""
        if not plain_password or not hashed_password:
            return False
        try:
            return bcrypt.checkpw(
                plain_password.encode("utf-8"),
                hashed_password.encode("utf-8")
            )
        except Exception:
            return False


def hash_password(password: str) -> str:
    return PasswordSecurity.hash_password(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return PasswordSecurity.verify_password(plain_password, hashed_password)
