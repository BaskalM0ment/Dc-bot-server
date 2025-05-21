import os
import interactions
import openai

# Load secrets
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

# Use correct Intents
bot = interactions.Client(
    token=DISCORD_TOKEN,
    intents=interactions.Intents.DEFAULT | interactions.Intents.GUILD_MEMBERS
)

# /ping
@interactions.slash_command(name="ping", description="Check if bot is alive")
async def ping(ctx: interactions.SlashContext):
    await ctx.send("🏓 Pong!")

# /kick
@interactions.slash_command(name="kick", description="Kick a member")
@interactions.slash_option(name="user", description="User to kick", required=True, opt_type=interactions.OptionType.USER)
async def kick(ctx: interactions.SlashContext, user: interactions.Member):
    if not ctx.author.permissions.kick_members:
        return await ctx.send("❌ You don't have permission to kick users.")
    await ctx.guild.kick(user)
    await ctx.send(f"✅ Kicked {user.username}")

# /ban
@interactions.slash_command(name="ban", description="Ban a member")
@interactions.slash_option(name="user", description="User to ban", required=True, opt_type=interactions.OptionType.USER)
async def ban(ctx: interactions.SlashContext, user: interactions.Member):
    if not ctx.author.permissions.ban_members:
        return await ctx.send("❌ You don't have permission to ban users.")
    await ctx.guild.ban(user)
    await ctx.send(f"✅ Banned {user.username}")

# /purge
@interactions.slash_command(name="purge", description="Delete messages")
@interactions.slash_option(name="amount", description="How many to delete", required=True, opt_type=interactions.OptionType.INTEGER)
async def purge(ctx: interactions.SlashContext, amount: int):
    if not ctx.author.permissions.manage_messages:
        return await ctx.send("❌ You don't have permission to manage messages.")
    await ctx.channel.purge(amount)
    await ctx.send(f"🧹 Deleted {amount} messages")

# /calc
@interactions.slash_command(name="calc", description="Solve a math expression")
@interactions.slash_option(name="expression", description="Math expression", required=True, opt_type=interactions.OptionType.STRING)
async def calc(ctx: interactions.SlashContext, expression: str):
    try:
        result = eval(expression)
        await ctx.send(f"🧮 Result: `{result}`")
    except Exception as e:
        await ctx.send(f"❌ Error: {e}")

# /ask
@interactions.slash_command(name="ask", description="Ask ChatGPT something")
@interactions.slash_option(name="prompt", description="Your question", required=True, opt_type=interactions.OptionType.STRING)
async def ask(ctx: interactions.SlashContext, prompt: str):
    await ctx.defer()
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        answer = response.choices[0].message.content
        await ctx.send(answer[:2000])
    except Exception as e:
        await ctx.send(f"❌ OpenAI error: {e}")

# Start
bot.start()
