import csv
import os
from dotenv import load_dotenv
from linebot.v3.messaging import (
    Configuration, ApiClient, MessagingApi, PushMessageRequest, TextMessage
)

load_dotenv()

LINE_ACCESS_TOKEN = os.getenv("LINE_ACCESS_TOKEN")

# LINE v3 setup
config = Configuration(access_token=LINE_ACCESS_TOKEN)
api_client = ApiClient(config)
messaging_api = MessagingApi(api_client)

# Load word of the day
with open("words.csv", newline='', encoding='utf-8') as csvfile:
    reader = list(csv.DictReader(csvfile))
    word_entry = reader[0]  # Can be random.choice(reader) if you prefer

word = word_entry["word"]
thai = word_entry["thai"]
example = word_entry["example"]

message_text = f"{word} - {thai}\nExample: {example}"

# Load all user IDs
with open("users.txt", "r") as f:
    users = [line.strip() for line in f.readlines()]

# Send to each user
for user_id in users:
    try:
        req = PushMessageRequest(
            to=user_id,
            messages=[TextMessage(text=message_text)]
        )
        messaging_api.push_message(req)
        print(f"Sent to {user_id}")
    except Exception as e:
        print(f"Failed to send to {user_id}: {e}")
