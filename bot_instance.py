from discord.ext import commands
import discord
import os

from realdatabase import puckvault

PREFIX = "-"





intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix=PREFIX,
                   intents=intents,
                   help_command=None)
creator = "LedMasker"
creator_id = "1125160333057724517"



from database import Database


DB_PATH = os.path.join(os.path.dirname(__file__), "bans")
db = Database(DB_PATH)

NHL_DB_PATH = os.path.join(os.path.dirname(__file__), "puck_vault.db")
db_nhl = puckvault(NHL_DB_PATH)


