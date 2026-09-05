import asyncio
from pymongo import AsyncMongoClient
from Core.Settings import SettingsApp

settings = SettingsApp()
MONGODB_URL = settings.mongodb_url
MONGODB_NAME = settings.mongodb_name

_clients = {}

def get_mongo_client() -> AsyncMongoClient:
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None
    if loop not in _clients or _clients[loop] is None:
        _clients[loop] = AsyncMongoClient(MONGODB_URL)
    return _clients[loop]

def get_db():
    return get_mongo_client()[MONGODB_NAME]

class CollectionProxy:
    def __init__(self, get_name):
        self.get_name = get_name

    def __getattr__(self, name):
        coll = get_db()[self.get_name()]
        return getattr(coll, name)

collection_users = CollectionProxy(lambda: settings.collection_users)



