import os
import requests
import interactions
from interactions import Option, OptionType

bot = interactions.Client(token=os.getenv("DISCORD_TOKEN"))

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PASTEBIN_API_KEY = os.getenv("PASTEBIN_API_KEY")

HEADERS = {
    "Authorization": f"Bearer {OPENAI_API_KEY}",
    "Content-Type": "application/json",
}

def pastebin_post(content: str, title="Paste") -> str:
    data = {
        "api_dev_key": PASTEBIN_API_KEY,
        "api_option": "paste",
        "api_paste_code": content,
        "api_paste_name": title,
        "api_paste_expire_date": "1W",
    }
    response = requests.post("https://pastebin.com/api/api_post.php", data=data)
    if response.ok:
        return response.text  # URL of paste
    else:
        return None

@bot.command(
    name="ask",
    description="Ask LLaMA a question",
    options=[
        Option(
            name="question",
            description="Your question to LLaMA",
            type=OptionType.STRING,
            required=True,
        )
    ],
)
async def ask(ctx: interactions.CommandContext, question: str):
    await ctx.defer()
    # Dummy LLaMA API call (replace with your actual LLaMA call)
    # For demo: just echo question reversed
    response_text = question[::-1]

    # If too long, upload to pastebin
    if len(response_text) > 1900 and PASTEBIN_API_KEY:
        paste_url = pastebin_post(response_text, title="LLaMA Response")
        if paste_url:
            await ctx.send(f"Response too long, posted to Pastebin: {paste_url}")
            return

    await ctx.send(response_text)

@bot.command(
    name="image",
    description="Generate an image with DALL·E",
    options=[
        Option(
            name="prompt",
            description="Prompt for image generation",
            type=OptionType.STRING,
            required=True,
        )
    ],
)
async def image(ctx: interactions.CommandContext, prompt: str):
    await ctx.defer()
    json_data = {
        "model": "dall-e-3",
        "prompt": prompt,
        "n": 1,
        "size": "1024x1024",
    }
    try:
        response = requests.post(
            "https://api.openai.com/v1/images/generations",
            headers=HEADERS,
            json=json_data,
        )
        response.raise_for_status()
        data = response.json()
        image_url = data["data"][0]["url"]
        await ctx.send(image_url)
    except Exception as e:
        await ctx.send(f"Error generating image: {e}")

if __name__ == "__main__":
    bot.start()
