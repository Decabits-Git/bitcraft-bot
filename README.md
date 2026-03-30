# bitcraft-bot
Bot for getting craft informations through the Bitjita API for the game "BitCraft" - specifically for our settlement (Myralune in R9)
## How to get started
### Set up Discord
Go to the Discord Developer Portal
https://discord.com/developers/home
0. Select "you want to create your own bot" if asked and start creating an "application"
1. Name it as you like - doesnt really matter
2. Left side switch to installation
  - uncheck user install
  - at the bottom in "Guild Install" add "bot" to the scope and add following permissions:
    - "Manage Messages", "Manage Threads", "Read Message History", "Send Messages", "Send Messages in Threads"
  - dont forget to "Save Changes"
3. Left side switch to Bot
  - give your bot a username and a profile picture and banner as you like
  - "Reset Token" to get a valid TOKEN, copy this and save it for now
  - activate "Message Content Intent"
4. (optional) You can add your own Emojis on the "Emojis" tab if needed
### Set up the script
1. Install requirements
   - create a virtual environment (https://docs.python.org/3/library/venv.html)
   - or just install it globally (https://packaging.python.org/en/latest/tutorials/installing-packages/)
2. Edit the bot.py
  - give your TOKEN to the script (line 5, simply paste it in the "")
  - get the channel id of the channel you want the bot to write in
    - right click the channel and there should be a field "Copy Channel ID"
    - place it behind (line 6) CHANNEL_ID =
  - update time interval at line 8 SLEEPTIME =

Note: CHANNEL_ID and SLEEPTIME are ints (numbers). Token is a string.
### Start the bot
1. Invite the bot to your discord server (guild)
  - at the Discord Developer Portal go to the page "Installation" and simply open the "Install Link"
  - select the server you want to add the bot to
  - allow the permissions that are requested
2. Start the bot.py script
python bot.py

## TODO
- create a leaderboard for finished crafts (see https://bitjita.com/docs/api/crafts/[craftId]/contributions)
  - delete finished crafts from their respective channel and post the leaderboard results somewhere else
 
### DONE
- use forums instead of channels - Decabits
- detect already posted crafts - Decabits

## Credits
HUGE thanks to Decabits!

