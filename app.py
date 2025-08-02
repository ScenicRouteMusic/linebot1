from flask import Flask, request
from dotenv import load_dotenv
import os

from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.webhooks import MessageEvent, TextMessageContent
from linebot.v3.webhook import WebhookHandler
from linebot.v3.messaging import (
    Configuration, ApiClient, MessagingApi,
    TextMessage, ReplyMessageRequest
)

load_dotenv()

# Load LINE credentials from .env
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
LINE_ACCESS_TOKEN = os.getenv("LINE_ACCESS_TOKEN")

# LINE SDK v3 setup
handler = WebhookHandler(LINE_CHANNEL_SECRET)
config = Configuration(access_token=LINE_ACCESS_TOKEN)
api_client = ApiClient(configuration=config)
messaging_api = MessagingApi(api_client)

# Flask app setup
app = Flask(__name__)

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

        reply = "Thanks! You'll start getting a daily English word soon."
        req = ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[TextMessage(text=reply)]
        )
        messaging_api.reply_message(req)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
