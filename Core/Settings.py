from dotenv import load_dotenv
import os
load_dotenv()


class SettingsApp:
    
    def __init__(self):
        self.mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
        self.mongodb_name = os.getenv("MONGODB_NAME", "TestDB")
        self.collection_users = os.getenv("COLLECTION_USERS") or os.getenv("COLLECTION_USERA") or "Users"