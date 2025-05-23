import os
import requests
import interactions
from interactions.ext.get_options import Option, OptionType

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PASTEBIN_API_KEY = os.getenv("PASTEBIN_API_KEY")

bot = interactions.Client(token=DISCORD_TOKEN)


async def upload_to_pastebin(content: str) -> str:
    paste_data = {
        "api_dev_key": PASTEBIN_API_KEY,
        "api_option": "paste",
        "api_paste_code": content,
        "api_paste_expire_date": "1W",
    }
    response = requests.post("https://pastebin.com/api/api_post.php", data=paste_data)
    if response.status_code == 200:
        return response.text  # URL of the paste
    else:
        return "Failed to upload to Pastebin."


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
    await ctx.defer()  # Defer response (acknowledge command)

    # Call LLaMA or OpenAI here (example with OpenAI chat completions)
    # Replace with your LLaMA/OpenRouter call if needed
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }
    data = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": question}],
        "max_tokens": 500,
    }
    try:
        resp = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)
        resp.raise_for_status()
        result = resp.json()
        answer = result["choices"][0]["message"]["content"].strip()
    except Exception as e:
        await ctx.send(f"Error contacting LLaMA/OpenAI API: {e}")
        return

    # If answer is too long, upload to pastebin
    if len(answer) > 1500:
        paste_url = upload_to_pastebin(answer)
        await ctx.send(f"Answer too long, posted here: {paste_url}")
    else:
        await ctx.send(answer)


@bot.command(
    name="image",
    description="Generate an image from a prompt",
    options=[
        Option(
            name="prompt",
            description="The prompt for image generation",
            type=OptionType.STRING,
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
    data = {
        "prompt": prompt,
        "n": 1,
        "size": "1024x1024",
    }
    try:
        resp = requests.post("https://api.openai.com/v1/images/generations", headers=headers, json=data)
        resp.raise_for_status()
        result = resp.json()
        image_url = result["data"][0]["url"]
        await ctx.send(image_url)
    except Exception as e:
        await ctx.send(f"Error generating image: {e}")


if __name__ == "__main__":
    bot.start()
