from flask import Flask, request
import requests
import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")  # Or hardcode it (not recommended)

app = Flask(__name__)

# 🔐 Tokens
VERIFY_TOKEN = "my_secret_token"  # You gave this to Facebook when verifying webhook
PAGE_ACCESS_TOKEN = "EAARZCFOn4eVYBOx5tAAKPBxE9bCgJeZBghBsFE6TyZB8JjO1ysgNZB8nfGPzhvsvFnsoDBw2rjfmMZBJsfEzxjQLv4gqOMphcqjq7HTAGtPKEX97j8uaaVvOIOsjnxYOOGu84LiLibU3hoE2ZAsZBFV7xQHANu5URgbkEF5ISLQIqSHvYIgXR60sMNnjXlhMTlomHtwKFZBnVAZDZD"

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
            model="gpt-4",  # or "gpt-3.5-turbo" if you're on a smaller budget
            messages=[
                {"role": "system", "content": "You are a helpful assistant for a restaurant named Kitchener Grill. Answer casually and helpfully."},
                {"role": "user", "content": user_text}
            ],
            temperature=0.7,
            max_tokens=200
        )
        return response["choices"][0]["message"]["content"].strip()

    except Exception as e:
        print("LLM error:", e)
        return "Oops! Something went wrong. Can you try again?"

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
