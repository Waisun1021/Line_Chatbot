from dotenv import load_dotenv
from flask import Flask, request, abort
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration, ApiClient, MessagingApi,
    ReplyMessageRequest, TextMessage
)
from linebot.v3.webhooks import (
    MessageEvent, TextMessageContent
)
from openai import OpenAI
import logging
import os
load_dotenv()
app = Flask(__name__)
logging.basicConfig(level=logging.INFO)




CHANNEL_ACCESS_TOKEN = os.getenv('CHANNEL_ACCESS_TOKEN')
CHANNEL_SECRET = os.getenv('CHANNEL_SECRET')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
penai_client = OpenAI(
    api_key=OPENAI_API_KEY,
    base_url="https://openrouter.ai/api/v1",
   
)


configuration = Configuration(access_token=CHANNEL_ACCESS_TOKEN)
line_handler = WebhookHandler(CHANNEL_SECRET)


@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers.get('X-Line-Signature', '')
    body = request.get_data(as_text=True)
    app.logger.info("Request body:\n" + body)

    try:
        line_handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.error("Invalid signature. Check your channel secret.")
        abort(400)

    return 'OK'

@line_handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    user_text = event.message.text
    print("使用者傳來的訊息：", user_text)

    try:
      
        response = openai_client.chat.completions.create(
            model="openai/gpt-oss-20b:free",
            messages=[
                {
                    "role": "system",
                    "content": "你是一位由李柏叡開發的虛擬老師，專門在 LINE 上教導使用者各種程式語言與相關知識。你具備專業、清晰、耐心的教學風格，能以深入淺出的方式解說程式邏輯、語法概念與實作技巧，幫助不同程度的學生理解並掌握程式設計。請根據使用者的問題給予具體實用的建議、範例或解法，必要時可分步驟解釋。"
                },
                {"role": "user", "content": user_text}
            ],
            temperature=0.5
        ) 

        reply_text = response.choices[0].message.content.strip()
    except Exception as e:
        reply_text = f"GPT 回覆錯誤：{str(e)}"
    a='柏叡ai-->'
    reply_text =a+reply_text 
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        res = line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=reply_text)]
            )
        )
        print("回應狀態：", res)

#if __name__ == "__main__":
    #app.run(port=5007)
