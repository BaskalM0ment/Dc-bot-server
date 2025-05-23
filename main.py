import os
import requests
import interactions

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PASTEBIN_API_KEY = os.getenv("PASTEBIN_API_KEY")

bot = interactions.Client(token=DISCORD_TOKEN)

@bot.slash_command(name="ask", description="Ask LLaMA a question")
@interactions.slash_option(name="question", description="Your question to LLaMA", opt_type=interactions.OptionType.STRING, required=True)
@interactions.AutoDefer  # <-- NO parentheses here
async def ask(ctx: interactions.SlashContext, question: str):
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
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        answer = response.json()["choices"][0]["message"]["content"]

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
                await ctx.send(f"📄 Response too long. View it here:\n{paste_url}")
            else:
                await ctx.send(f"❌ Failed to upload to Pastebin: {paste_url}", ephemeral=True)

    except Exception as e:
        await ctx.send(f"❌ Error: {e}", ephemeral=True)


@bot.slash_command(name="imagine", description="Generate an image with DALL·E")
@interactions.slash_option(name="prompt", description="Describe the image", opt_type=interactions.OptionType.STRING, required=True)
@interactions.AutoDefer  # <-- NO parentheses here either
async def imagine(ctx: interactions.SlashContext, prompt: str):
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

    try:
        response = requests.post("https://api.openai.com/v1/images/generations", headers=headers, json=payload)
        response.raise_for_status()
        image_url = response.json()["data"][0]["url"]
        await ctx.send(f"🖼️ Image for: `{prompt}`\n{image_url}")
    except Exception as e:
        await ctx.send(f"❌ Error generating image: {e}", ephemeral=True)


if __name__ == "__main__":
    bot.start()
