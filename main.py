import os
import interactions
import requests

# Pastebin & OpenRouter/OpenAI config
PASTEBIN_API_KEY = os.getenv("PASTEBIN_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

bot = interactions.Client(token=os.getenv("DISCORD_BOT_TOKEN"))

@interactions.slash_command(name="ask", description="Ask LLaMA a question")
@interactions.slash_option(
    name="question",
    description="Your question to LLaMA",
    required=True,
    opt_type=interactions.OptionType.STRING,
)
@interactions.AutoDefer()
async def ask(ctx: interactions.SlashContext, question: str):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    body = {
        "model": "meta-llama/llama-3-70b-instruct",
        "messages": [{"role": "user", "content": question}],
        "temperature": 0.7
    }

    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", json=body, headers=headers)
        response.raise_for_status()
        answer = response.json()["choices"][0]["message"]["content"]

        if len(answer) > 1900:
            paste = requests.post(
                "https://pastebin.com/api/api_post.php",
                data={
                    "api_dev_key": PASTEBIN_API_KEY,
                    "api_option": "paste",
                    "api_paste_code": "llama_response",
                    "api_paste_private": "1",
                    "api_paste_expire_date": "1H",
                    "api_paste_name": "LLaMA Response",
                    "api_paste_format": "text",
                    "api_paste_code": answer
                }
            )
            await ctx.send(f"📄 Response too long, view here: {paste.text}")
        else:
            await ctx.send(answer)

    except Exception as e:
        await ctx.send(f"❌ Error: {e}")

@interactions.slash_command(name="imagine", description="Generate an AI image with DALL·E")
@interactions.slash_option(
    name="prompt",
    description="Describe the image you want",
    required=True,
    opt_type=interactions.OptionType.STRING,
)
@interactions.AutoDefer()
async def imagine(ctx: interactions.SlashContext, prompt: str):
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
        response = requests.post("https://api.openai.com/v1/images/generations", headers=headers, json=data)
        response.raise_for_status()
        image_url = response.json()["data"][0]["url"]
        await ctx.send(image_url)
    except Exception as e:
        await ctx.send(f"❌ Error generating image: {e}")

bot.start()
