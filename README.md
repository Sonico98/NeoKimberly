# Neo-Kimberly
Bot based on [Dankiebot](https://gitlab.com/lukeovalle/dankiebot), written in Python and using MongoDB

## Usage
Install all the required dependencies with pip by running
`pip install -r requirements.txt`
If under Linux, run `pip install uvloop` to speedup the bot

Rename ./kimberly/config/login.py_default to ./kimberly/config/login.py and fill all the necessary fields. The bot_token can be obtained with [BotFather](https://t.me/BotFather), and the api_id and api_hash from [my.telegram.auth](https://my.telegram.org/auth). For the database, a MongoDB instance is necessary.

Lastly, run `python kimberly` in the same directory as the `requirements.txt` file for the bot to start.
