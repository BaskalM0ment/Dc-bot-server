import os
import interactions
import requests

bot = interactions.Client(token=os.getenv("DISCORD_TOKEN"))
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PASTEBIN_DEV_KEY = os.getenv("PASTEBIN_DEV_KEY")

async def paste_to_pastebin(text: str) -> str | None:
    url = "https://pastebin.com/api/api_post.php"
    data = {
        "api_dev_key": PASTEBIN_DEV_KEY,
        "api_option": "paste",
        "api_paste_code": text,
        "api_paste_private": "1",  # unlisted
        "api_paste_expire_date": "1W",  # 1 week expiry
    }
    try:
        resp = requests.post(url, data=data, timeout=10)
        resp.raise_for_status()
        if resp.text.startswith("http"):
            return resp.text
    except Exception as e:
        print(f"Pastebin upload failed: {e}")
    return None

@bot.command(
    name="ask",
    description="Ask LLaMA a question",
    options=[
        interactions.Option(
            name="question",
            description="Your question to LLaMA",
            type=interactions.OptionType.STRING,
            required=True,
        ),
    ],
)
async def ask(ctx: interactions.CommandContext, question: str):
    await ctx.defer()

    # OpenAI Chat Completion request (adjust model if needed)
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": question}],
    }

    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=15,
        )
        response.raise_for_status()
        data = response.json()
        answer = data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        await ctx.send(f"Error generating answer: {e}")
        return

    if len(answer) > 1900:
        paste_url = await paste_to_pastebin(answer)
        if paste_url:
            await ctx.send(f"Answer is too long. See full response here: {paste_url}")
        else:
            await ctx.send("Answer too long, and failed to upload to Pastebin.")
    else:
        await ctx.send(answer)

@bot.command(
    name="image",
    description="Generate an image from a prompt",
    options=[
        interactions.Option(
            name="prompt",
            description="Describe the image you want to generate",
            type=interactions.OptionType.STRING,
            required=True,
        ),
    ],
)
async def image(ctx: interactions.CommandContext, prompt: str):
    await ctx.defer()

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "prompt": prompt,
        "n": 1,
        "size": "1024x1024",
    }

    try:
        response = requests.post(
            "https://api.openai.com/v1/images/generations",
            headers=headers,
            json=payload,
            timeout=20,
        )
        response.raise_for_status()
        data = response.json()
        image_url = data["data"][0]["url"]
        await ctx.send(image_url)
    except Exception as e:
        await ctx.send(f"Error generating image: {e}")

bot.start()
