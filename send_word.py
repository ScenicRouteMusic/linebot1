import csv
import os
import random
from dotenv import load_dotenv
from linebot.v3.messaging import (
    Configuration, ApiClient, MessagingApi,
    PushMessageRequest, TextMessage
)

load_dotenv()

LINE_ACCESS_TOKEN = os.getenv("LINE_ACCESS_TOKEN")
config = Configuration(access_token=LINE_ACCESS_TOKEN)
api_client = ApiClient(config)
messaging_api = MessagingApi(api_client)

# Load sent words
sent_words = set()
if os.path.exists("sent_words.txt"):
    with open("sent_words.txt", "r", encoding="utf-8") as f:
        sent_words = set(line.strip().lower() for line in f if line.strip())

# Load all available words from CSV
with open("words.csv", newline='', encoding="utf-8") as csvfile:
    reader = list(csv.DictReader(csvfile))
    remaining_words = [row for row in reader if row["word"].lower() not in sent_words]

if not remaining_words:
    print("⚠️ All words have been sent!")
    exit()

# Pick one random unsent word
word_entry = random.choice(remaining_words)
word = word_entry["word"]
thai = word_entry["thai"]
example = word_entry["example"]

message_text = f"{word} - {thai}\nExample: {example}"

# Load user list
with open("users.txt", "r", encoding="utf-8") as f:
    users = [line.strip() for line in f if line.strip()]

# Send to each user
for user in users:
    try:
        req = PushMessageRequest(
            to=user,
            messages=[TextMessage(text=message_text)]
        )
        messaging_api.push_message(req)
        print(f"✅ Sent to {user}")
    except Exception as e:
        print(f"❌ Failed to send to {user}: {e}")

# Save the sent word
with open("sent_words.txt", "a", encoding="utf-8") as f:
    f.write(f"{word.lower()}\n")
