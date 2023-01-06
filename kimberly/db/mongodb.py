import motor.motor_asyncio
from config.login import uri

db_client = motor.motor_asyncio.AsyncIOMotorClient(uri, serverSelectionTimeoutMS=5000)
db = db_client.kimberly

