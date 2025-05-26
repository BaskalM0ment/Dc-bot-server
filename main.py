import os
import time
import requests
import interactions

# Load and sanitize environment variables
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "").strip()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
PASTEBIN_API_KEY = os.getenv("PASTEBIN_API_KEY", "").strip()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", "").strip()

# Initialize bot
bot = interactions.Client(token=DISCORD_TOKEN)

# Cooldown tracking
user_cooldowns = {}
COOLDOWN_SECONDS = 0  # Set to 0 to disable cooldown

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
        await ctx.send("⏳ Cooldown active.", ephemeral=True)
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
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
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
            if paste_response.status_code == 200 and paste_response.text.startswith("http"):
                await ctx.send(f"📄 Response too long: {paste_response.text}")
            else:
                await ctx.send(f"❌ Pastebin upload failed: {paste_response.text}", ephemeral=True)

    except Exception as e:
        await ctx.send(f"❌ Error: {e}", ephemeral=True)

@interactions.slash_command(name="image", description="Generate an image using DALL·E")
@interactions.slash_option(
    name="prompt",
    description="Image prompt",
    required=True,
    opt_type=interactions.OptionType.STRING
)
async def image(ctx: interactions.SlashContext, prompt: str):
    await ctx.defer()
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": "dall-e-3",
        "prompt": prompt,
        "n": 1,
        "size": "1024x1024",
    }

    try:
        response = requests.post("https://api.openai.com/v1/images/generations", headers=headers, json=payload)
        response.raise_for_status()
        image_url = response.json()["data"][0]["url"]
        await ctx.send(image_url)
    except Exception as e:
        await ctx.send(f"Error generating image: {e}", ephemeral=True)

# Start the bot
bot.start()
