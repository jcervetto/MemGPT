import os
import dotenv
import discord
from localAssistant import LocalAssistant  # Import the updated LocalAssistant class

dotenv.load_dotenv()

bot_token = os.getenv("LAN_TOKEN")
intents = discord.Intents.default()
intents.message_content = True  # Ensure the bot can access the content of messages

client = discord.Client(intents=intents)

# Initialize the LocalAssistant instance
assistant = LocalAssistant("ws://localhost:8282", "agent_4")  # Replace with your WebSocket URI and agent name

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if client.user is not None and client.user.mentioned_in(message):
        # Capture the username of the message sender
        username = message.author.display_name

        # Process the message content, ignoring the mention
        user_message = message.content.replace(f"@{client.user.name}", "")

        # Send the message to the LocalAssistant
        responses = await assistant.send_and_receive_message(f"{username} : {user_message}")
        
        if responses:
            for response in responses:
                # Format the response to include the username
                formatted_response = f"{response}"
                await send_split_messages(message.channel, formatted_response)
        else:
            await message.channel.send("No response received or an error occurred.")
    else:
        # Ignore other messages
        return

async def send_split_messages(channel, message, char_limit=2000):
    """Sends a message in chunks if it's longer than the char_limit."""
    for i in range(0, len(message), char_limit):
        chunk = message[i:i+char_limit]
        await channel.send(chunk)

client.run(bot_token)
