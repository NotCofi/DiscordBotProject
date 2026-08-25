#TODO: make the welcome message more visually appealing

import discord
from discord.ext import commands
from bot_instance import bot


class WelcomeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        channel = None
        for c in guild.text_channels:
            if c.permissions_for(guild.me).send_messages:
                channel = c
                break

        if channel is None:
            return
        embed = discord.Embed(
    title=f"👋 Hello!",
    description=f"👋 Hello! I am {bot.user.mention}! I am as of now in early BETA. I use Llama 3.3 70B Versatile API! The API as of now is free, so mind the limits!",
    color=discord.Color.blurple()
)
        embed.set_thumbnail(url="https://wallpapersden.com/starry-landscape-4k-cool-blue-moon-wallpaper/")

        embed.add_field(name="How to use API",
                value="Ping my name in the chat and write your message.",

                )

        embed.add_field(name="Information",
                value="I have currently three commands! filter enable/disable: These enable or disable filtering for the channel it is used in. "
                      "Ban does what it says in the name. "
                      "Delete deletes the number of messages you set after the delete command.",
                        inline=False
                )

        embed.add_field(name="Disclaimer",
                value=("By using this AI, you accept that whatever is generated is your responsibility. "
                       "The programmers are not responsible for any content generated."),
                        inline=False
                )

        embed.add_field(name="Prefix?",
                value="-"
                )

        embed.set_footer(text="Contact Led Masker for suggestions or requests.")

        await channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(WelcomeCog(bot))
