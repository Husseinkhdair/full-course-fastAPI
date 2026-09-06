from dotenv import load_dotenv
import os
load_dotenv()


class SettingsApp:
    
    def __init__(self):
        self.mongodb_url = os.getenv("MONGODB_URL")
        self.mongodb_name = os.getenv("MONGODB_NAME")
        self.collection_users = os.getenv("COLLECTION_USERA")
        
        self.postgre_url = os.getenv("PostgreURL")
        self.Development = os.getenv("Development","True")

        self.secret_key = os.getenv("SECRET_KEY", "super_secret_jwt_key_123456789_secure_32bytes")
        self.jwt_algorithm = os.getenv("JWT_ALGORITHM", "HS256")
        self.access_token_expire_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))

