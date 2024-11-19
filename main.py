import openai
import discord
from discord.ext import commands

# Set your API key and base URL
openai.api_key = "glhf_91994f31ff86447954f4f31c0360ea4f"  # Replace with your actual API key
openai.api_base = "https://glhf.chat/api/openai/v1"

# Discord bot token
BOT_TOKEN = "MTMwODEyMzI5NDA3OTEyMzQ1Ng.GuM1tw.UM8MCMNsSJdpe4IM3x0Bb9RnqrIRjR_Ae_qLb4"

# Conversations history for persistent chat context
conversations = [{"role": "system", "content": "act like a chav and use emojies say stuff like this put a # and put your words here init mate ."}]

# Create bot with command prefix
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

def get_ai_response(user_message):
    """
    Sends a message to OpenAI and retrieves the AI response.
    """
    # Add user message to conversation history
    conversations.append({"role": "user", "content": user_message})
    try:
        # Query OpenAI API
        response = openai.ChatCompletion.create(
            model="hf:mistralai/Mistral-7B-Instruct-v0.3",
            messages=conversations
        )
        assistant_reply = response.choices[0].message["content"]

        # Check if the response contains code and format it with triple backticks
        if "```" not in assistant_reply and any(line.strip().startswith("def") or line.strip().startswith("class") or line.strip().startswith("import") for line in assistant_reply.splitlines()):
            assistant_reply = f"```{assistant_reply}```"

        # Add assistant's reply to conversation history
        conversations.append({"role": "assistant", "content": assistant_reply})
        return assistant_reply
    except Exception as e:
        return f"Error: {e}"

def split_message(content, max_length=2000):
    """
    Split a message into chunks that are no longer than max_length (default 2000).
    """
    return [content[i:i + max_length] for i in range(0, len(content), max_length)]

@bot.event
async def on_ready():
    print(f"Bot is online as {bot.user}")

@bot.event
async def on_message(message):
    """
    Listens for mentions of the bot and responds accordingly.
    """
    # Check if the bot is mentioned in the message
    if bot.user.mentioned_in(message):
        # Remove the bot mention from the message to capture only the user input
        user_message = message.content[len(f"<@!{bot.user.id}>"):].strip()

        if not user_message:
            await message.channel.send(f"{message.author.mention} Please ask something after mentioning me.")
            return

        # Send a "Bot is typing..." message, reply to the sender
        typing_message = await message.channel.send(f"{message.author.mention} Bot is typing...")

        # Get AI response
        ai_response = get_ai_response(user_message)

        # Split the message if it's too long
        split_responses = split_message(ai_response)

        try:
            # Edit the "Bot is typing..." message to show the AI's response
            for part in split_responses:
                # Send the split parts one by one
                await typing_message.edit(content=f"{message.author.mention} {part}")
        except discord.errors.HTTPException as e:
            # Handle the error if the message is too long (more than 2000 characters)
            if "400 Bad Request" in str(e) and "Must be 2000 or fewer in length" in str(e):
                await typing_message.edit(content=f"{message.author.mention} The response is too long to display! Please ask something else.")
            else:
                # If the error isn't related to message length, log it
                print(f"Unexpected HTTP error: {e}")

if __name__ == "__main__":
    bot.run(BOT_TOKEN)
