import os
import openai
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from flask import Flask, request, abort

app = Flask(__name__)

line_bot_api = LineBotApi(os.environ["LINE_CHANNEL_ACCESS_TOKEN"])
handler = WebhookHandler(os.environ["LINE_CHANNEL_SECRET"])

openai.api_key = os.environ["OPENAI_API_KEY"]

@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]

    try:
        handler.handle(request.get_data(as_text=True), signature)
    except InvalidSignatureError:
        abort(400)

    return "OK"

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text = event.message.text
    song_and_artist = text.split()

    if len(song_and_artist) == 2:
        song_name, artist_name = song_and_artist
        prompt = f"ユーザーが曲名 {song_name} とアーティスト名 {artist_name} を入力すると、ボーカルの音域がその曲以内に収まる曲をいくつか提案してくれる"
        response = openai.Completion.create(
            engine="text-davinci-002",
            prompt=prompt,
            max_tokens=100,
            n=1,
            stop=None,
            temperature=0.8,
        )
        recommendations = response.choices[0].text.strip()
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=recommendations))
    else:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="曲名とアーティスト名をスペースで区切って入力してください。"))

if __name__ == "__main__":
    app.run()
