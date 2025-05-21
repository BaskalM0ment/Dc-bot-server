import os
import interactions
import openai

# Load environment variables
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

# Set up bot with intents
bot = interactions.Client(
    token=DISCORD_TOKEN,
    intents=interactions.Intents.ALL
)

# /ping command
@interactions.slash_command(name="ping", description="Check if the bot is online")
async def ping(ctx: interactions.CommandContext):
    await ctx.send("🏓 Pong!")

# /kick command
@interactions.slash_command(name="kick", description="Kick a user from the server")
@interactions.option()
async def kick(ctx: interactions.CommandContext, user: interactions.Member):
    if not ctx.author.permissions.kick_members:
        return await ctx.send("❌ You don't have permission to kick members.")
    await ctx.guild.kick(user)
    await ctx.send(f"✅ {user.username} has been kicked.")

# /ban command
@interactions.slash_command(name="ban", description="Ban a user from the server")
@interactions.option()
async def ban(ctx: interactions.CommandContext, user: interactions.Member):
    if not ctx.author.permissions.ban_members:
        return await ctx.send("❌ You don't have permission to ban members.")
    await ctx.guild.ban(user)
    await ctx.send(f"✅ {user.username} has been banned.")

# /purge command
@interactions.slash_command(name="purge", description="Delete a number of recent messages")
@interactions.option()
async def purge(ctx: interactions.CommandContext, amount: int):
    if not ctx.author.permissions.manage_messages:
        return await ctx.send("❌ You don't have permission to manage messages.")
    messages = await ctx.channel.history(limit=amount)
    await ctx.channel.purge(messages)
    await ctx.send(f"🧹 Deleted {amount} messages.")

# /calc command for math
@interactions.slash_command(name="calc", description="Calculate a math expression")
@interactions.option()
async def calc(ctx: interactions.CommandContext, expression: str):
    try:
        result = eval(expression)
        await ctx.send(f"🧮 Result: `{result}`")
    except Exception as e:
        await ctx.send(f"❌ Error: {e}")

# /ask command using ChatGPT
@interactions.slash_command(name="ask", description="Ask ChatGPT anything")
@interactions.option()
async def ask(ctx: interactions.CommandContext, prompt: str):
    await ctx.defer()
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # change to "gpt-4" if needed
            messages=[{"role": "user", "content": prompt}]
        )
        answer = response.choices[0].message.content
        await ctx.send(answer[:2000])  # Discord message limit
    except Exception as e:
        await ctx.send(f"❌ OpenAI error: {e}")

# Start bot
bot.start()
