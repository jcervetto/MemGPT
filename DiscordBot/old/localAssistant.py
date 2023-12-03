import asyncio
import websockets
import json
import re

CLIENT_TIMEOUT = 30  # Timeout for server response in seconds

def create_client_user_message(msg, agent_name=None):
    """Create a JSON message for user to server communication."""
    return json.dumps({
        "type": "user_message",
        "message": msg,
        "agent_name": agent_name,
    })

def create_client_command_load(agent_name):
    """Create a JSON message to load a specific agent."""
    return json.dumps({
        "type": "command",
        "command": "load_agent",
        "name": agent_name,
    })

async def send_and_receive_message(uri, agent_name, user_message):
    load_command = create_client_command_load(agent_name)
    user_message = create_client_user_message(user_message, agent_name)

    async with websockets.connect(uri) as websocket:
        await websocket.send(load_command)
        await websocket.send(user_message)

        extracted_message = None
        while True:
            try:
                response = await asyncio.wait_for(websocket.recv(), CLIENT_TIMEOUT)
                response = json.loads(response)
                message_type = response.get('message_type')
                message = response.get('message')

                if message_type == "function_message":
                    # Revised regular expression to match the format accurately
                    match = re.search(r"Running send_message\(\{'message': '([^']+)'", message)
                    if match:
                        extracted_message = match.group(1)
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

        return extracted_message

# Example usage
async def main():
    uri = "ws://localhost:8282"  # Replace with your server's URI
    agent_name = "agent_1"  # Replace with your agent's name
    message = "Tell me your name and purpose"  # Replace with your message

    response_message = await send_and_receive_message(uri, agent_name, message)
    if response_message:
        print(f"Extracted Message: {response_message}")
    else:
        print("No specific message was extracted.")

# Run the main coroutine
asyncio.get_event_loop().run_until_complete(main())
