import os
import dotenv
import discord
import requests
from datetime import datetime
import pytz  # Import the pytz module for time zone handling
from localAssistant import LocalAssistant

dotenv.load_dotenv()

bot_token = os.getenv("LAN_TOKEN")
intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

# Initialize the LocalAssistant instance
assistant = LocalAssistant("ws://localhost:8282", "agent_6")

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if client.user is not None and client.user.mentioned_in(message):
        # Fetch current time
        response = requests.get("http://worldtimeapi.org/api/timezone/America/Los_Angeles")
        current_time_data = response.json()
        current_time_str = current_time_data["datetime"]
        current_time = datetime.fromisoformat(current_time_str)
        formatted_current_time = current_time.strftime("%A, %B %d %H:%M")

        username = message.author.display_name
        user_message = message.content.replace(f"@{client.user.name}", "")
        responses = await assistant.send_and_receive_message(f"Time: The current time in Vancouver is {formatted_current_time}  \n {username} : {user_message} ")
        
        if responses:
            for response in responses:
                formatted_response = f"{response}"
                await send_split_messages(message.channel, formatted_response)
        else:
            await message.channel.send("No response received or an error occurred.")
    else:
        return

async def send_split_messages(channel, message, char_limit=2000):
    for i in range(0, len(message), char_limit):
        chunk = message[i:i+char_limit]
        await channel.send(chunk)

client.run(bot_token)
