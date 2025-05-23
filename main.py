import os
import asyncio
import requests
import interactions

# Load environment variables from Railway/host environment
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PASTEBIN_API_KEY = os.getenv("PASTEBIN_API_KEY")

bot = interactions.Client(token=DISCORD_TOKEN)

# /ask command: ask LLaMA via OpenRouter
@bot.slash_command(name="ask", description="Ask LLaMA a question")
@interactions.slash_option(
    name="question",
    description="Your question to LLaMA",
    opt_type=interactions.OptionType.STRING,
    required=True,
)
@interactions.AutoDefer()
async def ask(ctx: interactions.SlashContext, question: str):
    print(f"[ask] Question received: {question}")
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
            # If answer too long, upload to Pastebin
            paste_data = {
                'api_dev_key': PASTEBIN_API_KEY,
                'api_option': 'paste',
                'api_paste_code': answer,
                'api_paste_name': f"Response to: {question[:50]}",
                'api_paste_expire_date': '1D',
                'api_paste_private': '1',
            }
            paste_response = requests.post("https://pastebin.com/api/api_post.php", data=paste_data)
            paste_url = paste_response.text
            if paste_url.startswith("http"):
                await ctx.send(f"📄 Response too long, see here: {paste_url}")
            else:
                await ctx.send(f"Failed to upload to Pastebin: {paste_url}", ephemeral=True)
    except Exception as e:
        print(f"[ask] Exception: {e}")
        await ctx.send(f"Error: {e}", ephemeral=True)

# /imagine command: generate image with OpenAI DALL·E
@bot.slash_command(name="imagine", description="Generate an AI image with DALL·E")
@interactions.slash_option(
    name="prompt",
    description="Describe the image you want",
    opt_type=interactions.OptionType.STRING,
    required=True,
)
@interactions.AutoDefer()
async def imagine(ctx: interactions.SlashContext, prompt: str):
    print(f"[imagine] Prompt received: {prompt}")
    try:
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json",
        }
        json_data = {
            "prompt": prompt,
            "n": 1,
            "size": "1024x1024",
        }
        response = requests.post(
            "https://api.openai.com/v1/images/generations",
            headers=headers,
            json=json_data,
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        image_url = data["data"][0]["url"]
        await ctx.send(image_url)
    except Exception as e:
        print(f"[imagine] Exception: {e}")
        await ctx.send(f"Error generating image: {e}", ephemeral=True)

async def main():
    print("Starting bot...")
    await bot.start()
    print("Bot stopped.")

if __name__ == "__main__":
    asyncio.run(main())
