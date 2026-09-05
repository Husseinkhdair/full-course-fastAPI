from pymongo import AsyncMongoClient
from Core.Settings import SettingsApp

MONGODB_URL = SettingsApp().mongodb_url
MONGODB_NAME = SettingsApp().mongodb_name


client = AsyncMongoClient(MONGODB_URL)
db = client[MONGODB_NAME]


collection_users = db[SettingsApp().collection_users]


