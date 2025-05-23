import os
import requests
import interactions
import time

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
PASTEBIN_API_KEY = os.getenv("PASTEBIN_API_KEY")

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
async def ask(ctx: interactions.SlashContext, question: str):
    user_id = ctx.author.id
    now = time.time()
    last_used = user_cooldowns.get(user_id, 0)
    if now - last_used < COOLDOWN_SECONDS:
        await ctx.send(f"⏳ Please wait {int(COOLDOWN_SECONDS - (now - last_used))}s before asking again.", ephemeral=True)
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
        data = response.json()
        answer = data["choices"][0]["message"]["content"]

        if len(answer) <= 1900:
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
            await ctx.send(f"📄 Response too long, view it here: {paste_url}")
    except Exception as e:
        await ctx.send(f"❌ Error: {e}", ephemeral=True)


@interactions.slash_command(name="imagine", description="Generate an AI image")
@interactions.slash_option(
    name="prompt",
    description="Describe the image you want to generate",
    opt_type=interactions.OptionType.STRING,
    required=True
)
async def imagine(ctx: interactions.SlashContext, prompt: str):
    await ctx.defer()

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "openai/dall-e-3",
        "prompt": prompt,
        "size": "1024x1024",
        "n": 1
    }

    try:
        response = requests.post("https://openrouter.ai/api/v1/images/generations", headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        image_url = data['data'][0]['url']
        await ctx.send(f"🖼️ Here's your image: {image_url}")
    except Exception as e:
        await ctx.send(f"❌ Error generating image: {e}", ephemeral=True)


if __name__ == "__main__":
    bot.start()
