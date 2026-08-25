import logging
from dotenv import load_dotenv

import os
from bot_instance import bot
from pathlib import Path

load_dotenv()
token = os.getenv("DISCORD_TOKEN")


# Setup logs
handler = logging.FileHandler('discord.logs.log', encoding='utf-8')
logging.getLogger().addHandler(handler)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

logging.getLogger().setLevel(logging.DEBUG)


# Shows which cogs failed to load.
async def load_cogs():
    try:
        logging.info("Attempting to load cogs...")
        for filename in Path("./cogs").glob("*.py"):
            if filename.name.startswith("_"):
                continue
            if filename.suffix == ".py":
                try:
                    await bot.load_extension(f"cogs.{filename.stem}")
                    logging.info(f"Loaded: cogs.{filename.stem}")
                except Exception as e:
                    logging.error(f"Failed to load cog {filename.stem}. Reason: {e}")

    except Exception as e:
        logging.error(f"General cog failure: {e}")


bot.setup_hook = load_cogs
logging.getLogger("discord").setLevel(logging.WARNING)

bot.run(token, log_level=logging.DEBUG)