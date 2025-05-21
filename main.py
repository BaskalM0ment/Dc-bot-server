import interactions
import openai
import os

# Set OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Enable necessary Discord intents
intents = interactions.Intents.DEFAULT | interactions.Intents.GUILD_MEMBERS | interactions.Intents.GUILD_MESSAGES

# Create the bot client
bot = interactions.Client(token=os.getenv("DISCORD_TOKEN"), intents=intents)

# =========================
# Slash Command: /ping
# =========================
@interactions.slash_command(name="ping", description="Check bot responsiveness")
async def ping(ctx: interactions.SlashContext):
    await ctx.send("Pong! 🏓")

# =========================
# Slash Command: /kick
# =========================
@interactions.slash_command(name="kick", description="Kick a user")
@interactions.slash_option(
    name="user",
    description="User to kick",
    required=True,
    opt_type=interactions.OptionType.USER
)
async def kick(ctx: interactions.SlashContext, user: interactions.Member):
    if not ctx.member.permissions.kick_members:
        await ctx.send("❌ You don't have permission to kick members.", ephemeral=True)
        return
    await user.kick()
    await ctx.send(f"👢 {user.user.username} has been kicked.")

# =========================
# Slash Command: /ban
# =========================
@interactions.slash_command(name="ban", description="Ban a user")
@interactions.slash_option(
    name="user",
    description="User to ban",
    required=True,
    opt_type=interactions.OptionType.USER
)
async def ban(ctx: interactions.SlashContext, user: interactions.Member):
    if not ctx.member.permissions.ban_members:
        await ctx.send("❌ You don't have permission to ban members.", ephemeral=True)
        return
    await user.ban()
    await ctx.send(f"⛔ {user.user.username} has been banned.")

# =========================
# Slash Command: /purge
# =========================
@interactions.slash_command(name="purge", description="Delete messages in a channel")
@interactions.slash_option(
    name="amount",
    description="Number of messages to delete",
    required=True,
    opt_type=interactions.OptionType.INTEGER
)
async def purge(ctx: interactions.SlashContext, amount: int):
    if not ctx.member.permissions.manage_messages:
        await ctx.send("❌ You don't have permission to manage messages.", ephemeral=True)
        return
    messages = await ctx.channel.history(limit=amount)
    for msg in messages:
        await msg.delete()
    await ctx.send(f"🧹 Deleted {amount} messages.")

# =========================
# Slash Command: /ask
# =========================
@interactions.slash_command(name="ask", description="Ask ChatGPT a question")
@interactions.slash_option(
    name="question",
    description="Your question for ChatGPT",
    required=True,
    opt_type=interactions.OptionType.STRING
)
async def ask(ctx: interactions.SlashContext, question: str):
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": question}
            ]
        )
        await ctx.send(response.choices[0].message.content)
    except Exception as e:
        await ctx.send(f"OpenAI error: {e}")

# =========================
# Start the bot
# =========================
bot.start()
