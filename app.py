import os
import csv
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

# Save LINE user ID if not already saved
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
                # Load last non-empty word from sent_words.txt
                with open("sent_words.txt", "r", encoding="utf-8") as f:
                    lines = [line.strip().lower() for line in f if line.strip()]
                    if not lines:
                        reply_text = "❗No word has been sent yet today."
                    else:
                        last_word = lines[-1]

                        # Match it in words.csv
                        with open("words.csv", newline='', encoding='utf-8') as csvfile:
                            reader = list(csv.DictReader(csvfile))
                            match = next((row for row in reader if row["word"].lower() == last_word), None)

                        if match:
                            reply_text = (
                                f"📘 Word: {match['word']}\n"
                                f"🇹🇭 Thai: {match['thai']}\n"
                                f"🗣️ Phonetic: {match['phonetic']}\n"
                                f"📖 Example: {match['example_en']}\n"
                                f"📝 แปล: {match['example_th']}"
                            )
                        else:
                            reply_text = f"⚠️ Word '{last_word}' not found in words.csv."
            except Exception as e:
                reply_text = f"⚠️ Error loading today's word: {str(e)}"
        else:
            reply_text = (
                "👋 Welcome! This bot sends you daily English words.\n"
                "📩 Send `word` to see today's word again."
            )

        # Send the reply
        req = ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[TextMessage(text=reply_text)]
        )
        messaging_api.reply_message(req)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
