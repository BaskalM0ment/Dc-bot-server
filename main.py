import os
import time
import requests
import interactions

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
PASTEBIN_API_KEY = os.getenv("PASTEBIN_API_KEY")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

bot = interactions.Client(token=DISCORD_TOKEN)

user_cooldowns = {}
COOLDOWN_SECONDS = 0  # Set to 0 for no cooldown

@interactions.slash_command(name="ask", description="Ask LLaMA a question")
@interactions.slash_option(
    name="question",
    description="Your question to LLaMA",
    opt_type=interactions.OptionType.STRING,
    required=True
)
@interactions.AutoDefer()  # <-- THIS MUST BE LAST
async def ask(ctx: interactions.SlashContext, question: str):
    user_id = ctx.author.id
    now = time.time()
    last_used = user_cooldowns.get(user_id, 0)
    if now - last_used < COOLDOWN_SECONDS:
        await ctx.send(
            f"⏳ Wait {int(COOLDOWN_SECONDS - (now - last_used))}s before asking again.",
            ephemeral=True,
        )
        return
    user_cooldowns[user_id] = now

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "meta-llama/llama-3-8b-instruct",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": question},
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
                "api_dev_key": PASTEBIN_API_KEY,
                "api_option": "paste",
                "api_paste_code": answer,
                "api_paste_name": f"Response to: {question[:50]}",
                "api_paste_expire_date": "1D",
                "api_paste_private": "1",
            }
            paste_response = requests.post("https://pastebin.com/api/api_post.php", data=paste_data)
            paste_url = paste_response.text
            if paste_url.startswith("http"):
                await ctx.send(f"📄 Too long, view here: {paste_url}")
            else:
                await ctx.send(f"❌ Pastebin failed: {paste_url}", ephemeral=True)
    except Exception as e:
        await ctx.send(f"❌ Error: {e}", ephemeral=True)

bot.start()
