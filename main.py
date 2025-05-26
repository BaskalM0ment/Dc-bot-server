import os
import time
import requests
import asyncio
import interactions

# Environment variables
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "").strip()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
PASTEBIN_API_KEY = os.getenv("PASTEBIN_API_KEY", "").strip()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", "").strip()

bot = interactions.Client(token=DISCORD_TOKEN)

# Cooldown settings
user_cooldowns = {}
COOLDOWN_SECONDS = 0  # Set to > 0 to enable cooldown

# /ask command
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
        answer = response.json()["choices"][0]["message"]["content"]

        if len(answer) < 1900:
            await ctx.send(answer)
        else:
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
                await ctx.send(f"📄 Response too long. View it here: {paste_url}")
            else:
                await ctx.send(f"❌ Pastebin upload failed: {paste_url}", ephemeral=True)

    except Exception as e:
        await ctx.send(f"❌ Error: {e}", ephemeral=True)

# /image command
@interactions.slash_command(
    name="image",
    description="Generate an image using DALL·E"
)
@interactions.slash_option(
    name="prompt",
    description="Describe the image you want",
    required=True,
    opt_type=interactions.OptionType.STRING
)
async def image(ctx: interactions.SlashContext, prompt: str):
    await ctx.defer()

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }

    json_data = {
        "model": "dall-e-3",
        "prompt": prompt,
        "n": 1,
        "size": "1024x1024",
    }

    try:
        response = requests.post(
            "https://api.openai.com/v1/images/generations",
            headers=headers,
            json=json_data
        )
        response.raise_for_status()
        image_url = response.json()["data"][0]["url"]
        await ctx.send(image_url)
    except Exception as e:
        await ctx.send(f"❌ Error generating image: {e}", ephemeral=True)

# Fix event loop and run bot
if __name__ == "__main__":
    try:
        import nest_asyncio
        nest_asyncio.apply()
    except ImportError:
        pass

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(bot.start())
