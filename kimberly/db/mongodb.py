import motor.motor_asyncio
from config.login import host,port

db_client = motor.motor_asyncio.AsyncIOMotorClient(host, port, serverSelectionTimeoutMS=5000)
db = db_client.kimberly

