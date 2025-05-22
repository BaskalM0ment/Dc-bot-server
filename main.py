import interactions
import os
import requests

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
PASTEBIN_API_KEY = os.getenv("PASTEBIN_API_KEY")

# Enable default intents + direct messages intent
intents = interactions.Intents.DEFAULT | interactions.Intents.DIRECT_MESSAGES

bot = interactions.Client(token=os.getenv("DISCORD_TOKEN"), intents=intents)

@interactions.slash_command(name="ask", description="Ask LLaMA a question")
@interactions.AutoDefer()  # defer to give time for processing
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

# Debug listener to confirm DM commands reach the bot
@bot.event
async def on_interaction_create(interaction):
    if interaction.guild_id is None:  # Means DM
        print(f"Received DM interaction: {interaction.data.get('name')} from {interaction.user.username}")

if __name__ == "__main__":
    bot.start()
