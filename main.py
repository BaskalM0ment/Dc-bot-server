import interactions
import openai
import os

# Set OpenAI API key from environment variable
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Define Discord intents
intents = (
    interactions.Intents.GUILDS
    | interactions.Intents.GUILD_MESSAGES
    | interactions.Intents.GUILD_MEMBERS
)

bot = interactions.Client(token=os.getenv("DISCORD_TOKEN"), intents=intents)

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
        response = client.chat.completions.create(
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

if __name__ == "__main__":
    bot.start()
