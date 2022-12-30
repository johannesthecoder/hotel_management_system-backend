from os import environ
from dotenv import load_dotenv
import motor.motor_asyncio


load_dotenv()

MONGODB_URL = "mongodb://localhost:27017"
client = motor.motor_asyncio.AsyncIOMotorClient(environ.get("MONGODB_URL"))
db = client["hotel_management_database"]
