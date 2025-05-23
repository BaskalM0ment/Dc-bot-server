import os
import time
import requests
import interactions

# Environment variables
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
PASTEBIN_API_KEY = os.getenv("PASTEBIN_API_KEY")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

# Initialize bot
bot = interactions.Client(token=DISCORD_TOKEN)

# Cooldown settings (set to 0 to disable cooldown)
user_cooldowns = {}
COOLDOWN_SECONDS = 0

# Helper function: Upload long responses to Pastebin
def paste_to_pastebin(text: str) -> str:
    url = "https://pastebin.com/api/api_post.php"
    data = {
        "api_dev_key": PASTEBIN_API_KEY,
        "api_option": "paste",
        "api_paste_code": text,
        "api_paste_expire_date": "10M",
        "api_paste_format": "text",
        "api_paste_private": "1",
    }
    response = requests.post(url, data=data)
    if response.status_code == 200:
        print(f"Pastebin response: {response.text}")  # Debug log
        return response.text
    else:
        print(f"Pastebin failed with status {response.status_code}: {response.text}")  # Debug log
        return "Failed to upload to Pastebin."

# Slash command /ask
@interactions.slash_command(
    name="ask",
    description="Ask LLaMA a question"
)
@interactions.slash_option(
    name="question",
    description="Your question to LLaMA",
    required=True,
    opt_type=interactions.OptionType.STRING
)
async def ask(ctx: interactions.SlashContext, question: str):
    user_id = ctx.author.id
    now = time.time()
    last_used = user_cooldowns.get(user_id, 0)

    if now - last_used < COOLDOWN_SECONDS:
        await ctx.send(
            f"⏳ Please wait {int(COOLDOWN_SECONDS - (now - last_used))} seconds before asking again.",
            ephemeral=True
        )
        return

    user_cooldowns[user_id] = now
    await ctx.defer()

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
            timeout=30
        )
        response.raise_for_status()
        data = response.json()
        answer = data["choices"][0]["message"]["content"]

        if len(answer) < 1900:
            await ctx.send(answer)
        else:
            paste_url = paste_to_pastebin(answer)
            if paste_url.startswith("http"):
                await ctx.send(f"📄 Response too long. View it here: {paste_url}")
            else:
                await ctx.send(f"❌ Pastebin upload failed. Response: {paste_url}", ephemeral=True)

    except Exception as e:
        await ctx.send(f"❌ Error: {e}", ephemeral=True)

if __name__ == "__main__":
    bot.start()
