import interactions
import os
import requests
import json

bot = interactions.Client(token=os.getenv("DISCORD_TOKEN"))
openrouter_key = os.getenv("OPENROUTER_API_KEY")
openai_key = os.getenv("OPENAI_API_KEY")
pastebin_key = os.getenv("PASTEBIN_API_KEY")

@interactions.slash_command(name="ask", description="Ask LLaMA a question")
@interactions.option("question", str, description="Your question to LLaMA", required=True)
@interactions.AutoDefer()
async def ask(ctx: interactions.SlashContext, question: str):
    headers = {
        "Authorization": f"Bearer {openrouter_key}",
        "Content-Type": "application/json",
    }
    data = {
        "model": "meta-llama/llama-3-70b-instruct",
        "messages": [{"role": "user", "content": question}]
    }

    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
        response.raise_for_status()
        answer = response.json()["choices"][0]["message"]["content"]

        if len(answer) > 1900:
            paste = requests.post(
                "https://pastebin.com/api/api_post.php",
                data={
                    "api_dev_key": pastebin_key,
                    "api_option": "paste",
                    "api_paste_code": answer,
                }
            )
            paste.raise_for_status()
            await ctx.send(f"Response too long, view here: {paste.text}")
        else:
            await ctx.send(answer)

    except Exception as e:
        await ctx.send(f"Error: {e}")

@interactions.slash_command(name="imagine", description="Generate an image using AI")
@interactions.option("prompt", str, description="Prompt for the image", required=True)
@interactions.AutoDefer()
async def imagine(ctx: interactions.SlashContext, prompt: str):
    headers = {
        "Authorization": f"Bearer {openai_key}",
        "Content-Type": "application/json",
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
        await ctx.send(f"Error generating image: {e}")

bot.start()
