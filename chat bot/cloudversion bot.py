import json
import os
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from dotenv import load_dotenv, find_dotenv
import google.generativeai as genai
import whisper


_ = load_dotenv(find_dotenv()) # read local .env file
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"),)

def gemini_ai(text):
    model = genai.GenerativeModel('gemini-pro')
    chat = model.start_chat(history=[])
    response = chat.send_message(text)
    return response.text

def whisper_ai(fileName):
    model = whisper.load_model("base")
    audio = whisper.load_audio(fileName)
    audio = whisper.pad_or_trim(audio)
    mel = whisper.log_mel_spectrogram(audio).to(model.device)
    _, probs = model.detect_language(mel)
    print(f"Detected language: {max(probs, key=probs.get)}")
    options = whisper.DecodingOptions()
    result = whisper.decode(model, mel, options)
    return(result.text)


def linebot(request):
    body = request.get_data(as_text=True)                   
    try:
        json_data = json.loads(body)                       
        line_bot_api = LineBotApi(os.environ.get("LINE_BOT_TOKEN")) 
        handler = WebhookHandler(os.environ.get("LINE_BOT_SECRET")) 
        signature = request.headers['X-Line-Signature']     
        handler.handle(body, signature)                     
        tk = json_data['events'][0]['replyToken']            
        type = json_data['events'][0]['message']['type']    
        if type=='text':
            msg = json_data['events'][0]['message']['text']  
            reply = gemini_ai(msg)
        elif type=='audio':
            msgID = json_data['events'][0]['message']['id']
            message_content = line_bot_api.get_message_content(msgID)
            with open(f'temp.m4a', 'wb') as fd:
                fd.write(message_content.content)
            msg = whisper_ai('temp.m4a')
            reply = gemini_ai(msg)
            os.remove(f'temp.m4a')
        else:
            reply = '你傳的不是文字呦～'
        line_bot_api.reply_message(tk,TextSendMessage(reply))# 回傳訊息
    except:
        print(request.args)                                   
    return 'OK'                                             


# requirements line-bot-sdk openai-whisper python-dotenv google-generativeai