import interactions
import os
import aiohttp

TOKEN = os.getenv("DISCORD_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PASTEBIN_API_KEY = os.getenv("PASTEBIN_API_KEY")

bot = interactions.Client(token=TOKEN)

@interactions.slash_command(name="ask", description="Ask LLaMA a question")
@interactions.option("question", str, description="Your question to LLaMA", required=True)
@interactions.autodefer()
async def ask(ctx: interactions.SlashContext, question: str):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "meta-llama/llama-3-70b-instruct",
        "messages": [{"role": "user", "content": question}],
        "temperature": 0.7
    }
    async with aiohttp.ClientSession() as session:
        async with session.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data) as resp:
            if resp.status != 200:
                return await ctx.send(f"Error from OpenRouter: {resp.status}")
            response = await resp.json()
            message = response["choices"][0]["message"]["content"]
    
    if len(message) > 2000 and PASTEBIN_API_KEY:
        paste_data = {
            "api_dev_key": PASTEBIN_API_KEY,
            "api_option": "paste",
            "api_paste_code": question[:50],
            "api_paste_private": "1",
            "api_paste_expire_date": "10M",
            "api_paste_format": "text",
            "api_paste_code": message,
        }
        async with aiohttp.ClientSession() as session:
            async with session.post("https://pastebin.com/api/api_post.php", data=paste_data) as paste_resp:
                paste_link = await paste_resp.text()
                return await ctx.send(f"Response too long. View it here: {paste_link}")
    await ctx.send(message)

@interactions.slash_command(name="imagine", description="Generate an AI image from a prompt")
@interactions.option("prompt", str, description="Describe the image", required=True)
@interactions.autodefer()
async def imagine(ctx: interactions.SlashContext, prompt: str):
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "prompt": prompt,
        "n": 1,
        "size": "1024x1024"
    }
    async with aiohttp.ClientSession() as session:
        async with session.post("https://api.openai.com/v1/images/generations", headers=headers, json=data) as resp:
            if resp.status != 200:
                error_details = await resp.text()
                return await ctx.send(f"Error generating image: {resp.status}\n```{error_details}```")
            response = await resp.json()
            image_url = response["data"][0]["url"]
            await ctx.send(image_url)

bot.start()
