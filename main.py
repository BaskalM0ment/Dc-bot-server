import interactions
import os
import random

# Load bot using environment token
bot = interactions.Client(token=os.getenv("DISCORD_TOKEN"))

# /ping
@bot.slash_command(
    name="ping",
    description="Test if the bot is responsive"
)
async def ping(ctx):
    await ctx.send("🏓 Pong!")


# /kick
@bot.slash_command(
    name="kick",
    description="Kick a member from the server"
)
@interactions.option()
@interactions.option()
async def kick(ctx, user: interactions.Member, reason: str = "No reason provided"):
    if ctx.author.permissions.kick_members:
        await user.kick(reason=reason)
        await ctx.send(f"👢 {user.username} was kicked. Reason: {reason}")
    else:
        await ctx.send("🚫 You don't have permission.")


# /ban
@bot.slash_command(
    name="ban",
    description="Ban a member from the server"
)
@interactions.option()
@interactions.option()
async def ban(ctx, user: interactions.Member, reason: str = "No reason provided"):
    if ctx.author.permissions.ban_members:
        await user.ban(reason=reason)
        await ctx.send(f"🔨 {user.username} was banned. Reason: {reason}")
    else:
        await ctx.send("🚫 You don't have permission.")


# /purge
@bot.slash_command(
    name="purge",
    description="Delete a number of messages from the channel"
)
@interactions.option()
async def purge(ctx, amount: int):
    if ctx.author.permissions.manage_messages:
        await ctx.channel.purge(amount)
        await ctx.send(f"🧹 Deleted {amount} messages.")
    else:
        await ctx.send("🚫 You don't have permission.")


# /ask
@bot.slash_command(
    name="ask",
    description="Ask the bot a question"
)
@interactions.option()
async def ask(ctx, question: str):
    responses = [
        "That's a great question!",
        "Let me think... 🤔",
        "I'd say... maybe?",
        "Could be! Or maybe not.",
        "I'm a bot, not a psychic 😅",
        "42."
    ]
    await ctx.send(random.choice(responses))


# /calc
@bot.slash_command(
    name="calc",
    description="Calculate a math expression"
)
@interactions.option()
async def calc(ctx, expression: str):
    try:
        result = eval(expression)
        await ctx.send(f"🧮 `{expression}` = `{result}`")
    except Exception as e:
        await ctx.send(f"❌ Error: {e}")


# Start the bot
bot.start()
