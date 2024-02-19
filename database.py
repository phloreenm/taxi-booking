from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

class MongoDB:
    def __init__(self, uri, db_name):
        self.client = MongoClient(uri, server_api=ServerApi('1'))
        self.db = self.client[db_name]

    def insert_document(self, collection_name, document):
        collection = self.db[collection_name]
        collection.insert_one(document)

    def test_connection(self):
        try:
            self.client.admin.command('ping')
            print("Successfully connected to MongoDB!")
        except Exception as e:
            print(f"Connection failed: {e}")
