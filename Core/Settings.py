from dotenv import load_dotenv
import os
load_dotenv()


class SettingsApp:
    
    def __init__(self):
        self.mongodb_url = os.getenv("MONGODB_URL")
        self.mongodb_name = os.getenv("MONGODB_NAME")
        self.collection_users = os.getenv("COLLECTION_USERA")
        self.collection_posts = os.getenv("COLLECTION_POSTS", "posts")
        
        self.postgre_url = os.getenv("PostgreURL")
        self.Development = os.getenv("Development","True")

        self.secret_key = os.getenv("SECRET_KEY")
        self.jwt_algorithm = os.getenv("JWT_ALGORITHM",)
        self.access_token_expire_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

