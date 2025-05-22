import interactions
import os
import requests

# Load API keys from environment variables
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
PASTEBIN_API_KEY = os.getenv("PASTEBIN_API_KEY")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

# Define Discord intents
intents = (
    interactions.Intents.GUILDS
    | interactions.Intents.GUILD_MESSAGES
    | interactions.Intents.GUILD_MEMBERS
)

# Initialize bot
bot = interactions.Client(token=DISCORD_TOKEN, intents=intents)

# ====== /ping ======
@interactions.slash_command(name="ping", description="Check bot responsiveness")
async def ping(ctx: interactions.SlashContext):
    await ctx.send("Pong! 🏓")

# ====== /kick ======
@interactions.slash_command(name="kick", description="Kick a user")
@interactions.slash_option(
    name="user",
    description="User to kick",
    opt_type=interactions.OptionType.USER,
    required=True,
)
async def kick(ctx: interactions.SlashContext, user: interactions.Member):
    member = await ctx.guild.fetch_member(ctx.author.id)
    if not member or not member.permissions.has(interactions.Permissions.KICK_MEMBERS):
        await ctx.send("❌ You don't have permission to kick members.", ephemeral=True)
        return
    try:
        await user.kick()
        await ctx.send(f"👢 {user.user.username} has been kicked.")
    except Exception as e:
        await ctx.send(f"Failed to kick user: {e}", ephemeral=True)

# ====== /ban ======
@interactions.slash_command(name="ban", description="Ban a user")
@interactions.slash_option(
    name="user",
    description="User to ban",
    opt_type=interactions.OptionType.USER,
    required=True,
)
async def ban(ctx: interactions.SlashContext, user: interactions.Member):
    member = await ctx.guild.fetch_member(ctx.author.id)
    if not member or not member.permissions.has(interactions.Permissions.BAN_MEMBERS):
        await ctx.send("❌ You don't have permission to ban members.", ephemeral=True)
        return
    try:
        await user.ban()
        await ctx.send(f"⛔ {user.user.username} has been banned.")
    except Exception as e:
        await ctx.send(f"Failed to ban user: {e}", ephemeral=True)

# ====== /purge ======
@interactions.slash_command(name="purge", description="Delete messages in a channel")
@interactions.slash_option(
    name="amount",
    description="Number of messages to delete",
    opt_type=interactions.OptionType.INTEGER,
    required=True,
)
async def purge(ctx: interactions.SlashContext, amount: int):
    member = await ctx.guild.fetch_member(ctx.author.id)
    if not member or not member.permissions.has(interactions.Permissions.MANAGE_MESSAGES):
        await ctx.send("❌ You don't have permission to manage messages.", ephemeral=True)
        return
    try:
        deleted = 0
        async for message in ctx.channel.history(limit=amount):
            await message.delete()
            deleted += 1
        await ctx.send(f"🧹 Deleted {deleted} messages.", ephemeral=True)
    except Exception as e:
        await ctx.send(f"Failed to delete messages: {e}", ephemeral=True)

# ====== /ask (LLaMA via OpenRouter + Pastebin) ======
@interactions.slash_command(name="ask", description="Ask LLaMA a question")
@interactions.slash_option(
    name="question",
    description="Your question for the AI",
    opt_type=interactions.OptionType.STRING,
    required=True,
)
async def ask(ctx: interactions.SlashContext, question: str):
    await ctx.defer()

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "meta-llama/llama-3-8b-instruct",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": question}
        ],
        "max_tokens": 4096,
        "temperature": 0.7
    }

    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
        data = response.json()
        answer = data["choices"][0]["message"]["content"]

        if len(answer) <= 1900:
            await ctx.send(answer)
        else:
            paste_data = {
                "api_dev_key": PASTEBIN_API_KEY,
                "api_option": "paste",
                "api_paste_code": answer,
                "api_paste_private": "1",
                "api_paste_expire_date": "1D",
                "api_paste_name": f"Response to: {question[:50]}"
            }
            paste = requests.post("https://pastebin.com/api/api_post.php", data=paste_data)
            await ctx.send(f"📄 The response is too long. View it here: {paste.text}")

    except Exception as e:
        await ctx.send(f"OpenRouter error: {e}", ephemeral=True)

# ====== Start Bot ======
if __name__ == "__main__":
    bot.start()
