import interactions
import os
import requests

# Define Discord intents
intents = (
    interactions.Intents.GUILDS
    | interactions.Intents.GUILD_MESSAGES
    | interactions.Intents.GUILD_MEMBERS
)

# Initialize the bot
bot = interactions.Client(token=os.getenv("DISCORD_TOKEN"), intents=intents)

# === Local LLaMA Response Function ===
def ask_llama(prompt):
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3",
                "prompt": prompt,
                "stream": False
            }
        )
        if response.status_code == 200:
            return response.json()["response"].strip()
        else:
            return f"❌ LLaMA error: {response.text}"
    except Exception as e:
        return f"❌ Failed to contact LLaMA: {e}"

# ====== /ping command ======
@interactions.slash_command(name="ping", description="Check bot responsiveness")
async def ping(ctx: interactions.SlashContext):
    await ctx.send("Pong! 🏓")

# ====== /kick command ======
@interactions.slash_command(name="kick", description="Kick a user")
@interactions.slash_option(
    name="user",
    description="User to kick",
    opt_type=interactions.OptionType.USER,
    required=True,
)
async def kick(ctx: interactions.SlashContext, user: interactions.Member):
    if not ctx.member.permissions.kick_members:
        await ctx.send("❌ You don't have permission to kick members.", ephemeral=True)
        return
    try:
        await user.kick()
        await ctx.send(f"👢 {user.user.username} has been kicked.")
    except Exception as e:
        await ctx.send(f"Failed to kick user: {e}", ephemeral=True)

# ====== /ban command ======
@interactions.slash_command(name="ban", description="Ban a user")
@interactions.slash_option(
    name="user",
    description="User to ban",
    opt_type=interactions.OptionType.USER,
    required=True,
)
async def ban(ctx: interactions.SlashContext, user: interactions.Member):
    if not ctx.member.permissions.ban_members:
        await ctx.send("❌ You don't have permission to ban members.", ephemeral=True)
        return
    try:
        await user.ban()
        await ctx.send(f"⛔ {user.user.username} has been banned.")
    except Exception as e:
        await ctx.send(f"Failed to ban user: {e}", ephemeral=True)

# ====== /purge command ======
@interactions.slash_command(name="purge", description="Delete messages in a channel")
@interactions.slash_option(
    name="amount",
    description="Number of messages to delete",
    opt_type=interactions.OptionType.INTEGER,
    required=True,
)
async def purge(ctx: interactions.SlashContext, amount: int):
    if not ctx.member.permissions.manage_messages:
        await ctx.send("❌ You don't have permission to manage messages.", ephemeral=True)
        return
    try:
        deleted_count = 0
        async for message in ctx.channel.history(limit=amount):
            await message.delete()
            deleted_count += 1
        await ctx.send(f"🧹 Deleted {deleted_count} messages.", ephemeral=True)
    except Exception as e:
        await ctx.send(f"Failed to delete messages: {e}", ephemeral=True)

# ====== /ask command (uses LLaMA) ======
@interactions.slash_command(name="ask", description="Ask a question to LLaMA")
@interactions.slash_option(
    name="question",
    description="Your question",
    opt_type=interactions.OptionType.STRING,
    required=True,
)
async def ask(ctx: interactions.SlashContext, question: str):
    await ctx.defer()
    answer = ask_llama(question)
    await ctx.send(answer)

# ====== Start Bot ======
if __name__ == "__main__":
    bot.start()
