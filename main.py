import interactions
import os
import requests

# Load API keys from environment variables
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
PASTEBIN_API_KEY = os.getenv("PASTEBIN_API_KEY")

# Define Discord intents
intents = (
    interactions.Intents.GUILDS
    | interactions.Intents.GUILD_MESSAGES
)

# Initialize the bot client with your Discord token and intents
bot = interactions.Client(token=os.getenv("DISCORD_TOKEN"), intents=intents)

# ====== /ask (LLaMA via OpenRouter) ======
@interactions.slash_command(name="ask", description="Ask LLaMA a question")
@interactions.AutoDefer()
@interactions.slash_option(
    name="question",
    description="Your question for the AI",
    opt_type=interactions.OptionType.STRING,
    required=True,
)
async def ask(ctx: interactions.SlashContext, question: str):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "meta-llama/llama-3-8b-instruct",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant. Respond with full detail, include code or explanation as needed."},
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
            timeout=60,
        )
        data = response.json()
        answer = data["choices"][0]["message"]["content"]

        if len(answer) < 1900:
            await ctx.send(answer)
        else:
            # Upload to Pastebin for long answers
            pastebin_data = {
                'api_dev_key': PASTEBIN_API_KEY,
                'api_option': 'paste',
                'api_paste_code': answer,
                'api_paste_name': f"Response to: {question[:50]}",
                'api_paste_expire_date': '1D',
                'api_paste_private': '1'
            }
            paste_response = requests.post("https://pastebin.com/api/api_post.php", data=pastebin_data)
            paste_url = paste_response.text

            await ctx.send(f"📄 The response is too long. View it here: {paste_url}")

    except Exception as e:
        await ctx.send(f"OpenRouter error: {e}", ephemeral=True)

# ====== Start Bot ======
if __name__ == "__main__":
    bot.start()
