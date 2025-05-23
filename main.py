import os
import aiohttp
import interactions
from interactions import slash_command, slash_option, OptionType, auto_defer

bot = interactions.Client(token=os.getenv("DISCORD_BOT_TOKEN"))

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PASTEBIN_API_KEY = os.getenv("PASTEBIN_API_KEY")

HEADERS_OPENAI = {
    "Authorization": f"Bearer {OPENAI_API_KEY}",
    "Content-Type": "application/json",
}

HEADERS_PASTEBIN = {
    "Content-Type": "application/json",
    "X-API-Key": PASTEBIN_API_KEY,
}

async def upload_to_pastebin(text: str) -> str:
    url = "https://pastebin.com/api/api_post.php"
    data = {
        "api_dev_key": PASTEBIN_API_KEY,
        "api_option": "paste",
        "api_paste_code": text,
        "api_paste_private": "1",
        "api_paste_expire_date": "1D",
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=data) as resp:
            if resp.status == 200:
                return await resp.text()
            else:
                return "Failed to upload to Pastebin."

@slash_command(name="ask", description="Ask LLaMA a question")
@slash_option(
    name="question",
    description="Your question to LLaMA",
    required=True,
    opt_type=OptionType.STRING,
)
@auto_defer()
async def ask(ctx: interactions.SlashContext, question: str):
    ai_response = f"Simulated AI response to your question:\n{question}\n" + ("More text. " * 100)
    if len(ai_response) > 1500 and PASTEBIN_API_KEY:
        paste_link = await upload_to_pastebin(ai_response)
        await ctx.send(f"Response too long, uploaded to Pastebin: {paste_link}")
    else:
        await ctx.send(ai_response)

@slash_command(name="image", description="Generate an AI image from prompt")
@slash_option(
    name="prompt",
    description="Image prompt",
    required=True,
    opt_type=OptionType.STRING,
)
@auto_defer()
async def image(ctx: interactions.SlashContext, prompt: str):
    data = {
        "model": "dall-e-3",
        "prompt": prompt,
        "n": 1,
        "size": "1024x1024"
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://api.openai.com/v1/images/generations",
            headers=HEADERS_OPENAI,
            json=data
        ) as resp:
            if resp.status == 200:
                res_json = await resp.json()
                image_url = res_json["data"][0]["url"]
                await ctx.send(image_url)
            else:
                error_text = await resp.text()
                await ctx.send(f"Error generating image: {resp.status} {error_text}")

bot.start()
