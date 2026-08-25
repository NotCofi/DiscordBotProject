import discord

from discord.ext import commands
import asyncio
from discord.ext import tasks



class Delete(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.job_queue = asyncio.Queue(maxsize=200)
        self.job_worker.start()

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.job_worker.is_running():
            self.job_worker.start()

    @commands.command(name="delete", aliases=["del"])
    @commands.has_permissions(manage_messages=True)
    async def delete(self, ctx, amount: int):
        if self.job_queue.full():
            return await ctx.send("The line is busy. Sorry.", delete_after=3)

        job = {
            "func": self.delete_worker,
            "args": (ctx, amount),
        }
        await self.job_queue.put(job)
        # We return None to stop IDE from bitching about "MiSsInG rEtUrN sTaTeMeNtS oN sOmE pAtHs"
        return None

    async def delete_worker(self, ctx, amount):
        try:
            deleted = await ctx.channel.purge(limit=amount + 1)
            await ctx.send(f"Deleted {len(deleted) - 1} ", delete_after=3)
        except discord.Forbidden:
            await ctx.send(f"I do not have the permission to delete messages here.", delete_after=3)

    @tasks.loop(seconds=.8)
    async def job_worker(self):
        job = await self.job_queue.get()
        func = job["func"]
        args = job["args"]
        try:
            await func(*args)
        except Exception as e:
            print(f"An error occurred: {e}")
        self.job_queue.task_done()

async def setup(bot):
    await bot.add_cog(Delete(bot))
