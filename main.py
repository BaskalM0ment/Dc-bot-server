import interactions
import os
import requests

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
PASTEBIN_API_KEY = os.getenv("PASTEBIN_API_KEY")

MAX_CHARS = 2000

def split_response(text):
    return [text[i:i+MAX_CHARS] for i in range(0, len(text), MAX_CHARS)]

def upload_to_pastebin(content):
    data = {
        "api_dev_key": PASTEBIN_API_KEY,
        "api_option": "paste",
        "api_paste_code": content,
        "api_paste_private": 1,
        "api_paste_expire_date": "1D",
        "api_paste_name": "AI Response"
    }
    response = requests.post("https://pastebin.com/api/api_post.php", data=data)
    if response.status_code == 200:
        return response.text  # URL of paste
    else:
        return None

@interactions.slash_command(name="ask", description="Ask LLaMA (via OpenRouter)")
@interactions.slash_option(
    name="question",
    description="Your question for the AI",
    opt_type=interactions.OptionType.STRING,
    required=True,
)
async def ask(ctx: interactions.SlashContext, question: str):
    await ctx.defer()

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "meta-llama/llama-3-8b-instruct",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": question}
        ],
        "max_tokens": 2048
    }

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=60,
        )
        data = response.json()
        answer = data["choices"][0]["message"]["content"]

        if len(answer) < MAX_CHARS:
            await ctx.send(answer)
        else:
            paste_url = upload_to_pastebin(answer)
            if paste_url:
                await ctx.send(f"📝 The answer was too long! Here's the Pastebin link:\n{paste_url}")
            else:
                await ctx.send("❌ Failed to upload to Pastebin.", ephemeral=True)

    except Exception as e:
        await ctx.send(f"OpenRouter error: {e}", ephemeral=True)
