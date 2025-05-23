import os
import requests
import interactions

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PASTEBIN_API_KEY = os.getenv("PASTEBIN_API_KEY")  # You need to get your own Pastebin API key

if not DISCORD_TOKEN or not OPENAI_API_KEY or not PASTEBIN_API_KEY:
    raise RuntimeError("DISCORD_TOKEN, OPENAI_API_KEY and PASTEBIN_API_KEY must be set as environment variables")

bot = interactions.Client(token=DISCORD_TOKEN)

MAX_MESSAGE_LENGTH = 1900  # Discord max message length is 2000, keep margin

def upload_to_pastebin(content: str) -> str:
    data = {
        "api_dev_key": PASTEBIN_API_KEY,
        "api_option": "paste",
        "api_paste_code": content,
        "api_paste_expire_date": "1D",  # expires in 1 day
        "api_paste_private": "1",  # unlisted paste
        "api_paste_name": "LLaMA AI Response",
    }
    response = requests.post("https://pastebin.com/api/api_post.php", data=data)
    if response.status_code == 200 and response.text.startswith("http"):
        return response.text
    else:
        raise Exception(f"Pastebin upload failed: {response.text}")

@bot.command(
    name="ask",
    description="Ask LLaMA a question",
    options=[
        interactions.Option(
            name="question",
            description="Your question to LLaMA",
            type=interactions.OptionType.STRING,
            required=True,
        )
    ],
)
async def ask(ctx: interactions.CommandContext, question: str):
    await ctx.defer()

    # TODO: Replace with your actual LLaMA/OpenAI call
    # For demo, just echo the question * 10 to simulate a long response
    answer = (f"You asked: {question}. " * 20).strip()

    if len(answer) > MAX_MESSAGE_LENGTH:
        try:
            paste_url = upload_to_pastebin(answer)
            await ctx.send(f"Response was too long, here is a Pastebin link: {paste_url}")
        except Exception as e:
            await ctx.send(f"Failed to upload to Pastebin, here is the answer truncated:\n{answer[:MAX_MESSAGE_LENGTH]}")
    else:
        await ctx.send(answer)


@bot.command(
    name="image",
    description="Generate an image with DALL·E",
    options=[
        interactions.Option(
            name="prompt",
            description="Image prompt",
            type=interactions.OptionType.STRING,
            required=True,
        )
    ],
)
async def image(ctx: interactions.CommandContext, prompt: str):
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
        response = requests.post("https://api.openai.com/v1/images/generations", headers=headers, json=json_data)
        response.raise_for_status()
        data = response.json()
        image_url = data["data"][0]["url"]
        await ctx.send(image_url)
    except Exception as e:
        await ctx.send(f"Error generating image: {e}")


if __name__ == "__main__":
    bot.start()
