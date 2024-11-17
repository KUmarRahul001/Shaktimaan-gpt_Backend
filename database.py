from pymongo import MongoClient
import os

# Fetch database credentials from environment variables (for security)
DB_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017')  # Default to local MongoDB if not set
DB_NAME = os.getenv('DB_NAME', 'chat_db')  # Default database name

def get_db():
    """
    Returns a MongoDB database connection.
    
    :return: A MongoDB database instance.
    """
    client = MongoClient(DB_URI)
    db = client[DB_NAME]
    return db
