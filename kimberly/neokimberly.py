from pyrogram.client import Client
from config.login import api_id,api_hash,bot_token
import uvloop

uvloop.install()

kimberly = Client("kimberly", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

