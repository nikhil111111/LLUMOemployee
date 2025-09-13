# test_mongo.py
from pymongo import MongoClient
import sys

MONGO_URI = "mongodb://localhost:27017"  # default local MongoDB

def test_connection(uri):
    client = MongoClient(uri, serverSelectionTimeoutMS=5000)
    try:
        # quick ping to check connectivity
        client.admin.command("ping")
        print("✅ Connected to MongoDB!")
        # show available databases (helps verify)
        print("Databases:", client.list_database_names())
        # show whether assessment_db exists
        print("assessment_db exists?:", "assessment_db" in client.list_database_names())
    except Exception as e:
        print("❌ Connection failed:", repr(e))
        sys.exit(1)

if __name__ == "__main__":
    test_connection(MONGO_URI)
