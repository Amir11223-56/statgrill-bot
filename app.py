from flask import Flask, request
import requests
import os
import openai
from dotenv import load_dotenv

# 🔁 Load environment variables from .env file
load_dotenv()

# 🔐 Tokens
VERIFY_TOKEN = "my_secret_token"  # Facebook Webhook verification token
PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")
openai.api_key = os.getenv("GROQ_API_KEY")
openai.api_base = "https://api.groq.com/openai/v1"  # Use Groq's OpenAI-compatible API

app = Flask(__name__)

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        if token == VERIFY_TOKEN:
            return challenge, 200
        return "Verification failed", 403

    if request.method == "POST":
        data = request.get_json()
        print("Webhook received:", data)

        for entry in data.get("entry", []):
            for messaging_event in entry.get("messaging", []):
                sender_id = messaging_event["sender"]["id"]

                if "message" in messaging_event:
                    text = messaging_event["message"].get("text", "")
                    reply = generate_reply(text)
                    send_message(sender_id, reply)

        return "ok", 200

def generate_reply(user_text):
    
    try:
        response = openai.ChatCompletion.create(
            model="llama3-70b-8192",
            messages=[
                {
                    "role": "system",
                    "content": (
                        'Be funny'
                    )
                },
                {"role": "user", "content": user_text}
            ],
            temperature=0.7,
            max_tokens=150
        )

        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        print("Groq API error:", e)
        return "Sorry, I’m having trouble responding right now. Please try again later."

def send_message(recipient_id, message_text):
    url = "https://graph.facebook.com/v17.0/me/messages"
    params = {"access_token": PAGE_ACCESS_TOKEN}
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": message_text}
    }
    headers = {"Content-Type": "application/json"}

    response = requests.post(url, params=params, json=payload, headers=headers)
    print("Sent message:", response.status_code, response.text)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
