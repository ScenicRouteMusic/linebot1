from flask import Flask, request
from linebot.v3.webhookhandler import WebHookHandler
from linebot.v3.messaging import (
    Configuration, ApiClient, MessagingApi, ReplyMessageRequest, TextMessage
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent
from linebot.exceptions import InvalidSignatureError
from dotenv import load_dotenv
import os

load_dotenv()

# LINE credentials
LINE_ACCESS_TOKEN = os.getenv("LINE_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")

# Setup Flask
app = Flask(__name__)

# LINE v3 Messaging API
config = Configuration(access_token=LINE_ACCESS_TOKEN)
api_client = ApiClient(config)
messaging_api = MessagingApi(api_client)

# Webhook handler for signature validation
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# Save user IDs
def save_user(user_id):
    with open("users.txt", "a+") as f:
        f.seek(0)
        if user_id not in f.read():
            f.write(user_id + "\n")

@app.route("/")
def home():
    return "LINE Bot is running."

@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers.get("X-Line-Signature")
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        return "Invalid signature", 400

    return "OK"

@handler.add(MessageEvent)
def handle_message(event):
    if isinstance(event.message, TextMessageContent):
        user_id = event.source.user_id
        save_user(user_id)

        reply_text = "Thanks! You'll start getting a daily English word soon."
        request = ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[TextMessage(text=reply_text)]
        )
        messaging_api.reply_message(request)
