import nextcord
from nextcord.ext import commands
from nextcord import Interaction, SlashOption
import os
import random
import math

intents = nextcord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Bot is online as {bot.user}")

# /ping
@bot.slash_command(name="ping", description="Check if the bot is alive")
async def ping(interaction: Interaction):
    await interaction.response.send_message("🏓 Pong!")

# /kick
@bot.slash_command(name="kick", description="Kick a user")
async def kick(interaction: Interaction,
               member: nextcord.Member = SlashOption(description="User to kick"),
               reason: str = SlashOption(description="Reason", required=False, default="No reason")):
    if interaction.user.guild_permissions.kick_members:
        await member.kick(reason=reason)
        await interaction.response.send_message(f"👢 Kicked {member.name}")
    else:
        await interaction.response.send_message("🚫 You don't have permission.")

# /ban
@bot.slash_command(name="ban", description="Ban a user")
async def ban(interaction: Interaction,
              member: nextcord.Member = SlashOption(description="User to ban"),
              reason: str = SlashOption(description="Reason", required=False, default="No reason")):
    if interaction.user.guild_permissions.ban_members:
        await member.ban(reason=reason)
        await interaction.response.send_message(f"🔨 Banned {member.name}")
    else:
        await interaction.response.send_message("🚫 You don't have permission.")

# /purge
@bot.slash_command(name="purge", description="Delete messages")
async def purge(interaction: Interaction,
                amount: int = SlashOption(description="Number to delete", required=True)):
    if interaction.user.guild_permissions.manage_messages:
        await interaction.channel.purge(limit=amount)
        await interaction.response.send_message(f"🧹 Deleted {amount} messages")
    else:
        await interaction.response.send_message("🚫 You don't have permission.")

# /ask
@bot.slash_command(name="ask", description="Ask the bot a question")
async def ask(interaction: Interaction, question: str = SlashOption(description="Your question")):
    responses = [
        "Hmm, good question.",
        "I'm thinking... maybe?",
        "Definitely!",
        "Nope.",
        "Try again later!",
        "42 is the answer."
    ]
    await interaction.response.send_message(random.choice(responses))

# /calc
@bot.slash_command(name="calc", description="Calculate a math expression")
async def calc(interaction: Interaction, expression: str = SlashOption(description="Math expression")):
    try:
        result = eval(expression)
        await interaction.response.send_message(f"🧮 `{expression}` = `{result}`")
    except:
        await interaction.response.send_message("❌ Invalid math expression.")

# Run
bot.run(os.getenv("DISCORD_TOKEN"))
