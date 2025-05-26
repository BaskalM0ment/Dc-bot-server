@interactions.slash_command(
    name="image",
    description="Generate an image using DALL·E"
)
@interactions.slash_option(
    name="prompt",
    description="Describe the image you want",
    required=True,
    opt_type=interactions.OptionType.STRING
)
async def image(ctx: interactions.SlashContext, prompt: str):
    await ctx.defer()

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

    try:
        response = requests.post(
            "https://api.openai.com/v1/images/generations",
            headers=headers,
            json=json_data
        )
        response.raise_for_status()
        image_url = response.json()["data"][0]["url"]

        # Download image from the URL
        image_data = requests.get(image_url)
        image_data.raise_for_status()

        # Send the image as a file
        await ctx.send(files=[interactions.File(file=image_data.content, file_name="generated.png")])

    except Exception as e:
        await ctx.send(f"❌ Error generating image: {e}", ephemeral=True)
