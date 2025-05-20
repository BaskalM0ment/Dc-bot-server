import discord
from discord.ext import commands
import os

# Set up required Discord intents
intents = discord.Intents.default()
intents.message_content = True  # Allows the bot to read messages

# Create the bot with a prefix and the required intents
bot = commands.Bot(command_prefix="!", intents=intents)

# Triggered when the bot connects successfully
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

# A simple command: !ping
@bot.command()
async def ping(ctx):
    await ctx.send("🏓 Pong!")

# Debug print to verify token is being read from Railway variables
print("DISCORD_TOKEN from env:", os.getenv("DISCORD_TOKEN"))

# Start the bot using the token stored in Railway environment variables
bot.run(os.getenv("DISCORD_TOKEN"))
