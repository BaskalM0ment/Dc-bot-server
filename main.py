import os
import requests
import interactions
import aiohttp

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
PASTEBIN_API_KEY = os.getenv("PASTEBIN_API_KEY")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # For DALL·E image generation

bot = interactions.Client(token=DISCORD_TOKEN)

@interactions.slash_command(
    name="ask",
    description="Ask LLaMA a question"
)
async def ask(
    ctx: interactions.SlashContext, 
    question: interactions.Option(str, "Your question to LLaMA")
):
    await ctx.defer()
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "meta-llama/llama-3-8b-instruct",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": question}
        ],
        "max_tokens": 2048,
        "temperature": 0.7,
    }
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        answer = data["choices"][0]["message"]["content"]

        if len(answer) < 1900:
            await ctx.send(answer)
        else:
            paste_data = {
                'api_dev_key': PASTEBIN_API_KEY,
                'api_option': 'paste',
                'api_paste_code': answer,
                'api_paste_name': f"Response to: {question[:50]}",
                'api_paste_expire_date': '1D',
                'api_paste_private': '1'
            }
            paste_response = requests.post("https://pastebin.com/api/api_post.php", data=paste_data)
            paste_url = paste_response.text
            if paste_url.startswith("http"):
                await ctx.send(f"📄 Response too long, view it here: {paste_url}")
            else:
                await ctx.send(f"Failed to upload to Pastebin: {paste_url}", ephemeral=True)

    except Exception as e:
        await ctx.send(f"Error: {e}", ephemeral=True)

@interactions.slash_command(
    name="imagine",
    description="Generate an AI image using DALL·E"
)
async def imagine(
    ctx: interactions.SlashContext,
    prompt: interactions.Option(str, "Describe the image you want to generate")
):
    await ctx.defer()
    url = "https://api.openai.com/v1/images/generations"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "dall-e-3",
        "prompt": prompt,
        "n": 1,
        "size": "1024x1024"
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as resp:
                if resp.status != 200:
                    text = await resp.text()
                    await ctx.send(f"Error generating image: {resp.status} {text}", ephemeral=True)
                    return
                data = await resp.json()
                image_url = data["data"][0]["url"]
                await ctx.send(image_url)
    except Exception as e:
        await ctx.send(f"Error generating image: {e}", ephemeral=True)

if __name__ == "__main__":
    bot.start()
