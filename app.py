from flask import Flask, request, abort
import requests
import openai
import os

app = Flask(__name__)

LINE_ACCESS_TOKEN = os.getenv("LINE_ACCESS_TOKEN")
LINE_REPLY_URL = "https://api.line.me/v2/bot/message/reply"
openai.api_key = os.getenv("OPENAI_API_KEY")

def reply_message(reply_token, text):
    headers = {
        "Authorization": f"Bearer {LINE_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "replyToken": reply_token,
        "messages": [{"type": "text", "text": text}]
    }
    requests.post(LINE_REPLY_URL, headers=headers, json=data)

@app.route("/webhook", methods=["POST"])
def webhook():
    body = request.json
    try:
        for event in body['events']:
            if event['type'] == 'message' and event['message']['type'] == 'text':
                user_msg = event['message']['text']
                reply_token = event['replyToken']

                if user_msg.startswith("小幫手"):
                    query = user_msg.replace("小幫手", "").strip()
                    if not query:
                        reply_message(reply_token, "請輸入要查詢的內容，例如：小幫手 天氣如何？")
                        continue

                    response = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=[{"role": "user", "content": query}],
                        max_tokens=500
                    )
                    reply_text = response['choices'][0]['message']['content']
                    reply_message(reply_token, reply_text)

        return "OK"
    except Exception as e:
        print("Error:", e)
        abort(400)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
