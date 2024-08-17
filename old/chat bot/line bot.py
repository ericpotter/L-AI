from flask import Flask, request
import io

# 載入 json 標準函式庫，處理回傳的資料格式
import json
import os

# 載入 LINE Message API 相關函式庫
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import TextSendMessage, QuickReply, QuickReplyButton, MessageAction, LocationAction, MessageEvent, TextMessage
from dotenv import load_dotenv, find_dotenv

# Gemini
import google.generativeai as genai

# Whisper
import whisper

# Storage
import firebase_admin
from firebase_admin import credentials, initialize_app, storage
import firebase_admin.storage
from google.cloud import storage
from google.oauth2 import service_account

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

system_instruction = "你的身分是一位專業資深有禮貌的的中醫師\n主要使用繁體中文回答\n名字叫做L AI\n負責分析使用者症狀並讓使用者做諮詢\n只會回答中醫相關的問題 \n當如果想要問診則根據下面流程跑\n詢問流程如下，流程中可以讓使用者詢問名詞解釋，並用簡單的說法解釋，並且把所有詢問到的內容輸出成一個表格，不用告知對方推薦治療方式：\n1. 詢問是否需要諮詢，如果沒有則回覆使用者提出的中醫問題，下面的流程不用跑\n2. 詢問對方年齡\n3. 詢問身高體重（kg, cm）\n4. 詢問性別，如果是女生則再增加詢問月經問題：經期是否規律、是否有月經疼痛或其他不適情況、是否有更年期症狀\n5. 詢問是否會手腳冰冷\n6. 詢問感覺身體整體是冷還是熱\n7. 在日常生活中，是否經常感到悶熱或出汗\n8. 最近排便頻率如何，如果不正常，增加詢問：最近是否有消化系統問題，包含消化不良、腹脹、反胃或是其他，如果也有消化問題，則詢問最近每天吃幾餐\n9. 有沒有口臭、口乾、口苦等症狀，有的話增加詢問是否經常覺得口渴，口乾的話另外增加詢問尿液顏色或是否有其他狀況\n10. 最近是否有熬夜，如果有增加詢問其原因為何，包含壓力、心理因素或是生理因素。如果是壓力，詢問其壓力來源為何，包含工作、學業、家庭、感情或是其他，並詢問是否出現壓力反應，之後詢問是否因為過度壓力導致身體或心理健康問題；如果是心理因素，則詢問近期是否感到情緒上的困擾或不適\n11. 是否睡眠方面的困擾，如果有增加詢問是哪方面的睡眠困擾，包含睡不著、淺眠或是早醒。如果是睡不著，則詢問入睡需要多長時間，也詢問入睡前是否會出現思緒纏繞，之後詢問是否有在睡前使用電子產品的習慣；如果是淺眠，則詢問通常一晚上會醒來幾次，之後詢問醒來後是否能夠迅速入睡；如果是早醒，則訊問醒來時間是否早於您正常起床時間，之後詢問醒來後是否能夠迅速重新入睡\n12. 入睡是否容易受到外界干擾\n13. 醒來是否會有頭暈的症狀"
model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest",
                              generation_config=generation_config,
                              system_instruction=system_instruction,
                              safety_settings=safety_settings)
chat = model.start_chat(history=[])

def gemini_ai(text):
    response = chat.send_message(text)
    return response.text

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

        if type == 'text':
            msg = json_data['events'][0]['message']['text']  # 取得 LINE 收到的文字訊息
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