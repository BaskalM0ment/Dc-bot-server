import interactions
import os
import requests

# Load API keys from environment variables
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
PASTEBIN_API_KEY = os.getenv("PASTEBIN_API_KEY")

# Set up bot
intents = interactions.Intents.DEFAULT | interactions.Intents.GUILD_MEMBERS | interactions.Intents.MESSAGE_CONTENT
bot = interactions.Client(token=os.getenv("DISCORD_TOKEN"), intents=intents)


# ====== /ping ======
@interactions.slash_command(name="ping", description="Check bot responsiveness")
async def ping(ctx: interactions.SlashContext):
    await ctx.send("Pong! 🏓")


# ====== /kick ======
@interactions.slash_command(name="kick", description="Kick a user from the server")
@interactions.slash_option(
    name="member",
    description="The member to kick",
    opt_type=interactions.OptionType.USER,
    required=True
)
async def kick(ctx: interactions.SlashContext, member: interactions.User):
    guild = await ctx.get_guild()
    target = await guild.fetch_member(member.id)
    if not ctx.author.guild_permissions.kick_members:
        await ctx.send("❌ You don't have permission to kick members.", ephemeral=True)
        return
    try:
        await target.kick()
        await ctx.send(f"👢 {target.user.username} has been kicked.")
    except Exception as e:
        await ctx.send(f"Failed to kick member: {e}", ephemeral=True)


# ====== /ban ======
@interactions.slash_command(name="ban", description="Ban a user from the server")
@interactions.slash_option(
    name="member",
    description="The member to ban",
    opt_type=interactions.OptionType.USER,
    required=True
)
async def ban(ctx: interactions.SlashContext, member: interactions.User):
    guild = await ctx.get_guild()
    target = await guild.fetch_member(member.id)
    if not ctx.author.guild_permissions.ban_members:
        await ctx.send("❌ You don't have permission to ban members.", ephemeral=True)
        return
    try:
        await target.ban()
        await ctx.send(f"⛔ {target.user.username} has been banned.")
    except Exception as e:
        await ctx.send(f"Failed to ban member: {e}", ephemeral=True)


# ====== /purge ======
@interactions.slash_command(name="purge", description="Delete messages from a channel")
@interactions.slash_option(
    name="amount",
    description="Number of messages to delete",
    opt_type=interactions.OptionType.INTEGER,
    required=True,
)
async def purge(ctx: interactions.SlashContext, amount: int):
    if not ctx.author.guild_permissions.manage_messages:
        await ctx.send("❌ You don't have permission to manage messages.", ephemeral=True)
        return
    try:
        deleted = 0
        async for message in ctx.channel.history(limit=amount):
            await message.delete()
            deleted += 1
        await ctx.send(f"🧹 Deleted {deleted} messages.", ephemeral=True)
    except Exception as e:
        await ctx.send(f"Failed to purge messages: {e}", ephemeral=True)


# ====== /ask ======
@interactions.slash_command(name="ask", description="Ask LLaMA a question")
@interactions.slash_option(
    name="question",
    description="Your question for LLaMA",
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
            {"role": "system", "content": "You are a helpful assistant. Respond with detail."},
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
                'api_dev_key': PASTEBIN_API_KEY,
                'api_option': 'paste',
                'api_paste_code': answer,
                'api_paste_name': f"Response to: {question[:50]}",
                'api_paste_expire_date': '1D',
                'api_paste_private': '1'
            }
            paste_response = requests.post("https://pastebin.com/api/api_post.php", data=pastebin_data)
            await ctx.send(f"📄 Too long! View the full response here: {paste_response.text}")

    except Exception as e:
        await ctx.send(f"OpenRouter error: {e}", ephemeral=True)


# Start the bot
if __name__ == "__main__":
    bot.start()
