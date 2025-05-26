import os
import time
import requests
import interactions
import asyncio

# Load environment variables
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PASTEBIN_API_KEY = os.getenv("PASTEBIN_API_KEY")

# Initialize bot
bot = interactions.Client(token=DISCORD_TOKEN)

# Cooldown settings
user_cooldowns = {}
COOLDOWN_SECONDS = 0  # Set to 0 to disable

# Pastebin upload function
def paste_to_pastebin(text: str, question: str = "Answer") -> str:
    paste_data = {
        'api_dev_key': PASTEBIN_API_KEY,
        'api_option': 'paste',
        'api_paste_code': text,
        'api_paste_name': f"Response to: {question[:50]}",
        'api_paste_expire_date': '1D',
        'api_paste_private': '1'
    }
    response = requests.post("https://pastebin.com/api/api_post.php", data=paste_data)
    if response.status_code == 200 and response.text.startswith("http"):
        return response.text
    return f"Pastebin upload failed. Response: {response.text}"

# /ask command
@interactions.slash_command(name="ask", description="Ask LLaMA a question")
@interactions.slash_option(
    name="question",
    description="Your question to LLaMA",
    required=True,
    opt_type=interactions.OptionType.STRING
)
async def ask(ctx: interactions.SlashContext, question: str):
    user_id = ctx.author.id
    now = time.time()
    if now - user_cooldowns.get(user_id, 0) < COOLDOWN_SECONDS:
        await ctx.send(
            f"⏳ Wait {int(COOLDOWN_SECONDS - (now - user_cooldowns[user_id]))}s.",
            ephemeral=True
        )
        return

    user_cooldowns[user_id] = now
    await ctx.defer()

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY.strip()}",
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
        resp = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        answer = resp.json()["choices"][0]["message"]["content"]

        if len(answer) < 1900:
            await ctx.send(answer)
        else:
            paste_url = paste_to_pastebin(answer, question)
            await ctx.send(f"📄 Response too long: {paste_url}")
    except Exception as e:
        await ctx.send(f"❌ Error: {e}", ephemeral=True)

# /image command
@interactions.slash_command(name="image", description="Generate an image with DALL·E")
@interactions.slash_option(
    name="prompt",
    description="Describe the image you want",
    required=True,
    opt_type=interactions.OptionType.STRING
)
async def image(ctx: interactions.SlashContext, prompt: str):
    await ctx.defer()

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY.strip()}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "dall-e-3",
        "prompt": prompt,
        "n": 1,
        "size": "1024x1024"
    }

    try:
        resp = requests.post("https://api.openai.com/v1/images/generations", headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        image_url = resp.json()["data"][0]["url"]
        await ctx.send(image_url)
    except Exception as e:
        await ctx.send(f"Error generating image: {e}", ephemeral=True)

# Main async runner to sync commands and start bot
async def main():
    await bot.sync_commands(delete=True)  # Remove outdated commands
    await bot.start()

if __name__ == "__main__":
    asyncio.run(main())
