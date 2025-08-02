from linebot import LineBotApi
from linebot.models import TextSendMessage
import csv, random, os
from dotenv import load_dotenv

load_dotenv()

line_bot_api = LineBotApi(os.getenv("LINE_ACCESS_TOKEN"))

# Load words
with open("words.csv", newline='', encoding='utf-8') as csvfile:
    reader = list(csv.DictReader(csvfile))
    word_entry = random.choice(reader)

word = word_entry['word']
thai = word_entry['thai']
example = word_entry['example']

msg = f"{word} - {thai}\nExample: {example}"

# Load user IDs
with open("users.txt", "r") as f:
    users = [line.strip() for line in f.readlines()]

for user in users:
    line_bot_api.push_message(user, TextSendMessage(text=msg))
