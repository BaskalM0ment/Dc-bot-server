import sys
import os
import interactions

print("Starting minimal debug bot...")
print(f"Python version: {sys.version}")

try:
    print(f"interactions.py version: {interactions.__version__}")
except Exception as e:
    print(f"Failed to get interactions.py version: {e}")

print(f"DISCORD_TOKEN set: {'DISCORD_TOKEN' in os.environ}")
print(f"OPENROUTER_API_KEY set: {'OPENROUTER_API_KEY' in os.environ}")
print(f"PASTEBIN_API_KEY set: {'PASTEBIN_API_KEY' in os.environ}")

bot = interactions.Client(token=os.getenv("DISCORD_TOKEN"))

@bot.slash_command(name="ping", description="Ping the bot")
async def ping(ctx: interactions.SlashContext):
    print("Received ping command")
    await ctx.send("Pong!")

if __name__ == "__main__":
    print("Starting bot client...")
    bot.start()
