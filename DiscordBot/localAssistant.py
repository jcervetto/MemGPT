import json
import asyncio
import websockets

CLIENT_TIMEOUT = 18000  # Timeout for server response in seconds

class LocalAssistant:
    def __init__(self, uri, agent_name):
        self.uri = uri
        self.agent_name = agent_name

    def create_client_user_message(self, msg):
        """Create a JSON message for user to server communication."""
        return json.dumps({
            "type": "user_message",
            "message": msg,
            "agent_name": self.agent_name,
        })

    async def send_and_receive_message(self, user_message):
        """Sends a message to the WebSocket server and waits for a full response."""
        user_message_json = self.create_client_user_message(user_message)

        try:
            async with websockets.connect(self.uri) as websocket:
                await websocket.send(user_message_json)
                return await self.collect_responses(websocket)
        except websockets.exceptions.ConnectionClosedError as e:
            print(f"Connection to server was lost: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")

    async def collect_responses(self, websocket):
        """Collects all parts of the server response."""
        responses = []
        try:
            while True:
                response = await asyncio.wait_for(websocket.recv(), CLIENT_TIMEOUT)
                response_json = json.loads(response)

                if self.condition_to_stop_receiving(response_json):
                    break

                message = self.extract_assistant_message(response_json)
                if message:
                    responses.append(message)

            return responses
        except asyncio.TimeoutError:
            print("Timeout waiting for the server response.")
            return responses
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return responses

    def condition_to_stop_receiving(self, response):
        """Determines when to stop listening to the server"""
        return response.get("type") in ["agent_response_end", "agent_response_error", "command_response", "server_error"]

    def extract_assistant_message(self, response_json):
        """Extracts only 'assistant_message' from the server response."""
        if response_json.get("type") == "agent_response" and response_json.get("message_type") == "assistant_message":
            return response_json.get("message")

    @staticmethod
    def log_server_response(response_json):
        """Logs the server response."""
        print(f"Server response:\n{json.dumps(response_json, indent=2)}")
