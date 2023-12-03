import asyncio
import websockets
import json
import re  # Import the regular expressions module

# Constants
CLIENT_TIMEOUT = 30  # Timeout for server response in seconds
CLEAN_RESPONSES = True  # Set to True to format the responses

def print_server_response(response):
    """Prints the server response, extracting the message if it's a function message."""
    response_type = response.get('type')
    message_type = response.get('message_type')
    message = response.get('message')

    if response_type == "agent_response" and message_type == "function_message":
        # Extract the message from the function_message
        match = re.search(r"send_message\(\{'message': '(.+?)'\}\)", message)
        if match:
            extracted_message = match.group(1)
            print(f"Extracted Message: {extracted_message}")
        else:
            print(f"Function Message: {message}")
    else:
        # Print other types of responses as is
        print(f"Server response:\n{json.dumps(response, indent=2)}")

def condition_to_stop_receiving(response):
    """Define a condition to stop receiving messages from the server."""
    return response.get("type") == "agent_response_end"

def client_user_message(msg, agent_name=None):
    """Create a JSON message for user to server communication."""
    return json.dumps({
        "type": "user_message",
        "message": msg,
        "agent_name": agent_name,
    })

def client_command_load(agent_name):
    """Create a JSON message to load a specific agent."""
    return json.dumps({
        "type": "command",
        "command": "load_agent",
        "name": agent_name,
    })

async def send_message(uri, load_command, user_message):
    async with websockets.connect(uri) as websocket:
        # Send command to load the agent
        await websocket.send(load_command)
        
        # Send the user message to the loaded agent
        await websocket.send(user_message)

        # Wait for messages in a loop, since the server may send a few
        while True:
            try:
                response = await asyncio.wait_for(websocket.recv(), CLIENT_TIMEOUT)
                response = json.loads(response)

                if CLEAN_RESPONSES:
                    print_server_response(response)
                else:
                    print(f"Server response:\n{json.dumps(response, indent=2)}")

                # Check for a specific condition to break the loop
                if condition_to_stop_receiving(response):
                    break
            except asyncio.TimeoutError:
                print("Timeout waiting for the server response.")
                break
            except websockets.exceptions.ConnectionClosedError:
                print("Connection to server was lost.")
                break
            except Exception as e:
                print(f"An error occurred: {e}")
                break

# WebSocket server URI
uri = "ws://localhost:8282"  # Replace with your server's URI

# Create the load command and user message
load_command = client_command_load("agent_1")  # Replace with your agent's name
user_message = client_user_message("hello", "agent_1")  # Replace with your message and agent's name

# Run the coroutine to send the messages
asyncio.get_event_loop().run_until_complete(send_message(uri, load_command, user_message))
