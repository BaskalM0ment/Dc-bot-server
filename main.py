import os
import requests
import interactions

# Load tokens from environment variables
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PASTEBIN_API_KEY = os.getenv("PASTEBIN_API_KEY")

bot = interactions.Client(token=DISCORD_TOKEN)

# Helper: Upload long responses to Pastebin
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

@bot.command(
    name="image",
    description="Generate an image with DALL·E",
    options=[
        interactions.Option(
            name="prompt",
            description="Image description",
            type=interactions.OptionType.STRING,
            required=True,
        )
    ],
)
async def image(ctx: interactions.CommandContext, prompt: str):
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
    bot.start()
