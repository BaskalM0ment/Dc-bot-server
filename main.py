import os
import interactions
import requests
import time
import base64

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

bot = interactions.Client(token=DISCORD_TOKEN)

user_cooldowns = {}
COOLDOWN_SECONDS = 30

@interactions.slash_command(name="ask", description="Ask LLaMA a question")
@interactions.slash_option(
    name="question",
    description="Your question to LLaMA",
    opt_type=interactions.OptionType.STRING,
    required=True
)
@interactions.AutoDefer()
async def ask(ctx: interactions.SlashContext, question: str):
    user_id = ctx.author.id
    now = time.time()
    if user_id in user_cooldowns and now - user_cooldowns[user_id] < COOLDOWN_SECONDS:
        remaining = int(COOLDOWN_SECONDS - (now - user_cooldowns[user_id]))
        await ctx.send(f"⏳ Please wait {remaining} seconds before asking again.", ephemeral=True)
        return
    user_cooldowns[user_id] = now

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
    }

    try:
        res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload, timeout=30)
        res.raise_for_status()
        content = res.json()["choices"][0]["message"]["content"]
        await ctx.send(content if len(content) < 1900 else "Response too long.")
    except Exception as e:
        await ctx.send(f"Error: {e}", ephemeral=True)

@interactions.slash_command(name="imagine", description="Generate an AI image from a prompt")
@interactions.slash_option(
    name="prompt",
    description="Describe the image to generate",
    opt_type=interactions.OptionType.STRING,
    required=True
)
@interactions.AutoDefer()
async def imagine(ctx: interactions.SlashContext, prompt: str):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "openai/dall-e-3",
        "prompt": prompt,
        "size": "1024x1024",
        "response_format": "b64_json"
    }

    try:
        res = requests.post("https://openrouter.ai/api/v1/images/generations", headers=headers, json=payload)
        res.raise_for_status()
        b64_image = res.json()["data"][0]["b64_json"]
        img_bytes = base64.b64decode(b64_image)
        await ctx.send("Here is your generated image:", file=interactions.File(file=img_bytes, file_name="image.png"))
    except Exception as e:
        await ctx.send(f"Image generation failed: {e}", ephemeral=True)

bot.start()
