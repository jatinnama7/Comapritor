# drop_collection.py
import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()  # expects MONGODB_URI in .env

MONGO_URI = os.getenv("MONGODB_URI")
DB_NAME = "comparitor_db"
COLLECTION = "products"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

if COLLECTION in db.list_collection_names():
    db.drop_collection(COLLECTION)
    print(f"Dropped collection '{COLLECTION}' in DB '{DB_NAME}'.")
else:
    print(f"Collection '{COLLECTION}' not found in DB '{DB_NAME}'.")