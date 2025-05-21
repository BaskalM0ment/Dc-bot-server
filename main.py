import interactions
import os
from openai import OpenAI  # New import style

# Initialize OpenAI client properly without proxies
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Enable necessary Discord intents
intents = interactions.Intents.DEFAULT | interactions.Intents.GUILD_MEMBERS | interactions.Intents.GUILD_MESSAGES

# Create the bot client
bot = interactions.Client(token=os.getenv("DISCORD_TOKEN"), intents=intents)

# ... your other commands here (ping, kick, ban, purge) unchanged ...

# =========================
# Slash Command: /ask
# =========================
@interactions.slash_command(name="ask", description="Ask ChatGPT a question")
@interactions.slash_option(
    name="question",
    description="Your question for ChatGPT",
    required=True,
    opt_type=interactions.OptionType.STRING
)
async def ask(ctx: interactions.SlashContext, question: str):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": question}
            ]
        )
        await ctx.send(response.choices[0].message.content)
    except Exception as e:
        await ctx.send(f"OpenAI error: {e}")

# =========================
# Start the bot
# =========================
bot.start()
