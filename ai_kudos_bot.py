import os
import re
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize the Slack app
app = App(token=os.environ.get("Slack_Bot_Token"))

# Initialize the kudos store
kudos_store = {}

@app.event("app_mention")
def handle_mention(event, say, client):
    mentioned_users = re.findall(r'<@(\w+)>', event['text'])

    for user_id in mentioned_users:
        # Don't award points to the bot itself
        if user_id == event['bot_id']:
            continue

        # Award a point
        kudos_store[user_id] = kudos_store.get(user_id, 0) + 1

        try:
            # Fetch user info
            user_info = client.users_info(user=user_id)
            username = user_info['user']['name']

            say(f"Kudos point awarded to <@{user_id}>! {username} now has {kudos_store[user_id]} point(s).")
        except Exception as e:
            print(f"Error fetching user info: {e}")
            say(f"Kudos point awarded to <@{user_id}>! They now have {kudos_store[user_id]} point(s).")

if __name__ == "__main__":
    # Start the app using Socket Mode
    handler = SocketModeHandler(app, os.environ.get("Slack_App_Token"))
    handler.start()