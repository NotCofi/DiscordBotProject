
import re
from discord.ext import commands


disabled_channels = set()


class Filter(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.disabled_channels = disabled_channels

        # TODO: Get rid of this ugly shit
        self.bad_patterns = [
            r"\bb+i+t+c+h+\b",
            r"n+[\W_]*i+[\W_]*g+[\W_]*g+[\W_]*a+",
            r"n+[\W_]*i+[\W_]*g[\W_]*a+",
            r"n+[\W_]*i+[\W_]*g+[\W_]*e+[\W_]*r+",
            r"f[\W_]*[uúüv4@][\W_]*[c(¢k][\W_]*[kx]",
            r"n[\W_]*[i1!|l][\W_]*[g69][\W_]*[g69][\W_]*[e3a4@][\W_]*[rhd]?",
            r"f[\W_]*[uúü4@v][\W_]*[c(¢][\W_]*[kx]",
            r"b[\W_]*[i1!|l][\W_]*[t+7][\W_]*[c(¢k][\W_]*h",
            r"\ba[\W_]*[s5$][\W_]*[s5$]\b",
            r"w[\W_]*h[\W_]*[o0][\W_]*r[\W_]*[e3]",
            r"h[\W_]*[o0][\W_]*[e3]",
            r"s[\W_]*l[\W_]*[uúüv][\W_]*t",
            r"n[\W_]*(?:i|1|!|\|)[\W_]*(?:g|9)[\W_]*(?:g|9)[\W_]*(?:e|3|a|4|@)[\W_]*r?",
            r"(?:b[\W_]*[i1!|l][\W_]*[t+7][\W_]*[c(¢k][\W_]*h|a[\W_]*[s5$]{2}|w[\W_]*h[\W_]*[o0][\W_]*r[\W_]*[e3])(?:[\W_]+(?:b[\W_]*[i1!|l][\W_]*[t+7][\W_]*[c(¢k][\W_]*h|a[\W_]*[s5$]{2}|w[\W_]*h[\W_]*[o0][\W_]*r[\W_]*[e3]))+",
            r"(have\s+sex|sex\s+with|want\s+sex|let'?s\s+have\s+sex|send\s+nudes?)"

        ]

        # We are checking everything with AI? Talk about surveillance.
        self.bad_patterns_uncertain = [
            r"[A-Za-z0-9+/]{8,}(?:\s*=?)={0,2}",
            r"(?:(?:\b|_)\w{1,2}\W?){2,}",
            r"([!@#$%^&*])\1{5,}",
            r"[\W]{10,}",
            r"\b[a@4][e3][i1!|l][o0][uúüv]\b",
        ]

    # Checks if the user using the command has permissions to
    def is_admin_or_mod(self, member):
        perms = member.guild_permissions
        return perms.administrator or perms.manage_guild or perms.manage_messages


    # Checks if the message is breaking the filter.
    def contains_bad_word(self, text):
        text = text.lower()
        return any(re.search(pattern, text) for pattern in self.bad_patterns)


    # Checks if the channel the message was sent in is in disabled channels; if so, do nothing.
    def should_delete(self, message):
        if message.channel.id in disabled_channels:
            return False
        return self.contains_bad_words(message.content)

    # Disable the filter command.
    @commands.command(name="filter_disable", aliases=["fd"])
    async def filter_disable(self, ctx):
        if not self.is_admin_or_mod(ctx.author):
            await ctx.send("You are not allowed to use this command.", delete_after=3)
            return
        if ctx.channel.id in disabled_channels:
            await ctx.send("This channel is already disabled.", delete_after=3)
            return

        # Adds the disabled channel to the disabled_channels set
        disabled_channels.add(ctx.channel.id)
        await ctx.send(f"Disabled channel: {ctx.channel.mention}", delete_after=3)

    # Enable channel filtering.
    @commands.command(name="filter_enable", aliases=["fe"])
    async def filter_enable(self, ctx):
        if not self.is_admin_or_mod(ctx.author):
            await ctx.send("You are not allowed to use this command.", delete_after=3)
            return
        if ctx.channel.id not in disabled_channels:
            await ctx.send("Filtering in this channel is already enabled.", delete_after=3)
            return

        # Removes the channel the command was sent in from filtering
        disabled_channels.remove(ctx.channel.id)
        await ctx.send(f"Filtering **enabled** channel in {ctx.channel.mention}", delete_after=3)

    @commands.Cog.listener()
    # Checks if message sent trips the uncertain patterns
    async def is_uncertain(self, message):
        return any(re.search(p, message.content) for p in self.bad_patterns_uncertain)

    @commands.Cog.listener()
    async def on_message(self, message):
        raw = message.content
        ai_cog = self.bot.get_cog("AiFilter")

        if message.author.bot:
            return

        # Prevents the bot from responding twice to its own message.
        ctx = await self.bot.get_context(message)
        if ctx.valid:
            return

        if message.channel.id in disabled_channels:
            return


        if any(re.search(p, raw, flags=re.IGNORECASE) for p in self.bad_patterns):
            await message.delete()
            await ctx.channel.send("**REGEX:** Deleted!", delete_after=3)
            return

        # Ai-Mod: if message looks like an attempt to bypass filters
        if await self.is_uncertain(message):
            ai_cog = self.bot.get_cog("AiFilter")
            if ai_cog:
                verdict = await ai_cog.ai_moderator(message.content)
                if verdict is True:
                    try:
                        await message.delete()
                        await message.channel.send("**AI**: Deleted!", delete_after=3)
                    except Exception:
                        pass
            return

        await self.bot.process_commands(message)


@commands.Cog.listener()
async def on_raw_message_edit(self, payload):
    ai_cog = self.bot.get_cog("AiFilter")

    channel = self.bot.get_channel(payload.channel_id)
    if not channel:
        return

    content = payload.data.get("content")
    if not content:
        return

    try:
        message = await channel.fetch_message(payload.message_id)
    except Exception:
        return

    if getattr(payload, "user_id", None) == self.bot.user.id:
        return

    if payload.channel_id in disabled_channels:
        return

    if any(re.search(content, p) for p in self.bad_patterns):
        await message.delete()
        await channel.send("**REGEX:** Deleted!", delete_after=3)

    if await self.is_uncertain(message):
        ai_cog = self.bot.get_cog("AiFilter")

        if not self.bot.get_cog("AiFilter"):
            print("Ai Cog not found!")
            return

        if ai_cog:
            verdict = await ai_cog.ai_moderator(message.content)
            try:
                if verdict is True:
                    await message.delete()
                    await message.channel.send("**AI**: Deleted!", delete_after=3)
            except Exception as e:
                return


async def setup(bot):
    await bot.add_cog(Filter(bot))
