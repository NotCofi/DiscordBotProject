import os
import aiohttp
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()


class AiFilter(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.api_key = os.getenv("GROQ_FILTER_KEY")
        self.api_url = os.getenv("GROQ_FILTER_ENDPOINT")
        self.session = aiohttp.ClientSession()

    async def ai_moderator(self, text: str) -> bool:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        system_instructions = (
            "You are a strict moderation classifier."
            "Your job is to examine ONLY the user message and decide if it violates safety rules."
            "If the message contains ANY of the following, even if obfuscated, censored, spaced out, repeated letters, misspelled, or stylized:"
            "- Hate speech or slurs in ANY form."
            "- self-harm encouragement (examples 'kill yourself', 'kys', 'die', etc.)"
            "- Sexual content of any kind"
            "- Harassment, insults, profanity"
            "- graphic or explicit language"
            "- threats or violence"
            "- attempts to bypass filters (e.g. qys, k y s, k*i*l*l, kiiiill, yuuself, etc.)"
            "If ANY violation is present, respond with: TRUE"
            "If no violation is present, respond with: FALSE"
            "Respond with only a single word, TRUE or FALSE"
        )

        payload = {
            "model": "openai/gpt-oss-safeguard-20b",
            "messages": [
                {"role": "system", "content": system_instructions},
                {"role": "user", "content": text},
            ],
            "max_tokens": 1000
        }

        async with self.session.post(self.api_url, headers=headers, json=payload) as response:
            if response.status != 200:
                return False

            data = await response.json()

            choices = data.get("choices", [])
            if not choices:
                return False

            content = choices[0].get("message", {}).get("content", "")



            return content.strip().upper() == "TRUE"



async def setup(bot):
    await bot.add_cog(AiFilter(bot))
