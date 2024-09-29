import os
import re
import time
import threading
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from collections import defaultdict

import torch
from transformers import pipeline

# Initialize the Slack app
assert(os.getenv("Slack_Bot_Token") is not None)
print(os.getenv("Slack_Bot_Token"))
app = App(token=os.getenv("Slack_Bot_Token"))

# Temporary Dict for now
user_kudos:dict[str, int] = {}
user_given_kudos:dict[str, int] = {}
# seconds between awarding kudos (1 week = 604800)
time_between_kudos = 20 

# Your existing functions (slightly modified to use app.client instead of requests)
def post_message_to_slack(channel, text, blocks=None):
    try:
        result = app.client.chat_postMessage(
            channel=channel,
            text=text,
            blocks=blocks
        )
        return result
    except Exception as e:
        print(f"Error posting message: {e}")

def post_file_to_slack(channel, text, file_name, file_bytes, file_type=None, title=None):
    try:
        result = app.client.files_upload(
            channels=channel,
            initial_comment=text,
            filename=file_name,
            filetype=file_type,
            title=title,
            content=file_bytes
        )
        return result
    except Exception as e:
        print(f"Error uploading file: {e}")

def weekly_kudos_winner_to_slack(users_kudos:dict[str, int], channel="C07Q6AGELHW", given=False):
    max_kudos:int = -1
    max_user:str = None
    for user, kudos_num in users_kudos.items():
        if kudos_num > max_kudos:
            max_kudos = kudos_num
            max_user = user
    if not given:
        post_message_to_slack(channel=channel, text=f"Congratulations <@{max_user}> for recieving the most Kudos this week!")
        for user in user_kudos:
            user_kudos[user]=0
    else:
        post_message_to_slack(channel=channel, text=f"Congratulations <@{max_user}> for giving out the most Kudos this week!")
        for user in user_given_kudos:
            user_given_kudos[user]=0


def add_points(points_dict:dict[str, int], user:str, points:int):
    if user not in points_dict:
        points_dict[user] = points
    else:
        points_dict[user] += points
#def update_kudos_points(user_name):
    

# constantly checks if its been a week and updates kudos if so 
def check_and_award_points():
    while(True):
        time.sleep(time_between_kudos)
        weekly_kudos_winner_to_slack(user_kudos)
        weekly_kudos_winner_to_slack(user_given_kudos, given=True)
        #TODO make this reset the kudos amounts
        


# def post_start_process_to_slack(channel, process_name):
#     start_time = "0"  # You might want to use a real timestamp here
#     start_block = [
#         {
#             "type": "header",
#             "text": {
#                 "type": "plain_text",
#                 "text": "A new process has just started :rocket:",
#             }
#         },
#         {
#             "type": "section",
#             "fields": [{
#                 "type": "mrkdwn",
#                 "text": f"Process _{process_name}_ started at {start_time}"
#             }]
#         }
#     ]

#     post_message_to_slack(channel, "New process kicked off!", start_block)

# Event listener for messages
def parse_slack_user(event):
    blocks = event.get('blocks', [])
    mentioned_users = set()

    for block in blocks:
        if block['type'] == 'rich_text':
            for element in block.get('elements', []):
                if element['type'] == 'rich_text_section':
                    for item in element.get('elements', []):
                        if item['type'] == 'user':
                            mentioned_users.add(item['user_id'])

    return mentioned_users


def check_kudos(event, message):
    text = event.get('text')
    model_id = "meta-llama/Llama-3.2-1B-Instruct"
    pipe = pipeline(
    "text-generation",
    model=model_id,
    torch_dtype=torch.bfloat16,
    device_map="auto",
)
    messages = [
    {"role": "system", "content": "Please check if a message is positive and output a float"},
    {"role": "user", "content": text},
    ]

    outputs = pipe(
        messages,
        max_new_tokens=256,
    )
    print(outputs[0]["generated_text"][-1])


@app.event("message")
def handle_message(event, say):
    text = event.get('text')
    user = event.get('user')
    channel = event.get('channel')

    print(event)
    print(f"Message received - User: {user}, Channel: {channel}, Text: {text}")

    # Uncomment the following line if you want the bot to respond to messages
    # say(f"I received your message: {text}")
    # excludes @channel and @here

    # {'user': 'U07PELKA9AR', 'type': 'message', 'ts': '1727570796.123859', 'client_msg_id': '1e9b8d7f-f09c-4d72-9af7-54f157fe85fa', 'text': 'hello <@U07PL1TEGLC>', 'team': 'T07PW745R8R', 'blocks': [{'type': 'rich_text', 'block_id': 'lUvAn', 'elements': [{'type': 'rich_text_section', 'elements': [{'type': 'text', 'text': 'hello '}, {'type': 'user', 'user_id': 'U07PL1TEGLC'}]}]}], 'channel': 'C07Q6AGELHW', 'event_ts': '1727570796.123859', 'channel_type': 'channel'}

    # user_mention_pattern = re.compile(r'<@((?!channel|here)[A-Z0-9]+)>')
    mentioned_users = parse_slack_user(event)
    for mentioned_user in mentioned_users:
        if mentioned_user != user:
        # sends message in slac
            post_message_to_slack(channel, f"<@{user}> gave kudos to <@{mentioned_user}>")
            add_points(user_kudos, mentioned_user, 2)
            add_points(user_given_kudos, user, 1)
            post_message_to_slack(channel, f"<@{mentioned_user}> has received {user_kudos[mentioned_user]}, <@{user}> has given {user_given_kudos[user]}")

        else:
            post_message_to_slack(channel, f"Nice try <@{user}>, but you can't give kudos to yourself!")
        

# Event listener for reactions
@app.event("reaction_added")
def handle_reaction(event, say):
    reaction = event['reaction']
    print(f"{reaction}")

    positive_reactions = ["+1", "clap", "checkmark", "heart", "party popper", "smiley"]
    liked_user = event['item_user']
    user = event['user']
    if reaction in positive_reactions:
        add_points(user_kudos, liked_user, 1)
        #add_points(user, user_given_kudos, 1)
    if reaction=="frog":
        add_points(user_kudos, user, 10)


# Main function to start the app
if __name__ == "__main__":
    assert(os.getenv("Slack_App_Token") is not None)
    threading.Thread(target=check_and_award_points).start()
    handler = SocketModeHandler(app, os.getenv("Slack_App_Token"))
    print("Starting the app...")
    handler.start()