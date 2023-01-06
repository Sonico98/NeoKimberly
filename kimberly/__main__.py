from neokimberly import kimberly
from db.mongodb import db_client
from modules import *
from pyrogram.sync import idle
import asyncio
import sys


async def get_server_info():
    print("Trying to connect to MongoDB...")
    try:
        await db_client.server_info()
        print("Success!\n")
        return True
    except Exception:
        print("\nUnable to connect to the database.")
        print("Make sure the Mongo DataBase is running and " +
              "configured correctly")
        return False


async def start_pyrogram():
    print("Starting the bot...")
    try:
        await kimberly.start()
        print("Running!")
        await idle()
        print("\nGoodbye!")
        await kimberly.stop()
    except:
        print("\nError starting the bot. Please make sure you've " +
        "filled out all the information required in the " +
        "configuration file and that it's correct")
        exit(2)


async def main():
    db_is_running = await get_server_info()
    if (db_is_running):
        await start_pyrogram()
        sys.exit(0)
    sys.exit(1)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
