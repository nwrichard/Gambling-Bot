import discord, os, random
from replit import db
from keep_alive import keep_alive
from datetime import datetime, timedelta
from threading import Timer
from discord import Webhook, RequestsWebhookAdapter

#impetus_nox_webhook = os.environ['Impetus_Nox_Webhook']
#beans_webhook = os.environ['Beans_Webhook']
laser_webhook = os.environ['Laser_House']

webhook = Webhook.from_url(str(laser_webhook), adapter=RequestsWebhookAdapter())

help_doc = "---Help Functions---\n!join - Enter the casino to be eligible for rolls. New players start with 50000 gold.\n!stats - To view how much gold you currently have and how much you won/lost.\n!allstats - To view how much gold ALL players have and how much they won/lost.\nlimit x - Where x is the amount you want to change the limit to. At least 2 players must vote on this change. Change will take effect next roll.\nOnce you join the casino, every Tuesday you will be given an incentive to play and gain an additional "

GAME_LIMIT = 10000
NEW_GAME_LIMIT = 10000

client = discord.Client()

# Adds a user to the gambling database. New players start with 50,000.
def add_user(user_ID):
  user_ID = str(user_ID)
  if user_ID in db.keys():
    print('User already in database.')
    return
  else:
    db[user_ID] = {
      "name": str(user_ID),
      "current_gold": 50000,
      "overall_stats": 0,
      "playing_current_game": False,
      "current_game_roll": 0
    }
    return
  
# Deletes a user from the gabling database.
def delete_user(user_ID):
  user_ID = str(user_ID)
  if user_ID in db.keys():
    del db[user_ID]
    return
  else:
    print('No user with this name in database.')
    return

# Checks if a user is in the gambling database.
def check_if_gambling(user_ID):
  user_ID = str(user_ID)
  if user_ID in db.keys():
    return True
  else:
    return False

# Checks if a user is participating in the current roll.
def check_if_playing_current_game(user_ID):
  user_ID = str(user_ID)
  if user_ID in db.keys():
    if db[user_ID]["playing_current_game"] == True:
      return True
    else:
      return False
  else:
    return False

# Adds gold to the user.
def add_gold(user_ID, gold):
  user_ID = str(user_ID)
  if user_ID in db.keys():
    current_gold = db[user_ID]["current_gold"]
    overall_stats = db[user_ID]["overall_stats"]
    db[user_ID]["current_gold"] = int(current_gold) + int(gold)
    db[user_ID]["overall_stats"] = int(overall_stats) + int(gold)
    return
  else:
    return

# Subtracts gold from the user.
def subtract_gold(user_ID, gold):
  user_ID = str(user_ID)
  if user_ID in db.keys():
    current_gold = db[user_ID]["current_gold"]
    overall_stats = db[user_ID]["overall_stats"]
    db[user_ID]["current_gold"] = int(current_gold) - int(gold)
    db[user_ID]["overall_stats"] = int(overall_stats) - int(gold)
    return
  else:
    return

# Gets the user's current stats.
def user_stats(user_ID):
  user_ID = str(user_ID)
  if user_ID in db.keys():
    current_gold = db[user_ID]["current_gold"]
    overall_stats = db[user_ID]["overall_stats"]
    user_stats = "{name} - Gold: {current_gold} - Overall: {overall_stats}".format(name = user_ID, current_gold = current_gold, overall_stats = overall_stats)
    return user_stats
  else:
    return

# Gets the current stats of all users.
def all_stats():
  all_stats = "--- Overall Stats ---"
  for key in db:
    current_gold = db[key]["current_gold"]
    overall_stats = db[key]["overall_stats"]
    all_stats = all_stats + "\n{name} - Gold: {current_gold} - Overall: {overall_stats}".format(name = key, current_gold = current_gold, overall_stats = overall_stats)
  return all_stats

# Sets the game limit.
def set_game_limit(number):
  if number > 0:
    NEW_GAME_LIMIT = int(number)
    return

# Checks if the user has enough gold for the roll.
def enough_gold(user_ID, gold):
  user_ID = str(user_ID)
  if int(db[user_ID]["current_gold"]) > int(gold):
    return True
  else:
    webhook.send("Not enough gold to join roll!")
    return False

# A user joins the current roll.
def join_roll(user_ID, gold):
  user_ID = str(user_ID)
  if check_if_gambling(user_ID) == True:
    if enough_gold(user_ID, int(gold)) == True:
      db[user_ID]["playing_current_game"] = True
      return
    else:
      db[user_ID]["playing_current_game"] = False
      return
  else:
    db[user_ID]["playing_current_game"] = False
    return

# A user leaves the current roll.
def leave_roll(user_ID):
  user_ID = str(user_ID)
  if check_if_gambling(user_ID) == True:
    db[user_ID]["playing_current_game"] = False
    return
  else:
    return

# If the user is in the db gambling and playing the current game, roll between 1 and GAME_LIMIT
def roll(user_ID, limit):
  user_ID = str(user_ID)
  if check_if_playing_current_game(user_ID) == True:
    db[user_ID]["current_game_roll"] = random.randint(1,limit)
    return
  else:
    return

# Gamble Roll Timer Sequence
def gamble_roll():
  current_limit = GAME_LIMIT
  
  compare_win = 0
  compare_lose = current_limit
  players = 0
  rolls = "---ROLLS---"

  db["TEST"] = {
      "name": str("TEST"),
      "current_gold": 50000,
      "overall_stats": 0,
      "playing_current_game": True,
      "current_game_roll": 0
    }

  for key in db:
    if key == "The House#0000":
      del db["The House#0000"]

  # For each player, check if they are playing the current game.
  for key in db:
    if check_if_playing_current_game(key) == True:
      players = players + 1

  if players >= 2:
    for key in db:
      if check_if_playing_current_game(key) == True:
      
        roll(key, current_limit)

        # Tie breaker, just reroll. And when this inevitably breaks and Denis laughs at me, I'll change it.
        if (db[key]["current_game_roll"] == compare_win):
          roll(key, current_limit)
        if (db[key]["current_game_roll"] == compare_lose):
          roll(key, current_limit)

        print("{name} rolled {roll}.".format(name = str(key), roll = db[key]["current_game_roll"]))

        if db[key]["current_game_roll"] < compare_lose:
          compare_lose = db[key]["current_game_roll"]
          loser = key
        if db[key]["current_game_roll"] > compare_win:
          compare_win = db[key]["current_game_roll"]
          winner = key

        rolls = rolls + "\n{name} rolled {roll}.".format(name = key, roll = db[key]["current_game_roll"])

    webhook.send(rolls)
    
    # Calculate the difference between the winner and the loser.
    difference = db[winner]["current_game_roll"] - db[loser]["current_game_roll"]

    # Print how much the loser owes the winner.
    webhook.send('**{loser} owes {winner} {difference} gold!**'.format(winner = winner, loser = loser, difference = difference))

    add_gold(winner, difference)
    subtract_gold(loser, difference)

  # Reset the rolls and playing status
  winner = ""
  loser = ""
  players = 0
  rolls = ""
  for key in db:
    db[key]["playing_current_game"] = False
    db[key]["current_game_roll"] = 0
  
  # restart roll timer
  x=datetime.today()
  y = x.replace(day=x.day, hour=x.hour, minute=x.minute, second=x.second, microsecond=0) + timedelta(seconds=15)
  delta_t=y-x
  secs=delta_t.total_seconds()
  t = Timer(secs, gamble_roll)
  t.start()
  
  webhook.send('Welcome to Impetus Nox Gambling! A new game has begun! Type **1** to join, **-1** to unjoin. The roll will close in 6 hours.')

  GAME_LIMIT = NEW_GAME_LIMIT
  return

@client.event
async def on_ready():
  print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
  if message.author == client.user:
    return

  if message.author == "The House#0000":
    return

  if message.content.startswith('!helpgamble'):
    webhook.send('{help_doc}'.format(help_doc = help_doc))

  if message.content == "!join":
    if message.author in db.keys():
      webhook.send('You are already gambling, {message_author}!'.format(message_author = message.author))
    else:
      add_user(message.author)
      webhook.send('Welcome to Impetus Nox Gambling, {message_author}! You start with 50000 gold!'.format(message_author = message.author.mention))

  if message.content == "!admin_leave":
    delete_user(message.author)
    webhook.send('Come back soon, {message_author}!'.format(message_author = message.author.mention))

  if message.content == "!stats":
    stats = user_stats(message.author)
    webhook.send('{stats}'.format(stats = stats))

  if message.content == "!allstats":
    stats = all_stats()
    webhook.send('{stats}'.format(stats = stats))

  if message.content.startswith('!limit'):
    limit = message.content.split("!limit ",1)[1]
    set_game_limit(limit)
    webhook.send('Limit set to ${limit}!'.format(limit = limit))
  
  if message.content == "1":
    join_roll(message.author, GAME_LIMIT)

  if message.content == "-1":
    leave_roll(message.author)

  if message.content == "!admin_print":
    user_ID = str(message.author)
    webhook.send('Name: {name}\nGold: {gold}\nPlaying Current Game: {playing_current_game}\nCurrent Game Roll: {current_game_roll}'.format(name = db[user_ID]["name"], gold = db[user_ID]["current_gold"], playing_current_game = db[user_ID]["playing_current_game"], current_game_roll = db[user_ID]["current_game_roll"]))

  if message.content.startswith('!admin_modify_gold'):
    message = message.content.split(" ")
    user_ID = message[1]
    gold = message[2]
    db[user_ID]["current_gold"] = gold

for key in db:
  db[key]["playing_current_game"] = False
  db[key]["current_game_roll"] = 0

x=datetime.today()
y = x.replace(day=x.day, hour=x.hour, minute=x.minute, second=x.second, microsecond=0) + timedelta(seconds=15)
delta_t=y-x
secs=delta_t.total_seconds()
t = Timer(secs, gamble_roll)
t.start()
webhook.send('Welcome to Impetus Nox Gambling! A new game has begun! Type **1** to join, **-1** to unjoin. The roll will close in 15 minutes.')

for key in db:
  if key == "The House#0000":
    del db["The House#0000"]

keep_alive()
client.run(os.getenv('TOKEN'))