import interactions
import requests
import os

# Environment variables
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PASTEBIN_API_KEY = os.getenv("PASTEBIN_API_KEY")

# Initialize bot
bot = interactions.Client(token=os.getenv("DISCORD_BOT_TOKEN"))

# Ask Command
@interactions.slash_command(name="ask", description="Ask LLaMA a question")
@interactions.slash_option(
    name="question",
    description="Your question for LLaMA",
    opt_type=interactions.OptionType.STRING,
    required=True
)
async def ask(ctx: interactions.SlashContext, question: str):
    await ctx.defer()
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "meta-llama/llama-3-70b-instruct",
        "messages": [
            {"role": "user", "content": question}
        ]
    }
    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", json=data, headers=headers)
        response.raise_for_status()
        reply = response.json()["choices"][0]["message"]["content"]
        if len(reply) > 1800:
            paste_res = requests.post("https://pastebin.com/api/api_post.php", data={
                "api_dev_key": PASTEBIN_API_KEY,
                "api_option": "paste",
                "api_paste_code": "llama_response",
                "api_paste_private": "1",
                "api_paste_expire_date": "10M",
                "api_paste_format": "text",
                "api_paste_code": reply
            })
            await ctx.send(f"📄 Long response posted to Pastebin: {paste_res.text}")
        else:
            await ctx.send(reply)
    except Exception as e:
        await ctx.send(f"❌ Error: {str(e)}")

# Image Command
@interactions.slash_command(name="image", description="Generate an image using AI")
@interactions.slash_option(
    name="prompt",
    description="Description of the image to generate",
    opt_type=interactions.OptionType.STRING,
    required=True
)
async def image(ctx: interactions.SlashContext, prompt: str):
    await ctx.defer()
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "dall-e-3",
        "prompt": prompt,
        "n": 1,
        "size": "1024x1024"
    }
    try:
        response = requests.post("https://api.openai.com/v1/images/generations", json=data, headers=headers)
        response.raise_for_status()
        image_url = response.json()["data"][0]["url"]
        await ctx.send(image_url)
    except Exception as e:
        await ctx.send(f"❌ Error generating image: {str(e)}")

bot.start()
