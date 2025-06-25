from flask import Flask, request

app = Flask(__name__)

VERIFY_TOKEN = "my_secret_token"

@app.route("/webhook", methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        if token == VERIFY_TOKEN:
            return challenge, 200
        return "Verification failed", 403

    if request.method == 'POST':
        data = request.json
        print("Received webhook event:", data)
        return "Event received", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
