import interactions
import os
from openai import OpenAI

TOKEN = os.getenv("DISCORD_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

intents = interactions.Intents.DEFAULT
bot = interactions.Client(token=TOKEN, intents=intents)

# ✅ /ping
@interactions.slash_command(name="ping", description="Check if the bot is online")
async def ping(ctx: interactions.SlashContext):
    await ctx.send("🏓 Pong!")

# ✅ /ask (ChatGPT)
@interactions.slash_command(name="ask", description="Ask ChatGPT something")
@interactions.slash_option(
    name="prompt",
    description="Your question",
    required=True,
    opt_type=interactions.OptionType.STRING
)
async def ask(ctx: interactions.SlashContext, prompt: str):
    await ctx.defer()
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        answer = response.choices[0].message.content.strip()
        await ctx.send(answer[:2000])
    except Exception as e:
        await ctx.send(f"❌ OpenAI error: {e}")

# ✅ /math (Evaluate expressions)
@interactions.slash_command(name="math", description="Solve a math expression")
@interactions.slash_option(
    name="expression",
    description="e.g. 2 + 2 * 10",
    required=True,
    opt_type=interactions.OptionType.STRING
)
async def math(ctx: interactions.SlashContext, expression: str):
    try:
        result = eval(expression, {"__builtins__": {}})
        await ctx.send(f"🧮 Result: `{result}`")
    except Exception as e:
        await ctx.send(f"❌ Error: {e}")

# ✅ /purge
@interactions.slash_command(name="purge", description="Delete messages")
@interactions.slash_option(
    name="amount",
    description="Number of messages to delete",
    required=True,
    opt_type=interactions.OptionType.INTEGER
)
async def purge(ctx: interactions.SlashContext, amount: int):
    await ctx.defer(ephemeral=True)
    if not ctx.author.permissions.manage_messages:
        await ctx.send("❌ You don't have permission to do that.")
        return
    deleted = await ctx.channel.purge(amount)
    await ctx.send(f"🧹 Deleted {len(deleted)} messages", ephemeral=True)

# ✅ /kick
@interactions.slash_command(name="kick", description="Kick a member")
@interactions.slash_option(
    name="user",
    description="User to kick",
    required=True,
    opt_type=interactions.OptionType.USER
)
async def kick(ctx: interactions.SlashContext, user: interactions.Member):
    if not ctx.author.permissions.kick_members:
        await ctx.send("❌ You don't have permission to kick members.")
        return
    await user.kick()
    await ctx.send(f"👢 {user.username} was kicked.")

# ✅ /ban
@interactions.slash_command(name="ban", description="Ban a member")
@interactions.slash_option(
    name="user",
    description="User to ban",
    required=True,
    opt_type=interactions.OptionType.USER
)
async def ban(ctx: interactions.SlashContext, user: interactions.Member):
    if not ctx.author.permissions.ban_members:
        await ctx.send("❌ You don't have permission to ban members.")
        return
    await user.ban()
    await ctx.send(f"⛔ {user.username} was banned.")

bot.start()
