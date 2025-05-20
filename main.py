import discord
from discord.ext import commands
import os

bot = commands.Bot(command_prefix="!")

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

# Example command
@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")

# Start the bot using the token from environment
bot.run(os.getenv("DISCORD_TOKEN"))
