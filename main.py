import os
import requests
import interactions
import traceback
import sys
import logging

# Setup logging to stdout for Railway logs
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

# Get env vars - make sure you set these!
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
PASTEBIN_API_KEY = os.getenv("PASTEBIN_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # For DALL·E image generation

if not DISCORD_TOKEN or not OPENROUTER_API_KEY or not OPENAI_API_KEY or not PASTEBIN_API_KEY:
    print("ERROR: Missing one or more required environment variables.")
    sys.exit(1)

bot = interactions.Client(token=DISCORD_TOKEN)


@bot.event
async def on_ready():
    print(f"Bot logged in as {bot.me}")


@interactions.slash_command(
    name="ask",
    description="Ask LLaMA a question"
)
async def ask(ctx: interactions.SlashContext, question: str):
    await ctx.defer()  # Acknowledge command immediately to avoid timeout

    try:
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
            # Upload long answer to Pastebin
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
        print("Error in /ask command:", e)
        traceback.print_exc()
        await ctx.send(f"Error: {e}", ephemeral=True)


@interactions.slash_command(
    name="imagine",
    description="Generate an AI image from a prompt using DALL·E"
)
async def imagine(ctx: interactions.SlashContext, prompt: str):
    await ctx.defer()

    try:
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": "dall-e-3",
            "prompt": prompt,
            "n": 1,
            "size": "1024x1024"
        }
        response = requests.post(
            "https://api.openai.com/v1/images/generations",
            headers=headers,
            json=payload,
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        image_url = data["data"][0]["url"]
        await ctx.send(image_url)
    except Exception as e:
        print("Error in /imagine command:", e)
        traceback.print_exc()
        await ctx.send(f"Error generating image: {e}", ephemeral=True)


if __name__ == "__main__":
    try:
        bot.start()
    except Exception:
        print("Bot crashed on startup!")
        traceback.print_exc()
