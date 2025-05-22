import interactions
import os
import requests

# Load environment variables
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
PASTEBIN_API_KEY = os.getenv("PASTEBIN_API_KEY")

# Set up Discord bot with intents
intents = interactions.Intents.DEFAULT | interactions.Intents.GUILD_MEMBERS
bot = interactions.Client(token=DISCORD_TOKEN, intents=intents)

# ====== /ping ======
@bot.command()
@interactions.option()
async def ping(ctx: interactions.CommandContext):
    await ctx.send("🏓 Pong!")

# ====== /kick ======
@bot.command()
@interactions.option("user", description="User to kick", type=interactions.OptionType.USER, required=True)
async def kick(ctx: interactions.CommandContext, user: interactions.Member):
    if not ctx.member or not ctx.member.permissions.kick_members:
        await ctx.send("❌ You don't have permission to kick members.", ephemeral=True)
        return
    try:
        await user.kick()
        await ctx.send(f"👢 {user.user.username} has been kicked.")
    except Exception as e:
        await ctx.send(f"Error kicking user: {e}", ephemeral=True)

# ====== /ban ======
@bot.command()
@interactions.option("user", description="User to ban", type=interactions.OptionType.USER, required=True)
async def ban(ctx: interactions.CommandContext, user: interactions.Member):
    if not ctx.member or not ctx.member.permissions.ban_members:
        await ctx.send("❌ You don't have permission to ban members.", ephemeral=True)
        return
    try:
        await user.ban()
        await ctx.send(f"⛔ {user.user.username} has been banned.")
    except Exception as e:
        await ctx.send(f"Error banning user: {e}", ephemeral=True)

# ====== /purge ======
@bot.command()
@interactions.option("amount", description="Number of messages to delete", type=interactions.OptionType.INTEGER, required=True)
async def purge(ctx: interactions.CommandContext, amount: int):
    if not ctx.member or not ctx.member.permissions.manage_messages:
        await ctx.send("❌ You don't have permission to purge messages.", ephemeral=True)
        return
    try:
        deleted = await ctx.channel.purge(limit=amount)
        await ctx.send(f"🧹 Deleted {len(deleted)} messages.", ephemeral=True)
    except Exception as e:
        await ctx.send(f"Error purging messages: {e}", ephemeral=True)

# ====== /ask ======
@bot.command(name="ask", description="Ask LLaMA a question")
@interactions.option("question", description="Your question", type=interactions.OptionType.STRING, required=True)
async def ask(ctx: interactions.CommandContext, question: str):
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
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=60
        )
        response.raise_for_status()
        data = response.json()
        answer = data["choices"][0]["message"]["content"]

        if len(answer) <= 1900:
            await ctx.send(answer)
        else:
            paste_data = {
                'api_dev_key': PASTEBIN_API_KEY,
                'api_option': 'paste',
                'api_paste_code': answer,
                'api_paste_name': f"Ask LLaMA: {question[:40]}",
                'api_paste_expire_date': '1D',
                'api_paste_private': '1'
            }
            paste_response = requests.post("https://pastebin.com/api/api_post.php", data=paste_data)
            await ctx.send(f"📄 Response too long: {paste_response.text}")
    except Exception as e:
        await ctx.send(f"OpenRouter error: {e}", ephemeral=True)

# Start the bot
if __name__ == "__main__":
    bot.start()
