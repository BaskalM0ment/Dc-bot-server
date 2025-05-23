import os
import requests
import interactions

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PASTEBIN_API_KEY = os.getenv("PASTEBIN_API_KEY")

bot = interactions.Client(token=DISCORD_TOKEN)


@interactions.slash_command(name="ask", description="Ask LLaMA a question")
async def ask(ctx: interactions.SlashContext, question: str = interactions.slash_option(
    name="question",
    description="Your question to LLaMA",
    required=True,
    opt_type=interactions.OptionType.STRING
)):
    await ctx.defer()

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "meta-llama/llama-3-8b-instruct",
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": question},
                ],
                "max_tokens": 2048,
                "temperature": 0.7,
            },
        )
        response.raise_for_status()
        answer = response.json()["choices"][0]["message"]["content"]

        if len(answer) < 1900:
            await ctx.send(answer)
        else:
            paste = requests.post("https://pastebin.com/api/api_post.php", data={
                "api_dev_key": PASTEBIN_API_KEY,
                "api_option": "paste",
                "api_paste_code": answer,
                "api_paste_name": f"Ask result",
                "api_paste_expire_date": "1D",
                "api_paste_private": "1"
            })
            await ctx.send(f"📄 Response was too long. View it here: {paste.text}")

    except Exception as e:
        await ctx.send(f"Error: {e}", ephemeral=True)


@interactions.slash_command(name="imagine", description="Generate an AI image")
async def imagine(ctx: interactions.SlashContext, prompt: str = interactions.slash_option(
    name="prompt",
    description="Prompt for the image",
    required=True,
    opt_type=interactions.OptionType.STRING
)):
    await ctx.defer()

    try:
        response = requests.post(
            "https://api.openai.com/v1/images/generations",
            headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "dall-e-3",
                "prompt": prompt,
                "n": 1,
                "size": "1024x1024"
            }
        )
        response.raise_for_status()
        image_url = response.json()["data"][0]["url"]
        await ctx.send(f"🖼️ Image generated: {image_url}")
    except Exception as e:
        await ctx.send(f"Error generating image: {e}", ephemeral=True)


if __name__ == "__main__":
    bot.start()
