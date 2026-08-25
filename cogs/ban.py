import discord
from discord.ext import commands
import discord.client

client = discord.client


class ban(commands.Cog):
    def __init__(self, bot, db):
        self.bot = bot
        self.db = db

    # Ban command
    @commands.command(name='ban')
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason="No reason was given."):
        if member is None:
            return
        await member.ban(reason=reason)
        await ctx.send(f"Banned {member.mention}! for: {reason}", delete_after=3)
        self.db.add_bans(str(member.id), str(ctx.author.id), reason)

    # Ban info command
    @commands.command(name="ban_info")
    @commands.has_permissions(ban_members=True)
    async def ban_info(self, ctx, ban_id: int):
        ban_record = self.db.get_ban(ban_id)
        if ban_record is None:
            await ctx.send("**❌ Ban ID not found!**")
            return

        user_id = ban_record['user_id']
        moderator_id = ban_record['moderator_id']
        reason = ban_record['reason']
        timestamp = ban_record['timestamp']

        embed = discord.Embed(
            title="Ban Info",
            description="Ban information",
            colour=discord.Colour.blue(),
        )
        embed.add_field(name="User ID", value=ban_record['user_id'], inline=False)

        embed.add_field(name="User ID", value=user_id, inline=False)
        embed.add_field(name="Moderator ID", value=moderator_id, inline=False)
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.add_field(name="Timestamp", value=timestamp, inline=False)
        await ctx.send(embed=embed)


# Banlist command
    @commands.command(name="banlist")
    @commands.has_permissions(ban_members=True)
    async def banlist(self, ctx):
        bans = self.db.get_all_bans()

        if not bans:
            await ctx.send("No bans found!")
            return

        embed = discord.Embed(
            title="Ban List",
            description=f"Total Bans: {len(bans)}",
            colour=discord.Colour.dark_red()
        )

        for ban in bans[:10]:
            ban_id = ban['ban_id']
            user_id = ban['user_id']
            moderator_id = ban['moderator_id']
            reason = ban['reason']
            timestamp = ban['timestamp']

        embed.add_field(name=f"Ban ID, {ban_id}",
                        value=f"User: {user_id}\nModerator: {moderator_id}\nReason: {reason}\nTime: {timestamp}",
                        inline=False
                        )
        await ctx.send(embed=embed)


    @commands.command(name="unban")
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, user_id: int):
        user = await self.bot.fetch_user(user_id)
        if not user:
            await ctx.send("**User not found, make sure you used their ID**")
            return

        try:
            await ctx.guild.unban(user)
            self.db.remove_bans_by_user(str(user.id))
            await ctx.send(f"✅**Unbanned {user.mention}**")

        except commands.MissingPermissions:
            await ctx.send("You are not allowed to use this command")

        except discord.NotFound:
            await ctx.send("**That user isn't banned**")

        except Exception as e:
            await ctx.send(f"**Something went wrong, {e}**")


async def setup(bot):
    from bot_instance import db
    await bot.add_cog(ban(bot, db))
