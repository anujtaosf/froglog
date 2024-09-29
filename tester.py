
import os
import json
from typing import List, Dict

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

# Initialize the Slack Bolt app
app = App(token=os.environ["Slack_Bot_Token"])

def post_message_to_slack(text: str, blocks: List[Dict[str, str]] = None):
    try:
        response = app.client.chat_postMessage(
            channel=os.environ["Channel"],
            text=text,
            blocks=json.dumps(blocks) if blocks else None
        )
        return response
    except Exception as e:
        print(f"Error posting message: {e}")

@app.event("message")
def handle_message(event, say):
    text = event.get('text')
    user = event.get('user')
    channel = event.get('channel')

    mentioned_users = requests.findall(r'<@(\w+)>', event['text'])

    
    print(f"Message received - User: {user}, Channel: {channel}, Text: {text}")

    # Uncomment the following line if you want the bot to respond to messages
    say(f"I received your message: {text}")

if __name__ == "__main__":
    # Start the app using Socket Mode
    handler = SocketModeHandler(app, os.environ["Slack_App_Token"])
    print("⚡️ Bolt app is running!")
    handler.start()