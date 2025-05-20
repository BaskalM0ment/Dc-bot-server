import os
import discord
from discord.ext import commands
from discord import app_commands

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"✅ Logged in as {bot.user}")

@bot.tree.command(name="ping", description="Check bot status")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("🏓 Pong!")

bot.run(os.getenv("MTA1MjU3MTY4Mzc2MTk1MDc2MA.GrvarT.vcNeLNZ4deuL25wGMgJhEAyrHLIbBxqXq4hHx8"))
print("MTA1MjU3MTY4Mzc2MTk1MDc2MA.GrvarT.vcNeLNZ4deuL25wGMgJhEAyrHLIbBxqXq4hHx8 from env:"os.getenv("MTA1MjU3MTY4Mzc2MTk1MDc2MA.GrvarT.vcNeLNZ4deuL25wGMgJhEAyrHLIbBxqXq4hHx8"))