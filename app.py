import os
import csv
import random
from flask import Flask, request
from dotenv import load_dotenv
from linebot.v3.webhook import WebhookHandler
from linebot.v3.webhooks import MessageEvent, TextMessageContent
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration, ApiClient, MessagingApi,
    TextMessage, ReplyMessageRequest
)

# Load environment variables
load_dotenv()

LINE_ACCESS_TOKEN = os.getenv("LINE_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")

# Set up LINE Messaging API
handler = WebhookHandler(LINE_CHANNEL_SECRET)
config = Configuration(access_token=LINE_ACCESS_TOKEN)
api_client = ApiClient(configuration=config)
messaging_api = MessagingApi(api_client)

# Set up Flask
app = Flask(__name__)

# Save user if new
def save_user(user_id):
    with open("users.txt", "a+", encoding="utf-8") as f:
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
        text = event.message.text.strip().lower()
        save_user(user_id)

        if text == "word":
            try:
                # Load all words from CSV
                with open("words.csv", newline='', encoding='utf-8') as csvfile:
                    reader = list(csv.DictReader(csvfile))
                    word_entry = random.choice(reader)

                reply_text = (
                    f"📘 Word: {word_entry['word']}\n"
                    f"🇹🇭 Thai: {word_entry['thai']}\n"
                    f"🗣️ Phonetic: {word_entry['phonetic']}\n"
                    f"📖 Example: {word_entry['example_en']}\n"
                    f"📝 แปล: {word_entry['example_th']}"
                )
            except Exception as e:
                reply_text = f"⚠️ Error: {str(e)}"
        else:
            reply_text = (
                "👋 Welcome! Send the word `word` to get a random English vocabulary word with Thai translation."
            )

        req = ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[TextMessage(text=reply_text)]
        )
        messaging_api.reply_message(req)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
