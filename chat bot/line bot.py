from flask import Flask, request

# 載入 json 標準函式庫，處理回傳的資料格式
import json
import os

# 載入 LINE Message API 相關函式庫
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from dotenv import load_dotenv, find_dotenv

# Gemini
import google.generativeai as genai
# Whisper
import whisper

# dotenv
_ = load_dotenv(find_dotenv()) # read local .env file

# gemini
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"),)

# Set up the model
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 0,
    "max_output_tokens": 8192,
}

safety_settings = [
    {
      "category": "HARM_CATEGORY_HARASSMENT",
      "threshold": "BLOCK_NONE"
    },
    {
      "category": "HARM_CATEGORY_HATE_SPEECH",
      "threshold": "BLOCK_NONE"
    },
    {
      "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
      "threshold": "BLOCK_NONE"
    },
    {
      "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
      "threshold": "BLOCK_NONE"
    },
]

system_instruction = "你的身分是一位中醫師\n名字叫做L AI\n並且主要解決人睡眠障礙的問題\n根據症狀去判斷適合的藥材"

def gemini_ai(text):
    model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest",
                              generation_config=generation_config,
                              system_instruction=system_instruction,
                              safety_settings=safety_settings)
    chat = model.start_chat(history=[])
    response = chat.send_message(text)
    replay = response.text.replace("*", "")
    return replay

# whisper
def whisper_ai(fileName):
    model = whisper.load_model("base")

    # load audio and pad/trim it to fit 30 seconds
    audio = whisper.load_audio(fileName)
    audio = whisper.pad_or_trim(audio)

    # make log-Mel spectrogram and move to the same device as the model
    mel = whisper.log_mel_spectrogram(audio).to(model.device)

    # detect the spoken language
    _, probs = model.detect_language(mel)
    print(f"Detected language: {max(probs, key=probs.get)}")
    # decode the audio
    options = whisper.DecodingOptions()
    result = whisper.decode(model, mel, options)
    # print the recognized text
    return(result.text)

# line bot
app = Flask(__name__)
@app.route("/", methods=['POST'])

def linebot():
    body = request.get_data(as_text=True)                    # 取得收到的訊息內容
    try:
        json_data = json.loads(body)                         # json 格式化訊息內容
        line_bot_api = LineBotApi(os.environ.get("LINE_BOT_TOKEN")) # 確認 token 是否正確
        handler = WebhookHandler(os.environ.get("LINE_BOT_SECRET")) # 確認 secret 是否正確
        signature = request.headers['X-Line-Signature']      # 加入回傳的 headers
        handler.handle(body, signature)                      # 綁定訊息回傳的相關資訊
        tk = json_data['events'][0]['replyToken']            # 取得回傳訊息的 Token
        type = json_data['events'][0]['message']['type']     # 取得 LINe 收到的訊息類型
        if type=='text':
            msg = json_data['events'][0]['message']['text']  # 取得 LINE 收到的文字訊息
            reply = gemini_ai(msg)
        elif type=='audio':
            msgID = json_data['events'][0]['message']['id']
            message_content = line_bot_api.get_message_content(msgID)
            with open(f'temp.m4a', 'wb') as fd:
                fd.write(message_content.content)
            msg = whisper_ai('temp.m4a')
            reply = gemini_ai(msg)
        else:
            reply = '你傳的不是文字呦～'       
        line_bot_api.reply_message(tk,TextSendMessage(reply))# 回傳訊息
    except:
        print(body)                                          # 如果發生錯誤，印出收到的內容
    return 'OK'                                              # 驗證 Webhook 使用，不能省略

if __name__ == "__main__":
    app.run()


#ngrok http 127.0.0.1:5000