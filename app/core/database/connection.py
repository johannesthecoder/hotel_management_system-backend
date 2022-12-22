from os import environ
from dotenv import load_dotenv
from pymongo import MongoClient


load_dotenv()

client = MongoClient(environ.get("MONGODB_URL"), serverSelectionTimeoutMS=5000)

try:
    conn = client.server_info()
    print(f'Connected to MongoDB {conn.get("version")}')
except Exception:
    print("Unable to connect to the MongoDB server.")

db = client["hotel_management_database"]