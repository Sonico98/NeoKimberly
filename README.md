# Neo-Kimberly
Bot inspired on [Dankiebot](https://gitlab.com/lukeovalle/dankiebot), written in Python with Pyrogram and using MongoDB


## Installation
- Install `git, python` and `pip`.
	- If you're on Windows, install [git for Windows](https://git-scm.com/download/win) leaving all the options at their default (optionally disable the credential manager), and when installing python, make sure to tick the checkboxes for `Add Python to PATH` and `Install pip`.

- Clone the repository
	- Either by running `git clone https://github.com/Sonico98/NeoKimberly` on your terminal (or windows' cmd), or by clicking the green "Code" button at the top right of this page and clicking download zip.

- `cd` into the repository on your terminal
	- If under Windows, you may need to run the cmd with administrator privileges

- Run `pip install -r requirements.txt`


## Usage
- Rename `./kimberly/config/login.py_default` to `./kimberly/config/login.py` and fill all the necessary fields. The bot_token can be obtained with [BotFather](https://t.me/BotFather), and the `api_id` and `api_hash` from [my.telegram.auth](https://my.telegram.org/auth). For the database, a MongoDB instance is necessary.

- On Telegram, send the command `/mybots` to BotFather and choose your bot from the list. Then, go into Bot Settings -> Group Privacy -> Turn Off.

- Lastly, run `python kimberly` in the same directory as the `requirements.txt` file for the bot to start.

## Licensing
Copyright WhateverLicenseYouWant 3.0
