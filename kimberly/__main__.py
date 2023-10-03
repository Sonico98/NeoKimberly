import asyncio
import sys
from pyrogram.sync import idle
from config.login import *
from db.mongodb import db_client
from modules import *
from modules.nisman import build_timezones_list
from neokimberly import kimberly
from utils.time_parser import time_format_is_correct,timezone_exists


async def parse_config():
    if (not await timezone_exists(timezone)):
        exit(2)
    if (not await time_format_is_correct(nisman_time)):
        exit(2)


async def get_server_info():
    print("Trying to connect to MongoDB...")
    try:
        await db_client.server_info()
        print("Success!\n")
    except Exception:
        # TODO: Send a message to a channel informing errors
        print("\nUnable to connect to the database.")
        print("Make sure the Mongo DataBase is running and " +
              "configured correctly. Some features will not work")


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
        sys.exit(2)


async def main():
    await parse_config()
    await get_server_info()
    await build_timezones_list()
    await start_pyrogram()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
