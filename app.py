from flask import Flask, request
from linebot.v3.messaging import (
    Configuration, ApiClient, MessagingApi, ReplyMessageRequest, TextMessage
)
from linebot.v3.webhooks import WebhookParser, MessageEvent, TextMessageContent
from linebot.v3.exceptions import InvalidSignatureError
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

LINE_ACCESS_TOKEN = os.getenv("LINE_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")

# Initialize Flask app
app = Flask(__name__)

# LINE v3 SDK setup
config = Configuration(access_token=LINE_ACCESS_TOKEN)
api_client = ApiClient(config)
messaging_api = MessagingApi(api_client)
parser = WebhookParser(LINE_CHANNEL_SECRET)

# Save user ID to file (basic implementation)
def save_user(user_id):
    with open("users.txt", "a+") as f:
        f.seek(0)
        if user_id not in f.read():
            f.write(user_id + "\n")

@app.route("/")
def index():
    return "LINE Bot is running."

@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers.get("X-Line-Signature")
    body = request.get_data(as_text=True)

    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        return "Invalid signature", 400

    for event in events:
        if isinstance(event, MessageEvent) and isinstance(event.message, TextMessageContent):
            user_id = event.source.user_id
            save_user(user_id)

            reply_text = "Thanks! You'll start getting a daily English word soon."

            req = ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=reply_text)]
            )
            messaging_api.reply_message(req)

    return "OK"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
