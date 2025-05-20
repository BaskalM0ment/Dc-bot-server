import interactions
import os
import random

# Load the bot
bot = interactions.Client(token=os.getenv("DISCORD_TOKEN"))

# /ping command
@bot.command(
    name="ping",
    description="Test if the bot is responsive"
)
async def ping(ctx):
    await ctx.send("🏓 Pong!")


# /kick command
@bot.command(
    name="kick",
    description="Kick a member from the server",
    options=[
        interactions.Option(
            name="user",
            description="The user to kick",
            type=interactions.OptionType.USER,
            required=True
        ),
        interactions.Option(
            name="reason",
            description="Reason for the kick",
            type=interactions.OptionType.STRING,
            required=False
        )
    ]
)
async def kick(ctx, user: interactions.Member, reason: str = "No reason provided"):
    if ctx.author.permissions.kick_members:
        await user.kick(reason=reason)
        await ctx.send(f"👢 {user.username} was kicked. Reason: {reason}")
    else:
        await ctx.send("🚫 You don't have permission to use this command.")


# /ban command
@bot.command(
    name="ban",
    description="Ban a member from the server",
    options=[
        interactions.Option(
            name="user",
            description="The user to ban",
            type=interactions.OptionType.USER,
            required=True
        ),
        interactions.Option(
            name="reason",
            description="Reason for the ban",
            type=interactions.OptionType.STRING,
            required=False
        )
    ]
)
async def ban(ctx, user: interactions.Member, reason: str = "No reason provided"):
    if ctx.author.permissions.ban_members:
        await user.ban(reason=reason)
        await ctx.send(f"🔨 {user.username} was banned. Reason: {reason}")
    else:
        await ctx.send("🚫 You don't have permission to use this command.")


# /purge command
@bot.command(
    name="purge",
    description="Delete a number of messages",
    options=[
        interactions.Option(
            name="amount",
            description="Number of messages to delete",
            type=interactions.OptionType.INTEGER,
            required=True
        )
    ]
)
async def purge(ctx, amount: int):
    if ctx.author.permissions.manage_messages:
        await ctx.channel.purge(amount)
        await ctx.send(f"🧹 Deleted {amount} messages.")
    else:
        await ctx.send("🚫 You don't have permission to use this command.")


# /ask command
@bot.command(
    name="ask",
    description="Ask the bot a question",
    options=[
        interactions.Option(
            name="question",
            description="What do you want to ask?",
            type=interactions.OptionType.STRING,
            required=True
        )
    ]
)
async def ask(ctx, question: str):
    replies = [
        "That's a great question!",
        "Let me think... 🤔",
        "I'd say... maybe?",
        "Could be! Or maybe not.",
        "I'm a bot, not a psychic 😅",
        "42."
    ]
    await ctx.send(random.choice(replies))


# /calc command
@bot.command(
    name="calc",
    description="Calculate a math expression",
    options=[
        interactions.Option(
            name="expression",
            description="Math expression (e.g. 2+2*5)",
            type=interactions.OptionType.STRING,
            required=True
        )
    ]
)
async def calc(ctx, expression: str):
    try:
        result = eval(expression)
        await ctx.send(f"🧮 `{expression}` = `{result}`")
    except Exception as e:
        await ctx.send(f"❌ Error: {e}")


# Start the bot
bot.start()
