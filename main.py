import os
import requests
import interactions
from interactions import Client, slash_command, slash_option, OptionType, AutoDefer

# Load environment variables (make sure these are set in your environment)
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PASTEBIN_API_KEY = os.getenv("PASTEBIN_API_KEY")
PASTEBIN_USER_KEY = os.getenv("PASTEBIN_USER_KEY")  # Optional

bot = Client(token=DISCORD_TOKEN, intents=interactions.Intents.DEFAULT)

# Pastebin helper function
def paste_to_pastebin(text: str, title="LLaMA Response") -> str | None:
    url = "https://pastebin.com/api/api_post.php"
    data = {
        "api_dev_key": PASTEBIN_API_KEY,
        "api_option": "paste",
        "api_paste_code": text,
        "api_paste_name": title,
        "api_paste_expire_date": "1W",
    }
    if PASTEBIN_USER_KEY:
        data["api_user_key"] = PASTEBIN_USER_KEY
    resp = requests.post(url, data=data)
    if resp.status_code == 200 and "pastebin.com" in resp.text:
        return resp.text
    else:
        return None

# Image generation with OpenAI DALL·E
async def generate_image(prompt: str) -> str:
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }
    json_data = {
        "model": "dall-e-3",
        "prompt": prompt,
        "n": 1,
        "size": "1024x1024",
    }
    async with bot.http._session.post(
        "https://api.openai.com/v1/images/generations", headers=headers, json=json_data
    ) as resp:
        if resp.status != 200:
            text = await resp.text()
            raise Exception(f"OpenAI API error {resp.status}: {text}")
        data = await resp.json()
        return data["data"][0]["url"]

# Placeholder for LLaMA call - replace this function with your actual API call if you have one
def llama_query(question: str) -> str:
    # Simulate a long response for testing
    return (
        f"Simulated LLaMA response to:\n{question}\n\n" +
        "Lorem ipsum " * 300
    )

@slash_command(name="ask", description="Ask LLaMA a question")
@slash_option(
    name="question",
    description="Your question to LLaMA",
    opt_type=OptionType.STRING,
    required=True,
)
@AutoDefer()
async def ask(ctx: interactions.CommandContext, question: str):
    response_text = llama_query(question)
    MAX_LEN = 1900  # Discord message max safe length

    if len(response_text) > MAX_LEN:
        paste_url = paste_to_pastebin(response_text)
        if paste_url:
            await ctx.send(f"Response too long, see full here: {paste_url}")
        else:
            await ctx.send(response_text[:MAX_LEN] + "\n\n...(failed to upload full response)")
    else:
        await ctx.send(response_text)

@slash_command(name="image", description="Generate an image with DALL·E")
@slash_option(
    name="prompt",
    description="Describe the image you want",
    opt_type=OptionType.STRING,
    required=True,
)
@AutoDefer()
async def image(ctx: interactions.CommandContext, prompt: str):
    try:
        url = await generate_image(prompt)
        await ctx.send(url)
    except Exception as e:
        await ctx.send(f"Error generating image: {e}")

if __name__ == "__main__":
    bot.start()
