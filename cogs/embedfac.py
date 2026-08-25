import discord
from discord.ui import View, Button
from discord.ext import commands


class Help_Cog(commands.Cog):
        def __init__(self, bot: commands.Bot):
            self.bot = bot

        @commands.command(name="help")
        async def help_command(self, ctx):
            view = HelpView(ctx.author.id)
            await ctx.send(embed=HELP_PAGE[0], view=view)


def make_embed(title: str, description: str = "", fields=None):
    embed = discord.Embed(
        title = title,
        description = description,
        color = discord.Color.dark_embed()
    )

    if fields:
        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)

    embed.set_footer(text="Use the buttons below to navigate")
    return embed


HELP_PAGE = [
    make_embed(
        "🧠 Grog Bot Help",
    "Grog is a moderation-focused Discord bot with optional AI chat.\n\n"
        "It blocks slurs, harassment, self-harm content, and bypass attempts.",
        fields=[
            ("🛡️ Moderation", "Automatic filtering using regex + AI", False),
            ("🤖 Chat", "Optional AI chatbot (server-controlled)", False),
            ("⚙️ Control", "Admin-only configuration", False),
            ]
        ),

    make_embed(
        "🛡️ Moderation",
        fields=[
            ("Automatic Filtering",
             "Messages are using checked using:\n• AI fallback\n• Anti-bypass detection",
             False),
            ("Commands",
             "'-filter_enable'\n'-fe'\n'filter_disable'\n'-fd'",
             False)

        ]
    ),

    make_embed(
        "🤖 AI Chat",
        "Grok responds when mentioned.\nChat can disabled per server",
        fields=[
            ("Behaviour",
             "• Temporary memory\n Prompt-injection resistant\n• Moderated output",
             False)
        ]

    ),

    make_embed(
        "⚙️ Admin Controls",
        "Requires admin or moderator permissions.",
        fields=[
            ("Commands",
             "-settings'\n'set_log_channel'",
             False),
            ("Options",
             "• Toggle moderation\n• Toggle chat\n• Toggle AI fallback",
             False)
        ]
    ),

    make_embed(
        "📊 Bot Status",
        fields=[
            ("Command", "'-status'", False),
            ("Shows",
             "• Uptime\n• Model in use\n• Queue status\n• API health",
             False)
        ]
    ),

    make_embed(
        "Bot Version"

    )
]

class HelpView(View):
    def __init__(self, user_id: int):
            super().__init__(timeout=60)
            self.user_id = user_id
            self.page = 0

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.user_id


    @discord.ui.button(label="⬅️", style=discord.ButtonStyle.secondary)
    async def previous(self, interaction: discord.Interaction, button: Button):
        self.page -= 1
        await self.update(interaction)

    @discord.ui.button(label="➡️", style=discord.ButtonStyle.secondary)
    async def next(self, interaction: discord.Interaction, button: Button):
        self.page += 1
        await self.update(interaction)

    @discord.ui.button(label="❌", style=discord.ButtonStyle.danger)
    async def close(self, interaction, button):
        await interaction.message.delete()

    async def update(self, interaction: discord.Interaction):
        self.page = max(0, min(self.page, len(HELP_PAGE) - 1))

        self.previous.disabled = self.page == 0
        self.next.disabled = self.page == len(HELP_PAGE) - 1

        await interaction.response.edit_message(
            embed=HELP_PAGE[self.page],
            view=self
        )

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True

async def setup(bot):
    await bot.add_cog(Help_Cog(bot))


