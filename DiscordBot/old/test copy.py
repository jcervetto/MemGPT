import asyncio
import websockets
import json

# Constants
CLIENT_TIMEOUT = 30  # Timeout for server response in seconds
CLEAN_RESPONSES = False  # Set to True to format the responses

def print_server_response(response):
    """Prints the server response in a formatted manner."""
    print(f"Type: {response.get('type')}")
    if 'message' in response:
        print(f"Message: {response.get('message')}")
    print("---")

def condition_to_stop_receiving(response):
    """Define a condition to stop receiving messages from the server."""
    return response.get("type") == "agent_response_end"

# Define the functions from your provided code
def client_user_message(msg, agent_name=None):
    return json.dumps({
        "type": "user_message",
        "message": msg,
        "agent_name": agent_name,
    })

def client_command_load(agent_name):
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
