import torch
from transformers import AutoConfig, AutoModelForCausalLM, AutoTokenizer, pipeline
# import os
# from slack_bolt import App
# from slack_bolt.adapter.socket_mode import SocketModeHandler
# # Initialize the Slack app
# assert(os.getenv("Slack_Bot_Token") is not None)
# print(os.getenv("Slack_Bot_Token"))
# app = App(token=os.getenv("Slack_Bot_Token"))



pipe = pipeline("text-classification", model="cardiffnlp/twitter-roberta-base-sentiment-latest")
#sentiment_task = pipeline("sentiment-analysis", model=model_path, tokenizer=model_path)
print(pipe("<@U123458> you are doing great!"))