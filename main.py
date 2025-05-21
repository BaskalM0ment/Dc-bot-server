import interactions
import openai
import os

# Set OpenAI API key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

# Define Discord intents needed
intents = (
    interactions.Intents.GUILDS
    | interactions.Intents.GUILD_MESSAGES
    | interactions.Intents.GUILD_MEMBERS
)

# Initialize the bot client with your Discord token and intents
bot = interactions.Client(token=os.getenv("DISCORD_TOKEN"), intents=intents)

# ====== /ping command ======
@interactions.slash_command(name="ping", description="Check bot responsiveness")
async def ping(ctx: interactions.SlashContext):
    await ctx.send("Pong! 🏓")

# ====== /kick command ======
@interactions.slash_command(name="kick", description="Kick a user")
@interactions.slash_option(
    name="user",
    description="User to kick",
    opt_type=interactions.OptionType.USER,
    required=True,
)
async def kick(ctx: interactions.SlashContext, user: interactions.Member):
    if not ctx.member.permissions.kick_members:
        await ctx.send("❌ You don't have permission to kick members.", ephemeral=True)
        return
    try:
        await user.kick()
        await ctx.send(f"👢 {user.user.username} has been kicked.")
    except Exception as e:
        await ctx.send(f"Failed to kick user: {e}", ephemeral=True)

# ====== /ban command ======
@interactions.slash_command(name="ban", description="Ban a user")
@interactions.slash_option(
    name="user",
    description="User to ban",
    opt_type=interactions.OptionType.USER,
    required=True,
)
async def ban(ctx: interactions.SlashContext, user: interactions.Member):
    if not ctx.member.permissions.ban_members:
        await ctx.send("❌ You don't have permission to ban members.", ephemeral=True)
        return
    try:
        await user.ban()
        await ctx.send(f"⛔ {user.user.username} has been banned.")
    except Exception as e:
        await ctx.send(f"Failed to ban user: {e}", ephemeral=True)

# ====== /purge command ======
@interactions.slash_command(name="purge", description="Delete messages in a channel")
@interactions.slash_option(
    name="amount",
    description="Number of messages to delete",
    opt_type=interactions.OptionType.INTEGER,
    required=True,
)
async def purge(ctx: interactions.SlashContext, amount: int):
    if not ctx.member.permissions.manage_messages:
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

# ====== /ask command ======
@interactions.slash_command(name="ask", description="Ask ChatGPT a question")
@interactions.slash_option(
    name="question",
    description="Your question for ChatGPT",
    opt_type=interactions.OptionType.STRING,
    required=True,
)
async def ask(ctx: interactions.SlashContext, question: str):
    await ctx.defer()
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": question},
            ],
            max_tokens=500,
            temperature=0.7,
        )
        answer = response.choices[0].message.content.strip()
        await ctx.send(answer)
    except Exception as e:
        await ctx.send(f"OpenAI error: {e}", ephemeral=True)

# Run the bot
if __name__ == "__main__":
    bot.start()
