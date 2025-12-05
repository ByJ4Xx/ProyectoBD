import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

# Default to local MongoDB instance
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = "tienda_virtual"

def get_database():
    """
    Establishes a connection to the MongoDB database and returns the database object.
    """
    try:
        client = MongoClient(MONGO_URI)
        # The ismaster command is cheap and does not require auth.
        client.admin.command('ismaster')
        print("Connected to MongoDB successfully!")
        return client[DB_NAME]
    except ConnectionFailure:
        print("Server not available. Please ensure MongoDB is running.")
        return None

if __name__ == "__main__":
    db = get_database()
    if db is not None:
        print(f"Using database: {db.name}")
