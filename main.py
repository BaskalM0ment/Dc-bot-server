import os
import aiohttp
import interactions

# Initialize bot client
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

# Helper: Upload long text to Pastebin (assuming https://pastebin.com/api/api_post.php style)
async def upload_to_pastebin(text: str) -> str:
    # Adjust according to your pastebin provider API
    # Here is a dummy example with https://pastebin.com/api documentation
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
                link = await resp.text()
                return link
            else:
                return "Failed to upload to Pastebin."

# /ask command: send question, get AI response (simulate LLaMA here)
@bot.slash_command(name="ask", description="Ask LLaMA a question")
@interactions.slash_option(
    name="question",
    description="Your question to LLaMA",
    required=True,
    opt_type=interactions.OptionType.STRING,
)
@interactions.auto_defer()
async def ask(ctx: interactions.SlashContext, question: str):
    # Simulate AI response (replace with real API call)
    ai_response = f"Simulated AI response to your question:\n{question}\n" + ("More text. " * 100)

    # If response is too long (>1500 chars), upload to Pastebin
    if len(ai_response) > 1500 and PASTEBIN_API_KEY:
        paste_link = await upload_to_pastebin(ai_response)
        await ctx.send(f"Response too long, uploaded to Pastebin: {paste_link}")
    else:
        await ctx.send(ai_response)

# /image command: generate image using OpenAI DALL·E
@bot.slash_command(name="image", description="Generate an AI image from prompt")
@interactions.slash_option(
    name="prompt",
    description="Image prompt",
    required=True,
    opt_type=interactions.OptionType.STRING,
)
@interactions.auto_defer()
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

# Run the bot
bot.start()
