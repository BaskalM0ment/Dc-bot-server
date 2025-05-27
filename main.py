import os
import time
import requests
import asyncio
import interactions

# Environment variables
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "").strip()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
PASTEBIN_API_KEY = os.getenv("PASTEBIN_API_KEY", "").strip()
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN", "").strip()
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

# /image command using Replicate's SDXL
@interactions.slash_command(
    name="image",
    description="Generate an image using Stable Diffusion XL (SDXL)"
)
@interactions.slash_option(
    name="prompt",
    description="Describe the image you want",
    required=True,
    opt_type=interactions.OptionType.STRING
)
async def image(ctx: interactions.SlashContext, prompt: str):
    await ctx.defer()

    if not REPLICATE_API_TOKEN:
        await ctx.send("❌ Replicate API token is not set in environment variables.", ephemeral=True)
        return

    headers = {
        "Authorization": f"Token {REPLICATE_API_TOKEN}",
        "Content-Type": "application/json"
    }

    json_data = {
        "version": "7762fd07-0c67-48c0-b7ed-6d04409f8e05",
        "input": {
            "prompt": prompt
        }
    }

    try:
        response = requests.post("https://api.replicate.com/v1/predictions", headers=headers, json=json_data)
        response.raise_for_status()
        prediction = response.json()

        # Poll until the prediction completes
        prediction_url = prediction["urls"]["get"]
        status = prediction["status"]

        while status not in ["succeeded", "failed"]:
            await asyncio.sleep(1)
            poll_response = requests.get(prediction_url, headers=headers)
            poll_response.raise_for_status()
            prediction = poll_response.json()
            status = prediction["status"]

        if status == "succeeded":
            image_url = prediction["output"][-1]
            img_data = requests.get(image_url).content
            file = interactions.File(img_data, file_name="image.png")
            await ctx.send(files=file)
        else:
            await ctx.send("❌ Image generation failed.", ephemeral=True)

    except Exception as e:
        await ctx.send(f"❌ Error generating image: {e}", ephemeral=True)

# Fix event loop and run bot
if __name__ == "__main__":
    try:
        import nest_asyncio
        nest_asyncio.apply()
    except ImportError:
        pass

async def run_bot():
    await bot.astart(DISCORD_TOKEN)

asyncio.run(run_bot())
