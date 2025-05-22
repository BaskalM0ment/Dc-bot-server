import interactions
import os
import requests

# Load API keys from environment variables
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
PASTEBIN_API_KEY = os.getenv("PASTEBIN_API_KEY")

# Setup Discord bot intents
intents = interactions.Intents.DEFAULT | interactions.Intents.GUILD_MEMBERS

# Initialize bot client
bot = interactions.Client(token=DISCORD_TOKEN, intents=intents)

# Sync slash commands when bot is ready
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.me.name}")
    await bot.sync_commands()
    print("🔄 Synced slash commands.")

# ====== /ask (Ask LLaMA a Question) ======
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
            {"role": "system", "content": "You are a helpful assistant. Respond with full detail."},
            {"role": "user", "content": question}
        ],
        "max_tokens": 4096,
        "temperature": 0.7
    }

    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload, timeout=60)
        data = response.json()
        answer = data["choices"][0]["message"]["content"]

        if len(answer) < 1900:
            await ctx.send(answer)
        else:
            pastebin_data = {
                "api_dev_key": PASTEBIN_API_KEY,
                "api_option": "paste",
                "api_paste_code": answer,
                "api_paste_name": f"Response to: {question[:50]}",
                "api_paste_expire_date": "1D",
                "api_paste_private": "1"
            }
            paste_response = requests.post("https://pastebin.com/api/api_post.php", data=pastebin_data)
            await ctx.send(f"📄 The response is too long. View it here: {paste_response.text}")
    except Exception as e:
        await ctx.send(f"OpenRouter error: {e}", ephemeral=True)

# ====== /kick ======
@interactions.slash_command(name="kick", description="Kick a user")
@interactions.slash_option(
    name="user",
    description="User to kick",
    opt_type=interactions.OptionType.USER,
    required=True,
)
async def kick(ctx: interactions.SlashContext, user: interactions.User):
    guild = await ctx.get_guild()
    target = await guild.get_member(user.id)
    member = await guild.get_member(ctx.author.id)

    if not member.permissions.kick_members:
        await ctx.send("❌ You don't have permission to kick members.", ephemeral=True)
        return

    try:
        await target.kick()
        await ctx.send(f"👢 {target.user.username} has been kicked.")
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
async def ban(ctx: interactions.SlashContext, user: interactions.User):
    guild = await ctx.get_guild()
    target = await guild.get_member(user.id)
    member = await guild.get_member(ctx.author.id)

    if not member.permissions.ban_members:
        await ctx.send("❌ You don't have permission to ban members.", ephemeral=True)
        return

    try:
        await target.ban()
        await ctx.send(f"⛔ {target.user.username} has been banned.")
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
    guild = await ctx.get_guild()
    member = await guild.get_member(ctx.author.id)

    if not member.permissions.manage_messages:
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

# ====== Run Bot ======
if __name__ == "__main__":
    bot.start()
