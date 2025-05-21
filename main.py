import interactions
import openai
import os
import asyncio

# Set OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Enable necessary Discord intents
intents = (
    interactions.Intents.DEFAULT
    | interactions.Intents.GUILD_MEMBERS
    | interactions.Intents.GUILD_MESSAGES
)

# Create the bot client
bot = interactions.Client(token=os.getenv("DISCORD_TOKEN"), intents=intents)

# =========================
# Slash Command: /ping
# =========================
@bot.command(
    name="ping",
    description="Check bot responsiveness",
    scope=None,  # global command, you can specify guild ids if needed
)
async def ping(ctx: interactions.CommandContext):
    await ctx.send("Pong! 🏓")

# =========================
# Slash Command: /kick
# =========================
@bot.command(
    name="kick",
    description="Kick a user",
    options=[
        interactions.Option(
            name="user",
            description="User to kick",
            type=interactions.OptionType.USER,
            required=True,
        )
    ],
)
async def kick(ctx: interactions.CommandContext, user: interactions.Member):
    if not ctx.author.permissions.kick_members:
        await ctx.send("❌ You don't have permission to kick members.", ephemeral=True)
        return
    try:
        await user.kick()
        await ctx.send(f"👢 {user.user.username} has been kicked.")
    except Exception as e:
        await ctx.send(f"Failed to kick user: {e}", ephemeral=True)

# =========================
# Slash Command: /ban
# =========================
@bot.command(
    name="ban",
    description="Ban a user",
    options=[
        interactions.Option(
            name="user",
            description="User to ban",
            type=interactions.OptionType.USER,
            required=True,
        )
    ],
)
async def ban(ctx: interactions.CommandContext, user: interactions.Member):
    if not ctx.author.permissions.ban_members:
        await ctx.send("❌ You don't have permission to ban members.", ephemeral=True)
        return
    try:
        await user.ban()
        await ctx.send(f"⛔ {user.user.username} has been banned.")
    except Exception as e:
        await ctx.send(f"Failed to ban user: {e}", ephemeral=True)

# =========================
# Slash Command: /purge
# =========================
@bot.command(
    name="purge",
    description="Delete messages in a channel",
    options=[
        interactions.Option(
            name="amount",
            description="Number of messages to delete",
            type=interactions.OptionType.INTEGER,
            required=True,
        )
    ],
)
async def purge(ctx: interactions.CommandContext, amount: int):
    if not ctx.author.permissions.manage_messages:
        await ctx.send("❌ You don't have permission to manage messages.", ephemeral=True)
        return

    # Fetch and delete messages
    try:
        # interactions.py currently does not provide a direct way to fetch message history,
        # so we can use discord.py or fallback to using interactions Client HTTP requests,
        # but here we assume a small amount and try deleting recent messages from the channel.

        deleted_count = 0
        async for message in ctx.channel.history(limit=amount):
            await message.delete()
            deleted_count += 1
        await ctx.send(f"🧹 Deleted {deleted_count} messages.", ephemeral=True)
    except Exception as e:
        await ctx.send(f"Failed to delete messages: {e}", ephemeral=True)

# =========================
# Slash Command: /ask
# =========================
@bot.command(
    name="ask",
    description="Ask ChatGPT a question",
    options=[
        interactions.Option(
            name="question",
            description="Your question for ChatGPT",
            type=interactions.OptionType.STRING,
            required=True,
        )
    ],
)
async def ask(ctx: interactions.CommandContext, question: str):
    await ctx.defer()  # Acknowledge command and give more time for response
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": question},
            ],
            max_tokens=500,
            temperature=0.7,
        )
        answer = response.choices[0].message.content.strip()
        await ctx.send(answer)
    except Exception as e:
        await ctx.send(f"OpenAI error: {e}", ephemeral=True)

# =========================
# Run the bot
# =========================
if __name__ == "__main__":
    bot.start()
