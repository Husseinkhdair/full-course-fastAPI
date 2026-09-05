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
