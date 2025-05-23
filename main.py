import os
import requests
import interactions
from interactions import OptionType
from interactions.ext.paginators import Paginator

# Load tokens from env vars
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PASTEBIN_API_KEY = os.getenv("PASTEBIN_API_KEY")

bot = interactions.Client()

# Helper: paste long text to Pastebin and return URL
def paste_to_pastebin(text: str) -> str:
    url = "https://pastebin.com/api/api_post.php"
    data = {
        "api_dev_key": PASTEBIN_API_KEY,
        "api_option": "paste",
        "api_paste_code": text,
        "api_paste_expire_date": "10M",
        "api_paste_format": "text",
    }
    response = requests.post(url, data=data)
    if response.status_code == 200:
        return response.text
    else:
        return "Failed to upload to Pastebin."

@interactions.slash_command(name="ask", description="Ask LLaMA a question")
@interactions.slash_option(
    name="question",
    description="Your question to LLaMA",
    opt_type=OptionType.STRING,
    required=True,
)
async def ask(ctx: interactions.SlashContext, question: str):
    await ctx.defer()
    try:
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json",
        }
        json_data = {
            "model": "llama-2-13b-chat",
            "messages": [{"role": "user", "content": question}],
            "max_tokens": 500,
        }
        resp = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=json_data)
        resp.raise_for_status()
        answer = resp.json()["choices"][0]["message"]["content"]

        if len(answer) > 1900:
            paste_url = paste_to_pastebin(answer)
            await ctx.send(f"Answer too long, posted to Pastebin: {paste_url}")
        else:
            await ctx.send(answer)

    except Exception as e:
        await ctx.send(f"Error: {str(e)}")

@interactions.slash_command(name="image", description="Generate an image with DALL·E")
@interactions.slash_option(
    name="prompt",
    description="Image description",
    opt_type=OptionType.STRING,
    required=True,
)
async def image(ctx: interactions.SlashContext, prompt: str):
    await ctx.defer()
    try:
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
        resp = requests.post("https://api.openai.com/v1/images/generations", headers=headers, json=json_data)
        resp.raise_for_status()
        image_url = resp.json()["data"][0]["url"]
        await ctx.send(image_url)
    except Exception as e:
        await ctx.send(f"Error generating image: {str(e)}")

if __name__ == "__main__":
    bot.start(DISCORD_TOKEN)
