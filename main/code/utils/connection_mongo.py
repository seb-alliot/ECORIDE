# utils/mongo.py (ou ailleurs dans ton projet)
from pymongo import MongoClient
from django.conf import settings

_client = None
_db = None

def get_mongo_db():
    global _client, _db
    if _client is None:
        _client = MongoClient(settings.URI)
        _db = _client[settings.MONGO_DB_NAME]
    return _db
