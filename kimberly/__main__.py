from neokimberly import kimberly
from db.mongodb import db_client
from pyrogram.sync import idle
import asyncio

async def get_server_info():
    print("Trying to connect to MongoDB...")
    try:
        await db_client.server_info()
        print("Success!\n")
    except Exception:
        print("\nUnable to connect to the database.")
        print("Make sure the Mongo DataBase is running and " +
              "configured correctly")
        exit(2)

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


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(get_server_info())
    loop.run_until_complete(start_pyrogram())
