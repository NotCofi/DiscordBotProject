from discord.ext import commands
from bot_instance import db


class syncban(commands.Cog):

    def __init__(self, bot, db):
        self.bot = bot
        self.db = db


    @commands.command(name='syncban')
    @commands.has_permissions(administrator=True)
    async def sync_bans(self, ctx):
        guild_bans = [entry async for entry in ctx.guild.bans()]
        discord_ids = {str(entry.user.id) for entry in guild_bans}
        db_bans = self.db.get_all_bans()
        db_ids = {ban["user_id"] for ban in db_bans}

        to_add = discord_ids - db_ids
        to_remove = db_ids - discord_ids

        for user_id in to_add:
            self.db.add_bans(user_id, "SYSTEM", "Synced from Discord")

        for user_id in to_remove:
            self.db.remove_bans_by_user(user_id)

        await ctx.send(f"✅ Sync Completed!")


async def setup(bot):
    await bot.add_cog(syncban(bot, db))