import interactions
import os
import requests

# Load API keys from environment
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
PASTEBIN_API_KEY = os.getenv("PASTEBIN_API_KEY")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

# Initialize bot
bot = interactions.Client(token=DISCORD_TOKEN)


@interactions.slash_command(name="ask", description="Ask LLaMA a question")
@interactions.slash_option(
    name="question",
    description="Your question to the AI",
    opt_type=interactions.OptionType.STRING,
    required=True
)
@interactions.AutoDefer()
async def ask(ctx: interactions.SlashContext, question: str):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": "meta-llama/llama-3-8b-instruct",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": question}
        ],
        "max_tokens": 2048,
        "temperature": 0.7,
    }

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=60,
        )
        response.raise_for_status()
        data = response.json()
        answer = data["choices"][0]["message"]["content"]

        if len(answer) < 1900:
            await ctx.send(answer)
        else:
            # Upload to Pastebin
            paste_data = {
                'api_dev_key': PASTEBIN_API_KEY,
                'api_option': 'paste',
                'api_paste_code': answer,
                'api_paste_name': f"Response to: {question[:50]}",
                'api_paste_expire_date': '1D',
                'api_paste_private': '1'
            }
            paste_response = requests.post("https://pastebin.com/api/api_post.php", data=paste_data)
            paste_url = paste_response.text

            if paste_url.startswith("http"):
                await ctx.send(f"📄 Response too long, view it here: {paste_url}")
            else:
                await ctx.send(f"⚠️ Pastebin error: {paste_url}", ephemeral=True)

    except Exception as e:
        await ctx.send(f"❌ Error: {e}", ephemeral=True)


# Slash command to clear all old registered commands
@interactions.slash_command(name="clear", description="Clear all old slash commands (admin only)")
@interactions.AutoDefer()
async def clear(ctx: interactions.SlashContext):
    await bot.sync_commands(delete_commands=True)
    await ctx.send("✅ Old slash commands cleared.")


# Start the bot
if __name__ == "__main__":
    bot.start()
